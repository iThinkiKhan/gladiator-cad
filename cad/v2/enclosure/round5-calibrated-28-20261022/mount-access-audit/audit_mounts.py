from pathlib import Path
import FreeCAD as A,Part,json,math,traceback,os,hashlib
V=A.Vector
R=Path('/home/buralien/projects/gladiator-cad');N=R/'cad/v2/enclosure/round5-calibrated-28-20261022';O=N/'mount-access-audit'
def plain(s):
 q=Part.Shape();q.importBrepFromString(s.exportBrepToString());return q

def overlap(a,b):
 if not a.BoundBox.intersect(b.BoundBox):return 0.
 return a.common(b).Volume

def hitlist(probe,objects):
 out=[]
 for name,s in objects.items():
  v=overlap(probe,s)
  if v>.001:out.append([name,v])
 return out
try:
 path=N/'print/Gladiator_Round5_Print.FCStd';sourcehash=hashlib.sha256(path.read_bytes()).hexdigest();d=A.openDocument(str(path));hood=plain(d.Rear_Hood.Shape)
 shapes={o.Name:plain(o.Shape) for o in d.Objects if hasattr(o,'Shape') and not o.Shape.isNull() and not o.Name.startswith('Appearance_')}
 report={'source_native_sha256':sourcehash,'context_objects':[{'name':k,'bounds':[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]} for k,s in shapes.items() if any(w in k.lower() for w in ['speaker','rail','spk'])]}
 obstacles={k:s for k,s in shapes.items() if k.startswith(('Ref_','Head_')) or k in ['Rear_Hood','Front_Left','Front_Right','Aquila_Relief','Tablet_L','Tablet_R']}
 # SMA mounting access. Diameters here are tool-envelope tests, not invented hardware measurements.
 sma={}
 for label,r,y0,length in [('external_nut_D12',6,-36,3.95),('external_socket_D16',8,-57,24.95),('external_socket_D20',10,-57,24.95),('inside_flange_D12',6,-29.95,3.8),('inside_tool_D16_short',8,-29.95,11.9),('inside_tool_D20_short',10,-29.95,11.9)]:
  probe=Part.makeCylinder(r,length,V(68,y0,84.5),V(0,1,0));sma[label]={'hood_overlap_mm3':overlap(probe,hood),'assembled_reference_hits':hitlist(probe,obstacles)}
 thickness=[]
 for radius in [4.0,7.0,10.0]:
  for i in range(16):
   a=i*math.pi/8;x=68+radius*math.cos(a);z=84.5+radius*math.sin(a);ys=[-33+j*.025 for j in range(201) if hood.isInside(V(x,-33+j*.025,z),1e-6,False)]
   thickness.append((max(ys)-min(ys)+.025) if ys else 0)
 sma['sampled_land_thickness_mm_range']=[min(thickness),max(thickness)];sma['hole_surface_diameters_mm']=[]
 for f in hood.Faces:
  s=f.Surface
  if isinstance(s,Part.Cylinder) and abs(abs(s.Axis.y)-1)<.001 and abs(s.Center.x-68)<.01 and abs(s.Center.z-84.5)<.01:sma['hole_surface_diameters_mm'].append(2*s.Radius)
 report['antenna']=sma
 # Speaker bore geometry and loose-hood driver access.
 speaker={'hole_centres':[],'driver_access':[]}
 for y in [-16.25,20.25]:
  matches=[]
  for f in hood.Faces:
   s=f.Surface
   if isinstance(s,Part.Cylinder) and abs(abs(s.Axis.z)-1)<.001 and abs(s.Center.x-64)<.01 and abs(s.Center.y-y)<.01:matches.append({'diameter_mm':2*s.Radius,'bounds_z':[f.BoundBox.ZMin,f.BoundBox.ZMax]})
  speaker['hole_centres'].append({'x':64,'y':y,'cylindrical_faces':matches})
  for diameter in [5,7]:
   tool=Part.makeCylinder(diameter/2,24.9,V(64,y,70.5),V(0,0,1));speaker['driver_access'].append({'centre':[64,y],'tool_diameter_mm':diameter,'hood_hits':overlap(tool,hood),'other_context_hits':hitlist(tool,{k:s for k,s in obstacles.items() if k!='Rear_Hood'})})
 report['speaker']=speaker
 # Inspect the actual saved rail holes, independent of the JSON hardpoint list.
 rail_report=[]
 for side,name in [('L','Ref_ArchRail_Left_v4'),('R','Ref_ArchRail_Right_v4')]:
  rail=shapes[name];cylinders=[]
  for f in rail.Faces:
   s=f.Surface
   if isinstance(s,Part.Cylinder) and abs(s.Axis.x)>.99 and abs(s.Radius-2.3)<.01:
    cylinders.append({'center':[s.Center.x,s.Center.y,s.Center.z],'axis':[s.Axis.x,s.Axis.y,s.Axis.z],'radius':s.Radius,'bounds':[f.BoundBox.XMin,f.BoundBox.YMin,f.BoundBox.ZMin,f.BoundBox.XMax,f.BoundBox.YMax,f.BoundBox.ZMax]})
  for y,z in [(22,40),(35.5,46),(59,45)]:
   def dist(c):
    p=V(*c['center']);a=V(*c['axis']);q=V(0,y,z);return ((q-p).cross(a)).Length
   cylinder=min(cylinders,key=dist)
   # Ray samples around a nominal M3 head determine the real exterior bearing face.
   seats=[]
   for i in range(12):
    a=i*math.pi/6;yy=y+2.6*math.cos(a);zz=z+2.6*math.sin(a)
    line=Part.makeLine(V(-50 if side=='L' else 130,yy,zz),V(20 if side=='L' else 60,yy,zz));common=hood.common(line)
    if common.Vertexes:seats.append(min(p.Point.x for p in common.Vertexes) if side=='L' else max(p.Point.x for p in common.Vertexes))
   assert len(seats)==12,(side,y,z,'Incomplete screw head support',seats)
   seat=sum(seats)/len(seats);face=(7.5-math.atan(1/89)*(y-23.85)) if side=='L' else (71.5+math.atan(1/89)*(y-23.85))
   center=V(*cylinder['center']);axis=V(*cylinder['axis']);atface=center+axis*((face-center.x)/axis.x)
   yz_error=math.hypot(atface.y-y,atface.z-z);grip=abs(face-seat)
   entry=V(face,y,z);direction=V(1 if side=='L' else -1,0,0)
   probes={}
   for length in [20,25]:
    origin=V(seat,y,z);shaft=Part.makeCylinder(1.5,length,origin,direction)
    probes[str(length)]={'grip_to_rail_mm':grip,'nominal_entry_beyond_rail_face_mm':length-grip,'shaft_overlap_rail_material_mm3':overlap(shaft,rail),'shaft_overlap_hood_mm3':overlap(shaft,hood)}
   start=V(seat-40 if side=='L' else seat+.05,y,z);driver=Part.makeCylinder(3,39.95,start,V(1,0,0))
   hits=hitlist(driver,obstacles)
   rail_report.append({'side':side,'hole_yz':[y,z],'actual_rail_bore':cylinder,'hole_axis_yz_error_at_entry_mm':yz_error,'angular_difference_deg':math.degrees(math.acos(min(1,abs(axis.x)))),'screw_head_bearing_x_range_mm':[min(seats),max(seats)],'grip_to_rail_mm':grip,'screw_length_tests':probes,'external_D6_driver_hits':hits})
 report['rail_mounts']=rail_report
 assert hashlib.sha256(path.read_bytes()).hexdigest()==sourcehash
 (O/'mount-access-audit.json').write_text(json.dumps(report,indent=2))
except BaseException:(O/'AUDIT_ERROR.txt').write_text(traceback.format_exc())
os._exit(0)
