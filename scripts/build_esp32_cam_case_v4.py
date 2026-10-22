"""ESP32-CAM case v4: replaces the SEN0610 radar frame on the GH44 dual carrier.
Run:  QT_QPA_PLATFORM=offscreen freecadcmd -c "exec(open('scripts/build_esp32_cam_case_v4.py').read())"
Reads the saved v05 head assembly and the supplied ESP3-CAM STEP model; writes cad/head/esp32-cam-case-v4/.

Local frame = the v05 sensor-mount frame: X right, Y rearward, Z up (relative to the tilt axis); the
carrier sensor plate front face is y = -58 and sensors face -Y.  Global = local + (39.5, 113, 216.5).
Board frame (STEP): Xb along the 40 mm length (SD end at 0), Yb out of the lens face, Zb across 27 mm.
"""
import json, math, sys
from pathlib import Path
import FreeCAD as A
import Part, Mesh, MeshPart, Import

ROOT = Path('/home/buralien/projects/gladiator-cad')
OUT = ROOT / 'cad/head/esp32-cam-case-v4'
(OUT / 'stl').mkdir(parents=True, exist_ok=True)
(OUT / 'preview').mkdir(parents=True, exist_ok=True)
ASM = ROOT / 'cad/head/v05-sensor-mounts/Gladiator_Head_v05_PanStack.FCStd'
BOARD_STEP = str(ROOT / 'reference/esp32-cam/ESP3-CAM.STEP')   # supplied by Jim 2026-10-13 (SolidWorks 2020 export)
GLOBAL = A.Vector(39.5, 113.0, 216.5)

# ---------------------------------------------------------------- parameters (all mm)
M2_CLEAR, PILOT_M2 = 2.6, 2.35
Y_FACE = -58.0                    # carrier front face
FLOOR_T = 3.0                     # same 3 mm boss thickness as the radar frame, M2x6 engages fully
Y_FLOOR_IN = Y_FACE - FLOOR_T     # -61
XC = 26.5                         # board centre x; left outer wall stays 0.8 clear of the ToF frame
WALL, CLR = 2.0, 0.375
BOARD_W, BOARD_L = 27.2, 40.6     # AI-Thinker 27 x 40.5 (+-0.2); the STEP is 27 x 40
SD_PROTRUDE = 0.5                 # card sits 0.5 past the PCB edge in the STEP
LEN_FROM_SD_END = 11.4            # lens axis, STEP Xb
Z_SD = BOARD_L / 2.0              # z of the SD-end PCB edge (SD end is UP)
LC, HDR_PLASTIC, BEND = 14.0, 2.66, 3.0   # Dupont housing, header plastic height, wire bend room (v4: 3, was 5)
Y_BACK = Y_FLOOR_IN - (HDR_PLASTIC + LC + BEND)   # PCB back face; floor inner face is 19.66 behind it
LID_IN_Yb, LID_OUT_Yb = 7.3, 9.3   # lid faces forward of the PCB back face; Jim's calipers: camera square top 6.75, lens tip 9.4
Y_LID_IN = Y_BACK - LID_IN_Yb
Y_LID_OUT = Y_BACK - LID_OUT_Yb
PCB_T = 0.8                     # Jim's calipers
POST_GAP = 0.3

CX0, CX1 = XC - (BOARD_W / 2 + CLR), XC + (BOARD_W / 2 + CLR)
CZ0, CZ1 = -(BOARD_L / 2 + CLR), BOARD_L / 2 + CLR + SD_PROTRUDE
OX0, OX1, OZ0, OZ1 = CX0 - WALL, CX1 + WALL, CZ0 - WALL, CZ1 + WALL
EAR_R, EAR_DX = 3.0, 12.5
EAR_Z = {'sd': CZ1 + EAR_R, 'far': CZ0 - EAR_R}
EAR_PILOT_DEPTH = 10.0


def xb(Zb): return XC - (Zb - 13.5)       # board Zb -> head x
def zb(Xb): return Z_SD - Xb              # board Xb -> head z


def lbox(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, A.Vector(x0, y0, z0))


def cy(r, y0, y1, x, z):                  # cylinder along y, y0 < y1
    return Part.makeCylinder(r, y1 - y0, A.Vector(x, y0, z), A.Vector(0, 1, 0))


def fuse(*ss):
    r = ss[0]
    for s in ss[1:]:
        r = r.fuse(s)
    return r.removeSplitter()


