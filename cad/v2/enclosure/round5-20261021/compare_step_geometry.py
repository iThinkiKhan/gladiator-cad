from pathlib import Path
import FreeCAD as A,Part,json,os,traceback
O=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-20261021');out={}
try:
 d=A.openDocument(str(O/'Gladiator_Round5.FCStd'));r=json.loads((O/'validation.json').read_text())
 step=Part.Shape();step.read(str(O/'Gladiator_Round5_PrintParts.step'));available=list(step.Solids)
 rows=[]
 for n in r['parts']:
  s=d.getObject(n).Shape.Solids[0]
  if n.startswith('Tablet_'):s=s.fuse(d.getObject('Letters_'+n[-1]).Shape).removeSplitter().Solids[0]
  idx=min(range(len(available)),key=lambda i:(s.CenterOfMass-available[i].CenterOfMass).Length)
  q=available.pop(idx);bs,bq=s.BoundBox,q.BoundBox
  err=max(abs(a-b) for a,b in zip([bs.XMin,bs.XMax,bs.YMin,bs.YMax,bs.ZMin,bs.ZMax],[bq.XMin,bq.XMax,bq.YMin,bq.YMax,bq.ZMin,bq.ZMax]))
  rows.append(dict(name=n,native_volume=s.Volume,step_volume=q.Volume,difference=q.Volume-s.Volume,relative_error=abs(q.Volume-s.Volume)/s.Volume,centre_error_mm=(s.CenterOfMass-q.CenterOfMass).Length,bbox_error_mm=err))
 out['parts']=rows;out['total_native']=sum(x['native_volume'] for x in rows);out['total_step']=step.Volume
 (O/'step-geometry-comparison.json').write_text(json.dumps(out,indent=2))
except BaseException:out['error']=traceback.format_exc();(O/'step-geometry-comparison.json').write_text(json.dumps(out,indent=2))
os._exit(0)

