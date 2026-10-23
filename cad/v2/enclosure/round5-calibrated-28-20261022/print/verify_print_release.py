from pathlib import Path
import json,re,math,zipfile,hashlib,sys
import numpy as np
import postprocess_sd_colours as SD
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
R=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-calibrated-28-20261022/print');B=json.loads((R/'build-summary.json').read_text());S={k:json.loads((R/'slice-check'/k/'check.json').read_text()) for k in B['plates']};(R/'slice-summary.json').write_text(json.dumps(S,indent=2));N=json.loads((R/'native-mount-envelopes.json').read_text())
rep={'source_hashes_unchanged':True,'all_22_source_parts_covered':False,'all_slicer_guards_passed':all(x.get('original_start_guard_passed') for x in S.values()),'all_extrusions_fit_220':all(x.get('extrusions_fit_220_with_0_5mm_margin') for x in S.values()),'slicer_errors':{},'support_inside_new_insert_bores':{},'plate_times':{},'colour_change_plan':{}}
root=Path('/home/buralien/projects/gladiator-cad')
for p,h in B['source_hashes'].items():
 if hashlib.sha256((root/p).read_bytes()).hexdigest()!=h:rep['source_hashes_unchanged']=False
expected=set(p.name for p in (root/'cad/v2/enclosure/round5-calibrated-28-20261022/style/stl').glob('*.stl'))
covered={p['name']+'.stl' for info in B['plates'].values() for p in info['parts'] if p['name']+'.stl' in expected}
rep['all_22_source_parts_covered']=covered==expected;rep['source_part_count']=len(covered)
def secs(s):
 x=re.search(r'= (.*)',s)[1];return sum(int(n)*{'h':3600,'m':60,'s':1}[u] for n,u in re.findall(r'(\d+)([hms])',x))
for k,v in S.items():
 h=next(l for l in v['header'] if 'estimated printing time' in l);w=next(l for l in v['header'] if l.startswith('; filament used [g]'))
 rep['plate_times'][k]={'seconds':secs(h),'grams':float(w.split('=')[1])}
 log=(R/'slice-check'/k/'slicer.log').read_text();rep['slicer_errors'][k]=[l for l in log.splitlines() if re.search(r'error|warning|potentially lost|floating',l,re.I)]
