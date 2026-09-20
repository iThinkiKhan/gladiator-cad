"""Coupon D - SMA bulkhead bore.

ONE question: which bore diameter lets the real SMA bulkhead pass and clamp?

Why it exists: `ant_sma_dia` is currently 6.75, and that number is **pure
extrapolation** - it was derived from this printer's 0.25 curve shrink against a
6.35 thread spec, and nothing has ever tested it. It is the only guessed dimension
left on plate B, which is otherwise ready to print.

Why it reproduces the real stack rather than being a plain drilled plate: the
antenna post does not present a simple hole to the connector. It is a 6 thick
plate with an 11 counterbore 4 deep from the rear, leaving a 2.0 web at the bore.
The connector inserts from behind, its shoulder seats in the counterbore, and the
nut tightens on the front face against that 2.0 web. A coupon that skipped the
counterbore would answer a different question.

Parameters are read from the model so the coupon cannot drift from the part.
"""
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

doc = App.openDocument(REPO + '/cad/master/Gladiator_Master.FCStd')
sp = doc.getObject('Parameters')


def val(alias):
    q = sp.get(alias)
    return q.Value if hasattr(q, 'Value') else float(q)


PLATE_T = val('ant_plate_t')
CBORE = val('ant_cbore_dia')
WEB = val('ant_web_t')
NOMINAL = val('ant_sma_dia')
CB_DEPTH = PLATE_T - WEB

print('read from the model:')
print('   plate thickness   %.2f' % PLATE_T)
print('   counterbore       %.2f dia, %.2f deep from the rear' % (CBORE, CB_DEPTH))
print('   clamping web      %.2f' % WEB)
print('   current bore      %.2f  <- the untested extrapolation' % NOMINAL)

DIAS = [6.5, 6.75, 7.0]
PITCH = CBORE + 3.5          # keep 3.5 between counterbore walls
# END must clear the counterbore RADIUS, not its edge. At 6.0 the first
# counterbore left only 6.0 - 5.5 = 0.5 mm of wall at the end of the part - about
# one perimeter, and far too little to chamfer into. Caught when the 0.5 bed
# relief produced an invalid solid.
END = CBORE / 2.0 + 2.5
LEN = END * 2 + PITCH * (len(DIAS) - 1)
WID = CBORE + 5.0

assert END - CBORE / 2.0 >= 2.0, \
    'only %.2f of wall at the end of the part - the relief will break through' % (END - CBORE / 2.0)

V = App.Vector


def build():
    body = Part.makeBox(LEN, WID, PLATE_T)
    clip = 4.0
    wedge = Part.makePolygon([V(0, 0, 0), V(clip, 0, 0), V(0, clip, 0), V(0, 0, 0)])
    body = body.cut(Part.Face(wedge).extrude(V(0, 0, PLATE_T)))
    for i, d in enumerate(DIAS):
        x = END + i * PITCH
        c = V(x, WID / 2.0, 0)
        body = body.cut(Part.makeCylinder(d / 2.0, PLATE_T + 2, c - V(0, 0, 1), V(0, 0, 1)))
        # counterbore from the REAR face (z=0), leaving the web at the front
        body = body.cut(Part.makeCylinder(CBORE / 2.0, CB_DEPTH, c - V(0, 0, 0.001), V(0, 0, 1)))
    return body.removeSplitter()


shape = build()
print()
print('coupon %.1f x %.1f x %.1f   volume %.0f mm3  (about %.1f g in PLA)'
      % (LEN, WID, PLATE_T, shape.Volume, shape.Volume * 1.24 / 1000.0))

ok = shape.isValid() and len(shape.Solids) == 1
bores, cbores = {}, {}
for f in shape.Faces:
    if f.Surface.TypeId != 'Part::GeomCylinder':
        continue
    d = round(f.Surface.Radius * 2, 2)
    (cbores if abs(d - CBORE) < 0.01 else bores)[d] = 1
print('   through bores found: %s   counterbores: %s'
      % (sorted(bores), sorted(cbores)))
