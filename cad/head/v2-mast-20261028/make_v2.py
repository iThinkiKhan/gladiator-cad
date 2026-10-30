"""Writes scripts/build_head_v2_mast.py: the v05 head generator (geometry part only, unchanged apart
from the listed patches) + the v2 section in v2_tail.py. Run from the repo root with python3."""
import hashlib, sys
from pathlib import Path

ROOT = Path('/home/buralien/projects/gladiator-cad')
src = (ROOT / 'scripts/build_head_v05.py').read_text()
MARK = '# ================================================================== the current robot, from the master'
assert src.count(MARK) == 1
head = src.split(MARK)[0]


def sub(old, new, count=1):
    global head
    n = head.count(old)
    assert n == count, (n, old[:80])
    head = head.replace(old, new)


def span(start, end, new):
    """replace from the line starting with `start` through the line starting with `end`"""
    global head
    i = head.index(start)
    j = head.index(end, i)
    j = head.index('\n', j) + 1
    assert head.count(start) == 1
    head = head[:i] + new + head[j:]


sub("OUT = ROOT / 'cad/head/v05-sensor-mounts'", "OUT = ROOT / 'cad/head/v2-mast-20261028'")
sub("LIFT = 10.0                       # real mast top 130, drawn at 120",
    "LIFT = 30.0                       # v2: real mast top 150 (+20 over v1; Jim 2026-10-29, tipping), drawn at 120")
sub("C_MIN, C_MAX = 37.0, 40.4         # carriage travel. C_MIN gives belt slack; C_MAX is past taut\nC_NOM = 39.75",
    "C_MIN, C_MAX = 38.0, 48.0         # v2: the v1 belt was still loose at the 40.8 stop (Jim dremeled v1 to the screw holes)\nC_NOM = 44.0")
sub("POCKET_DEPTH, BOSS_RECESS, ROOF_T = 1.2, BOSS_UP + 0.6, 1.2",
    "POCKET_DEPTH, BOSS_RECESS, ROOF_T = 2.2, BOSS_UP + 0.6, 1.2   # v2: 2.0 horn arm fully buried (v1 1.2)")
sub("TOP_PLATE_Z, TOP_PLATE_T = 165.5, 4.0",
    "YOKE_DY = 26.0                                    # v2: yoke 26 mm rearward, tilt pivot over the mast axis\n"
    "TOP_PLATE_Z, TOP_PLATE_T = 166.5, 4.0  # v2 +1: the deeper horn pocket lifts the belt line 1.0;")

sub("T = A.Vector(0, -26, 205.0 + TILT_SHIFT)       # tilt axis",
    "YOKE_H = 10.0                                    # v2: pivot 10 higher over the same yoke floor (tilt sweep)\n"
    "T = A.Vector(0, -26, 205.0 + TILT_SHIFT + YOKE_H)  # tilt axis")
sub("assert abs(F0 - (TZ - 37.0)) < 1e-6, (F0, TZ)", "assert abs(F0 - (TZ - 37.0 - YOKE_H)) < 1e-6, (F0, TZ)")
sub("tower = fuse(box(28, -35, F0, 5, 18, 45), box(19, -35, F0, 14, 18, 4))",
    "# v2: pivot tower full width only from 10 below the pivot up; below that a 10 x 6 column (tilt sweep)\n"
    "tower = fuse(box(28, -35, TZ - 10.0, 5, 18, F0 + 45 + YOKE_H - (TZ - 10.0)),\n"
    "             box(23, T.y - 3.0, F0, 10, 6.0, TZ - 10.0 - F0 + 0.01), box(19, -35, F0, 14, 18, 4))")
sub("earplate = box(EARPLATE_X, -36, F0, 3, 20, 60)",
    "# v2: full 20 mm ear plate only from just below the servo ears up (taller by YOKE_H); below that a 12.2 x 6\n"
    "# column, so the receiver plate and screen bezel can swing past it (v1 stopped them near 27-32 deg).\n"
    "earplate = fuse(box(EARPLATE_X, -36, TZ - 12.0, 3, 20, F0 + 60 + YOKE_H - (TZ - 12.0)),\n"
    "                box(EARPLATE_X - 9.2, T.y - 3.0, F0, 12.2, 6.0, TZ - 12.0 - F0 + 0.01))")

