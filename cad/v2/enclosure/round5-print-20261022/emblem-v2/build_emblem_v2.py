"""Stronger white shield emblems (Claude, 2026-10-22). Read-only on the Round 5 CAD; writes cad/v2/enclosure/round5-print-20261022/emblem-v2/.

Jim: both printed white shield insets came out poorly; they must be inherently stronger and still fit the red shields he has.
Round 5 emblem: 1.0 mm thick curved lattice (R27.6..R28.6), 0.4 mm of it in the red field's recess, strokes 1.15 mm, feathers 1.65 mm,
printed standing on its lower edge with tree supports (thin strokes built up as stacked 1 mm slivers).
v2, same mounting, same red field, same boss and screw:
  * base layer (R27.6..R28.0) fills the red field's recess to 0.05 mm per side (was 0.15): bolts 1.35, feathers 1.85, ring 2.9..5.1
  * top layer (R28.0..R29.4) sits on the red surface and is wider: bolts 1.75, feathers 2.25, ring 2.7..5.4, rim 0.5 mm wider inward
  * 1.8 mm thick in total (was 1.0): bending stiffness about 6x, and the strokes are wider
  * prints lying on its back (concave side down, the visible face up) on snug supports, so every stroke is laid down along its length
The silk boss and the M2 x 6 screw are unchanged: the boss sits 0.8 mm higher and the screw still reaches the insert.
"""
import FreeCAD as A, Part, MeshPart, math, json, os
from pathlib import Path

V = A.Vector
SRC = '/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-print-20261022/Gladiator_Round5_Print.FCStd'
OUT = Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-print-20261022/emblem-v2')
OUT.mkdir(parents=True, exist_ok=True)


def clean(s):
    q = Part.Shape()
    q.importBrepFromString(s.exportBrepToString())
    if len(q.Solids) == 1:
        q = q.Solids[0]
    return q


def fuse(*ss):
    s = clean(ss[0])
    for q in ss[1:]:
        s = clean(s.fuse(clean(q), .00001))
    try:
        s = s.removeSplitter()
    except Part.OCCError:
        pass
    return clean(s)


def cut(s, *ss):
    s = clean(s)
    for q in ss:
        s = clean(s.cut(clean(q)))
    try:
        s = s.removeSplitter()
    except Part.OCCError:
        pass
    return clean(s)


def common(a, b):
    return clean(clean(a).common(clean(b)))


def poly(pts, z0, z1):
    vs = [V(x, y, z0) for x, y in pts]
    return Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(V(0, 0, z1 - z0))


def disk(x, y, r, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))


def strokeline(pts, w, z0, z1):
    ss = []
    for p, q in zip(pts, pts[1:]):
        dx, dy = q[0] - p[0], q[1] - p[1]
        l = math.hypot(dx, dy)
        nx, ny = -dy / l * w / 2, dx / l * w / 2
        ss.append(poly([(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny), (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)], z0, z1))
    for x, y in pts:
        ss.append(disk(x, y, w / 2, z0, z1))
    return fuse(*ss)


def feather(root, tip, width, z0, z1):
    r = V(*root, z0)
    t = V(*tip, z0)
    d = t - r
    n = V(-d.y, d.x, 0)
    n.normalize()
    n *= width / 2
    p = r + d * .20 + n * .7
    q = r + d * .68 + n
    t2 = t - d * .08 + n * .18
    a = Part.BezierCurve()
    a.setPoles([r, p, q, t])
    b = Part.BezierCurve()
    b.setPoles([t, t2 - d * .05 - n * .8, r + d * .22 - n, r])
    return Part.Face(Part.Wire([a.toShape(), b.toShape()])).extrude(V(0, 0, z1 - z0))


def frame(origin, U, N):
    U = V(*U)
    N = V(*N)
    W = V(0, 0, 1)
    assert (U.cross(W) - N).Length < 1e-6
    return A.Placement(V(*origin), A.Rotation(U, W, N, 'ZXY'))


def world(s, f):
    s = clean(s)
    s.Placement = f.multiply(s.Placement)
    return clean(s)


w, h = 27.3, 41.6
outline = [(-w / 2 + 2, -h / 2), (w / 2 - 2, -h / 2), (w / 2, -h / 2 + 2), (w / 2, h / 2 - 2), (w / 2 - 2, h / 2), (-w / 2 + 2, h / 2), (-w / 2, h / 2 - 2), (-w / 2, -h / 2 + 2)]
cycenter = 6.25 - 28.0


def cyl(radius):
    return Part.makeCylinder(radius, h + 8, V(0, -h / 2 - 4, cycenter), V(0, 1, 0))


