from pathlib import Path
import json,sys,zipfile,hashlib,subprocess,re,time,traceback
r=Path('/home/buralien/projects/gladiator-cad');src=r/'cad/head/camera-service-v2-20261021';out=src/'event-print-20261024'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 sys.path.insert(0,str(r/'cad/v2/enclosure/round5-print-20261022/jim-settings-reslice/source'))
 from jimflat import preset_values
 chains={};pv=preset_values('0.20mm Standard - FIrst Layer Comp','Generic PLA @System - First Print',chains)
 protected={p:digest(Path(p)) for paths in chains.values() for p in paths}
 expected={'Camera_Service_v2_Tray.stl':'012abba14aaddbfc432e0bcb29f8cc722d7b9556f41abd6524c80163fe447d41','Camera_Service_v2_Lid.stl':'ef633e4184a062c81482aa5ff1bea47c4b7f81046657dfc1949ef06e59333bd9'}
 for name,h in expected.items():assert digest(src/'stl'/name)==h,(name,'changed review mesh')
 ns={};exec(compile((r/'scripts/build_v2_savings_plates.py').read_text().split('summary = {}')[0],'existing-plate-packager','exec'),ns)
 ns['OUT']=out;ns['INCOMING']=out/'project-copy';ns['INCOMING'].mkdir(exist_ok=True)
 with zipfile.ZipFile(ns['TPL']) as z:settings=json.loads(z.read('Metadata/project_settings.config'))
 for k,v in pv.items():
  if k in ('compatible_printers','compatible_printers_condition','print_host') or k.startswith('printhost_'):continue
  old=settings.get(k)
  if isinstance(old,list):v=v if isinstance(v,list) else [v]
  elif isinstance(v,list) and old is not None and k!='post_process':v=','.join(v)
  settings[k]=v
 for k in list(settings):
  if k.startswith('printhost_') or k=='print_host':settings[k]=''
 overrides={'enable_support':'1','support_type':'normal(auto)','support_style':'snug','support_threshold_angle':'45','brim_type':'outer_only','brim_width':'5','curr_bed_type':'High Temp Plate','printer_settings_id':'EnderNeo SAFE','print_settings_id':'0.20mm Standard - FIrst Layer Comp','filament_settings_id':['Generic PLA @System - First Print'],'input_shaping_type':'Default'}
 settings.update(overrides);settings['post_process']=['/usr/bin/python3 /home/buralien/bin/check-ender3-start.py']
 parts=[('Camera_Service_v2_Tray',src/'stl/Camera_Service_v2_Tray.stl',(85,110),'outer_only',5),('Camera_Service_v2_Lid',src/'stl/Camera_Service_v2_Lid.stl',(135,110),'outer_only',5)]
 project,sizes=ns['build']('GLAD_CAMERA_SERVICE_V2.3mf','CAMERA_SERVICE_V2',settings,parts)
 cli=out/'slice-input.3mf'
 with zipfile.ZipFile(project) as zi,zipfile.ZipFile(cli,'w',zipfile.ZIP_DEFLATED) as zo:
  for item in zi.infolist():
   if item.filename.lower().endswith(('.png','.jpg','.jpeg')):continue
   data=zi.read(item.filename)
   if item.filename=='Metadata/project_settings.config':d=json.loads(data);d['post_process']=[];data=json.dumps(d,indent=2).encode()
   zo.writestr(item.filename,data)
 sliced=out/'sliced';sliced.mkdir(exist_ok=True)
 cmd=['flatpak','run','--filesystem=/home/buralien','com.orcaslicer.OrcaSlicer','--slice','1','--orient','0','--arrange','0','--outputdir',str(sliced),str(cli)]
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=1200);(out/'slice.log').write_text(p.stdout+p.stderr)
 files=list(sliced.glob('*.gcode'));assert p.returncode==0 and len(files)==1,(p.returncode,(p.stdout+p.stderr)[-1500:])
 g=out/'GLAD_CAMERA_SERVICE_V2.gcode';g.write_bytes(files[0].read_bytes())
 check=subprocess.run(['python3','/home/buralien/bin/check-ender3-start.py',str(g)],capture_output=True,text=True);assert check.returncode==0,check.stdout+check.stderr
 text=g.read_text();header=[line for line in text.splitlines() if any(s in line for s in ['estimated printing time (normal mode)','filament used [g]','total filament used [g]'])]
 assert 'M600' not in '\n'.join(l for l in text.splitlines() if not l.startswith(';'))
 assert all(digest(Path(p))==h for p,h in protected.items())
 # The original unmodified source meshes are the provenance for both parts.
 report={'status':'sliced-start-check-passed; final support/bounds/config audit pending','header':header,'sizes':sizes,'sourceHashes':expected,'presetHashes':protected,'intentionalOverrides':overrides,'guard':check.stdout.strip(),'gcode':g.name,'printerStarted':False}
 (out/'slice-report.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report),flush=True)
except BaseException:
 (out/'ERROR.txt').write_text(traceback.format_exc());raise
