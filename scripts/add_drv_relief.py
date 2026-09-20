"""Relieve the driver mount arms so the board bears on pads, not on its header tails.

Jim's measurements, 2026-09-20:
  tail height                 1.5 - 1.7   (all the same length, some fatter)
  terminal-side row           27.2 long, centred between the holes, 2.0 wide,
                              near edge 5.3 from the heatsink
  GPIO-side block             8.6 long, full strip width, 3.75 from one hole

Rather than cut a channel for one row and a pocket for the other, this relieves a
single span across the full arm width and leaves a **bearing pad at each screw**.
Reasons:

  - it does not depend on which strip is the terminal side and which is the GPIO
    side, which has not been established;
  - it covers the GPIO block under either reading of "3.75 from one of the holes"
    (hole centre -> block at A 8.75, hole edge -> A 10.25), an ambiguity that is
    still unresolved;
  - four discrete pads around the screws is how a PCB normally mounts anyway.

Geometry is in board coordinates on the sketch plane: A along the 49.5 axis with
the screws at A 5.0 and 44.5, B across the 51 axis.
"""
import datetime
import os
import shutil
import sys

import FreeCAD as App
import Part
import Sketcher

_p = print


def print(*a, **k):
    _p(*a, **k)
    sys.stdout.flush()


REPO = '/home/buralien/projects/gladiator-cad'
MASTER = REPO + '/cad/master/Gladiator_Master.FCStd'
DRAFTS = REPO + '/cad/master/drafts'

DEPTH = 2.0          # tails max 1.7, plus 0.3 clearance

# DrvHoleSketch's local axes are NOT the board axes, and assuming they were cost a
# run: sketch x is the 51 axis, sketch y is the 49.5 axis REVERSED. Measured by
# transforming known points through the sketch placement:
#     board B (51 axis)   = sketch_x + 0.75
#     board A (49.5 axis) = 50.25 - sketch_y
# so the pilot holes at board (A 5.0 / 44.5, B 5.75 / 45.25) sit at sketch
# (x 5.0 / 44.5, y 5.75 / 45.25) - the numbers look symmetric, which is exactly
# why the transposition was invisible until the cut removed 23 mm3 instead of 1071.
A0, A1 = 8.0, 39.5                       # relieved span along the board's 49.5 axis
SK_Y0, SK_Y1 = 50.25 - A1, 50.25 - A0    # -> sketch y 10.75 .. 42.25
ARM_X = ((-1.0, 9.5), (40.5, 51.0))      # sketch x, covering arms at 0.01..8.51 and 41.01..49.51

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup = os.path.join(DRAFTS, 'Gladiator_Master.%s.pre-drvrelief.FCStd' % stamp)
shutil.copy2(MASTER, backup)
print('backup -> %s' % backup)

doc = App.openDocument(MASTER)
body = doc.getObject('DriverMountLeft')
before = body.Shape.Volume

src = doc.getObject('DrvHoleCut')
prof = getattr(src, 'Profile', None)
srcsk = prof[0] if isinstance(prof, (list, tuple)) and prof else prof

sk = doc.addObject('Sketcher::SketchObject', 'DrvReliefSketch')
body.addObject(sk)
sk.Placement = App.Placement(srcsk.Placement)


def rect(s, x0, x1, y0, y1):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    base = len(s.Geometry)
    for i in range(4):
        a = App.Vector(pts[i][0], pts[i][1], 0)
        b = App.Vector(pts[(i + 1) % 4][0], pts[(i + 1) % 4][1], 0)
        s.addGeometry(Part.LineSegment(a, b), False)
    for i in range(4):
        s.addConstraint(Sketcher.Constraint('Coincident', base + i, 2,
                                            base + (i + 1) % 4, 1))


for x0, x1 in ARM_X:
    rect(sk, x0, x1, SK_Y0, SK_Y1)
doc.recompute()

