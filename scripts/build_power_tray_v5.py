"""Build the Gladiator power-board tray v5 plus its rear bases.  Standalone file; the master is only
read.  Refuses to export if any check fails.

Why v5 (Jim, 2026-10-03, after printing and fitting v4):
  1. The click bumps and 0.25-clearance pegs were far too tight: nothing would come out, and the thin
     front wall tore off the tray before a peg moved.  v5 has NO bumps and NO grooves.  The peg just
     slides into its well (Jim: the fit before the click engaged was fine).  The v4 bases still fit
     the v5 pegs; the groove-less v5 base is only slightly stronger.
  2. "The walls of the power board are far too weak; we don't need this tiny thin tray anymore."
       - front and rear walls 1.0 -> 2.4 (outward: the board and its end gaps are unchanged),
       - floor 1.6 -> 2.4 (thickened DOWNWARD: floor top, standoffs and board height are unchanged),
       - four 45 degree root gussets (2 x 2) along the inside of every wall,
       - four 2.5 square corner blocks (the front corners are where it tore),
       - a web from each board post to the side wall beside it.
     The side walls stay 1.0: the tub is only 0.1 inside the rails, and the tray has to lift out past them.
  4. Jim, later: the long arm beside the mast was too thick.  Its top comes down evenly from Z 40 to Z 34 (20 tall -> 14), same width,
     same outline; a 45 degree ramp joins it to the full-height taper.  The root block, taper, flare and post are untouched.
  3. Arms: EXACTLY the v3 arm again (Jim, 2026-10-03: the v4 'lighter arms' pass turned the arm into a V; he only wanted ceiling
     clearance and feet into a base, not an arm redesign).  The check below proves the arm webs, flares and taper match v3.
  Everything else (board position, 4.5 posts, pegs, base geometry) is as v4.
        Cells stand NEGLIGIBLY over the holder rim (Jim).  Modelled 0.5 as a conservative stand-in.
        The master BatteryCells value was corrected to match (commit e289c8e).

Pack leads leave the rear of the pack and run over the mast base, so nothing below/beside the arms
is filled, as in v3.
"""
import json
import shutil
import sys
from pathlib import Path

import FreeCAD as App
import MeshPart
import Part

V = App.Vector
ROOT = Path('/home/buralien/projects/gladiator-cad')
MASTER = ROOT / 'cad/master/Gladiator_Master.FCStd'
V3 = ROOT / 'cad/power-board/v3-cradle/PowerBoardTray_v3.FCStd'
V4 = ROOT / 'cad/power-board/v4-tray/PowerBoardTray_v4.FCStd'
OUT = ROOT / 'cad/power-board/v5-tray'
INCOMING = Path('/home/buralien/3D-Printer/Incoming/Gladiator')
(OUT / 'stl').mkdir(parents=True, exist_ok=True)
INCOMING.mkdir(parents=True, exist_ok=True)
N_TRAY = 'Gladiator_PowerTray_v5_print-on-rear-face.stl'
N_BASE_L = 'Gladiator_PowerTray_v5_BaseLeft_print-tab-down.stl'
N_BASE_R = 'Gladiator_PowerTray_v5_BaseRight_print-tab-down.stl'
N_COUPON = 'Gladiator_PowerTray_v5_FitCoupon_base-and-peg.stl'

FAILS = []


def p(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n'); sys.stdout.flush()


def check(ok, msg):
    p(('PASS ' if ok else 'FAIL ') + msg)
    if not ok:
        FAILS.append(msg)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def prism(points, z0, z1):
    w = [V(x, y, z0) for x, y in points]
    return Part.Face(Part.makePolygon(w + [w[0]])).extrude(V(0, 0, z1 - z0))


def mx(x):          # mirror about the deck centreline
    return 79.0 - x


def hit(a, b):
    if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    return a.common(b).Volume


def fine_mesh(shape):
    return MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.01, AngularDeflection=0.05, Relative=False)


# ---------------------------------------------------------------- board (unchanged)
BOARD_X0, BOARD_Y0 = 19.5, 29.0
BOARD_W, BOARD_L, PCB_T = 40.0, 60.0, 1.6
HOLE_DX, HOLE_DY = 34.5, 54.25
board_holes = [(BOARD_X0 + (BOARD_W - HOLE_DX) / 2 + ix * HOLE_DX,
                BOARD_Y0 + (BOARD_L - HOLE_DY) / 2 + iy * HOLE_DY) for ix in (0, 1) for iy in (0, 1)]

