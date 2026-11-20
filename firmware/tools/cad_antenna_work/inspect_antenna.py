"""Read-only clearance inspection of the saved antenna mount."""
import sys

sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as App
import Part

path = '/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd'
doc = App.openDocument(path)
obj = doc.getObject('AntennaPost')
shape = obj.Shape
print('object', obj.Name, obj.Label, 'tip', obj.Tip.Name)
print('valid', shape.isValid(), 'solids', len(shape.Solids), 'volume', shape.Volume)
print('bounds', shape.BoundBox)
for x in (60.0, 76.0):
    for radius in (1.7, 2.8, 3.2):
        for z0, z1 in ((58.0, 62.0), (62.0, 66.0), (66.0, 80.0)):
            probe = Part.makeCylinder(radius, z1-z0, App.Vector(x, 10, z0))
            print('axis', x, 'radius', radius, 'z', z0, z1,
                  'solid_overlap_mm3', round(shape.common(probe).Volume, 3))
App.closeDocument(doc.Name)
