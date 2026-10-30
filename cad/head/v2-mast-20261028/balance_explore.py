import sys,json,time
from pathlib import Path
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A,Part
V=A.Vector
D=Path('/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028')
O=D/'balance-tensioner-20261030';O.mkdir(exist_ok=True)
d=A.openDocument(str(D/'Gladiator_Head_v2_Mast.FCStd'))
r=json.loads((D/'validation.json').read_text())['v2']
S={o.Name:o.Shape.copy() for o in d.Objects if o.TypeId=='Part::Feature'}
T=V(*r['tilt_axis_world'])
base=S['GH44_Tilt_Receiver']
plane=T.y-15
fore=base.common(Part.makeBox(200,200,200,V(T.x-100,plane-200,T.z-100)))
aft=base.common(Part.makeBox(200,200,200,V(T.x-100,plane,T.z-100)))
payload=[n for n in r['groups']['tilt'] if n not in ('GH44_Tilt_Receiver','Tilt_Horn_Reference')]
obstacles=r['groups']['pan']+r['groups']['fixed']
def overlap(a,b):
    return a.common(b).Volume if a.BoundBox.intersect(b.BoundBox) else 0
out=[]
for shift in (2,4,6,8,10,12):
    f=fore.copy();f.translate(V(0,shift,0));rec=aft.fuse(f).removeSplitter()
    shapes={n:S[n].copy() for n in r['groups']['tilt']}
    shapes['GH44_Tilt_Receiver']=rec
    for n in payload: shapes[n].translate(V(0,shift,0))
    hits={}
    for tilt in (0,-38,34):
        hs=[]
        for n,s in shapes.items():
            p=s.copy();p.rotate(T,V(1,0,0),tilt)
            for b in obstacles:
                vol=overlap(p,S[b])
                if vol>.05: hs.append([n,b,round(vol,2)])
        hits[str(tilt)]=hs
    out.append({'shift':shift,'valid':rec.isValid(),'solids':len(rec.Solids),'hits':hits})
    print(json.dumps(out[-1]),flush=True)
(O/'exploration.json').write_text(json.dumps(out,indent=2))
A.closeDocument(d.Name)
