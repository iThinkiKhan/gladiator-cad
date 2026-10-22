"""Gladiator head v0.5 - the pan stack, rebuilt from the measured numbers.

What this builds (everything the PAN drive needs, calibrated and re-based):
    Neck_Main, Neck_Clamp_Cap   collar with the tested 1-notch key, M3 nut pockets, C arm,
                                spindle with the circlip groove, servo pad and riser
    Pan_Servo_Carriage          slides on the pad: belt tension and belt installation
    Pan_Rotor, Pan_Retainer     bearing seats at the tested 32.35, M2 pilots
    Pan_Raised_Pedestal         integral 40T driven ring, 4 retainer screws, yoke seat
    Pan_Drive_Pulley            60T with a horn plate that takes the real SG90 cross horn
    SG90 / horn / belt / bearings as clearance references

Stage 2 regenerates the tilt yoke, GH44 receiver, carrier and display frame.
Only sensor clearance envelopes and unused carrier variants remain inherited references.
Frame: local = mast axis at the origin, mast top drawn at Z 120. Everything is stored in the
FreeCAD file at real position, which is local + (39.5, 113, LIFT=10), so it overlays the master.

Run with freecadcmd on the CAD server. Never writes the master.
"""
import sys, json, math, hashlib, itertools, zipfile
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod', '/usr/lib/freecad-python3/lib'])
import FreeCAD as A
import Part, Mesh, MeshPart

ROOT = Path('/home/buralien/projects/gladiator-cad')
SOURCE = ROOT / 'cad/head/v03-belt/Gladiator_Head_v03_Belt.FCStd'
MASTER = ROOT / 'cad/master/Gladiator_Master.FCStd'
OUT = ROOT / 'cad/head/v05-sensor-mounts'
(OUT / 'stl').mkdir(parents=True, exist_ok=True)

# ================================================================== parameters
LIFT = 10.0                       # real mast top 130, drawn at 120
C0 = A.Vector(39.5, 113.0, 0.0)   # mast axis, real XY
WORLD = C0 + A.Vector(0, 0, LIFT)

# --- belt and drive (settled: 60T on the servo, 40T on the head, the 2-notch groove) ---------
PITCH, PLD, TOOTH_DEPTH, GROOVE_R = 2.0, 0.254, 0.75, 0.65
N_DRIVE, N_DRIVEN = 60, 40
BELT_TEETH, BELT_W = 90, 6.0
RATIO = N_DRIVE / float(N_DRIVEN)             # head degrees per servo degree = 1.5
HEAD_TRAVEL = (-20.0, 180.0)
SERVO_TRAVEL = (HEAD_TRAVEL[1] - HEAD_TRAVEL[0]) / RATIO
CHANNEL, FLANGE_OVER, CONE_H, RIM_T, RIM_WALL = 7.0, 1.5, 1.5, 0.6, 2.5

# --- slot: tightest about mid-slot (about 39.75) by Jim's eyeball; theory 39.49, 39.88 if small --
C_MIN, C_MAX = 37.0, 40.4         # carriage travel. C_MIN gives belt slack; C_MAX is past taut
C_NOM = 39.75
SERVO_ANG = 225.0                 # forward-left, as v0.3
DELTA = SERVO_ANG - 270.0

# --- fits, from the coupons and calibration -------------------------------------------------
M3_CLEAR, M2_CLEAR, NUT_AF, NUT_DEPTH = 3.6, 2.6, 6.0, 2.6
PILOT_M2 = 2.35       # SETTLED 2026-10-01: Jim, H4b "right in the middle between 1 and 2" (2.3 / 2.4)
POST_D = 20.05        # SETTLED 2026-10-01: Jim, H3b "two notch post wins" (20.20 had jammed a 6804)
SEAT_D = 32.35        # plate F coupon #2, fitted perfectly
BRG_ID, BRG_OD, BRG_W = 20.0, 32.0, 7.0
GROOVE_D, GROOVE_W, GROOVE_GAP, LAND = 19.25, 1.4, 0.1, 1.6
BED_RELIEF = 0.5

# --- mast collar, the tested 1-notch key ----------------------------------------------------
BORE_R, COLLAR_R = 10.2, 14.0
FLAT_Y, KEY_HALF, KEY_GAP = 9.1, 3.6, 0.10

# --- SG90, Jim's calipers 2026-10-01 -------------------------------------------------------
BODY_L, BODY_W = 22.8, 12.0       # the tested opening, not the 22.7 caliper reading
SHAFT_NEAR = 5.9                  # +-0.6, from Jim's 4 and about 15 with the 22.7 length
BODY_CTR = -(BODY_L / 2.0 - SHAFT_NEAR)     # body centre, from the shaft toward the outer end: -5.5
EAR_UNDER, EAR_T, BOSS_TOP, SPLINE_TOP = 17.5, 2.5, 28.5, 32.0
EAR_PITCH, EAR_SPAN = 27.2, 32.5

# --- cross horn, Jim 2026-10-01 -------------------------------------------------------------
HORN_LONG, HORN_SHORT = 36.0, 19.0
LONG_W_HUB, LONG_W_TIP, SHORT_W = 6.8, 4.8, 3.8
BOSS_D, BOSS_UP = 7.1, 1.0
ARM_T = 2.0           # ASSUMED, not measured. H6 will show it.
# MEASURED 2026-10-05 (Jim): ear underside to the top of the raised hub ring, horn pushed fully on = 16.5.
# The old model put the arm top at 13.25 (horn sitting 0.25 over the case boss); the real horn stands on a
# lower hub that covers the spline, so the arm top is 16.5 - BOSS_UP = 15.5 above the ear underside.
HORN_TOP = 16.5
HORN_G = HORN_TOP - BOSS_UP - ARM_T - (BOSS_TOP - EAR_UNDER)   # case boss to arm underside, 2.5
LOWER_HUB_GAP = 0.25  # ASSUMED gap between the case boss and the bottom of the horn's lower hub
HORN_C = 0.15         # SETTLED 2026-10-01: Jim, H6 "one notch horn pocket" (snug 0.15, not easy 0.30)
# The recess was 1.3 on the H6 coupon. Here the spline top stands 1.25 above the arms, so 1.3 left
# 0.05 mm to the roof, and the plate would have rested on the spline instead of clamping the horn.
POCKET_DEPTH, BOSS_RECESS, ROOF_T = 1.2, BOSS_UP + 0.6, 1.2
PLATE_T = POCKET_DEPTH + BOSS_RECESS + ROOF_T     # 3.7
CENTRE_HOLE = 3.4

# --- Z stack (local, mast top 120) ----------------------------------------------------------
BRG_LO_Z, BRG_HI_Z = 121.0, 137.0
GROOVE_Z = BRG_HI_Z + BRG_W + GROOVE_GAP          # 144.1
POST_TOP = GROOVE_Z + GROOVE_W + LAND             # 147.1
RET_Z, RET_T = 144.0, 3.0                         # retainer 144..147
PED_Z, PED_BASE_T = 147.0, 3.0                    # pedestal base plate 147..150
PLATE_RIM_Z = PED_Z + PED_BASE_T + 1.0            # 151.0, 1 mm over the base plate
ZC = PLATE_RIM_Z + PLATE_T                        # 154.7, belt channel bottom
TOP_PLATE_Z, TOP_PLATE_T = 165.5, 4.0             # was 164; the 60T pulley top is 164.1
TILT_SHIFT = TOP_PLATE_Z - 164.0                  # the inherited tilt side rises by this (1.5)
R_ROT = 21.5                                      # rotor / retainer / pedestal radius (was 20.5)
R_SCREW = 18.8                                    # retainer screw circle (was 18.3)

ARM_TOP = PLATE_RIM_Z + POCKET_DEPTH              # 152.2: the horn arm top touches the pocket floor
HORN_UNDER = ARM_TOP - ARM_T
ZP = HORN_UNDER - (BOSS_TOP - EAR_UNDER) - HORN_G  # ear plane, 138.95
ZSB = ZP - EAR_UNDER                              # servo body bottom, 121.45
CAR_T, PAD_T = 3.0, 4.5
PAD_TOP = ZP - CAR_T
PAD_BOT = PAD_TOP - PAD_T


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


before = {str(MASTER): digest(MASTER), str(SOURCE): digest(SOURCE), str(Path(__file__)): digest(__file__)}


# ================================================================== helpers
def box(x, y, z, dx, dy, dz): return Part.makeBox(dx, dy, dz, A.Vector(x, y, z))
def cyl(r, z, h, x=0.0, y=0.0): return Part.makeCylinder(r, h, A.Vector(x, y, z))
def cy(r, y, h, x, z): return Part.makeCylinder(r, h, A.Vector(x, y, z), A.Vector(0, 1, 0))
def ring(ro, ri, z, h, x=0.0, y=0.0): return cyl(ro, z, h, x, y).cut(cyl(ri, z - .1, h + .2, x, y))


def fuse(*ss):
    s = ss[0]
    for t in ss[1:]:
        s = s.fuse(t)
    return s.removeSplitter()


def prism(pts, z, h):
    vs = [A.Vector(x, y, z) for x, y in pts]
    return Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(A.Vector(0, 0, h))


def hex_z(af, z, h, x, y):
    r = af / math.sqrt(3)
    return prism([(x + r * math.cos(k * math.pi / 3), y + r * math.sin(k * math.pi / 3))
                  for k in range(6)], z, h)


