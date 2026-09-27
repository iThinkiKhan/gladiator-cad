"""Build the Gladiator power-board tray ("cradle") v3.  Standalone file; the master is
only read.  Refuses to export if any check fails.

Why v3 (Jim, 2026-09-27, after the first full build):
  1. Rear fixing off: v2's two pilot-hole tabs aimed at (19, 128) / (60, 128), but the real
     rear pilots are 1.2 further out (17.8 / 61.2), under the rail rear feet -- unreachable.
     Those tabs are gone; the two rear slit bolts (which fitted) are the only deck fixings
     (Jim's choice).
  2. v2 is fragile -- make it stronger, not weaker.  The weak links were the arms: ~4 x 3.8
     bars from the tub back past the mast.  v3 keeps v2's arm/post/flare plan footprint and
     grows them UPWARD into free air to a common top at Z 40, with the arm web resting on the
     mast collar rim from Z 20.  Arm section ~4 x 20.  Floor 1.0 -> 1.6.
  3. v2's "+2.5 length" was solid wall.  Jim wanted it as open space around the board ends
     for wires: the wall now stands 2.9 clear of each board end (0.4 before), board and its
     screw holes unmoved.
  4. Found in the model: v2's floor (Z 22.2) sat 3.3 into the installed cells, which stand
     4 above the holder.  v3 lifts the whole tray 4.3 so the floor clears the cells by 1.0.
     The v2 rails raised the upper deck 6.5, so connector room above the board still grows.

Pack leads leave the rear of the pack and run over the mast base (Jim), so nothing that was
air in v2 below/beside the arms is filled: growth is upward only, inside v2's plan footprint,
and the outboard lanes and the centre gap in front of the mast stay open (checked below).
"""
import json
import math
import shutil
import sys
from pathlib import Path

import FreeCAD as App
import MeshPart
import Part

V = App.Vector
ROOT = Path('/home/buralien/projects/gladiator-cad')
MASTER = ROOT / 'cad/master/Gladiator_Master.FCStd'
V2 = ROOT / 'cad/power-board/v2-cradle/PowerBoardCradle_v2.FCStd'
OUT = ROOT / 'cad/power-board/v3-cradle'
INCOMING = Path('/home/buralien/3D-Printer/Incoming')
(OUT / 'stl').mkdir(parents=True, exist_ok=True)
PRINT_NAME = 'Gladiator_PowerBoardTray_v3_print-on-rear-face.stl'

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


# ---------------------------------------------------------------- board (unchanged from v1/v2)
BOARD_X0, BOARD_Y0 = 19.5, 29.0
BOARD_W, BOARD_L, PCB_T = 40.0, 60.0, 1.6
HOLE_DX, HOLE_DY = 34.5, 54.25
board_holes = [(BOARD_X0 + (BOARD_W - HOLE_DX) / 2 + ix * HOLE_DX,
                BOARD_Y0 + (BOARD_L - HOLE_DY) / 2 + iy * HOLE_DY) for ix in (0, 1) for iy in (0, 1)]

# ---------------------------------------------------------------- v3 heights
CELL_TOP = 25.5                 # holder top 21.5 + 4 (Jim)
FLOOR_Z = CELL_TOP + 1.0        # 26.5  (v2 22.2)
FLOOR_T = 1.6                   # v2 1.0
STANDOFF_H = 7.0                # solder-side clearance, as v2
BOARD_Z = FLOOR_Z + FLOOR_T + STANDOFF_H     # 35.1
WALL_TOP = BOARD_Z + PCB_T + 1.0             # 37.7
TOP = 40.0                      # common top of roots, arms, flares, rear posts
ARM_Z0 = 20.0                   # arm web bottom = mast collar top
TAB_Z0, TAB_TOP = 2.2, 5.2      # rear tabs unchanged so Jim's bolts still fit
M2_PILOT, M2_CLEAR = 1.6, 2.2
BOARD_PILOT_DEPTH = 5.5
WALL_T = 1.0
SIDE_GAP = 0.4
END_GAP = 0.4 + 2.5             # open wire space at each board end

