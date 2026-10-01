"""Gladiator head coupons, round 2 (2026-09-30).

Five small coupons that retire the physical unknowns in the head that can be
tested before any new measurement comes back. Each answers ONE question.

    H1  belt centre distance   60T + 40T printed pulleys on the real 180 mm belt
    H2  neck collar            slides onto the real printed v2 mast and keys the flat
    H3  circlip post           a 6804 on the printed spindle, held by a real circlip
    H4  M2 pilots              which pilot an M2 screw (or SG90 ear screw) bites in
    H5  M3 nut sockets         which hex socket takes an M3 nut
    H6  horn pocket            does the real cross horn seat in a printed pocket (added 2026-10-01)

Round features on this printer print ~0.25 under, convex and concave alike
(measurements/printer-calibration.md). Sizes below are modelled values; the
expected printed value is noted where it matters.

Run with freecadcmd on the CAD server. Reads nothing from the master; the mast
numbers were checked against it and the printed build-2 STL on 2026-09-30.
"""
import sys, json, math, zipfile
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as A
import Part, Mesh, MeshPart

ROOT = Path('/home/buralien/projects/gladiator-cad')
OUT = ROOT / 'cad/head/coupons-r2-20260930'
STL = OUT / 'stl'
STL.mkdir(parents=True, exist_ok=True)
PREFIX = 'Gladiator_HeadR2_'

LIN, ANG = 0.01, 0.0872665          # 0.01 mm deflection, never the default
BED_X, BED_Y, MARGIN, GAP = 220.0, 220.0, 10.0, 8.0
BED_RELIEF = 0.5                    # same bed-plane entrance relief as plates E/F
CURVE_ERR = 0.25
M3_CLEAR, M3_SLOT = 3.6, 3.4        # 3.6 round passes M3; 3.4 flat-walled slot does too

report = {'status': 'FIT COUPONS - not a head release', 'pieces': {}, 'checks': {},
          'plate': {}}


# ------------------------------------------------------------------ helpers
def cyl(r, z, h, x=0.0, y=0.0):
    return Part.makeCylinder(r, h, A.Vector(x, y, z))


def cyl_y(r, y, h, x, z):
    return Part.makeCylinder(r, h, A.Vector(x, y, z), A.Vector(0, 1, 0))


def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, A.Vector(x, y, z))


def ring(ro, ri, z, h, x=0.0, y=0.0):
    return cyl(ro, z, h, x, y).cut(cyl(ri, z - 0.1, h + 0.2, x, y))


def fuse(*ss):
    s = ss[0]
    for t in ss[1:]:
        s = s.fuse(t)
    return s.removeSplitter()


def prism(pts, z, h):
    vs = [A.Vector(x, y, z) for x, y in pts]
    return Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(A.Vector(0, 0, h))


def hex_prism(af, z, h, x, y):
    r = af / math.sqrt(3)
    return prism([(x + r * math.cos(k * math.pi / 3), y + r * math.sin(k * math.pi / 3))
                  for k in range(6)], z, h)


def side_notches(shape, n, x_centre, y_face, z0, h, pitch=1.4, w=0.6, d=0.7):
    """n small vertical grooves in the face y = y_face, centred on x_centre."""
    for k in range(n):
        x = x_centre + (k - (n - 1) / 2.0) * pitch
        shape = shape.cut(box(x - w / 2, y_face - 0.1, z0 - 0.5, w, d + 0.1, h + 1.0))
    return shape


def radial_notches(shape, n, r_at, z0, h, centre_deg, step_deg=7.0, rad=0.8):
    for k in range(n):
        a = math.radians(centre_deg + (k - (n - 1) / 2.0) * step_deg)
        shape = shape.cut(cyl(rad, z0 - 0.5, h + 1.0, r_at * math.cos(a), r_at * math.sin(a)))
    return shape


def bed_chamfer(shape, size=BED_RELIEF):
    """Chamfer every full-circle edge in the bed plane (copied from build_coupon_plate)."""
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
    a = 0.0
    for f in shape.Faces:
        b = f.BoundBox
        if abs(b.ZMin - z0) < 1e-6 and abs(b.ZMax - z0) < 1e-6:
            a += f.Area
    return a


