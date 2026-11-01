"""Tilt yoke v2 + 45-degree tapers under the plate ledges (Jim 2026-11-01: weak joint where the plate meets the
column, and support warnings on the flat ledges). Run on cad-lab: python3 build_yoke_gussets.py
Source: balance-tensioner-20261030/Gladiator_Head_v2_Balanced.FCStd (current head). Output in this folder."""
import sys, os, json, math, hashlib
sys.path.append('/usr/lib/freecad/lib')
from pathlib import Path
import FreeCAD as A, Part, Mesh, MeshPart
V = A.Vector
HERE = Path(__file__).resolve().parent
V2 = HERE.parent
BAL = V2 / 'balance-tensioner-20261030/Gladiator_Head_v2_Balanced.FCStd'
VAL = json.load(open(V2 / 'validation.json'))['v2']
STAGED = Path('/home/buralien/3D-Printer/Incoming/Gladiator_Masthead_v2_20261031/04_Tilt_Yoke.stl')
d = A.openDocument(str(BAL))
objs = {o.Name: o for o in d.Objects if o.TypeId == 'Part::Feature' and o.Shape.Solids}
TAX = V(*VAL['tilt_axis_world'])
Ty, Tz = TAX.y, TAX.z
tilt = [n for n in objs if any(n == g for g in VAL['groups']['tilt'])]
Y0 = objs['Tilt_Yoke'].Shape.copy()
R = {'source': str(BAL.relative_to(V2.parent.parent.parent)), 'tilt_parts': tilt}

# 1) the staged STL must be this same yoke (same pose, floor on the bed)
st = Mesh.Mesh(str(STAGED)); sb = st.BoundBox; yb = Y0.BoundBox
R['staged_stl_vs_cad'] = {'stl_size': [round(sb.XLength, 2), round(sb.YLength, 2), round(sb.ZLength, 2)],
                          'cad_size': [round(yb.XLength, 2), round(yb.YLength, 2), round(yb.ZLength, 2)],
                          'stl_vol': round(st.Volume, 1), 'cad_vol': round(Y0.Volume, 1)}
assert abs(sb.XLength - yb.XLength) < 0.05 and abs(sb.ZLength - yb.ZLength) < 0.05 and abs(st.Volume - Y0.Volume) < 0.01 * Y0.Volume

# 2) the sweep check must reproduce the known first contacts (receiver at -40, camera tray at +36)
def posed(n, a):
    s = objs[n].Shape.copy(); s.rotate(TAX, V(1, 0, 0), a); return s
R['sanity_known_contacts'] = {
    'receiver_at_-40_mm3': round(posed('GH44_Tilt_Receiver', -40).common(Y0).Volume, 2),
    'camera_tray_at_+36_mm3': round(posed('Camera_Tray', 36).common(Y0).Volume, 2)}
assert R['sanity_known_contacts']['receiver_at_-40_mm3'] > 0 and R['sanity_known_contacts']['camera_tray_at_+36_mm3'] > 0

# 3) tapers: from each column edge up to the plate edge at 45 deg, through the plate thickness
X0 = TAX.x
FEAT = {'pivot_tower': dict(x0=X0 + 28, x1=X0 + 33, jz=Tz - 10.0, col=3.0, plate=9.0),
        'ear_plate': dict(x0=X0 - 2.8, x1=X0 + 0.2, jz=Tz - 12.0, col=3.0, plate=10.0)}


def wedge(f, s):
    w = f['plate'] - f['col']
    y0, y1 = Ty + s * (f['col'] - 0.3), Ty + s * f['plate']        # 0.3 into the column so it fuses
    zb = f['jz'] - (f['plate'] - f['col'] + 0.3)
    pts = [V(f['x0'], y0, zb), V(f['x0'], y0, f['jz'] + 0.3), V(f['x0'], y1, f['jz'] + 0.3), V(f['x0'], y1, f['jz']), V(f['x0'], y0, zb)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(f['x1'] - f['x0'], 0, 0))


W = [wedge(f, s) for f in FEAT.values() for s in (-1, 1)]
add = W[0].fuse(W[1:]).cut(Y0)
R['added_mm3'] = round(add.Volume, 1)
Y1 = Y0.fuse(W).removeSplitter()
assert Y1.isValid() and len(Y1.Solids) == 1

# 4) full sweep, every degree -40..+36: the NEW yoke may touch the tilt parts only where the OLD one did
new_hits = []
min_gap = {}
for a in range(-40, 37):
    for n in tilt:
        p = posed(n, a)
        if not p.BoundBox.intersect(add.BoundBox):
            continue
        v_add = p.common(add).Volume
        if v_add > 0.001:
            new_hits.append((a, n, round(v_add, 3)))
        if a % 4 == 0:
            g = p.distToShape(add)[0]
            min_gap[n] = min(min_gap.get(n, 99), g)
R['new_contacts_from_tapers'] = new_hits
R['closest_tilt_part_to_tapers_mm'] = {k: round(v, 1) for k, v in sorted(min_gap.items(), key=lambda kv: kv[1])[:5]}
assert not new_hits

# 5) other (non-tilt) parts: no new overlap
other = [n for n in objs if n not in tilt and not n.startswith('Tilt_Yoke')]
R['new_overlap_with_other_parts'] = sorted(n for n in other if objs[n].Shape.BoundBox.intersect(add.BoundBox) and objs[n].Shape.common(add).Volume > 0.01)

# 6) joint section just above the old junction, before / after (mm2, horizontal cut through each plate)
def section(shape, f, z):
    box = Part.makeBox(f['x1'] - f['x0'] + 0.02, 40, 0.1, V(f['x0'] - 0.01, Ty - 20, z))
    return round(shape.common(box).Volume / 0.1, 1)
R['section_mm2'] = {k: {'old_at_junction': section(Y0, f, f['jz'] - 0.2), 'new_at_junction': section(Y1, f, f['jz'] - 0.2),
                        'new_3mm_lower': section(Y1, f, f['jz'] - 3.2)} for k, f in FEAT.items()}

# 7) export: same pose as the staged STL (min corner at 0)
p = Y1.copy(); bb = p.BoundBox; p.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
(HERE / 'stl').mkdir(exist_ok=True)
p.exportStep(str(HERE / 'Tilt_Yoke_v2_Tapered.step'))
m = MeshPart.meshFromShape(Shape=p, LinearDeflection=0.02, AngularDeflection=0.2, Relative=False)
out = HERE / 'stl/Gladiator_Head_v2_Tilt_Yoke_Tapered.stl'
m.write(str(out))
R['stl_closed'] = bool(m.isSolid()) and not m.hasNonManifolds()
R['stl_sha256'] = hashlib.sha256(out.read_bytes()).hexdigest()
R['mass_g_pla_solid_est'] = [round(Y0.Volume * 1.24e-3, 2), round(Y1.Volume * 1.24e-3, 2)]
(HERE / 'validation.json').write_text(json.dumps(R, indent=1))
print(json.dumps(R, indent=1), flush=True)
os._exit(0)