slot_anchors = [(25.5, 130.5), (53.5, 130.5)]

# ---------------------------------------------------------------- tub
ix0, ix1 = BOARD_X0 - SIDE_GAP, BOARD_X0 + BOARD_W + SIDE_GAP          # 19.1 .. 59.9
iy0, iy1 = BOARD_Y0 - END_GAP, BOARD_Y0 + BOARD_L + END_GAP            # 26.1 .. 91.9
ox0, ox1, oy0, oy1 = ix0 - WALL_T, ix1 + WALL_T, iy0 - WALL_T, iy1 + WALL_T   # 18.1..60.9, 25.1..92.9
tray = box(ox0, ox1, oy0, oy1, FLOOR_Z, FLOOR_Z + FLOOR_T)
tray = tray.fuse(box(ox0, ox1, oy0, oy1, FLOOR_Z + FLOOR_T, WALL_TOP).cut(
    box(ix0, ix1, iy0, iy1, FLOOR_Z, WALL_TOP + 1)))
for x, y in board_holes:
    tray = tray.fuse(Part.makeCylinder(3.0, STANDOFF_H, V(x, y, FLOOR_Z + FLOOR_T)))

# ---------------------------------------------------------------- arms (v2 plan footprint, grown upward)
left_flare = [(25.0, 123.0), (29.1, 123.0), (32.7, 127.4), (32.7, 134.0), (28.7, 134.0), (28.7, 128.5), (25.0, 126.0)]
for side in (0, 1):
    f = (lambda x: x) if side == 0 else mx

    def B(x0, x1, y0, y1, z0, z1):
        a, b = sorted((f(x0), f(x1)))
        return box(a, b, y0, y1, z0, z1)

    parts = [
        B(22.0, 32.1, oy1 - 1.0, 100.0, FLOOR_Z, TOP),      # root: through the rear wall, back to Y 100
        B(24.0, 30.1, 100.0, 104.0, FLOOR_Z, TOP),          # taper
        B(25.0, 29.1, 100.0, 127.0, ARM_Z0, TOP),           # arm web, sits on the collar rim at Z 20
        B(28.7, 32.7, 127.4, 136.5, TAB_TOP, TOP),          # rear post
        B(18.4, 32.7, 127.4, 136.5, TAB_Z0, TAB_TOP),       # rear tab (slit bolt)
        prism([(f(x), y) for x, y in left_flare], ARM_Z0, TOP),
    ]
    for s in parts:
        tray = tray.fuse(s)
tray = tray.removeSplitter()
for x, y in board_holes:
    tray = tray.cut(Part.makeCylinder(M2_PILOT / 2, BOARD_PILOT_DEPTH + 0.1, V(x, y, BOARD_Z - BOARD_PILOT_DEPTH)))
for x, y in slot_anchors:
    tray = tray.cut(Part.makeCylinder(M2_CLEAR / 2, TAB_TOP - TAB_Z0 + 0.2, V(x, y, TAB_Z0 - 0.1)))
tray = tray.removeSplitter()

# ================================================================ checks
master = App.openDocument(str(MASTER))
O = master.getObject
v2doc = App.openDocument(str(V2))
v2 = v2doc.getObject('PowerBoardCradle').Shape

check(tray.isValid() and len(tray.Solids) == 1, 'tray is one valid solid (%.2f cm3, v2 %.2f)' % (tray.Volume / 1000, v2.Volume / 1000))

obstacles = ['ChassisDeck', 'BatteryBox', 'BatteryCells', 'MastBase', 'MastTube', 'SideRailLeft', 'SideRailRight',
             'UpperDeck', 'AntennaPost', 'S3Board', 'Breadboard', 'DriverMountLeft', 'DriverMountRight',
             'DrvV5_Base_L', 'DrvV5_Wedge_L', 'DrvV5_Base_R', 'DrvV5_Wedge_R',
             'DrvV5_Board_L', 'DrvV5_Fins_L', 'DrvV5_Board_R', 'DrvV5_Fins_R']
