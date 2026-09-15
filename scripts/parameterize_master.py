from pathlib import Path
import FreeCAD, Sketcher

root=Path('/home/buralien/projects/gladiator-cad/cad/master')
doc=FreeCAD.openDocument(str(root/'Gladiator_Master_candidate.FCStd'))
slots=doc.getObject('MountingSlits')
exprs=[
    (
        'Parameters.center_hole_x - Parameters.center_hole_diameter/2 - Parameters.inner_slit_hole_gap - Parameters.slit_width',
        'Parameters.long_slit_front',
        'Parameters.slit_width',
        'Parameters.deck_length - Parameters.slit_rear_gap - Parameters.long_slit_front'
    ),
    (
        'Parameters.center_hole_x + Parameters.center_hole_diameter/2 + Parameters.inner_slit_hole_gap',
        'Parameters.long_slit_front',
        'Parameters.slit_width',
        'Parameters.deck_length - Parameters.slit_rear_gap - Parameters.long_slit_front'
    ),
    (
        'Parameters.center_hole_x - Parameters.center_hole_diameter/2 - Parameters.inner_slit_hole_gap - Parameters.slit_width - Parameters.outer_slit_center_spacing',
        'Parameters.deck_length - Parameters.slit_rear_gap - Parameters.short_slit_length',
        'Parameters.slit_width',
        'Parameters.short_slit_length'
    ),
    (
        'Parameters.center_hole_x + Parameters.center_hole_diameter/2 + Parameters.inner_slit_hole_gap + Parameters.outer_slit_center_spacing',
        'Parameters.deck_length - Parameters.slit_rear_gap - Parameters.short_slit_length',
        'Parameters.slit_width',
        'Parameters.short_slit_length'
    ),
]
for n,(xexpr,yexpr,wexpr,lexpr) in enumerate(exprs,1):
    j=(n-1)*4
    for k in range(4):
        slots.addConstraint(Sketcher.Constraint('Coincident',j+k,2,j+(k+1)%4,1))
    for k in (0,2):
        slots.addConstraint(Sketcher.Constraint('Horizontal',j+k))
    for k in (1,3):
        slots.addConstraint(Sketcher.Constraint('Vertical',j+k))
    values=[
        ('DistanceX',j,1, slots.Geometry[j].StartPoint.x, 'X',xexpr),
        ('DistanceY',j,1, slots.Geometry[j].StartPoint.y, 'Y',yexpr),
        ('Distance',j, None, 4.0, 'Width',wexpr),
        ('Distance',j+1, None, slots.Geometry[j+1].EndPoint.y - slots.Geometry[j+1].StartPoint.y, 'Length',lexpr),
    ]
    for typ,g,p,v,name,expr in values:
        if p is None:
            idx=slots.addConstraint(Sketcher.Constraint(typ,g,v))
        else:
            idx=slots.addConstraint(Sketcher.Constraint(typ,g,p,v))
        cname=f'Slot{n}{name}'
        slots.renameConstraint(idx,cname)
        slots.setExpression(f'Constraints.{cname}',expr)
doc.recompute()
print('slots constrained',slots.FullyConstrained)

battery=doc.getObject('BatteryFootprint')
for k in range(4):
    battery.addConstraint(Sketcher.Constraint('Coincident',k,2,(k+1)%4,1))
for k in (0,2):
    battery.addConstraint(Sketcher.Constraint('Horizontal',k))
for k in (1,3):
    battery.addConstraint(Sketcher.Constraint('Vertical',k))
battery.addConstraint(Sketcher.Constraint('PointOnObject',0,1,-2))
for typ,g,v,name,expr in [
    ('DistanceY',0,21.0,'BatteryFront','Parameters.battery_front_gap'),
    ('Distance',0,79.0,'BatteryWidth','Parameters.battery_width'),
    ('Distance',1,75.5,'BatteryLength','Parameters.battery_length'),
]:
    if typ=='DistanceY':
        idx=battery.addConstraint(Sketcher.Constraint(typ,g,1,v))
    else:
        idx=battery.addConstraint(Sketcher.Constraint(typ,g,v))
    battery.renameConstraint(idx,name)
    battery.setExpression(f'Constraints.{name}',expr)
doc.recompute()
print('battery constrained',battery.FullyConstrained)
shape=doc.getObject('SlitCuts').Shape
print('valid',shape.isValid(),'volume',shape.Volume)
out=root/'Gladiator_Master_parametric.FCStd'
doc.saveAs(str(out))
FreeCAD.closeDocument(doc.Name)
print(out)