if sorted(bores) != sorted(DIAS) or sorted(cbores) != [round(CBORE, 2)]:
    print('   *** unexpected features')
    ok = False

# the web must survive at full thickness at every bore
print('   web thickness at each bore:')
for i, d in enumerate(DIAS):
    x = END + i * PITCH
    y = WID / 2.0 + d / 2.0 + 0.4      # just outside the bore wall
    runs = []
    z = -1.0
    cur = None
    while z < PLATE_T + 1.0:
        ins = shape.isInside(V(x, y, z), 1e-6, True)
        if ins and cur is None:
            cur = z
        if not ins and cur is not None:
            runs.append((cur, z))
            cur = None
        z += 0.01
    if cur is not None:
        runs.append((cur, PLATE_T + 1.0))
    t = sum(b - a for a, b in runs)
    print('      dia %.2f -> %.2f of material beside the bore (want %.2f)' % (d, t, WEB))
    if abs(t - WEB) > 0.05:
        ok = False

print('   checks passed: %s' % ok)
if not ok:
    raise SystemExit('coupon failed its own checks - nothing written')

# ---- bed-plane entrance relief ---------------------------------------------
# This prints counterbore-side down, so the 11 counterbore mouths are the first
# layer. A pinched mouth stops the connector's shoulder seating and the coupon
# then reports a fit problem that is really elephant's foot. 0.5 at 45 deg, to
# match the coupon plate.
import traceback
BED_RELIEF = 0.5
print('   starting bed relief')
z0 = shape.BoundBox.ZMin
edges = []
for e in shape.Edges:
    if len(e.Vertexes) != 1:
        continue
    try:
        if e.Curve.TypeId != 'Part::GeomCircle':
            continue
    except Exception:
        continue
    bb = e.BoundBox
    if abs(bb.ZMin - z0) > 1e-6 or abs(bb.ZMax - z0) > 1e-6:
        continue
    edges.append(e)
print('   found %d candidate bed edges' % len(edges))
if edges:
    try:
        cand = shape.makeChamfer(BED_RELIEF, edges)
    except Exception:
        print('   makeChamfer threw:')
        traceback.print_exc()
        sys.stdout.flush()
        raise
    print('   chamfer built: valid=%s solids=%d' % (cand.isValid(), len(cand.Solids)))
    if not (cand.isValid() and len(cand.Solids) == 1):
        raise SystemExit('bed relief broke the coupon')
    shape = cand
print()
print('   bed-plane relief: %d counterbore mouth(s) chamfered at %.2f' % (len(edges), BED_RELIEF))
if len(edges) != len(DIAS):
    raise SystemExit('expected one bed edge per bore, found %d' % len(edges))

# the through-bores must still measure full size - they start at the counterbore
# floor, well clear of the relief
post = {}
for f in shape.Faces:
    if f.Surface.TypeId == 'Part::GeomCylinder':
        post[round(f.Surface.Radius * 2, 2)] = 1
print('   bores after relief: %s' % sorted(k for k in post if k < 9))
if sorted(k for k in post if k < 9) != sorted(DIAS):
    raise SystemExit('a through-bore was damaged by the relief')

cdoc = App.newDocument('CouponD')
o = cdoc.addObject('Part::Feature', 'CouponD_SmaBore')
o.Shape = shape
cdoc.recompute()
cdoc.saveAs(os.path.join(COUPONS, 'Gladiator_Coupon_D_SmaBore.FCStd'))

m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.01,
                           AngularDeflection=0.05, Relative=False)
for d in (OUT, MIRROR):
    m.write(os.path.join(d, 'Gladiator_CouponD_SmaBore_counterbore-DOWN.stl'))
print()
print('   mesh %d facets  solid=%s  self-intersections=%s'
      % (m.CountFacets, m.isSolid(), m.hasSelfIntersections()))
print('   written. Print counterbore-side DOWN, as exported - that face is the bed face.')
print('   Clipped corner marks the smallest bore; sizes increase away from it.')
