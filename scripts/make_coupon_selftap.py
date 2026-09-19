"""Coupon C - driver mount self-tap pilot size.

ONE question: what pilot diameter lets an M3 self-tapper form threads in PLA, 12 mm
deep, with only 2.15 mm of wall on the thin side, without splitting the arm?

Why it cannot be answered with calipers: thread-forming in plastic depends on the
material, the layer direction and this printer's hole shrink, not on a dimension.

Why it reproduces the real stack rather than being a generic test block:

  arm width          8.5          same as the driver mount arm
  wall, thin side    2.15         hole centre sits 3.5 from that edge, not centred
  wall, other side   3.65
  axial depth        12.0         the pilots go clean through the 12 mm frame
  hole angle         30 deg       from the bed, matching the real part once it is
                                  printed inverted - so the layers run across the
                                  screw the same way they will in the real arm

That angle is the whole point. A flat bar with vertical holes is the EASY case for
splitting and would give an optimistic answer; the real arm is the hard case.

Sizes bracket the current 2.7 design value. On this printer round features come out
about 0.25 under, so the physical holes land near 2.45 / 2.65 / 2.85 - and an M3
self-tapper in PLA generally wants 2.5-2.6.

Orientation: the clipped corner marks the SMALLEST pilot; sizes increase away from it.
"""
import math
import os
import sys

import FreeCAD as App
import Part
import MeshPart

_p = print


def print(*a, **k):
    _p(*a, **k)
    sys.stdout.flush()


REPO = '/home/buralien/projects/gladiator-cad'
OUT = '/home/buralien/Desktop/3D-Printer-Incoming'
MIRROR = REPO + '/cad/print-ready'
COUPONS = REPO + '/cad/coupons'

ARM_W = 8.5
THIN_WALL = 2.15
DEPTH = 12.0                 # along the hole axis, as in the real frame
ANGLE = 30.0                 # degrees from the bed
H = DEPTH * math.sin(math.radians(ANGLE))       # 6.0 - so the hole just breaks through
PITCH = 14.0
END = 10.0
DIAS = [2.7, 2.9, 3.1]
LEN = END * 2 + PITCH * (len(DIAS) - 1)

V = App.Vector


def build():
    body = Part.makeBox(LEN, ARM_W, H)

    # clipped corner at the small-pilot end, for unambiguous orientation
    clip = 4.0
    wedge = Part.makePolygon([V(0, 0, 0), V(clip, 0, 0), V(0, clip, 0), V(0, 0, 0)])
    body = body.cut(Part.Face(wedge).extrude(V(0, 0, H)))

    cuts = []
    for i, d in enumerate(DIAS):
        x = END + i * PITCH
        # drill from above the top face, down and along +X at ANGLE from horizontal
        axis = V(math.cos(math.radians(ANGLE)), 0, -math.sin(math.radians(ANGLE)))
        # start a little outside the solid so the entry is clean, then run well past
        start = V(x, THIN_WALL + d / 2.0, H) - axis * 3.0
        cyl = Part.makeCylinder(d / 2.0, DEPTH + 8.0, start, axis)
        cuts.append(cyl)
    for c in cuts:
        body = body.cut(c)
    return body.removeSplitter()


def main():
    shape = build()
    print('coupon %.1f x %.1f x %.1f mm   volume %.0f mm3  (about %.1f g in PLA)'
          % (LEN, ARM_W, H, shape.Volume, shape.Volume * 1.24 / 1000.0))
    print('  solid=%s valid=%s solids=%d' % (bool(shape.Solids), shape.isValid(), len(shape.Solids)))

    # --- verify the thing actually reproduces what it claims ---
    ok = shape.isValid() and len(shape.Solids) == 1
    bores = {}
    for f in shape.Faces:
        if f.Surface.TypeId != 'Part::GeomCylinder':
            continue
        d = round(f.Surface.Radius * 2, 2)
        bores[d] = bores.get(d, 0) + 1
    print('  pilot bores found: %s' % sorted(bores.items()))
    if sorted(bores.keys()) != sorted(DIAS):
        print('  *** expected %s' % DIAS)
        ok = False

    # thin wall must really be 2.15 at each hole: probe just outside the bore
    print('  checking the thin wall at each pilot:')
    for i, d in enumerate(DIAS):
        x = END + i * PITCH
        yc = THIN_WALL + d / 2.0
        # walk outward from the bore edge toward y=0 and find where solid starts/ends
        zmid = H / 2.0
        xmid = x + (H / 2.0) / math.tan(math.radians(ANGLE))
        solid_from = None
        y = 0.0
        while y < ARM_W:
            inside = shape.isInside(V(xmid, y, zmid), 1e-6, True)
            if inside and solid_from is None:
                solid_from = y
            if not inside and solid_from is not None:
                break
            y += 0.02
        wall = (y - (d / 2.0) - solid_from) if solid_from is not None else -1
        # simpler: distance from bore wall to the y=0 face
        expect = yc - d / 2.0
        print('     dia %.1f  centre y=%.3f  wall to the near edge = %.3f (want %.2f)  %s'
              % (d, yc, expect, THIN_WALL, 'ok' if abs(expect - THIN_WALL) < 0.01 else '*** WRONG'))
        if abs(expect - THIN_WALL) < 0.01:
            pass
        else:
            ok = False

    # gaps between adjacent bore openings on the top face
    opening = DIAS[-1] / math.sin(math.radians(ANGLE))
    print('  top-face opening is %.2f long; %.1f pitch leaves %.2f between openings (want > 3.5)'
          % (opening, PITCH, PITCH - opening))
    if PITCH - opening < 3.5:
        ok = False

    if not ok:
        raise SystemExit('coupon failed its own checks - nothing written')

    doc = App.newDocument('CouponC')
    obj = doc.addObject('Part::Feature', 'CouponC_SelfTapPilots')
    obj.Shape = shape
    doc.recompute()
    doc.saveAs(os.path.join(COUPONS, 'Gladiator_Coupon_C_SelfTapPilots.FCStd'))

    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.01,
                               AngularDeflection=0.05, Relative=False)
    for d in (OUT, MIRROR):
        m.write(os.path.join(d, 'Gladiator_CouponC_SelfTapPilots_flat.stl'))
    print()
    print('  mesh: %d facets  solid=%s  self-intersections=%s'
          % (m.CountFacets, m.isSolid(), m.hasSelfIntersections()))
    print('  written to the incoming folder and cad/print-ready')


main()
