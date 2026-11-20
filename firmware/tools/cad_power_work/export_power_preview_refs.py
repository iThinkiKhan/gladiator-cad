import sys
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as App
import MeshPart
import Part

master = App.openDocument('/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd')
names = ['ChassisDeck', 'BatteryBox', 'MastBase', 'SideRailLeft',
         'SideRailRight', 'UpperDeck']
shape = Part.makeCompound([master.getObject(name).Shape for name in names])
mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.18,
                              AngularDeflection=0.35, Relative=False)
mesh.write('/tmp/power_preview_refs.stl')
App.closeDocument(master.Name)
