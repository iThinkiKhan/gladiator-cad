from pathlib import Path
import FreeCAD as A, Part, MeshPart, json, traceback, os
V=A.Vector
R=Path('/home/buralien/projects/gladiator-cad');S=R/'cad/v2/enclosure/round5-calibrated-28-20261022/style';O=R/'cad/v2/enclosure/round5-calibrated-28-20261022/print'
O.mkdir(exist_ok=True);(O/'fit-test-stl').mkdir(exist_ok=True)
try:
 d=A.openDocument(str(S/'Gladiator_Round5.FCStd'));result={}
 # Exact clipped samples of the new seats plus original wall, not newly modelled proxies.
 for name,owner,low,size in [
 ('FIT_Scutum_Seat','Front_Left',(0,144,56),(32,10,46)),
 ('FIT_Tablet_End','Rear_Hood',(85,-12,59),(11,34,22)),
 ('FIT_Aquila_Seat','Rear_Hood',(2,-39,57),(48,11,23))]:
  s=d.getObject(owner).Shape.common(Part.makeBox(*size,V(*low))).removeSplitter()
  assert s.isValid() and len(s.Solids)==1,(name,len(s.Solids))
  s.rotate(V(),V(1,0,0),180);b=s.BoundBox;s.translate(V(-b.XMin,-b.YMin,-b.ZMin))
  mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.015,AngularDeflection=.07,Relative=False)
  assert mesh.isSolid() and not mesh.hasNonManifolds(),name
  mesh.write(str(O/'fit-test-stl'/(name+'.stl')))
  result[name]={'source':owner,'clip_min':low,'clip_size':size,'size_mm':[s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength],'volume_mm3':s.Volume}
 (O/'fit-test-sources.json').write_text(json.dumps(result,indent=2))
except BaseException:(O/'PREP_ERROR.txt').write_text(traceback.format_exc())
os._exit(0)
