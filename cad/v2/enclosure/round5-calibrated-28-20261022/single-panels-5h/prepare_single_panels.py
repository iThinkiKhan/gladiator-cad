from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,zipfile,xml.etree.ElementTree as ET,traceback
import numpy as np
ROOT=Path('/home/buralien/projects/gladiator-cad');N=ROOT/'cad/v2/enclosure/round5-calibrated-28-20261022';P=N/'print';O=N/'single-panels-5h';SOURCE=N/'SD_PACKAGE/plates/GLAD_05_PANELS_SD_M2_28.3mf'
C='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}';ET.register_namespace('',C[1:-1]);ET.register_namespace('p','http://schemas.microsoft.com/3dmanufacturing/production/2015/06')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def phase(s):js(O/'status.json',{'phase':s});print(s,flush=True)
try:
 phase('Splitting front-panel plate without changing parts, placement or settings')
 package_hashes=json.loads((N/'SD_PACKAGE/SHA256SUMS.json').read_text());assert sha(SOURCE)==package_hashes['plates/'+SOURCE.name]
 B=json.loads((P/'build-summary.json').read_text());original=B['plates']['08'];summary={'plates':{},'source_plate_sha256':sha(SOURCE),'source_model_geometry_unchanged':True,'machine_process_filament_settings_unchanged':True,'insert_bore_mm':2.8};proof={}
 (O/'plates').mkdir(exist_ok=True);(O/'READY_TO_PRINT').mkdir(exist_ok=True);(O/'reports').mkdir(exist_ok=True)
 for suffix,name in [('L','Front_Left'),('R','Front_Right')]:
  key='08'+suffix;filename='GLAD_05'+suffix+'_PANEL_SD_M2_28.3mf'
  with zipfile.ZipFile(SOURCE) as z:files={f:z.read(f) for f in z.namelist() if f!='Metadata/slice_info.config' and not f.lower().endswith(('.png','.jpg','.jpeg'))}
  cfg=files['Metadata/project_settings.config'];settings=json.loads(cfg)
  assert settings['printer_settings_id']=='EnderNeo SAFE' and settings['hot_plate_temp']==['60']
  assert settings['filament_settings_id']==['Generic PLA @System - First Print']
  model=ET.fromstring(files['3D/3dmodel.model']);meta=ET.fromstring(files['Metadata/model_settings.config'])
  target=next(x for x in meta.findall('object') if any(m.get('key')=='name' and m.get('value')==name for m in x.findall('metadata')));ident=target.get('id')
  for item in list(model.find(C+'build')):
   if item.get('objectid')!=ident:model.find(C+'build').remove(item)
  for obj in list(model.find(C+'resources')):
   if obj.get('id')!=ident:model.find(C+'resources').remove(obj)
  for obj in list(meta.findall('object')):
   if obj.get('id')!=ident:meta.remove(obj)
  plate=meta.find('plate')
  for inst in list(plate.findall('model_instance')):
   if not any(m.get('key')=='object_id' and m.get('value')==ident for m in inst.findall('metadata')):plate.remove(inst)
  for m in plate.findall('metadata'):
   if m.get('key')=='plater_name':m.set('value',key)
  files['3D/3dmodel.model']=ET.tostring(model,encoding='utf-8',xml_declaration=True);files['Metadata/model_settings.config']=ET.tostring(meta,encoding='utf-8',xml_declaration=True)
  with zipfile.ZipFile(O/'plates'/filename,'w',zipfile.ZIP_DEFLATED) as z:
   for f,data in files.items():z.writestr(f,data)
  assert len(model.find(C+'build'))==1 and len(meta.findall('object'))==1
  with zipfile.ZipFile(SOURCE) as src:
   meshfiles=[f for f in files if f.startswith('3D/Objects/') and name in f]
   assert meshfiles and all(files[f]==src.read(f) for f in meshfiles)
  assert files['Metadata/project_settings.config']==cfg
  selected=[part for part in original['parts'] if part['name']==name];assert len(selected)==1
  summary['plates'][key]={'file':filename,'parts':selected,'settings_overrides':settings}
  proof[key]={'single_build_object':ident,'part':name,'geometry_files_byte_identical':meshfiles,'support_blocker_preserved':len(target.findall('part'))>1,'settings_byte_identical':True,'placement_unchanged':True}
 js(O/'build-summary.json',summary);js(O/'reports/split-provenance.json',proof)
 text=(P/'slice_and_check.py').read_text().replace(str(P),str(O));(O/'slice_and_check.py').write_text(text)
 phase('Slicing left and right individually')
 process=subprocess.run(['python3',str(O/'slice_and_check.py'),'08L','08R'],cwd=ROOT,capture_output=True,text=True,timeout=1800)
 (O/'slicer-run.log').write_text(process.stdout+'\n'+process.stderr);assert process.returncode==0,process.stderr
 S={k:json.loads((O/'slice-check'/k/'check.json').read_text()) for k in summary['plates']}
 for k,report in S.items():
  assert report['exit_code']==0 and report['original_start_guard_passed'] and report['extrusions_fit_220_with_0_5mm_margin'],(k,report)
  log=(O/'slice-check'/k/'slicer.log').read_text();warnings=[line for line in log.splitlines() if re.search(r'error|warning|potentially lost|floating',line,re.I)];assert not warnings,(k,warnings)
 # Check support finite segments against the actual native insert-bore envelopes at the unchanged plate placements.
 phase('Checking supports, SAFE starts and SD colour changes')
 checker=(P/'verify_print_release.py').read_text();a=checker.index('bores=');b=checker.index('# A single-colour shell',a)
 checker=checker[a:b].replace("for key in ['02','07','08']:","for key in list(B['plates']):").replace("if key in ['07','08']:",'if True:')
 rep={'support_inside_new_insert_bores':{}};envelopes=json.loads((P/'native-mount-envelopes.json').read_text())
 exec(compile(checker,'single-panel-finite-support-check','exec'),{'np':np,'json':json,'R':O,'B':summary,'N':envelopes,'rep':rep})
 assert len(rep['support_inside_new_insert_bores'])==2
 assert all(v['centreline_samples_inside']==0 and v.get('segments_intersecting_bore_with_0_20mm_bead_allowance',0)==0 for v in rep['support_inside_new_insert_bores'].values())
 js(O/'reports/support-bore-verification.json',rep)
 sys.path.insert(0,str(P));import postprocess_sd_colours as colours
 jobs=[]
 for key,info in summary['plates'].items():
  plain=(O/'slice-check'/key/'plate_1.gcode').read_text();gcode,report=colours.make(plain,'08');name=Path(info['file']).with_suffix('.gcode').name
  dest=O/'READY_TO_PRINT'/name;dest.write_text(gcode)
  guard=subprocess.run(['python3',str(Path.home()/'bin/check-ender3-start.py'),str(dest)],capture_output=True,text=True);assert guard.returncode==0,guard.stdout
  assert gcode.count('\nM0 ')==6
  js(O/'reports'/(name+'-colour-stops.json'),report)
  estimated=next(x for x in S[key]['header'] if 'estimated printing time' in x);seconds=sum(int(n)*{'h':3600,'m':60,'s':1}[u] for n,u in re.findall(r'(\d+)([hms])',estimated))
  grams=float(next(x.split('=')[1] for x in S[key]['header'] if x.startswith('; filament used [g]')))
  swaps=[{'load':x['load_colour'],'boundary_mm':x['actual_model_boundary_mm'],'estimated_elapsed_seconds':max(0,seconds-int((x['remaining_estimated_minutes'] or 0)*60))} for x in report['changes']]
  jobs.append({'key':key,'file':name,'part':info['parts'][0]['name'],'seconds':seconds,'grams':grams,'swaps':swaps,'sha256':sha(dest)})
 # Replay every released pause and move using the previously established modal-state verifier.
 checker=(P/'verify_sd_states.py').read_text();a=checker.index('R=Path(');b=checker.index('for f in ',a);checker=checker[:a]+"R=O/'reports';res={}\n"+checker[b:]
 a=checker.index('for f in ');b=checker.index('\n state=',a);checker=checker[:a]+"for f in sorted((O/'READY_TO_PRINT').glob('*.gcode')):"+checker[b:]
 checker=checker.replace('assert len(res)==3','assert len(res)==2').replace(';print(json.dumps(res,indent=2))','');exec(compile(checker,'single-panel-pause-state-replay','exec'),{'O':O})
 jobs.sort(key=lambda x:x['seconds']);js(O/'reports/jobs.json',jobs)
 assert jobs[0]['seconds']<5*3600,('No single-panel option fits five hours',jobs)
 lines=['# Individual front panels for a five-hour print window','','These are the same calibrated 2.8 mm front panels, separated into individual jobs. Geometry, orientation, positions, Neo SAFE, brim, supports and PLA settings are preserved. Both start RED and pause for GREY, RED, GREY. These replace the combined front-panel job when printing separately; do not print the same panels twice.','']
 for job in jobs:
  lines.append(f"{job['file']}: {job['part']}, {job['seconds']//3600}h {(job['seconds']%3600)//60:02d}m {job['seconds']%60:02d}s, {job['grams']:.2f} g.")
  for x in job['swaps']:lines.append(f"  Change to {x['load']} at approximately {x['estimated_elapsed_seconds']//3600}h {(x['estimated_elapsed_seconds']%3600)//60:02d}m, colour boundary {x['boundary_mm']:.2f} mm.")
 lines+=['','Times exclude warm-up, waiting at colour stops and manual purging. At each change: first click acknowledges you and reheats; at the second stop change/purge/wipe, reengage idler and click. Keep head and bed still.','', 'Verification: source mesh bytes, full project settings and support blockers preserved; SAFE starts pass; extrusion bounds within 220x220; supports clear of both insert bores; all released pause states restore XYZ, extrusion mode/coordinate, feed and heaters. No printer job started.']
 (O/'START_HERE.md').write_text('\n'.join(lines)+'\n')
 for k in S:shutil.copy2(O/'slice-check'/k/'check.json',O/'reports'/(k+'-slice-check.json'))
 export=O/'DELIVERY';export.mkdir(exist_ok=True)
 for folder in ['READY_TO_PRINT','plates','reports']:shutil.copytree(O/folder,export/folder,dirs_exist_ok=True)
 shutil.copy2(O/'START_HERE.md',export/'START_HERE.md');shutil.copy2(O/'build-summary.json',export/'build-summary.json')
 js(export/'SHA256SUMS.json',{str(p.relative_to(export)):sha(p) for p in sorted(export.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'})
 archive=N/'Gladiator_Single_Front_Panels_5h_20261022.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(export.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(export)))
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None
 incoming=Path.home()/'3D-Printer/Incoming/Gladiator/Round5_SINGLE_PANELS_5h_20261022';shutil.copytree(export,incoming,dirs_exist_ok=True)
 phase('PASSED - individual panels ready')
 print(json.dumps({'archive':str(archive),'jobs':jobs,'recommended':jobs[0]['file']},indent=2),flush=True)
except BaseException:
 (O/'ERROR.txt').write_text(traceback.format_exc());phase('FAILED - see ERROR.txt')
