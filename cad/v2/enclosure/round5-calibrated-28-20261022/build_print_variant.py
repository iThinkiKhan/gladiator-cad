from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part,MeshPart,Mesh,json,hashlib,traceback,os,math
V=A.Vector;ROOT=Path('/home/buralien/projects/gladiator-cad');S=ROOT/'cad/v2/enclosure/round5-calibrated-28-20261022/style';R=S.parent/'print'
(R/'print-stl').mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copied(s):
 q=Part.Shape();q.importBrepFromString(s.exportBrepToString());return q.Solids[0] if len(q.Solids)==1 else q
def overlap(a,b):return a.common(b).Volume if a.BoundBox.intersect(b.BoundBox) else 0.
try:
 before=sha(S/'Gladiator_Round5.FCStd');d=A.openDocument(str(S/'Gladiator_Round5.FCStd'));old=copied(d.Crest_Clamp.Shape)
 foot=Part.makeBox(12,3.95,2.51,V(33.5,155.8,234.3))
 # Clear the proven yoke sweep at the lower front corner; retain the insert's complete surround.
 foot=foot.cut(Part.makeBox(3.8,1.4,1.1,V(38.9,155.4,234.2)))
 bore=Part.makeCylinder(1.4,4.1,V(39.5,155.7,237.8),V(0,1,0))
 new=old.fuse(foot.cut(bore)).removeSplitter();new=copied(new);assert new.isValid() and len(new.Solids)==1
 report={'change':'Add full-width lower web to new Crest_Clamp only; keep existing clamp/contact surfaces and all original robot geometry. Insert is fully surrounded; bottom wall1.7mm except a small yoke-clearance relief with0.7mm nominal lip. The complete0.5mm material ring is checked over3mm insert engagement. M2 bore 2.8 accepted from Jim coupon result.', 'old_volume_mm3':old.Volume,'new_volume_mm3':new.Volume,'old_material_removed_mm3':old.cut(new).Volume,'static_hits':[],'pan_tilt_hits':[]}
 assert report['old_material_removed_mm3']<.001
 added=new.cut(old);report['added_material_mm3']=added.Volume;report['static_check_scope']='Only newly added material versus all old/new objects; old shape retained and prior verification reused.'
 for o in d.Objects:
  if not hasattr(o,'Shape') or o.Shape.isNull() or o.Name=='Crest_Clamp' or o.Name.startswith('Appearance_'):continue
  v=overlap(added,copied(o.Shape))
  if v>.001:report['static_hits'].append([o.Name,v])
 # Check supplemental camera assembly as well.
 cam=ROOT/'cad/head/camera-service-v2-20261021/Gladiator_Camera_Service_v2_REVIEW.FCStd'
 if cam.exists():
  cd=A.openDocument(str(cam))
  for n in ['Mount_Tray','Screw_Cover']:
   o=cd.getObject(n)
   if o:
    v=overlap(added,copied(o.Shape))
    if v>.001:report['static_hits'].append(['Camera_'+n,v])
 assert not report['static_hits'],report['static_hits']
 base=A.openDocument(str(S/'baseline-v28/Gladiator_Enclosure_v2.FCStd'));shapes={o.Name:copied(o.Shape) for o in base.Objects if hasattr(o,'Shape') and not o.Shape.isNull()}
 motion=json.loads((ROOT/'cad/head/master/build-check.json').read_text());panrefs={n:s for n,s in shapes.items() if n.startswith('Head_') and motion.get(n[5:],{}).get('motion')=='pan'}
 fixed={n:s for n,s in shapes.items() if not n.startswith('Head_') or motion.get(n[5:],{}).get('motion') in ('fixed','belt','servo')}
 minz=1e9
 for a in range(-25,26,1):
  q=new.copy();q.rotate(V(39.5,139,216.5),V(1,0,0),a);minz=min(minz,q.BoundBox.ZMin)
  for n,s in panrefs.items():
   v=overlap(q,s)
   if v>.001:
    hit=q.common(s);pv=hit.Vertexes;report['pan_tilt_hits'].append([a,n,v,[min(getattr(p.Point,k) for p in pv) for k in ['x','y','z']]+[max(getattr(p.Point,k) for p in pv) for k in ['x','y','z']]])
 report.update(min_clamp_z_over_51_tilt_poses_mm=minz,fixed_reference_max_z_mm=max(s.BoundBox.ZMax for s in fixed.values()),pan_range_unchanged=[-20,180],tilt_samples=51)
 assert not report['pan_tilt_hits'] and minz>report['fixed_reference_max_z_mm'],{'hits':report['pan_tilt_hits'],'minz':minz,'fixed_max':report['fixed_reference_max_z_mm']}
 # Sample a complete 0.5mm material ring around the insert over its assumed3mm engagement.
 ring_fail=[]
 for y in [156.0,156.5,157,157.5,158,158.5]:
  for i in range(72):
   t=i*math.pi/36;p=V(39.5+2.3*math.cos(t),y,237.8+2.3*math.sin(t))
   if not new.isInside(p,1e-6,True):ring_fail.append([p.x,p.y,p.z])
 report['full_insert_surround_ring_samples']=432;report['ring_failures']=ring_fail;assert not ring_fail
 d.Crest_Clamp.Shape=new;d.Crest_Clamp.ManufacturingNotes='Print variant: lower web encloses side insert fully, with1.7mm lower wall and a local0.7mm lip at the yoke relief. Existing contact faces unchanged. M2 bore2.8 calibrated/depth4 retained.'
 # Carry forward Jim's stronger shield emblems and their raised boss seating.
 ed=A.openDocument(str(ROOT/'cad/v2/enclosure/round5-print-20261022/emblem-v2/Scutum_Emblem_v2.FCStd'))
 for side in ['L','R']:
  d.getObject('Scutum_Emblem_'+side).Shape=copied(ed.getObject('Scutum_Emblem_v2_'+side).Shape)
  for name in ['Scutum_Boss_'+side,'Scutum_'+side+'_M2']:
   ss=copied(d.getObject(name).Shape);ss.translate(V(0,.8,0));d.getObject(name).Shape=ss
 report['stronger_insets_v2_integrated']=True
 report['shield_boss_seating_offset_mm']=.8
 d.recompute();A.setActiveDocument(d.Name);G.setActiveDocument(d.Name);d.saveAs(str(R/'Gladiator_Round5_Print.FCStd'))
 m=MeshPart.meshFromShape(Shape=new,LinearDeflection=.015,AngularDeflection=.07,Relative=False);bb=m.BoundBox;m.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
 assert m.isSolid() and not m.hasNonManifolds();m.write(str(R/'print-stl/Crest_Clamp.stl'))
 # New native manufacturing export: the other21 geometries are untouched; letters are fused for the tablet export.
 export=A.newDocument('Round5PrintExport');objects=[]
 names=json.loads((S/'validation.json').read_text())['parts']
 for n in names:
  s=copied(d.getObject(n).Shape)
  if n.startswith('Tablet_'):s=s.fuse(copied(d.getObject('Letters_'+n[-1]).Shape)).removeSplitter()
  assert s.isValid() and len(s.Solids)==1,n
  o=export.addObject('Part::Feature',n);o.Shape=s;objects.append(o)
 Part.export(objects,str(R/'Gladiator_Round5_PrintParts.step'))
 stepcheck=A.newDocument('StepCheck');Part.insert(str(R/'Gladiator_Round5_PrintParts.step'),stepcheck.Name)
 solids=[s for o in stepcheck.Objects if hasattr(o,'Shape') for s in o.Shape.Solids]
 report['step_solid_count']=len(solids);assert len(solids)==22 and all(s.isValid() for s in solids)
 nearest=min(solids,key=lambda s:(s.CenterOfMass-new.CenterOfMass).Length)
 report['new_clamp_step_volume_error_mm3']=abs(nearest.Volume-new.Volume);assert report['new_clamp_step_volume_error_mm3']<.001
 # Update the geometric placement reference used for independent support-path checks.
 N=json.loads((R/'native-mount-envelopes.json').read_text());pts,_=m.Topology
 # m was translated for STL; query the untransformed native mesh for true extrema.
 mm=MeshPart.meshFromShape(Shape=new,LinearDeflection=.015,AngularDeflection=.07,Relative=False);pp,_=mm.Topology
 N['Crest_Clamp']={'bounds':[min(getattr(p,a) for p in pp) for a in ['x','y','z']]+[max(getattr(p,a) for p in pp) for a in ['x','y','z']],'volume_mm3':new.Volume,'source':'Gladiator_Round5_Print.FCStd'}
 (R/'native-mount-envelopes.json').write_text(json.dumps(N,indent=2))
 # A close view for review; do not save visibility changes.
 A.setActiveDocument(d.Name);G.setActiveDocument(d.Name)
 for o in d.Objects:
  if hasattr(o,'Shape'):o.ViewObject.Visibility=o.Name in ['Crest_Clamp','Crest_Clamp_Shoe']
 view=G.activeDocument().activeView();dv=V(-.5,1,-.45);dv.normalize();right=dv.cross(V(0,0,1));right.normalize();up=right.cross(dv);view.setCameraOrientation(A.Rotation(right,up,-dv,'ZXY'));view.fitAll();G.updateGui();view.saveImage(str(R/'previews/crest-clamp-reinforced.png'),1200,1000,'White')
 assert sha(S/'Gladiator_Round5.FCStd')==before
 report.update(original_round5_native_sha256=before,original_round5_native_unchanged=True,new_native_sha256=sha(R/'Gladiator_Round5_Print.FCStd'),new_clamp_stl_sha256=sha(R/'print-stl/Crest_Clamp.stl'),passed=True)
 (R/'crest-clamp-reinforcement.json').write_text(json.dumps(report,indent=2))
 err=R/'CLAMP_REINFORCEMENT_ERROR.txt'
 if err.exists():err.unlink()
except BaseException:(R/'CLAMP_REINFORCEMENT_ERROR.txt').write_text(traceback.format_exc())
os._exit(0)





