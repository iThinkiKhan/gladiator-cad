import json,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
D=Path(__file__).resolve().parent
data=json.loads((D/'preview_meshes.json').read_text());r=json.loads((D/'validation.json').read_text())
fig=plt.figure(figsize=(16,9),facecolor='#f5f6f8');gs=fig.add_gridspec(2,3,height_ratios=[3,1])
def draw(ax,shapes,view=(1,0,0),only=None):
 view=np.array(view,float);view/=np.linalg.norm(view);right=np.cross(view,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,view)
 P=[];C=[];D=[]
 for n,pts in shapes.items():
  if only and n not in only:continue
  t=np.array(pts);normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-12)
  shade=.48+.52*np.abs(normal@np.array([.5,-.4,.7]))
  rgb=np.array([.72,.74,.77])
  if n=='GH44_Tilt_Receiver':rgb=np.array([.95,.57,.2])
  elif n.startswith('Tensioner_'):rgb=np.array([.24,.45,.72])
  elif n.startswith('SG90_'):rgb=np.array([.37,.50,.67])
  elif n=='Pan_Belt_Reference':rgb=np.array([.14,.16,.19])
  P.append(np.stack([t@right,t@up],axis=-1));D.append((t@view).mean(axis=1));C.append(rgb[None,:]*shade[:,None])
 P=np.concatenate(P);C=np.concatenate(C);depth=np.concatenate(D);idx=np.argsort(-depth)
 ax.add_collection(PolyCollection(P[idx],facecolors=C[idx],edgecolors='none'));ax.set_aspect('equal');ax.autoscale();ax.set_facecolor('#f5f6f8')
for i,(tag,title) in enumerate([('before','Previous v2'),('after','Revised v2')]):
 ax=fig.add_subplot(gs[0,i]);draw(ax,data[tag]);ax.set_xlim(-154,-44);ax.set_ylim(140,291);ax.axis('off');ax.set_title(title,fontsize=15,pad=14)
 b=r['balance']['before' if tag=='before' else 'after'];ty=113-b['tilting_com_ahead_of_pivot_mm']
 ax.plot([-113],[247.5],'o',color='#225f91',ms=6);ax.plot([-ty],[247.5],'o',color='#ad4738',ms=6)
 ax.annotate('',(-113,281),(-ty,281),arrowprops={'arrowstyle':'<->','color':'#444'})
 ax.text((-113-ty)/2,284,str(round(b['tilting_com_ahead_of_pivot_mm'],1))+' mm',ha='center',fontsize=11)
 ax.text(.5,-.035,'Blue: tilt axis   Red: estimated payload COM',transform=ax.transAxes,ha='center',fontsize=8)
ax=fig.add_subplot(gs[0,2]);draw(ax,data['after'],view=(.8,.7,-.4),only={'GH44_Tilt_Receiver','SG90_Tilt_Reference','Tilt_Yoke','Tilt_Horn_Reference','Tilt_Pivot_Bolt'});ax.axis('off');ax.set_title('Revised receiver (orange)\nexisting yoke and servo retained',fontsize=13,pad=14)
ax=fig.add_subplot(gs[1,:]);ax.axis('off')
b=r['balance']['before'];a=r['balance']['after']
text=('2.5 mm rearward payload shift  |  '+str(round(r['balance']['holding_moment_reduction_percent'],1))+'% lower estimated level holding moment\n'
      +format(b['level_holding_kgcm'],'.3f')+' -> '+format(a['level_holding_kgcm'],'.3f')+' kg cm  |  checked travel: 38 deg up / 34 deg down\n'
      +'M3x20 tensioner: reaches the full 38-48 mm carriage range; 2.5 mm head-to-lug gap at maximum extension')
ax.text(.5,.65,text,ha='center',va='center',fontsize=13,linespacing=1.8)
ax.text(.5,.02,'CAD estimates and sampled checks. Harness fit, strength and print results remain untested.',ha='center',fontsize=10,color='#555')
fig.suptitle('Masthead v2: tilt balance and tensioner revision',fontsize=21,y=.98)
fig.subplots_adjust(top=.88,bottom=.045,left=.03,right=.98,wspace=.12,hspace=.12)
fig.savefig(D/'balance_tensioner_review.png',dpi=140)
print('Rendered balance review')
