from pathlib import Path
import re,json,math
R=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-print-20261022');P=R/'SD_PACKAGE';res={}
for f in list((P/'PRINT_FIRST').glob('*TABLETS*.gcode'))+list((P/'HOLD_INSERTS').glob('*_SD.gcode.pending')):
 state=dict(x=0.,y=0.,z=0.,e=0.,f=0.,xyz_abs=True,e_rel=False,nozzle=0.,bed=0.);saved=None;records=[];maxz=0.
 for line in f.read_bytes().decode().splitlines():
  if line.startswith(';R5_SD_COLOUR_BEGIN'):saved=state.copy();continue
  if line.startswith(';R5_SD_COLOUR_END'):
   assert saved is not None
   err={k:abs(state[k]-saved[k]) for k in ['x','y','z','e','f','nozzle','bed']};assert max(err.values())<.00002,(f.name,err)
   assert state['xyz_abs']==saved['xyz_abs'] and state['e_rel']==saved['e_rel'];records.append({'state_restored':True,'max_error':max(err.values())});saved=None;continue
  raw=line.split(';')[0].strip()
  if not raw:continue
  cmd=raw.split()[0];v={a:float(b) for a,b in re.findall(r'\b([XYZEFST])([-+]?\d*\.?\d+)',raw)}
  if saved is not None:
   assert cmd not in ['G28','G29','M500','M501','M502','M600','M601','M25']
   if cmd=='M84':assert 'S' in v,'A pause must not release the axes'
  if cmd in ['G90','G91']:state['xyz_abs']=cmd=='G90';state['e_rel']=False
  elif cmd=='M82':state['e_rel']=False
  elif cmd=='M83':state['e_rel']=True
  elif cmd=='G92':
   for k in ['X','Y','Z','E']:
    if k in v:state[k.lower()]=v[k]
  elif cmd in ['G0','G1']:
   for k in ['X','Y','Z']:
    if k in v:state[k.lower()]=v[k] if state['xyz_abs'] else state[k.lower()]+v[k]
   if 'E' in v:state['e']=state['e']+v['E'] if state['e_rel'] else v['E']
   if 'F' in v:state['f']=v['F']
   assert -.01<=state['x']<=220.01 and -.01<=state['y']<=220.01 and -.01<=state['z']<=250.01
   maxz=max(maxz,state['z'])
  elif cmd in ['M104','M109'] and 'S' in v:state['nozzle']=v['S']
  elif cmd in ['M140','M190'] and 'S' in v:state['bed']=v['S']
 assert saved is None and records
 res[f.name]={'all_motion_within_220x220x250':True,'max_z_mm':maxz,'pause_state_checks':records,'physical_LCD_and_manual_purge_not_simulated':True}
assert len(res)==3
(R/'SD-pause-state-verification.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