# ---------------------------------------------------------------- v5 heights and walls
HOLDER_TOP = 21.5
CELL_ABOVE_HOLDER = 0.5                 # Jim: "negligibly over the rim"; 0.5 is a conservative stand-in
CELL_TOP = HOLDER_TOP + CELL_ABOVE_HOLDER
CELL_GAP = 1.0
FLOOR_TOP = 26.5 - 1.8 + 1.6            # 26.3, unchanged from v4, so the standoffs and the board stay exactly where they were
FLOOR_T = 2.4                           # v4 1.6; thickened DOWNWARD, so the underside is now 23.9 (1.9 over the modelled cells)
FLOOR_Z = FLOOR_TOP - FLOOR_T
STANDOFF_H = 4.5                        # v3 7.0 (Jim: 7 -> 4.5)
BOARD_Z = FLOOR_TOP + STANDOFF_H        # 30.8 (v3 35.1)
WALL_TOP = BOARD_Z + PCB_T + 1.0
TOP = 40.0
ARM_Z0 = 20.0
ARM_INNER = 29.1                        # exactly the v3 arm (Jim: no redesign of the arm)
WEB_TOP = 34.0                          # Jim 2026-10-03: the long arm beside the mast is too thick -> lower its top, keep its width (was 40)
RAMP = (104.0, 110.0)                   # 45 degree ramp from the full-height taper down to WEB_TOP, so the step prints without support
M2_PILOT, M2_CLEAR = 1.6, 2.2
M3_CLEAR = 3.4                          # base slit bolts are M3 now (Jim: they fit the slit better)
M3_HEAD_R = 3.0                          # pan or button head, d6; a d5.5 socket head is smaller
BOARD_PILOT_DEPTH = 4.0
SIDE_T = 1.0                            # side walls cannot grow outward: the tub is 0.1 inside the rails and must lift out past them
FRONT_T = REAR_T = 2.4                  # v4 1.0, grown outward
GUSSET = 2.0                            # 45 degree root gusset legs along the inside of every wall
CORNER = 2.5                            # inside corner blocks, full wall height
WEB_T = 2.0                             # post to side wall webs
SIDE_GAP = 0.4
END_GAP = 0.4 + 2.5

slot_anchors = [(25.5, 130.5), (53.5, 130.5)]

# ---------------------------------------------------------------- snap-in rear mount (left side, mirrored for right)
TAB_Z0, TAB_TOP = 2.2, 5.2              # base tab thickness unchanged
PEG_X = (30.3, 33.3)                    # 3.0 (post was 28.7-32.7).  Moved inboard so the M3 head clears the socket wall
PEG_Y = (128.85, 136.95)                # 8.1  (post was 127.4-136.5)
CLR = 0.25
POCK_X = (PEG_X[0] - CLR, PEG_X[1] + CLR)
POCK_Y = (PEG_Y[0] - CLR, PEG_Y[1] + CLR)
WALL_IN_T, WALL_REAR_T = 2.4, 2.0       # strengthened 2026-10-01 (were 1.6 and 1.6); bolt side stays 1.2 (M3 head)
BASE_X = (18.4, POCK_X[1] + WALL_IN_T)  # 35.95
BASE_Y = (127.4, POCK_Y[1] + WALL_REAR_T)   # front edge 127.4: the mast base flange ends at Y 127; rear 139.2
TAB_EXT_X, TAB_EXT_Y = 38.0, 139.9      # tab runs beyond the walls inboard and rear so the walls can be filleted into it
ROOT_FILLET = 1.8
WALL_OUT_X = POCK_X[0] - 1.2            # 28.85: bolt X 25.5 + head r 3.0 + 0.35
SOCK_TOP = 17.2
PEG_Z0 = 6.2                            # 1.0 above the socket floor; the arms bear on the collar, not the pegs
SHOULDER_Z0 = 18.0                      # 0.8 above the socket top
PEG_CHAMFER = 0.6
PEG_MID_X = sum(PEG_X) / 2.0


def side_func(side):
    return (lambda x: x) if side == 0 else mx


def make_peg_box(f):
    a, b = sorted((f(PEG_X[0]), f(PEG_X[1])))
    pg = box(a, b, PEG_Y[0], PEG_Y[1], PEG_Z0, SHOULDER_Z0 + 0.5)
    es = [e for e in pg.Edges if abs(e.BoundBox.ZMin - PEG_Z0) < 1e-6 and abs(e.BoundBox.ZMax - PEG_Z0) < 1e-6]
    return pg.makeChamfer(PEG_CHAMFER, es)


def peg_root_fillet(shape, f, r=0.7):
    a, b_ = sorted((f(PEG_X[0]), f(PEG_X[1])))
    es = [e for e in shape.Edges if abs(e.BoundBox.ZMin - SHOULDER_Z0) < 1e-6 and abs(e.BoundBox.ZMax - SHOULDER_Z0) < 1e-6
          and e.BoundBox.XMin > a - 0.01 and e.BoundBox.XMax < b_ + 0.01
          and e.BoundBox.YMin > PEG_Y[0] - 0.01 and e.BoundBox.YMax < PEG_Y[1] + 0.01]
    if not es:
        p('INFO peg root fillet: no edges found'); return shape
    try:
        out = shape.makeFillet(r, es)
        if out.isValid() and len(out.Solids) == 1:
            p('INFO peg root fillet r%.1f on %d edges' % (r, len(es))); return out
    except Exception as ex:
        p('INFO peg root fillet skipped:', ex)
    return shape


