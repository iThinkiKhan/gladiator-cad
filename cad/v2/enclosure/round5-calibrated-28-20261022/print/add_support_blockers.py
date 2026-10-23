from pathlib import Path
import zipfile,json,xml.etree.ElementTree as E
import numpy as np
R=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-calibrated-28-20261022/print');B=json.loads((R/'build-summary.json').read_text());N=json.loads((R/'native-mount-envelopes.json').read_text())
C='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';P='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
E.register_namespace('',C);E.register_namespace('p',P);E.register_namespace('BambuStudio','http://schemas.bambulab.com/package/2021')
def q(s):return '{'+C+'}'+s
bores={'Rear_Hood':[(f'Tablet_{side}_{y}',(x,y,70),0,4) for side,x in [('L',-11.8),('R',90.8)] for y in [-6,48]]+[('Aquila',(26,-34.8,68.5),1,4)],'Front_Left':[('Scutum_L',(16,150.8,79),1,4)],'Front_Right':[('Scutum_R',(63,150.8,79),1,4)],'Crest_Clamp':[('Crest_side',(39.5,157.8,237.8),1,4),('Crest_top',(39.5,163,242.15),2,3.9)],'Neck_Clamp_0':[('Neck0_side',(21.5,103.8,236.7),1,4),('Neck0_top',(21.5,110,241.2),2,4)],'Neck_Clamp_1':[('Neck1_side',(57.5,103.8,236.7),1,4),('Neck1_top',(57.5,110,241.2),2,4)]}
bores['FIT_Scutum_Seat']=bores['Front_Left'];bores['FIT_Tablet_End']=[b for b in bores['Rear_Hood'] if b[0]=='Tablet_R_-6'];bores['FIT_Aquila_Seat']=[bores['Rear_Hood'][-1]]
shoe={'Crest_Clamp':[(37.0,159.65,236.05,42.0,161.3,239.6)],'Neck_Clamp_0':[(18.6,105.4,234.8,24.4,107.2,238.6)],'Neck_Clamp_1':[(54.6,105.4,234.8,60.4,107.2,238.6)]}
FACES=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
report={}
for key in ['01','07','08']:
 path=R/'plates'/B['plates'][key]['file']
 with zipfile.ZipFile(path) as z:files={f:z.read(f) for f in z.namelist()}
 model=E.fromstring(files['3D/3dmodel.model']);ms=E.fromstring(files['Metadata/model_settings.config']);newid=10000;added=[]
 for entry in B['plates'][key]['parts']:
  name=entry['name']
  if name not in bores:continue
  # Rebuild blockers idempotently: no duplicate modifiers on a second execution.
  objms=next(o for o in ms.findall('object') if any(m.get('key')=='name' and m.get('value')==name for m in o.findall('metadata')))
  pobj=model.find(q('resources')).find(q('object')+f"[@id='{objms.get('id')}']");comps=pobj.find(q('components'))
  for c in list(comps)[1:]:comps.remove(c)
  for pp in list(objms.findall('part'))[1:]:objms.remove(pp)
  normalid=list(comps)[0].get('objectid');objms.find('part').set('id',normalid)
  fn='3D/Objects/'+name+'.model';meshfile=E.fromstring(files[fn]);resources=meshfile.find(q('resources'))
  for oo in list(resources):
   if oo.get('id')!=normalid:resources.remove(oo)
  bounds=N[name]['bounds'];low=np.array(bounds[:3]);high=np.array(bounds[3:]);mid=(low+high)/2
  boxes=[]
  for label,centre,axis,depth in bores[name]:
   size=np.array([4.5]*3);size[axis]=depth+5.0;c=np.array(centre);lo=c-size/2;hi=c+size/2
   # Do not let nonprinting modifiers lift a part off the bed or cover an unrelated region.
   lo=np.maximum(lo,low-np.array([.4,.4,0]));hi=np.minimum(hi,high+np.array([.4,.4,0]))
   if np.any(hi<=lo):continue
   lo[2]=low[2];hi[2]=high[2]
   boxes.append((label+'_no_support',lo,hi))
  for j,bb in enumerate(shoe.get(name,[])):
   lo=np.maximum(bb[:3],low);hi=np.minimum(bb[3:],high);lo[2]=low[2];hi[2]=high[2]
   boxes.append(('Shoe_pocket_no_support',lo,hi))
  for label,lo,hi in boxes:
   pts=np.array([[lo[0],lo[1],lo[2]],[hi[0],lo[1],lo[2]],[hi[0],hi[1],lo[2]],[lo[0],hi[1],lo[2]],[lo[0],lo[1],hi[2]],[hi[0],lo[1],hi[2]],[hi[0],hi[1],hi[2]],[lo[0],hi[1],hi[2]]])
   pts[:,0]-=mid[0]
   if key in ['01','07','08']:pts[:,1]=mid[1]-pts[:,1];pts[:,2]=high[2]-pts[:,2]
   else:pts[:,1]-=mid[1];pts[:,2]-=low[2]
   newid+=1;oo=E.SubElement(resources,q('object'),{'id':str(newid),'type':'model'});m=E.SubElement(oo,q('mesh'));vv=E.SubElement(m,q('vertices'));tt=E.SubElement(m,q('triangles'))
   for p in pts:E.SubElement(vv,q('vertex'),{a:f'{v:.6f}' for a,v in zip(['x','y','z'],p)})
   # Inversion of two axes for the shell preserves orientation.
   for f in FACES:E.SubElement(tt,q('triangle'),{a:str(v) for a,v in zip(['v1','v2','v3'],f)})
   E.SubElement(comps,q('component'),{'{'+P+'}path':'/'+fn,'objectid':str(newid),'transform':'1 0 0 0 1 0 0 0 1 0 0 0'})
   part=E.SubElement(objms,'part',{'id':str(newid),'subtype':'support_blocker'});E.SubElement(part,'metadata',{'key':'name','value':label});E.SubElement(part,'metadata',{'key':'matrix','value':'1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'});E.SubElement(part,'mesh_stat',{'face_count':'12','edges_fixed':'0','degenerate_facets':'0','facets_removed':'0','facets_reversed':'0','backwards_edges':'0'})
   added.append({'part':name,'label':label,'native_box_min':list(lo),'native_box_max':list(hi)})
  files[fn]=E.tostring(meshfile,encoding='utf-8',xml_declaration=True)
 files['3D/3dmodel.model']=E.tostring(model,encoding='utf-8',xml_declaration=True);files['Metadata/model_settings.config']=E.tostring(ms,encoding='utf-8',xml_declaration=True)
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for n,data in files.items():z.writestr(n,data)
 report[key]=added
(R/'support-blockers.json').write_text(json.dumps(report,indent=2));print({k:len(v) for k,v in report.items()})