def wedge(z_wall, z_tip, x0, x1):
    """Pad: top face at y = Y_BACK (board back plane), 45 deg underside back to the wall."""
    L = abs(z_wall - z_tip)
    pts = [A.Vector(x0, Y_BACK, z_wall), A.Vector(x0, Y_BACK, z_tip), A.Vector(x0, Y_BACK + L, z_wall)]
    f = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return f.extrude(A.Vector(x1 - x0, 0, 0))


CORNER_X = [(xb(26.4), xb(23.4)), (xb(3.8), xb(0.8))]          # (x0,x1) for left and right board corners
SD_PAD_TIP, FAR_PAD_TIP = 18.6, -18.6
POST_Z_SD, POST_Z_FAR = (16.9, 19.9), (-18.7, -15.7)

# ---------------------------------------------------------------- tray
tray = lbox(OX0, OX1, Y_LID_IN, Y_FACE, OZ0, OZ1).cut(lbox(CX0, CX1, Y_LID_IN - 1, Y_FLOOR_IN, CZ0, CZ1))
ears = []
for end, z in EAR_Z.items():
    for sx in (-1, 1):
        ears.append((XC + sx * EAR_DX, z))
tray = fuse(tray, *[cy(EAR_R, Y_LID_IN, Y_FACE, x, z) for x, z in ears])
for x0, x1 in CORNER_X:
    tray = fuse(tray, wedge(CZ1, SD_PAD_TIP, x0, x1), wedge(CZ0, FAR_PAD_TIP, x0, x1))
# Tilt clearance: at +25 deg the tray's lower rear edge would hit the yoke base plate (the carrier's own edge is
# at z -21 for this reason), so bevel everything beyond z -19.5 at the mating face by 45 degrees.
_pts = [A.Vector(OX0 - 1, Y_FACE, CZ0 + 1.175), A.Vector(OX0 - 1, Y_FACE - 9.5, CZ0 + 1.175 - 9.5),
        A.Vector(OX0 - 1, Y_FACE + 1.0, CZ0 + 1.175 - 9.5), A.Vector(OX0 - 1, Y_FACE + 1.0, CZ0 + 1.175)]
_bev = Part.Face(Part.makePolygon(_pts + [_pts[0]])).extrude(A.Vector(OX1 - OX0 + 2, 0, 0))
tray = tray.cut(_bev)
# SD window in the SD-end wall: Zb 5.3..22.3, Yb 0.6..5.8 (holder top 4.4 measured; card Zb 6.95..18.05)
SD_WIN = (xb(22.3), xb(5.3), Y_BACK - 5.8, Y_BACK - 0.6)
tray = tray.cut(lbox(SD_WIN[0], SD_WIN[1], SD_WIN[2], SD_WIN[3], CZ1 - 0.1, OZ1 + 0.1))
# finger recess: thin the SD-end wall to 1.0 mm around the window so an ejected card (it pops about 2-3 mm) can be reached
SD_POCKET = (SD_WIN[0] - 0.4, SD_WIN[1] + 0.4, Y_BACK - 6.6, Y_BACK + 0.2)
tray = tray.cut(lbox(SD_POCKET[0], SD_POCKET[1], SD_POCKET[2], SD_POCKET[3], OZ1 - 1.0, OZ1 + 0.1))
# wire exit: left (ToF-side) wall, in the rear zone, in line with the carrier cable slot (x -9..9, z +-5)
# wire slots, both long walls: all 16 header pins plug on from behind (straight pins) and each wire turns sideways at the
# connector end and leaves through the wall.  Two slots per wall (pins 1-4 and 5-8) with a 0.8 mm strut so each roof bridges < 10 mm.
PIN_Z = [zb(4.72 + 2.54 * k) for k in range(8)]          # head z of the 8 pin pairs (Xb 4.72 .. 22.5)
STRUT = 0.8
_mid = (PIN_Z[3] + PIN_Z[4]) / 2
SLOT_Z = [(_mid + STRUT / 2, PIN_Z[0] + 1.3), (PIN_Z[7] - 1.3, _mid - STRUT / 2)]
SLOT_Y = (Y_FLOOR_IN - 3.4, Y_FLOOR_IN)                    # from the floor surface up 3.4 mm
SLOTS = []
for (z0, z1) in SLOT_Z:
    SLOTS.append((OX0 - 0.1, CX0 + 0.1, SLOT_Y[0], SLOT_Y[1], z0, z1))      # left wall (ToF side)
    SLOTS.append((CX1 - 0.1, OX1 + 0.1, SLOT_Y[0], SLOT_Y[1], z0, z1))      # right wall