def make_base_left():
    b = box(BASE_X[0], TAB_EXT_X, BASE_Y[0], TAB_EXT_Y, TAB_Z0, TAB_TOP)
    b = b.fuse(box(WALL_OUT_X, BASE_X[1], BASE_Y[0], BASE_Y[1], TAB_TOP, SOCK_TOP))
    b = b.removeSplitter()
    for nm, axis, pos, rr in (('inboard', 'x', BASE_X[1], ROOT_FILLET), ('rear', 'y', BASE_Y[1], 0.6)):
        es = [e for e in b.Edges if abs(e.BoundBox.ZMin - TAB_TOP) < 1e-6 and abs(e.BoundBox.ZMax - TAB_TOP) < 1e-6 and
              ((axis == 'x' and abs(e.BoundBox.XMin - pos) < 1e-6 and abs(e.BoundBox.XMax - pos) < 1e-6 and e.BoundBox.YLength > 5) or
               (axis == 'y' and abs(e.BoundBox.YMin - pos) < 1e-6 and abs(e.BoundBox.YMax - pos) < 1e-6 and e.BoundBox.XLength > 5))]
        try:
            nb = b.makeFillet(rr, es) if es else b
            if nb.isValid() and len(nb.Solids) == 1:
                b = nb; p('INFO base %s root fillet r%.1f on %d edge(s)' % (nm, rr, len(es)))
        except Exception as ex:
            p('INFO base %s root fillet skipped:' % nm, ex)
    # rib on the bolt-side wall (kept from v4, now just extra stiffness): it starts above the M3 head (Z 8.2) and stays
    # 0.05 clear of the d5 driver path, so it needs no support when printed tab-down.
    rib_pts = [(WALL_OUT_X, 9.0), (WALL_OUT_X - 0.8, 12.0), (WALL_OUT_X - 0.8, SOCK_TOP), (WALL_OUT_X, SOCK_TOP)]
    rw = [V(x, 130.0, z) for x, z in rib_pts]
    b = b.fuse(Part.Face(Part.makePolygon(rw + [rw[0]])).extrude(V(0, 6.0, 0))).removeSplitter()
    b = b.cut(box(POCK_X[0], POCK_X[1], POCK_Y[0], POCK_Y[1], TAB_TOP, SOCK_TOP + 1.0))
    x, y = slot_anchors[0]
    b = b.cut(Part.makeCylinder(M3_CLEAR / 2, TAB_TOP - TAB_Z0 + 0.2, V(x, y, TAB_Z0 - 0.1)))
    b = b.removeSplitter()
    try:                                # lead-in on the pocket mouth
        es = [e for e in b.Edges if abs(e.BoundBox.ZMin - SOCK_TOP) < 1e-6 and abs(e.BoundBox.ZMax - SOCK_TOP) < 1e-6
              and e.BoundBox.XMin > POCK_X[0] - 1e-6 and e.BoundBox.XMax < POCK_X[1] + 1e-6
              and e.BoundBox.YMin > POCK_Y[0] - 1e-6 and e.BoundBox.YMax < POCK_Y[1] + 1e-6]
        if len(es) == 4:
            b = b.makeChamfer(0.5, es)
    except Exception as ex:
        p('INFO pocket lead-in chamfer skipped:', ex)
    return b


# ---------------------------------------------------------------- tub
ix0, ix1 = BOARD_X0 - SIDE_GAP, BOARD_X0 + BOARD_W + SIDE_GAP
iy0, iy1 = BOARD_Y0 - END_GAP, BOARD_Y0 + BOARD_L + END_GAP
ox0, ox1, oy0, oy1 = ix0 - SIDE_T, ix1 + SIDE_T, iy0 - FRONT_T, iy1 + REAR_T
tray = box(ox0, ox1, oy0, oy1, FLOOR_Z, FLOOR_TOP)
tray = tray.fuse(box(ox0, ox1, oy0, oy1, FLOOR_TOP, WALL_TOP).cut(
    box(ix0, ix1, iy0, iy1, FLOOR_Z, WALL_TOP + 1)))


def tri_xz(pts, y0, y1):
    w = [V(x, y0, z) for x, z in pts]
    return Part.Face(Part.makePolygon(w + [w[0]])).extrude(V(0, y1 - y0, 0))


def tri_yz(pts, x0, x1):
    w = [V(x0, y, z) for y, z in pts]
    return Part.Face(Part.makePolygon(w + [w[0]])).extrude(V(x1 - x0, 0, 0))


G = GUSSET
tray = tray.fuse(tri_xz([(ix0, FLOOR_TOP), (ix0 + G, FLOOR_TOP), (ix0, FLOOR_TOP + G)], iy0, iy1))
tray = tray.fuse(tri_xz([(ix1, FLOOR_TOP), (ix1 - G, FLOOR_TOP), (ix1, FLOOR_TOP + G)], iy0, iy1))
tray = tray.fuse(tri_yz([(iy0, FLOOR_TOP), (iy0 + G, FLOOR_TOP), (iy0, FLOOR_TOP + G)], ix0, ix1))
tray = tray.fuse(tri_yz([(iy1, FLOOR_TOP), (iy1 - G, FLOOR_TOP), (iy1, FLOOR_TOP + G)], ix0, ix1))
for xa, xb in ((ix0, ix0 + CORNER), (ix1 - CORNER, ix1)):
    for ya, yb in ((iy0, iy0 + CORNER), (iy1 - CORNER, iy1)):
        tray = tray.fuse(box(xa, xb, ya, yb, FLOOR_TOP, WALL_TOP))
