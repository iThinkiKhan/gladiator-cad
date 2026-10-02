"""Build the INA226 cassette v1: a removable shelf that hangs on the front wall of the power-board
tray v4, in front of the battery box.  The tray is NOT modified.  Standalone; the master and the
v4 tray are only read.  Refuses to export if any check fails.

Layout (Jim, 2026-10-01): board front-to-back, header edge facing the FRONT with its pins poking out,
terminals at the rear.  Flat shelf.  Removable from the tray so it can change independently.

Attachment: a plate in front of the tray's front wall, a lip over the wall top, and a tongue under the
tray floor (it slides on from the front, +Y, and off again).  Light friction bumps on the tongue.
No screws.  The cassette rides with the tray when the tray lifts out for a battery change.

INA226 numbers (Jim, 2026-10-01, measurements/components.md): board 26 (terminal edge to header edge) x 22,
PCB 1.6; screw terminals 14 tail-to-top, no overhang, wires leave from the terminal edge; header pins
protrude 7; the two M2 (d2) holes sit in the header-edge corners.
  INFERRED, NOT CALIPERED: Jim says the corner is rounded around the hole with about 1 mm of board left,
  read here as hole centres 2.0 from the header edge and 2.0 from each side edge.
  JIM 2026-10-01: about 3 mm between the bottom of the screw terminal and the bottom of the board, read as pin tails 3.0 below the PCB.
  ASSUMED: nothing on the PCB underside beyond the terminal and header tails.
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
TRAY = ROOT / 'cad/power-board/v4-tray/PowerBoardTray_v4.FCStd'
TRAYVAL = ROOT / 'cad/power-board/v4-tray/validation.json'
OUT = ROOT / 'cad/power-board/ina-cassette-v1'
INCOMING = Path('/home/buralien/3D-Printer/Incoming/Gladiator')
(OUT / 'stl').mkdir(parents=True, exist_ok=True)
INCOMING.mkdir(parents=True, exist_ok=True)
PRINT_NAME = 'Gladiator_INA226_Cassette_v1_print-upright.stl'

FAILS = []


def p(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n'); sys.stdout.flush()


def check(ok, msg):
    p(('PASS ' if ok else 'FAIL ') + msg)
    if not ok:
        FAILS.append(msg)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def hit(a, b):
    if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    return a.common(b).Volume


def fine_mesh(shape):
    return MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.01, AngularDeflection=0.05, Relative=False)


tv = json.load(open(TRAYVAL))
FLOOR_Z = tv['floor_z'][0]              # 24.7, tray floor underside
WALL_TOP = tv['wall_top']               # 33.4
WALL_OUT_Y = 25.1                       # tray front wall outer face (script constant oy0)
WALL_T = 1.0

# ---------------------------------------------------------------- INA226
BOARD_W, BOARD_L, PCB_T = 22.0, 26.0, 1.6
HOLE_D, HOLE_EDGE = 2.0, 2.0            # hole centre from the header edge and from each side edge (INFERRED)
TAIL = 3.0                              # Jim 2026-10-01: about 3 between the bottom of the screw terminal and the PCB underside
                                        # (read as the pin tails below the PCB; was derived 2.2)
TALLEST = 11.8                          # above the PCB underside, as recorded
TERM_DEPTH = 8.5                        # terminal block depth from the terminal edge (not measured; envelope)
PIN_OUT = 7.0
WIRE_GAP = 10.0                         # terminal edge to the plate: wires need about 3 straight + a 5 radius bend (was 6)
BOARD_X0 = 39.5 - BOARD_W / 2           # centred on the deck

# ---------------------------------------------------------------- cassette
CLR = 0.1                               # plate to wall face
GAP_Z = 0.1                             # lip above the wall top, tongue below the floor: 0.2 of total vertical play,
                                        # so the tongue bumps always preload against the floor
PLATE_Y = (WALL_OUT_Y - CLR - 1.2, WALL_OUT_Y - CLR)         # 23.8 .. 25.0
CASS_X = (18.5, 60.5)                   # 0.5 off each rail; the rails locate it sideways
Z0 = 23.2                               # bed plane of the part: shelf and tongue bottoms
TONGUE_T = FLOOR_Z - GAP_Z - Z0         # 1.3
TONGUE_Y1 = 33.0
LIP_Z = (WALL_TOP + GAP_Z, WALL_TOP + GAP_Z + 1.2)
LIP_Y1 = WALL_OUT_Y + WALL_T + 0.9      # 0.9 over the inside of the wall
BUMP_H, BUMP_Y = 0.3, 30.5
SHELF_T = 2.0
SHELF_TOP = Z0 + SHELF_T                # 25.2
POST_H = 4.0                            # tails 3.0 + 1.0 of clearance over the shelf
PCB_Z0 = SHELF_TOP + POST_H             # 28.2
POST_D, PILOT_D, PILOT_DEPTH = 5.0, 1.6, 3.5
LIP_H = 4.0
SIDE_LIP_T, SIDE_LIP_GAP = 1.0, 0.2

Y_T = PLATE_Y[0] - WIRE_GAP             # terminal edge
Y_H = Y_T - BOARD_L                     # header edge
SHELF_X = (BOARD_X0 - SIDE_LIP_GAP - SIDE_LIP_T, BOARD_X0 + BOARD_W + SIDE_LIP_GAP + SIDE_LIP_T)
SHELF_Y0 = Y_H - 1.0

holes = [(BOARD_X0 + HOLE_EDGE, Y_H + HOLE_EDGE), (BOARD_X0 + BOARD_W - HOLE_EDGE, Y_H + HOLE_EDGE)]

# plate, lip, tongue
body = box(CASS_X[0], CASS_X[1], PLATE_Y[0], PLATE_Y[1], Z0, LIP_Z[1])
body = body.fuse(box(CASS_X[0], CASS_X[1], PLATE_Y[0], LIP_Y1, LIP_Z[0], LIP_Z[1]))
body = body.fuse(box(CASS_X[0], CASS_X[1], PLATE_Y[0], TONGUE_Y1, Z0, Z0 + TONGUE_T))
# shelf, side lips, posts, pads
body = body.fuse(box(SHELF_X[0], SHELF_X[1], SHELF_Y0, PLATE_Y[0] + 0.5, Z0, SHELF_TOP))
# wings: flat tabs on the shelf that sit between the rails' front posts (they stand at X<=18 and X>=61 for Y 2..18.5),
# so the posts locate the cassette sideways whenever the tray is in the robot.
WING_X, WING_Y = (18.6, 60.4), (4.0, 17.0)
body = body.fuse(box(WING_X[0], WING_X[1], WING_Y[0], WING_Y[1], Z0, SHELF_TOP))
for x0 in (SHELF_X[0], SHELF_X[1] - SIDE_LIP_T):
    body = body.fuse(box(x0, x0 + SIDE_LIP_T, Y_H + 5.0, PLATE_Y[0] + 0.5, SHELF_TOP, SHELF_TOP + LIP_H))
for x, y in holes:
    body = body.fuse(Part.makeCylinder(POST_D / 2, POST_H, V(x, y, SHELF_TOP)))
for xc in (31.5, 47.5):
    body = body.fuse(box(xc - 2.0, xc + 2.0, Y_H + 12.0, Y_H + 14.0, SHELF_TOP, PCB_Z0))
body = body.removeSplitter()
for x, y in holes:
    body = body.cut(Part.makeCylinder(PILOT_D / 2, PILOT_DEPTH + 0.1, V(x, y, PCB_Z0 - PILOT_DEPTH)))
body = body.removeSplitter()
core = body                              # no friction bumps: used for the slide-on test


def tongue_bump(xc):
    pts = [V(xc - 2.0, BUMP_Y - 0.7, Z0 + TONGUE_T - 0.05), V(xc - 2.0, BUMP_Y, Z0 + TONGUE_T + BUMP_H),
           V(xc - 2.0, BUMP_Y + 0.7, Z0 + TONGUE_T - 0.05)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(V(4.0, 0, 0))


bumps = tongue_bump(30.0).fuse(tongue_bump(49.0))
cass = core.fuse(bumps).removeSplitter()

# ================================================================ checks
master = App.openDocument(str(MASTER))
O = master.getObject
trdoc = App.openDocument(str(TRAY))
tray = trdoc.getObject('PowerBoardTray').Shape

check(cass.isValid() and len(cass.Solids) == 1, 'cassette is one valid solid (%.2f cm3, ~%.1f g PLA)' % (cass.Volume / 1000, cass.Volume * 1.24e-3))
obstacles = ['ChassisDeck', 'BatteryBox', 'BatteryCells', 'SideRailLeft', 'SideRailRight', 'MastBase', 'MastTube', 'UpperDeck',
             'AntennaPost', 'S3Board', 'Breadboard', 'DriverMountLeft', 'DriverMountRight', 'DrvV5_Base_L', 'DrvV5_Base_R']
clash = {n: round(hit(cass, O(n).Shape), 3) for n in obstacles if O(n)}
clash = {k: v for k, v in clash.items() if v > 0.01}
check(not clash, 'no clashes with the master solids %s' % clash)
check(hit(core, tray) < 1e-6, 'no clash with the v4 tray (bumps excluded)')
d_tray = core.distToShape(tray)[0]
check(0.09 <= d_tray <= 0.3, 'nearest approach to the tray %.2f (plate %.1f, lip and tongue %.1f)' % (d_tray, CLR, GAP_Z))
rails = {n: round(cass.distToShape(O(n).Shape)[0], 2) for n in ('SideRailLeft', 'SideRailRight')}
cells_d = cass.distToShape(O('BatteryCells').Shape)[0]
box_d = cass.distToShape(O('BatteryBox').Shape)[0]
deck_d = cass.distToShape(O('ChassisDeck').Shape)[0]
p('INFO clearances: rails', rails, 'cells %.2f' % cells_d, 'battery holder %.2f' % box_d, 'deck %.2f' % deck_d)
check(0.5 <= min(rails.values()) <= 0.7, 'the rail front posts stand %.2f off each wing and locate the cassette sideways' % min(rails.values()))
check(cells_d >= 1.0, 'tongue clears the cells by %.2f' % cells_d)
check(hit(cass, tray) > 0.15, 'friction bumps press the tray floor: %.2f mm3 of interference (%.2f mm deep)' % (hit(cass, tray), BUMP_H - GAP_Z))

# INA board and its envelopes sit on the posts, clear of everything else
pcb = box(BOARD_X0, BOARD_X0 + BOARD_W, Y_H, Y_T, PCB_Z0, PCB_Z0 + PCB_T)
for x, y in holes:
    pcb = pcb.cut(Part.makeCylinder(HOLE_D / 2, PCB_T + 0.2, V(x, y, PCB_Z0 - 0.1)))
terms = box(BOARD_X0, BOARD_X0 + BOARD_W, Y_T - TERM_DEPTH, Y_T, PCB_Z0 - TAIL, PCB_Z0 + TALLEST)
header = box(39.5 - 5.1, 39.5 + 5.1, Y_H - PIN_OUT, Y_H + 2.0, PCB_Z0 + PCB_T, PCB_Z0 + PCB_T + 2.5)
check(hit(pcb, cass) < 1e-6 and hit(terms.cut(pcb), cass) < 1e-6, 'the board sits on the posts and pads with nothing else touching')
check(hit(header, cass) < 1e-6 and hit(header, tray) < 1e-6, 'header and its pins are free, poking out the front by %.0f' % PIN_OUT)
check(PCB_Z0 - TAIL - SHELF_TOP >= 0.9, 'terminal pin tails (3.0, Jim) clear the shelf by %.2f' % (PCB_Z0 - TAIL - SHELF_TOP))
tail_in = box(BOARD_X0, BOARD_X0 + BOARD_W, Y_T - TERM_DEPTH, Y_T, PCB_Z0 - TAIL, PCB_Z0)
check(hit(tail_in, cass) < 1e-6, 'terminal tails do not touch the pads or posts')
for nm, shp in (('terminals', terms), ('header', header), ('board', pcb)):
    c = {n: round(hit(shp, O(n).Shape), 3) for n in obstacles if O(n) and hit(shp, O(n).Shape) > 0.01}
    check(not c, 'INA %s envelope clear of the master %s' % (nm, c))
dup = box(34.0, 45.0, Y_H - PIN_OUT - 8.0, Y_H - PIN_OUT, PCB_Z0 + PCB_T, PCB_Z0 + PCB_T + 3.0)
check(sum(hit(dup, O(n).Shape) for n in obstacles if O(n)) < 1e-6, 'a Dupont housing on the pins has room in front (envelope 8 long)')
check(54.5 - (PCB_Z0 + TALLEST) > 10.0, 'terminal tops %.1f under the upper deck, screw access from above' % (54.5 - (PCB_Z0 + TALLEST)))
for x, y in holes:
    drv = Part.makeCylinder(2.5, 54.0 - (PCB_Z0 + PCB_T) - 0.1, V(x, y, PCB_Z0 + PCB_T + 0.1))
    check(hit(drv, cass) + hit(drv, tray) + hit(drv, terms) + hit(drv, header) < 1e-6,
          'M2 at (%.1f, %.1f): screwdriver path d5 clear above the board' % (x, y))

# slide on from the front, 20 mm of travel, and lift out with the tray
fixed = [O(n).Shape for n in ('SideRailLeft', 'SideRailRight', 'BatteryBox', 'BatteryCells', 'ChassisDeck', 'MastTube', 'MastBase')]
worst = 0.0
for i in range(0, 41):
    t = core.copy(); t.translate(V(0, -0.5 * i, 0))
    worst = max(worst, hit(t, tray), max(hit(t, s) for s in fixed))
check(worst < 1e-6, 'slides on and off along Y over 20 mm without touching the tray or the robot (worst %.3f)' % worst)
worst_l = 0.0
for i in range(1, 81):
    t = cass.copy(); t.translate(V(0, 0, 0.5 * i))
    worst_l = max(worst_l, max(hit(t, s) for s in fixed))
check(worst_l < 1e-6, 'lifts straight up with the tray over 40 mm (worst %.3f)' % worst_l)
lifted = core.copy(); lifted.translate(V(0, 0, 3.0))
check(hit(lifted, tray) > 1e-3, 'it cannot be lifted off the tray: the tongue catches the floor (3 mm lift overlaps %.2f mm3); '
      'it comes off by sliding forward' % hit(lifted, tray))

if FAILS:
    p('REFUSING TO EXPORT: %d failed' % len(FAILS))
    for f_ in FAILS:
        p('  -', f_)
    sys.exit(2)

# ================================================================ outputs
doc = App.newDocument('INA226_Cassette_v1')
o = doc.addObject('Part::Feature', 'INA226Cassette'); o.Label = 'INA226 cassette v1 - hangs on the tray front wall'; o.Shape = cass
b = doc.addObject('Part::Feature', 'INA226BoardReference'); b.Label = 'INA226 board reference (PCB)'; b.Shape = pcb
e = doc.addObject('Part::Feature', 'INA226TerminalEnvelope'); e.Label = 'Terminal envelope (assumed depth)'; e.Shape = terms
h = doc.addObject('Part::Feature', 'INA226HeaderEnvelope'); h.Label = 'Header and pins envelope'; h.Shape = header
doc.recompute()
doc.saveAs(str(OUT / 'INA226_Cassette_v1.FCStd'))
Part.export([o], str(OUT / 'INA226_Cassette_v1.step'))
fine_mesh(cass).write(str(OUT / 'stl/INA226_Cassette_v1_installed.stl'))

ps = cass.copy(); bb = ps.BoundBox
ps.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
pm = fine_mesh(ps)
ok = (pm.isSolid() and not pm.hasNonManifolds() and not pm.hasSelfIntersections() and abs(pm.BoundBox.ZMin) < 1e-6
      and abs(pm.Volume - cass.Volume) / cass.Volume < 0.005 and max(pm.BoundBox.XLength, pm.BoundBox.YLength) < 220)
check(ok, 'print mesh solid / manifold / on bed / volume %s' % pm.BoundBox)
bed = sum(f.Area for f in ps.Faces if f.Surface.TypeId == 'Part::GeomPlane' and abs(f.BoundBox.ZMax) < 1e-6)
down = sum(f.Area for f in ps.Faces if f.BoundBox.ZMin > 0.01 and f.Surface.TypeId == 'Part::GeomPlane' and f.normalAt(0, 0).z < -0.7)
p('INFO print: bbox %.1f x %.1f x %.1f, bed contact %.0f mm2, downward flat faces off the bed %.0f mm2 (the lip overhang)'
  % (pm.BoundBox.XLength, pm.BoundBox.YLength, pm.BoundBox.ZLength, bed, down))
if FAILS:
    sys.exit(3)
pm.write(str(OUT / 'stl' / PRINT_NAME))
shutil.copy2(OUT / 'stl' / PRINT_NAME, INCOMING / PRINT_NAME)


def wires(shape, axis, pos):
    return [[[round(q.x, 3), round(q.y, 3), round(q.z, 3)] for q in w.discretize(Deflection=0.05)] for w in shape.slice(axis, pos)]


prev = {}
for key, x in (('x39', 39.5), ('x30', 30.5)):
    prev[key] = {n: wires(s, V(1, 0, 0), x) for n, s in (('cass', cass), ('tray', tray), ('pcb', pcb), ('terms', terms),
                                                           ('header', header), ('cells', O('BatteryCells').Shape),
                                                           ('box', O('BatteryBox').Shape), ('deck', O('ChassisDeck').Shape))}
prev['z27'] = {n: wires(s, V(0, 0, 1), 27.0) for n, s in (('cass', cass), ('tray', tray), ('rail_l', O('SideRailLeft').Shape),
                                                            ('rail_r', O('SideRailRight').Shape), ('deck', O('ChassisDeck').Shape))}
prev['z29'] = {n: wires(s, V(0, 0, 1), 29.0) for n, s in (('cass', cass), ('tray', tray), ('pcb', pcb), ('header', header),
                                                            ('rail_l', O('SideRailLeft').Shape), ('rail_r', O('SideRailRight').Shape))}
json.dump(prev, open('/tmp/ina_preview.json', 'w'))

val = {'script': 'scripts/build_ina_cassette_v1.py', 'volume_cm3': round(cass.Volume / 1000, 2), 'pla_g_solid': round(cass.Volume * 1.24e-3, 1),
       'orientation': 'board front-to-back, header edge facing the front, terminals at the rear, flat shelf',
       'INFERRED_hole_centres': {'from_header_edge': HOLE_EDGE, 'from_side_edge': HOLE_EDGE, 'holes_xy': holes,
                                 'basis': "Jim: holes touch the corner, about 1 mm of board; read as a corner arc of r2 around a d2 hole"},
       'pin_tail_mm_Jim_about': TAIL, 'ASSUMED_terminal_depth_mm': TERM_DEPTH,
       'board_y': [Y_H, Y_T], 'board_x': [BOARD_X0, BOARD_X0 + BOARD_W], 'pcb_z': [PCB_Z0, PCB_Z0 + PCB_T],
       'front_overhang_past_deck_edge_mm': round(-Y_H, 1), 'pin_tips_past_deck_edge_mm': round(-(Y_H - PIN_OUT), 1),
       'wire_gap_mm': WIRE_GAP, 'tray_clearance_mm': round(d_tray, 2), 'rail_clearance_mm': rails,
       'print': {'file': PRINT_NAME, 'bbox': [round(pm.BoundBox.XLength, 1), round(pm.BoundBox.YLength, 1), round(pm.BoundBox.ZLength, 1)],
                 'bed_contact_mm2': round(bed), 'downward_faces_mm2': round(down)}}
json.dump(val, open(OUT / 'validation.json', 'w'), indent=1)
p('DONE', json.dumps(val['print']))
