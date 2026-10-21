"""Antenna pylon v3 (2026-10-14, Claude). Replaces the printed AntennaPost in the master, which is NOT modified.

Run: freecadcmd build_pylon_v3.py

Jim, 2026-10-14: the old pylon recessed the connector so much that the nut/flange was too hard to turn and tighten.
Old pylon (master AntennaPost): 6 mm plate, O11 x 4 deep round pocket on the inside, O7.0 hole, 2.0 web on the outside face.
v3 rule (also used by the enclosure v2 mount): NO pocket on either face.
  * 2.0 mm plate (the SMA clamp limit is about 2.2), flat on both faces
  * open flat zone of radius 11 mm around the axis on both faces (nut 8 AF / 9.2 corners, flange, fingers, pliers, spanner)
  * stiffness from two edge ribs and lower diagonal spokes that start OUTSIDE that zone
Footprint widened 2 mm each side (X54..82, still inside the deck edge) so the edge ribs start outside the clear zone. Same deck bosses (60,10) and (76,10), same hole position (68, 84.5) and O7.0 hole as the pylon on the robot.
"""
import FreeCAD as A, Part, MeshPart, math, json, os, shutil, traceback, time
from pathlib import Path

V = A.Vector
R = Path('/home/buralien/projects/gladiator-cad')
O = R / 'cad/v2/antenna-pylon/v3-20261014'
O.mkdir(parents=True, exist_ok=True)
W = Path('/tmp/pylonv3')
W.mkdir(exist_ok=True)
shutil.copy(R / 'cad/enclosure/concept-20261013/Gladiator_Enclosure_Concept.FCStd', W / 'c.FCStd')

P = dict(x0=54.0, x1=82.0, y0=2.0, flange_y1=13.0, z0=64.5, flange_top=68.5, z_top=92.5,
         plate_t=2.0, hole_x=68.0, hole_z=84.5, hole_d=7.0, clear_r=11.0,
         rib_t=2.8, rib_y1=10.0, spoke_t=3.0, bolt_d=3.6, bolts=[(60.0, 10.0), (76.0, 10.0)])


def plain(s):
    q = Part.Shape()
    q.importBrepFromString(s.exportBrepToString())
    return q


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def fuse(*s):
    r = plain(s[0])
    for x in s[1:]:
        r = plain(r.fuse(plain(x)))
    return plain(r.removeSplitter())


def cut(a, *s):
    a = plain(a)
    for x in s:
        a = plain(a.cut(plain(x)))
    return plain(a.removeSplitter())


def com(a, b):
    return plain(plain(a).common(plain(b)).removeSplitter())


p = P
parts = [box(p['x0'], p['x1'], p['y0'], p['flange_y1'], p['z0'], p['flange_top']),                  # base flange
         box(p['x0'], p['x1'], p['y0'], p['y0'] + p['plate_t'], p['z0'], p['z_top']),               # 2.0 plate
         box(p['x0'], p['x0'] + p['rib_t'], p['y0'], p['rib_y1'], p['flange_top'], p['z_top']),      # edge ribs
         box(p['x1'] - p['rib_t'], p['x1'], p['y0'], p['rib_y1'], p['flange_top'], p['z_top'])]
window = box(p['x0'], p['x1'], p['y0'], p['rib_y1'], p['flange_top'], p['z_top'])
for ang in (45, 135):                                                                               # lower diagonal spokes from r = clear_r
    sp = box(p['clear_r'], p['clear_r'] + 30, p['y0'], p['rib_y1'], -p['spoke_t'] / 2, p['spoke_t'] / 2)
    sp.rotate(V(0, 0, 0), V(0, 1, 0), ang)
    sp.translate(V(p['hole_x'], 0, p['hole_z']))
    parts.append(com(sp, window))
body = fuse(*parts)
holes = [Part.makeCylinder(p['hole_d'] / 2, 20, V(p['hole_x'], -5, p['hole_z']), V(0, 1, 0))]
holes += [Part.makeCylinder(p['bolt_d'] / 2, 20, V(bx, by, p['z0'] - 5)) for bx, by in p['bolts']]
body = cut(body, *holes)

