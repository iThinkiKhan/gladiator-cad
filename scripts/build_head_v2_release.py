"""Gladiator masthead v2 - RELEASE build. THE one script for the current head (consolidated 2026-11-01).

Starts from the v2 base (scripts/build_head_v2_mast.py -> cad/head/v2-mast-20261028/Gladiator_Head_v2_Mast.FCStd)
and applies every later change, in order, as numbered steps:
  1. Tilt balance + M3x20 tensioner   (was balance-tensioner-20261030)
  2. Pan-servo lead path, neck + tube  (was pcb-floor-20261030; its rejected yoke PCB pocket is NOT applied)
  3. Solid tube, slot filled, top window (was solid-tube-20261101)
  4. Yoke 45-degree tapers            (was yoke-taper-20261101)
Every print STL gets the bed chamfer (0.5 mm on hole edges on the bed, Jim 2026-10-15); the patch folders had
dropped it for the neck, tube, yoke and receiver.

FUTURE CHANGES GO HERE AS A NEW STEP, NOT A NEW FOLDER.

Run on cad-lab:  python3 scripts/build_head_v2_release.py [--quick]   (--quick skips the long motion sweep)
Output: cad/head/v2-mast-20261028/release/ (assembly FCStd + STEP, 7 print STLs, validation.json, MANIFEST.json)
"""
import sys, os, json, math, hashlib
sys.path.append('/usr/lib/freecad/lib')
from pathlib import Path
import FreeCAD as A, Part, Mesh, MeshPart

V = A.Vector
ROOT = Path(__file__).resolve().parent.parent
V2 = ROOT / 'cad/head/v2-mast-20261028'
OUT = V2 / 'release'
(OUT / 'stl').mkdir(parents=True, exist_ok=True)
QUICK = '--quick' in sys.argv
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
BASE_FC = V2 / 'Gladiator_Head_v2_Mast.FCStd'
base_val = json.loads((V2 / 'validation.json').read_text())['v2']
p = base_val['params']
T = V(*base_val['tilt_axis_world'])
G = {k: list(v) for k, v in base_val['groups'].items()}
R = {'base': str(BASE_FC.relative_to(ROOT)), 'base_sha256': sha(BASE_FC), 'script_sha256': sha(__file__), 'steps': {}, 'checks': {}}

src = A.openDocument(str(BASE_FC))
S = {o.Name: o.Shape.copy() for o in src.Objects if o.TypeId == 'Part::Feature'}
GROUP = {o.Name: o.getParentGroup().Name for o in src.Objects if o.TypeId == 'Part::Feature'}
ROBOT = {n for n, g in GROUP.items() if g == 'Robot_Context'}
ORIG = {n: s.copy() for n, s in S.items()}
A.closeDocument(src.Name)


def ov(a, b):
    return a.common(b).Volume if a.BoundBox.intersect(b.BoundBox) else 0.0


def signature(s):
    return (round(s.Volume, 4), round(s.Area, 4), len(s.Faces), len(s.Edges),
            sorted(tuple(round(c, 4) for c in (v.Point.x, v.Point.y, v.Point.z)) for v in s.Vertexes))


def xor(a, b):
    """0 when identical. Fingerprint first: a boolean of two identical detailed solids is very slow and can run
    cad-lab out of memory (2026-11-01). Only parts whose fingerprint differs get the real boolean difference."""
    if signature(a) == signature(b):
        return 0.0
    return a.cut(b).Volume + b.cut(a).Volume


# ============================================================ STEP 1: tilt balance + M3x20 tensioner
SHIFT = 2.5                                    # payload moved 2.5 mm rearward; receiver front shortened to match
tilt, pan, fixed = G['tilt'], G['pan'], G['fixed']
payload = [n for n in tilt if n not in ('GH44_Tilt_Receiver', 'Tilt_Horn_Reference')]
plane = T.y - 15
rec = S['GH44_Tilt_Receiver']
fore = rec.common(Part.makeBox(200, 200, 200, V(T.x - 100, plane - 200, T.z - 100)))
aft = rec.common(Part.makeBox(200, 200, 200, V(T.x - 100, plane, T.z - 100)))
fore.translate(V(0, SHIFT, 0)); rec = aft.fuse(fore).removeSplitter()


