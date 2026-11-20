"""Pan servo carriage v2: bigger servo opening so the SG90 body drops through and its ears sit ON TOP of the carriage.

Everything except the opening (and a first-layer relief) is copied from build_head_v04.py:
  CAR_HW 12.5, CAR_L 35 + EXT 9, CAR_T 3.0, ear pilots 2.35 at 27.2 pitch, two M3 slots (3.6 wide, 7.0 long) at x +-8.5.
Run with freecadcmd:  freecadcmd make_carriage.py   (argv via environment: OUT=/path RELEASED=/path/to/released.stl)
"""
import sys, os, math, struct, zipfile
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod', '/usr/lib/freecad-python3/lib'])
import FreeCAD as A
import Part, Mesh, MeshPart

OUT = os.environ['OUT']
RELEASED = os.environ.get('RELEASED', '')
os.makedirs(OUT, exist_ok=True)

CAR_HW, CAR_L, EXT, CAR_T = 12.5, 35.0, 9.0, 3.0
BODY_W, BODY_L, SHAFT_NEAR = 12.0, 22.8, 5.9
BODY_CTR = -(BODY_L / 2.0 - SHAFT_NEAR)
C_MIN, C_MAX, C_NOM = 37.0, 40.4, 39.75
EAR_PITCH, PILOT_M2, M3_CLEAR, NUT_X = 27.2, 2.35, 3.6, 8.5
SLOT_OFF = -(17.5 + EXT / 2.0)
SLOT_W = M3_CLEAR
SLOT_L = SLOT_W + (C_MAX - C_MIN)
YB = -C_NOM + BODY_CTR                       # body centre y at nominal spacing (the build script's y_bc(C_NOM))
Y0 = YB - CAR_L / 2 - EXT                    # carriage near edge; the part is shifted so this is 0
X0 = -CAR_HW


def box(x, y, z, dx, dy, dz): return Part.makeBox(dx, dy, dz, A.Vector(x, y, z))
def cyl(r, z, h, x, y): return Part.makeCylinder(r, h, A.Vector(x, y, z))


def slot(x, y1, y2, z, h, w):
    r = w / 2.0
    s = cyl(r, z, h, x, y1).fuse(cyl(r, z, h, x, y2)).fuse(box(x - r, y1, z, w, y2 - y1, h))
    return s


def carriage(open_w, open_l, dogbone_r=0.0, relief=0.0, relief_h=0.5):
    car = box(-CAR_HW, YB - CAR_L / 2 - EXT, 0, 2 * CAR_HW, CAR_L + EXT, CAR_T)
    # servo opening, through
    cut = box(-open_w / 2, YB - open_l / 2, -1, open_w, open_l, CAR_T + 2)
    if dogbone_r:
        for sx in (-1, 1):
            for sy in (-1, 1):
                cut = cut.fuse(cyl(dogbone_r, -1, CAR_T + 2, sx * open_w / 2, YB + sy * open_l / 2))
    car = car.cut(cut)
    if relief:   # first-layer relief at the bed face, same idea as the project's hole entry relief
        car = car.cut(box(-open_w / 2 - relief, YB - open_l / 2 - relief, -0.1, open_w + 2 * relief,
                          open_l + 2 * relief, relief_h + 0.1))
    for sy in (-1, 1):
        car = car.cut(cyl(PILOT_M2 / 2, -0.1, CAR_T + 0.2, 0, YB + sy * EAR_PITCH / 2))
        # the released part has a 0.5 mm 45 degree relief on these two pilots at the bed face
        car = car.cut(Part.makeCone(PILOT_M2 / 2 + 0.5, PILOT_M2 / 2, 0.5, A.Vector(0, YB + sy * EAR_PITCH / 2, 0)))
    ys = YB + SLOT_OFF
    for sx in (-1, 1):
        car = car.cut(slot(sx * NUT_X, ys - (SLOT_L - SLOT_W) / 2, ys + (SLOT_L - SLOT_W) / 2, -0.1, CAR_T + 0.2, SLOT_W))
        if relief:
            car = car.cut(slot(sx * NUT_X, ys - (SLOT_L - SLOT_W) / 2, ys + (SLOT_L - SLOT_W) / 2, -0.1, relief_h + 0.1,
                               SLOT_W + 2 * relief))
    car.translate(A.Vector(-X0, -Y0, 0))
    assert car.isValid() and len(car.Solids) == 1
    return car


