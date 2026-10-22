from pathlib import Path
import FreeCAD as A, Part, MeshPart, json, os,traceback
R=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure');O=R/'round5-print-20261022'
def actual_bounds(shape):
 m=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.015,AngularDeflection=.07,Relative=False)
 pts,_=m.Topology
 return [min(getattr(p,a) for p in pts) for a in ['x','y','z']]+[max(getattr(p,a) for p in pts) for a in ['x','y','z']]
try:
 d=A.openDocument(str(R/'round5-20261021/Gladiator_Round5.FCStd'));data={}
 for n in ['Rear_Hood','Front_Left','Front_Right','Crest_Clamp','Neck_Clamp_0','Neck_Clamp_1']:
  s=d.getObject(n).Shape;b=s.BoundBox;data[n]={'bounds':actual_bounds(s),'volume_mm3':s.Volume}
 for name,owner,low,size in [('FIT_Scutum_Seat','Front_Left',(0,144,56),(32,10,46)),('FIT_Tablet_End','Rear_Hood',(85,-12,59),(11,34,22)),('FIT_Aquila_Seat','Rear_Hood',(2,-39,57),(48,11,23))]:
  s=d.getObject(owner).Shape.common(Part.makeBox(*size,A.Vector(*low)));b=s.BoundBox
  data[name]={'bounds':actual_bounds(s)}
 (O/'native-mount-envelopes.json').write_text(json.dumps(data,indent=2))
except BaseException:(O/'ENVELOPE_ERROR.txt').write_text(traceback.format_exc())
os._exit(0)

