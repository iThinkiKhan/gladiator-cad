from pathlib import Path
import json,hashlib,shutil,sys,re,subprocess,time,zipfile,traceback
N=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-calibrated-28-20261022');P=N/'print';O=N/'mount-checked-release';D=O/'DELIVERY'
def js(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 for i in range(360):
  if (O/'PIPELINE_ERROR.txt').exists():raise RuntimeError((O/'PIPELINE_ERROR.txt').read_text())
  status=json.loads((O/'status.json').read_text())['phase']
  if status.startswith('CAD and slice PASS'):break
  time.sleep(3)
 else:raise TimeoutError('hood pipeline')
 assert json.loads((O/'speaker-correction-verification.json').read_text())['passed']
 clearance=json.loads((O/'mounting-path-support-check.json').read_text());assert all(x['support_segment_hits_with_0_2mm_bead_allowance']==0 for x in clearance.values())
 for folder in ['CAD/stl','READY_TO_PRINT','plates','reports','previews']:(D/folder).mkdir(parents=True,exist_ok=True)
 shutil.copytree(N/'SD_PACKAGE/CAD',D/'CAD',dirs_exist_ok=True)
 for name in ['Gladiator_Round5_Print.FCStd','Gladiator_Round5_PrintParts.step']:shutil.copy2(O/name,D/'CAD'/name)
 shutil.copy2(O/'Rear_Hood.stl',D/'CAD/stl/Rear_Hood.stl')
 for name in ['speaker-correction-verification.json','mounting-path-support-check.json','project-preservation.json','support-blockers.json']:shutil.copy2(O/name,D/'reports'/name)
 for name in ['mount-access-audit.json','splayed-axis-clearance.json']:shutil.copy2(N/'mount-access-audit'/name,D/'reports'/name)
 name='GLAD_04_HOOD_SD_M2_28';shutil.copy2(O/'plates'/(name+'.3mf'),D/'plates'/(name+'.3mf'))
 with zipfile.ZipFile(O/'plates'/(name+'.3mf')) as z:cfg=z.read('Metadata/project_settings.config')
 with zipfile.ZipFile(N/'SD_PACKAGE/plates'/(name+'.3mf')) as z:assert cfg==z.read('Metadata/project_settings.config')
 settings=json.loads(cfg);assert settings['wall_loops']=='4' and settings['sparse_infill_density']=='30%' and settings['layer_height']=='0.28'
 sys.path.insert(0,str(P));import postprocess_sd_colours as colours
 raw=(O/'slice-check/07/plate_1.gcode').read_bytes().decode();gcode,report=colours.make(raw,'07');report['physical_SD_pause_test_required']=False;report['operator_has_previously_used_colour_changes']=True
 dest=D/'READY_TO_PRINT'/(name+'.gcode');dest.write_bytes(gcode.encode());js(D/'reports'/(name+'-colour-stops.json'),report)
 guard=subprocess.run(['python3',str(Path.home()/'bin/check-ender3-start.py'),str(dest)],capture_output=True,text=True);assert guard.returncode==0,guard.stdout+guard.stderr
 assert gcode.count('\nM0 ')==6 and not re.search(r'^M(?:600|500|501|502)\b',gcode,re.M)
 optimized=N/'shell-time-optimized/DELIVERY'
 for folder,ext in [('READY_TO_PRINT','.gcode'),('plates','.3mf')]:shutil.copy2(optimized/folder/('GLAD_05_PANELS_SD_M2_28'+ext),D/folder/('GLAD_05_PANELS_SD_M2_28'+ext))
 check=json.loads((O/'slice-check/07/check.json').read_text());header=check['header'];duration=next(l for l in header if l.startswith('; estimated printing time (normal mode)'));seconds=sum(int(n)*{'h':3600,'m':60,'s':1}[u] for n,u in re.findall(r'(\d+)([hms])',duration));grams=float(next(l.split('=')[1] for l in header if l.startswith('; total filament used [g]')))
 js(D/'reports/hood-slice-check.json',check)
 jobs=json.loads((optimized/'reports/jobs.json').read_text());old=next(x['seconds'] for x in jobs if x['key']=='07')
 for j in jobs:
  if j['key']=='07':j.update(seconds=seconds,grams=grams,saved_seconds=old-seconds,sha256=sha(dest),changes=[{'load':x['load_colour'],'boundary_mm':x['actual_model_boundary_mm'],'elapsed_seconds':max(0,seconds-int((x['remaining_estimated_minutes'] or 0)*60))} for x in report['changes']])
 for j in jobs:assert sha(D/'READY_TO_PRINT'/j['file'])==j['sha256']
 js(D/'reports/jobs.json',jobs)
 checker=(P/'verify_sd_states.py').read_text();a=checker.index('R=Path(');b=checker.index('for f in ',a);checker=checker[:a]+"R=D/'reports';res={}\n"+checker[b:];a=checker.index('for f in ');b=checker.index('\n state=',a);checker=checker[:a]+"for f in sorted((D/'READY_TO_PRINT').glob('*.gcode')):"+checker[b:];checker=checker.replace('assert len(res)==3','assert len(res)==2').replace(';print(json.dumps(res,indent=2))','');exec(compile(checker,'mount-checked-pause-replay','exec'),{'D':D})
 # Reuse the established actual-toolpath overview renderer.
 render=(P/'verify_print_release.py').read_text();a=render.index('# Toolpath top + side views');b=render.index("(R/'print-verification.json').write_text",a);render=render[a:b].replace("for k in ['01','02','03','04','05','06','07','08','09']:","for k in ['07']:")
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 from matplotlib.collections import LineCollection
 B=json.loads((O/'build-summary.json').read_text());S={'07':check}
 exec(compile(render,'corrected-hood-preview','exec'),{'Path':Path,'json':json,'R':O,'B':B,'S':S,'plt':plt,'LineCollection':LineCollection})
 shutil.copytree(O/'previews',D/'previews',dirs_exist_ok=True)
 for name in ['correct_speaker_mount.py','prepare_corrected_hood.py','finalize_mount_checked.py']:shutil.copy2(O/name,D/'reports'/name)
 lines=['# Mount-checked shell release - 22 October 2026','','Use the hood file in this release; earlier hood files are superseded. Both front panels remain together, unchanged at7h00m34s. Hood: '+duration.split('=')[1].strip()+'. Estimates exclude heating, pauses and handling.','','Antenna:7mm through-hole in2mm flat mounting land;22mm clear flat zone. CAD nut/flange12mm and short20mm tool-envelope checks pass. X ribs reinforce the surrounding wall. Actual antenna hardware dimensions remain as recorded; no new physical fit claimed.','','Speaker:two previously retained1.6mm pilots corrected to tested2.8mm M2 heat-set pockets,4mm usable depth with0.15mm lead-in. Install inserts flush; measured ears2.8mm use M2x6. Install speaker with hood OFF:breadboard blocks one assembled driver path.7mm pads and roof retained.','','Rails:six mount positions verified against saved installed rail CAD. Local3.6mm clearance relief follows actual0.644degree splay, retaining round-hole calibration. Six M3x20 screws clear; M3x25 bottoms against blind rail bores. Head bearing and6mm driver access pass. Existing rail M3 insert bores remain unchanged. Front panels mount to the hood via four roof tabs, not directly to rails.','','All22 checked hood fastener cylinders have zero support intersections, including0.20mm bead allowance. Machine, material and process settings are byte-identical to the previous hood project; only geometry corrections and local support exclusions changed.4walls,30%infill,0.28mm layers retained. New native and22-solid reopened STEP,manifold STL,SAFE start,220mm bounds and actual SD pause replays pass.','','Both jobs start RED, then GREY, RED, GREY. Two clicks per change:acknowledge/reheat,then swap and hand-purge/wipe,reengage idler,resume. Keep head and bed still. No diagnostic test required.','']
 for j in jobs:
  lines.append(j['file'])
  for c in j['changes']:lines.append('  '+c['load']+' at about '+str(c['elapsed_seconds']//3600)+'h'+str((c['elapsed_seconds']%3600)//60).zfill(2)+'m')
 lines+=['','Printed:tablets,red shields/crest,coupon. Remaining accessories:stronger white emblems v2,silk,black clamps. LED window open. No printer started.']
 (D/'START_HERE.md').write_text('\n'.join(lines)+'\n')
 js(D/'SHA256SUMS.json',{str(p.relative_to(D)):sha(p) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'})
 archive=N/'Gladiator_Mount_Checked_20261022.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(D.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(D)))
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None
 incoming=Path.home()/'3D-Printer/Incoming/Gladiator/Round5_MOUNT_CHECKED_20261022';shutil.copytree(D,incoming,dirs_exist_ok=True)
 js(O/'FINAL_PASS.json',{'archive':str(archive),'sha256':sha(archive),'jobs':jobs,'total_shell_seconds':sum(x['seconds'] for x in jobs),'support_paths':len(clearance),'CAD_STEP_STL_SAFE_bounds_support_pause_pass':True,'printer_started':False})
 print('PASS',seconds,grams,flush=True)
except BaseException:(O/'FINAL_ERROR.txt').write_text(traceback.format_exc())
