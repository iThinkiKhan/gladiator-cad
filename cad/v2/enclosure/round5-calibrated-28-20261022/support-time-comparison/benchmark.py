from pathlib import Path
import json,zipfile,subprocess,re,time,concurrent.futures,traceback,hashlib,math
R=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-calibrated-28-20261022');O=R/'support-time-comparison';B=json.loads((R/'print/build-summary.json').read_text())
cases=[('07','hood_base35',{'support_base_pattern_spacing':'3.5'}),('07','hood_support80',{'support_speed':'80'}),('07','hood_base35_speed80',{'support_base_pattern_spacing':'3.5','support_speed':'80'}),('08','panels_normal',{'support_type':'normal(auto)','support_style':'snug','support_closing_radius':'0'}),('08','panels_normal_base35',{'support_type':'normal(auto)','support_style':'snug','support_closing_radius':'0','support_base_pattern_spacing':'3.5'}),('08','panels_tree_base35',{'support_base_pattern_spacing':'3.5'}),('08','panels_support80',{'support_speed':'80'}),('08','panels_tree_base35_speed80',{'support_base_pattern_spacing':'3.5','support_speed':'80'})]
def stats(p):
 data=p.read_text();h=next(l for l in data.splitlines() if l.startswith('; estimated printing time (normal mode)'))
 secs=sum(int(n)*{'h':3600,'m':60,'s':1}[u] for n,u in re.findall(r'(\d+)([hms])',h));grams=float(next(l.split('=')[1] for l in data.splitlines() if l.startswith('; total filament used [g]')))
 x=y=z=e=0.;rel=True;role='';roles={};f=1800.;area={}
 for line in data.splitlines():
  if line.startswith(';TYPE:'):role=line[6:].strip()
  raw=line.split(';')[0].strip()
  if not raw:continue
  cmd=raw.split()[0];v={a:float(b) for a,b in re.findall(r'\b([XYZEF])([-+]?\d*\.?\d+)',raw)}
  if cmd in ['G90','G91']:rel=False
  elif cmd=='M83':rel=True
  elif cmd=='M82':rel=False
  elif cmd=='G92':e=v.get('E',e)
  elif cmd in ['G0','G1']:
   nx,ny,nz=v.get('X',x),v.get('Y',y),v.get('Z',z);f=v.get('F',f);de=v.get('E',0 if rel else e);de=de if rel else de-e
   if 'E' in v:e=e+v['E'] if rel else v['E']
   length=math.sqrt((nx-x)**2+(ny-y)**2+(nz-z)**2)
   if de>0 and length>0:
    rec=roles.setdefault(role,{'length_mm':0.,'extrusion_mm':0.,'constant_speed_seconds':0.});rec['length_mm']+=length;rec['extrusion_mm']+=de;rec['constant_speed_seconds']+=length/(f/60)
   x,y,z=nx,ny,nz
 return {'seconds':secs,'grams':grams,'roles':roles}
base={k:stats(R/'print/slice-check'/k/'plate_1.gcode') for k in ['07','08']}
(O/'baseline.json').write_text(json.dumps(base,indent=2))
def one(case):
 key,name,changes=case;d=O/name;d.mkdir(exist_ok=True);src=R/'SD_PACKAGE/plates'/('GLAD_04_HOOD_SD_M2_28.3mf' if key=='07' else 'GLAD_05_PANELS_SD_M2_28.3mf')
 with zipfile.ZipFile(src) as z:files={f:z.read(f) for f in z.namelist() if f!='Metadata/slice_info.config'}
 config=json.loads(files['Metadata/project_settings.config']);before=dict(config);config.update(changes)
 diff={k:config[k] for k in config if config[k]!=before.get(k)};assert diff==changes
 # Structural settings, machine/filament profiles, all model meshes and local blockers stay identical.
 protected=['wall_loops','sparse_infill_density','sparse_infill_pattern','layer_height','top_shell_layers','bottom_shell_layers','outer_wall_speed','inner_wall_speed','filament_max_volumetric_speed','machine_start_gcode','nozzle_temperature','hot_plate_temp']
 assert all(config[k]==before[k] for k in protected)
 files['Metadata/project_settings.config']=json.dumps(config,indent=2).encode();project=d/(name+'.3mf')
 with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED) as z:
  for f,data in files.items():z.writestr(f,data)
 config['post_process']=[];files['Metadata/project_settings.config']=json.dumps(config,indent=2).encode();inp=d/'slice-input.3mf'
 with zipfile.ZipFile(inp,'w',zipfile.ZIP_DEFLATED) as z:
  for f,data in files.items():z.writestr(f,data)
 t=time.time();p=subprocess.run(['flatpak','run','--filesystem=/home/buralien','com.orcaslicer.OrcaSlicer','--slice','1','--orient','0','--arrange','0','--outputdir',str(d),str(inp)],capture_output=True,text=True,timeout=1500,cwd=d)
 log=p.stdout+'\n'+p.stderr;(d/'slicer.log').write_text(log);warnings=[l for l in log.splitlines() if re.search(r'error|warning|potentially lost|floating',l,re.I)]
 result={'key':key,'name':name,'changes':changes,'exit_code':p.returncode,'warnings':warnings,'source_meshes_and_blockers_unchanged':True,'structural_settings_and_machine_filament_fields_unchanged':True,'slice_seconds':round(time.time()-t,1)}
 g=d/'plate_1.gcode'
 if g.exists():
  result.update(stats(g));guard=subprocess.run(['python3',str(Path.home()/'bin/check-ender3-start.py'),str(g)],capture_output=True,text=True);result['SAFE_guard_passed']=guard.returncode==0;result['saved_seconds']=base[key]['seconds']-result['seconds']
 (d/'result.json').write_text(json.dumps(result,indent=2));return result
try:
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for result in pool.map(one,cases):results.append(result);(O/'results.json').write_text(json.dumps(results,indent=2))
 print(json.dumps([{k:v for k,v in x.items() if k!='roles'} for x in results],indent=2),flush=True)
 (O/'DONE').write_text('Slicing comparisons complete; selected candidates still need support, bounds and pause checks.')
except BaseException:(O/'ERROR.txt').write_text(traceback.format_exc())
