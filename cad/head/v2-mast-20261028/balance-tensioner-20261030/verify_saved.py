import sys,json,hashlib
from pathlib import Path
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A,Part,Mesh
D=Path(__file__).resolve().parent
r=json.loads((D/'validation.json').read_text())
d=A.openDocument(str(D/'Gladiator_Head_v2_Balanced.FCStd'))
b=A.openDocument(str(D.parent/'Gladiator_Head_v2_Mast.FCStd'))
checks={}
checks['baseline_hash_preserved']=hashlib.sha256((D.parent/'Gladiator_Head_v2_Mast.FCStd').read_bytes()).hexdigest()==r['source_sha256']
new=d.getObject('GH44_Tilt_Receiver').Shape
checks['saved_receiver_single_valid_solid']=new.isValid() and len(new.Solids)==1
for n in ('Mast_Tube_v2','Neck_Main','Pan_Servo_Carriage','Pan_Drive_Pulley','Pan_Raised_Pedestal','Tilt_Yoke'):
 a=d.getObject(n).Shape;c=b.getObject(n).Shape
 checks[n+'_preserved']=abs(a.Volume-c.Volume)<1e-6 and abs(a.Area-c.Area)<1e-5 and len(a.Faces)==len(c.Faces) and sorted(tuple(round(v,6) for v in (p.Point.x,p.Point.y,p.Point.z)) for p in a.Vertexes)==sorted(tuple(round(v,6) for v in (p.Point.x,p.Point.y,p.Point.z)) for p in c.Vertexes)
for n in ('GH44_Dual_Carrier','ToF_Sensor_Frame','Rear_Display_Frame','Camera_Tray','Camera_Cover'):
 a=d.getObject(n).Shape;c=b.getObject(n).Shape
 checks[n+'_only_moved_2p5']=abs(a.Volume-c.Volume)<1e-6 and abs((a.BoundBox.YMin-c.BoundBox.YMin)-2.5)<1e-6 and abs(a.BoundBox.ZMin-c.BoundBox.ZMin)<1e-6
bb=b.getObject('Tilt_Horn_Reference').Shape.BoundBox
zone=Part.makeBox(bb.XLength+4,bb.YLength+4,bb.ZLength+4,A.Vector(bb.XMin-2,bb.YMin-2,bb.ZMin-2))
old_seat=b.getObject('GH44_Tilt_Receiver').Shape.common(zone)
new_seat=new.common(zone)
checks['tested_horn_interface_preserved']=old_seat.cut(new_seat).Volume<1e-5 and new_seat.cut(old_seat).Volume<1e-5
s=Part.Shape();s.read(str(D/'GH44_Tilt_Receiver_Balanced.step'))
checks['receiver_STEP_valid_single_solid']=s.isValid() and len(s.Solids)==1
checks['receiver_STEP_volume_matches']=abs(s.Volume-new.Volume)<.001
m=Mesh.Mesh(str(D/'stl/GH44_Tilt_Receiver_Balanced.stl'))
checks['receiver_mesh_closed_manifold']=m.isSolid() and not m.hasNonManifolds()
checks['mesh_volume_close_to_CAD']=abs(m.Volume-new.Volume)/new.Volume<.002
r['independent_saved_checks']=checks
(D/'validation.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(checks,indent=2));assert all(checks.values())
A.closeDocument(d.Name);A.closeDocument(b.Name)