chk = dict(status='v3 REVIEW PART - not printed, not fitted', parameters=P, valid=body.isValid(), solids=len(body.Solids),
           volume_mm3=round(body.Volume, 1), old_pylon_volume_mm3=4333)
d = A.openDocument(str(W / 'c.FCStd'))
refs = {o.Name: plain(o.Shape) for o in d.Objects if o.Name.startswith('Ref_')}
coll, gaps = [], []
for n, r in refs.items():
    if not body.BoundBox.intersect(r.BoundBox):
        continue
    try:
        v = body.common(r).Volume
    except Exception:
        v = 0.0
    if v > 0.01:
        coll.append((n, round(v, 3)))
    else:
        gaps.append((round(body.distToShape(r)[0], 2), n))
gaps.sort()
chk['collisions_with_chassis_references'] = coll
chk['nearest_references_mm'] = gaps[:6]
# access checks: material within the clear radius on the inside face (should be none)
probe = []
for r_ in (5.0, 8.0, 10.5):
    for ang in (0, 45, 90, 135, 180, 225, 270, 315):
        x = p['hole_x'] + r_ * math.cos(math.radians(ang))
        z = p['hole_z'] + r_ * math.sin(math.radians(ang))
        if r_ > 3.6 and body.isInside(V(x, 6.0, z), 1e-6, True) and z < p['z_top']:
            probe.append((r_, ang))
chk['material_inside_clear_zone_at_Y6'] = probe
# print orientation: outside face down, ribs up (rotation about X by 90 degrees, proper rotation)
c = body.copy()
c.rotate(V(0, 0, 0), V(1, 0, 0), 90)       # (x,y,z) -> (x,-z,y)
bb = c.BoundBox
c.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
m = MeshPart.meshFromShape(Shape=c, LinearDeflection=0.03, AngularDeflection=math.radians(10))
m.write(str(O / 'Gladiator_AntennaPylon_v3.stl'))
chk['stl'] = dict(file='Gladiator_AntennaPylon_v3.stl', is_solid=m.isSolid(), non_manifold=m.hasNonManifolds(),
                  size_mm=[round(c.BoundBox.XLength, 1), round(c.BoundBox.YLength, 1), round(c.BoundBox.ZLength, 1)])
doc = A.newDocument('Gladiator_AntennaPylon_v3')
o = doc.addObject('Part::Feature', 'AntennaPylon_v3')
o.Shape = body
doc.recompute()
doc.saveAs(str(O / 'Gladiator_AntennaPylon_v3.FCStd'))
Part.export([o], str(O / 'Gladiator_AntennaPylon_v3.step'))
(O / 'validation.json').write_text(json.dumps(chk, indent=2))
print(json.dumps(chk, indent=1), flush=True)

# section image
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(13, 6))
    for w in body.slice(V(1, 0, 0), p['hole_x'] + 0.01):
        pts = w.discretize(100)
        axs[0].plot([q.y for q in pts], [q.z for q in pts], color='#c0392b', lw=1.6)
    axs[0].set_aspect('equal'); axs[0].grid(alpha=.3); axs[0].set_xlabel('Y (outside face at Y=2)')
    axs[0].set_title('v3 section X=68: 2.0 plate, flat both faces, no pocket')
    for w in body.slice(V(0, 1, 0), 6.0):
        pts = w.discretize(100)
        axs[1].plot([q.x for q in pts], [q.z for q in pts], color='#c0392b', lw=1.4)
    t = [a / 50.0 * 2 * math.pi for a in range(51)]
    axs[1].plot([p['hole_x'] + 11 * math.cos(a) for a in t], [p['hole_z'] + 11 * math.sin(a) for a in t], '--', color='#00897b', lw=1)
    axs[1].set_aspect('equal'); axs[1].grid(alpha=.3); axs[1].set_xlabel('X')
    axs[1].set_title('v3 section Y=6 (from behind): edge ribs + lower spokes, r=11 clear zone dashed', fontsize=9)
    fig.savefig(str(O / 'pylon_v3_sections.png'), dpi=75, bbox_inches='tight')
except Exception:
    traceback.print_exc()
os._exit(0)