clash = {n: round(hit(tray, O(n).Shape), 3) for n in obstacles if O(n)}
clash = {k: v for k, v in clash.items() if v > 0.01}
check(not clash, 'no clashes with %d master solids %s (PowerShield is legacy, superseded by the tray, not checked)'
      % (len(obstacles), clash))
gaps = {n: round(tray.distToShape(O(n).Shape)[0], 2) for n in
        ('BatteryCells', 'MastTube', 'MastBase', 'SideRailLeft', 'SideRailRight', 'UpperDeck', 'ChassisDeck')}
p('INFO clearances', gaps)
check(gaps['BatteryCells'] >= 0.99, 'floor clears the installed cells by >= 1.0 (%.2f)' % gaps['BatteryCells'])
check(gaps['MastTube'] >= 0.39, 'arms clear the mast tube like v2 (%.2f)' % gaps['MastTube'])
check(hit(v2, O('BatteryCells').Shape) > 1000, 'confirms v2 overlapped the cells (%.0f mm3)' % hit(v2, O('BatteryCells').Shape))

# arms rest on the collar rim
mb = O('MastBase').Shape
contact = 0.0
for side in (0, 1):
    xs = sorted((25.0, 29.1)) if side == 0 else sorted((mx(29.1), mx(25.0)))
    film = box(xs[0], xs[1], 100.0, 127.0, ARM_Z0 - 0.1, ARM_Z0)
    contact += hit(film, mb) / 0.1
check(contact > 20.0, 'arms bear on the mast collar rim (%.1f mm2 total)' % contact)

# open wire space at both board ends, full height inside the wall
# (the 6 mm board standoffs, fixed by the board's own holes, reach 0.125 past each board end;
# the strip is probed short of them)
for nm, y0, y1 in (('front', iy0, BOARD_Y0 - 0.2), ('rear', BOARD_Y0 + BOARD_L + 0.2, iy1)):
    v = hit(tray, box(ix0 + 0.01, ix1 - 0.01, y0 + 0.01, y1 - 0.01, FLOOR_Z + FLOOR_T + 0.01, WALL_TOP + 5))
    check(v < 1e-6, '%s end wire space %.1f x %.1f is open (v2: 0.4 gap, rest solid)' % (nm, y1 - y0, ix1 - ix0))

# nothing that was air in v2 below/beside the arms is filled: lead lanes over the mast base
lanes = {
    'left outboard lane X18.2-21.9': box(18.2, 21.9, 93.0, 127.0, 2.1, 54.0),
    'right outboard lane': box(mx(21.9), mx(18.2), 93.0, 127.0, 2.1, 54.0),
    'centre gap in front of mast': box(32.2, 46.8, 93.0, 102.9, 2.1, 54.0),
    'below the arms (Z<20) over the mast base': box(18.2, 60.8, 96.6, 127.3, 2.1, 19.99),
}
for nm, b in lanes.items():
    check(hit(tray, b) < 1e-6, 'kept open: %s' % nm)
# v2's two dead pilot holes at (19, 128) / (60, 128) are simply filled; ignore them
grew = tray.cut(v2)
for x in (19.0, 60.0):
    grew = grew.cut(Part.makeCylinder(0.85, 4.0, V(x, 128.0, 1.9)))
below = hit(grew, box(0, 79, 93.0, 140, 0, ARM_Z0 - 0.01))
check(below < 1e-6, 'no v3 growth below Z 20 behind the tub (%.3f mm3)' % below)

