import math
import os
import FreeCAD as App
import Mesh
import MeshPart

OUT = '/home/buralien/Desktop/3D-Printer-Incoming'
MASTER = '/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd'
COUPON = '/home/buralien/projects/gladiator-cad/cad/coupons/Gladiator_FitCoupon_v1.FCStd'

# 0.01 mm chord deviation. Matters a lot here: the coupon's whole job is to resolve
# 0.2 mm steps between bore sizes, and a coarse mesh flattens a circle from the inside.
LIN, ANG = 0.01, 0.05


def bore_error(shape, radius, deflection):
    """How much smaller a pin actually sees a hole of this radius, at this mesh deflection."""
    # facet count around the circle for a given chord deviation
    n = math.pi / math.acos(max(-1.0, min(1.0, 1.0 - deflection / radius)))
    n = max(3.0, n)
    eff = radius * math.cos(math.pi / n)
    return n, (radius - eff) * 2.0


print('=== mesh resolution sanity, before exporting ===')
for r, label in ((2.2, 'insert bore 4.4'), (1.7, 'M3 clearance 3.4'), (6.9, 'spigot peg 13.8')):
    for d in (0.1, 0.01):
        n, err = bore_error(None, r, d)
        print('  %-18s deflection %.2f -> ~%.0f facets, diameter off by %.3f mm'
              % (label, d, n, err))
print()


def export(shape, name, note=''):
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=LIN,
                               AngularDeflection=ANG, Relative=False)
    path = os.path.join(OUT, name)
    m.write(path)
    bb = m.BoundBox
    print('%-52s' % name)
    print('   facets %-7d  bbox %.2f x %.2f x %.2f  sits on Z=%.3f'
          % (m.CountFacets, bb.XLength, bb.YLength, bb.ZLength, bb.ZMin))
    print('   solid=%s  manifold(no free edges)=%s  self-intersections=%s'
          % (m.isSolid(), not m.hasNonManifolds() and m.CountEdges == m.CountFacets * 3 / 2,
             m.hasSelfIntersections()))
    if note:
        print('   %s' % note)
    return m


print('=== coupon ===')
cdoc = App.openDocument(COUPON)
cshape = cdoc.getObject('FitCoupon').Shape
export(cshape, 'Gladiator_FitCoupon_v1.stl', 'flat as modelled, no support')

print()
print('=== side rail, rotated onto its outboard face ===')
mdoc = App.openDocument(MASTER)
rail = mdoc.getObject('SideRailLeft').Shape.copy()

# lay the rail on its outboard (-X) face: find the rotation that puts X-thickness into Z
best = None
for ang in (90.0, -90.0):
    t = rail.copy()
    t.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), ang)
    if abs(t.BoundBox.ZLength - 12.0) < 0.01:
        best = (ang, t)
        break
if best is None:
    raise SystemExit('could not find the rotation that lays the rail down')
ang, rail_r = best
bb = rail_r.BoundBox
rail_r.translate(App.Vector(-bb.XMin, -bb.YMin, -bb.ZMin))
print('   rotated %+.0f deg about Y, then dropped to the bed' % ang)
export(rail_r, 'Gladiator_SideRail_L_print-on-outboard-face.stl',
       'already oriented: lies on its outboard face, 12 tall, ~159 mm2 support')

print()
print('=== files now waiting in the incoming folder ===')
for f in sorted(os.listdir(OUT)):
    if f.lower().endswith('.stl'):
        print('   %-52s %8.0f kB' % (f, os.path.getsize(os.path.join(OUT, f)) / 1024.0))
