"""Gladiator head v0.4 - the pan stack, rebuilt from the measured numbers.

What this builds (everything the PAN drive needs, calibrated and re-based):
    Neck_Main, Neck_Clamp_Cap   collar with the tested 1-notch key, M3 nut pockets, C arm,
                                spindle with the circlip groove, servo pad and riser
    Pan_Servo_Carriage          slides on the pad: belt tension and belt installation
    Pan_Rotor, Pan_Retainer     bearing seats at the tested 32.35, M2 pilots
    Pan_Raised_Pedestal         integral 40T driven ring, 4 retainer screws, yoke seat
    Pan_Drive_Pulley            60T with a horn plate that takes the real SG90 cross horn
    SG90 / horn / belt / bearings as clearance references

What it INHERITS from v0.3, unchanged except a 1 mm lift (the tilt side, stage 2):
    Tilt_Yoke, GH44 receiver and carriers, display frame, sensor envelopes.
    Their screw holes are still at the v0.3 nominal sizes. They are NOT print-ready.

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
OUT = ROOT / 'cad/head/v04-pan-stack'
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
PILOT_M2 = 2.2        # PENDING H4b: 2.2 was the best of 1.8/2.0/2.2 and Jim said maybe bigger
POST_D = 20.05        # PENDING H3b: 20.20 jammed a 6804. This is a placeholder, not a result
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
HORN_G = 0.25         # ASSUMED gap between the case boss and the horn underside
HORN_C = 0.15         # PENDING H6: snug 0.15 / easy 0.30
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


before = {str(MASTER): digest(MASTER), str(SOURCE): digest(SOURCE)}


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


report = {'release': 'DESIGN CANDIDATE, stage 1 (pan stack). Not released.',
          'source_sha256': before, 'parts': [], 'checks': {}, 'collisions': [],
          'pending': {}, 'assumed': {}, 'limitations': []}
report['pending'] = {
    'POST_D': 'placeholder %.2f until the H3b bearing-post coupon is read (20.20 jammed)' % POST_D,
    'PILOT_M2': 'placeholder %.1f until H4b is read (2.2 best of the first three; Jim said maybe bigger)' % PILOT_M2,
    'HORN_C': 'placeholder %.2f until H6 is read (0.15 snug / 0.30 easy)' % HORN_C,
}
report['assumed'] = {
    'ARM_T': '%.1f horn arm thickness, NOT measured' % ARM_T,
    'HORN_G': '%.2f gap between the case boss and the horn underside, NOT measured' % HORN_G,
    'SHAFT_NEAR': '%.1f from the near body end, about +-0.6' % SHAFT_NEAR,
    'servo_cross_centre': 'shaft assumed centred across the 12 mm width',
    'horn_screw_head': 'about 4 mm, read off a photo, NOT measured',
}

# ================================================================== inherited tilt side (v0.3)
src = A.openDocument(str(SOURCE))
inherit_names = ['Tilt_Yoke', 'SG90_Tilt_Reference', 'Tilt_Horn_Reference', 'Tilt_Idler_Bushing',
                 'GH44_Tilt_Receiver', 'GH44_Dual_Carrier', 'Dual_ToF_Envelope', 'Dual_Radar_Envelope',
                 'Rear_Display_Frame', 'ST7789_Board_62x29x3_2']
variant_names = ['GH44_Blank_Carrier', 'GH44_ToF_Carrier', 'GH44_Radar_Carrier', 'GH44_Camera_Carrier',
                 'SEN0628_Envelope', 'SEN0610_Envelope', 'ESP32_CAM_Envelope']
motion_of = {'Tilt_Yoke': 'pan', 'SG90_Tilt_Reference': 'pan', 'Tilt_Idler_Bushing': 'pan'}
inh = {}
for n in inherit_names + variant_names:
    o = src.getObject(n)
    s = o.Shape.copy()
    s.translate(A.Vector(-C0.x, -C0.y, TILT_SHIFT))
    inh[n] = {'shape': s, 'motion': motion_of.get(n, o.MotionGroup if 'MotionGroup' in o.PropertiesList else 'tilt')}
A.closeDocument(src.Name)

# the yoke M3 holes to the pedestal are re-drilled to the calibrated 3.6; its other holes stay nominal
YOKE_BOLTS = [(-20.0, -25.0), (20.0, -25.0)]
for x, y in YOKE_BOLTS:
    inh['Tilt_Yoke']['shape'] = inh['Tilt_Yoke']['shape'].cut(cyl(M3_CLEAR / 2, TOP_PLATE_Z, 16, x, y))

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
sv = fuse(box(-BODY_W / 2, -(BODY_L - SHAFT_NEAR), 0, BODY_W, BODY_L, EAR_UNDER),
          box(-BODY_W / 2, -(BODY_L - SHAFT_NEAR) - 4.9, EAR_UNDER, BODY_W, BODY_L + 9.8, EAR_T),
          box(-BODY_W / 2, -11.0, EAR_UNDER + EAR_T, BODY_W, 11.0 + SHAFT_NEAR, 6.0),
          cyl(5.5, EAR_UNDER + EAR_T, BOSS_TOP - EAR_UNDER - EAR_T),
          cyl(2.4, BOSS_TOP, SPLINE_TOP - BOSS_TOP))
# The body is already drawn with its long end (BODY_L - SHAFT_NEAR) toward -Y, the outer end.
# v0.3 drew it the other way round and rotated it 180; doing that here swung it into the arm.
sv.translate(A.Vector(0, -C_NOM, ZSB))
addp('SG90_Pan_Reference', rotF(sv), 'fixed', 'measured heights; shaft position +-0.6', 'Hardware')

horn = fuse(horn_solid(0.0, HORN_UNDER, ARM_T), cyl(BOSS_D / 2, HORN_UNDER + ARM_T, BOSS_UP))
horn = horn.cut(cyl(2.5, HORN_UNDER - 0.1, ARM_T + BOSS_UP + 0.2))      # the spline socket
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

for n in inherit_names:
    addp(n, inh[n]['shape'], inh[n]['motion'], 'INHERITED from v0.3, lifted %.1f; nominal holes' % TILT_SHIFT, 'TiltInherited')

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
TILTS = (-25.0, 0.0, 25.0)
PAN_SAMPLES = [float(a) for a in range(int(HEAD_TRAVEL[0]), int(HEAD_TRAVEL[1]) + 1, 5)]
SERVO_SIDE = ('SG90_Pan_Reference', 'Pan_Servo_Carriage', 'Pan_Drive_Pulley', 'Pan_Horn_Reference',
              'Pan_Belt_Reference')


def posed(p, pan=0.0, tilt=0.0, C=None):
    s = p['shape'].copy()
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
for pan in PAN_SAMPLES:
    for tilt in TILTS:
        for p in plist:
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
        for tilt in (0.0, 25.0):
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


frustum = Part.makeLoft([square(-71, .5, -17), square(-221, .5 + 150 * math.tan(math.radians(30)), -17)], True)
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
            if p['motion'] == 'tilt' or p['name'].startswith('GH44') or 'Envelope' in p['name']:
                continue
            v = overlap(f, posed(p, pan, tilt))
            if v > .05:
                report['fov_intersections'].append({'pan': pan, 'tilt': tilt, 'object': p['name'], 'mm3': round(v, 2)})

report['checks']['all_parts_single_valid_solid'] = all(p['shape'].isValid() and len(p['shape'].Solids) == 1
                                                       for p in plist)
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
doc = A.newDocument('GladiatorHeadV04')
doc.Label = 'Gladiator head v0.4 - pan stack (stage 1)'
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
doc.saveAs(str(OUT / 'Gladiator_Head_v04_PanStack.FCStd'))
Part.export([doc.getObject(p['name']) for p in plist], str(OUT / 'Gladiator_Head_v04_PanStack.step'))

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
                  'WAIT for H3b (post size) and the horn arm thickness from H6 (it sets the pad height)',
                  [((0, 12.5, 110), True), ((0, 0, 110), False), ((0, 9.3, 112), True)]),
    'Neck_Clamp_Cap': (front, 'as modelled, axis vertical, lugs on the bed; no support', 'none - tested geometry',
                       [((0, -12, 110), True), ((0, -8, 110), False)]),
    'Pan_Servo_Carriage': (car_F, 'flat, long axis along the bed X; no support',
                           'WAIT for H4b (ear pilots)', []),
    'Pan_Rotor': (rotor, 'axis vertical, LOWER bearing seat on the bed (relieved); no support',
                  'WAIT for H4b (M2 pilots)',
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
                         'WAIT for H6 (pocket clearance and the real arm thickness)',
                         [((10, 0, PLATE_RIM_Z + 0.6), False), ((10, 0, ZC - 0.5), True),
                          ((0, 0, ZC - 0.5), False)]),
}
OFF = {}
exp_report = []
for name, (shape, how, gate, probes) in exports.items():
    s = shape.copy()
    b0 = s.BoundBox
    dz = -b0.ZMin
    dx, dy = -b0.XMin, -b0.YMin
    s.translate(A.Vector(dx, dy, dz))
    pr = [((x + dx, y + dy, z + dz), ins) for (x, y, z), ins in probes]
    # the probes are given for parts centred on the mast axis; the carriage and pad are not, so skip those
    s, nch = bed_chamfer(s)
    assert s.isValid() and len(s.Solids) == 1, name + ' after chamfer'
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=LIN, AngularDeflection=ANG, Relative=False)
    path = OUT / 'stl' / ('Gladiator_Head_v04_%s.stl' % name)
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
           'NOT_RELEASED': True}
    exp_report.append(rec)
report['stl'] = exp_report

# ================================================================== write it out
report['limitations'] = [
    'Stage 1: the PAN stack only. The tilt yoke, GH44 receiver and carriers, display frame and sensor '
    'envelopes are INHERITED from v0.3, lifted %.1f mm, with their screw holes still at the v0.3 nominal '
    'sizes. Only the two yoke-to-pedestal M3 holes were re-drilled to 3.6. They are not print-ready.' % TILT_SHIFT,
    'Three numbers are placeholders until the final coupon plate is read: POST_D %.2f (H3b), PILOT_M2 %.1f (H4b), '
    'HORN_C %.2f (H6).' % (POST_D, PILOT_M2, HORN_C),
    'The horn arm thickness (%.1f) and the boss-to-horn gap (%.2f) are ASSUMED. They set the servo height, so '
    'they set the belt alignment. The first assembly should leave room to shim it.' % (ARM_T, HORN_G),
    'Servo shaft position along the body is +-0.6. The carriage slot covers it.',
    'Sampled rigid-solid checks every 5 degrees of pan. They do not prove clearance between samples, nor '
    'cable behaviour, belt tooth mesh, stiffness, creep, or that the belt can be fitted.',
    'The belt can be fitted with the carriage at its slack end, but that is argued, not tested.',
    'No load, torque or payload rating is claimed.']
report['checks']['master_unchanged'] = all(digest(p) == h for p, h in before.items())
report['checks']['sampled_geometry_pass'] = (
    not [c for c in report['collisions']] and not report['fov_intersections']
    and report['checks']['all_parts_single_valid_solid']
    and report['checks']['cable_passage_11_9mm_overlap_mm3'] < .01
    and report['checks']['master_unchanged'])
(OUT / 'validation.json').write_text(json.dumps(report, indent=2, default=str) + '\n')
(OUT / 'head-config.json').write_text(json.dumps({
    'drive': report['drive'], 'stack_Z': report['stack_Z'], 'pending': report['pending'],
    'assumed': report['assumed'], 'release': report['release']}, indent=2) + '\n')

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
    'horn screw blocked by: %s' % sorted(set(x[1] for v in horn_bad.values() for x in v)), '']
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
Path('/tmp/v04_summary.txt').write_text(NL.join(lines))
print(NL.join(lines))
A.closeDocument(doc.Name)
