"""Cut a standalone reprint of the one piece that came off plate F wrong.

The GH44 female receiver printed with its recess against the bed, so it came out
with no recess at all. Cause: switching those pieces to their BREP sources for
chamfering, then orienting them by "lay the thinnest axis into Z" - which does
not say WHICH face is down, and a 180 flip satisfies it equally well.

Fixed in build_coupon_plate.py by matching the reference STL's centroid height,
with an assertion. This pulls the corrected piece out of the rebuilt plate so it
can be reprinted on its own without re-running the whole plate.
"""
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

import FreeCAD as App
import Mesh

_p = print


def print(*a, **k):
    _p(*a, **k)
    sys.stdout.flush()


NS = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
REPO = '/home/buralien/projects/gladiator-cad'
OUT = '/home/buralien/Desktop/3D-Printer-Incoming'
MIRROR = REPO + '/cad/print-ready'
PLATE = MIRROR + '/Gladiator_PlateF_ALL-COUPONS.3mf'
WANT = 'GH44_Receiver_Fit'
REF = REPO + '/cad/head/v01/fit-prototypes/GH44_Receiver_Fit_Coupon.stl'


def centroid_frac(pts, tris):
    V = 0.0
    Cz = 0.0
    for ia, ib, ic in tris:
        a = App.Vector(*pts[ia])
        b = App.Vector(*pts[ib])
        c = App.Vector(*pts[ic])
        v = a.dot(b.cross(c)) / 6.0
        V += v
        Cz += v * (a.z + b.z + c.z) / 4.0
    zs = [q[2] for q in pts]
    return (Cz / V - min(zs)) / (max(zs) - min(zs)), V


z = zipfile.ZipFile(PLATE)
root = ET.fromstring(z.read('3D/3dmodel.model').decode('utf-8'))
found = None
for o in root.findall('.//%sobject' % NS):
    if o.get('name') != WANT:
        continue
    pts = [(float(v.get('x')), float(v.get('y')), float(v.get('z')))
           for v in o.findall('.//%svertex' % NS)]
    tris = [(int(t.get('v1')), int(t.get('v2')), int(t.get('v3')))
            for t in o.findall('.//%striangle' % NS)]
    found = (pts, tris)
if found is None:
    raise SystemExit('%s is not on the plate' % WANT)

pts, tris = found
c_new, v_new = centroid_frac(pts, tris)

m_ref = Mesh.Mesh(REF)
rp, rf = m_ref.Topology
c_ref, v_ref = centroid_frac([(q.x, q.y, q.z) for q in rp], [tuple(f) for f in rf])

print('corrected piece : centroid %.4f  volume %.1f' % (c_new, v_new))
print('reference STL   : centroid %.4f  volume %.1f' % (c_ref, v_ref))
if abs(c_new - c_ref) > 0.02:
    raise SystemExit('still not matching the reference orientation - refusing to write')
print('orientation matches the reference')

# drop to the origin corner and write
xs = [q[0] for q in pts]
ys = [q[1] for q in pts]
zs = [q[2] for q in pts]
dx, dy, dz = -min(xs), -min(ys), -min(zs)
mesh = Mesh.Mesh()
for ia, ib, ic in tris:
    mesh.addFacet(pts[ia][0] + dx, pts[ia][1] + dy, pts[ia][2] + dz,
                  pts[ib][0] + dx, pts[ib][1] + dy, pts[ib][2] + dz,
                  pts[ic][0] + dx, pts[ic][1] + dy, pts[ic][2] + dz)
mesh.removeDuplicatedPoints()
bb = mesh.BoundBox
print()
print('%.1f x %.1f x %.1f   %d facets   solid=%s  self-intersections=%s'
      % (bb.XLength, bb.YLength, bb.ZLength, mesh.CountFacets,
         mesh.isSolid(), mesh.hasSelfIntersections()))
if not mesh.isSolid() or mesh.hasSelfIntersections() or abs(bb.ZMin) > 1e-6:
    raise SystemExit('mesh failed its checks')

name = 'Gladiator_REPRINT_GH44_Receiver_recess-UP.stl'
for d in (OUT, MIRROR):
    mesh.write(os.path.join(d, name))
print('wrote %s  (%.1f g in PLA)' % (name, v_new * 1.24 / 1000.0))
print('The recess faces UP. Flat back on the bed, no support.')