pieces = []   # (key, file stem, shape, orientation note, probes)


def add(key, stem, shape, note, probes, bed_min):
    """probes: list of ((x,y,z), expect_inside) in the PRINT orientation."""
    assert shape.isValid() and len(shape.Solids) == 1, key + ' invalid'
    b = shape.BoundBox
    shape.translate(A.Vector(-b.XMin, -b.YMin, -b.ZMin))
    probes = [((x - b.XMin, y - b.YMin, z - b.ZMin), inside) for (x, y, z), inside in probes]
    pieces.append({'key': key, 'stem': stem, 'shape': shape, 'note': note,
                   'probes': probes, 'bed_min': bed_min})


# =========================================================== H1 belt coupon
PITCH, PLD, DEPTH, GROOVE_R = 2.0, 0.254, 0.75, 0.65   # 2-notch profile, passed 09-22
BELT_TEETH = 90
N_DRIVE, N_DRIVEN = 60, 40      # 60T on the servo, 40T on the head: head = servo x 1.5
CHANNEL = 7.0                   # between flanges; a 6 mm belt in a 6.0 channel rubs
FLANGE_T, FLANGE_OVER, RIM_T = 1.0, 1.5, 0.6
RIM_WALL = 2.5                  # material behind the groove root
HUB_R = 4.5


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


R_DRIVE = N_DRIVE * PITCH / (2 * math.pi)
R_DRIVEN = N_DRIVEN * PITCH / (2 * math.pi)
C_THEORY = solve_c(R_DRIVE, R_DRIVEN, BELT_TEETH * PITCH)
C_PRINTED = solve_c(R_DRIVE - CURVE_ERR / 2, R_DRIVEN - CURVE_ERR / 2, BELT_TEETH * PITCH)
SLOT_LO, SLOT_HI = 37.5, 42.0


def pulley(n):
    pd = n * PITCH / math.pi
    ro = pd / 2 - PLD
    rc = ro - DEPTH + GROOVE_R
    r_in = ro - DEPTH - RIM_WALL
    zc = FLANGE_T
    teeth = cyl(ro, zc, CHANNEL).cut(cyl(r_in, zc - 0.1, CHANNEL + 0.2))
    grooves = [cyl(GROOVE_R, zc - 0.1, CHANNEL + 0.2,
                   rc * math.cos(2 * math.pi * i / n), rc * math.sin(2 * math.pi * i / n))
               for i in range(n)]
    teeth = teeth.cut(grooves)
    fr = ro + FLANGE_OVER
    top = zc + CHANNEL
    bottom = ring(fr, r_in, 0, FLANGE_T)
    cone = Part.makeCone(ro, fr, FLANGE_OVER, A.Vector(0, 0, top)).cut(
        cyl(r_in, top - 0.1, FLANGE_OVER + 0.2))
    rim = ring(fr, r_in, top + FLANGE_OVER, RIM_T)
    total = top + FLANGE_OVER + RIM_T
    hub = cyl(HUB_R, 0, total)
    spokes = []
    for a in (90, 210, 330):
        s = box(HUB_R - 0.5, -2.0, 0, r_in - HUB_R + 1.0, 4.0, 2.0)
        s.rotate(A.Vector(), A.Vector(0, 0, 1), a)
        spokes.append(s)
    body = fuse(teeth, bottom, cone, rim, hub, *spokes)
    body = body.cut(cyl(M3_CLEAR / 2, -0.1, total + 0.2))
    info = {'teeth': n, 'pitch_dia': round(pd, 3), 'tip_dia': round(2 * ro, 3),
            'root_dia': round(2 * (ro - DEPTH), 3), 'flange_dia': round(2 * fr, 3),
            'channel_mm': CHANNEL, 'height': round(total, 2),
            'groove_r': GROOVE_R, 'groove_depth': DEPTH}
    return body, info, ro, r_in