def hex_y(af, y, depth, x, z):
    r = af / math.sqrt(3)
    pts = [A.Vector(x + r * math.cos(k * math.pi / 3), y, z + r * math.sin(k * math.pi / 3)) for k in range(6)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(A.Vector(0, depth, 0))


def slot_z(x, y1, y2, z, h, w):
    r = w / 2.0
    return fuse(cyl(r, z, h, x, y1), cyl(r, z, h, x, y2), box(x - r, y1, z, w, y2 - y1, h))


def wedge(r, z, h, a0, a1):
    seg = cyl(r, z, h)
    keep, a = [], a0
    while a < a1 - 1e-9:
        b = min(a + 15.0, a1)
        tri = Part.makePolygon([A.Vector(0, 0, z),
                                A.Vector(2 * r * math.cos(math.radians(a)), 2 * r * math.sin(math.radians(a)), z),
                                A.Vector(2 * r * math.cos(math.radians(b)), 2 * r * math.sin(math.radians(b)), z),
                                A.Vector(0, 0, z)])
        keep.append(Part.Face(tri).extrude(A.Vector(0, 0, h)))
        a = b
    return seg.common(fuse(*keep))


def belt_len(C, r1, r2):
    a = math.asin((r1 - r2) / C)
    return 2 * math.sqrt(C * C - (r1 - r2) ** 2) + r1 * (math.pi + 2 * a) + r2 * (math.pi - 2 * a)


def solve_c(r1, r2, L):
    lo, hi = 20.0, 80.0
    for _ in range(80):
        m = (lo + hi) / 2
        if belt_len(m, r1, r2) > L:
            hi = m
        else:
            lo = m
    return lo


def pitch_r(n): return n * PITCH / (2 * math.pi)
def tip_r(n): return pitch_r(n) - PLD


R_DRIVE_P, R_DRIVEN_P = pitch_r(N_DRIVE), pitch_r(N_DRIVEN)
C_THEORY = solve_c(R_DRIVE_P, R_DRIVEN_P, BELT_TEETH * PITCH)
SERVO_POS = A.Vector(C_NOM * math.cos(math.radians(SERVO_ANG)),
                     C_NOM * math.sin(math.radians(SERVO_ANG)), 0)


def rotF(shape):
    """Frame F (servo straight out along -Y) into the final frame, 225 degrees."""
    s = shape.copy()
    s.rotate(A.Vector(), A.Vector(0, 0, 1), DELTA)
    return s


def grooves_for(n, ro, z, h):
    rc = ro - TOOTH_DEPTH + GROOVE_R
    return [cyl(GROOVE_R, z - 0.1, h + 0.2, rc * math.cos(2 * math.pi * i / n), rc * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def flanges(ro, z_top, cx=0.0, cy_=0.0, r_in=None):
    """45 degree cone, then a thin rim, above the channel. No support needed."""
    fr = ro + FLANGE_OVER
    cone = Part.makeCone(ro, fr, CONE_H, A.Vector(cx, cy_, z_top))
    rim = cyl(fr, z_top + CONE_H, RIM_T, cx, cy_)
    if r_in:
        cone = cone.cut(cyl(r_in, z_top - .1, CONE_H + .2, cx, cy_))
        rim = rim.cut(cyl(r_in, z_top + CONE_H - .1, RIM_T + .2, cx, cy_))
    return cone, rim


def horn_solid(c, z, h):
    """The cross horn outline grown by c on every side, extruded z..z+h. Tips are rounded."""
    rb = BOSS_D / 2
    lt = HORN_LONG / 2 - LONG_W_TIP / 2
    st = HORN_SHORT / 2 - SHORT_W / 2
    h0, h1, hs = LONG_W_HUB / 2 + c, LONG_W_TIP / 2 + c, SHORT_W / 2 + c
    long_arm = prism([(-lt, -h1), (-rb, -h0), (rb, -h0), (lt, -h1), (lt, h1), (rb, h0), (-rb, h0), (-lt, h1)], z, h)
    return fuse(long_arm, cyl(h1, z, h, lt, 0), cyl(h1, z, h, -lt, 0),
                box(-hs, -st, z, 2 * hs, 2 * st, h), cyl(hs, z, h, 0, st), cyl(hs, z, h, 0, -st),
                cyl(rb + c, z, h))


report = {'release': 'v05 measured sensor mounts; prototype CAD checked, physical assembly not yet verified',
          'source_sha256': before, 'derived_from_v04_sha256': '228b5aab327ee1333d451dcba99aaa1191ff52ee734eecb20bdb387a5779d69e', 'parts': [], 'checks': {}, 'collisions': [],
          'pending': {}, 'assumed': {}, 'limitations': []}
report['pending'] = {
    'sensor_hardware': 'Measured-pattern frames designed; verify board orientation, M3 x16 lengths and connector/wire bends at assembly.',
    'harness_and_stops': 'Flex routing, strain relief and mechanical stops are not designed.',
    'horn_screws': 'Actual screw head and available thread engagement need full assembly checks.',
    'bearing_spacer': 'The modeled 9 mm inner-race spacer is not confirmed available hardware.',
    'screen': 'Pocket fit passed; final window alignment and corner screws remain unreported.',
}
report['settled'] = {
    'HORN_TOP': '%.1f ear underside to the top of the hub ring, horn fully on (Jim, 2026-10-05); arm top %.1f'
                % (HORN_TOP, HORN_TOP - BOSS_UP),
    'circlip': 'seats on the 2-notch post, "circlip fits well" (Jim, 2026-10-03)',
    'POST_D': '%.2f, H3b 2-notch post wins (Jim, 2026-10-01)' % POST_D,
    'PILOT_M2': '%.2f, H4b midway between 1 and 2 notches (Jim, 2026-10-01)' % PILOT_M2,
    'HORN_C': '%.2f, H6a 1-notch snug pocket (Jim, 2026-10-01)' % HORN_C,
}
report['assumed'] = {
    'ARM_T': '%.1f horn arm thickness, NOT measured' % ARM_T,
    'BOSS_UP': '%.1f hub ring above the arms ("about 1", Jim 10-01); sets the arm top under the 16.5 reading' % BOSS_UP,
    'LOWER_HUB_GAP': '%.2f case boss to the bottom of the horn lower hub, NOT measured' % LOWER_HUB_GAP,
    'SHAFT_NEAR': '%.1f from the near body end, about +-0.6' % SHAFT_NEAR,
    'servo_cross_centre': 'shaft assumed centred across the 12 mm width',
    'horn_screw_head': 'about 4 mm, read off a photo, NOT measured',
}

# ================================================ from v0.3: sensor envelopes and carrier variants only
# Stage 2 regenerates the yoke, receiver, carrier and display frame from code (below). Only the sensor
# clearance envelopes, which no coupon touches, and the unused carrier variants come from the v0.3 file.
src = A.openDocument(str(SOURCE))
inherit_names = []
variant_names = []  # old sensor variants use superseded dimensions; do not carry them forward
inh = {}
for n in inherit_names + variant_names:
    o = src.getObject(n)
    s = o.Shape.copy()
    s.translate(A.Vector(-C0.x, -C0.y, TILT_SHIFT))
    inh[n] = {'shape': s, 'motion': 'tilt'}
A.closeDocument(src.Name)

YOKE_BOLTS = [(-20.0, -25.0), (20.0, -25.0)]
T = A.Vector(0, -26, 205.0 + TILT_SHIFT)       # tilt axis

# ================================================================== the neck
parts = {}      # name -> dict(shape, motion, note)


def addp(name, shape, motion, note='', group='PanStack'):
    assert shape.isValid() and len(shape.Solids) == 1, name + ' invalid or disconnected'
    parts[name] = {'shape': shape, 'motion': motion, 'note': note, 'group': group}


collar = ring(COLLAR_R, BORE_R, 104, 16)
lug = fuse(box(-18, -5, 104.5, 9, 10, 9), box(9, -5, 104.5, 9, 10, 9))
collar = fuse(collar, lug).cut(cyl(BORE_R, 103, 18))
for x in (-13.5, 13.5):
    collar = collar.cut(cy(M3_CLEAR / 2, -6, 12, x, 109))
front = collar.common(box(-30, -30, 100, 60, 29.7, 25))
rear = collar.common(box(-30, .3, 100, 60, 30, 25))
# captive M3 nuts in the rear lugs, entered from the rear face (y +5), flat on top for bridging
for x in (-13.5, 13.5):
    rear = rear.cut(hex_y(NUT_AF, 5.0 - NUT_DEPTH, NUT_DEPTH + 0.2, x, 109))
key_y0 = FLAT_Y + KEY_GAP
rear = fuse(rear, box(-KEY_HALF, key_y0, 106, 2 * KEY_HALF, (BORE_R + 0.6) - key_y0, 13))

# C arm, as v0.3, passing under the rotor
arm = wedge(26, 114.5, 5.5, 88, 247).cut(cyl(15, 114, 7))
web = wedge(26, 114.5, 5.5, 95, 170).cut(cyl(10.2, 114, 7))
arm = fuse(arm, web)

# --- frame F: servo straight out along -Y, then rotated 225 degrees --------------------------
def y_bc(C): return -C + BODY_CTR                    # body centre y for a shaft at -C
# The two M3 clamp screws sit on a tab OUTBOARD of the servo, past the reach of the 60T flange
# (r20.3 around the shaft), so the belt can be tensioned with the pulley fitted. Their heads
# (at x +-8.5, 27.5 from the shaft) are 28 mm from the shaft axis; the flange stops at 20.3.
EXT = 9.0                                            # carriage tab beyond the ear region
NUT_X = 8.5
SLOT_OFF = -(17.5 + EXT / 2.0)                       # slot centre, from the carriage centre
NUT_Y = (y_bc(C_MIN) + y_bc(C_MAX)) / 2.0 + SLOT_OFF
PAD_Y0 = NUT_Y - NUT_AF / math.sqrt(3) - 2.0
PAD_Y1 = y_bc(C_MIN) + 17.5 + 0.5
PAD_HW = 13.5
riser = box(-11, -30.5, 119.5, 22, 8.0, PAD_BOT - 119.5 + 0.5)
pad = box(-PAD_HW, PAD_Y0, PAD_BOT, 2 * PAD_HW, PAD_Y1 - PAD_Y0, PAD_T)
pad = pad.cut(box(-(BODY_W / 2 + 0.4), y_bc(C_MAX) - BODY_L / 2 - 0.5, PAD_BOT - 1,
                  BODY_W + 0.8, (y_bc(C_MIN) - y_bc(C_MAX)) + BODY_L + 1.0, PAD_T + 2))
for sx in (-1, 1):
    pad = pad.cut(hex_z(NUT_AF, PAD_BOT - 0.1, NUT_DEPTH + 0.1, sx * NUT_X, NUT_Y))      # nut, from below
    pad = pad.cut(cyl(M3_CLEAR / 2, PAD_BOT - 0.1, PAD_T + 0.2, sx * NUT_X, NUT_Y))
pad = fuse(riser, pad)
pad = rotF(pad)

# --- spindle ---------------------------------------------------------------------------------
POST_R = POST_D / 2.0
spindle = fuse(ring(11.5, 10.2, 119, 2.0).common(box(-30, .3, 100, 60, 30, 25)),
               ring(11.5, 6, 120, 1.0),
               ring(POST_R, 6, 120.8, POST_TOP - 120.8))
spindle = spindle.cut(ring(POST_R + 0.1, GROOVE_D / 2, GROOVE_Z, GROOVE_W))
top_edges = [e for e in spindle.Edges if len(e.Vertexes) == 1 and e.Curve.TypeId == 'Part::GeomCircle'
             and abs(e.BoundBox.ZMin - POST_TOP) < 1e-6 and abs(e.Curve.Radius - POST_R) < 1e-6]
spindle = spindle.makeChamfer(0.5, top_edges)

neck = fuse(rear, arm, pad, spindle).cut(cyl(6, 103, 48))
addp('Neck_Main', neck, 'fixed', 'collar rear half + key, C arm, servo pad, spindle', 'FixedNeck')
addp('Neck_Clamp_Cap', front, 'fixed', 'collar front half', 'FixedNeck')

# --- the servo carriage ----------------------------------------------------------------------
CAR_HW, CAR_L = 12.5, 35.0
SLOT_W = M3_CLEAR
SLOT_L = SLOT_W + (C_MAX - C_MIN)
yb = y_bc(C_NOM)
car = box(-CAR_HW, yb - CAR_L / 2 - EXT, PAD_TOP, 2 * CAR_HW, CAR_L + EXT, CAR_T)
car = car.cut(box(-BODY_W / 2, yb - BODY_L / 2, PAD_TOP - 1, BODY_W, BODY_L, CAR_T + 2))
for sy in (-1, 1):
    car = car.cut(cyl(PILOT_M2 / 2, PAD_TOP - 0.1, CAR_T + 0.2, 0, yb + sy * EAR_PITCH / 2))
ys = yb + SLOT_OFF
for sx in (-1, 1):
    car = car.cut(slot_z(sx * NUT_X, ys - (SLOT_L - SLOT_W) / 2, ys + (SLOT_L - SLOT_W) / 2,
                         PAD_TOP - 0.1, CAR_T + 0.2, SLOT_W))
car_F = car.copy()                  # axis-aligned, for printing
car = rotF(car)
addp('Pan_Servo_Carriage', car, 'fixed', 'slides on the pad, M3 slots, ear pilots', 'FixedNeck')

# --- bearings, spacer, circlip (references) --------------------------------------------------
addp('Pan_Bearing_Lower', ring(BRG_OD / 2, BRG_ID / 2, BRG_LO_Z, BRG_W), 'fixed', '6804 20x32x7', 'Hardware')
addp('Pan_Bearing_Upper', ring(BRG_OD / 2, BRG_ID / 2, BRG_HI_Z, BRG_W), 'fixed', '6804 20x32x7', 'Hardware')
addp('Pan_Inner_Spacer', ring(12, BRG_ID / 2 + 0.1, BRG_LO_Z + BRG_W, BRG_HI_Z - BRG_LO_Z - BRG_W),
     'fixed', 'spacer between the inner races', 'Hardware')
# inner radius = the modelled groove root, so it touches the groove instead of cutting into it
addp('Pan_Circlip_Envelope', ring(12.4, GROOVE_D / 2.0, GROOVE_Z + 0.1, 1.2), 'fixed',
     '20 mm external circlip', 'Hardware')

# --- rotor and retainer ----------------------------------------------------------------------
SEAT_R = SEAT_D / 2.0
SCREW_ANGLES = (45, 135, 225, 315)
rotor = cyl(R_ROT, BRG_LO_Z, 23.0)
rotor = rotor.cut(cyl(SEAT_R, BRG_LO_Z - 0.1, BRG_W + 0.2))
rotor = rotor.cut(cyl(15.0, BRG_LO_Z + BRG_W, BRG_HI_Z - BRG_LO_Z - BRG_W))
rotor = rotor.cut(cyl(SEAT_R, BRG_HI_Z, BRG_W + 0.2))
retainer = ring(R_ROT, 14.5, RET_Z, RET_T)
for a in SCREW_ANGLES:
    x, y = R_SCREW * math.cos(math.radians(a)), R_SCREW * math.sin(math.radians(a))
    rotor = rotor.cut(cyl(PILOT_M2 / 2, BRG_HI_Z, 8, x, y))
    retainer = retainer.cut(cyl(M2_CLEAR / 2, RET_Z - 0.5, RET_T + 1, x, y))
addp('Pan_Rotor', rotor, 'pan', 'outer races only, 4 M2 pilots', 'Pan')
addp('Pan_Retainer', retainer, 'pan', 'bears on the outer race only', 'Pan')

# --- driven pedestal with the integral 40T ring ---------------------------------------------
ro40 = tip_r(N_DRIVEN)
teeth40 = cyl(ro40, ZC, CHANNEL).cut(cyl(6.5, ZC - 1, CHANNEL + 2))
teeth40 = teeth40.cut(grooves_for(N_DRIVEN, ro40, ZC, CHANNEL))
cone40, rim40 = flanges(ro40, ZC + CHANNEL, r_in=6.5)
ped = fuse(ring(R_ROT, 13, PED_Z, PED_BASE_T), ring(14, 6.5, 149, ZC - 149), teeth40, cone40, rim40,
           ring(11, 6.5, ZC + CHANNEL + CONE_H + RIM_T - 0.1, TOP_PLATE_Z - (ZC + CHANNEL + CONE_H + RIM_T) + 0.2),
           ring(R_ROT, 6.5, TOP_PLATE_Z, TOP_PLATE_T), box(-25, -30, TOP_PLATE_Z, 50, 30, TOP_PLATE_T))
ped = ped.cut(cyl(6.5, 146, 30)).cut(cyl(13, 146.9, 2.1))
for a in SCREW_ANGLES:
    x, y = R_SCREW * math.cos(math.radians(a)), R_SCREW * math.sin(math.radians(a))
    ped = ped.cut(cyl(M2_CLEAR / 2, PED_Z - 0.2, PED_BASE_T + 0.4, x, y))       # screw through the base plate
    ped = ped.cut(cyl(3.5, 150.0, TOP_PLATE_Z + TOP_PLATE_T - 150.0 + 1, x, y))  # driver access from above
for x, y in YOKE_BOLTS:
    ped = ped.cut(cyl(M3_CLEAR / 2, TOP_PLATE_Z - 0.1, TOP_PLATE_T + 0.2, x, y))
    ped = ped.cut(hex_z(NUT_AF, TOP_PLATE_Z - 0.1, NUT_DEPTH + 0.1, x, y))        # nut, from below
addp('Pan_Raised_Pedestal', ped, 'pan', 'integral 40T driven ring, yoke seat', 'Pan')

# --- the 60T drive pulley with its horn plate ------------------------------------------------
ro60 = tip_r(N_DRIVE)
R_FL = ro60 + FLANGE_OVER
r_in60 = ro60 - TOOTH_DEPTH - RIM_WALL
plate = cyl(R_FL, PLATE_RIM_Z, PLATE_T)
drum = cyl(ro60, ZC, CHANNEL).cut(cyl(r_in60, ZC - 1, CHANNEL + 2))
drum = drum.cut(grooves_for(N_DRIVE, ro60, ZC, CHANNEL))
cone60, rim60 = flanges(ro60, ZC + CHANNEL, r_in=r_in60)
dp = fuse(plate, drum, cone60, rim60)
# horn pocket from below, with a stepped first-layer relief at the mouth; boss recess; centre hole
dp = dp.cut(horn_solid(HORN_C + 0.35, PLATE_RIM_Z - 0.1, 0.5))
dp = dp.cut(horn_solid(HORN_C, PLATE_RIM_Z - 0.1, POCKET_DEPTH + 0.1))
dp = dp.cut(cyl(BOSS_D / 2 + HORN_C + 0.125, PLATE_RIM_Z + POCKET_DEPTH - 0.1, BOSS_RECESS + 0.1))
dp = dp.cut(cyl(CENTRE_HOLE / 2, PLATE_RIM_Z - 0.2, PLATE_T + 0.4))
drive_local = dp.copy()                         # at the origin; placed over the servo shaft below
dp.translate(SERVO_POS)
addp('Pan_Drive_Pulley', dp, 'servo', '60T, horn plate on the servo side', 'Pan')

# --- servo, horn, belt references -------------------------------------------------------------
def servo_shape():
    """SG90 in its own frame: body bottom at z 0, shaft on the z axis pointing up, the long end of
    the body toward -Y. Heights are Jim's calipers; the upper housing and boss are envelopes."""
    return fuse(box(-BODY_W / 2, -(BODY_L - SHAFT_NEAR), 0, BODY_W, BODY_L, EAR_UNDER),
                box(-BODY_W / 2, -(BODY_L - SHAFT_NEAR) - 4.9, EAR_UNDER, BODY_W, BODY_L + 9.8, EAR_T),
                box(-BODY_W / 2, -11.0, EAR_UNDER + EAR_T, BODY_W, 11.0 + SHAFT_NEAR, 6.0),
                cyl(5.5, EAR_UNDER + EAR_T, BOSS_TOP - EAR_UNDER - EAR_T),
                cyl(2.4, BOSS_TOP, SPLINE_TOP - BOSS_TOP))


def horn_shape(z_under):
    lower = HORN_G - LOWER_HUB_GAP
    h = fuse(horn_solid(0.0, z_under, ARM_T), cyl(BOSS_D / 2, z_under + ARM_T, BOSS_UP),
             cyl(BOSS_D / 2, z_under - lower, lower + 0.01))    # lower hub over the spline (diameter ASSUMED 7.1)
    return h.cut(cyl(2.5, z_under - HORN_G, HORN_G + ARM_T - 0.9))   # the spline socket, blind: about 2.0 over the spline


def horn_plate(z_rim, z_far, wall=2.0):
    """The horn pocket plate in the servo's own frame: pocket from z_rim, boss recess, a 1.2 roof
    with the 3.4 screw hole, then solid out to z_far with a r3.5 counterbore so the screw head
    still sits on the 1.2 roof."""
    p = horn_solid(HORN_C + wall, z_rim, z_far - z_rim)
    p = p.cut(horn_solid(HORN_C, z_rim - 0.1, POCKET_DEPTH + 0.1))
    p = p.cut(cyl(BOSS_D / 2 + HORN_C + 0.125, z_rim + POCKET_DEPTH - 0.1, BOSS_RECESS + 0.1))
    p = p.cut(cyl(CENTRE_HOLE / 2, z_rim - 0.2, z_far - z_rim + 0.4))
    roof_top = z_rim + POCKET_DEPTH + BOSS_RECESS + ROOF_T
    if z_far > roof_top + 0.05:
        p = p.cut(cyl(3.5, roof_top, z_far - roof_top + 0.2))
    return p


# The body is drawn with its long end (BODY_L - SHAFT_NEAR) toward -Y, the outer end.
# v0.3 drew it the other way round and rotated it 180; doing that here swung it into the arm.
sv = servo_shape()
sv.translate(A.Vector(0, -C_NOM, ZSB))
addp('SG90_Pan_Reference', rotF(sv), 'fixed', 'measured heights; shaft position +-0.6', 'Hardware')

horn = horn_shape(HORN_UNDER)
horn.translate(SERVO_POS)
addp('Pan_Horn_Reference', horn, 'servo', 'cross horn, arm thickness ASSUMED', 'Hardware')


# the belt: the 40T (driven, small) at the axis, the 60T (drive, big) C out along -Y in frame F
r_big, r_small = R_DRIVE_P, R_DRIVEN_P


def belt_for(C):
    g = math.asin((r_big - r_small) / C)
    # small pulley at origin, big pulley at (0,-C) in frame F
    def one(off):
        a, b = r_small + off, r_big + off
        pts = [A.Vector(a * math.cos(g), a * math.sin(g), 0), A.Vector(b * math.cos(g), -C + b * math.sin(g), 0),
               A.Vector(-b * math.cos(g), -C + b * math.sin(g), 0), A.Vector(-a * math.cos(g), a * math.sin(g), 0)]
        quad = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(A.Vector(0, 0, BELT_W))
        return fuse(cyl(a, 0, BELT_W), cyl(b, 0, BELT_W, 0, -C), quad)
    s = one(0.9).cut(one(-0.1))
    s.translate(A.Vector(0, 0, ZC + (CHANNEL - BELT_W) / 2.0))
    return s


addp('Pan_Belt_Reference', rotF(belt_for(C_NOM)), 'belt', '2GT 90T / 180 mm', 'Hardware')

# ================================================================== stage 2: the tilt side, from code
# Re-derived from the v0.1 / v0.2 generators (build_modular_head.py, build_screen_head_v02.py) at the
# v0.4 height, with the coupon-calibrated holes and nut pockets, the measured SG90 and cross horn, the
# real ST7789, and the same horn-plate drive as the pan pulley.
TZ = T.z
F0 = TOP_PLATE_Z + TOP_PLATE_T                   # yoke floor sits on the pedestal top plate
assert abs(F0 - (TZ - 37.0)) < 1e-6, (F0, TZ)
PIVOT_D = M3_CLEAR                               # 3.4 would not pass an M3 at all (fit coupon v2)


def cx(r, x, h, y, z): return Part.makeCylinder(r, h, A.Vector(x, y, z), A.Vector(1, 0, 0))


def hex_x(af, x, depth, y, z):
    """Hex prism along +X, flats top and bottom (so it bridges when the axis is horizontal)."""
    r = af / math.sqrt(3)
    pts = [A.Vector(x, y + r * math.cos(k * math.pi / 3), z + r * math.sin(k * math.pi / 3)) for k in range(6)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(A.Vector(depth, 0, 0))


REG_CHAMFER = 5.0                                # the GH44 register: tested, fits perfectly


def keyshape(w, h, y, depth):
    c = REG_CHAMFER
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2 - c), (w / 2 - c, h / 2), (-w / 2, h / 2)]
    vs = [A.Vector(x, y, TZ + v) for x, v in pts]
    return Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(A.Vector(0, depth, 0))


# --- the tilt servo: shaft on the tilt axis pointing -X, ears against the earplate at x -2.8 ---------
EARPLATE_X = -2.8
TS_X0 = EARPLATE_X + EAR_UNDER                   # body bottom, 14.7
M_TILT = A.Matrix(0, 0, -1, TS_X0,
                  1, 0, 0, T.y,
                  0, -1, 0, TZ,
                  0, 0, 0, 1)                    # servo frame (x, y, z) -> (TS_X0 - z, x - 26, TZ - y)


def to_tilt(s):
    r = s.copy()
    r.transformShape(M_TILT)
    return r


addp('SG90_Tilt_Reference', to_tilt(servo_shape()), 'pan', 'measured heights; long end up', 'Hardware')
addp('Tilt_Horn_Reference', to_tilt(horn_shape(BOSS_TOP + HORN_G)), 'tilt', 'cross horn, arm thickness ASSUMED',
     'Hardware')

# --- yoke --------------------------------------------------------------------------------------------
yoke = fuse(box(-27, -47, F0, 54, 7, 4), box(-27, -43, F0, 8, 31, 4), box(19, -43, F0, 8, 31, 4),
            box(-27, -30, F0, 54, 11, 4), box(-19, -43, F0, 19, 11, 4))
for x, y in YOKE_BOLTS:
    yoke = yoke.cut(cyl(M3_CLEAR / 2, F0 - 1, 6, x, y))
tower = fuse(box(28, -35, F0, 5, 18, 45), box(19, -35, F0, 14, 18, 4))
tower = tower.cut(cx(M3_CLEAR / 2, 27, 7, T.y, TZ))                          # pivot bolt
tower = tower.cut(hex_x(NUT_AF, 28 - 0.1, NUT_DEPTH + 0.1, T.y, TZ))          # its captive nut, inner face
earplate = box(EARPLATE_X, -36, F0, 3, 20, 60)
earplate = earplate.cut(box(EARPLATE_X - 0.7, T.y - BODY_W / 2, TZ - SHAFT_NEAR, 5, BODY_W, BODY_L))
for s_ in (-1, 1):
    earplate = earplate.cut(cx(PILOT_M2 / 2, EARPLATE_X - 1.2, 6, T.y, TZ - BODY_CTR + s_ * EAR_PITCH / 2))
yoke = fuse(yoke, tower, earplate)
addp('Tilt_Yoke', yoke, 'pan', 'servo window for the real shaft position, M2 ear pilots, M3 pivot + nut', 'Tilt')
addp('Tilt_Pivot_Bolt', fuse(cx(1.5, 22.0, 11.0, T.y, TZ), cx(2.75, 33.0, 3.0, T.y, TZ)), 'pan',
     'M3 x 10-12, head outside the tower, nut captive inside it', 'Hardware')

# --- GH44 receiver: the tested register, calibrated holes, 6.0 nut pockets, the horn plate drive ---------
rec = box(-22, -52, TZ - 22, 44, 4, 44)
# R3c (2026-10-03): a 1.6 deep recess printed facing the bed came out about 1 mm shallow (its roof is a bridge).
# So the register is cut clean THROUGH the 4.0 plate (to y -47.9); the carrier seats on the plate face and the
# backbone fused below is only a distant roof, 3.8 deep, far past the 1.4 key.
rec = rec.cut(keyshape(26.4, 22.4, -52.1, 4.2))
rec = rec.cut(keyshape(26.4 + 0.7, 22.4 + 0.7, -52.1, 0.5))      # first-layer relief: it prints face down
for x in (-16, 16):
    for dz in (-16, 16):
        rec = rec.cut(cy(M3_CLEAR / 2, -53, 7, x, TZ + dz)).cut(hex_y(NUT_AF, -50.6, 2.7, x, TZ + dz))
backbone = box(-27, -48.2, TZ - 6, 54, 4.2, 12)
left_arm = box(-24, -46, TZ - 6, 3, 25, 12)
right_arm = box(24, -46, TZ - 6, 3, 25, 12).cut(cx(PIVOT_D / 2, 23, 5, T.y, TZ))
rim_l = BOSS_TOP + HORN_G + ARM_T - POCKET_DEPTH                 # in the servo frame
far_l = TS_X0 - (-21.0) + 0.5                                     # reaches 0.5 into the left arm
tilt_plate = to_tilt(horn_plate(rim_l, far_l))
rec = fuse(rec, backbone, left_arm, right_arm, tilt_plate)
rec = rec.cut(box(-9, -53, TZ - 5, 18, 12, 10))                  # cable window
# Driver access to the horn screw. It must stop at the outer face of the 1.2 roof the screw head bears on:
# a fixed 7.0 cut removed that roof completely once the 16.5 horn height moved the plate outward
# (found by Codex, 2026-10-05). The assert below checks the bearing annulus is still solid.
ROOF_OUT_X = TS_X0 - (rim_l + POCKET_DEPTH + BOSS_RECESS + ROOF_T)
rec = rec.cut(cx(3.5, -25.5, ROOF_OUT_X - (-25.5), T.y, TZ))
# Recut the screw passage AFTER fusing the supporting arm. Its x=-21 face
# otherwise seals 0.1 mm of the hole after the horn-height correction.
rec = rec.cut(cx(CENTRE_HOLE / 2, -25.6, TS_X0 - rim_l + 25.7, T.y, TZ))
_shank = cx(CENTRE_HOLE / 2 - .01, -25.5, TS_X0 - rim_l + 25.5, T.y, TZ)
_shank_overlap = rec.common(_shank).Volume
assert _shank_overlap < 1e-6, 'tilt horn screw passage blocked after fusion'
report['checks']['tilt_screw_shank_overlap_mm3'] = _shank_overlap
_ann = cx(2.0, ROOF_OUT_X, ROOF_T, T.y, TZ).cut(cx(CENTRE_HOLE / 2, ROOF_OUT_X - 0.1, ROOF_T + 0.2, T.y, TZ))
_left = rec.common(_ann).Volume
print('tilt horn screw roof: %.3f of %.3f mm3 solid, outer face x %.2f' % (_left, _ann.Volume, ROOF_OUT_X))
assert abs(_left - _ann.Volume) < 1e-6, 'the driver cut ate the horn screw roof'
report['checks']['tilt_screw_bearing_annulus_mm3'] = _left
report['checks']['tilt_screw_bearing_annulus_expected_mm3'] = _ann.Volume
report['checks']['tilt_screw_roof_thickness_mm'] = ROOF_T
addp('GH44_Tilt_Receiver', rec, 'tilt', 'tested register; horn plate drive; M3 pivot hole', 'Tilt')

# --- GH44 dual carrier --------------------------------------------------------------------------------
car_base = box(-22, -55, TZ - 22, 44, 3, 44)
car_base = fuse(car_base, keyshape(26, 22, -52, 1.4)).cut(box(-9, -56, TZ - 5, 18, 8, 10))
dual = fuse(car_base, box(-42, -58, TZ - 21, 84, 3, 42))
for x in (-16, 16):
    for dz in (-16, 16):
        dual = dual.cut(cy(M3_CLEAR / 2, -60, 12, x, TZ + dz))
dual = dual.cut(box(-9, -59, TZ - 5, 18, 12, 10))
for x in (-32, 32):
    for dz in (-18, 18):
        dual = dual.cut(cy(M2_CLEAR / 2, -59, 9, x, TZ + dz))
# Removable sensor adapters: screw from the carrier rear into tested M2 pilots.
# Counterbores make the rear seating datum -55 even where the central plate is 6 mm thick.
TOF_ATTACH = [(-38.5, 7.0), (-24.0, -17.0), (6.5, 16.0)]
RAD_ATTACH = [(37.5, 8.0), (37.5, -8.0), (24.0, 17.5)]
for x, dz in TOF_ATTACH + RAD_ATTACH:
    dual = dual.cut(cy(M2_CLEAR/2, -58.1, 8.2, x, TZ+dz))
    dual = dual.cut(cy(2.25, -55, 4.5, x, TZ+dz))
addp('GH44_Dual_Carrier', dual, 'tilt', '84 mm sensor plate; tested male register; removable M2 sensor adapters', 'Tilt')

# PCB planes face -Y. Upright radar is 22 wide x30 high; holes 3.5 from each edge.
# ToF hole positions are derived from the official SEN0628 dimension drawing, not photo scale.
TOF_X, RAD_X = -15.0, 24.0
TOF_HOLES_ALL = [(-17.5,10.25), (17.5,10.25), (-17.5,-4.75), (17.5,-4.75), (-7.5,-10.25), (7.5,-10.25)]
TOF_HOLES = [TOF_HOLES_ALL[k] for k in (0,1,4,5)]
RAD_HOLES = [(x,z) for x in (-7.5,7.5) for z in (-11.5,11.5)]
TOF_SEAT, RAD_SEAT = -75.0, -73.0  # 14 / 12 mm from adapter's front plane -61
SENSOR_CHECKS = []

def stroke_y(p, q, r, y=-61, thickness=3):
    dx,dz = q[0]-p[0], q[1]-p[1]
    length = math.hypot(dx,dz)
    nx,nz = -dz*r/length, dx*r/length
    v = [A.Vector(x,y,TZ+z) for x,z in [(p[0]+nx,p[1]+nz),(q[0]+nx,q[1]+nz),
                                      (q[0]-nx,q[1]-nz),(p[0]-nx,p[1]-nz)]]
    body = Part.Face(Part.makePolygon(v+[v[0]])).extrude(A.Vector(0,thickness,0))
    return fuse(body,cy(r,y,thickness,p[0],TZ+p[1]),cy(r,y,thickness,q[0],TZ+q[1]))

def sensor_frame(name, center, holes, attach, seat):
    pts = [(center+x,z) for x,z in holes]
    # Connect the top row and each side, leaving the bottom open for leads.
    top = sorted([p for p in pts if p[1]>0])
    bottom = sorted([p for p in pts if p[1]<0])
    body = fuse(stroke_y(top[0],top[1],2), stroke_y(top[0],bottom[0],2), stroke_y(top[1],bottom[1],2))
    for x,z in pts:
        # A 3.25 radius seat stays inside the 3.5 mm hole-to-edge board land.
        # Wide captive-nut feet end at -64, behind the component keepout.
        body = fuse(body,cy(5,-64,6,x,TZ+z),cy(3.25,seat,-64-seat,x,TZ+z))
    for x,z in attach:
        near = min(pts,key=lambda p:(p[0]-x)**2+(p[1]-z)**2)
        body = fuse(body,stroke_y((x,z),near,2),cy(3.25,-61,3,x,TZ+z))
    for x,z in pts:
        body = body.cut(cy(M3_CLEAR/2,seat-.1,-58-seat+.2,x,TZ+z))
        body = body.cut(hex_y(NUT_AF,-63.6,NUT_DEPTH,x,TZ+z))
        body = body.cut(box(x-5.2,-63.7,TZ+z-3,5.2,2.8,6))
    for x,z in attach:
        body = body.cut(cy(PILOT_M2/2,-61.1,3.2,x,TZ+z))
    body = body.removeSplitter()
    addp(name,body,'tilt','four M3 x16 PCB screws, 6 AF side-loaded nuts; three rear M2 x6 adapter screws','Tilt')
    for x,z in pts:
        shank = cy(1.79,seat-.1,-58-seat+.2,x,TZ+z)
        annulus = cy(3.2,seat,.25,x,TZ+z).cut(cy(1.81,seat-.1,.45,x,TZ+z))
        probe = hex_y(5.95,-63.55,2.5,x,TZ+z)
        # Sweep the actual reduced nut through its insertion slot.
        route_overlap = 0.0
        for shift in (0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10):
            moved = probe.copy(); moved.translate(A.Vector(shift,0,0))
            route_overlap = max(route_overlap,body.common(moved).Volume)
        check = {'part':name,'hole_xz_mm':[x,z], 'shank_overlap_mm3':body.common(shank).Volume,
                 'seat_annulus_mm3':body.common(annulus).Volume,'seat_annulus_expected_mm3':annulus.Volume,
                 'nut_insertion_overlap_mm3':route_overlap,
                 'm3x16_tip_y_mm':seat-1.6+16,'minimum_carrier_tip_clearance_mm':-58-(seat-1.6+16)}
        SENSOR_CHECKS.append(check)
        assert check['shank_overlap_mm3']<1e-6, check
        assert abs(check['seat_annulus_mm3']-annulus.Volume)<1e-6, check
        assert route_overlap<1e-6, check
    for x,z in attach:
        assert body.common(cy(1.165,-61.1,3.2,x,TZ+z)).Volume<1e-6
        assert dual.common(cy(1.29,-58.1,7.6,x,TZ+z)).Volume<1e-6
    return body

tof_frame = sensor_frame('ToF_Sensor_Frame',TOF_X,TOF_HOLES,TOF_ATTACH,TOF_SEAT)
rad_frame = sensor_frame('Radar_Sensor_Frame',RAD_X,RAD_HOLES,RAD_ATTACH,RAD_SEAT)

def board_keepout(center,width,height,seat,holes,hole_d,back_height,front_height):
    # These are clearance reservations, not a component-accurate PCB model.
    # ToF uses the full rectangular bounding outline including ears, conservatively.
    pcb = box(center-width/2,seat-1.6,TZ-height/2,width,1.6,height)
    rear = box(center-width/2,seat,TZ-height/2,width,back_height,height)
    front = box(center-width/2,seat-1.6-front_height,TZ-height/2,width,front_height,height)
    for x,z in holes:
        pcb = pcb.cut(cy(hole_d/2,seat-1.7,1.8,center+x,TZ+z))
        # Mounting land must be free of components within radius 3.5 of the hole.
        rear = rear.cut(cy(3.5,seat-.1,back_height+.2,center+x,TZ+z))
        front = front.cut(cy(3.5,seat-1.7-front_height,front_height+.2,center+x,TZ+z))
    return fuse(pcb,rear,front)

tof_ref = board_keepout(TOF_X,42,27.5,TOF_SEAT,TOF_HOLES_ALL,3.1,9.9,9.9)
rad_ref = board_keepout(RAD_X,22,30,RAD_SEAT,RAD_HOLES,3.0,8.0,8.0)
addp('Dual_ToF_Envelope',tof_ref,'tilt','42 x27.5; 1.6 PCB and 11.5 whole stack per SEN0628 drawing; conservative 9.9 per-side clearance','Hardware')
addp('Dual_Radar_Envelope',rad_ref,'tilt','22 x30, corner holes diameter3, edge gap2, max rear component8 measured; 1.6 PCB/front8 assumed','Hardware')
report['sensor_mounts'] = {
    'coordinate_frame':'local: X right, Y rearward, Z up; sensor face -Y; z coordinates relative to tilt axis',
    'ToF':{'board_mm':[42,27.5], 'holes_drawing_xy_from_bottom_left_mm':[[3.5,24],[38.5,24],[3.5,9],[38.5,9],[13.5,3.5],[28.5,3.5]],
           'drawing_url':'https://dfimg.dfrobot.com/62d52567aa9508d63a4247a1/wikien/778eca8cf06dcba34c8748d079867f14_0x0.jpg.webp',
           'used_holes_relative_center_mm':TOF_HOLES,'center_x_mm':TOF_X,'rear_standoff_mm':14,
           'rear_component_reservation_mm':9.9,'rear_reservation_to_nut_foot_mm':1.1,'pcb_back_y_mm':TOF_SEAT},
    'radar':{'board_mm':[22,30],'hole_diameter_mm':3,'hole_edge_gap_mm':2,'derived_pitch_mm':[15,23],
             'used_holes_relative_center_mm':RAD_HOLES,'center_x_mm':RAD_X,'rear_standoff_mm':12,
             'rear_component_height_measured_mm':8,'rear_component_to_nut_foot_mm':1,'pcb_back_y_mm':RAD_SEAT},
    'pcb_mount_screws':'8 x M3 x16 with 8 M3 nuts; nominal length includes assumed 1.6 radar PCB; verify actual hardware',
    'adapter_screws':'6 x M2 x6 from carrier rear; head diameter <=4.5, head height <=2.6; pilots 2.35',
    'nut_pockets_mm':{'across_flats':6,'depth':2.6,'insertion':'from -X side; fit nuts before installing the adapters'},
    'checks':SENSOR_CHECKS,
    'limitations':['ToF rectangular envelope intentionally over-reserves the ear cutouts.',
                   'ToF optical center and radar antenna location not measured; FOV reservations use stated board bounds.',
                   'Radar PCB thickness 1.6 and front height8 assumed. Rear height8 is Jim measured.',
                   'Both PCBs require clear radius3.5 mounting lands. Actual connector exits and cable bends need assembly checks.']}
report['checks']['sensor_mounts_pass'] = True


# --- the rear display: the real ST7789 ------------------------------------------------------------------
# Board 62.5 x 29 x 3.2 (Jim). Visible area 51.2 x 25.6, 6.2 from the pin-hole edge and 1.5 from the
# top (Jim, 2026-10-01). Holes 58.25 x 26.00 centres, confirmed by the plate F gauge; their offset to
# the board edges is ASSUMED symmetric (it agrees with Jim's raw readings to about 0.3).
# The screen faces +Y (rear). The pin edge is at +X: the viewer's LEFT when standing behind the robot.
BOARD_L, BOARD_H, BOARD_T = 62.5, 29.0, 3.2
VIS_W, VIS_H, VIS_PIN, VIS_TOP = 51.2, 25.6, 6.2, 1.5
HOLE_DX, HOLE_DZ = 58.25, 26.00
LIP, WIN_MARGIN, POCKET_CLR = 3.0, 0.3, 0.3
vx_hi = BOARD_L / 2 - VIS_PIN
vx_lo = vx_hi - VIS_W
vz_hi = TZ + BOARD_H / 2 - VIS_TOP
vz_lo = vz_hi - VIS_H
board = box(-BOARD_L / 2, 0, TZ - BOARD_H / 2, BOARD_L, BOARD_T, BOARD_H)
fr = box(-37, -1.0, TZ - 22, 74, 1.0 + BOARD_T + LIP, 44)
fr = fr.cut(box(-BOARD_L / 2 - POCKET_CLR, -1.1, TZ - BOARD_H / 2 - POCKET_CLR,
                BOARD_L + 2 * POCKET_CLR, 1.1 + BOARD_T, BOARD_H + 2 * POCKET_CLR))   # pocket, open behind
fr = fr.cut(box(vx_lo - WIN_MARGIN, BOARD_T - 0.1, vz_lo - WIN_MARGIN,
                VIS_W + 2 * WIN_MARGIN, LIP + 0.2, VIS_H + 2 * WIN_MARGIN))           # window
for sx in (-1, 1):
    for sz in (-1, 1):
        fr = fr.cut(cy(PILOT_M2 / 2, BOARD_T - 0.1, 2.6 + 0.1, sx * HOLE_DX / 2, TZ + sz * HOLE_DZ / 2))
for side in (-1, 1):
    xr = 34.0 if side > 0 else -37.0
    for dz in (-20, 16):
        fr = fuse(fr, box(xr, -52, TZ + dz, 3, 52, 4))
    tx = 27.0 if side > 0 else -37.0
    for dz in (-21, 14):
        fr = fuse(fr, box(tx, -55, TZ + dz, 10, 3, 7))
for x in (-32, 32):
    for dz in (-18, 18):
        fr = fr.cut(cy(PILOT_M2 / 2, -56, 5, x, TZ + dz))
addp('Rear_Display_Frame', fr, 'tilt', 'real ST7789: window at 6.2 / 1.5, M2 pilots, open back for the header',
     'Tilt')
addp('ST7789_Board', board, 'tilt', '62.5 x 29 x 3.2, screen face +Y, pins at +X', 'Hardware')
report['display'] = {
    'board_mm': [BOARD_L, BOARD_H, BOARD_T], 'visible_mm': [VIS_W, VIS_H],
    'visible_from_pin_edge_mm': VIS_PIN, 'visible_from_top_mm': VIS_TOP,
    'hole_centres_mm': [HOLE_DX, HOLE_DZ], 'hole_offset_to_edges': 'ASSUMED symmetric',
    'pin_edge': '+X, the viewer\'s left from behind the robot', 'window_margin_per_side_mm': WIN_MARGIN,
    'lip_mm': LIP, 'board_screws': '4 x M2 x 4-5 from behind the board into the lip'}

for n in inherit_names:
    addp(n, inh[n]['shape'], 'tilt', 'sensor clearance envelope from v0.3', 'Hardware')

# ================================================================== the current robot, from the master
master = A.openDocument(str(MASTER))
ROBOT_NAMES = ['MastTube', 'MastBase', 'UpperDeck', 'S3Board', 'Breadboard', 'AntennaPost', 'ChassisDeck',
               'SideRailLeft', 'SideRailRight', 'PowerShield', 'BatteryBox',
               'DrvV5_Base_L', 'DrvV5_Wedge_L', 'DrvV5_Base_R', 'DrvV5_Wedge_R',
               'DrvV5_Board_L', 'DrvV5_Fins_L', 'DrvV5_Board_R', 'DrvV5_Fins_R']
robot, robot_world = [], {}
for n in ROBOT_NAMES:
    o = master.getObject(n)
    if o is None or o.Shape.isNull():
        continue
    w = o.Shape.copy()
    robot_world[n] = w
    s = w.copy()
    s.translate(A.Vector(-WORLD.x, -WORLD.y, -WORLD.z))
    robot.append((n, s))
report['checks']['master_mast_top_z'] = master.getObject('Parameters').get('mast_top_z')
report['checks']['robot_solids_compared'] = [n for n, _ in robot]
report['checks']['robot_solids_missing'] = [n for n in ROBOT_NAMES if n not in robot_world]
A.closeDocument(master.Name)

# ================================================================== collision sweeps
TILTS = tuple(float(t) for t in range(-25, 26, 5))
PAN_SAMPLES = [float(a) for a in range(int(HEAD_TRAVEL[0]), int(HEAD_TRAVEL[1]) + 1, 5)]
SERVO_SIDE = ('SG90_Pan_Reference', 'Pan_Servo_Carriage', 'Pan_Drive_Pulley', 'Pan_Horn_Reference',
              'Pan_Belt_Reference')


def posed(p, pan=0.0, tilt=0.0, C=None):
    # A sliding servo changes both pulley spacing and the belt path. This is
    # a taut-path envelope; slack/sag and installation need physical checks.
    s = rotF(belt_for(C)) if C is not None and p.get('name') == 'Pan_Belt_Reference' else p['shape'].copy()
    if C is not None and p.get('name') in SERVO_SIDE and p['name'] != 'Pan_Belt_Reference':
        u = A.Vector(math.cos(math.radians(SERVO_ANG)), math.sin(math.radians(SERVO_ANG)), 0)
        s.translate(u * (C - C_NOM))
    m = p['motion']
    if m == 'tilt':
        s.rotate(T, A.Vector(1, 0, 0), tilt)
    if m in ('pan', 'tilt'):
        s.rotate(A.Vector(), A.Vector(0, 0, 1), pan)
    if m == 'servo':
        centre = SERVO_POS if C is None else SERVO_POS + A.Vector(math.cos(math.radians(SERVO_ANG)),
                                                                   math.sin(math.radians(SERVO_ANG)), 0) * (C - C_NOM)
        s.rotate(centre, A.Vector(0, 0, 1), pan / RATIO)
    return s


def overlap(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    return a.common(b).Volume


plist = []
for n, p in parts.items():
    q = dict(p)
    q['name'] = n
    plist.append(q)
byname = {p['name']: p for p in plist}

# by design: the printed post is modelled a touch over the 20.00 bore, so it will "overlap" the bearings
INTENDED = {frozenset(['Pan_Bearing_Lower', 'Neck_Main']), frozenset(['Pan_Bearing_Upper', 'Neck_Main'])}
INTENDED_NOTE = 'bearing bore 20.00 against the modelled post %.2f: a press fit by design, set by H3b' % POST_D


def note(a, b, pan, tilt, kind, v, C=None):
    report['collisions'].append({'a': a, 'b': b, 'pan': pan, 'tilt': tilt, 'kind': kind, 'mm3': round(v, 3),
                                 'carriage': C})


tests = 0
for a, b in itertools.combinations(plist, 2):
    if frozenset([a['name'], b['name']]) in INTENDED:
        continue
    ma, mb = a['motion'], b['motion']
    if ma == mb:
        poses = [(0.0, 0.0)]
    elif ma in ('pan', 'tilt') and mb in ('pan', 'tilt'):
        poses = [(0.0, t) for t in TILTS]
    else:
        tilt_involved = 'tilt' in (ma, mb)
        poses = [(pn, t) for pn in PAN_SAMPLES for t in (TILTS if tilt_involved else (0.0,))]
    for pan, tilt in poses:
        v = overlap(posed(a, pan, tilt), posed(b, pan, tilt))
        tests += 1
        if v > 0.05:
            note(a['name'], b['name'], pan, tilt, 'head', v)
report['checks']['head_pair_pose_tests'] = tests

tests = 0
for p in plist:
    # Test each distinct pose. Fixed parts ignore both axes; pan-only parts
    # ignore tilt. This preserves coverage without repeating the same Boolean.
    pans = PAN_SAMPLES if p['motion'] in ('pan', 'tilt', 'servo') else (0.0,)
    tilts = TILTS if p['motion'] == 'tilt' else (0.0,)
    for pan in pans:
        for tilt in tilts:
            s = posed(p, pan, tilt)
            for n, r in robot:
                tests += 1
                v = overlap(s, r)
                if v > 0.05:
                    note(p['name'], n, pan, tilt, 'robot', v)
report['checks']['robot_pair_pose_tests'] = tests

# the carriage at both ends of its travel, against everything that is near it
tests = 0
for C in (C_MIN, C_MAX):
    for pan in range(-20, 181, 20):
        for tilt in (-25.0, 0.0, 25.0):
            for a in [byname[n] for n in SERVO_SIDE]:
                sa = posed(a, float(pan), tilt, C)
                for b in plist:
                    if b['name'] in SERVO_SIDE:
                        continue
                    tests += 1
                    v = overlap(sa, posed(b, float(pan), tilt))
                    if v > 0.05:
                        note(a['name'], b['name'], float(pan), tilt, 'carriage-end', v, C)
                for n, r in robot:
                    tests += 1
                    v = overlap(sa, r)
                    if v > 0.05:
                        note(a['name'], n, float(pan), tilt, 'carriage-end-robot', v, C)
report['checks']['carriage_end_pose_tests'] = tests

# ================================================================== clearances, service paths, FOV
clear = {}
def dist(a, b, **kw):
    return round(posed(byname[a], **kw).distToShape(posed(byname[b], **kw))[0], 3)

clear['drive_pulley_to_pedestal_mm'] = min(dist('Pan_Drive_Pulley', 'Pan_Raised_Pedestal', pan=p)
                                           for p in (0.0, 45.0, 90.0, 135.0, 180.0))
clear['drive_pulley_to_yoke_mm'] = min(dist('Pan_Drive_Pulley', 'Tilt_Yoke', pan=p)
                                       for p in (0.0, 45.0, 90.0, 135.0, 180.0))
clear['drive_pulley_to_retainer_mm'] = dist('Pan_Drive_Pulley', 'Pan_Retainer')
clear['drive_pulley_to_servo_body_mm'] = dist('Pan_Drive_Pulley', 'SG90_Pan_Reference')
clear['servo_body_to_neck_mm'] = dist('SG90_Pan_Reference', 'Neck_Main')
clear['neck_arm_to_rotor_mm'] = dist('Neck_Main', 'Pan_Rotor')
clear['spline_to_pulley_roof_mm'] = round(
    (PLATE_RIM_Z + POCKET_DEPTH + BOSS_RECESS) - (ZSB + SPLINE_TOP), 3)
clear['horn_to_servo_boss_mm'] = HORN_G
report['clearances'] = clear

# service path 1: the four retainer screws, driver from above. A cylinder of r3.5 over each head.
def screw_cyl(a):
    x, y = R_SCREW * math.cos(math.radians(a)), R_SCREW * math.sin(math.radians(a))
    return cyl(3.5, PED_Z + PED_BASE_T, 40.0, x, y)

access = {}
ok_pans = []
for pan in [float(v) for v in range(-20, 181, 5)]:
    blocked = []
    for a in SCREW_ANGLES:
        c = screw_cyl(a)
        c.rotate(A.Vector(), A.Vector(0, 0, 1), pan)
        for p in plist:
            if p['name'] in ('Pan_Rotor', 'Pan_Retainer', 'Pan_Raised_Pedestal', 'Pan_Bearing_Lower',
                             'Pan_Bearing_Upper', 'Pan_Inner_Spacer', 'Pan_Circlip_Envelope', 'Neck_Main',
                             'Neck_Clamp_Cap', 'SG90_Pan_Reference', 'Pan_Servo_Carriage'):
                continue
            if 'Belt' in p['name'] or 'Horn' in p['name']:
                continue
            if overlap(c, posed(p, pan, 0.0)) > 1.0:
                blocked.append((a, p['name']))
    access[pan] = blocked
    if not blocked:
        ok_pans.append(pan)
report['service_paths'] = {
    'retainer_screws_from_above': {
        'pan_angles_with_all_four_open': ok_pans,
        'blocked_by_at_pan0': access.get(0.0),
        'note': 'a vertical driver cylinder r3.5 over each screw head, against the moving parts'}}

# service paths 3 and 4: a driver straight down onto (3) the belt-tension clamp screws and (4) the
# horn screw. Both are made with the pulley FITTED. The carriage screws moved outboard for this.
BELOW = ('Neck_Main', 'Neck_Clamp_Cap', 'Pan_Servo_Carriage', 'SG90_Pan_Reference', 'Pan_Bearing_Lower',
         'Pan_Bearing_Upper', 'Pan_Inner_Spacer', 'Pan_Circlip_Envelope', 'Pan_Rotor', 'Pan_Retainer')


def open_from_above(cylinders, ignore, pans, C=None):
    bad = {}
    for pan in pans:
        for lbl, c in cylinders:
            for p in plist:
                if p['name'] in ignore or 'Belt' in p['name']:
                    continue
                if overlap(c, posed(p, pan, 0.0, C)) > 1.0:
                    bad.setdefault(pan, []).append((lbl, p['name']))
    return bad


clamp_cyls = []
for sx in (-1, 1):
    c = rotF(cyl(4.0, ZP, 60.0, sx * NUT_X, NUT_Y))
    clamp_cyls.append(('clamp_x%+.1f' % (sx * NUT_X), c))
pans30 = [float(v) for v in range(-20, 181, 10)]
clamp_bad = open_from_above(clamp_cyls, BELOW, pans30)
clamp_bad_end = {}
for Cx in (C_MIN, C_MAX):
    # the carriage moves; the screw (in the pad) does not, so the cylinders stay put
    clamp_bad_end[Cx] = open_from_above(clamp_cyls, BELOW + ('Pan_Servo_Carriage',), pans30, Cx)
horn_cyl = [('horn_screw', cyl(3.5, ZC + 1.0, 60.0, SERVO_POS.x, SERVO_POS.y))]
horn_bad = open_from_above(horn_cyl, BELOW + ('Pan_Drive_Pulley', 'Pan_Horn_Reference'), pans30)
report['service_paths']['clamp_screws_from_above_pulley_fitted'] = {
    'blocked_at_pans': {str(k): v for k, v in clamp_bad.items()},
    'blocked_at_carriage_ends': {str(k): {str(p): x for p, x in v.items()} for k, v in clamp_bad_end.items()},
    'note': 'driver cylinder r4.0 over each M3 clamp screw'}
report['service_paths']['horn_screw_from_above'] = {
    'blocked_at_pans': {str(k): v for k, v in horn_bad.items()},
    'open_pans': [p for p in pans30 if p not in horn_bad],
    'note': 'driver cylinder r3.5 down the pulley axis, from above the pulley roof'}

# service paths 5-7, the tilt side.
# 5: the tilt horn screw, driver along the tilt axis from the left, through the receiver's access hole
tilt_cyl = cx(3.4, -90.0, (ROOF_OUT_X - 0.05) + 90.0, T.y, TZ)   # stops at the roof the screw head bears on
tilt_bad = {}
for tilt in TILTS:
    for p in plist:
        if p['name'] == 'Tilt_Horn_Reference':
            continue
        if overlap(tilt_cyl, posed(p, 0.0, tilt)) > 1.0:
            tilt_bad.setdefault(tilt, []).append(p['name'])
# 6: the two yoke-to-pedestal M3 bolts, driver from above
yb_bad = {}
for tilt in TILTS:
    for (x, y) in YOKE_BOLTS:
        c = cyl(3.5, F0 + 4.0, 80.0, x, y)
        for p in plist:
            if p['name'] in ('Tilt_Yoke', 'Pan_Raised_Pedestal'):
                continue
            if overlap(c, posed(p, 0.0, tilt)) > 1.0:
                yb_bad.setdefault(tilt, []).append(('x%+.0f' % x, p['name']))
# 7: the four GH44 carrier M3 screws, driver from the front
gh_bad = []
for x in (-16, 16):
    for dz in (-16, 16):
        c = cy(3.5, -140.0, 140.0 - 58.2, x, TZ + dz)
        for p in plist:
            if p['name'] in ('GH44_Dual_Carrier', 'GH44_Tilt_Receiver'):
                continue
            if overlap(c, p['shape']) > 1.0:
                gh_bad.append(('x%+d z%+d' % (x, dz), p['name']))
report['service_paths']['tilt_horn_screw_along_axis'] = {
    'blocked_at_tilts': {str(k): v for k, v in tilt_bad.items()},
    'note': 'driver r3.4 along the tilt axis from the left, through the receiver access hole'}
report['service_paths']['yoke_bolts_from_above'] = {
    'blocked_at_tilts': {str(k): v for k, v in yb_bad.items()},
    'note': 'blocked means: bolt the yoke to the pedestal BEFORE fitting the receiver'}
report['service_paths']['gh44_carrier_screws_from_front'] = {
    'blocked_by': gh_bad, 'note': 'blocked by a sensor means: screw the carrier on before the sensors'}

# service path 2: the cable bore, 11.9 mm, all the way up
cab = cyl(5.95, 105, 66)
report['checks']['cable_passage_11_9mm_overlap_mm3'] = round(sum(
    overlap(cab, p['shape']) for p in plist
    if p['name'] in ('Neck_Main', 'Neck_Clamp_Cap', 'Pan_Rotor', 'Pan_Retainer', 'Pan_Raised_Pedestal',
                     'Pan_Bearing_Lower', 'Pan_Bearing_Upper', 'Pan_Inner_Spacer', 'Pan_Circlip_Envelope')), 4)

# nominal 60 x 60 degree ToF frustum, swept across the whole pan range, against the CURRENT robot
def square(y, half, cx):
    vs = [A.Vector(cx + x, y, T.z + v) for x, v in [(-half, -half), (half, -half), (half, half), (-half, half)]]
    return Part.makePolygon(vs + [vs[0]])


def rect_wire(y,cx,hw,hh):
    vs = [A.Vector(cx+x,y,TZ+z) for x,z in [(-hw,-hh),(hw,-hh),(hw,hh),(-hw,hh)]]
    return Part.makePolygon(vs+[vs[0]])
TOF_FRONT_Y = TOF_SEAT-1.6-9.9
frustum = Part.makeLoft([rect_wire(TOF_FRONT_Y,TOF_X,21,13.75),
                        rect_wire(TOF_FRONT_Y-150,TOF_X,21+150*math.tan(math.radians(30)),
                                  13.75+150*math.tan(math.radians(30)))],True)
report['tof_fov_reservation'] = {'full_angle_degrees':[60,60],'near_plane_mm':[42,27.5],
                                  'length_mm':150,'front_y_mm':TOF_FRONT_Y,
                                  'note':'conservative whole-board origin envelope; exact optical center unmeasured'}
report['fov_intersections'] = []
for pan in PAN_SAMPLES:
    for tilt in TILTS:
        f = frustum.copy()
        f.rotate(T, A.Vector(1, 0, 0), tilt)
        f.rotate(A.Vector(), A.Vector(0, 0, 1), pan)
        for n, s in robot:
            v = overlap(f, s)
            if v > .05:
                report['fov_intersections'].append({'pan': pan, 'tilt': tilt, 'object': n, 'mm3': round(v, 2)})
        for p in plist:
            if p['name'] == 'Dual_ToF_Envelope':
                continue
            v = overlap(f, posed(p, pan, tilt))
            if v > .05:
                report['fov_intersections'].append({'pan': pan, 'tilt': tilt, 'object': p['name'], 'mm3': round(v, 2)})

report['checks']['all_parts_single_valid_solid'] = all(p['shape'].isValid() and len(p['shape'].Solids) == 1
                                                       for p in plist)
report['checks']['belt_path_at_carriage_ends'] = {
    str(c): {'pitch_path_length_mm': belt_len(c, R_DRIVE_P, R_DRIVEN_P),
             'available_belt_length_mm': BELT_TEETH * PITCH,
             'note': 'Taut envelope only; set tension on the actual belt, not at a prescribed stop.'}
    for c in (C_MIN, C_NOM, C_MAX)}
report['drive'] = {
    'teeth_drive_on_servo': N_DRIVE, 'teeth_driven_on_head': N_DRIVEN,
    'ratio_head_per_servo_deg': RATIO, 'head_travel_deg': list(HEAD_TRAVEL),
    'servo_travel_needed_deg': round(SERVO_TRAVEL, 1), 'servo_sweep_measured_deg': 160,
    'belt': '2GT 90T / 180 mm', 'groove': '2-notch, r0.65, depth 0.75 (passed on Jim\'s belt)',
    'theory_centre_distance_mm': round(C_THEORY, 3), 'carriage_travel_mm': [C_MIN, C_MAX],
    'nominal_mm': C_NOM, 'evidence_nominal': 'tightest about mid-slot on H1 (eyeball)',
    'tip_dia_60T_mm': round(2 * ro60, 3), 'tip_dia_40T_mm': round(2 * ro40, 3),
    'flange_dia_60T_mm': round(2 * R_FL, 3), 'belt_channel_bottom_Z': ZC,
}
report['stack_Z'] = {'plate_rim': PLATE_RIM_Z, 'plate_top_belt_channel_bottom': ZC, 'arm_top': ARM_TOP,
                     'horn_underside': HORN_UNDER, 'servo_ear_plane': ZP, 'servo_body_bottom': ZSB,
                     'pad': [PAD_BOT, PAD_TOP], 'pedestal_top_plate': [TOP_PLATE_Z, TOP_PLATE_Z + TOP_PLATE_T],
                     'tilt_axis_local': T.z, 'tilt_axis_real': T.z + LIFT, 'mast_top_real': 120 + LIFT,
                     'inherited_tilt_lift': TILT_SHIFT}

# ================================================================== the FreeCAD document
doc = A.newDocument('GladiatorHeadV05')
doc.Label = 'Gladiator head v0.5 - measured removable sensor mounts, 2026-10-05'
groups = {}
def grp(name):
    if name not in groups:
        groups[name] = doc.addObject('App::DocumentObjectGroup', name)
    return groups[name]

def to_world(s):
    w = s.copy()
    w.translate(WORLD)
    return w

for p in plist:
    o = doc.addObject('Part::Feature', p['name'])
    o.Shape = to_world(p['shape'])
    for k, v in (('MotionGroup', p['motion']), ('DesignStatus', p['note'])):
        o.addProperty('App::PropertyString', k).__setattr__(k, v)
    grp(p['group']).addObject(o)
ctx = grp('Robot_Context_from_master')
for n, w in robot_world.items():
    o = doc.addObject('Part::Feature', 'Ctx_' + n)
    o.Shape = w
    ctx.addObject(o)
for n in variant_names:
    o = doc.addObject('Part::Feature', n)
    o.Shape = to_world(inh[n]['shape'])
    o.addProperty('App::PropertyString', 'DesignStatus').DesignStatus = 'INHERITED v0.3 carrier variant, reference only'
    grp('CarrierVariants_inherited').addObject(o)
doc.recompute()
doc.saveAs(str(OUT / 'Gladiator_Head_v05_PanStack.FCStd'))
Part.export([doc.getObject(p['name']) for p in plist], str(OUT / 'Gladiator_Head_v05_PanStack.step'))

# ================================================================== STL export, in print orientation
LIN, ANG = 0.01, 0.0872665


def bed_chamfer(shape, size=BED_RELIEF):
    z0 = shape.BoundBox.ZMin
    edges = []
    for e in shape.Edges:
        if len(e.Vertexes) != 1:
            continue
        try:
            if e.Curve.TypeId != 'Part::GeomCircle':
                continue
        except Exception:
            continue
        bb = e.BoundBox
        if abs(bb.ZMin - z0) > 1e-6 or abs(bb.ZMax - z0) > 1e-6:
            continue
        edges.append(e)
    if not edges:
        return shape, 0
    try:
        out = shape.makeChamfer(size, edges)
        if out.isValid() and len(out.Solids) == 1:
            return out, len(edges)
    except Exception:
        pass
    out, n = shape, 0
    for e in edges:
        try:
            cand = out.makeChamfer(size, [e])
            if cand.isValid() and len(cand.Solids) == 1:
                out, n = cand, n + 1
        except Exception:
            pass
    return out, n


def bed_area(shape):
    z0 = shape.BoundBox.ZMin
    return sum(f.Area for f in shape.Faces if abs(f.BoundBox.ZMin - z0) < 1e-6 and abs(f.BoundBox.ZMax - z0) < 1e-6)


# name -> (shape to print, note, gate, probes in LOCAL coordinates: ((x,y,z), inside?))
rp = R_ROT - 0.7
exports = {
    'Neck_Main': (neck, 'mast axis vertical, collar on the bed; the C arm, riser and pad need support',
                  'released: horn top 16.5 above the ear underside (Jim, 10-05) sets the pad height; circlip seats on the 2-notch post',
                  [((0, 12.5, 110), True), ((0, 0, 110), False), ((0, 9.3, 112), True)]),
    'Neck_Clamp_Cap': (front, 'as modelled, axis vertical, lugs on the bed; no support', 'none - tested geometry',
                       [((0, -12, 110), True), ((0, -8, 110), False)]),
    'Pan_Servo_Carriage': (car_F, 'flat, long axis along the bed X; no support',
                           'released: H4b settled the ear pilots (2.35)', []),
    'Pan_Rotor': (rotor, 'axis vertical, LOWER bearing seat on the bed (relieved); no support',
                  'released: H4b settled the M2 pilots (2.35)',
                  [((SEAT_R - 0.5, 0, BRG_LO_Z + 3), False), ((R_ROT - 0.5, 0, BRG_LO_Z + 3), True)]),
    'Pan_Retainer': (retainer, 'flat; no support', 'none - clearance holes only',
                     [((16, 0, RET_Z + 1), True), ((14, 0, RET_Z + 1), False)]),
    'Pan_Raised_Pedestal': (ped, 'axis vertical, base plate on the bed; support ONLY under the top plate, '
                                 'and block support from the belt channel',
                            'none for the geometry; the belt line is set by this part',
                            [((rp, 0, PED_Z + 1), True), ((0, 0, PED_Z + 1), False),
                             ((rp, 0, TOP_PLATE_Z + 1), True)]),
    'Pan_Drive_Pulley': (drive_local, 'axis vertical, horn plate on the bed (pocket faces the bed, relieved); '
                                      'no support',
                         'released: H6a snug pocket (0.15) won',
                         [((10, 0, PLATE_RIM_Z + 0.6), False), ((10, 0, ZC - 0.5), True),
                          ((0, 0, ZC - 0.5), False)]),
    'Tilt_Yoke': (parts['Tilt_Yoke']['shape'], 'floor on the bed; no support (the servo window and the '
                                               'pivot hole bridge)',
                  'released: H4b settled the ear pilots (2.35)',
                  [((-1.3, T.y, TZ + 5), False), ((30.5, -30, TZ - 10), True), ((30.5, T.y, TZ), False)]),
    'GH44_Tilt_Receiver': (parts['GH44_Tilt_Receiver']['shape'],
                           'GH44 face DOWN (through register opening on the bed, relieved), arms up; no support',
                           'released: H6a snug pocket (0.15) won',
                           [((10, -51.5, TZ + 8), False), ((18, -50, TZ), True), ((25.5, T.y, TZ), False),
                            ((25.5, -40, TZ), True)]),
    'GH44_Dual_Carrier': (parts['GH44_Dual_Carrier']['shape'], 'sensor plate down, register key up; no support',
                          'prototype: tested GH44 interface; measured board patterns; verify connector routing and screws at assembly',
                          [((10, -51.0, TZ + 8), True), ((18, -53.5, TZ), True), ((0, -53.5, TZ), False)]),
    'Rear_Display_Frame': (parts['Rear_Display_Frame']['shape'],
                           'bezel face down; support under the four mounting tabs only',
                           'released: H4b settled the pilots (2.35); the hole-to-edge offset is still assumed symmetric',
                           [((0, 4.5, TZ), False), ((33, 4.5, TZ), True), ((0, 1.5, TZ), False)]),
}
for name, shape, holes, center, seat in [('ToF_Sensor_Frame',tof_frame,TOF_HOLES,TOF_X,TOF_SEAT),
                                          ('Radar_Sensor_Frame',rad_frame,RAD_HOLES,RAD_X,RAD_SEAT)]:
    x,z = holes[0]; x += center
    exports[name] = (shape,'carrier mating face DOWN, posts UP; no support; short 6 mm nut-slot bridges',
                     'prototype: tested nut and pilot fits; measured PCB pattern',
                     [((x+2.6,seat+.2,TZ+z),True),((x,seat+.2,TZ+z),False)])
# print orientation: a rotation applied before dropping each part onto the bed
X_AXIS = A.Vector(1, 0, 0)
HOLD = set()  # prototype manufacturing candidates; physical assembly verification remains
ROT = {'GH44_Tilt_Receiver': (X_AXIS, 90.0),      # the face (y = -52) goes down
       'GH44_Dual_Carrier': (X_AXIS, 90.0),       # the sensor plate (y = -58) goes down
       'Rear_Display_Frame': (X_AXIS, -90.0),
       'ToF_Sensor_Frame': (X_AXIS,-90.0), 'Radar_Sensor_Frame': (X_AXIS,-90.0)}     # the bezel face (y = +6.2) goes down
OFF = {}
exp_report = []
for name, (shape, how, gate, probes) in exports.items():
    s = shape.copy()
    if name in ROT:
        ax_, ang_ = ROT[name]
        s.rotate(A.Vector(), ax_, ang_)
        R_ = A.Rotation(ax_, ang_)
        probes = [(tuple(R_.multVec(A.Vector(*pt))), ins) for pt, ins in probes]
    b0 = s.BoundBox
    dz = -b0.ZMin
    dx, dy = -b0.XMin, -b0.YMin
    s.translate(A.Vector(dx, dy, dz))
    pr = [((x + dx, y + dy, z + dz), ins) for (x, y, z), ins in probes]
    # the probes are given for parts centred on the mast axis; the carriage and pad are not, so skip those
    s, nch = bed_chamfer(s)
    assert s.isValid() and len(s.Solids) == 1, name + ' after chamfer'
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=LIN, AngularDeflection=ANG, Relative=False)
    path = OUT / 'stl' / ('Gladiator_Head_v05_%s.stl' % name)
    m.write(str(path))
    back = Mesh.Mesh(str(path))
    bb = s.BoundBox
    probe_ok = all(s.isInside(A.Vector(*pt), 1e-6, True) == ins for pt, ins in pr)
    rec = {'part': name, 'file': path.name, 'print_orientation': how, 'gate': gate,
           'size_mm': [round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
           'volume_cm3': round(s.Volume / 1000, 2), 'grams_pla': round(s.Volume * 0.00124, 1),
           'bed_contact_mm2': round(bed_area(s)), 'bed_relief_edges': nch,
           'on_z0': abs(bb.ZMin) < 1e-9, 'probes_pass': probe_ok, 'n_probes': len(pr),
           'mesh_solid': back.isSolid(), 'mesh_non_manifold': back.hasNonManifolds(),
           'mesh_volume_error_pct': round(100 * abs(back.Volume - s.Volume) / s.Volume, 3),
           'released': name not in HOLD}
    exp_report.append(rec)
report['stl'] = exp_report

# ================================================================== write it out
report['limitations'] = [
    'Sensor mounts use measured radar dimensions and published ToF hole positions. Complete harness, '
    'strain relief and motion stops remain unfinished. Confirm connector orientation and wire bends in assembly.',
    'The display holes are 58.25 x 26.00 (confirmed), but their offset to the board edges is ASSUMED '
    'symmetric. The pin edge is put at +X (the viewer\'s left from behind the robot); firmware can rotate '
    'the picture.',
    'The tilt pivot is an M3 bolt running in a 3.6 hole in PLA: fine for a prototype, it will wear.',
    'Settled by the final coupon plate (Jim, 2026-10-01): POST_D %.2f (H3b), PILOT_M2 %.2f (H4b), '
    'HORN_C %.2f (H6). Circlip seating confirmed by Jim, 2026-10-03.' % (POST_D, PILOT_M2, HORN_C),
    'The installed horn hub top is measured at 16.5 above the ear underside. Arm thickness %.1f, '
    'approximately 1 mm hub rise and lower hub geometry remain partly assumed; derived gap %.2f. '
    'Verify the complete screw and belt fit at first assembly.' % (ARM_T, HORN_G),
    'Servo shaft position along the body is +-0.6. The carriage slot covers it.',
    'Sampled rigid-solid checks every 5 degrees of pan and tilt. They do not prove clearance between samples, nor '
    'cable behaviour, belt tooth mesh, stiffness, creep, or that the belt can be fitted.',
    'The belt can be fitted with the carriage at its slack end, but that is argued, not tested.',
    'No load, torque or payload rating is claimed.']
report['checks']['master_unchanged'] = all(digest(p) == h for p, h in before.items())
report['checks']['sampled_geometry_pass'] = (
    not [c for c in report['collisions']] and not report['fov_intersections']
    and report['checks']['all_parts_single_valid_solid']
    and report['checks']['cable_passage_11_9mm_overlap_mm3'] < .01
    and report['checks']['master_unchanged']
    and not report['checks']['robot_solids_missing']
    and not tilt_bad
    and report['checks']['sensor_mounts_pass']
    and all(r['on_z0'] and r['probes_pass'] and r['mesh_solid']
            and not r['mesh_non_manifold'] and r['mesh_volume_error_pct'] < .1 for r in exp_report))
(OUT / 'validation.json').write_text(json.dumps(report, indent=2, default=str) + '\n')
(OUT / 'head-config.json').write_text(json.dumps({
    'drive': report['drive'], 'stack_Z': report['stack_Z'], 'pending': report['pending'],
    'assumed': report['assumed'], 'settled': report['settled'], 'release': report['release']}, indent=2) + '\n')

NL = chr(10)
lines = ['stack: ZC %.2f  plate rim %.2f  ARM_TOP %.2f  horn under %.2f  ZP %.2f  servo bottom %.2f  pad %.2f..%.2f  tilt axis %.1f'
         % (ZC, PLATE_RIM_Z, ARM_TOP, HORN_UNDER, ZP, ZSB, PAD_BOT, PAD_TOP, T.z),
         'theory C %.3f  nominal %.2f  carriage %.1f..%.1f' % (C_THEORY, C_NOM, C_MIN, C_MAX), '']
for n, p in parts.items():
    b = p['shape'].BoundBox
    lines.append('%-26s %-6s vol %9.1f  z %6.1f..%6.1f' % (n, p['motion'], p['shape'].Volume, b.ZMin, b.ZMax))
lines += ['', 'tests: head %d  robot %d  carriage-end %d' % (
    report['checks']['head_pair_pose_tests'], report['checks']['robot_pair_pose_tests'],
    report['checks']['carriage_end_pose_tests']),
    'collisions: %d   fov: %d   cable overlap %.4f   master unchanged %s' % (
        len(report['collisions']), len(report['fov_intersections']),
        report['checks']['cable_passage_11_9mm_overlap_mm3'], report['checks']['master_unchanged']),
    'clearances: ' + json.dumps(clear),
    'retainer screws: all four open at %d of %d pan angles, e.g. %s' % (len(ok_pans), len(access), ok_pans[:8]),
    'at pan 0 blocked: %s' % access.get(0.0),
    'clamp screws (pulley fitted) blocked at pans: %s' % sorted(clamp_bad),
    'clamp screws blocked at carriage ends: %s' % {k: sorted(v) for k, v in clamp_bad_end.items()},
    'horn screw from above, open pans: %s' % report['service_paths']['horn_screw_from_above']['open_pans'],
    'horn screw blocked by: %s' % sorted(set(x[1] for v in horn_bad.values() for x in v)),
    'tilt horn screw along the axis blocked: %s' % tilt_bad,
    'tilt horn screw roof: %.3f of %.3f mm3 solid, outer face x %.2f' % (_left, _ann.Volume, ROOF_OUT_X),
    'yoke bolts from above blocked: %s' % {k: sorted(set(v)) for k, v in yb_bad.items()},
    'GH44 carrier screws from the front blocked by: %s' % sorted(set(b for _, b in gh_bad)), '']
seen = {}
for c in report['collisions']:
    k = (c['a'], c['b'], c['kind'])
    seen.setdefault(k, []).append(c)
for k, v in seen.items():
    lines.append('COLLISION %s: %d poses, worst %.1f mm3 (pan %s tilt %s C %s)' % (
        k, len(v), max(x['mm3'] for x in v), v[0]['pan'], v[0]['tilt'], v[0]['carriage']))
for r in exp_report:
    lines.append('%-22s %5.1f x %5.1f x %5.1f  %5.2f cm3  bed %4s  probes %s  mesh %s' % (
        r['part'], r['size_mm'][0], r['size_mm'][1], r['size_mm'][2], r['volume_cm3'], r['bed_contact_mm2'],
        r['probes_pass'], 'ok' if r['mesh_solid'] and not r['mesh_non_manifold'] else 'BAD'))
(OUT / 'build-summary.txt').write_text(NL.join(lines))
Path('/tmp/v05_summary.txt').write_text(NL.join(lines))
print(NL.join(lines))
A.closeDocument(doc.Name)
if not report['checks']['sampled_geometry_pass']:
    raise RuntimeError('v05 failed validation; do not regenerate or replace print plates.')