for x, y in board_holes:
    tray = tray.fuse(Part.makeCylinder(3.0, STANDOFF_H, V(x, y, FLOOR_TOP)))
    wx = ix0 if x < 39.5 else ix1
    xa, xb = sorted((wx, x))
    tray = tray.fuse(box(xa, xb, y - WEB_T / 2, y + WEB_T / 2, FLOOR_TOP, BOARD_Z - 0.2))   # post to side wall web, 0.2 under the board

left_flare = [(25.0, 123.0), (29.1, 123.0), (32.7, 127.4), (32.7, 134.0), (28.7, 134.0), (28.7, 128.5), (25.0, 126.0)]
for side in (0, 1):
    f = side_func(side)

    def B(x0, x1, y0, y1, z0, z1):
        a, b = sorted((f(x0), f(x1)))
        return box(a, b, y0, y1, z0, z1)

    parts = [
        B(22.0, 32.1, oy1 - 1.0, 100.0, FLOOR_Z, TOP),
        B(24.0, 30.1, 100.0, 104.0, FLOOR_Z, TOP),
        B(25.0, ARM_INNER, 100.0, 127.0, ARM_Z0, WEB_TOP),
        B(25.0, ARM_INNER, 123.0, 127.0, ARM_Z0, TOP),          # full height again where the arm runs into the flare, as v3
        tri_yz([(RAMP[0], WEB_TOP - 0.01), (RAMP[0], TOP), (RAMP[1], WEB_TOP - 0.01)], *sorted((f(25.0), f(ARM_INNER)))),
        B(28.7, PEG_X[1], 127.4, PEG_Y[1], SHOULDER_Z0, TOP),   # shoulder: the full-size post, above the socket
        make_peg_box(f),                                    # the plug-in peg, 1 mm smaller
        prism([(f(x), y) for x, y in left_flare], ARM_Z0, TOP),
    ]
    for s in parts:
        tray = tray.fuse(s)
tray = tray.removeSplitter()
for side in (0, 1):
    tray = peg_root_fillet(tray, side_func(side))
for x, y in board_holes:
    tray = tray.cut(Part.makeCylinder(M2_PILOT / 2, BOARD_PILOT_DEPTH + 0.1, V(x, y, BOARD_Z - BOARD_PILOT_DEPTH)))
tray = tray.removeSplitter()
tray_core = tray                                        # v5 has no click bumps: this is the tray

base_l = make_base_left()
base_r = base_l.mirror(V(39.5, 0, 0), V(1, 0, 0))

# ================================================================ checks
master = App.openDocument(str(MASTER))
O = master.getObject
v3doc = App.openDocument(str(V3))
v3 = v3doc.getObject('PowerBoardTray').Shape
v4doc = App.openDocument(str(V4))
v4 = v4doc.getObject('PowerBoardTray').Shape
pcb_env = box(BOARD_X0, BOARD_X0 + BOARD_W, BOARD_Y0, BOARD_Y0 + BOARD_L, BOARD_Z, BOARD_Z + PCB_T)
cells = box(0.0, 79.0, 21.0, 96.5, HOLDER_TOP, CELL_TOP)        # modelled from CELL_ABOVE_HOLDER, master untouched

check(tray.isValid() and len(tray.Solids) == 1, 'tray is one valid solid (%.2f cm3, v4 %.2f, v3 %.2f)' % (tray.Volume / 1000, v4.Volume / 1000, v3.Volume / 1000))
check(hit(tray, pcb_env) < 1e-6, 'the board volume (X %.1f-%.1f, Y %.1f-%.1f, Z %.1f-%.1f) is clear of every wall, gusset, web and post' % (
    BOARD_X0, BOARD_X0 + BOARD_W, BOARD_Y0, BOARD_Y0 + BOARD_L, BOARD_Z, BOARD_Z + PCB_T))
under = box(BOARD_X0, BOARD_X0 + BOARD_W, BOARD_Y0, BOARD_Y0 + BOARD_L, FLOOR_TOP, BOARD_Z)
p('INFO under the board: %.0f of %.0f mm3 is plastic (posts, webs, wall gussets); the rest is free for solder tails (%.1f tall)' % (
    hit(tray, under), under.Volume, STANDOFF_H))
mid = box(BOARD_X0 + 6.0, BOARD_X0 + BOARD_W - 6.0, BOARD_Y0 + 6.0, BOARD_Y0 + BOARD_L - 6.0, FLOOR_TOP, BOARD_Z)
check(hit(tray, mid) < 1e-6, 'the middle under the board (6 in from every edge, clear of the posts) is free for solder tails')
check(base_l.isValid() and len(base_l.Solids) == 1 and base_r.isValid() and len(base_r.Solids) == 1,
      'each base is one valid solid (%.2f cm3 each)' % (base_l.Volume / 1000))

obstacles = ['ChassisDeck', 'BatteryBox', 'MastBase', 'MastTube', 'SideRailLeft', 'SideRailRight',
             'UpperDeck', 'AntennaPost', 'S3Board', 'Breadboard', 'DriverMountLeft', 'DriverMountRight',
             'DrvV5_Base_L', 'DrvV5_Wedge_L', 'DrvV5_Base_R', 'DrvV5_Wedge_R',
             'DrvV5_Board_L', 'DrvV5_Fins_L', 'DrvV5_Board_R', 'DrvV5_Fins_R']