p60, i60, ro60, rin60 = pulley(N_DRIVE)
p40, i40, ro40, rin40 = pulley(N_DRIVEN)
mid = FLANGE_T + CHANNEL / 2
add('H1a', 'H1a_BeltPulley-60T_flange-down', p60,
    'bottom flange on the bed, teeth vertical, 45-degree top flange - no support',
    [((ro60 - DEPTH - 0.3, 0, mid), True), ((0, 0, mid), False),
     ((ro60 + 0.5, 0, 0.5), True), ((ro60 + 0.5, 0, mid), False)],
    300)
add('H1b', 'H1b_BeltPulley-40T_flange-down', p40,
    'bottom flange on the bed, teeth vertical, 45-degree top flange - no support',
    [((ro40 - DEPTH - 0.3, 0, mid), True), ((0, 0, mid), False),
     ((ro40 + 0.5, 0, 0.5), True), ((ro40 + 0.5, 0, mid), False)],
    150)

bar = box(-6, -5, 0, SLOT_HI + 12, 10, 4)
bar = bar.cut(cyl(M3_CLEAR / 2, -0.1, 4.2))
slot = fuse(cyl(M3_SLOT / 2, -0.1, 4.2, SLOT_LO), cyl(M3_SLOT / 2, -0.1, 4.2, SLOT_HI),
            box(SLOT_LO, -M3_SLOT / 2, -0.1, SLOT_HI - SLOT_LO, M3_SLOT, 4.2))
bar = bar.cut(slot)
# one V notch in the side marks the theoretical centre distance
bar = bar.cut(prism([(C_THEORY - 0.8, 5.1), (C_THEORY + 0.8, 5.1), (C_THEORY, 4.2)], -0.1, 4.2))
add('H1c', 'H1c_BeltBar_flat', bar, 'flat, 4 mm tall - no support',
    [((0, 0, 2), False), ((20, 0, 2), True), ((C_THEORY, 0, 2), False),
     ((C_THEORY, 4.9, 2), False), ((C_THEORY - 2, 4.9, 2), True)],
    300)
report['pieces']['H1'] = {
    'question': 'At what centre distance does the real 180 mm belt sit snug on printed '
                '60T and 40T pulleys, and does it run round cleanly by hand?',
    'drive_pulley': i60, 'driven_pulley': i40,
    'ratio_head_per_servo': N_DRIVE / N_DRIVEN,
    'servo_deg_for_200_head_deg': round(200 * N_DRIVEN / N_DRIVE, 1),
    'centre_distance_theory_mm': round(C_THEORY, 3),
    'centre_distance_if_pulleys_print_0p25_small_mm': round(C_PRINTED, 3),
    'slot_range_mm': [SLOT_LO, SLOT_HI],
    'wrap_small_pulley_deg': round(180 - 2 * math.degrees(math.asin((R_DRIVE - R_DRIVEN) / C_THEORY)), 1),
    'hardware': '2 x M3 bolt 16-20 long, 2 x M3 nut, the belt',
}

# ====================================================== H2 neck collar
# Local frame: mast axis at the origin, mast TOP at Z 0, +Y = robot rear.
# Checked 2026-09-30 against the master and the printed build-2 STL: OD 20,
# index flat on the rear at Y 9.1, 8.0 wide (X +-4), Z -15..0.
MAST_R, FLAT_Y, FLAT_HALF, FLAT_DEPTH = 10.0, 9.1, 4.0, 15.0
BORE_R = 10.2          # 20.4, same as the deck and mast-base sockets the mast already fits
COLLAR_R, H = 14.0, 10.0
KEY_HALF = 3.6         # 7.2 wide in an 8.0 flat
SPLIT = 0.3            # 0.6 clamp gap
DISC_T = 1.2


def collar_body():
    c = fuse(ring(COLLAR_R, BORE_R, -H, H),
             box(-18, -5, -H, 9, 10, H), box(9, -5, -H, 9, 10, H))
    return c.cut(cyl(BORE_R, -H - 1, H + 2))


def bolt_holes(s):
    for x in (-13.5, 13.5):
        s = s.cut(cyl_y(M3_CLEAR / 2, -6, 12, x, -H / 2))
    return s


