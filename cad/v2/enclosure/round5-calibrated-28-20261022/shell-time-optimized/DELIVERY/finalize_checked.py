from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,zipfile,collections,math,traceback
import numpy as np
ROOT=Path('/home/buralien/projects/gladiator-cad');N=ROOT/'cad/v2/enclosure/round5-calibrated-28-20261022';P=N/'print';O=N/'shell-time-optimized';BENCH=N/'support-time-comparison'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def phase(s):js(O/'status.json',{'phase':s});print(s,flush=True)
def parse(path):
 text=path.read_text();rows=[];x=y=z=pe=0.;rel=True;role='';bounds=[1e9,1e9,-1e9,-1e9];model_e=0.;heights=[]
 for l in text.splitlines():
  if l.startswith(';TYPE:'):role=l[6:].strip()
  if l.startswith(';Z:'):heights.append(float(l.split(':')[1]))
  if l.startswith('M82'):rel=False
  if l.startswith('M83'):rel=True
  if l.startswith('G92'):
   m=re.search(r' E([-\d.]+)',l)
   if m:pe=float(m[1])
  if not re.match(r'^G[01]\s',l):continue
  v={a:float(b) for a,b in re.findall(r'([XYZE])([-\d.]+)',l.split(';')[0])};nx=v.get('X',x);ny=v.get('Y',y);nz=v.get('Z',z);e=v.get('E',0 if rel else pe);de=e if rel else e-pe
  if 'E' in v:pe=e
  if de>0 and (nx!=x or ny!=y):
   bounds=[min(bounds[0],x,nx),min(bounds[1],y,ny),max(bounds[2],x,nx),max(bounds[3],y,ny)]
   if role:rows.append([x,y,nx,ny,nz,role])
   if not role.startswith('Support') and role not in ['Custom','Brim','Skirt']:model_e+=de
  x,y,z=nx,ny,nz
 header=[l for l in text.splitlines() if l.startswith(';') and any(s in l for s in ['estimated printing time','total filament','filament used [g]','total layers count'])]
 duration=next(l for l in header if l.startswith('; estimated printing time (normal mode)'))
 seconds=sum(int(n)*{'h':3600,'m':60,'s':1}[u] for n,u in re.findall(r'(\d+)([hms])',duration));grams=float(next(l.split('=')[1] for l in header if l.startswith('; total filament used [g]')))
 return {'header':header,'seconds':seconds,'grams':grams,'extrusion_bounds_xy_mm':bounds,'extrusions_fit_220_with_0_5mm_margin':min(bounds[:2])>=.5 and max(bounds[2:])<=219.5,'model_extrusion_mm':model_e,'layer_heights_mm':heights},rows
