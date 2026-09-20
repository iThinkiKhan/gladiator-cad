"""Cut the wire pass-through in the upper deck.

Jim, 2026-09-20: rectangular, forward of the mast, centred on the mast axis.
X 29.5..49.5, Y 90..98 - 20 x 8, the largest that fits between the S3 board's rear
edge at Y 89 and the mast collar at Y 99.

Corners rounded R3 and both faces chamfered, because wires will sit against these
edges permanently and a printed edge is sharp enough to cut insulation over time.
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

X0, X1 = 29.5, 49.5
Y0, Y1 = 90.0, 98.0
R = 3.0
EASE = 0.8          # chamfer on both faces, so wires do not chafe
Z_BOT, Z_TOP = 48.0, 52.0

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup = os.path.join(DRAFTS, 'Gladiator_Master.%s.pre-wireslot.FCStd' % stamp)
shutil.copy2(MASTER, backup)
print('backup -> %s' % backup)

doc = App.openDocument(MASTER)
body = doc.getObject('UpperDeck')
before = body.Shape.Volume

# build the rounded rectangle as a face, extrude it through the plate, cut it
base = Part.makeBox(X1 - X0, Y1 - Y0, Z_TOP - Z_BOT + 4.0,
                    App.Vector(X0, Y0, Z_BOT - 2.0))
tool = base.makeFillet(R, [e for e in base.Edges if abs(e.tangentAt(e.FirstParameter).z) > 0.99])

cut = doc.addObject('PartDesign::SubtractiveBox', 'WireSlotHelper') if False else None
feat = doc.addObject('Part::Feature', 'WireSlotTool')
feat.Shape = tool
doc.recompute()

boolean = doc.addObject('PartDesign::Boolean', 'WireSlotCut')
body.addObject(boolean)
boolean.Type = 'Cut'
boolean.Group = [feat]
doc.recompute()

after = body.Shape.Volume
area = (X1 - X0) * (Y1 - Y0) - (4.0 - 3.14159265) * R * R
expect = area * (Z_TOP - Z_BOT)
print()
print('opening %.1f x %.1f, R%.1f corners' % (X1 - X0, Y1 - Y0, R))
print('volume %.1f -> %.1f   removed %.1f mm3 (expected about %.1f)'
      % (before, after, before - after, expect))

s = body.Shape
ok = s.isValid() and len(s.Solids) == 1
print('valid=%s solids=%d' % (s.isValid(), len(s.Solids)))
if abs((before - after) - expect) > 5.0:
    print('*** removed volume does not match the intended opening')
    ok = False

# ease both faces of the new opening
edges = []
for e in s.Edges:
    bb = e.BoundBox
    if bb.XMin < X0 - 0.01 or bb.XMax > X1 + 0.01:
        continue
    if bb.YMin < Y0 - 0.01 or bb.YMax > Y1 + 0.01:
        continue
    if abs(bb.ZLength) > 1e-6:
        continue
    if abs(bb.ZMin - Z_BOT) < 1e-6 or abs(bb.ZMin - Z_TOP) < 1e-6:
        edges.append(e)
print()
print('easing %d edge(s) around the opening at %.1f' % (len(edges), EASE))
# a rounded rectangle is 4 lines + 4 arcs per face, so 16 across both faces -
# not 2. The first version asserted 2 and failed on correct geometry.
if len(edges) != 16:
    print('*** expected 16 edges (8 per face), found %d' % len(edges))
    ok = False
else:
    # match by geometry, not by isSame - body.Shape and tip.Shape are different
    # instances and isSame matched none of them
    tip = body.Tip
    names = []
    for i, te in enumerate(tip.Shape.Edges):
        bb = te.BoundBox
        if bb.XMin < X0 - 0.01 or bb.XMax > X1 + 0.01:
            continue
        if bb.YMin < Y0 - 0.01 or bb.YMax > Y1 + 0.01:
            continue
        if abs(bb.ZLength) > 1e-6:
            continue
        if abs(bb.ZMin - Z_BOT) < 1e-6 or abs(bb.ZMin - Z_TOP) < 1e-6:
            names.append('Edge%d' % (i + 1))
    print('   matched %d of them on the body tip' % len(names))
    if len(names) != 16:
        print('*** could not match every edge on the tip')
        ok = False
    else:
        ch = doc.addObject('PartDesign::Chamfer', 'WireSlotEase')
        ch.Base = (tip, names)
        ch.Size = EASE
        body.addObject(ch)
        doc.recompute()
        s = body.Shape
        cones = [f for f in s.Faces if f.Surface.TypeId in
                 ('Part::GeomCone', 'Part::GeomPlane', 'Part::GeomCylinder')]
        if not (s.isValid() and len(s.Solids) == 1):
            print('*** easing produced an invalid solid')
            ok = False
        else:
            print('   eased: volume now %.1f' % s.Volume)

# clearances
print()
for n in ('MastTube', 'MastBase'):
    o = doc.getObject(n)
    d = s.distToShape(o.Shape)[0]
    print('   clearance to %-10s %.2f mm' % (n, d))

print()
print('bosses and holes still present:')
n46 = sum(1 for f in s.Faces if f.Surface.TypeId == 'Part::GeomCylinder'
          and abs(f.Surface.Radius * 2 - 4.6) < 0.01)
n36 = sum(1 for f in s.Faces if f.Surface.TypeId == 'Part::GeomCylinder'
          and abs(f.Surface.Radius * 2 - 3.6) < 0.01)
print('   4.6 insert bores %d (want 10)   3.6 clearance holes %d (want 6)' % (n46, n36))
if n46 != 10 or n36 != 6:
    ok = False

if not ok:
    raise SystemExit('VERIFICATION FAILED - not saving')

doc.save()
print()
print('saved. previous state: %s' % backup)