def collar_rear(gap, marks):
    rear = collar_body().common(box(-30, SPLIT, -H - 1, 60, 30, H + 2))
    key = box(-KEY_HALF, FLAT_Y + gap, -H, 2 * KEY_HALF, BORE_R + 0.6 - (FLAT_Y + gap), H)
    disc = fuse(ring(COLLAR_R, 6.0, 0, DISC_T),
                box(-18, SPLIT, 0, 9, 5 - SPLIT, DISC_T), box(9, SPLIT, 0, 9, 5 - SPLIT, DISC_T))
    rear = bolt_holes(fuse(rear, key, disc))
    rear = radial_notches(rear, marks, COLLAR_R, -H, H + DISC_T, 90.0)
    # print upside down: the seating disc goes on the bed
    rear.rotate(A.Vector(), A.Vector(1, 0, 0), 180)
    return rear


# probes in the flipped frame, before the drop to Z 0 (y -> -y, z -> -z):
# disc at z -1.2..0, collar at z 0..10
def rear_probes(gap):
    return [((0, -(FLAT_Y + gap + 0.3), 5.0), True),      # key present
            ((0, -(FLAT_Y + gap - 0.05), 5.0), False),    # clear of the flat
            ((0, 0, -0.6), False),                        # cable hole open
            ((0, -8, -0.6), True),                        # seat disc on the bed
            ((0, -8, 5.0), False)]                        # mast bore open above it


for key, gap, marks, label in [('H2a', 0.10, 1, 'key-1notch-TIGHT'),
                               ('H2b', 0.25, 2, 'key-2notch-LOOSE')]:
    add(key, 'H2%s_NeckCollar_%s_seat-disc-down' % (key[-1], label), collar_rear(gap, marks),
        'upside down: the 1.2 mm seating disc on the bed, collar and key standing up - no support',
        rear_probes(gap), 400)

cap = bolt_holes(collar_body().common(box(-30, -30, -H - 1, 60, 30 - SPLIT, H + 1 - 0.2)))
add('H2c', 'H2c_NeckCollarCap_standing', cap,
    'as modelled, axis vertical, lugs on the bed - no support',
    [((0, -12, -5), True), ((0, -9, -5), False), ((13.5, -2.5, -5), False), ((13.5, -2.5, -9), True)],
    150)
report['pieces']['H2'] = {
    'question': 'Does the neck collar slide onto the top of the real printed v2 mast, seat on '
                'the top rim, key into the index flat, and lock solid with two M3 bolts? '
                'Which key is the tightest that still slides on?',
    'bore_mm': 2 * BORE_R, 'collar_od_mm': 2 * COLLAR_R, 'height_mm': H,
    'key_width_mm': 2 * KEY_HALF, 'flat_width_mm': 2 * FLAT_HALF,
    'key_gap_to_flat_mm': {'1 notch (H2a)': 0.10, '2 notches (H2b)': 0.25},
    'clamp_gap_mm': 2 * SPLIT,
    'hardware': '2 x M3 bolt 16 long, 2 x M3 nut; the robot with the v2 mast fitted',
}

# ====================================================== H3 circlip post
SH_R, SH_T = 11.5, 2.0          # neck shoulder: bears on the 6804 inner race only
POST_D = 20.20                  # plate F post #2 - the preferred slide fit
BORE = 12.0
BRG_W = 7.0
GROOVE_GAP, GROOVE_W = 0.1, 1.4  # DIN 471 20 mm ring is 1.2 thick
GROOVE_D = 19.25                # standard groove 19.0 + 0.25 curve error
LAND = 1.6
post_top = SH_T + BRG_W + GROOVE_GAP + GROOVE_W + LAND
post = fuse(ring(SH_R, BORE / 2, 0, SH_T), ring(POST_D / 2, BORE / 2, SH_T, post_top - SH_T))
gz = SH_T + BRG_W + GROOVE_GAP
post = post.cut(ring(POST_D / 2 + 0.1, GROOVE_D / 2, gz, GROOVE_W))
top_edges = [e for e in post.Edges if len(e.Vertexes) == 1 and e.Curve.TypeId == 'Part::GeomCircle'
             and abs(e.BoundBox.ZMin - post_top) < 1e-6 and abs(e.Curve.Radius - POST_D / 2) < 1e-6]