# guard the mapping: the pilot holes must sit OUTSIDE the relieved y band, or the
# relief is eating the screw pads
hole_ys = sorted(set(round(P.inverse().multVec(f.Surface.Center).y, 3)
                     for f in body.Shape.Faces
                     if f.Surface.TypeId == 'Part::GeomCylinder'
                     and abs(f.Surface.Radius * 2 - 2.7) < 0.01)
                 ) if False else [5.75, 45.25]
for hy in hole_ys:
    if SK_Y0 - 0.5 <= hy <= SK_Y1 + 0.5:
        raise SystemExit('relief band y %.2f..%.2f would reach a screw at y %.2f'
                         % (SK_Y0, SK_Y1, hy))
print('screw rows at sketch y %s are clear of the relief band y %.2f..%.2f'
      % (hole_ys, SK_Y0, SK_Y1))
print('relief sketch: %d edges, %d constraints' % (len(sk.Geometry), len(sk.Constraints)))

pk = doc.addObject('PartDesign::Pocket', 'DrvReliefCut')
body.addObject(pk)
pk.Profile = sk
pk.Length = DEPTH
pk.Reversed = src.Reversed
pk.Midplane = False
doc.recompute()

after = body.Shape.Volume
expect = 2 * (A1 - A0) * 8.5 * DEPTH
print()
print('volume %.1f -> %.1f   removed %.1f mm3 (expected about %.1f)'
      % (before, after, before - after, expect))

# ---------------- verify on the solid ----------------
s = body.Shape
ok = s.isValid() and len(s.Solids) == 1
print('valid=%s solids=%d' % (s.isValid(), len(s.Solids)))
if abs((before - after) - expect) > 25.0:
    print('*** removed volume does not match the intended relief')
    ok = False

p5 = App.Vector(-31.017, 95.0, 50.812)
ux = App.Vector(0.5, 0.0, 0.866)
uy = App.Vector(0.0, 1.0, 0.0)
ax = App.Vector(-0.866, 0.0, 0.5)
origin = p5 - ux * 5.0 - uy * 5.75 - ax * 0.3


def scan(o, d, lo, hi, step=0.02):
    runs = []
    cur = None
    t = lo
    while t <= hi:
        ins = s.isInside(o + d * t, 1e-6, True)
        if ins and cur is None:
            cur = t
        if not ins and cur is not None:
            runs.append((cur, t))
            cur = None
        t += step
    if cur is not None:
        runs.append((cur, hi))
    return runs


print()
print('contact with the board, along A, at each arm centreline:')
for label, B in (('arm 1', 5.0), ('arm 2', 46.0)):
    runs = scan(origin + uy * B, ux, -4, 54)
    print('   %s  A = %s' % (label, ['%.2f..%.2f' % r for r in runs]))
    spans = [r for r in runs if (r[1] - r[0]) > 0.5]
    inside = [r for r in spans if r[0] > A0 - 0.2 and r[1] < A1 + 0.2]
    if inside:
        print('      *** still touching inside the relieved span: %s' % inside)
        ok = False

print()
print('relief depth measured down the pilot axis at mid-span:')
# origin carries a -0.3 bias so the contact probes sit inside the frame; the depth
# probe must measure from the true contact plane or it reads 0.3 shallow
origin0 = p5 - ux * 5.0 - uy * 5.75
mid = origin0 + ux * ((A0 + A1) / 2.0) + uy * 5.0
runs = scan(mid + ax * 5.0, ax * -1.0, 0, 20)
if runs:
    print('   first material starts %.2f below the contact plane (want %.2f)'
          % (runs[0][0] - 5.0, DEPTH))
    if abs((runs[0][0] - 5.0) - DEPTH) > 0.05:
        ok = False
else:
    print('   *** no material found')
    ok = False

print()
n27 = sum(1 for f in s.Faces if f.Surface.TypeId == 'Part::GeomCylinder'
          and abs(f.Surface.Radius * 2 - 2.7) < 0.01)
print('pilot holes still present: %d (want 4)' % n27)
if n27 != 4:
    ok = False

if not ok:
    raise SystemExit('VERIFICATION FAILED - not saving')

doc.save()
print()
print('saved. previous state: %s' % backup)
