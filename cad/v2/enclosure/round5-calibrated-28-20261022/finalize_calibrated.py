from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,zipfile,xml.etree.ElementTree as ET
ROOT=Path('/home/buralien/projects/gladiator-cad');N=ROOT/'cad/v2/enclosure/round5-calibrated-28-20261022';P=N/'print';PK=N/'SD_PACKAGE';OLD=ROOT/'cad/v2/enclosure/round5-print-20261022'
sys.path.insert(0,str(P));import postprocess_sd_colours as colour
V=json.loads((P/'print-verification.json').read_text());B=json.loads((P/'build-summary.json').read_text())
assert json.loads((N/'saved-cad-verification.json').read_text())['passed']
assert V['all_22_source_parts_covered'] and V['all_slicer_guards_passed'] and V['all_extrusions_fit_220'] and V['source_hashes_unchanged']
assert len(V['support_inside_new_insert_bores'])==13
assert all(x['centreline_samples_inside']==0 and x.get('segments_intersecting_bore_with_0_20mm_bead_allowance',0)==0 for x in V['support_inside_new_insert_bores'].values())
assert not any(V['slicer_errors'].values())
for folder in ['READY_TO_PRINT','OPTIONAL_FIT_CHECK','plates','CAD/stl','reports','previews','source']:(PK/folder).mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p,data):p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
profile=Path.home()/'.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer'
def flatten(p):
 d=json.loads(p.read_text());base={}
 if d.get('inherits'):
  hits=list((profile/'user/default').rglob(d['inherits']+'.json'))+list((profile/'system').rglob(d['inherits']+'.json'));assert hits;base=flatten(hits[0])
 base.update(d);return base
machine=flatten(profile/'user/default/machine/EnderNeo SAFE.json')
filaments={name:flatten(profile/'user/default/filament'/(name+'.json')) for name in ['Generic PLA @System - First Print','Generic PLA Silk @System - First Print']}
skip={'name','type','from','version','inherits','compatible_printers','compatible_printers_condition','print_settings_id','printer_settings_id','filament_settings_id','printhost_apikey','print_host','printhost_user','printhost_password','default_print_profile','default_filament_profile'}
C='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
jobs=[('04','GLAD_01_WHITE_EMBLEMS_V2','WHITE','READY_TO_PRINT'),('06','GLAD_02_SILK_DETAILS','SILK','READY_TO_PRINT'),('02','GLAD_03_BLACK_CLAMPS_M2_28','BLACK','READY_TO_PRINT'),('07','GLAD_04_HOOD_SD_M2_28','RED -> GREY -> RED -> GREY','READY_TO_PRINT'),('08','GLAD_05_PANELS_SD_M2_28','RED -> GREY -> RED -> GREY','READY_TO_PRINT'),('01','GLAD_OPTIONAL_FIT_SEATS_M2_28','Regular PLA','OPTIONAL_FIT_CHECK')]
audit={'M2_bore_mm':2.8,'basis':'Jim accepted 2.8 mm from coupon, 2026-10-22','insert_bore_blocker':'CLEARED','profiles':{},'colour_changes':{},'print_file_guards':{},'no_printer_started':True,'completed':['tablets','red shield fields and crest','coupon','original white insets (superseded; reprint required)'],'remaining_accessories':['stronger white inset reprint','silk details','calibrated black clamps'],'LED_cover':'omitted; window open'}
for key,name,load,folder in jobs:
 f=P/'plates'/B['plates'][key]['file']
 with zipfile.ZipFile(f) as z:files={x:z.read(x) for x in z.namelist() if x!='Metadata/slice_info.config'}
 cfg=json.loads(files['Metadata/project_settings.config']);mat='Generic PLA Silk @System - First Print' if key=='06' else 'Generic PLA @System - First Print'
 mm={k:(val,cfg.get(k)) for k,val in machine.items() if k in cfg and k not in skip and cfg[k]!=val}
 ff={k:(val,cfg.get(k)) for k,val in filaments[mat].items() if k in cfg and k not in skip and cfg[k]!=val}
 assert not mm,(key,'machine mismatch',mm)
 assert not ff,(key,'filament mismatch',ff)
 assert cfg['printer_settings_id']=='EnderNeo SAFE' and cfg['filament_settings_id']==[mat]
 assert cfg['curr_bed_type']=='High Temp Plate' and cfg['hot_plate_temp']==['60']
 assert '/usr/bin/python3 /home/buralien/bin/check-ender3-start.py' in cfg['post_process']
 if key in ['07','08']:
  hook=f'/usr/bin/python3 {P}/postprocess_sd_colours.py --plate {key}'
  if hook not in cfg['post_process']:cfg['post_process'].append(hook)
 files['Metadata/project_settings.config']=json.dumps(cfg,indent=2).encode()
 model=ET.fromstring(files['3D/3dmodel.model']);meta=ET.fromstring(files['Metadata/model_settings.config'])
 for o in meta.findall('object'):
  parent=next(x for x in model.find(C+'resources') if x.get('id')==o.get('id'))
  if o.find('part') is not None:o.find('part').set('id',parent.find(C+'components')[0].get('objectid'))
 files['Metadata/model_settings.config']=ET.tostring(meta,encoding='utf-8',xml_declaration=True)
 with zipfile.ZipFile(PK/'plates'/(name+'.3mf'),'w',zipfile.ZIP_DEFLATED) as z:
  for fn,data in files.items():z.writestr(fn,data)
 source=P/'slice-check'/key/'plate_1.gcode';data=source.read_bytes().decode('utf-8')
 if key in ['07','08']:
  data,rep=colour.make(data,key);audit['colour_changes'][name]=rep;js(PK/'reports'/(name+'-colour-stops.json'),rep)
 target=PK/folder/(name+'.gcode');target.write_bytes(data.encode('utf-8'))
 guard=subprocess.run(['python3','/home/buralien/bin/check-ender3-start.py',str(target)],capture_output=True,text=True)
 assert guard.returncode==0,(name,guard.stdout)
 commands=[l.split(';')[0].strip().split()[0] for l in data.splitlines() if l.split(';')[0].strip()]
 assert commands.count('M0')==(6 if key in ['07','08'] else 0)
 assert not any(cmd in commands for cmd in ['M600','M601','M25','M500'])
 audit['profiles'][name]={'machine':'EnderNeo SAFE','filament':mat,'machine_fields_match':True,'filament_fields_match':True,'bed_c':60,'extrusions_in_220x220':True}
 audit['print_file_guards'][name]=guard.stdout.strip()
 audit.setdefault('jobs',[]).append({'file':folder+'/'+target.name,'plate':key,'load':load,**V['plate_times'][key],'sha256':sha(target)})
 # A fresh top/side toolpath preview belongs to this slice.
 preview=P/'previews'/(key+'-toolpaths.png')
 if preview.exists():shutil.copy2(preview,PK/'previews'/preview.name)