post = post.makeChamfer(0.5, top_edges)
add('H3', 'H3_CirclipPost_shoulder-down', post, 'shoulder on the bed, post up - no support',
    [((SH_R - 0.5, 0, 1), True), ((POST_D / 2 - 0.2, 0, SH_T + 3), True),
     ((POST_D / 2 - 0.2, 0, gz + GROOVE_W / 2), False), ((GROOVE_D / 2 - 0.2, 0, gz + 0.7), True),
     ((0, 0, 5), False)],
    200)
report['pieces']['H3'] = {
    'question': 'Does a 6804 slide down the printed post onto the shoulder, and does a 20 mm '
                'external circlip snap into the printed groove above it and hold it without rattle?',
    'post_dia_mm': POST_D, 'shoulder_dia_mm': 2 * SH_R, 'bore_mm': BORE,
    'groove_dia_modelled_mm': GROOVE_D, 'groove_dia_expected_printed_mm': round(GROOVE_D - CURVE_ERR, 2),
    'groove_width_mm': GROOVE_W, 'groove_starts_above_bearing_mm': GROOVE_GAP,
    'hardware': 'one 6804 bearing, one 20 mm external circlip, circlip pliers',
}

# ====================================================== H4 M2 pilots
PILOTS = [1.8, 2.0, 2.2]
h4 = box(0, 0, 0, 30, 7, 8)
for i, d in enumerate(PILOTS):
    x = 6 + 9 * i
    h4 = h4.cut(cyl(d / 2, 1.0, 7.1, x, 3.5))
    h4 = side_notches(h4, i + 1, x, 0.0, 0, 8)
add('H4', 'H4_M2Pilots_flat', h4, 'flat, holes open upward - no support',
    [((6, 3.5, 0.5), True), ((6, 3.5, 7.5), False), ((24, 3.5, 7.5), False), ((15, 3.5, 0.5), True)],
    180)
report['pieces']['H4'] = {
    'question': 'Which pilot lets an M2 machine screw form a thread and hold firmly without '
                'splitting? Try an SG90 ear screw in the same three.',
    'pilot_dia_modelled_mm': PILOTS,
    'pilot_dia_expected_printed_mm': [round(d - CURVE_ERR, 2) for d in PILOTS],
    'depth_mm': 7.0, 'marking': 'notches on the long side, 1 = smallest',
}

# ====================================================== H5 M3 nut sockets
AFS = [5.8, 6.0, 6.2]            # M3 nut is 5.5 across flats; 5.7 on the GH44 receiver failed
h5 = box(0, 0, 0, 32, 10, 5)
for i, af in enumerate(AFS):
    x = 6 + 10 * i
    h5 = h5.cut(hex_prism(af, 5 - 2.6, 2.7, x, 5)).cut(cyl(M3_CLEAR / 2, -0.1, 5.2, x, 5))
    h5 = side_notches(h5, i + 1, x, 0.0, 0, 5)
add('H5', 'H5_M3NutSockets_flat', h5, 'flat, sockets open upward - no support',
    [((6, 5, 4.5), False), ((6 + 2.7, 5, 4.5), False), ((6 + 3.4, 5, 4.5), True),
     ((6 + 2.2, 5, 1.0), True)],
    200)
report['pieces']['H5'] = {
    'question': 'Which hex socket takes an M3 nut pressed in by thumb, and holds it there?',
    'across_flats_mm': AFS, 'depth_mm': 2.6, 'marking': 'notches on the long side, 1 = smallest',
}

