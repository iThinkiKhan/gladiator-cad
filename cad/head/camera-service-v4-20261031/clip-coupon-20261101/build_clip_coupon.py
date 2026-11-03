"""Camera case v4 plug-clip test coupon (2026-11-01).

Jim: "im not sure about these retention clips, lets get a coupon ready to test".
Rebuilds v4 geometry (into /tmp, v4 files untouched) and cuts:
  - three plug clips, pocket 2.56 / 2.66 (as designed) / 2.76 mm, marked with 1 / 2 / 3 notches;
  - a plug-gap coupon: the bottom of the v4 tray (floor 1.2 mm, backstop pads, corner board seats, wire exits),
    cut 0.6 mm above the board seat, cover lugs and snap bumps removed.
Run on cad-lab from the repo root:  python3 cad/head/camera-service-v4-20261031/clip-coupon-20261101/build_clip_coupon.py
"""
import json, sys, hashlib
from pathlib import Path
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A
import Part

ROOT = Path('/home/buralien/projects/gladiator-cad')
V4 = ROOT / 'cad/head/camera-service-v4-20261031'
OUT = V4 / 'clip-coupon-20261101'
TMP = Path('/tmp/clip_coupon_v4_rebuild')
TMP.mkdir(parents=True, exist_ok=True)
(OUT / 'stl').mkdir(parents=True, exist_ok=True)

src = (V4 / 'generated-build.py').read_text()
old = "OUT = ROOT / 'cad/head/camera-service-v4-20261031'"
assert src.count(old) == 1
src = src.replace(old, "OUT = Path('%s')" % TMP)
ns = {'__name__': '__coupon__'}
exec(compile(src, str(TMP / 'generated-build.py'), 'exec'), ns)
g = ns.__getitem__
lbox, xs, mesh = g('lbox'), g('xs'), g('mesh')
HOUS, CL_IN, CL_OUT, CL_END_OUT, CL_END = g('HOUS'), g('CL_IN'), g('CL_OUT'), g('CL_END_OUT'), g('CL_END')
TOOTH, SPINE_IN = g('TOOTH'), g('SPINE_IN')
Y_CL0, Y_CLB, Y_DEND, Y_BACK, Y_FLOOR_IN = g('Y_CL0'), g('Y_CLB'), g('Y_DEND'), g('Y_BACK'), g('Y_FLOOR_IN')
CL_Z0, CL_Z1, PIN_Z, ROWS = g('CL_Z0'), g('CL_Z1'), g('PIN_Z'), g('ROWS')
OX0, OX1, OZ0, OZ1 = g('OX0'), g('OX1'), g('OZ0'), g('OZ1')
tray, clips, backstops = g('tray'), g('clips'), g('backstops')
rep = {'request': 'plug clip test coupon', 'v4_rebuilt_from': str(V4 / 'generated-build.py'), 'checks': {}}
C = rep['checks']


def clip(px, so, e):
    """v4 clip with the pocket widened by 2e; wall thicknesses unchanged (the outside grows by e per side)."""
    c_ = lbox(*xs(px, so, -(HOUS + CL_END_OUT) - e, HOUS + CL_IN + e), Y_CL0, Y_CLB, CL_Z0, CL_Z1)
    c_ = c_.fuse(lbox(*xs(px, so, -(HOUS + CL_OUT) - e, -(HOUS + CL_END_OUT) - e + .01), Y_CL0, Y_DEND, CL_Z0 + CL_END + .3, CL_Z1 - CL_END - .3))
    c_ = c_.cut(lbox(*xs(px, so, -HOUS - .03 - e, HOUS + .03 + e), Y_CL0 - .1, Y_DEND, CL_Z0 + CL_END - .05, CL_Z1 - CL_END + .05))
    hw_ = (2.54 - TOOTH) / 2
    for pz in PIN_Z:
        c_ = c_.cut(lbox(*xs(px, so, -(HOUS + CL_OUT) - .2 - e, SPINE_IN), Y_DEND - .05, Y_CLB + .1, pz - hw_, pz + hw_))
    return c_.removeSplitter()


def to_bed(s):
    """Print orientation: rotate -90 deg about x (local +y = rear goes down), then sit on z = 0 at the origin."""
    s = s.copy()
    s.rotate(A.Vector(0, 0, 0), A.Vector(1, 0, 0), -90)
    b = s.BoundBox
    s.translate(A.Vector(-b.XMin, -b.YMin, -b.ZMin))
    return s


px, so = ROWS[1]
nominal = clip(px, so, 0.0)
C['nominal_clip_matches_v4_clip_mm3'] = round(abs(nominal.Volume - clips[1].Volume) + nominal.cut(clips[1]).Volume, 6)
assert C['nominal_clip_matches_v4_clip_mm3'] < 1e-4, 'nominal coupon clip is not the v4 clip'