# service: slit bolt heads, driver shafts, mast cross pin, mast base screws
deck = O('ChassisDeck').Shape
for x, y in slot_anchors:
    check(hit(Part.makeCylinder(1.0, 3.0, V(x, y, -0.5)), deck) < 1e-6, 'M2 at (%.1f, %.1f) passes the deck slit' % (x, y))
    ring = Part.makeCylinder(2.5, 0.3, V(x, y, TAB_TOP - 0.3)).cut(Part.makeCylinder(M2_CLEAR / 2 + 0.01, 0.5, V(x, y, TAB_TOP - 0.4)))
    check(hit(ring, tray) / 0.3 > 14.0, 'bolt head bearing at (%.1f, %.1f) %.1f mm2' % (x, y, hit(ring, tray) / 0.3))
    check(hit(Part.makeCylinder(3.0, 54.0 - TAB_TOP - 0.1, V(x, y, TAB_TOP + 0.1)), tray) < 1e-6,
          'driver shaft d6 clear above bolt at (%.1f, %.1f)' % (x, y))
pin_l = Part.makeCylinder(3.0, 26.0, V(0, 113, 13), V(1, 0, 0))
pin_r = Part.makeCylinder(3.0, 26.5, V(52.5, 113, 13), V(1, 0, 0))
check(hit(pin_l, tray) + hit(pin_r, tray) < 1e-6, 'mast cross pin reachable from both sides with the tray on')
for x in (17.8, 61.2):
    check(hit(Part.makeCylinder(2.0, 30.0, V(x, 111, 6.0)), tray) < 1e-6, 'mast base M2 at X %.1f untouched' % x)
for x, y in board_holes:
    shell = Part.makeCylinder(3.0, BOARD_PILOT_DEPTH - 0.2, V(x, y, BOARD_Z - BOARD_PILOT_DEPTH)).cut(
        Part.makeCylinder(M2_PILOT / 2, BOARD_PILOT_DEPTH, V(x, y, BOARD_Z - BOARD_PILOT_DEPTH - 0.1)))
    check(hit(shell, tray) > 60.0, 'board standoff (%.2f, %.2f) intact, pilot blind above the floor' % (x, y))
    check(hit(Part.makeCylinder(M2_PILOT / 2 - 0.01, FLOOR_T, V(x, y, FLOOR_Z)), tray) > 0,
          'floor solid under pilot (%.2f, %.2f)' % (x, y))

# drop-on: the tray lowers straight down onto the mast base with the mast tube fitted
obst = [O(n).Shape for n in ('MastTube', 'MastBase', 'SideRailLeft', 'SideRailRight', 'BatteryCells', 'BatteryBox', 'ChassisDeck')]
worst = 0.0
for i in range(1, 81):
    t = tray.copy(); t.translate(V(0, 0, 0.5 * i))
    worst = max(worst, max(hit(t, s) for s in obst))
check(worst < 1e-6, 'drops on vertically over 40 mm with the mast tube in place (worst %.3f)' % worst)

# strength comparison: sections through the arm and the root
def section(shape, y, x0, x1):
    s = shape.common(box(x0, x1, y - 0.05, y + 0.05, 0, 60))
    if s.Volume <= 0:
        return 0.0, 0.0
    return s.Volume / 0.1, s.BoundBox.ZLength

rows = {}
for nm, y, xa, xb in (('arm beside mast Y115', 115.0, 18, 39.5), ('arm Y105', 105.0, 18, 39.5),
                      ('root Y96', 96.0, 18, 39.5), ('flare Y125', 125.0, 18, 39.5)):
    a2, h2 = section(v2, y, xa, xb)
    a3, h3 = section(tray, y, xa, xb)
    rows[nm] = {'v2_area_mm2': round(a2, 1), 'v2_depth': round(h2, 1), 'v3_area_mm2': round(a3, 1), 'v3_depth': round(h3, 1)}
    p('INFO section %-22s v2 %6.1f mm2 (depth %4.1f)  v3 %6.1f mm2 (depth %4.1f)' % (nm, a2, h2, a3, h3))
    check(a3 >= a2, '%s not weaker than v2' % nm)

if FAILS:
    p('REFUSING TO EXPORT: %d failed' % len(FAILS))
    for f_ in FAILS:
        p('  -', f_)
    sys.exit(2)

