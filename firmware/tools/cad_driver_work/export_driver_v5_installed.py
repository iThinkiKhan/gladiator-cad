import sys
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as App
import MeshPart

doc = App.openDocument('/home/buralien/projects/gladiator-cad/cad/drivers/v5-interlock/DriverMount_v5.FCStd')
for name in ['Base_Left', 'Wedge_Left']:
    mesh = MeshPart.meshFromShape(Shape=doc.getObject(name).Shape,
                                  LinearDeflection=0.04,
                                  AngularDeflection=0.12,
                                  Relative=False)
    mesh.write('/tmp/' + name + '_installed.stl')
App.closeDocument(doc.Name)
