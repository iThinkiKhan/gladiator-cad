"""Build the Gladiator power-board cradle v2: reinforced arm roots + 5mm more
overall length, split front/back.  Same mounting strategy as v1 (does not
edit the master, does not move the deck M2 anchors or the PCB standoff
holes).

Changes from v1, per Jim's 2026-09-23 feedback after the v1 print:
  1. Both overhead arms sheared off where they met the main body.  v1 had
     only a 1.0 mm Y-overlap between each arm and the body/wall there, so
     the whole cantilevered arm (37 mm out to the mast rim) funnelled its
     bending load through a ~4 mm x 2 mm cross-section with no fillet.
     v2 replaces the single arm box with a root / taper / rail sequence
     that flares out to a wide, tall base tied into the existing wall mass
     (mirroring the flare-to-column taper v1 already used at the rear) and
     resumes a slightly thicker rail after the taper.
  2. Overall tray footprint is 5 mm longer: +2.5 mm at the front edge of
     the body/wall, +2.5 mm at the back edge of the low mounting tabs.
     The PCB standoff holes (board_holes) and the deck M2 anchors
     (slot_anchors, m2_anchors) are untouched -- confirmed clear of
     BatteryBox/ChassisDeck/MastBase/MastTube by direct solid queries
     before this script was written (see docs/ai/HANDOFF.md).
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
OUT = ROOT / 'cad/power-board/v2-cradle'
(OUT / 'stl').mkdir(parents=True, exist_ok=True)

# Installed coordinate system, millimetres.
BOARD_X0, BOARD_Y0 = 19.5, 29.0
BOARD_W, BOARD_L, PCB_T = 40.0, 60.0, 1.6
HOLE_DX, HOLE_DY = 34.5, 54.25
FLOOR_Z, FLOOR_T = 22.2, 1.0
BOARD_Z = 30.2                  # PCB underside; 7 mm clear over the shield
WALL_TOP = BOARD_Z + PCB_T + 1.0
M2_PILOT = 1.6                 # thread-forming pilot in the printed standoffs
M2_CLEAR = 2.2
BOARD_PILOT_DEPTH = 5.5
TAB_TOP = 5.2

FRONT_EXTRA = 2.5               # v2: extra length at the front edge
BACK_EXTRA = 2.5                # v2: extra length at the back edge

board_holes = [
    (BOARD_X0 + (BOARD_W - HOLE_DX) / 2 + ix * HOLE_DX,
     BOARD_Y0 + (BOARD_L - HOLE_DY) / 2 + iy * HOLE_DY)
    for ix in (0, 1) for iy in (0, 1)
]
slot_anchors = [(25.5, 130.5), (53.5, 130.5)]
m2_anchors = [(19.0, 128.0), (60.0, 128.0)]


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0,
                        App.Vector(x0, y0, z0))


def plan_prism(points, z0, z1):
    wire = [App.Vector(x, y, z0) for x, y in points]
    face = Part.Face(Part.makePolygon(wire + [wire[0]]))
    return face.extrude(App.Vector(0, 0, z1 - z0))


def hit(a, b):
    if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    return a.common(b).Volume


before = hashlib.sha256(MASTER.read_bytes()).hexdigest()
master = App.openDocument(str(MASTER))

# Thin insulating back shield with a little margin around the PCB.
# v2: front edge moved from 27.6 to 27.6 - FRONT_EXTRA (25.1).
FLOOR_Y0 = 27.6 - FRONT_EXTRA
cradle = box(18.1, 60.9, FLOOR_Y0, 90.4, FLOOR_Z, FLOOR_Z + FLOOR_T)

# A continuous perimeter wall protects every edge of the solder side.  The
# wall has 0.4 mm board clearance and stands only 1 mm above the PCB top;
# connectors remain accessible because they all enter vertically from above.
wall_t = 1.0
inner_x0, inner_x1 = BOARD_X0 - 0.4, BOARD_X0 + BOARD_W + 0.4
inner_y0, inner_y1 = BOARD_Y0 - 0.4, BOARD_Y0 + BOARD_L + 0.4
wall_z0 = FLOOR_Z + FLOOR_T
# v2: outer wall front edge extended by the same FRONT_EXTRA as the floor.
# (Y is the tray's length axis; X is its width -- FRONT_EXTRA must move the
# Y-start, not the X-min, or it eats into SideRailLeft's clearance.)
wall_outer = box(inner_x0 - wall_t, inner_x1 + wall_t,
                 inner_y0 - wall_t - FRONT_EXTRA, inner_y1 + wall_t,
                 wall_z0, WALL_TOP)
wall_void = box(inner_x0, inner_x1, inner_y0, inner_y1,
                wall_z0 - 0.1, WALL_TOP + 0.1)
cradle = cradle.fuse(wall_outer.cut(wall_void))

# PCB standoffs: 6 mm OD and blind M2 thread-forming pilots.  The pilot stops
# above the shield so the solder side remains electrically isolated.
# Unchanged from v1 -- these must stay exactly where the PCB's own screw
# holes are.
for x, y in board_holes:
    boss = Part.makeCylinder(3.0, BOARD_Z - (FLOOR_Z + FLOOR_T),
                             App.Vector(x, y, FLOOR_Z + FLOOR_T))
    cradle = cradle.fuse(boss)
cradle = cradle.removeSplitter()
for x, y in board_holes:
    pilot = Part.makeCylinder(M2_PILOT / 2, BOARD_PILOT_DEPTH + 0.1,
                              App.Vector(x, y, BOARD_Z - BOARD_PILOT_DEPTH))
    cradle = cradle.cut(pilot)

# --- v2 arm reinforcement -------------------------------------------------
# Each arm is now a root / taper / rail sequence instead of one thin box.
# The root ties directly into the wall mass (which is already solid, full
# width, up to Z32.8, across Y89.4-90.4) with a wide, tall block; the taper
# steps down; the rail is the same run length as v1 but slightly thicker.
# Clearance for every zone below was confirmed against ChassisDeck,
# BatteryBox, MastBase, MastTube, SideRails, AntennaPost, UpperDeck and the
# driver mounts by direct solid probes -- nothing occupies this airspace.
arm_specs = [
    # (x0, x1) for root, taper, rail -- left arm, then right arm
    dict(root=(22.0, 32.1), taper=(24.0, 30.1), rail=(25.0, 29.1)),
    dict(root=(46.9, 57.0), taper=(48.9, 55.0), rail=(49.9, 54.0)),
]
ROOT_Y0, ROOT_Y1 = 89.4, 96.0
TAPER_Y0, TAPER_Y1 = 96.0, 104.0
RAIL_Y0, RAIL_Y1 = 104.0, 126.8
ROOT_Z1 = 30.0
TAPER_Z1 = 27.5
RAIL_Z1 = 26.0        # was 25.2 in v1; a bit thicker for stiffness

for spec in arm_specs:
    rx0, rx1 = spec['root']
    tx0, tx1 = spec['taper']
    lx0, lx1 = spec['rail']
    cradle = cradle.fuse(box(rx0, rx1, ROOT_Y0, ROOT_Y1, FLOOR_Z, ROOT_Z1))
    cradle = cradle.fuse(box(tx0, tx1, TAPER_Y0, TAPER_Y1, FLOOR_Z, TAPER_Z1))
    cradle = cradle.fuse(box(lx0, lx1, RAIL_Y0, RAIL_Y1, FLOOR_Z, RAIL_Z1))
cradle = cradle.removeSplitter()

# Support pads/columns on the mast rim, and the rear flare brackets -- as
# v1, unchanged; they already fuse cleanly onto the new taller rail tail.
cradle = cradle.fuse(box(26.5, 29.1, 100.0, 126.0, 20.0, FLOOR_Z))
cradle = cradle.fuse(box(49.9, 52.5, 100.0, 126.0, 20.0, FLOOR_Z))
# Low mounting tabs keep both screw heads exposed just above the deck.
# v2: back edge extended from 134.0 to 134.0 + BACK_EXTRA (136.5).
TAB_Y1 = 134.0 + BACK_EXTRA
cradle = cradle.fuse(box(18.4, 32.7, 127.4, TAB_Y1, 2.2, TAB_TOP))
cradle = cradle.fuse(box(46.3, 60.6, 127.4, TAB_Y1, 2.2, TAB_TOP))
# Four-millimetre rear columns are offset from the M2 service screws.
cradle = cradle.fuse(box(28.7, 32.7, 127.4, TAB_Y1, TAB_TOP, RAIL_Z1))
cradle = cradle.fuse(box(46.3, 50.3, 127.4, TAB_Y1, TAB_TOP, RAIL_Z1))
# Full-width flares overlap the rails for several millimetres, then wrap around
# the offset columns. Their vertical section acts as an integral gusset.
left_flare = [(25.0, 123.0), (29.1, 123.0), (32.7, 127.4),
              (32.7, 134.0), (28.7, 134.0), (28.7, 128.5),
              (25.0, 126.0)]
right_flare = [(54.0, 123.0), (49.9, 123.0), (46.3, 127.4),
               (46.3, 134.0), (50.3, 134.0), (50.3, 128.5),
               (54.0, 126.0)]
cradle = cradle.fuse(plan_prism(left_flare, 20.0, RAIL_Z1))
cradle = cradle.fuse(plan_prism(right_flare, 20.0, RAIL_Z1))
cradle = cradle.removeSplitter()

# Short M2 bolts with washers through the low tabs and deck slots carry the
# load. The deck's rear M2 features are 1.6 mm pilots, so matching blind pilots
# in the low tabs take short thread-forming screws from below.
# Anchor coordinates are unchanged from v1 -- these match already-existing
# holes in the fixed aluminium deck and must not move.
for x, y in slot_anchors:
    cradle = cradle.cut(Part.makeCylinder(M2_CLEAR / 2, TAB_TOP - 2.0,
                                           App.Vector(x, y, 2.1)))
for x, y in m2_anchors:
    cradle = cradle.cut(Part.makeCylinder(M2_PILOT / 2, TAB_TOP - 2.3,
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
    'm2_slot_anchors': slot_anchors,
    'm2_rear_anchors': m2_anchors,
    'mast_fasteners_shared': False,
    'continuous_perimeter_wall': True,
    'front_extra_mm': FRONT_EXTRA,
    'back_extra_mm': BACK_EXTRA,
    'overall_length_mm': round(TAB_Y1 - FLOOR_Y0, 2),
    'clashes': {},
}

for name in ['ChassisDeck', 'BatteryBox', 'MastBase', 'MastTube',
             'SideRailLeft', 'SideRailRight', 'UpperDeck', 'AntennaPost',
             'S3Board', 'Breadboard', 'DriverMountLeft', 'DriverMountRight']:
    obj = master.getObject(name)
    if not obj or not getattr(obj, 'Shape', None) or obj.Shape.isNull():
        continue
    volume = hit(cradle, obj.Shape)
    if volume > 0.05:
        checks['clashes'][name] = round(volume, 2)

# Confirm every screw axis lands in the intended deck feature.
deck = master.getObject('ChassisDeck').Shape
checks['deck_axis_passages'] = {}
for x, y in slot_anchors + m2_anchors:
    dia = M2_CLEAR if (x, y) in slot_anchors else M2_PILOT
    axis = Part.makeCylinder(dia / 2, 2.4, App.Vector(x, y, -0.2))
    checks['deck_axis_passages']['%.1f,%.1f' % (x, y)] = round(hit(axis, deck), 4)

# Bearing retained under standard-size heads/washers at the top of the feet.
checks['top_bearing_mm2'] = {}
checks['pilot_thread_wall_mm3'] = {}
checks['slot_driver_access_clear'] = {}
for x, y in slot_anchors:
    ring = Part.makeCylinder(2.5, 0.3, App.Vector(x, y, TAB_TOP - 0.3)).cut(
        Part.makeCylinder(M2_CLEAR / 2, 0.4,
                          App.Vector(x, y, TAB_TOP - 0.35)))
    checks['top_bearing_mm2']['M2 slot %.1f,%.1f' % (x, y)] = round(hit(ring, cradle) / 0.3, 2)
    driver = Part.makeCylinder(3.0, 43.0, App.Vector(x, y, TAB_TOP + 0.1))
    checks['slot_driver_access_clear']['%.1f,%.1f' % (x, y)] = hit(driver, cradle) < 0.05
for x, y in m2_anchors:
    shell = Part.makeCylinder(2.2, TAB_TOP - 2.3, App.Vector(x, y, 2.2)).cut(
        Part.makeCylinder(M2_PILOT / 2, TAB_TOP - 2.2, App.Vector(x, y, 2.15)))
    checks['pilot_thread_wall_mm3']['M2 %.1f,%.1f' % (x, y)] = round(hit(shell, cradle), 2)

# Board-post material and mast-rim bearing are explicit release checks.
checks['board_post_thread_wall_mm3'] = {}
for x, y in board_holes:
    shell = Part.makeCylinder(3.0, BOARD_PILOT_DEPTH - 0.2,
                              App.Vector(x, y, BOARD_Z - BOARD_PILOT_DEPTH)).cut(
        Part.makeCylinder(M2_PILOT / 2, BOARD_PILOT_DEPTH - 0.1,
                          App.Vector(x, y, BOARD_Z - BOARD_PILOT_DEPTH - 0.05)))
    checks['board_post_thread_wall_mm3']['%.3f,%.3f' % (x, y)] = round(hit(shell, cradle), 2)
mast = master.getObject('MastBase').Shape
left_contact = box(26.5, 29.1, 100.0, 126.0, 19.8, 20.0)
right_contact = box(49.9, 52.5, 100.0, 126.0, 19.8, 20.0)
checks['mast_support_contact_mm2'] = round(
    (hit(left_contact, mast) + hit(right_contact, mast)) / 0.2, 2)

# v2-specific: bonded cross-section at each arm root, to confirm the fix is
# real and not just moving the thin joint somewhere else.  Sampled just past
# the wall at Y=90.4-92.4 (2mm slice), full local root width, full height.
checks['arm_root_bond_mm2'] = {}
for label, (rx0, rx1) in [('left', arm_specs[0]['root']), ('right', arm_specs[1]['root'])]:
    probe = box(rx0, rx1, 90.4, 92.4, FLOOR_Z, ROOT_Z1)
    checks['arm_root_bond_mm2'][label] = round(hit(cradle, probe) / 2.0, 2)

checks['master_unchanged'] = hashlib.sha256(MASTER.read_bytes()).hexdigest() == before

doc = App.newDocument('PowerBoardCradle_v2')
part = doc.addObject('Part::Feature', 'PowerBoardCradle')
part.Label = 'Power board cradle v2 - reinforced arms, +5mm length'
part.Shape = cradle
part.addProperty('App::PropertyString', 'BoardSize', 'Design').BoardSize = '60 x 40 x 1.6 mm'
part.addProperty('App::PropertyString', 'HolePattern', 'Design').HolePattern = '54.25 x 34.5 mm; 4 x M2'
part.addProperty('App::PropertyString', 'DeckMounts', 'Design').DeckMounts = '2 x exposed M2 in rear slots + rear M2 pilot pair; no mast screws'
for name, label, shape in [
    ('BoardReference', 'Power board reference', board),
    ('UndersideKeepout', '8 mm solder-side keepout', underside),
    ('ConnectorKeepout', 'Available top connector envelope to Z48', connector),
]:
    obj = doc.addObject('Part::Feature', name)
    obj.Label = label
    obj.Shape = shape
doc.recompute()
doc.saveAs(str(OUT / 'PowerBoardCradle_v2.FCStd'))

Part.export([part], str(OUT / 'PowerBoardCradle_v2.step'))

# Installed STL, plus the recommended side-print orientation (-Y face down).
# Fine tessellation throughout -- bare/coarse deflection undersizes holes.
mesh = MeshPart.meshFromShape(Shape=cradle, LinearDeflection=0.01,
                              AngularDeflection=0.05, Relative=False)
mesh.write(str(OUT / 'stl/PowerBoardCradle_v2_installed.stl'))
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
print_mesh = MeshPart.meshFromShape(Shape=print_shape, LinearDeflection=0.01,
                                    AngularDeflection=0.05, Relative=False)
print_mesh.write(str(OUT / 'stl/PowerBoardCradle_v2_print-on-rear-face.stl'))

with (OUT / 'validation.json').open('w', encoding='utf-8') as handle:
    json.dump(checks, handle, indent=2)
    handle.write('\n')

print(json.dumps(checks, indent=2))
App.closeDocument(doc.Name)
App.closeDocument(master.Name)

if not checks['cradle_valid'] or checks['cradle_solids'] != 1 or checks['clashes']:
    raise SystemExit('candidate failed geometry validation')
