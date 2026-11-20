"""Read-only FreeCAD assembly audit; run with workstation FreeCAD Python libs."""
import sys
import json
sys.path.append('/usr/lib/freecad/lib')
sys.path.append('/usr/lib/freecad/Mod')
import FreeCAD as App
import Part
import PartDesign
import Sketcher

doc = App.openDocument('/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd')
print('AUDIT_START')
sheet = doc.getObject('Parameters')
for cell in sheet.getNonEmptyCells():
    alias = sheet.getAlias(cell)
    if alias:
        print('PARAM', alias, sheet.get(cell))
for obj in doc.Objects:
    if obj.TypeId == 'PartDesign::Body' or (hasattr(obj, 'Shape') and not obj.getParentGeoFeatureGroup()):
        if not hasattr(obj, 'Shape') or obj.Shape.isNull() or not obj.Shape.Solids:
            continue
        b = obj.Shape.BoundBox
        print('SHAPE', json.dumps({'name':obj.Name, 'label':obj.Label,'type':obj.TypeId,
            'bounds':[b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax],
            'volume':obj.Shape.Volume,'valid':obj.Shape.isValid()}))
for a,b in [('MastTube','MastBase'),('MastTube','UpperDeck'),('MastBase','ChassisDeck'),
            ('MastTube','PowerShield'),('MastTube','S3Board'),('MastTube','DriverMountLeft'),
            ('MastTube','DriverMountRight')]:
    one,two = doc.getObject(a),doc.getObject(b)
    assert one is not None and two is not None, (a,b)
    print('CLASH_MM3',a,b,one.Shape.common(two.Shape).Volume)
for label,point in [('base_closed_below_bore',(39.5,113,4)),('mast_bore',(39.5,113,60)),
                    ('rear_wire_window',(39.5,122,30)),('mast_rear_above_window',(39.5,122,37))]:
    bodies=[doc.getObject('MastTube'),doc.getObject('MastBase')]
    print('SOLID_AT',label,any(o.Shape.isInside(App.Vector(*point),1e-6,True) for o in bodies))
for o in doc.Objects:
    if 'MastWindow' in o.Name or 'MastTubePin' in o.Name or o.Name == 'MastPinCut':
        print('WINDOW_FEATURE',o.Name,o.TypeId,[(p,str(getattr(o,p))) for p in ['Length','Reversed','Direction','Placement','Profile'] if p in o.PropertiesList])
for z in [25,30,35]:
    print('WIRE_PATH',z,[(y,doc.MastTube.Shape.isInside(App.Vector(39.5,y,z),1e-6,False)) for y in [103.5,106,108,113,118,119.5,120.5,121.5,122.5]])
for name in ['MastTube','MastBase']:
    obj=doc.getObject(name)
    print('PIN_PATH',name,[(x,obj.Shape.isInside(App.Vector(x,113,13),1e-6,False)) for x in [27,30,32,39.5,47,49,52]])
for o in doc.Objects:
    if o.Name.startswith('Mast') and o.TypeId in ['PartDesign::Pad','PartDesign::Pocket']:
        print('FEATURE_VOLUME',o.Name,o.Shape.Volume)
# Test a correction in this isolated document only; never save the source CAD.
window = doc.getObject('MastWindowCut')
window.Reversed = True
window.Length = 12
doc.recompute()
print('TRIAL_WINDOW_CORRECTION',doc.MastTube.Shape.isValid(),len(doc.MastTube.Shape.Solids),doc.MastTube.Shape.Volume)
for z in [25,30,35]:
    print('TRIAL_WIRE_PATH',z,[(y,doc.MastTube.Shape.isInside(App.Vector(39.5,y,z),1e-6,False)) for y in [103.5,106,108,113,118,119.5,120.5,121.5,122.5]])
print('AUDIT_END')
App.closeDocument(doc.Name)