for sl in SLOTS:
    tray = tray.cut(lbox(*sl))
# carrier interface through the floor
RAD_ATTACH = [(37.5, 8.0), (37.5, -8.0), (24.5, 12.0)]
for x, z in RAD_ATTACH:
    tray = tray.cut(cy(PILOT_M2 / 2, Y_FLOOR_IN - 0.1, Y_FACE + 0.1, x, z))
DISPLAY_SCREWS = [(32.0, 18.0), (32.0, -18.0)]
for x, z in DISPLAY_SCREWS:
    tray = tray.cut(cy(2.7, Y_FLOOR_IN - 0.1, Y_FACE + 0.1, x, z))
M3_HEADS = [(16.0, 16.0), (16.0, -16.0)]
for x, z in M3_HEADS:
    tray = tray.cut(cy(3.4, Y_FLOOR_IN - 0.1, Y_FACE + 0.1, x, z))
for x, z in ears:
    tray = tray.cut(cy(PILOT_M2 / 2, Y_LID_IN - 0.1, Y_LID_IN + EAR_PILOT_DEPTH, x, z))
tray = tray.removeSplitter()

# ---------------------------------------------------------------- lid
lid = lbox(OX0, OX1, Y_LID_OUT, Y_LID_IN, OZ0, OZ1)
lid = fuse(lid, *[cy(EAR_R, Y_LID_OUT, Y_LID_IN, x, z) for x, z in ears])
lip_out = lbox(CX0 + 0.25, CX1 - 0.25, Y_LID_IN, Y_LID_IN + 1.2, CZ0 + 0.25, CZ1 - 0.25)
lip_in = lbox(CX0 + 1.25, CX1 - 1.25, Y_LID_IN - 0.1, Y_LID_IN + 1.3, CZ0 + 1.25, CZ1 - 1.25)
lid = fuse(lid, lip_out.cut(lip_in))
for x0, x1 in CORNER_X:
    for z0, z1 in (POST_Z_SD, POST_Z_FAR):
        lid = fuse(lid, lbox(x0, x1, Y_LID_IN, Y_BACK - PCB_T - POST_GAP, z0, z1))
LENS_X, LENS_Z = xb(13.5), zb(LEN_FROM_SD_END)
lid = lid.cut(cy(4.5, Y_LID_OUT - 0.1, Y_LID_IN + 0.1, LENS_X, LENS_Z))   # 7 mm lens, 1 mm per side for placement slop
for x, z in ears:
    lid = lid.cut(cy(M2_CLEAR / 2, Y_LID_OUT - 0.1, Y_LID_IN + 0.1, x, z))
    lid = lid.cut(cy(2.4, Y_LID_OUT - 0.1, Y_LID_OUT + 1.2, x, z))
lid = lid.removeSplitter()

# ---------------------------------------------------------------- checks
doc = A.openDocument(str(ASM))
G = {o.Name: o.Shape for o in doc.Objects if hasattr(o, 'Shape') and not o.Shape.isNull()}
Import.open(BOARD_STEP)
bd = A.ActiveDocument
asm_obj = max((o for o in bd.Objects if hasattr(o, 'Shape') and not o.Shape.isNull()), key=lambda o: len(o.Shape.Solids))
board_solids = list(asm_obj.Shape.Solids)
assert 100 <= len(list(asm_obj.Shape.Solids)) <= 130
# Replace the STEP's camera, SD holder, module and PCB heights with Jim's caliper values (all from the PCB back face):
# PCB 0.8; SD holder top 4.4; camera square top 6.75 (it rests on the SD holder); lens tip 9.4, lens circle 7 mm;
# ESP32 module + PCB thickest 6.2 (module 5.4 behind the PCB).
keep = []
for s_ in board_solids:
    bb_ = s_.BoundBox
    if abs(s_.Volume - 1079.1) < 2 and bb_.YLength < 1.1:        continue      # PCB -> measured box
    if bb_.YMax > 3.25:                                           continue      # camera parts
    if abs(bb_.YMin - 1.2) < 0.01 and abs(bb_.YMax - 3.2) < 0.01: continue      # SD holder -> measured box
    if s_.Volume > 900 and bb_.YMax < 0:                          continue      # ESP32 module -> measured box
    keep.append(s_)