def stats(s, tag):
    bb = s.BoundBox
    print('%s: vol %.1f  bbox %.2f x %.2f x %.2f' % (tag, s.Volume, bb.XLength, bb.YLength, bb.ZLength))


# --- 1. rebuild the RELEASED carriage and prove the reconstruction before changing anything
orig = carriage(BODY_W, BODY_L)
stats(orig, 'reconstructed released')
assert abs(orig.Volume - 2316.6) < 0.2, 'does not reproduce the released volume (2316.6 from the released STL)'
if RELEASED:
    m = Mesh.Mesh(RELEASED)
    pts = m.Points
    worst = 0.0
    for i in range(0, len(pts), max(1, len(pts) // 600)):
        p = pts[i].Vector
        worst = max(worst, orig.distToShape(Part.Vertex(p))[0])
    print('released STL vertices vs reconstruction: worst distance %.4f mm' % worst)
    assert worst < 0.03, 'orientation or geometry differs from the released carriage'

# --- 2. the new carriages
VARIANTS = [
    ('A_standard', dict(open_w=12.8, open_l=23.4, dogbone_r=0.5, relief=0.35)),
    ('B_roomy',    dict(open_w=13.4, open_l=23.4, dogbone_r=0.5, relief=0.35)),
]
meshes = []
for name, kw in VARIANTS:
    s = carriage(**kw)
    stats(s, name)
    mesh = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.2, Relative=False)
    ok = mesh.isSolid() and not mesh.hasNonManifolds() and not mesh.hasSelfIntersections()
    print('  mesh: %d facets  solid/manifold/no-selfintersect=%s  volume %.1f  (shape %.1f)' % (
        mesh.CountFacets, ok, mesh.Volume, s.Volume))
    assert ok and abs(mesh.Volume - s.Volume) / s.Volume < 0.002
    # wall left between the opening end and each ear pilot, for the report
    wall = EAR_PITCH / 2 - PILOT_M2 / 2 - kw['open_l'] / 2
    print('  wall opening-end to ear pilot: %.2f mm' % wall)
    mesh.write(os.path.join(OUT, 'Gladiator_Head_Pan_Servo_Carriage_v2_%s.stl' % name))
    meshes.append((name, mesh))

# --- 3. one 3MF with both on the bed (flat, no supports)
parts, items = [], []
for i, (name, mesh) in enumerate(meshes, 1):
    idx, vs, ts = {}, [], []
    for f in mesh.Facets:
        tri = []
        for p in f.Points:
            key = (round(p[0], 5), round(p[1], 5), round(p[2], 5))
            if key not in idx:
                idx[key] = len(vs)
                vs.append(key)
            tri.append(idx[key])
        ts.append(tri)
    parts.append('<object id="%d" name="Carriage_v2_%s" type="model"><mesh><vertices>%s</vertices><triangles>%s</triangles></mesh></object>' % (
        i, name, ''.join('<vertex x="%.5f" y="%.5f" z="%.5f"/>' % v for v in vs),
        ''.join('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t) for t in ts)))
    items.append('<item objectid="%d" transform="1 0 0 0 1 0 0 0 1 %.3f %.3f 0"/>' % (i, 80.0 + (i - 1) * 40.0, 88.0))
model = ('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" '
         'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>%s</resources><build>%s</build></model>'
         % (''.join(parts), ''.join(items)))
ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
with zipfile.ZipFile(os.path.join(OUT, 'Gladiator_Head_Pan_Servo_Carriage_v2_x2.3mf'), 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', ct)
    z.writestr('_rels/.rels', rels)
    z.writestr('3D/3dmodel.model', model)
print('DONE', OUT)
