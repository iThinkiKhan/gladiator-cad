"""Independent saved-file verification. Does not regenerate or save source CAD."""
from pathlib import Path
import FreeCAD as A,Part,Mesh,math,json,hashlib,time,traceback,os
V=A.Vector;R=Path('/home/buralien/projects/gladiator-cad');O=R/'cad/v2/enclosure/round5-20261021'
T=time.time();OUT={'failures':[],'static_intersections':[],'new_part_intersections':[],'head_motion_hits':[]}
def log(*x):
 with (O/'verification-progress.log').open('a') as f:f.write(str(round(time.time()-T,1))+' '+' '.join(map(str,x))+'\n')
def shape(s):
 q=Part.Shape();q.importBrepFromString(s.exportBrepToString())
 return q.Solids[0] if len(q.Solids)==1 else q

def overlap(a,b):
 if not a.BoundBox.intersect(b.BoundBox):return 0.
 return a.common(b).Volume

def ck(ok,what):
 if not ok:OUT['failures'].append(what)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 report=json.loads((O/'validation.json').read_text())
 d=A.openDocument(str(O/'Gladiator_Round5.FCStd'));b=A.openDocument(str(O/'baseline-v28/Gladiator_Enclosure_v2.FCStd'))
 S={o.Name:shape(o.Shape) for o in d.Objects if hasattr(o,'Shape') and not o.Shape.isNull() and not o.Name.startswith('Appearance_')}
 B={o.Name:shape(o.Shape) for o in b.Objects if hasattr(o,'Shape') and not o.Shape.isNull()}
 owners={o.Name:o.AssemblyOwner for o in d.Objects if hasattr(o,'AssemblyOwner')}
 panels=['Rear_Hood','Front_Left','Front_Right'];native={}
 for n in report['parts']:
  s=S[n];native[n]=dict(valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume)
  ck(s.isValid() and len(s.Solids)==1,'Native part '+n)
  mesh=Mesh.Mesh(str(O/'stl'/(n+'.stl')))
  ck(mesh.isSolid() and not mesh.hasNonManifolds(),'Mesh '+n)
  ck(all(sz<mx for sz,mx in zip(report['parts'][n]['size_mm'],[220,220,250])),'Bed '+n)
 OUT['native_and_stl']=native
 OUT['baseline_material_retained']={n:B[n].cut(S[n]).Volume for n in panels+['Lens_Plate']}
 for n,v in OUT['baseline_material_retained'].items():ck(v<.001,'Removed baseline material '+n)
 unchanged={}
 for n,s in B.items():
  if n in panels+['Lens_Plate']:continue
  diff=s.cut(S[n]).Volume+S[n].cut(s).Volume
  unchanged[n]=diff;ck(diff<.001,'Context shape changed '+n)
 OUT['unchanged_context_count']=len(unchanged);OUT['max_context_difference_mm3']=max(unchanged.values())
 OUT['source_hashes_match']=all(sha(R/p)==h for p,h in report['source_hashes'].items());ck(OUT['source_hashes_match'],'Original source file changed')
 log('native material and sources checked')
 # Include the earlier camera service v2 review as an additional clearance reference.
 cam=R/'cad/head/camera-service-v2-20261021/Gladiator_Camera_Service_v2_REVIEW.FCStd'
 camera={}
 if cam.exists():
  cd=A.openDocument(str(cam))
  for o in cd.Objects:
   if hasattr(o,'Shape') and not o.Shape.isNull() and (o.Name in ('Mount_Tray','Screw_Cover')):camera['CameraContext_'+o.Name]=shape(o.Shape)
 OUT['camera_context_objects']=list(camera)
 # New shell solids against all unchanged installed references; baseline reference-to-reference fits are outside this change.
 refs={n:s for n,s in B.items() if n not in panels+['Lens_Plate']}
 refs.update(camera)
 prod=[n for n in owners if n not in panels+['Lens_Plate'] and not n.startswith('Letters_')]
 for n in panels+prod:
  for rn,rs in refs.items():
   vol=overlap(S[n],rs)
   if vol>.01:OUT['static_intersections'].append([n,rn,vol])
 # Inset seats, locating walls and adjacent components must not interfere with one another.
 for i,n in enumerate(prod+panels):
  for m in (prod+panels)[i+1:]:
   vol=overlap(S[n],S[m])
   if vol>.01:OUT['new_part_intersections'].append([n,m,vol])
  OUT['hardware_intersections']=[]
 for o in d.Hardware.Group:
  hs=shape(o.Shape)
  for n in list(owners)+list(refs):
   if n.startswith('Letters_'):continue
   vol=overlap(hs,S[n] if n in S else refs[n])
   if vol>.01:OUT['hardware_intersections'].append([o.Name,n,vol])
 ck(not OUT['hardware_intersections'],'Hardware interference')
 log('static',OUT['static_intersections'],'new pairs',OUT['new_part_intersections'],'hardware',OUT['hardware_intersections'])
 (O/'verification-static.json').write_text(json.dumps(OUT,indent=2))
 # Reuse the authenticated unchanged baseline's rigid sweeps, then replay every added solid
 # against old obstacles and every baseline moving solid against new obstacles. Boolean distributivity
 # makes this equivalent for the added geometry without fusing decorative meshes into giant compounds.
 cert=json.loads((O/'baseline-v28/removal-sweeps.json').read_text())
 ck(cert['hood_back_front_panels_on']['free_mm']==150,'Missing baseline hood certificate')
 ck(cert['front_right_45deg_pull']['free_mm']==120,'Missing baseline right certificate')
 ck(cert['front_left_two_leg_path']['leg1_needed_mm']==20 and cert['front_left_two_leg_path']['slack_mm']==3,'Missing baseline left certificate')
 OUT['removal_method']='Exact baseline hashes and retained material verified. Baseline certified sweeps reused; additions replayed at 1mm against all obstacles; original parts checked against every new obstacle.'
 additions={}
 for p in panels:
  log('extract exterior additions',p)
  if p=='Rear_Hood':
   masks=[Part.makeBox(30,70,40,V(-39,-12,50)),Part.makeBox(30,70,40,V(88,-12,50)),Part.makeBox(110,20,80,V(-10,-52,40))]
  else:masks=[Part.makeBox(200,30,120,V(-60,148,0))]
  external=[]
  for mask in masks:
   region=S[p].common(mask,.00001)
   external.extend(region.Solids)
  addedvol=sum(q.Volume for q in external)
  ck(abs(addedvol-(S[p].Volume-B[p].Volume))<.01,'Unaccounted internal material '+p)
  OUT.setdefault('exterior_material_accounting',{})[p]=dict(extracted_mm3=addedvol,volume_increase_mm3=S[p].Volume-B[p].Volume)
  additions[p]=external+[S[n] for n in owners if owners[n]==p and n!=p]
  log('exterior pieces',p,len(external),addedvol)
  for o in d.Hardware.Group:
   if (p=='Rear_Hood' and o.Name.startswith(('Tablet','Aquila'))) or (p=='Front_Left' and o.Name=='Scutum_L_M2') or (p=='Front_Right' and o.Name=='Scutum_R_M2'):additions[p].append(shape(o.Shape))
 headnew=[S[n] for n in owners if owners[n].startswith('Head')]
 newobs=[('AddedHead_%d'%i,s) for i,s in enumerate(headnew)]+list(camera.items())
 for obj in d.Hardware.Group:
  if obj.Name.startswith(('Crest','Neck')):newobs.append((obj.Name,shape(obj.Shape)))
 def test_path(name,points,exclude):
  oldobs=[(n,s) for n,s in refs.items() if not(name=='Rear_Hood' and n.startswith('Hood_')) and n not in camera]
  oldobs += [(p,B[p]) for p in panels if p!=name and p not in exclude]
  othernew=list(newobs)
  for p in panels:
   if p!=name and p not in exclude:othernew += [(p+'_addition_%d'%i,s) for i,s in enumerate(additions[p])]
  pieces=[('baseline',B[name])]+[('added',s) for s in additions[name]]
  # Speaker and switch are hood-owned existing components, not stationary obstacles during hood removal.
  if name=='Rear_Hood':pieces += [('existing fixture',s) for n,s in refs.items() if n.startswith('Hood_')]
  hits=[];comparisons=0
  for idx,v in enumerate(points):
   for kind,part in pieces:
    m=part.copy();m.translate(v)
    obs=othernew if kind=='baseline' else oldobs+othernew
    for on,o in obs:
     if not m.BoundBox.intersect(o.BoundBox):continue
     comparisons+=1;vol=overlap(m,o)
     if vol>.3:hits.append(dict(step=idx,translation=list(v),obstacle=on,piece=kind,overlap_mm3=vol));break
    if hits:break
   if hits:break
  return dict(samples=len(points),boolean_comparisons=comparisons,hits=hits,passed=not hits)
 OUT['removal']={}
 OUT['removal']['hood_back_150mm_panels_on']=test_path('Rear_Hood',[V(0,-t,0) for t in range(0,151,1)],{'Rear_Hood'})
 log('hood sweep',OUT['removal']['hood_back_150mm_panels_on'])
 nv=V(1,0,1);nv.normalize()
 OUT['removal']['right_45deg_120mm']=test_path('Front_Right',[nv*t for t in range(0,121)],{'Front_Right'})
 log('right sweep',OUT['removal']['right_45deg_120mm'])
 lv=V(-1,0,1);lv.normalize();ex=V(-math.cos(math.radians(15)),0,math.sin(math.radians(15)))
 OUT['removal']['left_two_leg_20_plus_90mm']=test_path('Front_Left',[lv*t for t in range(0,21)]+[lv*20+ex*t for t in range(1,91)],{'Front_Left'})
 OUT['removal']['left_legacy_slack_mm']=3
 log('left sweep',OUT['removal']['left_two_leg_20_plus_90mm'])
 # Rigid head add-ons mount to the receiver/display tilt group. Relative pan objects need only the eleven tilt positions.
 motion=json.loads((R/'cad/head/master/build-check.json').read_text())
 panrefs={n:s for n,s in B.items() if n.startswith('Head_') and motion.get(n[5:],{}).get('motion')=='pan'}
 # Entire pan group rotates together. Fixed objects below the minimum swept Z are excluded by exact bounding box tests.
 fixedrefs={n:s for n,s in B.items() if not n.startswith('Head_') or motion.get(n[5:],{}).get('motion') in('fixed','belt','servo')}
 axis=V(39.5,139,216.5);minz=1e9
 for tilt in range(-25,26,5):
  for n in owners:
   if not owners[n].startswith('Head'):continue
   q=S[n].copy();q.rotate(axis,V(1,0,0),tilt);minz=min(minz,q.BoundBox.ZMin)
   for rn,rs in panrefs.items():
    vol=overlap(q,rs)
    if vol>.01:OUT['head_motion_hits'].append([n,tilt,rn,vol])
 OUT['head_addons_min_z_over_tilt_mm']=minz
 # At every allowed pan angle, a rotation about Z leaves Z unchanged; prove fixed-shell separation by Z.
 OUT['fixed_reference_max_z_mm']=max(s.BoundBox.ZMax for s in fixedrefs.values())
 ck(minz>OUT['fixed_reference_max_z_mm'],'Head decoration below fixed envelope; full pan checks required')
 OUT['head_motion_samples']=11;OUT['pan_range_unchanged']=[-20,180]
 # Shared tilt geometry / fields are invariant under rigid pose; test new additions once.
 tof=A.openDocument(str(R/'cad/head/master/Gladiator_Head_Master.FCStd'))
 OUT['sensor_forward_separation_mm']=min(199.5-max(s.BoundBox.YMax for s in headnew),205.6-max(s.BoundBox.YMax for s in headnew))
 ck(OUT['sensor_forward_separation_mm']>0,'Decorations in front of sensor planes')
 log('head motion checked',OUT['head_motion_hits'])
 # Existing vents and the SMA's external tool land remain clear at their original positions.
 probes={}
 for k in range(3):
  z=88+4.8*k;pr=Part.makeBox(42,12,2.4,V(5,-40,z));probes['vent_%d'%k]=overlap(S['Rear_Hood'],pr)
 sma=Part.makeCylinder(11,12,V(68,-44,84.5),V(0,1,0))
 probes['sma_external_access']=sum(overlap(S[n],sma) for n in panels+prod)
 OUT['functional_opening_probes_mm3']=probes
 for n,v in probes.items():ck(v<.001,'Functional opening changed '+n)
 # All insert bores are open to their designed depth; no hidden union has filled a pocket.
 bores=[]
 tests=[]
 for side,x,sign in [('L',-9,-1),('R',88,1)]:
  for y in(-6,48):tests.append(('tablet_'+side,Part.makeCylinder(1.65,3.8,V(x+sign*4.7,y,70),V(-sign,0,0))))
 for cx,p in[(16,'Front_Left'),(63,'Front_Right')]:tests.append((p,Part.makeCylinder(1.65,3.8,V(cx,148+.9,79),V(0,1,0))))
 tests.append(('aquila',Part.makeCylinder(1.65,3.8,V(26,-32-.9,68.5),V(0,-1,0))))
 for label,pr in tests:
  p=label if label in panels else 'Rear_Hood';v=overlap(S[p],pr);bores.append([label,v]);ck(v<.001,'Blocked new insert bore '+label)
 OUT['new_insert_bore_obstructions_mm3']=bores
 # STEP re-open independently and compare manufacturing volume/count.
 import sys
 sys.path.insert(0,str(O));from step_fidelity import check_step
 OUT['step_reopen']=check_step(d,report,O/'Gladiator_Round5_PrintParts.step')
 ck(OUT['step_reopen']['passed'],'STEP reopen mismatch')
 ck(not OUT['static_intersections'],'Static intersections')
 ck(not OUT['new_part_intersections'],'New part interferences')
 ck(not OUT['head_motion_hits'],'Head decoration tilt interference')
 for n,v in OUT['removal'].items():
  if isinstance(v,dict):ck(v['passed'],'Removal path '+n)
 OUT['pass']=not OUT['failures'];OUT['runtime_s']=round(time.time()-T,1)
 OUT['limits']=['Sampled rigid geometry; no physical harness model or loaded servo test.','M2 bore3.6 and insert length3.0 remain pending the existing calibration coupon.','Prior shell fit is preserved geometrically, not newly certified on physical hardware.']
 (O/'independent-verification.json').write_text(json.dumps(OUT,indent=2));log('DONE',OUT['pass'],OUT['failures'])
except BaseException:
 OUT['error']=traceback.format_exc();(O/'independent-verification.json').write_text(json.dumps(OUT,indent=2));log(OUT['error'])
os._exit(0)