def padded_box(x, y, z, dx, dy, dz, pad=.4):
    return Part.makeBox(dx + 2 * pad, dy + 2 * pad, dz + 2 * pad, T + V(x - pad, y - pad, z - pad))


def padded_cx(r, x, length, pad=.4):
    return Part.makeCylinder(r + pad, length + 2 * pad, T + V(x - pad, 0, 0), V(1, 0, 0))


servo_bits = [padded_box(-2.8, -6, -5.9, 17.5, 12, 22.8), padded_box(-5.3, -6, -10.8, 2.5, 12, 32.6),
              padded_box(-11.3, -6, -5.9, 6, 12, 16.9), padded_cx(5.5, -13.8, 2.5), padded_cx(2.4, -17.3, 3.5)]
servo_offset = servo_bits[0]
for b_ in servo_bits[1:]:
    servo_offset = servo_offset.fuse(b_)
yoke_bits = [padded_box(-2.8, -10, -12, 3, 20, 35), padded_box(-12, -3, -47, 12.2, 6, 35)]
yoke_offset = yoke_bits[0].fuse(yoke_bits[1])
for t in range(-38, 35):
    for b_ in (yoke_offset, servo_offset):
        cut = b_.copy(); cut.rotate(T, V(1, 0, 0), -t)
        if ov(rec, cut) > .0001:
            rec = rec.cut(cut).removeSplitter()
bb = ORIG['Tilt_Horn_Reference'].BoundBox
horn_zone = Part.makeBox(bb.XLength + 4, bb.YLength + 4, bb.ZLength + 4, V(bb.XMin - 2, bb.YMin - 2, bb.ZMin - 2))
rec = rec.cut(horn_zone).fuse(ORIG['GH44_Tilt_Receiver'].common(horn_zone)).removeSplitter()
assert rec.isValid() and len(rec.Solids) == 1
S['GH44_Tilt_Receiver'] = rec
for n in payload:
    S[n].translate(V(0, SHIFT, 0))


def frame(shape):
    s = shape.copy(); s.rotate(V(), V(0, 0, 1), -45); s.translate(V(39.5, 113, p['LIFT'])); return s


PAD, ZT = p['PAD_Y0'], p['TS_Z']
screw = frame(Part.makeCylinder(1.5, 20, V(0, PAD - 20, ZT), V(0, 1, 0)).fuse(Part.makeCylinder(3, 3, V(0, PAD - 23, ZT), V(0, 1, 0))))