R_IN, R_FIELD, R_TOP = 27.6, 28.0, 29.4
P = dict(base=dict(rim_scale=(0.837, 0.895), ring=(2.9, 5.1), bolt=1.35, feather=1.85, arrow_pad=0.20),
         top=dict(rim_scale=(0.810, 0.875), ring=(2.7, 5.4), bolt=1.75, feather=2.25, arrow_pad=0.50),
         radii=dict(back=R_IN, field_surface=R_FIELD, top=R_TOP), centre_hole_r=1.3)


def pattern(q):
    rim = cut(poly(outline, 0, 10), poly([(x * q['rim_scale'][0], y * q['rim_scale'][1]) for x, y in outline], -.1, 10.1))
    ring = cut(disk(0, 0, q['ring'][1], 0, 10), disk(0, 0, q['ring'][0], -.1, 10.1))
    parts = [rim, ring]
    for sx in (-1, 1):
        for sy in (-1, 1):
            pts = [(sx * 3, sy * 3), (sx * 6, sy * 7), (sx * 4.8, sy * 9), (sx * 8.5, sy * 13), (sx * 8, sy * 15), (sx * 11.9, sy * 19.5)]
            parts.append(strokeline(pts, q['bolt'], 0, 10))
            arr = [(sx * 11.9, sy * 19.9), (sx * 8.2, sy * 18.3), (sx * 11.6, sy * 15.7)]
            parts.append(fuse(poly(arr, 0, 10), strokeline(arr + [arr[0]], q['arrow_pad'], 0, 10)))
        for j in range(4):
            parts.append(feather((sx * 3.5, 1.5 + j * .45), (sx * (11.8 - j * .65), 5.5 + j * 1.55), q['feather'], 0, 10))
    return fuse(*parts)


base = common(pattern(P['base']), cut(cyl(R_FIELD), cyl(R_IN)))
top = common(pattern(P['top']), cut(cyl(R_TOP), cyl(R_FIELD)))
top = common(top, poly(outline, -1, 11))                     # nothing overhangs the red field's outer edge
white = cut(fuse(base, top), disk(0, 0, P['centre_hole_r'], 0, 11))

r5 = A.openDocument(SRC)
rep = dict(parameters=P, local=dict(valid=white.isValid(), solids=len(white.Solids), volume_mm3=round(white.Volume, 1)))
old_local_vol = None
for side, cx in (('L', 16), ('R', 63)):
    f = frame((cx, 148, 79), (-1, 0, 0), (0, 1, 0))
    wnew = world(white, f)
    field = clean(r5.getObject('Scutum_Field_' + side).Shape)
    old = clean(r5.getObject('Scutum_Emblem_' + side).Shape)
    boss = clean(r5.getObject('Scutum_Boss_' + side).Shape)
    panel = clean(r5.getObject('Front_Left' if side == 'L' else 'Front_Right').Shape)
    # the boss is 0.8 mm higher on the thicker emblem: move it out along the shield normal (world +Y) to check it
    boss_up = clean(boss)
    boss_up.translate(V(0, R_TOP - 28.6, 0))
    rep[side] = dict(old_volume=round(old.Volume, 1), new_volume=round(wnew.Volume, 1),
                     new_vs_red_field_overlap_mm3=round(wnew.common(field).Volume, 4), new_to_red_field_gap_mm=round(wnew.distToShape(field)[0], 3),
                     new_vs_panel_overlap_mm3=round(wnew.common(panel).Volume, 4),
                     raised_boss_vs_new_overlap_mm3=round(boss_up.common(wnew).Volume, 4), raised_boss_gap_mm=round(boss_up.distToShape(wnew)[0], 3),
                     old_emblem_inside_new_mm3=round(old.common(wnew).Volume, 1))
    if side == 'L':
        doc = A.newDocument('Emblem_v2')
    o = doc.addObject('Part::Feature', 'Scutum_Emblem_v2_' + side)
    o.Shape = wnew
# print orientation: local frame as is (cylinder axis along Y, visible face up), lying on its concave back
pr = clean(white)
b = pr.BoundBox
pr.translate(V(-b.XMin, -b.YMin, -b.ZMin))
m = MeshPart.meshFromShape(Shape=pr, LinearDeflection=.01, AngularDeflection=.06, Relative=False)
m.write(str(OUT / 'Scutum_Emblem_v2.stl'))
rep['stl'] = dict(file='Scutum_Emblem_v2.stl', is_solid=m.isSolid(), non_manifold=m.hasNonManifolds(),
                  size_mm=[round(pr.BoundBox.XLength, 2), round(pr.BoundBox.YLength, 2), round(pr.BoundBox.ZLength, 2)],
                  orientation='lying on its concave back, visible face up; edges on the bed, crown 3.6 mm up on supports')
doc.recompute()
doc.saveAs(str(OUT / 'Scutum_Emblem_v2.FCStd'))
(OUT / 'validation.json').write_text(json.dumps(rep, indent=1, default=str))
print(json.dumps(rep, indent=1, default=str), flush=True)
os._exit(0)