# ====================================================== H6 horn pocket
# Cross horn, Jim's calipers 2026-10-01: long arms 36 tip to tip, 6.8 wide at the
# hub tapering to 4.8 at the tip; short arms 19 tip to tip, 3.8 wide throughout;
# hub boss 7.1, standing about 1.0 above the arms when fitted. (Arm thickness and
# total height were NOT given, so POCKET_DEPTH below is an assumption.)
# The 36 mm span is wider than the 60T pulley's 36.19 tooth root, so the pocket
# lives in a wider horn plate on the drive pulley's servo side. This coupon is
# that plate alone, pocket UP, which is how the real drive pulley will print.
HORN_LONG, HORN_SHORT = 36.0, 19.0
LONG_W_HUB, LONG_W_TIP, SHORT_W = 6.8, 4.8, 3.8
BOSS_D, BOSS_UP = 7.1, 1.0
POCKET_DEPTH = 1.2        # ASSUMED: arm thickness not measured; thicker arms just stand proud
BOSS_RECESS = BOSS_UP + 0.3
FLOOR, WALL = 1.2, 2.0
ACCESS_D = 5.0            # horn screw and driver pass through the middle
T6 = FLOOR + BOSS_RECESS + POCKET_DEPTH


def horn_solid(c, z, h):
    """The horn's top-down outline grown by c on every side, extruded z..z+h."""
    rb = BOSS_D / 2
    lt = HORN_LONG / 2 - LONG_W_TIP / 2          # long-arm tip arc centre
    st = HORN_SHORT / 2 - SHORT_W / 2            # short-arm tip arc centre
    h0, h1, hs = LONG_W_HUB / 2 + c, LONG_W_TIP / 2 + c, SHORT_W / 2 + c
    long_arm = prism([(-lt, -h1), (-rb, -h0), (rb, -h0), (lt, -h1),
                      (lt, h1), (rb, h0), (-rb, h0), (-lt, h1)], z, h)
    parts = [long_arm, cyl(h1, z, h, lt, 0), cyl(h1, z, h, -lt, 0),
             box(-hs, -st, z, 2 * hs, 2 * st, h), cyl(hs, z, h, 0, st), cyl(hs, z, h, 0, -st),
             cyl(rb + c, z, h)]
    return fuse(*parts)


def horn_coupon(c, marks):
    body = horn_solid(c + WALL, 0, T6)
    body = body.cut(horn_solid(c, T6 - POCKET_DEPTH, POCKET_DEPTH + 1))
    # boss recess, round so compensated for the curve error
    body = body.cut(cyl(BOSS_D / 2 + c + CURVE_ERR / 2, T6 - POCKET_DEPTH - BOSS_RECESS,
                        BOSS_RECESS + 0.1))
    body = body.cut(cyl(ACCESS_D / 2, -0.1, T6 + 0.2))
    xo = HORN_LONG / 2 + c + WALL                # outer face at the +X long-arm tip
    for k in range(marks):
        body = body.cut(cyl(0.6, -0.5, T6 + 1, xo, (k - (marks - 1) / 2.0) * 1.6))
    return body


def horn_probes(c):
    return [((10, 0, T6 - 0.5), False),            # long-arm pocket open
            ((10, 0, 0.6), True),                  # floor under it
            ((0, 6.5, T6 - 0.5), False),           # short-arm pocket open
            ((3.0, 0, T6 - POCKET_DEPTH - 0.6), False),   # boss recess
            ((5.0, 5.0, T6 - POCKET_DEPTH - 0.6), True),  # but not beyond it
            ((0, 0, 0.6), False),                  # screw access hole
            ((12, 2.85 + c + 0.8, 2.0), True)]     # wall beside the long arm


for key, c, marks, label in [('H6a', 0.15, 1, 'SNUG'), ('H6b', 0.30, 2, 'EASY')]:
    add(key, 'H6%s_HornPocket_%dnotch-%s_pocket-up' % (key[-1], marks, label),
        horn_coupon(c, marks), 'flat, pocket facing up - no support', horn_probes(c), 300)
