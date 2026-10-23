from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part,MeshPart,json,hashlib,traceback,os
V=A.Vector
R=Path('/home/buralien/projects/gladiator-cad');N=R/'cad/v2/enclosure/round5-calibrated-28-20261022';O=N/'mount-checked-release'
def clean(s):
 q=Part.Shape();q.importBrepFromString(s.exportBrepToString());return q.Solids[0] if len(q.Solids)==1 else q
try:
 source=N/'print/Gladiator_Round5_Print.FCStd';before=hashlib.sha256(source.read_bytes()).hexdigest();d=A.openDocument(str(source));old=clean(d.Rear_Hood.Shape);new=old.copy();tools=[]
 for y in [-16.25,20.25]:
  cylindrical=[f.Surface.Radius for f in old.Faces if isinstance(f.Surface,Part.Cylinder) and abs(abs(f.Surface.Axis.z)-1)<.001 and abs(f.Surface.Center.x-64)<.01 and abs(f.Surface.Center.y-y)<.01]
  assert any(abs(r-.8)<.001 for r in cylindrical),(y,cylindrical)
  bore=Part.makeCylinder(1.4,4.05,V(64,y,99.85));lead=Part.makeCone(1.55,1.4,.15,V(64,y,99.9),V(0,0,1));tool=bore.fuse(lead);tools.append(tool);new=new.cut(tool)
 rail_checks=[]
 for record in json.loads((N/'mount-access-audit/mount-access-audit.json').read_text())['rail_mounts']:
  side=record['side'];seat=sum(record['screw_head_bearing_x_range_mm'])/2;grip=record['grip_to_rail_mm'];p=V(*record['actual_rail_bore']['center']);axis=V(*record['actual_rail_bore']['axis']);start=p+axis*((seat-p.x)/axis.x);direction=axis if axis.x*(1 if side=='L' else -1)>0 else -axis
  tool=Part.makeCylinder(1.8,grip/abs(axis.x)+.3,start-direction*.1,direction);tools.append(tool);new=new.cut(tool)
  print('RAIL',side,record['hole_yz'],new.isValid(),len(new.Solids),[x.Volume for x in new.Solids],flush=True)
  rail_checks.append((record,start,direction,grip/abs(axis.x)-.21))
 print('BEFORE CLEAN',new.isValid(),flush=True);new=clean(new.removeSplitter());print('AFTER CLEAN',new.isValid(),len(new.Solids),[x.Volume for x in new.Solids],flush=True);new.exportBrep(str(O/'debug-hood.brep'));assert new.isValid() and len(new.Solids)==1
 removed=old.cut(new);allowed=tools[0]
 for tool in tools[1:]:allowed=allowed.fuse(tool);assert removed.cut(allowed).Volume<.001 and new.cut(old).Volume<.001
 assert max(abs(getattr(new.BoundBox,k)-getattr(old.BoundBox,k)) for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax'])<.00001
 report={'source_native_sha256':before,'change':'Two speaker M2 heat-set pockets 2.8mm x4mm, plus six local 3.6mm rail-axis clearance reliefs following the saved rails. Other parts unchanged.','material_removed_mm3':removed.Volume,'unexpected_removal_mm3':removed.cut(allowed).Volume,'speaker_mounts':[]}
 for y in [-16.25,20.25]:
  failed=[]
  for z in [100.15,100.8,101.9,103.5]:
   for i in range(36):
    a=i*3.141592653589793/18
    for r,inside in [(1.35,False),(1.65,True)]:
     actual=new.isInside(V(64+r*__import__('math').cos(a),y+r*__import__('math').sin(a),z),1e-6,True)
     if actual!=inside:failed.append([z,i,r,actual])
  assert not failed,(y,failed[:5])
  report['speaker_mounts'].append({'centre':[64,y,99.9],'CAD_bore_mm':2.8,'usable_depth_mm':4.0,'ear_thickness_mm':2.8,'M2x6_nominal_thread_reach_past_ear_mm':3.2,'M2x6_tip_clearance_to_4mm_pocket_end_mm':.8,'radial_wall_min_without_entry_chamfer_mm':2.1,'bore_checks_pass':True})
 report['rail_clearance_checks']=[]
 for record,start,direction,length in rail_checks:
  overlap=new.common(Part.makeCylinder(1.6,length,start,direction)).Volume
  assert overlap<.001,(record['side'],record['hole_yz'],overlap)
  bearing=[]
  import math
  for i in range(36):
   a=i*math.pi/18
   bearing.append(new.isInside(start+direction*.08+V(0,2.6*math.cos(a),2.6*math.sin(a)),1e-6,True))
  assert all(bearing),(record['side'],record['hole_yz'],'head bearing')
  report['rail_clearance_checks'].append({'side':record['side'],'hole_yz':record['hole_yz'],'aligned_bore_mm':3.6,'shaft_D3_2_overlap_mm3':overlap,'head_bearing_radius_2_6_all_samples_solid':True,'M3x20_reach_past_rail_face_mm':20-record['grip_to_rail_mm']})
 d.Rear_Hood.Shape=new
 # Keep the displayed colour regions consistent with the changed manufacturing solid.
 for tag,z0,z1 in [('Lower',-20,50),('Belt',50,56),('Wall',56,99.9),('Cap',99.9,130)]:
  obj=d.getObject('Appearance_Rear_Hood_'+tag)
  if obj:obj.Shape=new.common(Part.makeBox(400,450,z1-z0,V(-200,-200,z0)))
 meta=d.addObject('App::FeaturePython','Speaker_Heatsets_20261022');meta.addProperty('App::PropertyString','ManufacturingNotes');meta.ManufacturingNotes='Two calibrated M2 heat-set pockets:2.8mm x4.0mm, install flush from inside before fitting speaker. For measured2.8mm ears use M2x6 machine screws. Original 1.6mm pilot tails remain below the usable pocket; roof and7mm pads unchanged.'
 d.recompute();d.saveAs(str(O/'Gladiator_Round5_Print.FCStd'))
 names=json.loads((N/'style/validation.json').read_text())['parts'];export=A.newDocument('MountCheckedManufacturing');objects=[]
 for name in names:
  s=clean(d.getObject(name).Shape)
  if name.startswith('Tablet_'):s=clean(s.fuse(clean(d.getObject('Letters_'+name[-1]).Shape)).removeSplitter())
  assert s.isValid() and len(s.Solids)==1,name
  obj=export.addObject('Part::Feature',name);obj.Shape=s;objects.append(obj)
 Part.export(objects,str(O/'Gladiator_Round5_PrintParts.step'))
 recheck=A.newDocument('MountCheckedSTEPReopen');Part.insert(str(O/'Gladiator_Round5_PrintParts.step'),recheck.Name);solids=[s for obj in recheck.Objects if hasattr(obj,'Shape') for s in obj.Shape.Solids];assert len(solids)==22 and all(s.isValid() for s in solids)
 report['saved_STEP_valid_solids']=22
 # Export the actual new hood in its original roof-down print orientation.
 pr=new.copy();pr.rotate(V(),V(1,0,0),180);bb=pr.BoundBox;pr.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin));mesh=MeshPart.meshFromShape(Shape=pr,LinearDeflection=.015,AngularDeflection=.07,Relative=False)
 assert mesh.isSolid() and not mesh.hasNonManifolds();mesh.write(str(O/'Rear_Hood.stl'))
 report['STL_solid_manifold']=True;report['STL_bounds']=[mesh.BoundBox.XMin,mesh.BoundBox.YMin,mesh.BoundBox.ZMin,mesh.BoundBox.XMax,mesh.BoundBox.YMax,mesh.BoundBox.ZMax]
 assert hashlib.sha256(source.read_bytes()).hexdigest()==before
 report['source_preserved']=True;report['passed']=True
 (O/'speaker-correction-verification.json').write_text(json.dumps(report,indent=2))
except BaseException:(O/'CAD_ERROR.txt').write_text(traceback.format_exc())
os._exit(0)
