"""R3d (2026-10-03): the GH44 register cut through the plate, replacing R3c whose face-down recess printed about
1 mm shallow. Derived from build_head_coupons_r3.py. Run with freecadcmd on the CAD server."""
"""Gladiator head coupons, round 3 (2026-10-01). Three small checks of things the released head parts
depend on that no coupon has tested yet. Each answers ONE question.

    R3a  screen slice       does the real ST7789 sit in the frame pocket, the visible area in the window,
                            and the 4 M2 screws line up with the pilots? (the hole offset is ASSUMED)
    R3b  sideways nut       does an M3 nut press into a 6.0 pocket printed on its SIDE (neck collar,
                            tilt pivot), when H5 only tested pockets printed upright?
    R3c  face-down register does the GH44 key seat in a recess printed AGAINST THE BED (the receiver
                            prints face down), when the register was only tested recess-up?

Every dimension is copied from build_head_v04.py (2026-10-01). Run with freecadcmd on the CAD server.
"""
import sys, json, math, zipfile
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod', '/usr/lib/freecad-python3/lib'])
import FreeCAD as A
import Part, Mesh, MeshPart

ROOT = Path('/home/buralien/projects/gladiator-cad')
OUT = ROOT / 'cad/head/coupons-r3d-20261003'
STL = OUT / 'stl'
STL.mkdir(parents=True, exist_ok=True)
PREFIX = 'Gladiator_HeadR3d_'
LIN, ANG = 0.01, 0.0872665
BED_X, BED_Y, MARGIN, GAP = 220.0, 220.0, 10.0, 8.0
BED_RELIEF = 0.5

# --- copied from build_head_v04.py ------------------------------------------------------------
M3_CLEAR, NUT_AF, NUT_DEPTH, PILOT_M2 = 3.6, 6.0, 2.6, 2.35
BOARD_L, BOARD_H, BOARD_T = 62.5, 29.0, 3.2
VIS_W, VIS_H, VIS_PIN, VIS_TOP = 51.2, 25.6, 6.2, 1.5
HOLE_DX, HOLE_DZ = 58.25, 26.00
LIP, WIN_MARGIN, POCKET_CLR = 3.0, 0.3, 0.3
REG_CHAMFER = 5.0


def box(x, y, z, dx, dy, dz): return Part.makeBox(dx, dy, dz, A.Vector(x, y, z))
def cyl(r, z, h, x=0.0, y=0.0): return Part.makeCylinder(r, h, A.Vector(x, y, z))
def cy(r, y, h, x, z): return Part.makeCylinder(r, h, A.Vector(x, y, z), A.Vector(0, 1, 0))


def fuse(*ss):
    s = ss[0]
    for t in ss[1:]:
        s = s.fuse(t)
    return s.removeSplitter()


def hex_y(af, y, depth, x, z):
    r = af / math.sqrt(3)
    pts = [A.Vector(x + r * math.cos(k * math.pi / 3), y, z + r * math.sin(k * math.pi / 3)) for k in range(6)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(A.Vector(0, depth, 0))


def keyshape(w, h, y, depth, zc=0.0):
    c = REG_CHAMFER
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2 - c), (w / 2 - c, h / 2), (-w / 2, h / 2)]
    vs = [A.Vector(x, y, zc + v) for x, v in pts]
    return Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(A.Vector(0, depth, 0))


def bed_chamfer(shape, size=BED_RELIEF):
    z0 = shape.BoundBox.ZMin
    edges = [e for e in shape.Edges if len(e.Vertexes) == 1 and getattr(e.Curve, 'TypeId', '') == 'Part::GeomCircle'
             and abs(e.BoundBox.ZMin - z0) < 1e-6 and abs(e.BoundBox.ZMax - z0) < 1e-6]
    if not edges:
        return shape, 0
    try:
        out = shape.makeChamfer(size, edges)
        if out.isValid() and len(out.Solids) == 1:
            return out, len(edges)
    except Exception:
        pass
    return shape, 0


def bed_area(shape):
    z0 = shape.BoundBox.ZMin
    return sum(f.Area for f in shape.Faces if abs(f.BoundBox.ZMin - z0) < 1e-6 and abs(f.BoundBox.ZMax - z0) < 1e-6)


pieces = []
X_AXIS = A.Vector(1, 0, 0)


def add(key, stem, shape, note, probes, rot=None, bed_min=100):
    assert shape.isValid() and len(shape.Solids) == 1, key
    s = shape.copy()
    if rot is not None:
        s.rotate(A.Vector(), X_AXIS, rot)
        R = A.Rotation(X_AXIS, rot)
        probes = [(tuple(R.multVec(A.Vector(*p))), i) for p, i in probes]
    b = s.BoundBox
    s.translate(A.Vector(-b.XMin, -b.YMin, -b.ZMin))
    probes = [((x - b.XMin, y - b.YMin, z - b.ZMin), i) for (x, y, z), i in probes]
    pieces.append({'key': key, 'stem': stem, 'shape': s, 'note': note, 'probes': probes, 'bed_min': bed_min})


