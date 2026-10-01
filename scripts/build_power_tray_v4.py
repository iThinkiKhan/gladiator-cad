"""Build the Gladiator power-board tray v4 plus its snap-in rear base.  Standalone file; the
master is only read.  Refuses to export if any check fails.

Why v4 (Jim, 2026-10-01, once the real power board was built and he had the whole thing in hand):
  1. Battery change without unbolting the tray.  v3 bolted straight to the deck at two slits.  v4
     splits that: a printed BASE per side is bolted once to the same two slit bolts, and the tray
     lifts straight out of / drops straight into the bases.  Retention is a friction fit with a
     small click bump (a ridge on each peg face into a groove in the socket wall), no printed
     latch arms (v1's arms sheared off).
  2. Rear posts are now 1 mm smaller pegs (3.0 x 8.1, was 4 x 9.1) so the socket walls fit inside
     the old footprint.  The peg stands in a 0.25-clearance pocket; the full-size post is the
     shoulder above it.
  3. "We need height back".  Floor 1.8 closer to the cells, and the four board screw posts go from
     7 to 4.5 tall.  Together the board sits 4.3 lower than v3, which hands the room back above the
     board for connectors.
        Cells stand NEGLIGIBLY over the holder rim (Jim, measured by eye).  Modelled 0.5 as a conservative stand-in.
        The master BatteryCells (4 above the holder) is now known to be wrong; the master is not changed here.
  The INA module cassette is NOT in this build (module dimensions still wanted).

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
OUT = ROOT / 'cad/power-board/v4-tray'
INCOMING = Path('/home/buralien/3D-Printer/Incoming/Gladiator')
(OUT / 'stl').mkdir(parents=True, exist_ok=True)
INCOMING.mkdir(parents=True, exist_ok=True)
N_TRAY = 'Gladiator_PowerTray_v4_print-on-rear-face.stl'
N_BASE_L = 'Gladiator_PowerTray_v4_BaseLeft_print-tab-down.stl'
N_BASE_R = 'Gladiator_PowerTray_v4_BaseRight_print-tab-down.stl'
N_COUPON = 'Gladiator_PowerTray_v4_FitCoupon_base-and-peg.stl'

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

# ---------------------------------------------------------------- v4 heights
HOLDER_TOP = 21.5
CELL_ABOVE_HOLDER = 0.5                 # Jim: "negligibly over the rim"; 0.5 is a conservative stand-in
CELL_TOP = HOLDER_TOP + CELL_ABOVE_HOLDER
CELL_GAP = 1.0
FLOOR_Z = 26.5 - 1.8                  # 24.7: Jim asked for 1.8 closer than v3 (26.5); gap to the cells is then larger
FLOOR_T = 1.6
STANDOFF_H = 4.5                        # v3 7.0 (Jim: 7 -> 4.5)
BOARD_Z = FLOOR_Z + FLOOR_T + STANDOFF_H     # 30.8 (v3 35.1)
WALL_TOP = BOARD_Z + PCB_T + 1.0
TOP = 40.0
ARM_Z0 = 20.0
M2_PILOT, M2_CLEAR = 1.6, 2.2
M3_CLEAR = 3.4                          # base slit bolts are M3 now (Jim: they fit the slit better)
M3_HEAD_R = 3.0                          # pan or button head, d6; a d5.5 socket head is smaller
BOARD_PILOT_DEPTH = 4.0
WALL_T = 1.0
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
BUMP_Z = 11.7
BUMP_APEX, BUMP_HALF = 0.5, 0.6
GROOVE_APEX, GROOVE_HALF = 0.55, 0.85
BUMP_Y = (PEG_Y[0] + 1.0, PEG_Y[1] - 1.0)
GROOVE_Y = (BUMP_Y[0] - 0.3, BUMP_Y[1] + 0.3)
PEG_MID_X = sum(PEG_X) / 2.0


def ridge(f, x_in, x_face, x_apex, zc, hh, y0, y1):
    """Triangle ridge (bump) or groove cutter, extruded along Y.  x_in is inside the solid it
    joins, x_face the surface, x_apex the point.  f maps left coordinates to the working side."""
    pts = [(x_in, zc - hh), (x_face, zc - hh), (x_apex, zc), (x_face, zc + hh), (x_in, zc + hh)]
    w = [V(f(x), y0, z) for x, z in pts]
    return Part.Face(Part.makePolygon(w + [w[0]])).extrude(V(0, y1 - y0, 0))


def mir_in(x):                          # mirror about the peg's own centre line
    return 2 * PEG_MID_X - x


def side_func(side):
    return (lambda x: x) if side == 0 else mx


def peg_bumps(side):
    f = side_func(side)
    out = ridge(f, PEG_X[0] + 0.2, PEG_X[0], PEG_X[0] - BUMP_APEX, BUMP_Z, BUMP_HALF, *BUMP_Y)
    out = out.fuse(ridge(f, mir_in(PEG_X[0] + 0.2), mir_in(PEG_X[0]), mir_in(PEG_X[0] - BUMP_APEX),
                         BUMP_Z, BUMP_HALF, *BUMP_Y))
    return out


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
    # rib on the bolt-side wall behind the bump groove: the groove leaves only 0.65 of the 1.2 wall.  It starts above the
    # M3 head (Z 8.2) and stays 0.05 clear of the d5 driver path, so it needs no support when printed tab-down.
    rib_pts = [(WALL_OUT_X, 9.0), (WALL_OUT_X - 0.8, 12.0), (WALL_OUT_X - 0.8, SOCK_TOP), (WALL_OUT_X, SOCK_TOP)]
    rw = [V(x, 130.0, z) for x, z in rib_pts]
    b = b.fuse(Part.Face(Part.makePolygon(rw + [rw[0]])).extrude(V(0, 6.0, 0))).removeSplitter()
    b = b.cut(box(POCK_X[0], POCK_X[1], POCK_Y[0], POCK_Y[1], TAB_TOP, SOCK_TOP + 1.0))
    ident = lambda x: x
    # grooves in both pocket side walls (cut depth into the wall; the 1.2 outer wall keeps 0.7)
    b = b.cut(ridge(ident, POCK_X[0] + 0.05, POCK_X[0], POCK_X[0] - GROOVE_APEX, BUMP_Z, GROOVE_HALF, *GROOVE_Y))
    b = b.cut(ridge(ident, mir_in(POCK_X[0] + 0.05), mir_in(POCK_X[0]), mir_in(POCK_X[0] - GROOVE_APEX),
                    BUMP_Z, GROOVE_HALF, *GROOVE_Y))
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
ox0, ox1, oy0, oy1 = ix0 - WALL_T, ix1 + WALL_T, iy0 - WALL_T, iy1 + WALL_T
tray = box(ox0, ox1, oy0, oy1, FLOOR_Z, FLOOR_Z + FLOOR_T)
tray = tray.fuse(box(ox0, ox1, oy0, oy1, FLOOR_Z + FLOOR_T, WALL_TOP).cut(
    box(ix0, ix1, iy0, iy1, FLOOR_Z, WALL_TOP + 1)))
for x, y in board_holes:
    tray = tray.fuse(Part.makeCylinder(3.0, STANDOFF_H, V(x, y, FLOOR_Z + FLOOR_T)))

left_flare = [(25.0, 123.0), (29.1, 123.0), (32.7, 127.4), (32.7, 134.0), (28.7, 134.0), (28.7, 128.5), (25.0, 126.0)]
for side in (0, 1):
    f = side_func(side)

    def B(x0, x1, y0, y1, z0, z1):
        a, b = sorted((f(x0), f(x1)))
        return box(a, b, y0, y1, z0, z1)

    parts = [
        B(22.0, 32.1, oy1 - 1.0, 100.0, FLOOR_Z, TOP),
        B(24.0, 30.1, 100.0, 104.0, FLOOR_Z, TOP),
        B(25.0, 29.1, 100.0, 127.0, ARM_Z0, TOP),
        B(28.7, PEG_X[1], 127.4, PEG_Y[1], SHOULDER_Z0, TOP),   # shoulder: the full-size post, above the socket
        make_peg_box(f),                                    # the plug-in peg, 1 mm smaller
        prism([(f(x), y) for x, y in left_flare], ARM_Z0, TOP),
    ]
    for s in parts:
        tray = tray.fuse(s)
tray = tray.removeSplitter()
# arms were overbuilt (Jim, 2026-10-01): scoop the top between the two collar contacts.  Bending there is tiny (about 0.4 MPa for a
# 60 g tray); the root, flare and posts stay full depth.  The front ramp is 40 degrees from the print axis so it needs no support.
SCOOP = [(104.5, TOP + 0.1), (117.5, 29.0), (120.0, 29.0), (123.0, TOP + 0.1)]
for side in (0, 1):
    fs = side_func(side)
    xa, xb = sorted((fs(24.9), fs(29.2)))
    sw = [V(xa, y, z) for y, z in SCOOP]
    tray = tray.cut(Part.Face(Part.makePolygon(sw + [sw[0]])).extrude(V(xb - xa, 0, 0)))
tray = tray.removeSplitter()
for side in (0, 1):
    tray = peg_root_fillet(tray, side_func(side))
for x, y in board_holes:
    tray = tray.cut(Part.makeCylinder(M2_PILOT / 2, BOARD_PILOT_DEPTH + 0.1, V(x, y, BOARD_Z - BOARD_PILOT_DEPTH)))
tray = tray.removeSplitter()
tray_core = tray                                        # no click bumps: used for the travel tests
bumps = peg_bumps(0).fuse(peg_bumps(1))
tray = tray_core.fuse(bumps).removeSplitter()

base_l = make_base_left()
base_r = base_l.mirror(V(39.5, 0, 0), V(1, 0, 0))

# ================================================================ checks
master = App.openDocument(str(MASTER))
O = master.getObject
v3doc = App.openDocument(str(V3))
v3 = v3doc.getObject('PowerBoardTray').Shape
cells = box(0.0, 79.0, 21.0, 96.5, HOLDER_TOP, CELL_TOP)        # modelled from CELL_ABOVE_HOLDER, master untouched

check(tray.isValid() and len(tray.Solids) == 1, 'tray is one valid solid (%.2f cm3, v3 %.2f)' % (tray.Volume / 1000, v3.Volume / 1000))
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
check(tray.distToShape(cells)[0] >= CELL_GAP - 0.01, 'floor clears the modelled cells by %.2f' % tray.distToShape(cells)[0])
check(gaps['MastTube'] >= 0.39, 'arms clear the mast tube like v3 (%.2f)' % gaps['MastTube'])
p('INFO master BatteryCells still says 4 above the holder; Jim reports cells are negligibly over the rim, so the master value is stale.')

# tray <-> base fit
d_fit = tray_core.distToShape(base_l)[0]
check(d_fit >= 0.2, 'peg (with its root fillet) to socket clearance %.3f (design %.2f)' % (d_fit, CLR))
check(hit(tray, base_l) + hit(tray, base_r) < 1e-6, 'installed: bumps sit in their grooves, nothing overlaps')
check(PEG_Z0 - TAB_TOP >= 0.99,
      'peg bottom is %.1f above the socket floor (the arms bear on the collar)' % (PEG_Z0 - TAB_TOP))
check(SHOULDER_Z0 - SOCK_TOP >= 0.79, 'shoulder is %.1f above the socket top; peg engaged %.1f' % (SHOULDER_Z0 - SOCK_TOP, SOCK_TOP - PEG_Z0))
lift = tray.copy(); lift.translate(V(0, 0, 2.0))
i_det = hit(lift, base_l)
check(i_det > 0.8, 'click bump rides the wall when lifted 2 mm: interference %.2f mm3 per side pair (%.2f mm deep)'
      % (i_det, BUMP_APEX - CLR))

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
    v = hit(tray, box(ix0 + 0.01, ix1 - 0.01, y0 + 0.01, y1 - 0.01, FLOOR_Z + FLOOR_T + 0.01, WALL_TOP + 5))
    check(v < 1e-6, '%s end wire space %.1f x %.1f is open' % (nm, y1 - y0, ix1 - ix0))

# lead lanes over the mast base stay open (tray AND bases)
lanes = {
    'left outboard lane X18.2-21.9': box(18.2, 21.9, 93.0, 127.0, 2.1, 54.0),
    'right outboard lane': box(mx(21.9), mx(18.2), 93.0, 127.0, 2.1, 54.0),
    'centre gap in front of mast': box(32.2, 46.8, 93.0, 102.9, 2.1, 54.0),
    'below the arms (Z<20) over the mast base': box(18.2, 60.8, 96.6, 127.3, 2.1, 19.99),
}
for nm, b in lanes.items():
    check(hit(tray, b) + hit(base_l, b) + hit(base_r, b) < 1e-6, 'kept open: %s' % nm)
grew = tray_core.cut(v3)
below = hit(grew, box(0, 79, 93.0, 127.3, 0, ARM_Z0 - 0.01))
check(below < 1e-6, 'no v4 growth below Z 20 over the mast base (%.3f mm3)' % below)

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
    rows[nm] = {'v3_area_mm2': round(a3, 1), 'v3_depth': round(h3, 1), 'v4_area_mm2': round(a4, 1), 'v4_depth': round(h4, 1)}
    p('INFO section %-22s v3 %6.1f mm2 (depth %4.1f)  v4 %6.1f mm2 (depth %4.1f)' % (nm, a3, h3, a4, h4))
    if nm.startswith('arm beside'):
        check(a4 >= 40.0, '%s lightened but still %.1f mm2 (v3 %.1f), depth %.1f' % (nm, a4, a3, h4))
    elif nm == 'arm Y105':
        check(a4 >= a3 - 3.0, '%s is where the scoop ramp starts: %.1f mm2 (v3 %.1f)' % (nm, a4, a3))
    else:
        check(a4 >= a3 - 0.5, '%s not weaker than v3' % nm)
peg_a = tray_core.common(box(0, 79, 132.0 - 0.05, 132.0 + 0.05, 8.0, 15.0))
p('INFO peg section at Y132, Z8-15 (both pegs): %.1f mm2 (v3 post %.1f)' % (peg_a.Volume / 0.1,
  v3.common(box(0, 79, 132.0 - 0.05, 132.0 + 0.05, 8.0, 15.0)).Volume / 0.1))

if FAILS:
    p('REFUSING TO EXPORT: %d failed' % len(FAILS))
    for f_ in FAILS:
        p('  -', f_)
    sys.exit(2)

# ================================================================ outputs
doc = App.newDocument('PowerBoardTray_v4')
objs = []
for nm, lab, sh in (('PowerBoardTray', 'Power board tray v4 - lifts out of the bases', tray),
                    ('BaseLeft', 'Snap-in base, left', base_l), ('BaseRight', 'Snap-in base, right', base_r)):
    o = doc.addObject('Part::Feature', nm); o.Label = lab; o.Shape = sh; objs.append(o)
brd = box(BOARD_X0, BOARD_X0 + BOARD_W, BOARD_Y0, BOARD_Y0 + BOARD_L, BOARD_Z, BOARD_Z + PCB_T)
for x, y in board_holes:
    brd = brd.cut(Part.makeCylinder(M2_CLEAR / 2, PCB_T + 0.2, V(x, y, BOARD_Z - 0.1)))
o = doc.addObject('Part::Feature', 'BoardReference'); o.Label = 'Power board reference'; o.Shape = brd
doc.recompute()
doc.saveAs(str(OUT / 'PowerBoardTray_v4.FCStd'))
Part.export(objs, str(OUT / 'PowerBoardTray_v4.step'))
fine_mesh(tray).write(str(OUT / 'stl/PowerBoardTray_v4_installed.stl'))


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
stub = box(28.7, PEG_X[1], 127.4, PEG_Y[1], SHOULDER_Z0, SHOULDER_Z0 + 6.0).fuse(make_peg_box(side_func(0))).fuse(peg_bumps(0))
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
json.dump(prev, open('/tmp/v4_preview.json', 'w'))

val = {'script': 'scripts/build_power_tray_v4.py', 'tray_volume_cm3': round(tray.Volume / 1000, 2),
       'tray_pla_g_solid': round(tray.Volume * 1.24e-3, 1), 'base_volume_cm3_each': round(base_l.Volume / 1000, 2),
       'v3_volume_cm3': round(v3.Volume / 1000, 2),
       'cell_above_holder_modelled_negligible': CELL_ABOVE_HOLDER, 'cell_gap': CELL_GAP,
       'floor_z': [FLOOR_Z, FLOOR_Z + FLOOR_T], 'board_z': [BOARD_Z, BOARD_Z + PCB_T], 'wall_top': WALL_TOP,
       'standoff_h': STANDOFF_H, 'board_drop_vs_v3_mm': round(35.1 - BOARD_Z, 2), 'arm_top': TOP,
       'connector_room_to_upper_deck_mm': round(54.5 - (BOARD_Z + PCB_T), 1), 'v3_connector_room_mm': 17.8,
       'board_holes': board_holes, 'deck_fixings': slot_anchors,
       'peg': {'x': PEG_X, 'y': PEG_Y, 'size': [PEG_X[1] - PEG_X[0], PEG_Y[1] - PEG_Y[0]], 'clearance': CLR,
               'engaged_mm': SOCK_TOP - PEG_Z0, 'bump_apex_mm': BUMP_APEX, 'groove_apex_mm': GROOVE_APEX,
               'bump_interference_mm_per_side': round(BUMP_APEX - CLR, 2)},
       'base': {'x': BASE_X, 'y': BASE_Y, 'socket_top_z': SOCK_TOP, 'tab_z': [TAB_Z0, TAB_TOP]},
       'clearances_mm': gaps, 'collar_contact_mm2': round(contact, 1), 'sections': rows,
       'print': {'tray': N_TRAY, 'bases': [N_BASE_L, N_BASE_R], 'coupon': N_COUPON,
                 'tray_orientation': 'rear face down (as v2/v3)', 'bases_orientation': 'tab down',
                 'tray_bbox': [round(pm_tray.BoundBox.XLength, 1), round(pm_tray.BoundBox.YLength, 1), round(pm_tray.BoundBox.ZLength, 1)],
                 'tray_bed_contact_mm2': round(bed), 'tray_downward_faces_mm2': round(down)}}
json.dump(val, open(OUT / 'validation.json', 'w'), indent=1)
p('DONE', json.dumps(val['print']))
