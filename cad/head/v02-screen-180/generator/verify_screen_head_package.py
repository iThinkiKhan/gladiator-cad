"""Read-only native/STEP and pose-toggle checks in an isolated FreeCAD GUI."""
import sys, json, hashlib, os
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad/Mod',
 '/usr/lib/freecad/Mod/Part','/usr/lib/freecad/Mod/PartDesign'])
import FreeCAD as A, FreeCADGui as G
G.showMainWindow()
import Part, PartGui, PartDesign, PartDesignGui, Sketcher
out=Path('/home/buralien/projects/gladiator-cad/cad/head/v02-screen-180')
r=json.loads((out/'validation.json').read_text())
d=A.openDocument(str(out/'Gladiator_Head_v02_Screen180.FCStd'))
assert d.Sensors_0deg.ViewObject.Visibility
assert not d.Presentation_180deg.ViewObject.Visibility
d.Sensors_0deg.ViewObject.Visibility=False
d.Presentation_180deg.ViewObject.Visibility=True
assert all(not d.getObject(p['name']).ViewObject.Visibility for p in r['parts'])
assert all(d.getObject('ScreenPose_'+p['name']).ViewObject.Visibility for p in r['parts'])
d.Presentation_180deg.ViewObject.Visibility=False
d.Sensors_0deg.ViewObject.Visibility=True
assert all(d.getObject(p['name']).ViewObject.Visibility for p in r['parts'])
assert all(not d.getObject('ScreenPose_'+p['name']).ViewObject.Visibility for p in r['parts'])
A.closeDocument(d.Name)
step_results={}
expected=sum(p['volume_mm3'] for p in r['parts'])
for file in ['Gladiator_Head_v02_Screen180.step','Gladiator_Head_v02_Screen180_Presented.step']:
    shape=Part.read(str(out/file))
    assert shape.isValid(),file
    assert len(shape.Solids)==len(r['parts']),(file,len(shape.Solids))
    # STEP translation can change numerical integration of curved surfaces.
    # Bound the aggregate difference to 0.001%, while requiring every solid.
    tolerance=max(.05,expected*1e-5)
    assert abs(shape.Volume-expected)<tolerance,(file,shape.Volume,expected)
    step_results[file]={'valid':True,'solids':len(shape.Solids),'volume_mm3':shape.Volume,
        'volume_delta_mm3':shape.Volume-expected,'volume_tolerance_mm3':tolerance}
for p,h in r['source_sha256'].items():
    assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
r['checks']['pose_group_toggle_verified']=True
r['checks']['step_roundtrip']=step_results
(out/'validation.json').write_text(json.dumps(r,indent=2)+'\n')
print('POSE_TOGGLE_AND_STEP_OK',flush=True)
os._exit(0)