clash = {n: round(hit(tray, O(n).Shape), 3) for n in obstacles if O(n)}
clash = {k: v for k, v in clash.items() if v > 0.01}
check(not clash, 'tray: no clashes with %d master solids %s' % (len(obstacles), clash))
clash_b = {}
for nm, b in (('base L', base_l), ('base R', base_r)):
    for n in obstacles:
        if O(n):
            v = hit(b, O(n).Shape)
            if v > 0.01:
                clash_b[nm + ' / ' + n] = round(v, 3)
check(not clash_b, 'bases: no clashes with the master solids %s' % clash_b)
check(hit(tray, cells) < 1e-6, 'tray clears the modelled cells (top %.1f)' % CELL_TOP)
gaps = {n: round(tray.distToShape(O(n).Shape)[0], 2) for n in
        ('MastTube', 'MastBase', 'SideRailLeft', 'SideRailRight', 'UpperDeck', 'ChassisDeck')}
gaps['cells (modelled %.1f above holder)' % CELL_ABOVE_HOLDER] = round(tray.distToShape(cells)[0], 2)
p('INFO clearances', gaps)
check(tray.distToShape(cells)[0] >= CELL_GAP - 0.01, 'floor (now 2.4 thick, underside %.1f) clears the modelled cells by %.2f' % (FLOOR_Z, tray.distToShape(cells)[0]))
check(gaps['MastTube'] >= 0.39, 'arms clear the mast tube by %.2f, as v3' % gaps['MastTube'])
p('INFO master BatteryCells still says 4 above the holder; Jim reports cells are negligibly over the rim, so the master value is stale.')

# tray <-> base fit
d_fit = tray_core.distToShape(base_l)[0]
check(d_fit >= 0.2, 'peg (with its root fillet) to socket clearance %.3f (design %.2f); no bumps, no grooves' % (d_fit, CLR))
check(hit(tray, base_l) + hit(tray, base_r) < 1e-6, 'installed: nothing overlaps')
check(PEG_Z0 - TAB_TOP >= 0.99,
      'peg bottom is %.1f above the socket floor (the arms bear on the collar)' % (PEG_Z0 - TAB_TOP))
check(SHOULDER_Z0 - SOCK_TOP >= 0.79, 'shoulder is %.1f above the socket top; peg engaged %.1f' % (SHOULDER_Z0 - SOCK_TOP, SOCK_TOP - PEG_Z0))

# arms rest on the collar rim
mb = O('MastBase').Shape
contact = 0.0
for side in (0, 1):
    xs = sorted((25.0, 29.1)) if side == 0 else sorted((mx(29.1), mx(25.0)))
    film = box(xs[0], xs[1], 100.0, 127.0, ARM_Z0 - 0.1, ARM_Z0)
    contact += hit(film, mb) / 0.1
check(contact > 20.0, 'arms bear on the mast collar rim (%.1f mm2 total)' % contact)

# open wire space at both board ends
for nm, y0, y1 in (('front', iy0, BOARD_Y0 - 0.2), ('rear', BOARD_Y0 + BOARD_L + 0.2, iy1)):
    v = hit(tray, box(ix0 + CORNER + 0.1, ix1 - CORNER - 0.1, y0 + 0.01, y1 - 0.01, FLOOR_TOP + GUSSET + 0.1, WALL_TOP + 5))
    check(v < 1e-6, '%s end wire space %.1f x %.1f is open above the %.0f gusset and between the corner blocks' % (nm, y1 - y0, ix1 - ix0 - 2 * CORNER, GUSSET))

# lead lanes over the mast base stay open (tray AND bases)
lanes = {
    'left outboard lane X18.2-21.9': box(18.2, 21.9, oy1 + 0.1, 127.0, 2.1, 54.0),
    'right outboard lane': box(mx(21.9), mx(18.2), oy1 + 0.1, 127.0, 2.1, 54.0),
    'centre gap in front of mast': box(32.2, 46.8, oy1 + 0.1, 102.9, 2.1, 54.0),
    'below the arms (Z<20) over the mast base': box(18.2, 60.8, 96.6, 127.3, 2.1, 19.99),
}
for nm, b in lanes.items():
    check(hit(tray, b) + hit(base_l, b) + hit(base_r, b) < 1e-6, 'kept open: %s' % nm)
grew = tray_core.cut(v3)
below = hit(grew, box(0, 79, 93.0, 127.3, 0, ARM_Z0 - 0.01))
check(below < 1e-6, 'no v5 growth below Z 20 over the mast base (%.3f mm3)' % below)