# Replay the exact released shell G-code, including all pause parks and modal state.
text=(P/'verify_sd_states.py').read_text()
a=text.index("R=Path(");b=text.index('for f in ',a)
text=text[:a]+"R=PK/'reports';res={}\n"+text[b:]
a=text.index('for f in ');b=text.index('\n state=',a)
text=text[:a]+"for f in [PK/'READY_TO_PRINT/GLAD_04_HOOD_SD_M2_28.gcode',PK/'READY_TO_PRINT/GLAD_05_PANELS_SD_M2_28.gcode']:"+text[b:]
text=text.replace('assert len(res)==3','assert len(res)==2').replace(';print(json.dumps(res,indent=2))','')
exec(compile(text,'released-shell-pause-check','exec'),{'PK':PK})
# Saved native and STEP have 22 current parts including stronger insets and reinforced calibrated clamps.
for name in ['Gladiator_Round5_Print.FCStd','Gladiator_Round5_PrintParts.step']:shutil.copy2(P/name,PK/'CAD'/name)
parts=json.loads((N/'style/validation.json').read_text())['parts']
for name in parts:
 source=N/'style/stl'/(name+'.stl')
 if name=='Crest_Clamp':source=P/'print-stl/Crest_Clamp.stl'
 elif name.startswith('Scutum_Emblem_'):source=OLD/'emblem-v2/Scutum_Emblem_v2.stl'
 shutil.copy2(source,PK/'CAD/stl'/(name+'.stl'))