try:
 phase('Validating final artifacts: combined panels optimized, hood unchanged')
 names={'07':'GLAD_04_HOOD_SD_M2_28','08':'GLAD_05_PANELS_SD_M2_28'};baseB=json.loads((P/'build-summary.json').read_text());B={'plates':{}};S={};proof={};jobs=[]
 for folder in ['plates','slice-check','READY_TO_PRINT','reports','previews']:(O/folder).mkdir(exist_ok=True)
 for k,name in names.items():
  baseline=N/'SD_PACKAGE/plates'/(name+'.3mf');selected=baseline if k=='07' else BENCH/'panels_normal_base35/panels_normal_base35.3mf'
  with zipfile.ZipFile(selected) as z:files={f:z.read(f) for f in z.namelist()};cfg=json.loads(files['Metadata/project_settings.config'])
  with zipfile.ZipFile(baseline) as z:
   before=json.loads(z.read('Metadata/project_settings.config'));assert all(files[f]==z.read(f) for f in files if f.startswith('3D/'))
  changes={name:value for name,value in cfg.items() if before.get(name)!=value};allowed={} if k=='07' else {'support_type':'normal(auto)','support_style':'snug','support_closing_radius':'0','support_base_pattern_spacing':'3.5'}
  assert changes==allowed,(k,changes)
  assert cfg['wall_loops']=='4' and cfg['sparse_infill_density']=='30%' and cfg['layer_height']=='0.28'
  assert cfg['support_speed']=='60' and cfg['support_interface_speed']=='40'
  shutil.copy2(selected,O/'plates'/(name+'.3mf'));entry=dict(baseB['plates'][k]);entry['file']=name+'.3mf';entry['settings_overrides']=cfg;B['plates'][k]=entry
  source=P/'slice-check'/k/'plate_1.gcode' if k=='07' else BENCH/'panels_normal_base35/plate_1.gcode';d=O/'slice-check'/k;d.mkdir(exist_ok=True);shutil.copy2(source,d/'plate_1.gcode')
  check,segments=parse(source);original,oldsegments=parse(P/'slice-check'/k/'plate_1.gcode')
  def canonical(rows):
   return collections.Counter(tuple(sorted([(round(s[0],5),round(s[1],5)),(round(s[2],5),round(s[3],5))]))+(round(s[4],5),s[5]) for s in rows if not s[5].startswith('Support') and s[5] not in ['Custom','Brim','Skirt'])
  assert canonical(segments)==canonical(oldsegments),(k,'Printed model centerlines changed')
  assert abs(check['model_extrusion_mm']-original['model_extrusion_mm'])<.005,(k,'Printed model material changed')
  assert check['extrusions_fit_220_with_0_5mm_margin']
  guard=subprocess.run(['python3',str(Path.home()/'bin/check-ender3-start.py'),str(d/'plate_1.gcode')],capture_output=True,text=True);assert guard.returncode==0
  check['original_start_guard_passed']=True;check['guard_output']=guard.stdout.strip();S[k]=check
  js(d/'segments.json',segments);js(d/'check.json',check)
  proof[k]={'config_changes':changes,'geometry_and_blockers_byte_identical':True,'all_other_settings_unchanged':True,'printed_shell_centerlines_identical_ignoring_path_direction':True,'printed_shell_extrusion_mm_difference':check['model_extrusion_mm']-original['model_extrusion_mm'],'seconds_saved':original['seconds']-check['seconds'],'source_gcode_sha256':sha(source)}
 js(O/'build-summary.json',B);js(O/'reports/structural-preservation.json',proof)
 # Check all seven shell insert cavities against actual support segments.
 checker=(P/'verify_print_release.py').read_text();a=checker.index('bores=');b=checker.index('# A single-colour shell',a);checker=checker[a:b].replace("for key in ['02','07','08']:","for key in ['07','08']:")
 rep={'support_inside_new_insert_bores':{}};envelopes=json.loads((P/'native-mount-envelopes.json').read_text());exec(compile(checker,'final-support-check','exec'),{'np':np,'json':json,'R':O,'B':B,'N':envelopes,'rep':rep})
 assert len(rep['support_inside_new_insert_bores'])==7 and all(x['centreline_samples_inside']==0 and x.get('segments_intersecting_bore_with_0_20mm_bead_allowance',0)==0 for x in rep['support_inside_new_insert_bores'].values())
 js(O/'reports/support-clearance.json',rep)
 sys.path.insert(0,str(P));import postprocess_sd_colours as colours
 for k,name in names.items():
  plain=(O/'slice-check'/k/'plate_1.gcode').read_text();gcode,colour=colours.make(plain,k);dest=O/'READY_TO_PRINT'/(name+'.gcode');dest.write_bytes((N/'SD_PACKAGE/READY_TO_PRINT'/dest.name).read_bytes()) if k=='07' else dest.write_text(gcode)
  guard=subprocess.run(['python3',str(Path.home()/'bin/check-ender3-start.py'),str(dest)],capture_output=True,text=True);assert guard.returncode==0
  assert gcode.count('\nM0 ')==6
  js(O/'reports'/(name+'-colour-stops.json'),colour)
  jobs.append({'key':k,'file':dest.name,'seconds':S[k]['seconds'],'grams':S[k]['grams'],'saved_seconds':proof[k]['seconds_saved'],'start_colour':'RED','changes':[{'load':x['load_colour'],'boundary_mm':x['actual_model_boundary_mm'],'elapsed_seconds':max(0,S[k]['seconds']-int((x['remaining_estimated_minutes'] or 0)*60))} for x in colour['changes']],'sha256':sha(dest)})
 # Replay all actual emitted colour pauses and movement.
 checker=(P/'verify_sd_states.py').read_text();a=checker.index('R=Path(');b=checker.index('for f in ',a);checker=checker[:a]+"R=O/'reports';res={}\n"+checker[b:];a=checker.index('for f in ');b=checker.index('\n state=',a);checker=checker[:a]+"for f in sorted((O/'READY_TO_PRINT').glob('*.gcode')):"+checker[b:]
 checker=checker.replace('assert len(res)==3','assert len(res)==2').replace(';print(json.dumps(res,indent=2))','');exec(compile(checker,'final-shell-pause-replay','exec'),{'O':O})
 phase('Rendering final shell and support previews')
 render=(P/'verify_print_release.py').read_text();a=render.index('# Toolpath top + side views');b=render.index("(R/'print-verification.json').write_text",a);render=render[a:b].replace("for k in ['01','02','03','04','05','06','07','08','09']:","for k in ['07','08']:")
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 from matplotlib.collections import LineCollection
 exec(compile(render,'selected-support-previews','exec'),{'Path':Path,'json':json,'R':O,'B':B,'S':S,'plt':plt,'LineCollection':LineCollection})
 js(O/'reports/jobs.json',jobs);js(O/'reports/slice-checks.json',S)
 comparison=json.loads((BENCH/'results.json').read_text());js(O/'reports/benchmarks.json',[{k:v for k,v in x.items() if k!='roles'} for x in comparison])
 lines=['# Shell time reduction - combined front panels retained','','Current combined front panels: 7h 00m 34s (was 8h31m20s). Hood unchanged at9h43m33s. Total16h44m07s; saving1h30m46s. Times exclude warm-up, waiting at pauses, purging and handling.','','Only the panel support layout changes: snug normal supports, base spacing3.5mm instead of2.5. Dense contact interfaces, gaps, support speed, all model geometry and printed shell extrusion centerlines/material remain unchanged. Four walls,30% crosshatch infill,0.28mm layers,four top/bottom layers,calibrated2.8mm bores,Neo SAFE and original PLA/material/machine settings retained. No physical strength test newly claimed.','','The hood stays at its original settings. Other benchmark variants are recorded but not released. Individual split-panel files are optional; the main queue uses both panels together.','','Both shell jobs start RED, then SD pauses for GREY, RED, GREY. Two clicks per change: acknowledge/reheat, then swap and hand-purge/wipe/reengage idler/resume. Keep head and bed still. No LCD test required.','']
 for job in jobs:
  lines.append(job['file'])
  for c in job['changes']:lines.append(f"  {c['load']} at about {c['elapsed_seconds']//3600}h{(c['elapsed_seconds']%3600)//60:02d}m; colour boundary {c['boundary_mm']:.2f}mm")
 (O/'START_HERE.md').write_text('\n'.join(lines)+'\n')
 export=O/'DELIVERY';export.mkdir(exist_ok=True)
 for folder in ['READY_TO_PRINT','plates','reports','previews']:shutil.copytree(O/folder,export/folder,dirs_exist_ok=True)
 for name in ['START_HERE.md','build-summary.json','finalize_checked.py']:shutil.copy2(O/name,export/name)
 js(export/'SHA256SUMS.json',{str(p.relative_to(export)):sha(p) for p in sorted(export.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'})
 archive=N/'Gladiator_Combined_Shells_Time_Optimized_20261022.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(export.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(export)))
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None
 incoming=Path.home()/'3D-Printer/Incoming/Gladiator/Round5_COMBINED_SHELLS_20261022';shutil.copytree(export,incoming,dirs_exist_ok=True)
 phase('PASSED - combined shells ready for visual check and delivery')
 print(json.dumps({'archive':str(archive),'jobs':jobs,'total_seconds':sum(x['seconds'] for x in jobs),'saved_seconds':sum(x['saved_seconds'] for x in jobs)},indent=2),flush=True)
except BaseException:(O/'FINAL_ERROR.txt').write_text(traceback.format_exc());phase('FAILED - see FINAL_ERROR.txt')
