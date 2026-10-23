from pathlib import Path
import subprocess,json,re,math,concurrent.futures,time,zipfile,sys
R=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-calibrated-28-20261022/single-panels-5h')
summary=json.loads((R/'build-summary.json').read_text()); (R/'slice-check').mkdir(exist_ok=True)
def one(key):
 info=summary['plates'][key];out=R/'slice-check'/key;out.mkdir(exist_ok=True)
  # CLI rejects post_process. Slice a work copy with only that hook disabled, then run the original guard directly.
 inp=out/'slice-input.3mf'
 for old in out.glob('*.gcode'):old.unlink()
 with zipfile.ZipFile(R/'plates'/info['file']) as src,zipfile.ZipFile(inp,'w',zipfile.ZIP_DEFLATED) as dest:
  for it in src.infolist():
   dat=src.read(it.filename)
   if it.filename=='Metadata/project_settings.config':
    cfg=json.loads(dat);cfg['post_process']=[];dat=json.dumps(cfg,indent=2).encode()
   dest.writestr(it.filename,dat)
 cmd=['flatpak','run','--filesystem=/home/buralien','com.orcaslicer.OrcaSlicer','--slice','1','--orient','0','--arrange','0','--outputdir',str(out),str(inp)]
 t=time.time();p=subprocess.run(cmd,capture_output=True,text=True,timeout=1500,cwd=out)
 (out/'slicer.log').write_text(p.stdout+'\n'+p.stderr)
 g=list(out.glob('*.gcode'));res={'exit_code':p.returncode,'seconds_to_slice':round(time.time()-t,1),'gcode':str(g[0].relative_to(R)) if g else None}
 if g:
  guard=subprocess.run(['python3','/home/buralien/bin/check-ender3-start.py',str(g[0])],capture_output=True,text=True);res['original_start_guard_passed']=guard.returncode==0;res['guard_output']=guard.stdout.strip()
  data=g[0].read_text(errors='replace');lines=data.splitlines()
  res['header']=[l for l in lines if l.startswith(';') and any(k in l for k in ['estimated printing time','total filament','filament used [g]','total layers count'])]
  x=y=z=pe=0.;rel=True;role='';objectname='';bbox=[1e9,1e9,-1e9,-1e9];types={};segs=[];heights=[];lastz=None
  for l in lines:
   if l.startswith(';TYPE:'):role=l[6:].strip()
   if l.startswith(';Z:'):heights.append(float(l.split(':')[1]))
   if l.startswith('M82'):rel=False
   if l.startswith('M83'):rel=True
   if l.startswith('G92'):
    m=re.search(r' E([-\d.]+)',l)
    if m:pe=float(m[1])
   if not re.match(r'^G[01]\s',l):continue
   v={a:float(b) for a,b in re.findall(r'([XYZE])([-\d.]+)',l.split(';')[0])}
   nx=v.get('X',x);ny=v.get('Y',y);nz=v.get('Z',z);e=v.get('E',0 if rel else pe);de=e if rel else e-pe
   if 'E' in v:pe=e
   if de>0 and (nx!=x or ny!=y):
    bbox=[min(bbox[0],x,nx),min(bbox[1],y,ny),max(bbox[2],x,nx),max(bbox[3],y,ny)]
    dist=math.hypot(nx-x,ny-y);types[role]=types.get(role,0)+dist
    if role:segs.append([x,y,nx,ny,nz,role])
   x,y,z=nx,ny,nz
  res.update(extrusion_bounds_xy_mm=bbox,extrusions_fit_220_with_0_5mm_margin=min(bbox[:2])>=.5 and max(bbox[2:])<=219.5,path_length_by_role_mm={k:round(v,1) for k,v in types.items()},layer_heights_mm=heights,max_model_z_mm=max(s[4] for s in segs),toolpath_segments=len(segs))
  (out/'segments.json').write_text(json.dumps(segs,separators=(',',':')))
 (out/'check.json').write_text(json.dumps(res,indent=2));return key,res
# First resolve overnight prints, then short material plates. Two independent slicer processes.
keys=sys.argv[1:] or (['07','08']+[k for k in summary['plates'] if k not in ['07','08']])
res={}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:
 for f in concurrent.futures.as_completed([e.submit(one,k) for k in keys]):
  k,v=f.result();res[k]=v;(R/'slice-summary.json').write_text(json.dumps(res,indent=2));print(k,json.dumps({x:v.get(x) for x in ['exit_code','header','extrusion_bounds_xy_mm','extrusions_fit_220_with_0_5mm_margin']}),flush=True)


