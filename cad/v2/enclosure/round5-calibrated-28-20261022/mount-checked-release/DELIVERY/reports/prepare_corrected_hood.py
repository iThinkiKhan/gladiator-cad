from pathlib import Path
import json,hashlib,shutil,struct,zipfile,xml.etree.ElementTree as E,subprocess,time,traceback,math
import numpy as np
R=Path('/home/buralien/projects/gladiator-cad');N=R/'cad/v2/enclosure/round5-calibrated-28-20261022';P=N/'print';O=N/'mount-checked-release';C='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
def js(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def phase(s):js(O/'status.json',{'phase':s});print(s,flush=True)
try:
 phase('Waiting for corrected speaker CAD')
 for i in range(180):
  if (O/'CAD_ERROR.txt').exists():raise RuntimeError((O/'CAD_ERROR.txt').read_text())
  if (O/'speaker-correction-verification.json').exists():break
  time.sleep(3)
 assert json.loads((O/'speaker-correction-verification.json').read_text())['passed']
 phase('Replacing only hood mesh in the proven hood project')
 (O/'plates').mkdir(exist_ok=True);source=N/'SD_PACKAGE/plates/GLAD_04_HOOD_SD_M2_28.3mf'
 with zipfile.ZipFile(source) as z:files={f:z.read(f) for f in z.namelist() if f!='Metadata/slice_info.config'}
 originalcfg=files['Metadata/project_settings.config'];meshfile='3D/Objects/Rear_Hood.model';model=E.fromstring(files[meshfile]);normal=model.find(C+'resources').find(C+'object');oldmesh=normal.find(C+'mesh');oldpts=np.array([[float(v.get(k)) for k in ['x','y','z']] for v in oldmesh.find(C+'vertices')]);lo=oldpts.min(0);hi=oldpts.max(0)
 raw=(O/'Rear_Hood.stl').read_bytes();count=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+count*50
 vertices=[];triangles=[];lookup={}
 for i in range(count):
  face=[]
  for j in range(3):
   xyz=tuple(struct.unpack_from('<fff',raw,84+i*50+12+j*12))
   if xyz not in lookup:lookup[xyz]=len(vertices);vertices.append(xyz)
   face.append(lookup[xyz])
  triangles.append(face)
 pts=np.array(vertices);assert np.max(np.abs((pts.max(0)-pts.min(0))-(hi-lo)))<.001
 pts+=lo-pts.min(0);newmesh=E.Element(C+'mesh');vv=E.SubElement(newmesh,C+'vertices');tt=E.SubElement(newmesh,C+'triangles')
 for x,y,z in pts:E.SubElement(vv,C+'vertex',{'x':format(x,'.9g'),'y':format(y,'.9g'),'z':format(z,'.9g')})
 for a,b,c in triangles:E.SubElement(tt,C+'triangle',{'v1':str(a),'v2':str(b),'v3':str(c)})
 normal.remove(oldmesh);normal.append(newmesh);files[meshfile]=E.tostring(model,encoding='utf-8',xml_declaration=True)
 target=O/'plates/GLAD_04_HOOD_SD_M2_28.3mf'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
  for name,data in files.items():z.writestr(name,data)
 assert files['Metadata/project_settings.config']==originalcfg
 B=json.loads((P/'build-summary.json').read_text());B['plates']={'07':B['plates']['07']};B['plates']['07']['file']=target.name;B['plates']['07']['parts'][0]['source']=str((O/'Rear_Hood.stl').relative_to(R));B['source_hashes']={};B['speaker_M2_heatsets']='2.8mm x4.0mm, M2x6 screws through2.8mm ears';js(O/'build-summary.json',B)
 shutil.copy2(P/'native-mount-envelopes.json',O/'native-mount-envelopes.json')
 # Add local support exclusions for the two new upright heat-set pockets.
 text=(P/'add_support_blockers.py').read_text().replace(str(P),str(O)).replace("for key in ['01','07','08']:","for key in ['07']:")
 marker="bores['FIT_Scutum_Seat']=";a=text.index(marker);text=text[:a]+"bores['Rear_Hood'] += [('Speaker_rear',(64,-16.25,101.9),2,4),('Speaker_front',(64,20.25,101.9),2,4)]\nfor y,z in [(22,40),(35.5,46),(59,45)]:\n slope=__import__('math').atan(1/89);left=7.5-slope*(y-23.85)-.2;right=71.5+slope*(y-23.85)+.2\n bores['Rear_Hood'] += [(f'Rail_L_{y}',((-9+left)/2,y,z),0,left+9),(f'Rail_R_{y}',((88+right)/2,y,z),0,88-right)]\nbores['Rear_Hood'] += [(f'Roof_{x}',(x,72,101),2,11) for x in [22,33,50,66]]+[('SMA',(68,-31,84.5),1,2)]\n"+text[a:]
 text=text.replace("size=np.array([4.5]*3);size[axis]=depth+5.0","width=8.4 if label=='SMA' else 5.2 if label.startswith('Roof_') else 4.9 if label.startswith('Rail_') else 4.5;size=np.array([width]*3);size[axis]=depth+5.0")
 (O/'add_support_blockers.py').write_text(text);p=subprocess.run(['python3',str(O/'add_support_blockers.py')],capture_output=True,text=True,cwd=R);assert p.returncode==0,(p.stdout,p.stderr)
 phase('Slicing corrected hood with unchanged Neo SAFE and process settings')
 text=(P/'slice_and_check.py').read_text().replace(str(P),str(O));(O/'slice_and_check.py').write_text(text);p=subprocess.run(['python3',str(O/'slice_and_check.py'),'07'],capture_output=True,text=True,cwd=R,timeout=1800);(O/'slicer-run.log').write_text(p.stdout+'\n'+p.stderr);assert p.returncode==0,p.stderr
 check=json.loads((O/'slice-check/07/check.json').read_text());assert check['original_start_guard_passed'] and check['extrusions_fit_220_with_0_5mm_margin'] and check['exit_code']==0
 warnings=[l for l in (O/'slice-check/07/slicer.log').read_text().splitlines() if __import__('re').search(r'error|warning|potentially lost|floating',l,__import__('re').I)];assert not warnings,warnings
 phase('Checking all mounting paths for support intrusion')
 # Transform support segment endpoints back into the native hood's coordinate system.
 seg=json.loads((O/'slice-check/07/segments.json').read_text());a=np.array([s[:5] for s in seg if s[5].startswith('Support')]);bounds=json.loads((O/'native-mount-envelopes.json').read_text())['Rear_Hood']['bounds'];mid=np.array([(bounds[0]+bounds[3])/2,(bounds[1]+bounds[4])/2]);at=np.array(B['plates']['07']['parts'][0]['at_mm'])
 p0=np.column_stack([a[:,0]-at[0]+mid[0],mid[1]-(a[:,1]-at[1]),bounds[5]-a[:,4]]);p1=np.column_stack([a[:,2]-at[0]+mid[0],mid[1]-(a[:,3]-at[1]),bounds[5]-a[:,4]])
 holes=[(f'Tablet_{side}_{y}',(x,y,70),0,1.4,4) for side,x in [('L',-11.8),('R',90.8)] for y in [-6,48]]+[('Aquila',(26,-34.8,68.5),1,1.4,4),('Speaker_rear',(64,-16.25,101.9),2,1.4,4),('Speaker_front',(64,20.25,101.9),2,1.4,4)]
 slope=math.atan(1/89)
 for y,z in [(22,40),(35.5,46),(59,45)]:
  left=7.5-slope*(y-23.85)-.2;right=71.5+slope*(y-23.85)+.2
  holes += [(f'Rail_L_{y}',((-9+left)/2,y,z),0,1.8,left+9),(f'Rail_R_{y}',((88+right)/2,y,z),0,1.8,88-right)]
 for x in [22,33,50,66]:
  holes += [(f'Roof_insert_{x}',(x,72,(95.6+103.1)/2),2,2.3,103.1-95.6),(f'Roof_clearance_{x}',(x,72,(103.1+106.7)/2),2,1.8,106.7-103.1)]
 holes += [('SMA',(68,-31,84.5),1,3.5,2)]
 report={}
 for label,centre,axis,radius,depth in holes:
  delta=p0-np.array(centre);direction=p1-p0;axial=delta[:,axis];ad=direction[:,axis];half=depth/2+.2;lower=np.zeros(len(a));upper=np.ones(len(a));moving=np.abs(ad)>1e-10;ta=np.zeros(len(a));tb=np.zeros(len(a));ta[moving]=(-half-axial[moving])/ad[moving];tb[moving]=(half-axial[moving])/ad[moving];lower[moving]=np.maximum(0,np.minimum(ta[moving],tb[moving]));upper[moving]=np.minimum(1,np.maximum(ta[moving],tb[moving]));ok=(lower<=upper)&(moving|(np.abs(axial)<=half));radial=np.delete(delta,axis,axis=1);rd=np.delete(direction,axis,axis=1);den=np.sum(rd*rd,axis=1);t=np.zeros(len(a));mask=den>1e-15;t[mask]=-np.sum(radial[mask]*rd[mask],axis=1)/den[mask];t=np.maximum(lower,np.minimum(upper,t));hits=ok&(np.sum((radial+t[:,None]*rd)**2,axis=1)<(radius+.2)**2)
  report[label]={'support_segment_hits_with_0_2mm_bead_allowance':int(hits.sum()),'centre':centre,'axis':axis,'radius':radius,'depth':depth}
 js(O/'mounting-path-support-check.json',report)
 assert all(report[k]['support_segment_hits_with_0_2mm_bead_allowance']==0 for k in report)
 js(O/'project-preservation.json',{'machine_material_process_settings_byte_identical_before_blockers':True,'geometry_change':'two speaker heat-set pockets and six rail-axis clearance reliefs','new_support_exclusions':['Speaker_rear','Speaker_front'],'mount_support_paths_clear':True,'source_native_preserved':True})
 phase('CAD and slice PASS; mount support results ready for review')
except BaseException:(O/'PIPELINE_ERROR.txt').write_text(traceback.format_exc());phase('FAILED - see PIPELINE_ERROR.txt')