# service
deck = O('ChassisDeck').Shape
for x, y in slot_anchors:
    check(hit(Part.makeCylinder(1.5, 3.0, V(x, y, -0.5)), deck) < 1e-6, 'M3 shank at (%.1f, %.1f) passes the deck slit' % (x, y))
    base = base_l if x < 39.5 else base_r
    ring = Part.makeCylinder(M3_HEAD_R, 0.3, V(x, y, TAB_TOP - 0.3)).cut(Part.makeCylinder(M3_CLEAR / 2 + 0.01, 0.5, V(x, y, TAB_TOP - 0.4)))
    check(hit(ring, base) / 0.3 > 17.0, 'bolt head bearing at (%.1f, %.1f) %.1f mm2' % (x, y, hit(ring, base) / 0.3))
    drv = Part.makeCylinder(2.5, 54.0 - TAB_TOP - 0.1, V(x, y, TAB_TOP + 0.1))
    check(hit(drv, tray) + hit(drv, base_l) + hit(drv, base_r) < 1e-6,
          'bolt at (%.1f, %.1f) can be tightened with the tray seated (d5 driver path clear)' % (x, y))
pin_l = Part.makeCylinder(3.0, 26.0, V(0, 113, 13), V(1, 0, 0))
pin_r = Part.makeCylinder(3.0, 26.5, V(52.5, 113, 13), V(1, 0, 0))
check(hit(pin_l, tray) + hit(pin_r, tray) < 1e-6, 'mast cross pin reachable from both sides with the tray on')
for x in (17.8, 61.2):
    check(hit(Part.makeCylinder(2.0, 30.0, V(x, 111, 6.0)), tray) < 1e-6, 'mast base M2 at X %.1f untouched' % x)
for x, y in board_holes:
    shell = Part.makeCylinder(3.0, BOARD_PILOT_DEPTH - 0.2, V(x, y, BOARD_Z - BOARD_PILOT_DEPTH)).cut(
        Part.makeCylinder(M2_PILOT / 2, BOARD_PILOT_DEPTH, V(x, y, BOARD_Z - BOARD_PILOT_DEPTH - 0.1)))
    check(hit(shell, tray) > 60.0, 'board screw post (%.2f, %.2f) intact, pilot blind above the floor' % (x, y))
    check(hit(Part.makeCylinder(M2_PILOT / 2 - 0.01, FLOOR_T, V(x, y, FLOOR_Z)), tray) > 0, 'floor solid under pilot (%.2f, %.2f)' % (x, y))
    wx = ix0 if x < 39.5 else ix1
    check(hit(box(min(wx, x) + 0.3, max(wx, x) - 0.3, y - 0.5, y + 0.5, FLOOR_TOP + 0.5, BOARD_Z - 0.4), tray) > 5.0,
          'post (%.2f, %.2f) is tied to the side wall by a web' % (x, y))

# drop-on and lift-out with the bases fixed to the deck
fixed = [O(n).Shape for n in ('MastTube', 'MastBase', 'SideRailLeft', 'SideRailRight', 'BatteryBox', 'ChassisDeck')] + [cells, base_l, base_r]
worst = 0.0
for i in range(1, 81):
    t = tray_core.copy(); t.translate(V(0, 0, 0.5 * i))
    worst = max(worst, max(hit(t, s) for s in fixed))
check(worst < 1e-6, 'tray lifts straight out and drops straight back in over 40 mm with the mast tube fitted (worst %.3f)' % worst)
worst_m = 0.0
for dx, dy in ((0.2, 0.2), (-0.2, 0.2), (0.2, -0.2), (-0.2, -0.2)):
    for i in range(1, 25):
        t = tray_core.copy(); t.translate(V(dx, dy, 0.5 * i))
        worst_m = max(worst_m, hit(t, base_l), hit(t, base_r))
check(worst_m < 1e-6, 'pegs still enter the sockets 0.2 off in X and Y (worst %.3f)' % worst_m)

# strength comparison against v3
def section(shape, y, x0, x1):
    s = shape.common(box(x0, x1, y - 0.05, y + 0.05, 0, 60))
    if s.Volume <= 0:
        return 0.0, 0.0
    return s.Volume / 0.1, s.BoundBox.ZLength

rows = {}
for nm, y, xa, xb in (('arm beside mast Y115', 115.0, 18, 39.5), ('arm Y105', 105.0, 18, 39.5),
                      ('root Y96', 96.0, 18, 39.5), ('flare Y125', 125.0, 18, 39.5)):
    a3, h3 = section(v3, y, xa, xb)
    a4, h4 = section(tray, y, xa, xb)
    rows[nm] = {'v3_area_mm2': round(a3, 1), 'v3_depth': round(h3, 1), 'v5_area_mm2': round(a4, 1), 'v5_depth': round(h4, 1)}
    p('INFO section %-22s v3 %6.1f mm2 (depth %4.1f)  v5 %6.1f mm2 (depth %4.1f)' % (nm, a3, h3, a4, h4))
    if nm == 'arm beside mast Y115':
        check(abs(h4 - (WEB_TOP - ARM_Z0)) < 0.05 and a4 > 50.0, '%s lowered to Z %.0f as asked: %.1f mm2 (v3 %.1f), depth %.1f' % (nm, WEB_TOP, a4, a3, h4))
    elif nm == 'arm Y105':
        check(a4 >= 0.9 * a3, '%s is on the ramp up to the taper: %.1f mm2 (v3 %.1f), depth %.1f' % (nm, a4, a3, h4))
    else:
        check(a4 >= a3 - 0.5, '%s not weaker than v3' % nm)