def bx(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, A.Vector(x0, y0, z0))
pcb_s = bx(0, 40, 0, PCB_T, 0, 27)
sd_holder = bx(0.34, 15.34, PCB_T, 4.4, 5.77, 21.77)
cam_flange = bx(3.67, 19.13, 4.4, 6.75, 9.26, 17.76)
lens_s = Part.makeCylinder(3.5, 9.4 - 6.75, A.Vector(11.4, 6.75, 13.5), A.Vector(0, 1, 0))
module_s = bx(15.33, 34.57, -5.4, 0.0, 4.84, 22.91)
board_solids = keep + [pcb_s, sd_holder, cam_flange, lens_s, module_s]
pin_solids = [s for s in board_solids if s.BoundBox.YMin < -8.9]
M = A.Matrix(0, 0, -1, XC + 13.5, 0, -1, 0, Y_BACK, -1, 0, 0, Z_SD, 0, 0, 0, 1)
def place(s):
    return s.copy().transformShape(M)
board = [place(s) for s in board_solids]
board_comp = Part.makeCompound(board)
pcb, lens, module_b = place(pcb_s), place(lens_s), place(module_s)

report = {'case': {}, 'checks': {}}
for name, s in (('tray', tray), ('lid', lid)):
    report['case'][name] = {'valid': s.isValid(), 'solids': len(s.Solids), 'volume_mm3': round(s.Volume, 1),
                            'bbox_local': [round(v, 2) for v in (s.BoundBox.XMin, s.BoundBox.XMax, s.BoundBox.YMin,
                                                                 s.BoundBox.YMax, s.BoundBox.ZMin, s.BoundBox.ZMax)]}
    assert s.isValid() and len(s.Solids) == 1, name


def glob(s):
    c = s.copy()
    c.translate(GLOBAL)
    return c


tray_g, lid_g, board_g = glob(tray), glob(lid), glob(board_comp)
case_g = Part.makeCompound([tray_g, lid_g])

# 1. board vs case: no overlap, and the clearances that matter
ov_tray = tray_g.common(board_g).Volume
ov_lid = lid_g.common(board_g).Volume
report['checks']['board_tray_overlap_mm3'] = round(ov_tray, 6)
report['checks']['board_lid_overlap_mm3'] = round(ov_lid, 6)
pcb_g = glob(pcb)
report['checks']['pcb_to_pads_mm'] = round(pcb_g.distToShape(tray_g)[0], 4)
report['checks']['pcb_to_lid_posts_mm'] = round(pcb_g.distToShape(lid_g)[0], 4)
lens_tip_y = lens.BoundBox.YMin  # forward-most in local frame (most negative y)
report['checks']['lens_tip_local_y'] = round(lens_tip_y, 3)
report['checks']['lens_tip_vs_lid_outer_face_mm'] = round(lens_tip_y - Y_LID_OUT, 3)   # + means tip is behind the face
report['checks']['lens_xz_local'] = [round(lens.BoundBox.Center.x, 3), round(lens.BoundBox.Center.z, 3)]
report['checks']['lens_hole_xz_local'] = [round(LENS_X, 3), round(LENS_Z, 3)]
lens_g = glob(lens)
report['checks']['lens_to_lid_hole_edge_mm'] = round(lens_g.distToShape(lid_g)[0], 3)
report['checks']['board_to_lid_min_mm'] = round(board_g.distToShape(lid_g)[0], 3)

# 2. Dupont housings (2.6 x 2.6 x 14) on every header pin
dup_overlaps, dup_floor = [], []
for s in pin_solids:
    cxb, czb = s.BoundBox.Center.x, s.BoundBox.Center.z
    px, pz = xb(czb), zb(cxb)
    y_a = Y_BACK + HDR_PLASTIC                  # housing seats on the header plastic (rear of PCB)
    box = lbox(px - 1.3, px + 1.3, y_a, y_a + LC, pz - 1.3, pz + 1.3)
    dup_overlaps.append(round(glob(box).common(tray_g).Volume, 6))
    dup_floor.append(round(Y_FLOOR_IN - (y_a + LC), 3))
