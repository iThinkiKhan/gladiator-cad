from pathlib import Path
import FreeCAD, Part, Sketcher

root = Path('/home/buralien/projects/gladiator-cad')
source = root / 'cad/master/Gladiator_Master.FCStd'
candidate = root / 'cad/master/Gladiator_Master_candidate.FCStd'
doc = FreeCAD.openDocument(str(source))
sheet = doc.getObject('Parameters')

entries = {
    2: ('deck_length', '140 mm', 'Front-to-back deck length'),
    3: ('deck_width', '79 mm', 'Side-to-side deck width'),
    4: ('deck_thickness', '2 mm', 'Metal deck thickness'),
    5: ('center_hole_diameter', '14 mm', 'Tower opening interior diameter'),
    6: ('center_hole_x', '=B3/2', 'Centered across deck'),
    7: ('center_hole_y', '=B2-B11-B5/2', 'From front; rear opening edge is 20 mm from rear'),
    11: ('center_hole_rear_edge_gap', '20 mm', 'Rear edge of hole to rear deck edge'),
    12: ('battery_front_gap', '21 mm', 'Front edge of battery case'),
    13: ('battery_length', '75.5 mm', 'Battery case front-to-back'),
    14: ('battery_width', '79 mm', 'Battery case across deck'),
    15: ('battery_rear_gap', '=B2-B12-B13', 'Calculated 43.5 mm; physical estimate about 45.5 mm'),
    16: ('slit_width', '4 mm', 'Approximate slot width'),
    17: ('slit_rear_gap', '7.5 mm', 'Rear end of slots to rear deck edge'),
    18: ('long_slit_front', '=B12+B13/2', 'Approximate: halfway down battery footprint'),
    19: ('short_slit_length', '33 mm', 'Approximate shorter outer slots'),
    20: ('inner_slit_hole_gap', '5 mm', 'Nearest slot edge to tower opening edge'),
    21: ('outer_slit_center_spacing', '12 mm', 'Outer slots further toward deck edges'),
}
for row, (name, value, note) in entries.items():
    sheet.set(f'A{row}', name)
    sheet.set(f'B{row}', value)
    sheet.setAlias(f'B{row}', name)
    sheet.set(f'C{row}', note)
doc.recompute()

body = doc.addObject('PartDesign::Body', 'ChassisDeck')
body.Label = 'Chassis deck'
base = body.newObject('Sketcher::SketchObject', 'DeckOutline')
base.Label = 'Deck outline (front-left origin)'
corners = [(0,0),(79,0),(79,140),(0,140)]
for i in range(4):
    p, q = corners[i], corners[(i+1)%4]
    base.addGeometry(Part.LineSegment(FreeCAD.Vector(p[0],p[1],0), FreeCAD.Vector(q[0],q[1],0)), False)
for i in range(4):
    base.addConstraint(Sketcher.Constraint('Coincident', i, 2, (i+1)%4, 1))
for i in (0,2):
    base.addConstraint(Sketcher.Constraint('Horizontal', i))
for i in (1,3):
    base.addConstraint(Sketcher.Constraint('Vertical', i))
base.addConstraint(Sketcher.Constraint('Coincident', 0, 1, -1, 1))
wi = base.addConstraint(Sketcher.Constraint('Distance', 0, 79.0))
li = base.addConstraint(Sketcher.Constraint('Distance', 1, 140.0))
base.renameConstraint(wi, 'DeckWidth')
base.renameConstraint(li, 'DeckLength')
base.setExpression('Constraints.DeckWidth', 'Parameters.deck_width')
base.setExpression('Constraints.DeckLength', 'Parameters.deck_length')
doc.recompute()

pad = body.newObject('PartDesign::Pad', 'DeckPad')
pad.Label = 'Deck thickness'
pad.Profile = base
pad.Length = 2.0
pad.setExpression('Length', 'Parameters.deck_thickness')
doc.recompute()

opening = body.newObject('Sketcher::SketchObject', 'TowerOpening')
opening.Label = 'Tower opening (14 mm)'
opening.Placement.Base.z = 2.0
opening.setExpression('Placement.Base.z', 'Parameters.deck_thickness')
opening.addGeometry(Part.Circle(FreeCAD.Vector(39.5,113,0), FreeCAD.Vector(0,0,1), 7), False)
xi = opening.addConstraint(Sketcher.Constraint('DistanceX', 0, 3, 39.5))
yi = opening.addConstraint(Sketcher.Constraint('DistanceY', 0, 3, 113.0))
ri = opening.addConstraint(Sketcher.Constraint('Radius', 0, 7.0))
opening.renameConstraint(xi, 'TowerX')
opening.renameConstraint(yi, 'TowerY')
opening.renameConstraint(ri, 'TowerRadius')
opening.setExpression('Constraints.TowerX', 'Parameters.center_hole_x')
opening.setExpression('Constraints.TowerY', 'Parameters.center_hole_y')
opening.setExpression('Constraints.TowerRadius', 'Parameters.center_hole_diameter/2')
doc.recompute()

tower = body.newObject('PartDesign::Pocket', 'TowerHole')
tower.Label = 'Tower opening through deck'
tower.Profile = opening
tower.Length = 2.0
tower.setExpression('Length', 'Parameters.deck_thickness')
doc.recompute()

slots = body.newObject('Sketcher::SketchObject', 'MountingSlits')
slots.Label = 'Mounting slits (approximate rectangles)'
slots.Placement.Base.z = 2.0
slots.setExpression('Placement.Base.z', 'Parameters.deck_thickness')
slot_rects = [
    (23.5, 58.75, 27.5, 132.5),
    (51.5, 58.75, 55.5, 132.5),
    (11.5, 99.5, 15.5, 132.5),
    (63.5, 99.5, 67.5, 132.5),
]
for x0,y0,x1,y1 in slot_rects:
    pts = [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    for i in range(4):
        p,q=pts[i],pts[(i+1)%4]
        slots.addGeometry(Part.LineSegment(FreeCAD.Vector(p[0],p[1],0),FreeCAD.Vector(q[0],q[1],0)),False)
doc.recompute()
slotcut = body.newObject('PartDesign::Pocket', 'SlitCuts')
slotcut.Label = 'Four mounting slits through deck'
slotcut.Profile = slots
slotcut.Length = 2.0
slotcut.setExpression('Length', 'Parameters.deck_thickness')
doc.recompute()

battery = doc.addObject('Sketcher::SketchObject', 'BatteryFootprint')
battery.Label = '4S battery case footprint (reference)'
battery.Placement.Base.z = 2.0
battery.setExpression('Placement.Base.z', 'Parameters.deck_thickness')
pts = [(0,21),(79,21),(79,96.5),(0,96.5)]
for i in range(4):
    p,q=pts[i],pts[(i+1)%4]
    battery.addGeometry(Part.LineSegment(FreeCAD.Vector(p[0],p[1],0),FreeCAD.Vector(q[0],q[1],0)),False)
doc.recompute()

for obj in (base,pad,opening,tower,slots):
    obj.Visibility = False
slotcut.Visibility = True
battery.Visibility = True
print('fully constrained:', base.FullyConstrained, opening.FullyConstrained)
for obj in (pad,tower,slotcut):
    print(obj.Name, obj.Shape.isNull(), obj.Shape.Volume if not obj.Shape.isNull() else None)
print('sheet battery rear gap', sheet.get('B15'))
doc.saveAs(str(candidate))
FreeCAD.closeDocument(doc.Name)
print('candidate',candidate)
