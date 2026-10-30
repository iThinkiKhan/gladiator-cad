import json, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
d=json.load(open("/tmp/padview.json"))
fig,axs=plt.subplots(1,2,figsize=(16,9))
cols={"neck":"#e8913a","SG90":"#3b6fb6","Pan_Servo":"#999999"}
for ax,(proj,lab) in zip(axs,(((0,1),"TOP view (servo slides along -Y)"),((1,2),"SIDE view (Y vs Z)"))):
    for k,tris in d.items():
        t=np.array(tris)[:,:,list(proj)]
        c=cols["neck"] if k=="neck" else (cols["SG90"] if k.startswith("SG90") else cols["Pan_Servo"])
        a=0.35 if k=="neck" else 0.25
        ls="-" if k.endswith("38") or k=="neck" else "--"
        ax.add_collection(PolyCollection(t,facecolors=c,edgecolors="none",alpha=a))
    ax.autoscale(); ax.set_aspect("equal"); ax.grid(alpha=.3); ax.set_title(lab)
axs[0].set_xlim(-30,30); axs[0].set_ylim(-105,20)
axs[1].set_xlim(-105,20)
fig.suptitle("Neck (orange) with the pan servo (blue) and carriage (grey) drawn at BOTH ends of travel, C 38 and C 48")
fig.savefig("/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/preview/neck_pad_travel.png",dpi=90); print("png")