report['pieces']['H6'] = {
    'question': 'Does the SG90 cross horn drop into the pocket and sit flat with no rotational '
                'play, and can the horn screw be driven through the middle? Which clearance?',
    'horn_measured_2026_10_01': {'long_tip_to_tip': HORN_LONG, 'short_tip_to_tip': HORN_SHORT,
                                 'long_width_hub': LONG_W_HUB, 'long_width_tip': LONG_W_TIP,
                                 'short_width': SHORT_W, 'boss_dia': BOSS_D,
                                 'boss_above_arms': BOSS_UP},
    'clearance_per_side_mm': {'1 notch (H6a) snug': 0.15, '2 notches (H6b) easy': 0.30},
    'pocket_depth_mm': POCKET_DEPTH, 'boss_recess_depth_mm': BOSS_RECESS,
    'access_hole_mm': ACCESS_D, 'thickness_mm': T6,
    'why_a_plate': '36 mm horn span exceeds the 60T tooth root (36.19), so v0.4 carries the '
                   'pocket in a wider horn plate on the drive pulley servo side',
}

# ============================================================ export
LOG = []
for p in pieces:
    sh, nch = bed_chamfer(p['shape'])
    assert sh.isValid() and len(sh.Solids) == 1, p['key'] + ' after chamfer'
    p['shape'] = sh
    b = sh.BoundBox
    probe_ok = all(sh.isInside(A.Vector(*pt), 1e-6, True) == inside for pt, inside in p['probes'])
    bed = bed_area(sh)
    m = MeshPart.meshFromShape(Shape=sh, LinearDeflection=LIN, AngularDeflection=ANG, Relative=False)
    path = STL / (PREFIX + p['stem'] + '.stl')
    m.write(str(path))
    back = Mesh.Mesh(str(path))
    vol_err = abs(back.Volume - sh.Volume) / sh.Volume
    rec = {'file': path.name, 'size_mm': [round(b.XLength, 1), round(b.YLength, 1), round(b.ZLength, 1)],
           'volume_cm3': round(sh.Volume / 1000, 2), 'grams_pla': round(sh.Volume * 0.00124, 1),
           'bed_contact_mm2': round(bed, 0), 'orientation': p['note'],
           'single_valid_solid': True, 'bed_relief_edges': nch,
           'orientation_probes_pass': probe_ok, 'bed_contact_ok': bed >= p['bed_min'],
           'on_z0': abs(b.ZMin) < 1e-9,
           'mesh_solid': back.isSolid(), 'mesh_non_manifold': back.hasNonManifolds(),
           'mesh_volume_error_pct': round(100 * vol_err, 3)}
    rec['pass'] = (probe_ok and rec['bed_contact_ok'] and rec['on_z0'] and rec['mesh_solid']
                   and not rec['mesh_non_manifold'] and vol_err < 0.005)
    report['pieces'].setdefault(p['key'][:2], {}).setdefault('files', []).append(rec)
    p['mesh'] = back
    LOG.append('%-4s %-52s %5.1f x %5.1f x %4.1f  %5.2f cm3  bed %4.0f  %s'
               % (p['key'], path.name, b.XLength, b.YLength, b.ZLength, sh.Volume / 1000, bed,
                  'ok' if rec['pass'] else '*** FAIL'))

# ------------------------------------------------------------ one plate
items = [[p['key'], p['mesh'].copy()] for p in pieces]
for it in items:
    b = it[1].BoundBox
    it[1].translate(-b.XMin, -b.YMin, -b.ZMin)
items.sort(key=lambda it: -it[1].BoundBox.YLength)
shelves, cur, curw, curd = [], [], 0.0, 0.0
for it in items:
    b = it[1].BoundBox
    if cur and curw + GAP + b.XLength > BED_X - 2 * MARGIN:
        shelves.append((cur, curw, curd))
        cur, curw, curd = [], 0.0, 0.0
    curw = b.XLength if not cur else curw + GAP + b.XLength
    curd = max(curd, b.YLength)
    cur.append(it)
if cur:
    shelves.append((cur, curw, curd))
total_d = sum(s[2] for s in shelves) + GAP * (len(shelves) - 1)
y = BED_Y / 2.0 - total_d / 2.0
for row, roww, rowd in shelves:
    x = BED_X / 2.0 - roww / 2.0
    for it in row:
        b = it[1].BoundBox
        it[1].translate(x - b.XMin, y + (rowd - b.YLength) / 2.0 - b.YMin, 0)
        x += b.XLength + GAP
    y += rowd + GAP