for nm, (xa, xb, ya, yb) in (('front wall', (30, 49, oy0 + 0.5, oy0 + 0.6)), ('rear wall', (30, 49, oy1 - 0.6, oy1 - 0.5))):
    p('INFO %s: %.1f thick, %.1f deep (v4 1.0 x 8.7)' % (nm, FRONT_T, WALL_TOP - FLOOR_Z))
for nm_, xa_, xb_ in (('left', 23.9, 33.0), ('right', 79.0 - 33.0, 79.0 - 23.9)):
    for part_, y0_, y1_ in (('taper', 100.0, 104.0), ('flare', 123.0, 127.0)):
        zone = box(xa_, xb_, y0_, y1_, 26.5, TOP)             # v3 floor underside up
        diff = tray.common(zone).cut(v3.common(zone)).Volume + v3.common(zone).cut(tray.common(zone)).Volume
        check(diff < 1.0, '%s %s is identical to v3: %.2f mm3 different' % (nm_, part_, diff))
    web = box(xa_, xb_, 104.0, 123.0, ARM_Z0, TOP + 1)
    added = tray.common(web).cut(v3).Volume
    check(added < 0.5, '%s long arm was only lowered, nothing added: %.2f mm3 outside the v3 arm' % (nm_, added))
    check(hit(tray, box(xa_, xb_, RAMP[1] + 0.05, 122.95, WEB_TOP + 0.05, TOP + 1)) < 1e-6,
          '%s long arm top is Z %.0f from Y %.0f to the flare' % (nm_, WEB_TOP, RAMP[1]))
peg_a = tray_core.common(box(0, 79, 132.0 - 0.05, 132.0 + 0.05, 8.0, 15.0))
p('INFO peg section at Y132, Z8-15 (both pegs): %.1f mm2 (v3 post %.1f)' % (peg_a.Volume / 0.1,
  v3.common(box(0, 79, 132.0 - 0.05, 132.0 + 0.05, 8.0, 15.0)).Volume / 0.1))

if FAILS:
    p('REFUSING TO EXPORT: %d failed' % len(FAILS))
    for f_ in FAILS:
        p('  -', f_)
    sys.exit(2)

# ================================================================ outputs
doc = App.newDocument('PowerBoardTray_v5')
objs = []
for nm, lab, sh in (('PowerBoardTray', 'Power board tray v5 - thick walls, plain pegs, lifts out of the bases', tray),
                    ('BaseLeft', 'Base, left (plain well)', base_l), ('BaseRight', 'Base, right (plain well)', base_r)):
    o = doc.addObject('Part::Feature', nm); o.Label = lab; o.Shape = sh; objs.append(o)
brd = box(BOARD_X0, BOARD_X0 + BOARD_W, BOARD_Y0, BOARD_Y0 + BOARD_L, BOARD_Z, BOARD_Z + PCB_T)
for x, y in board_holes:
    brd = brd.cut(Part.makeCylinder(M2_CLEAR / 2, PCB_T + 0.2, V(x, y, BOARD_Z - 0.1)))
o = doc.addObject('Part::Feature', 'BoardReference'); o.Label = 'Power board reference'; o.Shape = brd
doc.recompute()
doc.saveAs(str(OUT / 'PowerBoardTray_v5.FCStd'))
Part.export(objs, str(OUT / 'PowerBoardTray_v5.step'))
fine_mesh(tray).write(str(OUT / 'stl/PowerBoardTray_v5_installed.stl'))


def to_bed(shape):
    s = shape.copy(); bb = s.BoundBox
    s.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
    return s


def tray_orient(shape):
    s = shape.copy()
    s.rotate(V(0, 0, 0), V(1, 0, 0), -90.0)         # rear face (Y max) onto the bed, as v2/v3
    return to_bed(s)


def mesh_ok(pm, vol, label, maxdim=220):
    ok = (pm.isSolid() and not pm.hasNonManifolds() and not pm.hasSelfIntersections() and abs(pm.BoundBox.ZMin) < 1e-6
          and abs(pm.Volume - vol) / vol < 0.005 and max(pm.BoundBox.XLength, pm.BoundBox.YLength) < maxdim)
    check(ok, '%s print mesh solid / manifold / on bed / volume %s' % (label, pm.BoundBox))


ps = tray_orient(tray)
pm_tray = fine_mesh(ps); mesh_ok(pm_tray, tray.Volume, 'tray')
pb_l = to_bed(base_l); pm_bl = fine_mesh(pb_l); mesh_ok(pm_bl, base_l.Volume, 'base L')
pb_r = to_bed(base_r); pm_br = fine_mesh(pb_r); mesh_ok(pm_br, base_r.Volume, 'base R')

# fit coupon: the real left base plus the peg and a short shoulder stub, printed in the tray's own orientation
stub = box(28.7, PEG_X[1], 127.4, PEG_Y[1], SHOULDER_Z0, SHOULDER_Z0 + 6.0).fuse(make_peg_box(side_func(0)))
stub = stub.cut(box(0, 79, 0, 200, SHOULDER_Z0 + 6.0, 80)).removeSplitter()
stub = peg_root_fillet(stub, side_func(0))
pstub = tray_orient(stub)
pstub.translate(V(pb_l.BoundBox.XLength + 8.0, 0, 0))
coupon = Part.makeCompound([pb_l, pstub])
pm_cpn = fine_mesh(coupon)
check(pm_cpn.isSolid() and not pm_cpn.hasNonManifolds() and abs(pm_cpn.BoundBox.ZMin) < 1e-6, 'fit coupon mesh solid / on bed %s' % pm_cpn.BoundBox)

