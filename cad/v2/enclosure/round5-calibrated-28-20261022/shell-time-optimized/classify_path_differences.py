from pathlib import Path
import FreeCAD as A,json,traceback,os
N=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-calibrated-28-20261022');O=N/'shell-time-optimized'
try:
 d=A.openDocument(str(N/'print/Gladiator_Round5_Print.FCStd'));B=json.loads((O/'build-summary.json').read_text());bounds=json.loads((N/'print/native-mount-envelopes.json').read_text());diff=json.loads((O/'path-differences.json').read_text());report={}
 for k,delta in diff.items():
  report[k]={}
  for kind in ['missing','added']:
   output=[]
   for row in delta[kind]:
    x,y,nx,ny,z,role=row
    obj=min(B['plates'][k]['parts'],key=lambda p:abs((x+nx)/2-p['at_mm'][0]));name=obj['name'];bb=bounds[name]['bounds'];cx,cy=obj['at_mm'];mx=(bb[0]+bb[3])/2;my=(bb[1]+bb[4])/2
    hits=0
    for t in [.1,.3,.5,.7,.9]:
     px=x+(nx-x)*t;py=y+(ny-y)*t
     point=A.Vector(px-cx+mx,my-(py-cy),bb[5]-(z-.14))
     hits+=bool(d.getObject(name).Shape.isInside(point,1e-5,True))
    output.append({'segment':row,'part':name,'inside_native_solid_samples':hits,'sample_count':5})
   report[k][kind]=output
 (O/'path-difference-native-classification.json').write_text(json.dumps(report,indent=2))
except BaseException:(O/'CLASSIFY_ERROR.txt').write_text(traceback.format_exc())
os._exit(0)
