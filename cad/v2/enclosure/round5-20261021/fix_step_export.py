from pathlib import Path
import FreeCAD as A,Part,json,os,traceback
O=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-20261021')
out={}
try:
 d=A.openDocument(str(O/'Gladiator_Round5.FCStd'));r=json.loads((O/'validation.json').read_text())
 e=A.newDocument('Round5_Manufacturing_Export');objects=[]
 for name in r['parts']:
  s=d.getObject(name).Shape.copy()
  if name.startswith('Tablet_'):
   s=s.fuse(d.getObject('Letters_'+name[-1]).Shape).removeSplitter()
  assert s.isValid() and len(s.Solids)==1,(name,len(s.Solids))
  o=e.addObject('Part::Feature',name);o.Shape=s;objects.append(o)
 Part.export(objects,str(O/'Gladiator_Round5_PrintParts.step'))
 check=Part.Shape();check.read(str(O/'Gladiator_Round5_PrintParts.step'))
 out=dict(valid=check.isValid(),solids=len(check.Solids),expected_solids=len(r['parts']),volume_mm3=check.Volume,expected_volume_mm3=sum(x['volume_mm3'] for x in r['parts'].values()))
 assert out['solids']==out['expected_solids'] ,out
 (O/'step-export-check.json').write_text(json.dumps(out,indent=2))
except BaseException:out['error']=traceback.format_exc();(O/'step-export-check.json').write_text(json.dumps(out,indent=2))
os._exit(0)

