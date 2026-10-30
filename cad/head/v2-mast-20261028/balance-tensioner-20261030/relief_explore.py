exec(open('/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/balance_explore.py').read().split('out=[]')[0])
for shift in (2,2.5,3,3.5):
 f=fore.copy();f.translate(V(0,shift,0));rec=aft.fuse(f).removeSplitter()
 car=S['GH44_Dual_Carrier'].copy();car.translate(V(0,shift,0))
 cs=[]
 for t in (-38,34):
  q=car.copy();q.rotate(T,V(1,0,0),t)
  cs.append((t,round(overlap(q,S['Tilt_Yoke']),5),round(q.distToShape(S['Tilt_Yoke'])[0],4)))
 print('shift',shift,'carrier/yoke',cs,flush=True)
# Build conservative clearance pockets in only the receiver, using inverse posed enlarged obstacles.
shift=3.0
f=fore.copy();f.translate(V(0,shift,0));rec=aft.fuse(f).removeSplitter()
original=rec.copy()
removed=[]
obs={}
for n in ('Tilt_Yoke','SG90_Tilt_Reference'):
 try: obs[n]=S[n].makeOffsetShape(.4,.01,fill=False,join=0)
 except: obs[n]=S[n]
for t in range(-38,35,2):
 for n,b in obs.items():
  p=b.copy();p.rotate(T,V(1,0,0),-t)
  if rec.BoundBox.intersect(p.BoundBox) and overlap(rec,p)>.001:
   rec=rec.cut(p).removeSplitter()
 print('pocket',t,flush=True)
print('rec valid',rec.isValid(),'solids',len(rec.Solids),'removed',original.Volume-rec.Volume,flush=True)
obj=d.addObject('Part::Feature','Receiver_Balance_3mm');obj.Shape=rec
d.recompute();Part.export([obj],str(O/'receiver_trial.step'))
# Check whether the original through-register bearing profile was touched at its front 1 mm.
keyfront=Part.makeBox(28,1,24,V(T.x-14,T.y-26+shift,T.z-12))
removed=original.cut(rec)
print('removed near register front',removed.common(keyfront).Volume,flush=True)
A.closeDocument(d.Name)