span("collar = ring(COLLAR_R, BORE_R, 104, 16)",
     "rear = fuse(rear, box(-KEY_HALF, key_y0, 106, 2 * KEY_HALF, (BORE_R + 0.6) - key_y0, 13))",
     '''# v2 collar (Jim, 2026-10-28: "a pass through screw with a wingnut, like ... where the mast meets the deck").
# One piece, 40 tall (v1: 16 mm split clamp + cap, 2 x M3). The tested 1-notch key on the flat stays.
# One M3 through-bolt across X passes the collar AND the mast; a 2 mm split on the -Y side lets the
# wingnut also squeeze the collar onto the tube. The closed band above the split carries the C arm.
COLLAR_H, COLLAR_Z0 = 37.0, 83.0       # bottom at world 113: 3.6 over the front panels (Z 109.4)
BOLT_Z = COLLAR_Z0 + 10.0
SPLIT_W, SPLIT_TOP = 2.0, 112.0
LUG_X = 15.0
def cx_(r, x, h, y, z): return Part.makeCylinder(r, h, A.Vector(x, y, z), A.Vector(1, 0, 0))
rear = fuse(ring(COLLAR_R, BORE_R, COLLAR_Z0, COLLAR_H), box(-LUG_X, -5, BOLT_Z - 6, 2 * LUG_X, 10, 12))
rear = rear.cut(cyl(BORE_R, COLLAR_Z0 - 1, COLLAR_H + 2))
rear = rear.cut(box(-SPLIT_W / 2, -COLLAR_R - 1, COLLAR_Z0 - 1, SPLIT_W, COLLAR_R - BORE_R + 1.5, SPLIT_TOP - COLLAR_Z0 + 1))
rear = rear.cut(cx_(M3_CLEAR / 2, -LUG_X - 1, 2 * LUG_X + 2, 0, BOLT_Z))
key_y0 = FLAT_Y + KEY_GAP
rear = fuse(rear, box(-KEY_HALF, key_y0, COLLAR_Z0 + 2, 2 * KEY_HALF, (BORE_R + 0.6) - key_y0, COLLAR_H - 3))
''')

span("EXT = 9.0                                            # carriage tab beyond the ear region",
     "PAD_HW = 13.5",
     '''# v2: travel 37..43 (v1 37..40.4). The clamp screws stay outboard, placed so their heads clear the
# ear tips by 0.5 at C_MAX (v3 had only 0.4 at 42.4).
C_RANGE = C_MAX - C_MIN
HEAD_R = 2.75
NUT_X = 11.0                                  # v2: screws BESIDE the servo body (v1 8.5, in line)
NUT_Y = y_bc(C_MAX) - (EAR_SPAN / 2 + HEAD_R + 0.5)
SLOT_OFF = NUT_Y - (y_bc(C_MIN) + y_bc(C_MAX)) / 2.0  # slot centre, from the body centre
PAD_Y0 = NUT_Y - NUT_AF / math.sqrt(3) - 2.0
PAD_Y1 = y_bc(C_MIN) + 17.5 + 0.5
PAD_HW = 15.5
END_BAR = 4.0                                 # v2: the only bar left outboard of the servo; the tensioner pushes on it
''')

sub("addp('Neck_Clamp_Cap', front, 'fixed', 'collar front half', 'FixedNeck')\n", "")
sub("addp('Neck_Main', neck, 'fixed', 'collar rear half + key, C arm, servo pad, spindle', 'FixedNeck')",
    "addp('Neck_Main', neck, 'fixed', 'v2: 40 mm one-piece collar + key, wingnut bolt, C arm, pad, spindle', 'FixedNeck')")