# ================================================================ outputs
doc = App.newDocument('PowerBoardTray_v3')
part = doc.addObject('Part::Feature', 'PowerBoardTray')
part.Label = 'Power board tray v3 - lifted over cells, deep arms, open board ends'
part.Shape = tray
brd = box(BOARD_X0, BOARD_X0 + BOARD_W, BOARD_Y0, BOARD_Y0 + BOARD_L, BOARD_Z, BOARD_Z + PCB_T)
for x, y in board_holes:
    brd = brd.cut(Part.makeCylinder(M2_CLEAR / 2, PCB_T + 0.2, V(x, y, BOARD_Z - 0.1)))
o = doc.addObject('Part::Feature', 'BoardReference'); o.Label = 'Power board reference'; o.Shape = brd
doc.recompute()
doc.saveAs(str(OUT / 'PowerBoardTray_v3.FCStd'))
Part.export([part], str(OUT / 'PowerBoardTray_v3.step'))

m = MeshPart.meshFromShape(Shape=tray, LinearDeflection=0.01, AngularDeflection=0.05, Relative=False)
m.write(str(OUT / 'stl/PowerBoardTray_v3_installed.stl'))
ps = tray.copy()
ps.rotate(V(0, 0, 0), V(1, 0, 0), -90.0)        # rear face (Y 136.5) onto the bed, as v2
bb = ps.BoundBox
ps.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
pm = MeshPart.meshFromShape(Shape=ps, LinearDeflection=0.01, AngularDeflection=0.05, Relative=False)
ok = (pm.isSolid() and not pm.hasNonManifolds() and not pm.hasSelfIntersections() and abs(pm.BoundBox.ZMin) < 1e-6
      and abs(pm.Volume - tray.Volume) / tray.Volume < 0.005 and max(pm.BoundBox.XLength, pm.BoundBox.YLength) < 220)
check(ok, 'print mesh solid / manifold / on bed / volume %s' % pm.BoundBox)
bed = sum(f.Area for f in ps.Faces if f.Surface.TypeId == 'Part::GeomPlane' and abs(f.BoundBox.ZMax) < 1e-6)
down = sum(f.Area for f in ps.Faces if f.BoundBox.ZMin > 0.01 and f.Surface.TypeId == 'Part::GeomPlane'
           and f.normalAt(0, 0).z < -0.7)
p('INFO print: bbox %.1f x %.1f x %.1f, bed contact %.0f mm2, downward flat faces off the bed %.0f mm2 (bridges/ledges)'
  % (pm.BoundBox.XLength, pm.BoundBox.YLength, pm.BoundBox.ZLength, bed, down))
if FAILS:
    sys.exit(3)
pm.write(str(OUT / 'stl' / PRINT_NAME))
shutil.copy2(OUT / 'stl' / PRINT_NAME, INCOMING / PRINT_NAME)

val = {'script': 'scripts/build_power_cradle_v3.py', 'volume_cm3': round(tray.Volume / 1000, 2),
       'pla_g_solid': round(tray.Volume * 1.24e-3, 1), 'v2_volume_cm3': round(v2.Volume / 1000, 2),
       'floor_z': [FLOOR_Z, FLOOR_Z + FLOOR_T], 'board_z': [BOARD_Z, BOARD_Z + PCB_T], 'wall_top': WALL_TOP,
       'arm_top': TOP, 'cell_top': CELL_TOP, 'end_wire_gap_mm': END_GAP, 'board_holes': board_holes,
       'deck_fixings': slot_anchors, 'clearances_mm': gaps, 'collar_contact_mm2': round(contact, 1),
       'sections': rows, 'connector_room_to_upper_deck_mm': round(54.5 - (BOARD_Z + PCB_T), 1),
       'print': {'file': PRINT_NAME, 'orientation': 'rear face down (as v2)',
                 'bbox': [round(pm.BoundBox.XLength, 1), round(pm.BoundBox.YLength, 1), round(pm.BoundBox.ZLength, 1)],
                 'bed_contact_mm2': round(bed), 'downward_faces_mm2': round(down)}}
json.dump(val, open(OUT / 'validation.json', 'w'), indent=1)
p('DONE', json.dumps(val['print']))