report['checks']['dupont_pin_count'] = len(pin_solids)
mod_g = glob(module_b)
report['checks']['dupont_vs_module_overlap_mm3'] = round(max(glob(lbox(xb(s.BoundBox.Center.z) - 1.3, xb(s.BoundBox.Center.z) + 1.3, Y_BACK + HDR_PLASTIC, Y_BACK + HDR_PLASTIC + LC, zb(s.BoundBox.Center.x) - 1.3, zb(s.BoundBox.Center.x) + 1.3)).common(mod_g).Volume for s in pin_solids), 6)
report['checks']['module_to_tray_min_mm'] = round(mod_g.distToShape(tray_g)[0], 3)
report['checks']['dupont_tray_overlap_max_mm3'] = max(dup_overlaps)
report['checks']['dupont_end_to_floor_mm'] = min(dup_floor)
report['checks']['dupont_wall_clearance_mm'] = round(min(
    glob(lbox(xb(s.BoundBox.Center.z) - 1.3, xb(s.BoundBox.Center.z) + 1.3, Y_BACK + HDR_PLASTIC, Y_BACK + HDR_PLASTIC + LC,
              zb(s.BoundBox.Center.x) - 1.3, zb(s.BoundBox.Center.x) + 1.3)).distToShape(tray_g)[0] for s in pin_solids), 3)

# 3. carrier / frame interference and clearances
for n in ('GH44_Dual_Carrier', 'ToF_Sensor_Frame', 'Dual_ToF_Envelope', 'Rear_Display_Frame', 'GH44_Tilt_Receiver'):
    report['checks']['case_vs_%s_overlap_mm3' % n] = round(case_g.common(G[n]).Volume, 6)
report['checks']['tray_to_carrier_mm'] = round(tray_g.distToShape(G['GH44_Dual_Carrier'])[0], 4)
report['checks']['case_to_ToF_frame_mm'] = round(case_g.distToShape(G['ToF_Sensor_Frame'])[0], 3)
report['checks']['case_to_ToF_envelope_mm'] = round(case_g.distToShape(G['Dual_ToF_Envelope'])[0], 3)
report['checks']['tray_floor_seats_on_carrier_face'] = abs(tray.BoundBox.YMax - Y_FACE) < 1e-6

# 4. screw / driver access with the lid and board absent
def probe(r, y0, y1, x, z, shape):
    return round(glob(cy(r, y0, y1, x, z)).common(shape).Volume, 6)

acc = {}
for x, z in DISPLAY_SCREWS:
    acc['display_M2_driver_r2.4 (%g,%g)' % (x, z)] = probe(2.4, -140, Y_FACE, x, z, tray_g)
for x, z in M3_HEADS:
    acc['carrier_M3_driver_r2.2 (%g,%g)' % (x, z)] = probe(2.2, -140, Y_FACE, x, z, tray_g)
    acc['carrier_M3_head_pocket_r3.0_in_floor (%g,%g)' % (x, z)] = probe(3.0, Y_FLOOR_IN, Y_FACE, x, z, tray_g)
for x, z in RAD_ATTACH:
    acc['M2x6_shank_through_carrier_and_floor (%g,%g)' % (x, z)] = probe(1.0, Y_FACE - 3.2, -50, x, z, tray_g)  # must be 0 only in the carrier part
for x, z in ears:
    acc['lid_screw_clear_hole (%g,%g)' % (x, z)] = probe(1.25, Y_LID_OUT, Y_LID_IN, x, z, lid_g)
report['checks']['screw_access_overlap_mm3'] = acc

# 5. fields of view, conservative
y_ap = -86.5                                   # ToF front reservation plane (local)
tof_apex = A.Vector(-15.0, y_ap, 0.0)
H = 90.0
hw = H                                         # 45 deg half-angle each axis
v = [tof_apex, A.Vector(-15 - hw, y_ap - H, -hw), A.Vector(-15 + hw, y_ap - H, -hw),
     A.Vector(-15 + hw, y_ap - H, hw), A.Vector(-15 - hw, y_ap - H, hw)]
def pyramid(apex, base):
    faces = [Part.Face(Part.makePolygon([base[i], base[(i + 1) % 4], apex, base[i]])) for i in range(4)]
    faces.append(Part.Face(Part.makePolygon(base + [base[0]])))
    return Part.Solid(Part.Shell(faces))