span("CAR_HW, CAR_L = 12.5, 35.0", "car_F = car.copy()                  # axis-aligned, for printing",
     '''CAR_HW, CAR_L = 14.5, 35.0                          # v2: wider for the outboard screws
SLOT_W = M3_CLEAR
SLOT_L = SLOT_W + C_RANGE
# v2 belt tensioner: a lug hangs from the carriage just outside the pad end. An M3 x16 runs through a
# captive nut in it; its tip bears on the pad end face, so screwing it in pushes the servo out.
LUG_T, LUG_HW = 7.0, 5.0
LUG_IN = (PAD_Y0 - 0.5) - y_bc(C_MIN)               # lug inner face from the body centre: 0.5 off the pad at C_MIN
LUG_OUT = LUG_IN - LUG_T
TS_Z = PAD_BOT + PAD_T / 2.0                        # screw axis: middle of the pad end face
LUG_BOT = TS_Z - NUT_AF / math.sqrt(3) - 0.15 - 1.5
yb = y_bc(C_NOM)
car = box(-CAR_HW, yb + LUG_OUT, PAD_TOP, 2 * CAR_HW, CAR_L / 2 - LUG_OUT, CAR_T)
car = car.cut(box(-BODY_W / 2, yb - BODY_L / 2, PAD_TOP - 1, BODY_W, BODY_L, CAR_T + 2))
for sy in (-1, 1):
    car = car.cut(cyl(PILOT_M2 / 2, PAD_TOP - 0.1, CAR_T + 0.2, 0, yb + sy * EAR_PITCH / 2))
ys = yb + SLOT_OFF
for sx in (-1, 1):
    car = car.cut(slot_z(sx * NUT_X, ys - (SLOT_L - SLOT_W) / 2, ys + (SLOT_L - SLOT_W) / 2,
                         PAD_TOP - 0.1, CAR_T + 0.2, SLOT_W))
car = fuse(car, box(-LUG_HW, yb + LUG_OUT, LUG_BOT, 2 * LUG_HW, LUG_T, PAD_TOP - LUG_BOT + 0.01))
car = car.cut(box(-(NUT_AF / 2 + 0.1), yb + LUG_OUT + LUG_T / 2 - 1.4, TS_Z - NUT_AF / math.sqrt(3) - 0.15,
                  NUT_AF + 0.2, 2.8, PAD_TOP + CAR_T + 1 - (TS_Z - NUT_AF / math.sqrt(3) - 0.15)))   # nut, from the top
car = car.cut(cy(M3_CLEAR / 2, yb + LUG_OUT - 0.1, LUG_T + 0.2, 0, TS_Z))
assert NUT_Y - y_bc(C_MAX) + HEAD_R <= -(EAR_SPAN / 2) - 0.5 + 1e-9
car_F = car.copy()                  # axis-aligned, for printing
''')

sub("ring(R_ROT, 6.5, TOP_PLATE_Z, TOP_PLATE_T), box(-25, -30, TOP_PLATE_Z, 50, 30, TOP_PLATE_T))",
    "ring(R_ROT, 6.5, TOP_PLATE_Z, TOP_PLATE_T), box(-27, -47 + YOKE_DY, TOP_PLATE_Z, 54, 35, TOP_PLATE_T))  # v2 seat under the moved yoke")
sub('''for x, y in YOKE_BOLTS:
    ped = ped.cut(cyl(M3_CLEAR / 2, TOP_PLATE_Z - 0.1, TOP_PLATE_T + 0.2, x, y))
    ped = ped.cut(hex_z(NUT_AF, TOP_PLATE_Z - 0.1, NUT_DEPTH + 0.1, x, y))''',
    '''for x, y in YOKE_BOLTS:
    y = y + YOKE_DY                                                               # v2: the yoke moved
    ped = ped.cut(cyl(M3_CLEAR / 2, TOP_PLATE_Z - 0.1, TOP_PLATE_T + 0.2, x, y))
    ped = ped.cut(hex_z(NUT_AF, TOP_PLATE_Z - 0.1, NUT_DEPTH + 0.1, x, y))''')
sub("addp('Pan_Raised_Pedestal', ped, 'pan', 'integral 40T driven ring, yoke seat', 'Pan')",
    "addp('Pan_Raised_Pedestal', ped, 'pan', 'v2: belt line +1, yoke seat 26 mm rearward', 'Pan')")

sub('pad = pad.cut(box(-(BODY_W / 2 + 0.4), y_bc(C_MAX) - BODY_L / 2 - 0.5, PAD_BOT - 1,\n                  BODY_W + 0.8, (y_bc(C_MIN) - y_bc(C_MAX)) + BODY_L + 1.0, PAD_T + 2))',
    'pad = pad.cut(box(-(BODY_W / 2 + 0.4), PAD_Y0 + END_BAR, PAD_BOT - 1,   # v2: open out to the end bar\n                  BODY_W + 0.8, (y_bc(C_MIN) + BODY_L / 2 + 0.5) - (PAD_Y0 + END_BAR), PAD_T + 2))')

tail = Path(sys.argv[1]).read_text()
banner = ('"""Gladiator masthead v2 (2026-10-28), GENERATED by make_v2.py. Do not hand-edit.\n'
          'Geometry part = scripts/build_head_v05.py (sha256 %s) up to the robot section, with the\n'
          'patches marked "v2" below; then the v2 section (mast tube, v06 frame, camera case, moved yoke,\n'
          'sweeps, balance, exports). Run: xvfb-run -a freecadcmd scripts/build_head_v2_mast.py\n"""\n'
          % hashlib.sha256(src.encode()).hexdigest())
out = ROOT / 'scripts/build_head_v2_mast.py'
out.write_text(banner + head + MARK + ' (v2 section)\n' + tail)
print('wrote', out, len((banner + head + tail).splitlines()), 'lines')