def nut_at(C):
    outer = -C - 5.5 + p['LUG_IN'] - 7
    cy = outer + 3.5; rr = 5.8 / math.sqrt(3)
    vs = [V(rr * math.cos(math.radians(30 + 60 * k)), cy - 1.2, ZT + rr * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    nut = Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(V(0, 2.4, 0))
    return frame(nut.cut(Part.makeCylinder(1.5, 2.6, V(0, cy - 1.3, ZT), V(0, 1, 0))))


S['Tensioner_M3x20_Envelope'] = screw
S['Tensioner_Nut_Envelope'] = nut_at(p['C_NOM'])
GROUP['Tensioner_M3x20_Envelope'] = GROUP['Tensioner_Nut_Envelope'] = 'Hardware'
fixed = fixed + ['Tensioner_M3x20_Envelope', 'Tensioner_Nut_Envelope']
# must equal what balance-tensioner-20261030 produced
bal = A.openDocument(str(V2 / 'balance-tensioner-20261030/Gladiator_Head_v2_Balanced.FCStd'))
diff1 = {o.Name: round(xor(S[o.Name], o.Shape), 4) for o in bal.Objects
         if o.TypeId == 'Part::Feature' and o.Name in S and o.Name not in ROBOT}
R['steps']['1_balance_tensioner'] = {'matches_balance_folder_xor_mm3_max': max(diff1.values()),
                                     'parts_compared': len(diff1)}
assert max(diff1.values()) < 0.01, {k: v for k, v in diff1.items() if v >= 0.01}
A.closeDocument(bal.Name)
print('step 1 ok', flush=True)

# ============================================================ STEP 2: pan-servo lead path through neck and tube
AX = V(39.5, 113.0, 0)
C_NOM, C_MIN, C_MAX, SHAFT_NEAR = 44.0, 38.0, 48.0, 5.9
UDIR = V(-math.sqrt(0.5), -math.sqrt(0.5), 0)
LEAD_W = 8.4                                   # plug 7.6 + clearance
TUN_Z0, TUN_Z1 = 145.0, 148.6                  # closed tunnel through the collar wall; flange Z 144..150
SLOT_Z0 = 143.0
GROOVE = (28.3, 32.0, 5.6, 143.0, 158.5)


def rbox(r0, r1, w, z0, z1):
    s = Part.makeBox(r1 - r0, w, z1 - z0, V(r0, -w / 2, z0)); s.rotate(V(), V(0, 0, 1), 225.0); s.translate(AX); return s


neck0, tube0 = S['Neck_Main'], S['Mast_Tube_v2']
assert neck0.common(rbox(GROOVE[0] - 1.5, GROOVE[0], GROOVE[2], 151, GROOVE[4])).Volume > 0.9 * 1.5 * GROOVE[2] * (GROOVE[4] - 151)
neck = neck0.cut(rbox(3.0, 27.0, LEAD_W, TUN_Z0, TUN_Z1)).cut(rbox(14.5, 27.0, LEAD_W, SLOT_Z0, TUN_Z1)).cut(rbox(*GROOVE)).removeSplitter()
tube = tube0.cut(rbox(3.0, 11.0, LEAD_W, TUN_Z0 - 0.2, 151.0)).removeSplitter()
assert neck.isValid() and tube.isValid() and len(tube.Solids) == 1
S['Neck_Main'], S['Mast_Tube_v2'] = neck, tube
plug = rbox(4.0, 33.0, 7.8, TUN_Z0 + 0.3, TUN_Z0 + 3.0)
pcb = A.openDocument(str(V2 / 'pcb-floor-20261030/Gladiator_Head_v2_PCB_Floor.FCStd'))
R['steps']['2_pan_lead'] = {'neck_xor_vs_pcb_floor_mm3': round(xor(neck, pcb.getObject('Neck_Main').Shape), 4),
                            'tube_xor_vs_pcb_floor_mm3': round(xor(tube, pcb.getObject('Mast_Tube_v2').Shape), 4),
                            'plug_path_hits': sorted(n for n in ('Neck_Main', 'Mast_Tube_v2') if ov(plug, S[n]) > 0.01)}
pan_lead_route = pcb.getObject('Pan_Lead_Route').Shape.copy()
A.closeDocument(pcb.Name)
assert R['steps']['2_pan_lead']['neck_xor_vs_pcb_floor_mm3'] < 0.01 and R['steps']['2_pan_lead']['tube_xor_vs_pcb_floor_mm3'] < 0.01
assert not R['steps']['2_pan_lead']['plug_path_hits']
print('step 2 ok', flush=True)

# ============================================================ STEP 3: solid tube (slot filled) + top wire window
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, AX + V(x0, y0, z0))


ring = Part.makeCylinder(10, 144, AX + V(0, 0, 6)).cut(Part.makeCylinder(6, 146, AX + V(0, 0, 5)))
t1 = S['Mast_Tube_v2'].fuse(ring.common(box(-3.6, 3.6, -10.5, -4.0, 21.9, 142.1))).removeSplitter()
WIN_TOP = (90.0, 102.0)                        # inside the body under the top panel (panel underside ~104, collar 113+)
tube = t1.cut(box(-5, 5, 0, 11, *WIN_TOP)).removeSplitter()
assert tube.isValid() and len(tube.Solids) == 1
S['Mast_Tube_v2'] = tube
ref = Part.read(str(V2 / 'solid-tube-20261101/Mast_Tube_v2_Solid.step')); ref.translate(V(AX.x, AX.y, 6.0))
R['steps']['3_solid_tube'] = {'xor_vs_solid_tube_folder_mm3': round(xor(tube, ref), 4),
                              'rear_wall_open_mm3': round(ring.common(box(-3.5, 3.5, -10, -6, 22, 142)).cut(tube).Volume, 4)}
assert R['steps']['3_solid_tube']['xor_vs_solid_tube_folder_mm3'] < 0.01
print('step 3 ok', flush=True)

# ============================================================ STEP 4: yoke 45-degree tapers under the plate ledges
X0, Ty, Tz = T.x, T.y, T.z
FEAT = {'pivot_tower': dict(x0=X0 + 28, x1=X0 + 33, jz=Tz - 10.0, col=3.0, plate=9.0),
        'ear_plate': dict(x0=X0 - 2.8, x1=X0 + 0.2, jz=Tz - 12.0, col=3.0, plate=10.0)}


def wedge(f, s):
    y0, y1 = Ty + s * (f['col'] - 0.3), Ty + s * f['plate']
    zb = f['jz'] - (f['plate'] - f['col'] + 0.3)
    pts = [V(f['x0'], y0, zb), V(f['x0'], y0, f['jz'] + 0.3), V(f['x0'], y1, f['jz'] + 0.3), V(f['x0'], y1, f['jz']), V(f['x0'], y0, zb)]
    return Part.Face(Part.makePolygon(pts)).extrude(V(f['x1'] - f['x0'], 0, 0))


Y0 = S['Tilt_Yoke']
Y1 = Y0.fuse([wedge(f, s) for f in FEAT.values() for s in (-1, 1)]).removeSplitter()
assert Y1.isValid() and len(Y1.Solids) == 1
S['Tilt_Yoke'] = Y1
ref = Part.read(str(V2 / 'yoke-taper-20261101/Tilt_Yoke_v2_Tapered.step'))
rb, yb = ref.BoundBox, Y1.BoundBox; ref.translate(V(yb.XMin - rb.XMin, yb.YMin - rb.YMin, yb.ZMin - rb.ZMin))
R['steps']['4_yoke_taper'] = {'xor_vs_yoke_taper_folder_mm3': round(xor(Y1, ref), 4), 'added_mm3': round(Y1.Volume - Y0.Volume, 1)}
assert R['steps']['4_yoke_taper']['xor_vs_yoke_taper_folder_mm3'] < 0.01
print('step 4 ok', flush=True)

# ============================================================ CHECKS on the finished assembly
intent = {frozenset(('Pan_Bearing_Lower', 'Neck_Main')), frozenset(('Pan_Bearing_Upper', 'Neck_Main'))}
movers = set(tilt + pan + fixed)
names = [n for n in S if n in movers]
home = []
for i, a in enumerate(names):
    for b in names[i + 1:]:
        if frozenset((a, b)) in intent:
            continue
        v = ov(S[a], S[b])
        if v > .05:
            home.append([a, b, round(v, 3)])
R['checks']['home_collisions'] = home
assert not home, home
unit = UDIR
car_side = ('Pan_Servo_Carriage', 'SG90_Pan_Reference', 'Pan_Drive_Pulley', 'Pan_Horn_Reference')
tens = []
for C in range(38, 49):
    cur = {n: S[n].copy() for n in S}
    for n in car_side:
        cur[n].translate(unit * (C - p['C_NOM']))
    cur['Tensioner_Nut_Envelope'] = nut_at(C)
    for a_ in ('Tensioner_M3x20_Envelope', 'Tensioner_Nut_Envelope'):
        for b_ in cur:
            if b_ != a_ and ov(cur[a_], cur[b_]) > .01:
                tens.append([C, a_, b_])
R['checks']['tensioner_full_travel_collisions'] = tens
assert not tens, tens
print('static checks ok', flush=True)

if not QUICK:
    tilt_angles = list(range(-38, 35, 2))
    zs = []
    for n in tilt:
        b_ = S[n].BoundBox
        for t in tilt_angles:
            a_ = math.radians(t)
            for y in (b_.YMin - T.y, b_.YMax - T.y):
                for z in (b_.ZMin - T.z, b_.ZMax - T.z):
                    zs.append(T.z + math.sin(a_) * y + math.cos(a_) * z)
    zlo, zhi = min(zs), max(zs)
    active = [n for n in fixed if S[n].BoundBox.ZMax >= zlo and S[n].BoundBox.ZMin <= zhi]
    servo_axis = V(39.5, 113, 0) + unit * p['C_NOM']
    fixed_in_head = {}
    for pn in range(-20, 181, 20):
        fixed_in_head[pn] = {}
        for n in active:
            q = S[n].copy()
            if n in ('Pan_Drive_Pulley', 'Pan_Horn_Reference'):
                q.rotate(servo_axis, V(0, 0, 1), pn / 1.5)
            q.rotate(V(39.5, 113, 0), V(0, 0, 1), -pn)
            fixed_in_head[pn][n] = q
    motion = []
    for t in tilt_angles:
        for n in tilt:
            q = S[n].copy(); q.rotate(T, V(1, 0, 0), t)
            for b_ in pan:
                v = ov(q, S[b_])
                if v > .05:
                    motion.append([n, b_, 0, t, round(v, 3)])
            for pn, obs in fixed_in_head.items():
                for b_, o_ in obs.items():
                    v = ov(q, o_)
                    if v > .05:
                        motion.append([n, b_, pn, t, round(v, 3)])
        print('tilt', t, flush=True)
    R['checks']['motion_grid'] = {'tilt_deg': [-38, 34, 2], 'pan_deg': [-20, 180, 20]}
    R['checks']['motion_collisions'] = motion
    assert not motion, motion
    # the two known end stops must still be where they were
    def at(n, a):
        q = S[n].copy(); q.rotate(T, V(1, 0, 0), a); return q
    R['checks']['end_stops_mm3'] = {'receiver_vs_yoke_at_-40': round(ov(at('GH44_Tilt_Receiver', -40), S['Tilt_Yoke']), 3),
                                    'camera_tray_vs_yoke_at_+36': round(ov(at('Camera_Tray', 36), S['Tilt_Yoke']), 3)}
    print('motion ok', flush=True)

# ============================================================ OUTPUT: assembly + print STLs
doc = A.newDocument('Gladiator_Head_v2_RELEASE')
grp = {}
for n, s in S.items():
    g = GROUP.get(n, 'Hardware')
    if g not in grp:
        grp[g] = doc.addObject('App::DocumentObjectGroup', g)
    o = doc.addObject('Part::Feature', n); o.Shape = s.copy(); grp[g].addObject(o)
if 'References' not in grp:
    grp['References'] = doc.addObject('App::DocumentObjectGroup', 'References')
o = doc.addObject('Part::Feature', 'Pan_Lead_Route'); o.Shape = pan_lead_route; grp['References'].addObject(o)
doc.recompute()
doc.saveAs(str(OUT / 'Gladiator_Head_v2_RELEASE.FCStd'))
Part.export([doc.getObject(n) for n in S if n in movers and not n.startswith('Ref_')], str(OUT / 'Gladiator_Head_v2_RELEASE_assembly.step'))

LIN, ANG, BED_RELIEF = 0.01, 0.0872665, 0.5


def bed_chamfer(shape, size=BED_RELIEF):
    z0 = shape.BoundBox.ZMin
    edges = [e for e in shape.Edges if len(e.Vertexes) == 1 and e.Curve.TypeId == 'Part::GeomCircle'
             and abs(e.BoundBox.ZMin - z0) < 1e-6 and abs(e.BoundBox.ZMax - z0) < 1e-6]
    out, k = shape, 0
    for e in edges:
        try:
            cand = out.makeChamfer(size, [e])
            if cand.isValid() and len(cand.Solids) == 1:
                out, k = cand, k + 1
        except Exception:
            pass
    return out, k


def pose(n, s):
    s = s.copy()
    if n == 'GH44_Tilt_Receiver':
        s.translate(-T); s.rotate(V(), V(1, 0, 0), 90)
    elif n == 'Pan_Servo_Carriage':
        s.rotate(V(), V(0, 0, 1), 45); s.rotate(V(), V(1, 0, 0), 180)
    elif n == 'Pan_Drive_Pulley':
        s.rotate(V(), V(1, 0, 0), 180)
    b_ = s.BoundBox; s.translate(V(-b_.XMin, -b_.YMin, -b_.ZMin)); return s


PRINT = [('01_Neck_Main_PanLead', 'Neck_Main', 'collar on the bed; supports ON (painted) under the servo-pad frame, flange and arm'),
         ('02_Mast_Tube_v2_Solid', 'Mast_Tube_v2', 'upright, pin end on the bed; no support'),
         ('03_Pan_Raised_Pedestal', 'Pan_Raised_Pedestal', 'base plate on the bed; supports ON under the top plate, none within 17 mm of the hub'),
         ('04_Tilt_Yoke_Tapered', 'Tilt_Yoke', 'floor on the bed; no support'),
         ('05_GH44_Tilt_Receiver_Balanced', 'GH44_Tilt_Receiver', 'GH44 face down, arms up; no support'),
         ('06_Pan_Drive_Pulley', 'Pan_Drive_Pulley', 'horn plate on the bed; no support'),
         ('07_Pan_Servo_Carriage', 'Pan_Servo_Carriage', 'top face on the bed, tensioner lug up; no support')]
BASE_STL = {'Pan_Raised_Pedestal', 'Pan_Drive_Pulley', 'Pan_Servo_Carriage'}   # unchanged since v2: must match the v2 STLs
man = []
for fname, n, how in PRINT:
    s, nch = bed_chamfer(pose(n, S[n]))
    assert s.isValid() and len(s.Solids) == 1, n
    path = OUT / 'stl' / (fname + '.stl')
    MeshPart.meshFromShape(Shape=s, LinearDeflection=LIN, AngularDeflection=ANG, Relative=False).write(str(path))
    m = Mesh.Mesh(str(path)); b_ = m.BoundBox
    e = {'file': fname + '.stl', 'part': n, 'orientation': how, 'size_mm': [round(b_.XLength, 2), round(b_.YLength, 2), round(b_.ZLength, 2)],
         'grams_solid_pla': round(s.Volume * 1.24e-3, 2), 'bed_chamfers': nch, 'mesh_closed': m.isSolid() and not m.hasNonManifolds(),
         'fits_220x220x250': b_.XLength <= 220 and b_.YLength <= 220 and b_.ZLength <= 250, 'sha256': sha(path)}
    if n in BASE_STL:
        # unchanged since v2: same size, and the same volume except for bed chamfers. The v2 export's chamfer loop
        # skipped edges after the first chamfer changed the shape (pulley: 1 of its 2 bed circles), so allow up to
        # one 0.5 mm chamfer round a 25 mm radius (~20 mm3) and report it.
        ref = Mesh.Mesh(str(V2 / 'stl' / ('Gladiator_Head_v2_%s.stl' % n)))
        v2_ch = {r_['part']: r_['bed_relief_edges'] for r_ in base_val['print_stl']}[n]
        dv = m.Volume - ref.Volume
        same_size = all(abs(a_ - c_) < 0.02 for a_, c_ in zip((ref.BoundBox.XLength, ref.BoundBox.YLength, ref.BoundBox.ZLength),
                                                              (b_.XLength, b_.YLength, b_.ZLength)))
        e['vs_v2_stl'] = {'volume_diff_mm3': round(dv, 2), 'bed_chamfers_v2': v2_ch, 'bed_chamfers_now': nch, 'same_size': same_size}
        assert same_size and (abs(dv) < 0.5 or (nch > v2_ch and -20 < dv < 0)), (n, e['vs_v2_stl'])
    assert e['mesh_closed'] and e['fits_220x220x250'], e
    man.append(e)
R['print_parts'] = man
(OUT / 'MANIFEST.json').write_text(json.dumps(man, indent=1))
(OUT / 'validation.json').write_text(json.dumps(R, indent=1))
print('RELEASE BUILD PASSED', json.dumps(R['steps']), flush=True)
os._exit(0)