tof_fov = pyramid(v[0], v[1:])
tof_fov.translate(GLOBAL)
report['checks']['ToF_fov_45deg_vs_case_overlap_mm3'] = round(case_g.common(tof_fov).Volume, 6)
report['checks']['ToF_fov_assumption'] = 'square pyramid, 45 deg half-angle each axis (SEN0628 is 60 deg total), apex at the ToF front reservation plane y=-86.5, x=-15, z=0'
cam_apex = A.Vector(LENS_X, lens_tip_y + 1.5, LENS_Z)
cam_fov = Part.makeCone(0.0, 120.0 * math.tan(math.radians(40)), 120.0, cam_apex, A.Vector(0, -1, 0))
cam_fov.translate(GLOBAL)
for n in ('ToF_Sensor_Frame', 'Dual_ToF_Envelope', 'GH44_Dual_Carrier'):
    report['checks']['camera_fov_40deg_vs_%s_overlap_mm3' % n] = round(cam_fov.common(G[n]).Volume, 6)
report['checks']['camera_fov_vs_lid_overlap_mm3'] = round(cam_fov.common(lid_g).Volume, 6)
report['checks']['camera_fov_assumption'] = 'cone 40 deg half-angle (OV2640 is about 32 deg half diagonal) from 1.5 mm behind the lens tip'
report['checks']['lens_tip_ahead_of_ToF_front_mm'] = round(y_ap - Y_LID_OUT, 3)
report['checks']['case_front_global_Y'] = round(lid_g.BoundBox.YMin, 3)

# 6. pan / tilt sweeps against the rest of the assembly
tilt_pt, tilt_dir = A.Vector(0, 87.0, 216.5), A.Vector(1, 0, 0)
pan_pt, pan_dir = A.Vector(39.5, 113.0, 0), A.Vector(0, 0, 1)
static = [n for n in G if n.startswith('Ctx_') or n in ('Neck_Main', 'Neck_Clamp_Cap', 'Pan_Servo_Carriage', 'SG90_Pan_Reference')]
pan_mov = ['Pan_Rotor', 'Pan_Retainer', 'Pan_Raised_Pedestal', 'Pan_Drive_Pulley', 'Pan_Belt_Reference', 'Pan_Bearing_Lower',
           'Pan_Bearing_Upper', 'Pan_Inner_Spacer', 'Pan_Circlip_Envelope', 'Tilt_Yoke', 'SG90_Tilt_Reference', 'Tilt_Pivot_Bolt']
sweep = {'static_overlap_max_mm3': 0.0, 'pan_moving_overlap_max_mm3': 0.0, 'poses_bbox_close': 0, 'poses': 0,
         'min_static_gap_mm': 1e9}
parts_t = [tray_g, lid_g]
for tilt in range(-25, 26, 5):
    t = [p.copy() for p in parts_t]
    for p in t:
        p.rotate(tilt_pt, tilt_dir, float(tilt))
    for n in pan_mov:
        for p in t:
            if p.BoundBox.intersect(G[n].BoundBox):
                v_ = p.common(G[n]).Volume
                if v_ > 1e-6:
                    sweep.setdefault('pan_moving_hits', []).append([tilt, n, 'tray' if p is t[0] else 'lid', round(v_, 3)])
                sweep['pan_moving_overlap_max_mm3'] = max(sweep['pan_moving_overlap_max_mm3'], v_)
    for pan in range(-200, 201, 10):
        sweep['poses'] += 1
        pp = [p.copy() for p in t]
        for p in pp:
            p.rotate(pan_pt, pan_dir, float(pan))
        for n in static:
            sb = G[n].BoundBox
            for p in pp:
                bb = p.BoundBox
                if bb.intersect(sb):
                    sweep['poses_bbox_close'] += 1
                    sweep['static_overlap_max_mm3'] = max(sweep['static_overlap_max_mm3'], p.common(G[n]).Volume)
                    sweep['min_static_gap_mm'] = min(sweep['min_static_gap_mm'], p.distToShape(G[n])[0])
if sweep['min_static_gap_mm'] > 1e8:
    # no bounding box ever overlaps: report the lowest case z and lowest static top for context
    sweep['min_static_gap_mm'] = None
report['checks']['sweep'] = sweep

if sweep.get('pan_moving_hits'):
    yk = G['Tilt_Yoke'].copy()
    yk.rotate(tilt_pt, tilt_dir, -25.0)
    reg = tray_g.common(yk)
    bb = reg.BoundBox
    sweep['hit_region_local_bbox'] = [round(v, 3) for v in (bb.XMin - 39.5, bb.XMax - 39.5, bb.YMin - 113, bb.YMax - 113,
                                                           bb.ZMin - 216.5, bb.ZMax - 216.5)]
    pts = []
    for v_ in reg.Vertexes:
        pts.append([round(v_.X - 39.5, 2), round(v_.Y - 113, 2), round(v_.Z - 216.5, 2)])
    sweep['hit_region_vertices_local'] = pts[:40]