rep['all_plates_seconds']=sum(x['seconds'] for x in rep['plate_times'].values())
rep['shells_seconds']=sum(rep['plate_times'][k]['seconds'] for k in ['07','08'])
# Check the actual support toolpaths in all thirteen newly added insert cavities.
bores={'Rear_Hood':[(f'Tablet_{side}_{y}',(x,y,70),0,1.4,4) for side,x in [('L',-11.8),('R',90.8)] for y in [-6,48]]+[('Aquila',(26,-34.8,68.5),1,1.4,4)],'Front_Left':[('Scutum_L',(16,150.8,79),1,1.4,4)],'Front_Right':[('Scutum_R',(63,150.8,79),1,1.4,4)],'Crest_Clamp':[('Crest_side',(39.5,157.8,237.8),1,1.4,4),('Crest_top',(39.5,163,242.15),2,1.4,3.9)],'Neck_Clamp_0':[('Neck0_side',(21.5,103.8,236.7),1,1.4,4),('Neck0_top',(21.5,110,241.2),2,1.4,4)],'Neck_Clamp_1':[('Neck1_side',(57.5,103.8,236.7),1,1.4,4),('Neck1_top',(57.5,110,241.2),2,1.4,4)]}
for key in ['02','07','08']:
 seg=json.loads((R/'slice-check'/key/'segments.json').read_text());a=np.array([s[:5] for s in seg if s[5].startswith('Support')])
 if a.size==0:
  for p in B['plates'][key]['parts']:
   for nm,cen,axis,rad,depth in bores.get(p['name'],[]):
    rep['support_inside_new_insert_bores'][nm]={'centreline_samples_inside':0,'checked_samples':0,'note':'No support extrusion anywhere on this plate; clamps print on broad sides.'}
  continue
 pts=np.vstack([a[:,[0,1,4]],a[:,[2,3,4]],np.column_stack([(a[:,0]+a[:,2])/2,(a[:,1]+a[:,3])/2,a[:,4]])])
 for p in B['plates'][key]['parts']:
  name=p['name']
  if name not in bores:continue
  b=N[name]['bounds'];c=p['at_mm'];mid=np.array([(b[0]+b[3])/2,(b[1]+b[4])/2]);world=pts.copy()
  world[:,0]=pts[:,0]-c[0]+mid[0]
  if key in ['07','08']:world[:,1]=mid[1]-(pts[:,1]-c[1]);world[:,2]=b[5]-pts[:,2]
  else:world[:,1]=pts[:,1]-c[1]+mid[1];world[:,2]=pts[:,2]+b[2]
  for nm,cen,axis,rad,depth in bores[name]:
   delta=world-np.array(cen);mask=(np.abs(delta[:,axis])<depth/2-.15)&(np.sum(np.delete(delta,axis,axis=1)**2,axis=1)<(rad-.15)**2)
   # Transform actual segment endpoints, then clip to the finite bore axis interval.
   p0=world[:len(a)];p1=world[len(a):2*len(a)];delta0=p0-np.array(cen);direction=p1-p0
   axial0=delta0[:,axis];ad=direction[:,axis];half=depth/2+.20
   lower=np.zeros(len(a));upper=np.ones(len(a));moving=np.abs(ad)>1e-10
   ta=np.zeros(len(a));tb=np.zeros(len(a));ta[moving]=(-half-axial0[moving])/ad[moving];tb[moving]=(half-axial0[moving])/ad[moving]
   lower[moving]=np.maximum(0,np.minimum(ta[moving],tb[moving]));upper[moving]=np.minimum(1,np.maximum(ta[moving],tb[moving]))
   ok=(lower<=upper)&(moving|(np.abs(axial0)<=half))
   radial0=np.delete(delta0,axis,axis=1);rd=np.delete(direction,axis,axis=1);den=np.sum(rd*rd,axis=1)
   t=np.zeros(len(a));nz=den>1e-15;t[nz]=-np.sum(radial0[nz]*rd[nz],axis=1)/den[nz];t=np.maximum(lower,np.minimum(upper,t))
   dist2=np.sum((radial0+t[:,None]*rd)**2,axis=1);hits=ok&(dist2<(rad+.20)**2)
   rep['support_inside_new_insert_bores'][nm]={'centreline_samples_inside':int(mask.sum()),'checked_samples':len(world),'radius_mm':rad,'axis':axis,'segments_intersecting_bore_with_0_20mm_bead_allowance':int(hits.sum()),'checked_segments':len(a)}
# A single-colour shell may be painted later. Exact layer stop plan for the multicolour variant.
for k in SD.TARGETS:
 _,colour_report=SD.make((R/'slice-check'/k/'plate_1.gcode').read_bytes().decode('utf-8'),k)
 rep['colour_change_plan'][k]=colour_report
if '--no-render' in sys.argv:
 (R/'print-verification.json').write_text(json.dumps(rep,indent=2))
 print(json.dumps(rep['support_inside_new_insert_bores'],indent=2));sys.exit(0)
# Toolpath top + side views, supports grey and model coloured by print height.
O=R/'previews';O.mkdir(exist_ok=True)
for k in ['01','02','03','04','05','06','07','08','09']:
 seg=json.loads((R/'slice-check'/k/'segments.json').read_text());seg=[s for s in seg if s[5] not in ['Custom','Brim','Skirt']]
 fig,axes=plt.subplots(1,2,figsize=(13,5));model=[s for s in seg if not s[5].startswith('Support')];support=[s for s in seg if s[5].startswith('Support')]
 for ax,side in zip(axes,[False,True]):
  for arr,color in [(support,'#999999'),(model,'#176A8A')]:
   stride=max(1,len(arr)//90000);ss=arr[::stride]
   lines=[[(s[0],s[4] if side else s[1]),(s[2],s[4] if side else s[3])] for s in ss]
   ax.add_collection(LineCollection(lines,colors=color,linewidths=.3,alpha=.65))
  ax.autoscale();ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('X (mm)');ax.set_ylabel('Z (mm)' if side else 'Y (mm)');ax.set_title('Side: supports grey' if side else 'Top: model blue')
 fig.suptitle(B['plates'][k]['file']+' | '+next(l.split('= ')[1] for l in S[k]['header'] if 'estimated printing time' in l));fig.tight_layout();fig.savefig(O/(k+'-toolpaths.png'),dpi=130);plt.close(fig)
(R/'print-verification.json').write_text(json.dumps(rep,indent=2))
print(json.dumps({k:v for k,v in rep.items() if k not in ['colour_change_plan','plate_times']},indent=2));print('colour changes',json.dumps(rep['colour_change_plan'],indent=2))