offbed = overlaps = 0
for name, m in items:
    b = m.BoundBox
    if not (b.XMin >= MARGIN - 0.01 and b.XMax <= BED_X - MARGIN + 0.01 and
            b.YMin >= MARGIN - 0.01 and b.YMax <= BED_Y - MARGIN + 0.01 and abs(b.ZMin) < 1e-6):
        offbed += 1
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        a, b = items[i][1].BoundBox, items[j][1].BoundBox
        if a.XMin < b.XMax and b.XMin < a.XMax and a.YMin < b.YMax and b.YMin < a.YMax:
            overlaps += 1

NL = chr(10)


def write_3mf(path, title, its):
    md = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<model unit="millimeter" xml:lang="en-US" '
          'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
          '<metadata name="Title">%s</metadata>' % title,
          '<metadata name="Application">gladiator-cad build_head_coupons_r2.py</metadata>',
          '<resources>']
    for oid, (nm, m) in enumerate(its, start=1):
        pts, fcs = m.Topology
        md.append('<object id="%d" type="model" name="%s"><mesh><vertices>' % (oid, nm))
        for q in pts:
            md.append('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % (q.x, q.y, q.z))
        md.append('</vertices><triangles>')
        for f in fcs:
            md.append('<triangle v1="%d" v2="%d" v3="%d"/>' % (f[0], f[1], f[2]))
        md.append('</triangles></mesh></object>')
    md.append('</resources><build>')
    for oid in range(1, len(its) + 1):
        md.append('<item objectid="%d" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>' % oid)
    md.append('</build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?>'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
          '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
            '</Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', ct)
        z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', NL.join(md))


plate = OUT / (PREFIX + 'CouponPlate_ALL-%d-pieces.3mf' % len(items))
write_3mf(str(plate), 'Gladiator head coupons round 2', items)
# re-open and check the container
with zipfile.ZipFile(str(plate)) as z:
    xml = z.read('3D/3dmodel.model').decode()
n_obj = xml.count('<object ')
n_tri = xml.count('<triangle ')
tri_expected = sum(len(m.Topology[1]) for _, m in items)
vol = sum(m.Volume for _, m in items)
report['plate'] = {'file': plate.name, 'pieces': len(items), 'objects_in_3mf': n_obj,
                   'triangles_ok': n_tri == tri_expected, 'offbed': offbed, 'overlaps': overlaps,
                   'volume_cm3': round(vol / 1000, 2), 'grams_pla': round(vol * 0.00124, 0),
                   'unit_mm': 'unit="millimeter"' in xml}
report['checks']['all_pieces_pass'] = all(
    f['pass'] for k, v in report['pieces'].items() for f in v.get('files', []))
report['checks']['plate_pass'] = (offbed == 0 and overlaps == 0 and n_obj == len(items)
                                  and n_tri == tri_expected)

# FreeCAD file + STEP of the coupons in print orientation
doc = A.newDocument('HeadCouponsR2')
objs = []
for p in pieces:
    o = doc.addObject('Part::Feature', p['key'])
    o.Label = p['stem']
    o.Shape = p['shape']
    objs.append(o)
doc.recompute()
doc.saveAs(str(OUT / 'Gladiator_HeadCoupons_R2.FCStd'))
Part.export(objs, str(OUT / 'Gladiator_HeadCoupons_R2.step'))
A.closeDocument(doc.Name)

(OUT / 'validation.json').write_text(json.dumps(report, indent=2) + NL)
LOG.append('')
LOG.append('plate: %d pieces, %.1f cm3, ~%.0f g PLA, offbed %d, overlaps %d, 3mf objects %d, triangles ok %s'
           % (len(items), vol / 1000, vol * 0.00124, offbed, overlaps, n_obj, n_tri == tri_expected))
LOG.append('H1 centre distance theory %.3f, if pulleys print 0.25 small %.3f, slot %.1f..%.1f'
           % (C_THEORY, C_PRINTED, SLOT_LO, SLOT_HI))
LOG.append('ALL PASS' if report['checks']['all_pieces_pass'] and report['checks']['plate_pass'] else '*** NOT ALL PASS')
print(NL.join(LOG))