assert len(list((PK/'CAD/stl').glob('*.stl')))==22
for name in ['build-summary.json','slice-summary.json','print-verification.json','support-blockers.json','native-mount-envelopes.json','fit-test-sources.json','preset-provenance.json','crest-clamp-reinforcement.json']:shutil.copy2(P/name,PK/'reports'/name)
for name in ['saved-cad-verification.json','PRINT_STATUS.json','protected-source-hashes.json']:shutil.copy2(N/name,PK/'reports'/name)
shutil.copy2(OLD/'emblem-v2/validation.json',PK/'reports/stronger-inset-v2-verification.json')
for name in ['build_style_28.py','build_print_variant.py','verify_saved_28.py','run_pipeline.py']:shutil.copy2(N/name,PK/'source'/name)
for name in ['build_print_plates.py','slice_and_check.py','postprocess_sd_colours.py','verify_print_release.py']:shutil.copy2(P/name,PK/'source'/name)
shutil.copy2(Path.home()/'bin/check-ender3-start.py',PK/'source/check-ender3-start.py')
js(PK/'reports/release-audit.json',audit)
def duration(seconds):return f'{seconds//3600}h {(seconds%3600)//60:02d}m' if seconds>=3600 else f'{seconds//60}m {seconds%60:02d}s'
rows=['# Gladiator - current calibrated print files, 22 October 2026','','M2 heat-set coupon accepted: **2.8 mm**. The insert-bore blocker is cleared.','','Already printed: tablets, red shields/crest and coupon. Reprint the stronger white insets; silk is still outstanding. The LED window stays open.','','| File | Load | Estimated print time |','| --- | --- | --- |']
for job in audit['jobs']:rows.append(f"| {Path(job['file']).name} | {job['load']} | {duration(job['seconds'])} |")
rows+=['','White v2 is the stronger revision, lying face-up with snug supports. The red shields you printed are unchanged. Silk uses your separate silk profile. Black clamps are newly released with 2.8 mm bores. Fit seats are optional; no extra coupon or LCD test is required.','','The two shell jobs are prepared for whenever you choose to print them. Each starts RED, then pauses for GREY, RED, GREY. At each change: first click acknowledges you and reheats; at the second stop swap and hand-purge to the requested colour, wipe, reengage the idler, then click. Keep the head and bed still. There are two clicks per change.','','| Shell | Load at stop | Actual colour boundary | Approximate elapsed slicer time |','| --- | --- | --- | --- |']
for name,rep in audit['colour_changes'].items():
 key='07' if 'HOOD' in name else '08';total=V['plate_times'][key]['seconds']
 for change in rep['changes']:
  elapsed=max(0,total-int((change.get('remaining_estimated_minutes') or 0)*60))
  rows.append(f"| {name} | {change['load_colour']} | {change['actual_model_boundary_mm']:.2f} mm | {duration(elapsed)} |")
rows+=['','Times exclude warm-up, waiting at pauses, manual purging and assembly.','','All files use EnderNeo SAFE with your inherited machine/filament presets, 60 C bed, original G28/M420 S1/left purge start and separate silk profile. Production bores are 2.8 mm, depth 4.0 mm retained; earlier structural insert sizes and screw clearances are unchanged. Original models and stronger-v2 source files remain hash-unchanged. All thirteen production bores checked in the saved native, 22 valid STEP solids, no support paths through the insert cavities, actual extrusion bounds inside 220 x 220 mm. Released shell pause states replayed and restored correctly. These are CAD/toolpath checks; actual assembly and clamp retention are not newly claimed as tested.','','Windows destination: X:/3D Printer. CAD and 3MF projects are included. Source scripts target cad-lab paths. No printer job has been started.']
(PK/'START_HERE.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
js(PK/'SHA256SUMS.json',{str(p.relative_to(PK)):sha(p) for p in sorted(PK.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'})
archive=N/'Gladiator_Calibrated_M2_28_20261022.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(PK.rglob('*')):
  if p.is_file():z.write(p,str(p.relative_to(PK)))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for path,h in json.loads(z.read('SHA256SUMS.json')).items():assert hashlib.sha256(z.read(path)).hexdigest()==h
incoming=Path.home()/'3D-Printer/Incoming/Gladiator/Round5_CALIBRATED_M2_28_20261022'
shutil.copytree(PK,incoming,dirs_exist_ok=True)
for path,h in json.loads((PK/'SHA256SUMS.json').read_text()).items():assert sha(incoming/path)==h
current='Current release: Round5_CALIBRATED_M2_28_20261022/\nM2 bore 2.8 mm accepted. Stronger white v2, silk and calibrated clamps remain; shell SD jobs ready when desired. LED window open. Earlier Round5_SD and Accessories_White_First folders are historical.\n'
(incoming.parent/'CURRENT_PRINTS.txt').write_text(current)
for folder,filename in [('Round5_SD_20261022','START_HERE.md'),('Accessories_White_First_20261022','START_HERE.txt')]:
 p=incoming.parent/folder/filename
 if p.exists():
  old=p.read_text();prefix='SUPERSEDED: use ../Round5_CALIBRATED_M2_28_20261022/. The 3.6 mm bores in this historical package are obsolete.\n\n'
  if not old.startswith('SUPERSEDED:'):p.write_text(prefix+old)
print(json.dumps({'archive':str(archive),'archive_bytes':archive.stat().st_size,'incoming':str(incoming),'jobs':audit['jobs'],'all_checks_passed':True},indent=2))