bed = sum(f.Area for f in ps.Faces if f.Surface.TypeId == 'Part::GeomPlane' and abs(f.BoundBox.ZMax) < 1e-6)
down = sum(f.Area for f in ps.Faces if f.BoundBox.ZMin > 0.01 and f.Surface.TypeId == 'Part::GeomPlane' and f.normalAt(0, 0).z < -0.7)
p('INFO tray print: bbox %.1f x %.1f x %.1f, bed contact %.0f mm2, downward flat faces off the bed %.0f mm2 (bridges/ledges)'
  % (pm_tray.BoundBox.XLength, pm_tray.BoundBox.YLength, pm_tray.BoundBox.ZLength, bed, down))
if FAILS:
    sys.exit(3)
for mesh, nm in ((pm_tray, N_TRAY), (pm_bl, N_BASE_L), (pm_br, N_BASE_R), (pm_cpn, N_COUPON)):
    mesh.write(str(OUT / 'stl' / nm))
    shutil.copy2(OUT / 'stl' / nm, INCOMING / nm)

# preview data (plotted separately)
def wires(shape, axis, pos):
    out = []
    for w in shape.slice(axis, pos):
        out.append([[round(q.x, 3), round(q.y, 3), round(q.z, 3)] for q in w.discretize(Deflection=0.05)])
    return out

prev = {}
for key, x in (('x31', 31.2), ('x27', 27.5)):
    prev[key] = {n: wires(s, V(1, 0, 0), x) for n, s in (('tray', tray), ('base', base_l), ('cells', cells),
                                                           ('mastbase', mb), ('deck', deck))}
for key, z in (('z10', 10.0), ('z30', 30.0)):
    prev[key] = {n: wires(s, V(0, 0, 1), z) for n, s in (('tray', tray), ('base_l', base_l), ('base_r', base_r),
                                                           ('mastbase', mb), ('rail_l', O('SideRailLeft').Shape),
                                                           ('rail_r', O('SideRailRight').Shape), ('deck', deck))}
json.dump(prev, open('/tmp/v5_preview.json', 'w'))

val = {'script': 'scripts/build_power_tray_v5.py', 'tray_volume_cm3': round(tray.Volume / 1000, 2),
       'tray_pla_g_solid': round(tray.Volume * 1.24e-3, 1), 'base_volume_cm3_each': round(base_l.Volume / 1000, 2),
       'v3_volume_cm3': round(v3.Volume / 1000, 2), 'v4_volume_cm3': round(v4.Volume / 1000, 2),
       'front_wall_outer_y': oy0, 'rear_wall_outer_y': oy1, 'inner_xy': [ix0, ix1, iy0, iy1], 'corner_block': CORNER, 'gusset': GUSSET,
       'floor_top': FLOOR_TOP, 'wall_t': {'side': SIDE_T, 'front': FRONT_T, 'rear': REAR_T, 'floor': FLOOR_T},
       'cell_above_holder_modelled_negligible': CELL_ABOVE_HOLDER, 'cell_gap': CELL_GAP,
       'floor_z': [FLOOR_Z, FLOOR_TOP], 'board_z': [BOARD_Z, BOARD_Z + PCB_T], 'wall_top': WALL_TOP,
       'standoff_h': STANDOFF_H, 'board_drop_vs_v3_mm': round(35.1 - BOARD_Z, 2), 'arm_top': TOP,
       'connector_room_to_upper_deck_mm': round(54.5 - (BOARD_Z + PCB_T), 1), 'v3_connector_room_mm': 17.8,
       'board_holes': board_holes, 'deck_fixings': slot_anchors,
       'peg': {'x': PEG_X, 'y': PEG_Y, 'size': [PEG_X[1] - PEG_X[0], PEG_Y[1] - PEG_Y[0]], 'clearance': CLR,
               'engaged_mm': SOCK_TOP - PEG_Z0, 'detent': 'none, plain slide fit'},
       'base': {'x': BASE_X, 'y': BASE_Y, 'socket_top_z': SOCK_TOP, 'tab_z': [TAB_Z0, TAB_TOP]},
       'clearances_mm': gaps, 'collar_contact_mm2': round(contact, 1), 'sections': rows,
       'print': {'tray': N_TRAY, 'bases': [N_BASE_L, N_BASE_R], 'coupon': N_COUPON,
                 'tray_orientation': 'rear face down (as v2/v3)', 'bases_orientation': 'tab down',
                 'tray_bbox': [round(pm_tray.BoundBox.XLength, 1), round(pm_tray.BoundBox.YLength, 1), round(pm_tray.BoundBox.ZLength, 1)],
                 'tray_bed_contact_mm2': round(bed), 'tray_downward_faces_mm2': round(down)}}
json.dump(val, open(OUT / 'validation.json', 'w'), indent=1)
p('DONE', json.dumps(val['print']))