# lowest point of the case at the worst tilt, for the neck clearance context
lows = []
for tilt in (-25, 25):
    for p in parts_t:
        c = p.copy(); c.rotate(tilt_pt, tilt_dir, float(tilt)); lows.append(c.BoundBox.ZMin)
report['checks']['case_lowest_global_z_at_tilt_extremes'] = round(min(lows), 2)
report['checks']['neck_main_top_global_z'] = round(G['Neck_Main'].BoundBox.ZMax, 2)

# 7. independent additions (review 2026-10-13)
extra = {}
# (a) the M2x6 shank really passes the carrier's clear hole and the tray pilot
for x, z in RAD_ATTACH:
    extra['M2_shank_r1.0_vs_carrier (%g,%g)' % (x, z)] = round(glob(cy(1.0, Y_FLOOR_IN, -50.0, x, z)).common(G['GH44_Dual_Carrier']).Volume, 6)
# (b) every one of the 16 wires: from the connector's rear end down to the slot level, then straight out through its wall
wire_hits = []
for k in range(8):
    pz = PIN_Z[k]
    for side, px, x_out in (('left', xb(25.2), OX0 - 4.0), ('right', xb(2.2), OX1 + 4.0)):
        y_end = Y_BACK + HDR_PLASTIC + LC
        yc = Y_FLOOR_IN - 1.7                                   # wire centre inside the slot (slot is 3.4 tall)
        seg1 = lbox(px - 0.7, px + 0.7, y_end, yc, pz - 0.7, pz + 0.7)          # connector end -> slot level
        seg2 = lbox(min(px, x_out) - 0.7, max(px, x_out) + 0.7, yc - 0.7, yc + 0.7, pz - 0.7, pz + 0.7)  # sideways, out the wall
        wire_hits.append(round(glob(seg1).common(tray_g).Volume + glob(seg2).common(tray_g).Volume, 6))
extra['wire_probes_16_vs_tray_max_mm3'] = max(wire_hits)
extra['wire_probe_count'] = len(wire_hits)
extra['wire_slot_strut_to_nearest_wire_mm'] = round(min(abs(PIN_Z[3] - (_mid + STRUT / 2)), abs(PIN_Z[4] - (_mid - STRUT / 2))) - 0.7, 3)
# (c) SD card ejection path: a card-wide, holder-height-deep box swept out through the window along +z
card_x0, card_x1 = xb(18.05), xb(6.95)
card = lbox(card_x0 - 0.3, card_x1 + 0.3, Y_BACK - 4.4, Y_BACK - PCB_T, Z_SD - 15.0, Z_SD + 12.0)
extra['sd_card_path_vs_tray_mm3'] = round(glob(card).common(tray_g).Volume, 6)
extra['sd_card_path_vs_lid_mm3'] = round(glob(card).common(lid_g).Volume, 6)
extra['sd_wall_left_at_pocket_mm'] = 1.0
# (d) 1-degree tilt sweep against everything that moves with the pan, both directions
fine = 0.0
for tilt10 in range(-250, 251, 10):
    tl = tilt10 / 10.0
    for p_ in (tray_g, lid_g):
        c_ = p_.copy(); c_.rotate(tilt_pt, tilt_dir, tl)
        for n in pan_mov:
            if c_.BoundBox.intersect(G[n].BoundBox):
                fine = max(fine, c_.common(G[n]).Volume)
extra['tilt_sweep_1deg_pan_moving_overlap_max_mm3'] = round(fine, 6)
# (e) tray/lid assembled with no interference of their own
extra['tray_vs_lid_overlap_mm3'] = round(tray_g.common(lid_g).Volume, 6)
report['checks']['review_additions'] = extra

# ---------------------------------------------------------------- hard assertions
c = report['checks']
(OUT / 'validation-prelim.json').write_text(json.dumps(report, indent=1, default=str))
assert c['board_tray_overlap_mm3'] < 1e-4 and c['board_lid_overlap_mm3'] < 1e-4, 'board interferes with the case'
assert c['dupont_tray_overlap_max_mm3'] < 1e-6 and c['dupont_vs_module_overlap_mm3'] < 1e-6
for n in ('GH44_Dual_Carrier', 'ToF_Sensor_Frame', 'Dual_ToF_Envelope', 'Rear_Display_Frame', 'GH44_Tilt_Receiver'):
    assert c['case_vs_%s_overlap_mm3' % n] < 1e-6, n
