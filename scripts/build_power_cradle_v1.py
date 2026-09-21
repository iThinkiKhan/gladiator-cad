"""Build the Gladiator power-board cradle as a standalone, reversible candidate.

The cradle replaces PowerShield but does not edit the master.  It uses the two
rear ends of the long deck slots as its primary M3 anchors and the rear M2 pair
as light anti-lift/locating fasteners, leaving every mast-base fastener alone.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as App
import MeshPart
import Part

ROOT = Path('/home/buralien/projects/gladiator-cad')
MASTER = ROOT / 'cad/master/Gladiator_Master.FCStd'
OUT = ROOT / 'cad/power-board/v1-cradle'
(OUT / 'stl').mkdir(parents=True, exist_ok=True)

# Installed coordinate system, millimetres.
BOARD_X0, BOARD_Y0 = 19.5, 29.0
BOARD_W, BOARD_L, PCB_T = 40.0, 60.0, 1.6
HOLE_DX, HOLE_DY = 34.5, 54.25
FLOOR_Z, FLOOR_T = 22.2, 1.0
BOARD_Z = 31.2                  # PCB underside; 8 mm clear over the shield
WALL_TOP = BOARD_Z + PCB_T + 1.0
M2_PILOT = 1.6                 # thread-forming pilot in the printed standoffs
M2_CLEAR = 2.2                 # board-reference clearance only
M3_CLEAR = 3.6

board_holes = [
    (BOARD_X0 + (BOARD_W - HOLE_DX) / 2 + ix * HOLE_DX,
     BOARD_Y0 + (BOARD_L - HOLE_DY) / 2 + iy * HOLE_DY)
    for ix in (0, 1) for iy in (0, 1)
]
m3_anchors = [(25.5, 130.5), (53.5, 130.5)]
m2_anchors = [(19.0, 128.0), (60.0, 128.0)]


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0,
                        App.Vector(x0, y0, z0))


def hit(a, b):
    if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    return a.common(b).Volume


before = hashlib.sha256(MASTER.read_bytes()).hexdigest()
master = App.openDocument(str(MASTER))

# Thin insulating back shield with a little margin around the PCB.
cradle = box(18.1, 60.9, 27.6, 90.4, FLOOR_Z, FLOOR_Z + FLOOR_T)

# A continuous perimeter wall protects every edge of the solder side.  The
# wall has 0.4 mm board clearance and stands only 1 mm above the PCB top;
# connectors remain accessible because they all enter vertically from above.
wall_t = 1.0
inner_x0, inner_x1 = BOARD_X0 - 0.4, BOARD_X0 + BOARD_W + 0.4
inner_y0, inner_y1 = BOARD_Y0 - 0.4, BOARD_Y0 + BOARD_L + 0.4
wall_z0 = FLOOR_Z + FLOOR_T
wall_outer = box(inner_x0 - wall_t, inner_x1 + wall_t,
                 inner_y0 - wall_t, inner_y1 + wall_t,
                 wall_z0, WALL_TOP)
wall_void = box(inner_x0, inner_x1, inner_y0, inner_y1,
                wall_z0 - 0.1, WALL_TOP + 0.1)
cradle = cradle.fuse(wall_outer.cut(wall_void))

# PCB standoffs: 6 mm OD and blind M2 thread-forming pilots.  The pilot stops
# above the shield so the solder side remains electrically isolated.
for x, y in board_holes:
    boss = Part.makeCylinder(3.0, BOARD_Z - (FLOOR_Z + FLOOR_T),
                             App.Vector(x, y, FLOOR_Z + FLOOR_T))
    cradle = cradle.fuse(boss)
cradle = cradle.removeSplitter()
for x, y in board_holes:
    pilot = Part.makeCylinder(M2_PILOT / 2, 6.8,
                              App.Vector(x, y, BOARD_Z - 6.7))
    cradle = cradle.cut(pilot)

# Two overhead rails now run over the mast-base rim.  Pads beneath them land on
# the rim's Z20 top surface, so the long spans are supported instead of acting
# as cantilevers.  They merge into rear foot blocks independent of mast screws.
arm_z1 = FLOOR_Z + 3.0
cradle = cradle.fuse(box(25.0, 29.1, 89.4, 134.0, FLOOR_Z, arm_z1))
cradle = cradle.fuse(box(49.9, 54.0, 89.4, 134.0, FLOOR_Z, arm_z1))
cradle = cradle.fuse(box(26.5, 29.1, 100.0, 126.0, 20.0, FLOOR_Z))
cradle = cradle.fuse(box(49.9, 52.5, 100.0, 126.0, 20.0, FLOOR_Z))
cradle = cradle.fuse(box(18.4, 29.0, 127.4, 134.0, 2.2, arm_z1))
cradle = cradle.fuse(box(50.0, 60.6, 127.4, 134.0, 2.2, arm_z1))
# Full top lands support ordinary M3 washers and connect the inboard rails.
cradle = cradle.fuse(box(18.05, 29.1, 126.8, 134.0, 20.0, arm_z1))
cradle = cradle.fuse(box(49.9, 60.95, 126.8, 134.0, 20.0, arm_z1))
cradle = cradle.removeSplitter()

# M3 bolts with ordinary washers through the long slots carry the load.  Their
# top holes are simple 3.6 mm clearances—no ambiguous stepped counterbores.  The
# deck's rear M2 features are 1.6 mm pilots, so matching blind pilots in the
# feet take thread-forming screws from below.
for x, y in m3_anchors:
    cradle = cradle.cut(Part.makeCylinder(M3_CLEAR / 2, arm_z1 - 2.0,
                                           App.Vector(x, y, 2.1)))
for x, y in m2_anchors:
    cradle = cradle.cut(Part.makeCylinder(M2_PILOT / 2, 8.1,
                                           App.Vector(x, y, 2.1)))

cradle = cradle.removeSplitter()

# Reference envelopes for the standalone source file.
board = box(BOARD_X0, BOARD_X0 + BOARD_W, BOARD_Y0, BOARD_Y0 + BOARD_L,
            BOARD_Z, BOARD_Z + PCB_T)
for x, y in board_holes:
    board = board.cut(Part.makeCylinder(M2_CLEAR / 2, PCB_T + 0.2,
                                         App.Vector(x, y, BOARD_Z - 0.1)))
underside = box(BOARD_X0, BOARD_X0 + BOARD_W, BOARD_Y0, BOARD_Y0 + BOARD_L,
                BOARD_Z - 8.0, BOARD_Z)
connector = box(BOARD_X0, BOARD_X0 + BOARD_W, BOARD_Y0, BOARD_Y0 + BOARD_L,
                BOARD_Z + PCB_T, 48.0)

checks = {
    'cradle_valid': cradle.isValid(),
    'cradle_solids': len(cradle.Solids),
    'cradle_volume_cm3': round(cradle.Volume / 1000.0, 2),
    'board_outline_mm': [BOARD_L, BOARD_W, PCB_T],
    'board_hole_pattern_mm': [HOLE_DY, HOLE_DX],
    'board_hole_centres': [[round(x, 3), round(y, 3)] for x, y in board_holes],
    'shield_floor_z': [FLOOR_Z, FLOOR_Z + FLOOR_T],
    'battery_top_z': 21.5,
    'battery_to_shield_gap_mm': round(FLOOR_Z - 21.5, 2),
    'underside_clearance_mm': round(BOARD_Z - (FLOOR_Z + FLOOR_T), 2),
    'pcb_top_z': round(BOARD_Z + PCB_T, 2),
    'connector_budget_to_upper_deck_mm': round(48.0 - (BOARD_Z + PCB_T), 2),
    'm3_slot_anchors': m3_anchors,
    'm2_rear_anchors': m2_anchors,
    'mast_fasteners_shared': False,
    'continuous_perimeter_wall': True,
    'clashes': {},
}

for name in ['ChassisDeck', 'BatteryBox', 'MastBase', 'MastTube',
             'SideRailLeft', 'SideRailRight', 'UpperDeck', 'AntennaPost',
             'S3Board', 'Breadboard', 'DriverMountLeft', 'DriverMountRight']:
    obj = master.getObject(name)
    if not obj or not getattr(obj, 'Shape', None) or obj.Shape.isNull():
        continue
    volume = hit(cradle, obj.Shape)
    # Touching the deck is avoided by the 0.2 mm installed gap.  All reference
    # clashes above numerical fuzz are a failed candidate.
    if volume > 0.05:
        checks['clashes'][name] = round(volume, 2)

# Confirm every screw axis lands in the intended deck feature.
deck = master.getObject('ChassisDeck').Shape
checks['deck_axis_passages'] = {}
for x, y in m3_anchors + m2_anchors:
    dia = M3_CLEAR if (x, y) in m3_anchors else M2_PILOT
    axis = Part.makeCylinder(dia / 2, 2.4, App.Vector(x, y, -0.2))
    checks['deck_axis_passages']['%.1f,%.1f' % (x, y)] = round(hit(axis, deck), 4)

# Bearing retained under standard-size heads/washers at the top of the feet.
checks['top_bearing_mm2'] = {}
checks['pilot_thread_wall_mm3'] = {}
for x, y in m3_anchors:
    ring = Part.makeCylinder(3.5, 0.3, App.Vector(x, y, arm_z1 - 0.3)).cut(
        Part.makeCylinder(M3_CLEAR / 2, 0.4,
                          App.Vector(x, y, arm_z1 - 0.35)))
    checks['top_bearing_mm2']['M3 %.1f,%.1f' % (x, y)] = round(hit(ring, cradle) / 0.3, 2)
for x, y in m2_anchors:
    shell = Part.makeCylinder(2.2, 8.0, App.Vector(x, y, 2.2)).cut(
        Part.makeCylinder(M2_PILOT / 2, 8.1, App.Vector(x, y, 2.15)))
    checks['pilot_thread_wall_mm3']['M2 %.1f,%.1f' % (x, y)] = round(hit(shell, cradle), 2)

# Board-post material and mast-rim bearing are explicit release checks.
checks['board_post_thread_wall_mm3'] = {}
for x, y in board_holes:
    shell = Part.makeCylinder(3.0, 6.6, App.Vector(x, y, BOARD_Z - 6.6)).cut(
        Part.makeCylinder(M2_PILOT / 2, 6.7, App.Vector(x, y, BOARD_Z - 6.65)))
    checks['board_post_thread_wall_mm3']['%.3f,%.3f' % (x, y)] = round(hit(shell, cradle), 2)
mast = master.getObject('MastBase').Shape
left_contact = box(26.5, 29.1, 100.0, 126.0, 19.8, 20.0)
right_contact = box(49.9, 52.5, 100.0, 126.0, 19.8, 20.0)
checks['mast_support_contact_mm2'] = round(
    (hit(left_contact, mast) + hit(right_contact, mast)) / 0.2, 2)

checks['master_unchanged'] = hashlib.sha256(MASTER.read_bytes()).hexdigest() == before

doc = App.newDocument('PowerBoardCradle_v1')
part = doc.addObject('Part::Feature', 'PowerBoardCradle')
part.Label = 'Power board cradle v1 - installed position'
part.Shape = cradle
part.addProperty('App::PropertyString', 'BoardSize', 'Design').BoardSize = '60 x 40 x 1.6 mm'
part.addProperty('App::PropertyString', 'HolePattern', 'Design').HolePattern = '54.25 x 34.5 mm; 4 x M2'
part.addProperty('App::PropertyString', 'DeckMounts', 'Design').DeckMounts = '2 x rear M3 slot + rear M2 pair; no mast screws'
for name, label, shape in [
    ('BoardReference', 'Power board reference', board),
    ('UndersideKeepout', '8 mm solder-side keepout', underside),
    ('ConnectorKeepout', 'Available top connector envelope to Z48', connector),
]:
    obj = doc.addObject('Part::Feature', name)
    obj.Label = label
    obj.Shape = shape
doc.recompute()
doc.saveAs(str(OUT / 'PowerBoardCradle_v1.FCStd'))

Part.export([part], str(OUT / 'PowerBoardCradle_v1.step'))

# Installed STL, plus the recommended side-print orientation (-Y face down).
mesh = MeshPart.meshFromShape(Shape=cradle, LinearDeflection=0.08,
                              AngularDeflection=0.25, Relative=False)
mesh.write(str(OUT / 'stl/PowerBoardCradle_v1_installed.stl'))
print_shape = cradle.copy()
print_shape.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90.0)
bb = print_shape.BoundBox
print_shape.translate(App.Vector(-bb.XMin, -bb.YMin, -bb.ZMin))
checks['print_bbox_mm'] = [round(print_shape.BoundBox.XLength, 2),
                           round(print_shape.BoundBox.YLength, 2),
                           round(print_shape.BoundBox.ZLength, 2)]
bed_probe = Part.makeBox(print_shape.BoundBox.XLength + 2.0,
                         print_shape.BoundBox.YLength + 2.0, 0.2,
                         App.Vector(-1.0, -1.0, 0.0))
checks['print_bed_contact_mm2'] = round(hit(print_shape, bed_probe) / 0.2, 2)
print_mesh = MeshPart.meshFromShape(Shape=print_shape, LinearDeflection=0.08,
                                    AngularDeflection=0.25, Relative=False)
print_mesh.write(str(OUT / 'stl/PowerBoardCradle_v1_print-on-rear-face.stl'))

with (OUT / 'validation.json').open('w', encoding='utf-8') as handle:
    json.dump(checks, handle, indent=2)
    handle.write('\n')

print(json.dumps(checks, indent=2))
App.closeDocument(doc.Name)
App.closeDocument(master.Name)

if not checks['cradle_valid'] or checks['cradle_solids'] != 1 or checks['clashes']:
    raise SystemExit('candidate failed geometry validation')
