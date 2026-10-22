"""Insert verified, state-restoring SD/LCD colour stops. Manual purge is required.
Run: python3 postprocess_sd_colours.py --plate 05|07|08 input.gcode [--output output.gcode]
Standalone for Orca GUI post_process: filename is appended by Orca. No printer calls.
"""
from pathlib import Path
import re,json,argparse,hashlib
TARGETS={'05':[(1.5,'RED')],'07':[(12,'GREY'),(55.9,'RED'),(61.9,'GREY')],'08':[(12,'GREY'),(52,'RED'),(58,'GREY')]}
MODEL_ROLES={'Inner wall','Outer wall','Overhang wall','Internal solid infill','Top surface','Bottom surface','Sparse infill','Bridge','Internal Bridge','Gap infill','Ironing','Thin wall'}
def make(data,key):
 if ';R5_SD_COLOUR_BEGIN' in data:raise ValueError('Colour pauses already present; refusing duplicate insertion')
 starts=list(re.finditer(r'^;LAYER_CHANGE\s*\n;Z:([\d.]+)',data,re.M))
 if not starts:raise ValueError('No Orca layer markers')
 head=data[:starts[0].start()];blocks=[]
 for i,m in enumerate(starts):
  text=data[m.start():starts[i+1].start() if i+1<len(starts) else len(data)]
  roles=set(re.findall(r'^;TYPE:(.+)$',text,re.M));blocks.append((float(m[1]),text,bool(roles&MODEL_ROLES)))
 models=[];previous=0.
 for i,(z,t,hasmodel) in enumerate(blocks):
  if hasmodel:models.append((i,previous,z));previous=z
 choice={}
 for target,colour in TARGETS[key]:
  idx,bottom,z=min(models,key=lambda a:abs(a[1]-target))
  if abs(bottom-target)>.15:raise ValueError('Colour boundary exceeds .15mm allowance')
  choice[idx]={'target_boundary_mm':target,'actual_model_boundary_mm':bottom,'before_model_layer_z_mm':z,'load_colour':colour}
 state={'x':0.,'y':0.,'z':0.,'e':0.,'f':1800.,'relative_e':False,'absolute_xyz':True,'retracted':0.,'nozzle':200.,'bed':60.,'remaining_minutes':None}
 def read(t):
  for line in t.splitlines():
   c=line.split(';')[0].strip()
   if not c:continue
   cmd=c.split()[0];v={a:float(b) for a,b in re.findall(r'\b([XYZEFSTR])([-+]?\d*\.?\d+)',c)}
   if cmd=='G90':state['absolute_xyz']=True;state['relative_e']=False
   elif cmd=='G91':state['absolute_xyz']=False;state['relative_e']=False
   elif cmd=='M83':state['relative_e']=True
   elif cmd=='M82':state['relative_e']=False
   elif cmd=='G92':
    for a in ['X','Y','Z','E']:
     if a in v:state[a.lower()]=v[a]
   elif cmd in ['M104','M109'] and 'S' in v:state['nozzle']=v['S']
   elif cmd in ['M140','M190'] and 'S' in v:state['bed']=v['S']
   elif cmd=='M73' and 'R' in v:state['remaining_minutes']=v['R']
   elif cmd in ['G0','G1']:
    for a in ['X','Y','Z']:
     if a in v:state[a.lower()]=v[a] if state['absolute_xyz'] else state[a.lower()]+v[a]
    if 'F' in v:state['f']=v['F']
    if 'E' in v:
     de=v['E'] if state['relative_e'] else v['E']-state['e'];state['e']+=de;state['retracted']=max(0.,state['retracted']-de)
 def pause(entry):
  assert state['relative_e'] and state['absolute_xyz'],'Expected original G90/M83 mode'
  z=state['z'];lift=z+5;colour=entry['load_colour'];rr=state['retracted']
  assert 0<=state['x']<=220 and 0<=state['y']<=220 and lift<250
  assert rr<5 and 150<=state['nozzle']<=240 and state['bed']==60
  entry.update(saved_xyz_mm=[state[a] for a in ['x','y','z']],saved_e_mm=state['e'],saved_feed_mm_min=state['f'],original_retraction_mm=rr,remaining_estimated_minutes=state['remaining_minutes'],park_xyz_mm=[10,180,lift],nozzle_c=state['nozzle'])
  # First click announces that the operator is present. Reheat, then wait for actual manual swap.
  # M84 S0 keeps the axes locked during an unattended stop. S120 restores a 2-min runtime idle timeout.
  lines=[f';R5_SD_COLOUR_BEGIN {colour}',
   'M400','G90','M83','M84 S0','G1 E-1 F1800',f'G1 Z{lift:.5f} F180','G1 X10 Y180 F3000','M400','M300 S880 P300',f'M117 Click for {colour}',f'M0 Click to change {colour}',
   f'M190 S{state["bed"]:g}',f'M109 S{state["nozzle"]:g}',f'M117 Load {colour} purge wipe',f'M0 Load {colour} purge wipe',f'M109 S{state["nozzle"]:g}',
   'G90','M83',f'G1 E-{rr+1:.5f} F1800',f'G1 X{state["x"]:.5f} Y{state["y"]:.5f} F3000',f'G1 Z{z:.5f} F180','G1 E1 F1800',f'G92 E{state["e"]:.5f}',f'G1 F{state["f"]:g}','M84 S120','M117 Printing',f';R5_SD_COLOUR_END {colour}']
  return '\n'.join(lines)+'\n'
 out=[head];read(head);records=[]
 for i,(z,text,hasmodel) in enumerate(blocks):
  if i in choice:
   entry=choice[i];out.append(pause(entry));records.append(entry)
  out.append(text);read(text)
 result=''.join(out)
 stripped=re.sub(r'^;R5_SD_COLOUR_BEGIN.*?^;R5_SD_COLOUR_END[^\n]*\n','',result,flags=re.M|re.S)
 assert stripped==data,'Original G-code lines changed'
 assert len(records)==len(TARGETS[key]);assert result.count('\nM0 ')==2*len(records)
 return result,{'plate':key,'start_colour':'WHITE' if key=='05' else 'RED','changes':records,'original_bytes_preserved_outside_pause_blocks':True,'source_sha256':hashlib.sha256(data.encode()).hexdigest(),'output_sha256':hashlib.sha256(result.encode()).hexdigest(),'physical_SD_pause_test_required':True,'manual_swap':'Click when present; wait for heat; release extruder idler, swap and hand-purge to pure new colour, wipe nozzle, reengage idler, click. Keep bed/head still. No firmware-managed unloading assumed.','runtime_idle_timeout':'0 while paused;120s after resume; no EEPROM writes.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--plate',choices=TARGETS,required=True);p.add_argument('gcode');p.add_argument('--output');args=p.parse_args()
 inp=Path(args.gcode);out=Path(args.output) if args.output else inp
 result,report=make(inp.read_bytes().decode('utf-8'),args.plate);out.write_bytes(result.encode('utf-8'));out.with_suffix(out.suffix+'.colour-stops.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()

