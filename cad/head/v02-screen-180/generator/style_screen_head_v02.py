"""Style and verify the second candidate in a private Xvfb display."""
import sys, os, json, hashlib, zipfile, xml.etree.ElementTree as E
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad/Mod',
                 '/usr/lib/freecad/Mod/Part','/usr/lib/freecad/Mod/PartDesign'])
import FreeCAD as A, FreeCADGui as G
G.showMainWindow()
import Part, PartDesign, Sketcher, PartGui, PartDesignGui
out=Path('/home/buralien/projects/gladiator-cad/cad/head/v02-screen-180')
report=json.loads((out/'validation.json').read_text())
assert report['checks']['sampled_geometry_pass'], 'Resolve sampled collisions before styling'
path=out/'Gladiator_Head_v02_Screen180.FCStd'
d=A.openDocument(str(path))
active={p['name'] for p in report['parts']}
travel=d.addObject('App::DocumentObjectGroup','Sensors_0deg')
travel.Label='POSE 1 - sensors forward (0 deg)'
for name in list(active)+['Pan_Belt_Path_Reference']:
    obj=d.getObject(name)
    for parent in list(obj.InList):
        if parent.TypeId=='App::DocumentObjectGroup': parent.removeObject(obj)
    travel.addObject(obj)
d.Presentation_180deg.Label='POSE 2 - screen forward (180 deg)'
beltpose=d.addObject('Part::Feature','ScreenPose_Pan_Belt_Path_Reference')
beltpose.Shape=d.Pan_Belt_Path_Reference.Shape.copy()
beltpose.addProperty('App::PropertyString','SourcePart').SourcePart='Pan_Belt_Path_Reference'
d.Presentation_180deg.addObject(beltpose)
for o in d.Objects:
    if o.ViewObject: o.ViewObject.Visibility=False
d.Sensors_0deg.ViewObject.Visibility=True
for name in ['ChassisDeck','SideRailLeft','SideRailRight','BatteryBox','MastTube','UpperDeck',
             'S3Board','Breadboard','PowerShield','AntennaPost','DriverMountLeft','DriverMountRight']:
    o=d.getObject(name)
    if o and o.ViewObject:
        o.ViewObject.Visibility=True
        o.ViewObject.ShapeColor=(.58,.60,.63)
        if hasattr(o,'Tip') and o.Tip and o.Tip.ViewObject: o.Tip.ViewObject.Visibility=True
for o in d.Objects:
    base=o.SourcePart if hasattr(o,'SourcePart') else o.Name
    if base not in active and o.Name!='Pan_Belt_Path_Reference': continue
    source=d.getObject(base)
    motion=source.MotionGroup
    color=(.22,.34,.40) if motion=='fixed' else (.18,.56,.60)
    if base in ['Rear_Display_Frame','GH44_Dual_Carrier']: color=(.91,.57,.22)
    if 'Reference' in base or 'Envelope' in base: color=(.25,.35,.72)
    if any(n in base for n in ['Bearing','Spacer','Circlip','Bushing','Horn']): color=(.65,.67,.70)
    if base=='ST7789_Board_62x29x3_2': color=(.10,.17,.22)
    if base=='Pan_Belt_Path_Reference': color=(.18,.20,.23)
    o.ViewObject.ShapeColor=color
    o.ViewObject.LineColor=(.12,.16,.19)
    o.ViewObject.Transparency=0
    o.ViewObject.DisplayMode='Flat Lines'
    o.ViewObject.Visibility=o.Name in active or o.Name=='Pan_Belt_Path_Reference'
d.Presentation_180deg.ViewObject.Visibility=False
G.activeDocument().activeView().viewAxonometric()
G.activeDocument().activeView().fitAll()
d.recompute(); d.save()
for p in report['parts']:
    o=d.getObject(p['name'])
    assert o.Shape.isValid() and len(o.Shape.Solids)==1,p['name']
    assert abs(o.Shape.Volume-p['volume_mm3'])<.01,p['name']
A.closeDocument(d.Name)
# Re-open saved file to validate serialization, including both stored poses.
d=A.openDocument(str(path))
for p in report['parts']:
    assert abs(d.getObject(p['name']).Shape.Volume-p['volume_mm3'])<.01,p['name']
    assert abs(d.getObject('ScreenPose_'+p['name']).Shape.Volume-p['volume_mm3'])<.01,p['name']
A.closeDocument(d.Name)
for p,h in report['source_sha256'].items():
    assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
with zipfile.ZipFile(path) as z:
    x=E.fromstring(z.read('GuiDocument.xml'))
    states={o.get('name'):o.find('./Properties/Property[@name="Visibility"]/Bool').get('value')
            for o in x.findall('./ViewProviderData/ViewProvider')
            if o.find('./Properties/Property[@name="Visibility"]/Bool') is not None}
    for name in active: assert states[name]=='true',(name,states.get(name))
    assert states['Presentation_180deg']=='false'
    for name in ['GH44_Blank_Carrier','GH44_Camera_Carrier','GH44_Fixed_Head_Adapter']:
        assert states[name]=='false'
report['checks']['saved_native_file_reopened_and_verified']=True
report['checks']['both_pose_volumes_preserved']=True
report['checks']['saved_visibility_verified']=True
# Check belt pitch envelope against all non-pulley parts at the sampled poses.
# Pulley engagement/contact is deliberately excluded because teeth are not modeled.
center=A.Vector(39.5,113,0)
tiltcenter=A.Vector(39.5,87,205)
d=A.openDocument(str(path))
belt=d.Pan_Belt_Path_Reference.Shape
belt_hits=[]
for angle in range(0,181,10):
    for tilt in [-25,0,25]:
        for p in report['parts']:
            if 'Pulley' in p['name']: continue
            s=d.getObject(p['name']).Shape.copy()
            if p['motion']=='tilt': s.rotate(tiltcenter,A.Vector(1,0,0),tilt)
            if p['motion'] in ['tilt','pan']: s.rotate(center,A.Vector(0,0,1),angle)
            if p['motion']=='servo': s.rotate(A.Vector(39.5,155,0),A.Vector(0,0,1),angle)
            if belt.BoundBox.intersect(s.BoundBox):
                v=belt.common(s).Volume
                if v>.05: belt_hits.append({'part':p['name'],'pan':angle,'tilt':tilt,'mm3':v})
report['checks']['belt_nonpulley_intersections']=belt_hits
assert not belt_hits,belt_hits
# Add the belt guide to the preview data using the exact saved geometry.
mesh=json.loads((out/'head-preview-mesh.json').read_text())
b=belt.copy(); b.translate(-center)
vs,fs=b.tessellate(.35)
mesh.append({'name':'Pan_Belt_Path_Reference','color':[.18,.20,.23],'motion':'belt',
    'vertices':[[v.x,v.y,v.z] for v in vs],'faces':fs})
(out/'head-preview-mesh.json').write_text(json.dumps(mesh,separators=(',',':')))
A.closeDocument(d.Name)
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PACKAGE_OK: saved native file, both poses, visibility and unchanged original/master verified.',flush=True)
os._exit(0)