parts, variants = {}, []
for n, (label, pocket) in enumerate([('tight', 2.56), ('as_designed', 2.66), ('loose', 2.76)], start=1):
    e = (pocket - 2.66) / 2
    c_ = clip(px, so, e)
    # n notches, 0.6 wide x 0.8 deep, across the inner plate at the open (top-in-print) edge
    x0, x1 = xs(px, so, HOUS + .03 + e - .1, HOUS + CL_IN + e + .1)
    zc = (CL_Z0 + CL_Z1) / 2
    for k in range(n):
        z = zc + (k - (n - 1) / 2) * 1.6
        c_ = c_.cut(lbox(x0, x1, Y_CL0 - .1, Y_CL0 + .8, z - .3, z + .3))
    c_ = c_.removeSplitter()
    assert c_.isValid() and len(c_.Solids) == 1, label
    name = '0%d_Clip_%s_pocket_%.2f_%d_notch%s' % (n, label, pocket, n, 'es' if n > 1 else '')
    b = to_bed(c_)
    parts[name] = b
    variants.append({'file': name + '.stl', 'notches': n, 'pocket_width_mm': pocket, 'pocket_length_mm': round(CL_Z1 - CL_Z0 - 2 * CL_END + .1, 2),
                     'volume_mm3': round(c_.Volume, 1), 'print_size_mm': [round(b.BoundBox.XLength, 2), round(b.BoundBox.YLength, 2), round(b.BoundBox.ZLength, 2)],
                     'outer_wall_mm': [round(CL_END_OUT - .03, 2), round(CL_OUT - .03, 2)], 'inner_plate_mm': round(CL_IN - .03, 2)})
rep['clips'] = variants

# ---- plug-gap coupon: bottom of the v4 tray
FLOOR_KEEP, SEAT_LIP = 1.2, 0.6
keep = lbox(OX0, OX1, Y_BACK - SEAT_LIP, Y_FLOOR_IN + FLOOR_KEEP, OZ0, OZ1)
gap = tray.common(keep).removeSplitter()
sols = sorted(gap.Solids, key=lambda s: -s.Volume)
C['gap_coupon_loose_bits_mm3'] = round(sum(s.Volume for s in sols[1:]), 4)
gap = sols[0]
assert gap.isValid()
bs = Part.makeCompound(backstops)
board = g('board_comp')
clip_cmp = Part.makeCompound(clips)
C['pads_kept_mm3_missing'] = round(bs.Volume - bs.common(gap).Volume, 6)
C['board_vs_coupon_mm3'] = round(board.common(gap).Volume, 6)
C['clips_vs_coupon_mm3'] = round(clip_cmp.common(gap).Volume, 6)
C['plugs_vs_coupon_mm3'] = round(max(d.common(gap).Volume for d in g('dups')), 6)
C['wires_vs_coupon_mm3'] = round(max(w.common(gap).Volume for w in g('wire_shapes')), 6)
C['clip_rear_to_pads_mm'] = round(clip_cmp.distToShape(bs)[0], 3)
# the board's back face rests on the corner seats at y = Y_BACK
seat_faces = [f for f in gap.Faces if abs(f.CenterOfMass.y - Y_BACK) < 1e-6 and abs(abs(f.normalAt(0, 0).y) - 1) < 1e-6]
C['board_seat_faces'] = len(seat_faces)
C['board_seat_area_mm2'] = round(sum(f.Area for f in seat_faces), 2)
C['seat_to_floor_mm'] = round(Y_FLOOR_IN - Y_BACK, 3)
C['seat_lip_mm'] = SEAT_LIP
C['floor_mm'] = FLOOR_KEEP
assert C['pads_kept_mm3_missing'] < 1e-4 and C['board_vs_coupon_mm3'] < 1e-4 and C['clips_vs_coupon_mm3'] < 1e-4
assert C['plugs_vs_coupon_mm3'] < 1e-4 and C['wires_vs_coupon_mm3'] < 1e-4 and C['board_seat_faces'] == 4
gb = to_bed(gap)
# preview only: board, plugs, wires and the v4 clips placed on the coupon (same rotation and shift)
_r = gap.copy(); _r.rotate(A.Vector(0, 0, 0), A.Vector(1, 0, 0), -90); _b = _r.BoundBox; _sh = A.Vector(-_b.XMin, -_b.YMin, -_b.ZMin)
(OUT / 'preview').mkdir(exist_ok=True)
for nm, shp in (('board', board), ('plugs', Part.makeCompound(g('dups'))), ('wires', Part.makeCompound(g('wire_shapes'))), ('clips', clip_cmp)):
    q = shp.copy(); q.rotate(A.Vector(0, 0, 0), A.Vector(1, 0, 0), -90); q.translate(_sh)
    mesh(q).write(str(OUT / 'preview' / ('on_coupon_%s.stl' % nm)))
parts['04_Plug_Gap_Tray_Coupon'] = gb
rep['gap_coupon'] = {'file': '04_Plug_Gap_Tray_Coupon.stl', 'volume_mm3': round(gap.Volume, 1), 'v4_tray_volume_mm3': round(tray.Volume, 1),
                     'print_size_mm': [round(gb.BoundBox.XLength, 2), round(gb.BoundBox.YLength, 2), round(gb.BoundBox.ZLength, 2)]}

hashes = {}
for name, s in parts.items():
    fn = OUT / 'stl' / (name + '.stl')
    mesh(s).write(str(fn))
    hashes[fn.name] = hashlib.sha256(fn.read_bytes()).hexdigest()
rep['stl_sha256'] = hashes
rep['total_volume_mm3'] = round(sum(s.Volume for s in parts.values()), 1)
rep['pla_grams_solid'] = round(rep['total_volume_mm3'] * 1.24e-3, 1)
Part.export(list(parts.values()), str(OUT / 'Clip_Coupon_parts_print_orientation.step'))
(OUT / 'coupon_checks.json').write_text(json.dumps(rep, indent=1))
print(json.dumps(rep, indent=1))
