"""Build the power switch holder v1b: a small housing for the slide power switch that hangs on the
ROBOT'S LEFT side rail's raceway floor, beside the rear leg, between the rail and the power tray's leg.
The rail, tray and master are only read.  Refuses to export if any check fails.

v1b = v1 mirrored onto the other rail (Jim, 2026-10-05: "this is shaped to fit the right leg, not the left").
HANDEDNESS: the master has the front at Y 0 and Z up, so its low-X side is the robot's RIGHT.  The objects
named SideRailLeft / "Base, left" are physically on the robot's right.  The robot's left rail is the master's
SideRailRight (X 61-73).  The layout below is written on the low-X rail (where it was first worked out) and then
mirrored about the deck centre X 39.5; every check runs against the real high-X rail, tray and right base.
Knob width 4.0 (Jim, 2026-10-05), so the 5.0 window leaves 0.5 each side.

Layout (Jim, 2026-10-05):
  - Knob faces the REAR, pins point FORWARD.  Not toward the tray legs, not toward the rail.
  - Slide axis vertical; UP is ON.
  - "Right on the floor of the upper wire runner and the rear leg space"; the raceway floor carries it.
  - Must not stop the power tray lifting out, or the upper deck going on.

Switch (Jim, calipers, 2026-10-05): body 6.8 wide x 12.7 tall (slide axis) x 6.37 deep (knob face to pin
face).  Knob stands 5.0 off the body.  Knob envelope along the slide axis, travel included, is 6.0.
Pins 3.7 long.  Pin tip to knob top 15.0 (= 3.7 + 6.37 + 5.0, checks).
  ASSUMED, NOT MEASURED: knob width <= 4.4 (window is 5.0 wide); pins in one row down the middle of the
  pin face (only used to check the pins clear things; the pin face is fully open).

Placement (rail coordinates, left rail X 6-18):
  - Raceway floor slab Z 36.5-38.5, inboard edge X 18, runs to the rail's sealed rear wall at Y 132.
  - Tray left leg: X >= 25.0 forward of Y 128, >= 27.96 for Y 128-130, >= 28.7 from Y 130 back.
  - Left base: X >= 18.4, Y 127.4-139.9, Z <= 17.2.
  So the switch body sits Y 128.6-135.0, X 19.35-26.15: behind the step in the leg, beside the rail's rear wall.
  Knob top at Y 140.0, flush with the lower deck's rear edge; 5.0 past the rail's rear face.

Holding it: a C-clip (two tongues, 0.1 gap each side) slides over the raceway floor's inboard edge from
the inboard side.  A rear flange wraps 3.7 behind the rail's rear face, so it cannot slide forward; the
tongues stop it sliding back against the rail's rear wall.  Once the tray is in, the leg (0.66 away at
the closest) stops it backing off the 5 mm tongue overlap, so it cannot fall off.  Fit the holder with
the tray out.  The switch pushes in from the front (pins last) into a snug pocket (0.15 per side;
flat walls print about 0.1-0.25 over on this printer).
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
TRAY = ROOT / 'cad/power-board/v5-tray/PowerBoardTray_v5.FCStd'
OUT = ROOT / 'cad/power-switch/v1b'
INCOMING = Path('/home/buralien/3D-Printer/Incoming/Gladiator')
(OUT / 'stl').mkdir(parents=True, exist_ok=True)
PRINT_NAME = 'Gladiator_PowerSwitchHolder_v1b_robot-LEFT-rail_print-on-inboard-face_no-supports.stl'

FAILS = []
RESULTS = {}


def p(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n'); sys.stdout.flush()


def check(ok, msg):
    p(('PASS ' if ok else 'FAIL ') + msg)
    if not ok:
        FAILS.append(msg)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def hit(a, b):
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


# ---- switch (Jim's numbers) -------------------------------------------------------------
SW_W, SW_L, SW_D = 6.8, 12.7, 6.37
KNOB_H, KNOB_ENV, PIN_L = 5.0, 6.0, 3.7
KNOB_W = 4.0                 # Jim, 2026-10-05

# ---- fixed geometry read from the model (asserted below) --------------------------------
SLAB_Z0, SLAB_Z1, SLAB_EDGE_X = 36.5, 38.5, 18.0
RAIL_REAR_WALL_Y0, RAIL_REAR_Y = 132.0, 135.0

# ---- layout ---------------------------------------------------------------------------
CL = 0.15                    # pocket clearance per side
WALL = 1.0                   # side walls
PLATE = 1.2                  # rear plate, floor, ceiling
TONGUE_T = 1.5
TONGUE_GAP = 0.1             # each side of the 2.0 slab
TONGUE_X0 = 13.0             # tongue tips (5.0 overlap on the slab)
KNOB_FACE_Y = 135.0          # body rear face; knob top lands at 140.0
BODY_TOP_Z = 36.4            # body just under the slab level
OUT_X0 = 18.2                # outboard wall's outer face, 0.2 off the rail's inboard face
FLANGE_X0 = 14.5             # rear flange reaches behind the rail's rear face
WINDOW_W = 5.0
WINDOW_L = KNOB_ENV + 0.8

pocket_x0 = OUT_X0 + WALL
pocket_x1 = pocket_x0 + SW_W + 2 * CL
in_x1 = pocket_x1 + WALL
body_x0 = pocket_x0 + CL
body_xc = body_x0 + SW_W / 2
body_y0 = KNOB_FACE_Y - SW_D
body_z0 = BODY_TOP_Z - SW_L
body_zc = body_z0 + SW_L / 2
pocket_y0 = body_y0                          # front open, flush with the body's pin face
pocket_y1 = KNOB_FACE_Y + 0.1
pocket_z0 = body_z0 - CL
pocket_z1 = BODY_TOP_Z + CL
plate_y1 = pocket_y1 + PLATE
floor_z0 = pocket_z0 - PLATE
ceil_z1 = pocket_z1 + PLATE
lt_z1 = SLAB_Z0 - TONGUE_GAP                 # lower tongue under the slab
lt_z0 = lt_z1 - TONGUE_T
ut_z0 = SLAB_Z1 + TONGUE_GAP                 # upper tongue on the raceway floor
ut_z1 = ut_z0 + TONGUE_T
tongue_y1 = RAIL_REAR_WALL_Y0 - 0.2

# housing
outer = box(OUT_X0, in_x1, pocket_y0, plate_y1, floor_z0, ceil_z1)
pocket = box(pocket_x0, pocket_x1, pocket_y0 - 1, pocket_y1, pocket_z0, pocket_z1)
window = box(body_xc - WINDOW_W / 2, body_xc + WINDOW_W / 2, pocket_y1 - 1, plate_y1 + 1,
             body_zc - WINDOW_L / 2, body_zc + WINDOW_L / 2)
housing = outer.cut(pocket).cut(window)
# outboard wall rises to carry the upper tongue
housing = housing.fuse(box(OUT_X0, pocket_x0, pocket_y0, plate_y1, floor_z0, ut_z1))
# 45 degree gusset under that riser, so it does not overhang when printed on the inboard face
gus = Part.Face(Part.makePolygon([V(pocket_x0 - 0.01, 0, ceil_z1 - 0.01), V(pocket_x0 + (ut_z1 - ceil_z1), 0, ceil_z1 - 0.01),
                                  V(pocket_x0 - 0.01, 0, ut_z1), V(pocket_x0 - 0.01, 0, ceil_z1 - 0.01)]))
gus.translate(V(0, pocket_y0, 0))
housing = housing.fuse(gus.extrude(V(0, plate_y1 - pocket_y0, 0)))
# tongues
housing = housing.fuse(box(TONGUE_X0, pocket_x0, pocket_y0, tongue_y1, lt_z0, lt_z1))
housing = housing.fuse(box(TONGUE_X0, pocket_x0, pocket_y0, tongue_y1, ut_z0, ut_z1))
# rear flange behind the rail's rear face
housing = housing.fuse(box(FLANGE_X0, OUT_X0 + 0.01, RAIL_REAR_Y + 0.1, plate_y1, floor_z0, ceil_z1))
# ON arrow, engraved 0.4 into the rear face above the window, pointing up
tri_z0 = body_zc + WINDOW_L / 2 + 0.9
tri = Part.Face(Part.makePolygon([V(body_xc - 1.6, 0, tri_z0), V(body_xc + 1.6, 0, tri_z0),
                                  V(body_xc, 0, tri_z0 + 2.6), V(body_xc - 1.6, 0, tri_z0)]))
tri.translate(V(0, plate_y1 - 0.4, 0))
housing = housing.cut(tri.extrude(V(0, 1.0, 0)))
housing = housing.removeSplitter()

# switch reference envelopes
sw_body = box(body_x0, body_x0 + SW_W, body_y0, KNOB_FACE_Y, body_z0, BODY_TOP_Z)
sw_knob = box(body_xc - KNOB_W / 2, body_xc + KNOB_W / 2, KNOB_FACE_Y, KNOB_FACE_Y + KNOB_H,
              body_zc - KNOB_ENV / 2, body_zc + KNOB_ENV / 2)
sw_pins = box(body_xc - 0.6, body_xc + 0.6, body_y0 - PIN_L, body_y0, body_z0 + 1.0, BODY_TOP_Z - 1.0)
# room for the solder joints and wire ends ahead of the pins
wire_zone = box(body_xc - 2.0, body_xc + 2.0, body_y0 - PIN_L - 4.0, body_y0, body_z0, BODY_TOP_Z)

# ---- mirror onto the robot's left rail (master high-X side) ------------------------------
CX = 39.5


def M(s):
    return s.mirror(V(CX, 0, 0), V(1, 0, 0))


def mbox(*a):
    return M(box(*a))


housing, sw_body, sw_knob, sw_pins, wire_zone = [M(s) for s in (housing, sw_body, sw_knob, sw_pins, wire_zone)]

# ---- read the world ----------------------------------------------------------------------
doc = App.openDocument(str(MASTER))
rail = doc.getObject('SideRailRight').Shape     # robot's LEFT rail
world = {}
for o in doc.Objects:
    if not hasattr(o, 'Shape') or o.Shape.isNull() or not o.Shape.Solids:
        continue
    if 'Reference' in o.Label or 'Field' in o.Label or 'Tool' in o.Name or o.Name.endswith('Tool'):
        continue
    if o.Name in ('BatteryCells',):
        world[o.Name] = o.Shape
        continue
    if o.TypeId in ('PartDesign::Body', 'Part::Mirroring', 'Part::Feature', 'Part::Box'):
        world[o.Name] = o.Shape
# the master's PowerShield is the superseded cradle; the v5 tray replaces it
world.pop('PowerShield', None)
td = App.openDocument(str(TRAY))
tray = base_r = None
for o in td.Objects:
    if hasattr(o, 'Shape') and o.Label.startswith('Power board tray'):
        tray = o.Shape
    if hasattr(o, 'Shape') and o.Label.startswith('Base, right'):
        base_r = o.Shape
world['TrayV5'] = tray
world['BaseRightV5'] = base_r

# ---- checks -------------------------------------------------------------------------------
check(housing.isValid() and len(housing.Solids) == 1, 'housing is one valid solid')
# the model is what this script assumes
slab = mbox(8.6, 17.9, 120, 131.9, SLAB_Z0 + 0.05, SLAB_Z1 - 0.05)
check(abs(hit(rail, slab) - slab.Volume) < 1e-3, 'raceway floor is solid Z %.1f-%.1f to X %.1f' % (SLAB_Z0, SLAB_Z1, SLAB_EDGE_X))
check(hit(rail, mbox(18.0, 18.5, 119, 132, SLAB_Z0, SLAB_Z1)) < 1e-6, 'raceway floor edge is at X 18')
check(hit(rail, mbox(TONGUE_X0 - 0.5, 17.9, 120, 131.9, SLAB_Z1 + 0.05, SLAB_Z1 + 1.8)) < 1e-6, 'raceway floor is clear above (tongue path)')
check(hit(rail, mbox(TONGUE_X0 - 0.5, 17.9, 120, 131.9, SLAB_Z0 - 1.8, SLAB_Z0 - 0.05)) < 1e-6, 'rear well is clear under the floor (tongue path)')
check(abs(hit(rail, mbox(6.1, 17.9, 132.05, 134.95, 10, 50)) - 11.8 * 2.9 * 40) < 1e-2, 'rail rear wall solid Y 132-135')

for name, shp in sorted(world.items()):
    v = hit(housing, shp)
    if name in ('SideRailRight', 'TrayV5', 'BaseRightV5', 'UpperDeck', 'ChassisDeck') or v != 0:
        check(abs(v) < 1e-6, 'housing vs %s: %.4f mm3' % (name, v))
d_rail = housing.distToShape(rail)[0]
d_tray = housing.distToShape(tray)[0]
d_base = housing.distToShape(base_r)[0]
d_ud = housing.distToShape(world['UpperDeck'])[0]
check(d_rail >= 0.099, 'housing to rail %.2f' % d_rail)
check(d_tray >= 0.5, 'housing to tray %.2f (static)' % d_tray)
check(d_base >= 3.0, 'housing to right-named base (robot left) %.2f' % d_base)
check(d_ud >= 10.0, 'housing to upper deck %.2f' % d_ud)

# tray lifts straight up: sweep it through 60 mm
near = tray.common(mbox(15, 45, 110, 142, 0, 45))
lift = 0.0
for dz in [i * 0.5 for i in range(0, 121)]:
    lift += hit(housing, near.translated(V(0, 0, dz)))
check(lift < 1e-6, 'tray lift path (0-60 up) clear of the housing: %.4f' % lift)
# and of the switch
sw_all = sw_body.fuse([sw_knob, sw_pins])
lift_sw = sum(hit(sw_all, near.translated(V(0, 0, i * 0.5))) for i in range(0, 121))
check(lift_sw < 1e-6, 'tray lift path clear of the switch: %.4f' % lift_sw)

# switch fits the housing and touches nothing in the robot
check(hit(sw_body, housing) < 1e-6, 'switch body vs housing: %.4f' % hit(sw_body, housing))
check(hit(sw_knob, housing) < 1e-6, 'knob (both ends of travel) clears the window: %.4f' % hit(sw_knob, housing))
for name, shp in sorted(world.items()):
    for lab, s in (('switch', sw_all), ('wire zone', wire_zone)):
        v = hit(s, shp)
        if v != 0:
            check(False, '%s vs %s: %.4f' % (lab, name, v))
check(hit(wire_zone, housing) < 1e-6, 'pins + 4 mm ahead of them are open (housing %.4f)' % hit(wire_zone, housing))
knob_top = KNOB_FACE_Y + KNOB_H
check(knob_top <= 140.0 + 1e-6, 'knob top Y %.2f, within the deck edge (140)' % knob_top)
win_margin = (WINDOW_W - KNOB_W) / 2
check(win_margin >= 0.25, 'window %.1f wide; %.2f each side of the 4.0 knob' % (WINDOW_W, win_margin))
lip = (SW_W - WINDOW_W) / 2
check(lip >= 0.8, 'rear plate laps the body by %.2f each side' % lip)

# retention: how far can it back off with the tray in?
play_x = min(near.distToShape(housing)[0], 99)
overlap = SLAB_EDGE_X - TONGUE_X0
check(play_x < overlap - 2.0, 'with the tray in: max inboard play %.2f vs tongue overlap %.1f' % (play_x, overlap))
# fitting: slide on from inboard (tray out) along -X, path clear of the rail
slide = sum(hit(housing.translated(V(-dx, 0, 0)), rail) for dx in [i * 0.5 for i in range(0, 15)])
check(slide < 1e-6, 'slide-on path (7 mm, inboard to fitted) clear of the rail: %.4f' % slide)
# forward/backward captured
check(housing.distToShape(rail)[0] < 0.25, 'flange/tongues hold it 0.1-0.2 off the rail both ways')

p('housing volume %.1f mm3, ~%.1f g PLA' % (housing.Volume, housing.Volume * 1.24e-3))
bb = housing.BoundBox
p('housing bbox X %.2f..%.2f Y %.2f..%.2f Z %.2f..%.2f' % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))

if FAILS:
    p('\n%d FAILED; nothing exported' % len(FAILS))
    sys.exit(1)

# ---- export -------------------------------------------------------------------------------
# print on the inboard face: tongues and flange stand up, nothing overhangs but a 7.1 bridge
pr = housing.copy()
pr.rotate(V(0, 0, 0), V(0, 1, 0), -90)      # +X -> +Z, so the inboard face (min X on this rail) goes to the bottom
pb = pr.BoundBox
pr.translate(V(-pb.XMin, -pb.YMin, -pb.ZMin))
pb = pr.BoundBox
bottom = sum(f.Area for f in pr.Faces if abs(f.BoundBox.ZMax) < 1e-6 and abs(f.BoundBox.ZMin) < 1e-6)
check(bottom > 100, 'bed contact %.0f mm2' % bottom)
if FAILS:
    p('print orientation check failed; nothing exported')
    sys.exit(1)

ndoc = App.newDocument('PowerSwitchHolder_v1b')
f = ndoc.addObject('Part::Feature', 'PowerSwitchHolder_v1b'); f.Shape = housing
f.Label = 'Power switch holder v1b (installed on the robot-left rail, master coordinates)'
for nm, s in (('Switch_Body', sw_body), ('Switch_Knob_travel', sw_knob), ('Switch_Pins', sw_pins)):
    ndoc.addObject('Part::Feature', nm).Shape = s
ndoc.recompute()
ndoc.saveAs(str(OUT / 'PowerSwitchHolder_v1b.FCStd'))
Part.export([f], str(OUT / 'PowerSwitchHolder_v1b.step'))
mesh = MeshPart.meshFromShape(Shape=pr, LinearDeflection=0.01, AngularDeflection=0.05, Relative=False)
stl = OUT / 'stl' / PRINT_NAME
mesh.write(str(stl))
shutil.copy2(stl, INCOMING / PRINT_NAME)
RESULTS.update({
    'script': 'scripts/build_power_switch_holder_v1b.py',
    'print_file': PRINT_NAME,
    'print_bounds': [round(pb.XLength, 2), round(pb.YLength, 2), round(pb.ZLength, 2)],
    'bed_contact_mm2': round(bottom, 1),
    'volume_mm3': round(housing.Volume, 1),
    'installed_bbox': [round(v, 2) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)],
    'switch_body': [round(v, 2) for v in (sw_body.BoundBox.XMin, sw_body.BoundBox.XMax, sw_body.BoundBox.YMin, sw_body.BoundBox.YMax, sw_body.BoundBox.ZMin, sw_body.BoundBox.ZMax)],
    'knob_top_y': knob_top,
    'clearances': {'rail': round(d_rail, 3), 'tray': round(d_tray, 3), 'base': round(d_base, 3),
                   'upper_deck': round(d_ud, 3), 'max_play_with_tray_in': round(play_x, 3)},
    'assumed': ['pins in one row down the middle of the pin face'],
    'handedness': 'master low-X = robot right; this part is on SideRailRight = robot LEFT',
    'fails': FAILS,
})
(OUT / 'validation.json').write_text(json.dumps(RESULTS, indent=1))
p('exported', stl, pb.XLength, pb.YLength, pb.ZLength)
