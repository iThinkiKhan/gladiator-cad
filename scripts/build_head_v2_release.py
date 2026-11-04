"""Gladiator masthead v2 - RELEASE build. THE one script for the current head (consolidated 2026-11-01).

Starts from the v2 base (scripts/build_head_v2_mast.py -> cad/head/v2-mast-20261028/Gladiator_Head_v2_Mast.FCStd)
and applies every later change, in order, as numbered steps:
  1. Tilt balance + M3x20 tensioner   (was balance-tensioner-20261030)
  2. Pan-servo lead path, neck + tube  (was pcb-floor-20261030; its rejected yoke PCB pocket is NOT applied)
  3. Solid tube, slot filled, top window (was solid-tube-20261101)
  4. Yoke 45-degree tapers            (was yoke-taper-20261101)
  5. Screen frame v07: v06 + 2 standoff posts, 4 M2 inserts, for the 30 x 70 side board (replaces side-window-pcb-20261030;
     superseded by step 6, kept as the record)
  6. Screen frame v08: v06 + camera-end post + screen-end pad, 4 M2 inserts, side board CUT to 30 x 61, flat on the rails (superseded by step 7)
  7. Screen frame = v06 + 4 M2 insert pockets for Jim's 40 x 60 side board (centred, holes 2 mm in from the edges)
  8. Pan servo carriage: servo body opening 12.0 x 22.8 -> 12.75 x 23.8 (Jim 2026-11-04)
  9. Tilt yoke: the same 12.75 x 23.8 servo body opening in the ear plate (Jim 2026-11-04)
 10. Tilt yoke: ear plate 3 -> 8 mm thick on the servo-body side, trimmed where the receiver swings (Jim 2026-11-04)
Every print STL gets the bed chamfer (0.5 mm on hole edges on the bed, Jim 2026-10-15); the patch folders had
dropped it for the neck, tube, yoke and receiver.

FUTURE CHANGES GO HERE AS A NEW STEP, NOT A NEW FOLDER.

Run on cad-lab:  python3 scripts/build_head_v2_release.py [--quick]   (--quick skips the long motion sweep)
Output: cad/head/v2-mast-20261028/release/ (assembly FCStd + STEP, 8 print STLs, validation.json, MANIFEST.json)
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

# ============================================================ STEP 5: screen frame v07 = v06 + standoff posts for the side board
# Jim 2026-11-02: screw his 30 x 70 perfboard straight onto the screen frame, uncut, no clamp bars.
# Two solid posts on the -X rail face (one at each end of the side window) stand the board 5 mm off the frame;
# 2 M2 heat-set inserts in each. The board ends level with the bezel face and overhangs the camera end.
F0 = S['Rear_Display_Frame']; fb = F0.BoundBox
RX = fb.XMin                                   # outer face of the -X rail
assert abs(RX - 1.0) < 0.01 and abs(fb.YMin - 86.5) < 0.01 and abs(fb.YMax - 147.7) < 0.01, fb
RAIL_Z0, RAIL_Z1 = T.z - 21.5, T.z + 21.5      # rails 226..235.5 and 259.5..269 (v06 RAIL_DZ0/1 = 12/21.5)
for z in (T.z - 17, T.z + 17):                 # rails are solid where the posts join them
    assert F0.isInside(V(RX + 2, 100, z), 0.01, True) and F0.isInside(V(RX + 2, 140, z), 0.01, True)
assert not F0.isInside(V(RX + 2, 110, T.z), 0.01, True)   # the side window is open
SB_L, SB_W, SB_T, STAND = 70.0, 30.0, 1.6, 5.0
PITCH, COLS, ROWS = 2.54, 24, 10               # usual 30 x 70 perfboard grid, assumed centred on the board
MY, MZ = (SB_L - (COLS - 1) * PITCH) / 2, (SB_W - (ROWS - 1) * PITCH) / 2
SB_Y1 = fb.YMax; SB_Y0 = SB_Y1 - SB_L          # level with the bezel face; overhangs the camera end
SB_Z0, SB_Z1 = T.z - SB_W / 2, T.z + SB_W / 2
SB_X1 = RX - STAND; SB_X0 = SB_X1 - SB_T
HOLE_COLS, HOLE_ROWS = (3, 23), (0, ROWS - 1)  # 4th and last column from the camera end, outer rows
holes = [(SB_Y0 + MY + PITCH * k, SB_Z0 + MZ + PITCH * j) for k in HOLE_COLS for j in HOLE_ROWS]
INS_D, INS_DEPTH = 2.8, 4.6                    # M2 insert 4 long + 0.6 for the M2 x 6 screw tip; 0.4 floor left
y_cam, y_scr = holes[0][0], holes[2][0]
POST_HALF = 3.5
cam_post = Part.makeBox(STAND, y_cam + POST_HALF - fb.YMin, RAIL_Z1 - RAIL_Z0, V(SB_X1, fb.YMin, RAIL_Z0))
# 45 deg taper on the bezel side of the camera post: it faces the bed when the frame prints bezel-down
tri = Part.Face(Part.makePolygon([V(SB_X1, y_cam + POST_HALF, RAIL_Z0), V(RX, y_cam + POST_HALF, RAIL_Z0),
                                  V(RX, y_cam + POST_HALF + STAND, RAIL_Z0), V(SB_X1, y_cam + POST_HALF, RAIL_Z0)]))
cam_post = cam_post.fuse(tri.extrude(V(0, 0, RAIL_Z1 - RAIL_Z0)))
scr_post = Part.makeBox(STAND, fb.YMax - (y_scr - POST_HALF), RAIL_Z1 - RAIL_Z0, V(SB_X1, y_scr - POST_HALF, RAIL_Z0))
F1 = F0.fuse([cam_post, scr_post])
for y, z in holes:
    F1 = F1.cut(Part.makeCylinder(INS_D / 2, INS_DEPTH, V(SB_X1, y, z), V(1, 0, 0)))
F1 = F1.removeSplitter()
assert F1.isValid() and len(F1.Solids) == 1
for y, z in holes:                             # every insert sits in solid post with at least 1.5 mm of wall
    ring = Part.makeCylinder(INS_D / 2 + 1.5, INS_DEPTH, V(SB_X1, y, z), V(1, 0, 0)).cut(
        Part.makeCylinder(INS_D / 2, INS_DEPTH, V(SB_X1, y, z), V(1, 0, 0)))
    assert abs(F1.common(ring).Volume - ring.Volume) < 0.05, (y, z)
removed = F0.cut(F1).Volume                   # nothing of the v06 frame is cut away (bores stay inside the posts)
assert removed < 0.01, removed
S['Rear_Display_Frame'] = F1
ACCESS_D = 6.0                                 # screwdriver to the tilt horn screw, on the tilt axis
sb = Part.makeBox(SB_T, SB_L, SB_W, V(SB_X0, SB_Y0, SB_Z0))
sb = sb.cut(Part.makeCylinder(ACCESS_D / 2, 10, V(SB_X0 - 5, T.y, T.z), V(1, 0, 0)))
for y, z in holes:
    sb = sb.cut(Part.makeCylinder(1.1, 10, V(SB_X0 - 5, y, z), V(1, 0, 0)))
S['Side_Board_30x70_Placeholder'] = sb
# outside face: solder joints, M2 pan heads (3.8 x 1.6) and a margin, 6 mm deep
S['Side_Board_Outer_Envelope'] = Part.makeBox(6.0, SB_L, SB_W, V(SB_X0 - 6.0, SB_Y0, SB_Z0))
for n in ('Side_Board_30x70_Placeholder', 'Side_Board_Outer_Envelope'):
    GROUP[n] = 'Hardware'; tilt.append(n)
driver = Part.makeCylinder(1.6, 60, V(-40, T.y, T.z), V(1, 0, 0))
drv = sorted(n for n in S if n not in ('Tilt_Horn_Reference', 'Side_Board_Outer_Envelope') and ov(driver, S[n]) > .05)
R['steps']['5_frame_v07_side_board'] = {
    'board_mm': [SB_L, SB_W, SB_T], 'board_world_Y': [round(SB_Y0, 2), round(SB_Y1, 2)], 'board_world_Z': [SB_Z0, SB_Z1],
    'standoff_mm': STAND, 'board_overhang_past_camera_end_of_frame_mm': round(fb.YMin - SB_Y0, 2),
    'grid_assumed': '%d x %d holes at %.2f, centred: first column %.2f from each end, first row %.2f from each long edge'
                    % (ROWS, COLS, PITCH, MY, MZ),
    'screw_holes_from_camera_end_and_bottom_edge_mm': [[round(y - SB_Y0, 2), round(z - SB_Z0, 2)] for y, z in holes],
    'screw_holes_grid_col_row_1based': [[k + 1, j + 1] for k in HOLE_COLS for j in HOLE_ROWS],
    'access_hole_d_and_from_camera_end_bottom_mm': [ACCESS_D, round(T.y - SB_Y0, 2), round(T.z - SB_Z0, 2)],
    'inserts': '4 x M2 heat-set, bore %.1f x %.1f deep, from the board side; screws M2 x 6' % (INS_D, INS_DEPTH),
    'posts_added_mm3': round(F1.Volume - F0.Volume, 1), 'posts_added_g_pla': round((F1.Volume - F0.Volume) * 1.24e-3, 2),
    'horn_screw_driver_blockers': drv}
assert not drv, drv
print('step 5 ok', flush=True)

# ============================================================ STEP 6: screen frame v08 = v06 + end posts, board CUT to 61 mm, flat on the rails
# Jim 2026-11-02: cut the 30 x 70 board to the frame length rather than stand it off past the camera end (v07).
# The board lies straight on the -X rail face, flush with the bezel face, and stops 0.2 mm short of the camera end of
# the frame (nothing over the carrier or ToF, no standoff). v06 has a solid end post only at the screen end, 1.5 mm
# below the rail face, and the camera end of the window is open: v08 adds a post filling the camera end of the window
# and a pad bringing the screen-end post up to the rail face, 4 M2 inserts. Replaces the step 5 v07 frame and board.
F06 = F0                                       # the v06 frame step 5 started from
assert F06.Volume < S['Rear_Display_Frame'].Volume
for n in ('Side_Board_30x70_Placeholder', 'Side_Board_Outer_Envelope'):
    S.pop(n); GROUP.pop(n); tilt.remove(n)
SB6_L = 61.0
SB6_Y1 = fb.YMax; SB6_Y0 = SB6_Y1 - SB6_L      # factory edge at the screen end, cut edge at the camera end
SB6_X1 = RX; SB6_X0 = SB6_X1 - SB_T            # inner face on the rail face
# grid as on the uncut board (screen end is the factory edge, so the columns are where they were in step 5)
gy = lambda k: SB_Y0 + MY + PITCH * (k - 1)    # column k, 1-based, counted on the uncut board from the camera end
gz = lambda j: SB_Z0 + MZ + PITCH * (j - 1)    # row j, 1-based, from the bottom edge
H6_COLS, H6_ROWS = (4, 24), (2, 9)             # rows 2 and 9 keep the screen-end holes clear of the factory corner holes
holes6 = [(gy(k), gz(j)) for k in H6_COLS for j in H6_ROWS]
for k in (6, 22):                              # the window is open at the first and last free column
    assert not F06.isInside(V(RX + 2, gy(k), T.z), 0.01, True), k
INS6_DEPTH, POST6_DEEP = 4.5, 5.5              # M2 insert 4 + 0.5 for the screw tip; 1.0 mm floor
P6_X1 = RX + POST6_DEEP
y6c, y6s = gy(H6_COLS[0]), gy(H6_COLS[1])
cam6 = Part.makeBox(POST6_DEEP, y6c + POST_HALF - fb.YMin, RAIL_Z1 - RAIL_Z0, V(RX, fb.YMin, RAIL_Z0))
scr6 = Part.makeBox(POST6_DEEP, fb.YMax - (y6s - POST_HALF), RAIL_Z1 - RAIL_Z0, V(RX, y6s - POST_HALF, RAIL_Z0))
F6 = F06.fuse([cam6, scr6])
for y, z in holes6:
    F6 = F6.cut(Part.makeCylinder(INS_D / 2, INS6_DEPTH, V(RX, y, z), V(1, 0, 0)))
F6 = F6.removeSplitter()
assert F6.isValid() and len(F6.Solids) == 1
assert abs(F6.BoundBox.XMin - RX) < 0.01 and abs(F6.BoundBox.YMin - fb.YMin) < 0.01 and abs(F6.BoundBox.YMax - fb.YMax) < 0.01
for y, z in holes6:
    ring = Part.makeCylinder(INS_D / 2 + 1.5, INS6_DEPTH + 1.0, V(RX, y, z), V(1, 0, 0)).cut(
        Part.makeCylinder(INS_D / 2, INS6_DEPTH, V(RX, y, z), V(1, 0, 0)))
    assert abs(F6.common(ring).Volume - ring.Volume) < 0.05, (y, z)    # 1.5 mm wall round and 1.0 mm floor behind
# only the insert bores may remove v06 material (the screen-end bores go into the v06 end post)
bores6 = Part.Compound([Part.makeCylinder(INS_D / 2, INS6_DEPTH, V(RX, y, z), V(1, 0, 0)) for y, z in holes6])
removed6 = F06.cut(F6).Volume
assert abs(removed6 - F06.common(bores6).Volume) < 0.01, removed6
# the board must bear on frame all along both rails and on both posts (no gap like the v06 recessed end post)
for y in (fb.YMin + 1, 113, fb.YMax - 1):
    for z in (SB_Z0 + 1.5, SB_Z1 - 1.5):
        assert F6.isInside(V(RX + 0.2, y, z), 0.01, True), (y, z)
S['Rear_Display_Frame'] = F6
sb6 = Part.makeBox(SB_T, SB6_L, SB_W, V(SB6_X0, SB6_Y0, SB_Z0))
sb6 = sb6.cut(Part.makeCylinder(ACCESS_D / 2, 10, V(SB6_X0 - 5, T.y, T.z), V(1, 0, 0)))
for y, z in holes6:
    sb6 = sb6.cut(Part.makeCylinder(1.1, 10, V(SB6_X0 - 5, y, z), V(1, 0, 0)))
S['Side_Board_30x61_Placeholder'] = sb6
S['Side_Board_Outer_Envelope'] = Part.makeBox(6.0, SB6_L, SB_W, V(SB6_X0 - 6.0, SB6_Y0, SB_Z0))
for n in ('Side_Board_30x61_Placeholder', 'Side_Board_Outer_Envelope'):
    GROUP[n] = 'Hardware'; tilt.append(n)
drv6 = sorted(n for n in S if n not in ('Tilt_Horn_Reference', 'Side_Board_Outer_Envelope') and ov(driver, S[n]) > .05)
R['steps']['5_frame_v07_side_board']['superseded_by'] = '6_frame_v08_cut_board'
R['steps']['6_frame_v08_cut_board'] = {
    'board_mm': [SB6_L, SB_W, SB_T], 'board_world_Y': [round(SB6_Y0, 2), round(SB6_Y1, 2)], 'board_world_Z': [SB_Z0, SB_Z1],
    'standoff_mm': 0.0, 'cut_mm_off_camera_end_of_70_board': round(70 - SB6_L, 2),
    'board_gap_to_camera_end_of_frame_mm': round(SB6_Y0 - fb.YMin, 2),
    'grid_assumed': R['steps']['5_frame_v07_side_board']['grid_assumed'],
    'screw_holes_from_cut_end_and_bottom_edge_mm': [[round(y - SB6_Y0, 2), round(z - SB_Z0, 2)] for y, z in holes6],
    'screw_holes_from_factory_end_mm': sorted({round(SB6_Y1 - y, 2) for y, _ in holes6}),
    'screw_holes_grid_col_row_1based_uncut_count': [[k, j] for k in H6_COLS for j in H6_ROWS],
    'free_columns_over_window_1based_uncut_count': [k for k in range(1, COLS + 1)
                                                    if y6c + POST_HALF + 1.0 <= gy(k) <= y6s - POST_HALF - 1.0],
    'access_hole_d_and_from_cut_end_bottom_mm': [ACCESS_D, round(T.y - SB6_Y0, 2), round(T.z - SB_Z0, 2)],
    'inserts': '4 x M2 heat-set, bore %.1f x %.1f deep, from the board side; screws M2 x 6' % (INS_D, INS6_DEPTH),
    'posts_added_mm3': round(F6.Volume - F06.Volume, 1), 'posts_added_g_pla': round((F6.Volume - F06.Volume) * 1.24e-3, 2),
    'horn_screw_driver_blockers': drv6}
assert not drv6, drv6
print('step 6 ok', flush=True)

# ============================================================ STEP 7: v06 frame + 4 insert pockets for Jim's 40 x 60 board
# Jim 2026-11-02: a 40 x 60 perfboard fits the v06 frame as it is, centred on the frame, flat on the -X rail face.
# Its factory corner holes are 2.0 mm in from each edge. Pressing inserts into the printed frame without pockets
# filled them with plastic, so this reprints v06 with 4 M2 heat-set pockets under those holes. Nothing else changes.
for n in ('Side_Board_30x61_Placeholder', 'Side_Board_Outer_Envelope'):
    S.pop(n); GROUP.pop(n); tilt.remove(n)
B7_L, B7_W, B7_HOLE_IN = 60.0, 40.0, 2.0
B7_Y0 = (fb.YMin + fb.YMax) / 2 - B7_L / 2; B7_Y1 = B7_Y0 + B7_L      # centred on the frame
B7_Z0, B7_Z1 = T.z - B7_W / 2, T.z + B7_W / 2                          # centred on the frame (= tilt axis)
assert abs((fb.ZMin + fb.ZMax) / 2 - T.z) < 0.01
B7_X1 = RX; B7_X0 = RX - SB_T
holes7 = [(y, z) for y in (B7_Y0 + B7_HOLE_IN, B7_Y1 - B7_HOLE_IN) for z in (B7_Z0 + B7_HOLE_IN, B7_Z1 - B7_HOLE_IN)]
B7_BORE = 4.5                                  # M2 insert 4 long + 0.5 for the plastic it pushes ahead
bores7 = [Part.makeCylinder(INS_D / 2, B7_BORE, V(RX, y, z), V(1, 0, 0)) for y, z in holes7]
for b_ in bores7:
    assert abs(F06.common(b_).Volume - b_.Volume) < 0.05      # every pocket fully in v06 material
F7 = F06
for b_ in bores7:
    F7 = F7.cut(b_)
F7 = F7.removeSplitter()
assert F7.isValid() and len(F7.Solids) == 1
walls7 = []
for (y, z), b_ in zip(holes7, bores7):
    wall = 0.0
    for w in (2.0, 1.5, 1.2, 1.0, 0.8):
        ring = Part.makeCylinder(INS_D / 2 + w, B7_BORE, V(RX, y, z), V(1, 0, 0)).cut(b_)
        if abs(F06.common(ring).Volume - ring.Volume) < 0.05:
            wall = w; break
    walls7.append(wall)
S['Rear_Display_Frame'] = F7
sb7 = Part.makeBox(SB_T, B7_L, B7_W, V(B7_X0, B7_Y0, B7_Z0))
for y, z in holes7:
    sb7 = sb7.cut(Part.makeCylinder(1.0, 10, V(B7_X0 - 5, y, z), V(1, 0, 0)))
S['Side_Board_40x60_Placeholder'] = sb7
S['Side_Board_Outer_Envelope'] = Part.makeBox(6.0, B7_L, B7_W, V(B7_X0 - 6.0, B7_Y0, B7_Z0))
for n in ('Side_Board_40x60_Placeholder', 'Side_Board_Outer_Envelope'):
    GROUP[n] = 'Hardware'; tilt.append(n)
R['steps']['6_frame_v08_cut_board']['superseded_by'] = '7_v06_pockets_40x60_board'
R['steps']['7_v06_pockets_40x60_board'] = {
    'frame': 'v06 + 4 M2 heat-set pockets (Jim reprints it)',
    'board_mm': [B7_L, B7_W, SB_T], 'board_world_Y': [round(B7_Y0, 2), round(B7_Y1, 2)], 'board_world_Z': [B7_Z0, B7_Z1],
    'board_holes_in_from_each_edge_mm': B7_HOLE_IN,
    'pockets_world_YZ': [[round(y, 2), round(z, 2)] for y, z in holes7],
    'pockets_from_camera_end_of_frame_mm': sorted({round(y - fb.YMin, 2) for y, _ in holes7}),
    'pockets_from_bottom_of_frame_mm': sorted({round(z - fb.ZMin, 2) for _, z in holes7}),
    'pocket': 'dia %.1f x %.1f deep, from the board side' % (INS_D, B7_BORE),
    'pocket_min_wall_mm': walls7, 'removed_mm3': round(F06.Volume - F7.Volume, 2),
    'hardware': '4 x M2 heat-set inserts (4 long) + 4 x M2 x 5 (or M2 x 6)'}
print('step 7 ok', flush=True)

# ============================================================ STEP 8: pan servo carriage, larger servo body opening
# Jim 2026-11-04: the SG90 body only just goes into the printed carriage ("I can get this one in"); make the
# opening "3/4mm wider and at least 1mm longer". 12.0 x 22.8 -> 12.75 x 23.8, still centred on the servo body.
# Nothing else on the carriage moves. The ear pilots stay where the servo's ears are, so the plastic between
# each pilot and the opening drops from 1.0 to 0.5 mm.
CAR0 = S['Pan_Servo_Carriage']


def to_F(shape):                                   # inverse of frame(): world -> servo frame F
    s = shape.copy(); s.translate(V(-39.5, -113, -p['LIFT'])); s.rotate(V(), V(0, 0, 1), 45); return s


CAR_T8, PILOT8, PITCH8 = 3.0, 2.35, 27.2            # carriage plate, M2 ear pilot, SG90 ear pitch (base script)
OLD8, NEW8 = (12.0, 22.8), (12.75, 23.8)            # (width, length) of the body opening
YB8 = -p['C_NOM'] - 5.5                             # servo body centre in frame F at the nominal belt setting
cF = to_F(CAR0)
TOP8 = cF.BoundBox.ZMax                             # carriage top face (ears sit here); the lug hangs below


def opening8(w, l):
    return Part.makeBox(w, l, CAR_T8 + 2, V(-w / 2, YB8 - l / 2, TOP8 - CAR_T8 - 1))


# the old opening is exactly where the base script cut it: empty inside, plastic just outside it
assert ov(cF, opening8(OLD8[0] - 0.02, OLD8[1] - 0.02)) < 1e-6
assert ov(cF, opening8(OLD8[0] + 0.1, OLD8[1])) > 0.1 and ov(cF, opening8(OLD8[0], OLD8[1] + 0.1)) > 0.1
c8 = cF.cut(opening8(*NEW8)).removeSplitter()
removed8 = cF.Volume - c8.Volume
expect8 = (NEW8[0] * NEW8[1] - OLD8[0] * OLD8[1]) * CAR_T8
assert abs(removed8 - expect8) < 0.01, (removed8, expect8)       # only plate plastic removed: no pilot or slot touched
assert c8.isValid() and len(c8.Solids) == 1
S['Pan_Servo_Carriage'] = frame(c8)
R['steps']['8_carriage_body_opening'] = {
    'opening_mm_before': list(OLD8), 'opening_mm_now': list(NEW8),
    'wider_mm': round(NEW8[0] - OLD8[0], 2), 'longer_mm': round(NEW8[1] - OLD8[1], 2), 'centred_on_servo_body': True,
    'ear_pilot_wall_to_opening_mm': round(PITCH8 / 2 - PILOT8 / 2 - NEW8[1] / 2, 3),
    'ear_pilot_wall_before_mm': round(PITCH8 / 2 - PILOT8 / 2 - OLD8[1] / 2, 3),
    'removed_mm3': round(removed8, 2),
    'bed_chamfer': 'none on the ear pilots: a 0.5 chamfer would break through the 0.5 mm wall into the opening'}
print('step 8 ok', flush=True)

# ============================================================ STEP 9: tilt yoke, same larger servo body opening
# Jim 2026-11-04: "The yoke needs to be made bigger too, i just broke the yoke trying to get the tilt servo in."
# The SG90 body goes through the 3 mm ear plate (x -2.8..0.2 from the tilt axis) in a 12.0 x 22.8 opening, the
# same size as the carriage's; it gets the step 8 size, 12.75 x 23.8, centred on the servo body. The ear pilots
# stay where the ears are (0.5 mm wall to the opening, was 1.0); the plate keeps 3.6 mm each side of it.
Y0 = S['Tilt_Yoke']
EP_X, BODY_Z8 = -2.8, 5.5                          # ear plate inner face, servo body centre above the tilt axis


def opening9(w, l):                                # the base script's cut: 5 deep from 0.7 outside the plate
    return Part.makeBox(5, w, l, T + V(EP_X - 0.7, -w / 2, BODY_Z8 - l / 2))


assert ov(Y0, opening9(OLD8[0] - 0.02, OLD8[1] - 0.02)) < 1e-6
assert ov(Y0, opening9(OLD8[0] + 0.1, OLD8[1])) > 0.1 and ov(Y0, opening9(OLD8[0], OLD8[1] + 0.1)) > 0.1
Y9 = Y0.cut(opening9(*NEW8)).removeSplitter()
removed9 = Y0.Volume - Y9.Volume
expect9 = (NEW8[0] * NEW8[1] - OLD8[0] * OLD8[1]) * 3.0
assert abs(removed9 - expect9) < 0.01, (removed9, expect9)     # only ear plate plastic: no pilot touched
assert Y9.isValid() and len(Y9.Solids) == 1
S['Tilt_Yoke'] = Y9
R['steps']['9_yoke_body_opening'] = {
    'opening_mm_before': list(OLD8), 'opening_mm_now': list(NEW8), 'centred_on_servo_body': True,
    'ear_pilot_wall_to_opening_mm': round(PITCH8 / 2 - PILOT8 / 2 - NEW8[1] / 2, 3),
    'ear_plate_side_wall_mm': round((20.0 - NEW8[0]) / 2, 3), 'removed_mm3': round(removed9, 2)}
print('step 9 ok', flush=True)

# ============================================================ STEP 10: stronger tilt servo ear plate
# Jim 2026-11-04: "Strengthen the tilt servo holder as well, i dont want it snapping apart like that. Only one of the
# arms for the servo holding enclosure survived, the rest snapped off." The servo hangs on the 3 mm ear plate alone;
# round the opening it leaves four bars (sides 3.6 x 3), printed upright, so pushing the servo in bends them across
# the layers. The plate gets 5 mm more on the servo-body side (+x, x 0.2..5.2): 8 mm in all. The ear face (x -2.8)
# does not move. 45 deg underside so it prints without support. Opening and ear pilots run through the new depth.
# Where the receiver and carrier swing past (front top corner, tilt -28..-40) the new material is trimmed by their
# pieces in that slab, each padded 0.8 mm, swept every 1 deg over -40..+36, so the printed receiver still fits and
# the -40 end stop is still the old plate.
YS = S['Tilt_Yoke']
X10 = 5.2
prof = [T + V(x, -10, z) for x, z in ((0.15, -12.0), (0.15, 23.0), (X10, 23.0), (X10, -12.0 + (X10 - 0.2)))]
ext = Part.Face(Part.makePolygon(prof + [prof[0]])).extrude(V(0, 20, 0))
ext = ext.cut(opening9(NEW8[0], NEW8[1]).fuse(Part.makeBox(X10 + 1.5, NEW8[0], NEW8[1], T + V(0, -NEW8[0] / 2, BODY_Z8 - NEW8[1] / 2))))
slab = Part.makeBox(X10 + 1.0, 90, 90, T + V(-0.2, -45, -45))
pads = []
for n in tilt:
    if not S[n].BoundBox.intersect(slab.BoundBox):
        continue
    for s_ in S[n].common(slab).Solids:
        b_ = s_.BoundBox
        pads.append((n, Part.makeBox(b_.XLength + 1.6, b_.YLength + 1.6, b_.ZLength + 1.6, V(b_.XMin - 0.8, b_.YMin - 0.8, b_.ZMin - 0.8))))
ext0 = ext.Volume
trim_hits = set()
for t in range(-40, 37):
    for n, b_ in pads:
        q = b_.copy(); q.rotate(T, V(1, 0, 0), t)
        if ov(ext, q) > 1e-4:
            ext = ext.cut(q); trim_hits.add(n)
ext = ext.removeSplitter()
Y10 = YS.fuse(ext).removeSplitter()
for s_ in (-1, 1):                                  # ear pilots through the full 8 mm
    Y10 = Y10.cut(Part.makeCylinder(PILOT8 / 2, X10 + 5.0, T + V(EP_X - 1.2, 0, BODY_Z8 + s_ * PITCH8 / 2), V(1, 0, 0)))
Y10 = Y10.removeSplitter()
assert Y10.isValid() and len(Y10.Solids) == 1


def bar_x(y, z):                                    # plate thickness along x through (y, z), from the ear face
    ln = Part.makeLine(T + V(EP_X - 0.01, y, z), T + V(X10 + 1, y, z))
    c = Y10.common(ln)
    return round(sum(e.Length for e in c.Edges), 2)


bars = {'side_rear_+y': bar_x(8.2, BODY_Z8), 'side_front_-y': bar_x(-8.2, BODY_Z8),
        'top_mid': bar_x(0, 20.5), 'bottom_mid': bar_x(0, -9.5),
        'front_top_corner_-y': bar_x(-8.2, 16.0), 'rear_top_corner_+y': bar_x(8.2, 16.0)}
S['Tilt_Yoke'] = Y10
R['steps']['10_yoke_strong_ear_plate'] = {
    'ear_plate_mm_before': 3.0, 'ear_plate_mm_now': round(X10 - EP_X, 2), 'ear_face_x_unchanged': EP_X,
    'added_mm3': round(Y10.Volume - YS.Volume, 1), 'added_before_trim_mm3': round(ext0, 1),
    'trimmed_for': sorted(trim_hits), 'trim': 'tilt-side pieces in the slab, padded 0.8, swept -40..+36 every 1 deg',
    'plate_thickness_through_bars_mm': bars, 'underside': '45 deg, no support'}
print('step 10 ok', bars, flush=True)

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
    elif n == 'Rear_Display_Frame':
        s.rotate(V(), V(1, 0, 0), -90)          # bezel face (+Y) down, as the v06 frame
    b_ = s.BoundBox; s.translate(V(-b_.XMin, -b_.YMin, -b_.ZMin)); return s


PRINT = [('01_Neck_Main_PanLead', 'Neck_Main', 'collar on the bed; supports ON (painted) under the servo-pad frame, flange and arm'),
         ('02_Mast_Tube_v2_Solid', 'Mast_Tube_v2', 'upright, pin end on the bed; no support'),
         ('03_Pan_Raised_Pedestal', 'Pan_Raised_Pedestal', 'base plate on the bed; supports ON under the top plate, none within 17 mm of the hub'),
         ('04_Tilt_Yoke_Strong_WideBody', 'Tilt_Yoke', 'floor on the bed; no support'),
         ('05_GH44_Tilt_Receiver_Balanced', 'GH44_Tilt_Receiver', 'GH44 face down, arms up; no support'),
         ('06_Pan_Drive_Pulley', 'Pan_Drive_Pulley', 'horn plate on the bed; no support'),
         ('07_Pan_Servo_Carriage_WideBody', 'Pan_Servo_Carriage', 'top face on the bed, tensioner lug up; no support'),
         ('08_Screen_Frame_v06_Pockets_40x60', 'Rear_Display_Frame', 'bezel face down, as the v06 frame; no support')]
BASE_STL = {'Pan_Raised_Pedestal', 'Pan_Drive_Pulley'}   # unchanged since v2: must match the v2 STLs (carriage: step 8)
man = []
for fname, n, how in PRINT:
    # the v06 frame already has its own bed chamfers on the 4 screen pilots: leave its geometry as it is
    if n == 'Rear_Display_Frame':
        s, nch = pose(n, S[n]), 'v06 own'
    elif n == 'Pan_Servo_Carriage':                # step 8: ear pilots are 0.5 mm from the opening, no chamfer
        s, nch = pose(n, S[n]), 0
    else:
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
