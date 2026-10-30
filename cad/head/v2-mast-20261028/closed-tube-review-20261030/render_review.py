import json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Circle,Rectangle
D=Path('/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/closed-tube-review-20261030')
data=json.loads((D/'preview_meshes.json').read_text())
fig=plt.figure(figsize=(15,8),facecolor='#f4f5f7')
gs=fig.add_gridspec(1,4,width_ratios=[1,1,1,1.5])
colors={'Slotted':'#a7aeb9','Closed':'#e99a3e','Protected':'#e99a3e','Cutaway':'#e99a3e'}
def draw(ax,name,view):
    tri=np.array(data[name]);view=np.array(view,float);view/=np.linalg.norm(view)
    right=np.cross(view,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,view)
    xy=np.stack([tri@right,tri@up],axis=-1)
    dep=(tri@view).mean(axis=1)
    n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-10)
    light=np.array([-.5,-.5,.7]);shade=.5+.5*np.abs(n@light)
    import matplotlib.colors as mc
    rgb=np.array(mc.to_rgb(colors[name]));cs=rgb[None,:]*shade[:,None]
    order=np.argsort(-dep)
    ax.add_collection(PolyCollection(xy[order],facecolors=cs[order],edgecolors='none'))
    ax.set_aspect('equal');ax.autoscale();ax.axis('off');ax.set_facecolor('#f4f5f7')
for i,(name,title) in enumerate([('Slotted','Previous draft\ncontinuous slot'),('Closed','Closed tube\nrounded lower inlet'),('Cutaway','Bolt guard option\ncutaway')]):
    ax=fig.add_subplot(gs[i]);draw(ax,name,(-.8,.6,-.16) if name=='Cutaway' else (.6,-.8,-.16) if name=='Closed' else (.6,.8,-.16));ax.set_title(title,fontsize=12,pad=20)
    if name=='Cutaway':
        ax.annotate('Rounded guard\naround M3 bolt',xy=(0,122),xytext=(-21,96),fontsize=9,arrowprops=dict(arrowstyle='->',color='#444'))
ax=fig.add_subplot(gs[3]);ax.set_facecolor('#f4f5f7')
# Exact mid-bolt section: 20 OD / 12 ID and the guard occupies |Y|<=2.8 in the bore.
a=np.linspace(0,2*np.pi,400)
ax.fill(10*np.cos(a),np.minimum(10*np.sin(a),9.1),color='#e99a3e')
ax.fill(6*np.cos(a),6*np.sin(a),color='#f4f5f7')
x=np.linspace(-6,6,600);y=np.sqrt(36-x*x);band=np.minimum(y,2.8)
ax.fill_between(x,-band,band,color='#e99a3e')
ax.add_patch(Rectangle((-10,-1.5),20,3,facecolor='#617487',edgecolor='none'))
for side in [-1,1]:
    ax.add_patch(Circle((0,side*4.4),1.6,fill=False,edgecolor='#147d79',linewidth=2))
    ax.add_patch(Rectangle((-1.42,side*4.4-1.42),2.84,2.84,fill=False,edgecolor='#52687b',linestyle='--'))
ax.annotate('Two wire passages\n3.2 mm round gauge each',xy=(.4,4.5),xytext=(-15,15),fontsize=10,arrowprops=dict(arrowstyle='->'))
ax.annotate('M3 bolt isolated\nfrom wires',xy=(5,0),xytext=(-15,-17),fontsize=10,arrowprops=dict(arrowstyle='->'))
ax.set_aspect('equal');ax.set_xlim(-18,18);ax.set_ylim(-22,23);ax.axis('off');ax.set_title('At the head bolt\nview down the mast',fontsize=12,pad=20)
fig.suptitle('Mast v2: closed tube with pull-cord wiring',fontsize=19,y=.97)
fig.text(.5,.08,'20 mm OD | 12 mm bore | 144 mm tube length | existing key and bolt positions retained',ha='center',fontsize=12)
fig.text(.5,.035,'CAD proposal only. Guard reduces connector clearance locally. Harness fit and print bridging still need checking.',ha='center',fontsize=10,color='#555')
fig.subplots_adjust(left=.03,right=.98,top=.84,bottom=.16,wspace=.25)
fig.savefig(D/'closed_mast_review.png',dpi=140)
print('Rendered',D/'closed_mast_review.png')