# ===================================================== R3d: the GH44 register cut THROUGH the plate, as the receiver now is
# R3c's 1.6 deep recess printed facing the bed came out about 1 mm shallow (its roof is a bridge).
# Here the register goes clean through the 4.0 plate; the strip behind is the receiver's backbone (3.8 deep).
rg = box(-17, -52, -15, 34, 4, 30)
rg = rg.cut(keyshape(26.4, 22.4, -52.1, 4.2))
rg = rg.cut(keyshape(26.4 + 0.7, 22.4 + 0.7, -52.1, 0.5))   # the same first-layer relief as the receiver
rg = fuse(rg, box(-17, -48.2, -6, 34, 4.2, 12))             # the backbone, fused after the cut like the receiver
add('R3d', 'R3d_GH44Register_THROUGH-window_face-DOWN', rg,
    'plate face DOWN against the bed, exactly as the real receiver prints; no support',
    [((-15, -50, 13), True), ((0, -51, 0), False), ((0, -50, 9), False), ((0, -46, 0), True)], rot=90.0)

# ============================================================================== export
report = {'status': 'FIT COUPON, R3d', 'pieces': []}
LOG = []
for p in pieces:
    sh, nch = bed_chamfer(p['shape'])
    p['shape'] = sh
    probe_ok = all(sh.isInside(A.Vector(*pt), 1e-6, True) == ins for pt, ins in p['probes'])
    m = MeshPart.meshFromShape(Shape=sh, LinearDeflection=LIN, AngularDeflection=ANG, Relative=False)
    path = STL / (PREFIX + p['stem'] + '.stl')
    m.write(str(path))
    back = Mesh.Mesh(str(path))
    b = sh.BoundBox
    rec = {'key': p['key'], 'file': path.name, 'orientation': p['note'],
           'size_mm': [round(b.XLength, 1), round(b.YLength, 1), round(b.ZLength, 1)],
           'volume_cm3': round(sh.Volume / 1000, 2), 'grams_pla': round(sh.Volume * 0.00124, 1),
           'bed_contact_mm2': round(bed_area(sh)), 'probes_pass': probe_ok,
           'mesh_ok': back.isSolid() and not back.hasNonManifolds(),
           'mesh_volume_error_pct': round(100 * abs(back.Volume - sh.Volume) / sh.Volume, 3)}
    rec['pass'] = probe_ok and rec['mesh_ok'] and rec['mesh_volume_error_pct'] < 0.5 and rec['bed_contact_mm2'] >= p['bed_min']
    report['pieces'].append(rec)
    p['mesh'] = back
    LOG.append('%-4s %-62s %5.1f x %5.1f x %4.1f  %5.2f cm3  bed %4d  %s' % (
        p['key'], path.name, b.XLength, b.YLength, b.ZLength, sh.Volume / 1000, rec['bed_contact_mm2'],
        'ok' if rec['pass'] else '*** FAIL'))

items = [[p['stem'], p['mesh'].copy()] for p in pieces]
for it in items:
    b = it[1].BoundBox
    it[1].translate(-b.XMin, -b.YMin, -b.ZMin)
items.sort(key=lambda it: -it[1].BoundBox.YLength)
x = BED_X / 2.0 - (sum(it[1].BoundBox.XLength for it in items) + GAP * (len(items) - 1)) / 2.0
for it in items:
    b = it[1].BoundBox
    it[1].translate(x - b.XMin, BED_Y / 2.0 - b.YLength / 2.0 - b.YMin, 0)
    x += b.XLength + GAP
offbed = sum(1 for _, m in items if not (m.BoundBox.XMin >= MARGIN and m.BoundBox.XMax <= BED_X - MARGIN))
overlaps = sum(1 for i in range(len(items)) for j in range(i + 1, len(items))
               if items[i][1].BoundBox.XMax > items[j][1].BoundBox.XMin
               and items[j][1].BoundBox.XMax > items[i][1].BoundBox.XMin)
NL = chr(10)


def write_3mf(path, title, its):
    md = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
          '<metadata name="Title">%s</metadata>' % title, '<resources>']
    for oid, (nm, m) in enumerate(its, start=1):
        pts, fcs = m.Topology
        md.append('<object id="%d" type="model" name="%s"><mesh><vertices>' % (oid, nm))
        md += ['<vertex x="%.4f" y="%.4f" z="%.4f"/>' % (q.x, q.y, q.z) for q in pts]
        md.append('</vertices><triangles>')
        md += ['<triangle v1="%d" v2="%d" v3="%d"/>' % (f[0], f[1], f[2]) for f in fcs]
        md.append('</triangles></mesh></object>')
    md.append('</resources><build>')
    md += ['<item objectid="%d" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>' % oid for oid in range(1, len(its) + 1)]
    md.append('</build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', ct)
        z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', NL.join(md))


plate = OUT / (PREFIX + 'CouponPlate_1-piece.3mf')
write_3mf(str(plate), 'Gladiator head coupon R3d', items)
xml = zipfile.ZipFile(str(plate)).read('3D/3dmodel.model').decode()
vol = sum(m.Volume for _, m in items)
report['plate'] = {'file': plate.name, 'objects': xml.count('<object '), 'offbed': offbed, 'overlaps': overlaps,
                   'triangles_ok': xml.count('<triangle ') == sum(len(m.Topology[1]) for _, m in items),
                   'volume_cm3': round(vol / 1000, 2), 'grams_pla': round(vol * 0.00124, 1)}
report['all_pass'] = all(r['pass'] for r in report['pieces']) and offbed == 0 and overlaps == 0 \
    and report['plate']['triangles_ok']
(OUT / 'validation.json').write_text(json.dumps(report, indent=2) + NL)
LOG.append('plate: %.1f cm3, %.0f g, offbed %d, overlaps %d, triangles ok %s  ->  %s' % (
    vol / 1000, vol * 0.00124, offbed, overlaps, report['plate']['triangles_ok'],
    'ALL PASS' if report['all_pass'] else '*** NOT ALL PASS'))
print(NL.join(LOG))