for k, vv in acc.items():
    if k.startswith('M2x6'):
        continue
    assert vv < 1e-6, (k, vv)
assert c['ToF_fov_45deg_vs_case_overlap_mm3'] < 1e-6
assert c['camera_fov_vs_lid_overlap_mm3'] < 1e-6
assert sweep['static_overlap_max_mm3'] < 1e-6 and sweep['pan_moving_overlap_max_mm3'] < 1e-6
for k, vv in extra.items():
    if k.endswith('mm3') or 'mm3' in k:
        assert vv < 1e-4, (k, vv)
report['checks']['all_asserts_pass'] = True

# ---------------------------------------------------------------- exports
def mesh(shape):
    return MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.02, AngularDeflection=0.25)

def to_print(shape, which):
    c = shape.copy()
    if which == 'tray':      # floor mating face down, cavity opens up: (x,y,z) -> (x-XC, z, -58-y)
        m = A.Matrix(1, 0, 0, -XC, 0, 0, 1, 0, 0, -1, 0, Y_FACE, 0, 0, 0, 1)
    else:                    # lid: outer face down, lip/posts up: (x,y,z) -> (x-XC, -z, y-Y_LID_OUT)
        m = A.Matrix(1, 0, 0, -XC, 0, 0, -1, 0, 0, 1, 0, -Y_LID_OUT, 0, 0, 0, 1)
    c = c.transformShape(m)
    bb = c.BoundBox
    c.translate(A.Vector(-bb.XMin, -bb.YMin, -bb.ZMin))
    return c

for name, s in (('tray', tray), ('lid', lid)):
    ps = to_print(s, name)
    m = mesh(ps)
    fn = OUT / 'stl' / ('ESP32_CAM_Case_v4_%s.stl' % name.capitalize())
    m.write(str(fn))
    report['case'][name]['stl'] = fn.name
    report['case'][name]['print_bbox_mm'] = [round(ps.BoundBox.XLength, 2), round(ps.BoundBox.YLength, 2), round(ps.BoundBox.ZLength, 2)]
    report['case'][name]['mesh_solid'] = bool(m.isSolid())
    report['case'][name]['mesh_triangles'] = m.CountFacets
# assembled-pose previews (head local frame)
for name, s in (('tray', tray), ('lid', lid), ('board', board_comp)):
    mesh(s).write(str(OUT / 'preview' / ('assembled_%s_local.stl' % name)))
for n in ('GH44_Dual_Carrier', 'ToF_Sensor_Frame'):
    c = G[n].copy(); c.translate(-GLOBAL)
    mesh(c).write(str(OUT / 'preview' / ('ctx_%s_local.stl' % n)))

report['design'] = {
    'frame': 'head local: X right, Y rearward, Z up from tilt axis; sensors face -Y',
    'measured_by_jim': 'PCB 0.8; SD holder top 4.4; camera square top 6.75; lens tip 9.4 (all from PCB back); lens circle 7; module+PCB 6.2',
    'board_centre_x': XC, 'sd_end': 'UP (+z)', 'board_wh_assumed': [BOARD_W, BOARD_L],
    'floor_y': [Y_FLOOR_IN, Y_FACE], 'pcb_back_y': Y_BACK, 'lid_outer_y': Y_LID_OUT,
    'carrier_interface': 'same three M2 pilots as the radar frame at (37.5,+-8) and (24.5,12), M2x6 from carrier rear',
    'tray_outer_x': [round(OX0, 3), round(OX1, 3)], 'tray_outer_z': [round(OZ0, 3), round(OZ1, 3)],
    'cavity_xz': [round(CX0, 3), round(CX1, 3), round(CZ0, 3), round(CZ1, 3)],
    'sd_window_x': [round(SD_WIN[0], 3), round(SD_WIN[1], 3)], 'sd_window_y': [round(SD_WIN[2], 3), round(SD_WIN[3], 3)],
    'wire_slots_local': [[round(v, 3) for v in sl] for sl in SLOTS],
    'ears_xz': [[round(x, 3), round(z, 3)] for x, z in ears],
}
(OUT / 'validation.json').write_text(json.dumps(report, indent=1))
print(json.dumps(report, indent=1))
