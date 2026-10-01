"""Unpowered SG90 cross-horn / 60T GT2 drive-pulley fit coupon.

The radial slots deliberately do not claim measured horn-hole coordinates.
Run on the CAD server with its FreeCAD Python modules.
"""
import json
import math
import sys
from pathlib import Path

sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as App
import MeshPart
import Part

ROOT = Path('/home/buralien/projects/gladiator-cad')
OUT = ROOT / 'cad/head/drive-coupons-20260922'
OUT.mkdir(parents=True, exist_ok=True)

TEETH = 60
PITCH = 2.0
PITCH_LINE_DIFFERENTIAL = 0.254
GROOVE_RADIUS = 0.65  # Jim's two-notch belt mesh coupon passed
GROOVE_DEPTH = 0.75
BELT_CHANNEL_HEIGHT = 6.0
FLANGE_HEIGHT = 0.7
FLANGE_OVERHANG = 1.2
SLOT_INNER_CENTER = 7.0
SLOT_OUTER_CENTER = 14.0
SLOT_WIDTH = 2.6  # PLA printer's tested M2 clearance target
CENTER_ACCESS_DIAMETER = 5.5  # pass the original horn-retaining screw/tool


def cylinder(radius, z, height, x=0.0, y=0.0):
    return Part.makeCylinder(radius, height, App.Vector(x, y, z))


def ring(outer, inner, z, height):
    return cylinder(outer, z, height).cut(
        cylinder(inner, z - 0.1, height + 0.2))


def radial_slot(angle_deg, z, height):
    radius = SLOT_WIDTH / 2.0
    shape = cylinder(radius, z, height, SLOT_INNER_CENTER)
    shape = shape.fuse(cylinder(radius, z, height, SLOT_OUTER_CENTER))
    shape = shape.fuse(Part.makeBox(SLOT_OUTER_CENTER - SLOT_INNER_CENTER,
                                   SLOT_WIDTH, height,
                                   App.Vector(SLOT_INNER_CENTER, -radius, z)))
    shape.rotate(App.Vector(), App.Vector(0, 0, 1), angle_deg)
    return shape


pitch_diameter = TEETH * PITCH / math.pi
outside_diameter = pitch_diameter - 2 * PITCH_LINE_DIFFERENTIAL
outside_radius = outside_diameter / 2
groove_center_radius = outside_radius - GROOVE_DEPTH + GROOVE_RADIUS
height = BELT_CHANNEL_HEIGHT + 2 * FLANGE_HEIGHT

pulley = cylinder(outside_radius, 0, height)
for tooth in range(TEETH):
    angle = 2 * math.pi * tooth / TEETH
    pulley = pulley.cut(cylinder(
        GROOVE_RADIUS, -0.1, height + 0.2,
        groove_center_radius * math.cos(angle),
        groove_center_radius * math.sin(angle)))

flange_radius = outside_radius + FLANGE_OVERHANG
pulley = pulley.fuse(ring(flange_radius, outside_radius - 1.0,
                          0, FLANGE_HEIGHT))
pulley = pulley.fuse(ring(flange_radius, outside_radius - 1.0,
                          height - FLANGE_HEIGHT, FLANGE_HEIGHT))
pulley = pulley.cut(cylinder(CENTER_ACCESS_DIAMETER / 2,
                              -0.1, height + 0.2))
for angle in (0, 90, 180, 270):
    pulley = pulley.cut(radial_slot(angle, -0.1, height + 0.2))
pulley = pulley.removeSplitter()

assert pulley.isValid() and len(pulley.Solids) == 1
assert pulley.BoundBox.ZMin == 0
assert abs(pulley.BoundBox.ZLength - height) < 1e-6

doc = App.newDocument('Drive60HornFitCoupon')
obj = doc.addObject('Part::Feature', 'Drive60HornFitCoupon')
obj.Label = '60T printed drive pulley - cross-horn slot fit coupon'
obj.Shape = pulley
obj.addProperty('App::PropertyString', 'DesignStatus')
obj.DesignStatus = 'Unpowered horn / belt fit coupon only; no final attachment'
doc.recompute()
doc.saveAs(str(OUT / 'Drive60_HornSlot_Fit_Coupon.FCStd'))
Part.export([obj], str(OUT / 'Drive60_HornSlot_Fit_Coupon.step'))

mesh = MeshPart.meshFromShape(Shape=pulley, LinearDeflection=0.01,
                             AngularDeflection=0.0872665, Relative=False)
mesh.write(str(OUT / 'Drive60_HornSlot_Fit_Coupon_print-flat.stl'))

report = {
    'status': 'UNPOWERED FIT COUPON - NOT A FULL HEAD OR DRIVE RELEASE',
    'belt_profile': 'Jim physically selected 2-notch / groove radius 0.65 mm',
    'teeth': TEETH,
    'pitch_mm': PITCH,
    'pitch_diameter_mm': pitch_diameter,
    'outside_diameter_mm': outside_diameter,
    'flange_diameter_mm': 2 * flange_radius,
    'groove_depth_mm': GROOVE_DEPTH,
    'belt_channel_height_mm': BELT_CHANNEL_HEIGHT,
    'total_height_mm': height,
    'horn_tip_radius_mm_measured': 17,
    'slot_radial_centers_mm': [SLOT_INNER_CENTER, SLOT_OUTER_CENTER],
    'slot_width_mm': SLOT_WIDTH,
    'center_access_diameter_mm': CENTER_ACCESS_DIAMETER,
    'minimum_tooth_root_to_slot_outer_edge_mm':
        outside_radius - GROOVE_DEPTH - (SLOT_OUTER_CENTER + SLOT_WIDTH / 2),
    'single_valid_solid': pulley.isValid() and len(pulley.Solids) == 1,
    'mesh_is_solid': mesh.isSolid(),
    'volume_cm3': pulley.Volume / 1000,
    'notes': [
        'Print flat with the pulley axis vertical, no supports; use a brim if bed adhesion needs it.',
        'Use the supplied horn and its original center screw; do not print a spline.',
        'Offer up the cross horn unpowered and choose two opposite existing arm holes within the slots.',
        'Check M2 screw fit, underside nut clearance, horn seating, and unobstructed center-screw access.',
        'Do not run this pulley on the servo until the attachment and full drive are redesigned and checked.',
    ],
}
(OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
App.closeDocument(doc.Name)
print(json.dumps(report, indent=2))
