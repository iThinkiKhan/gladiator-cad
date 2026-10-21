import FreeCAD as A, Part, os, traceback
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
V=A.Vector
O="/home/buralien/projects/gladiator-cad/cad/v2/enclosure/v2-20261013/"
d=A.openDocument(O+"Gladiator_Enclosure_v2.FCStd")
def col(n):
    if n in("Rear_Hood","Front_Left","Front_Right"): return ("#c0392b",2.2)
    if n=="Lens_Plate": return ("#00bcd4",2.0)
    if n.startswith("Head_"): return ("#8e44ad",0.7)
    if "Fins" in n: return ("#d68910",1.0)
    if "Drv" in n and "Board" in n: return ("#16a085",1.0)
    if n.startswith(("Track","Wheel")): return ("#bbbbbb",0.7)
    return ("#34495e",0.8)
def section(ax,axis,val,title,xl,xlim=None,zlim=None):
    nrm=V(0,1,0) if axis=="Y" else V(1,0,0)
    for o in d.Objects:
        if o.Shape.isNull(): continue
        try: wires=o.Shape.slice(nrm,val)
        except Exception: continue
        c,lw=col(o.Name)
        for w in wires:
            pts=w.discretize(120)
            xs=[p.x if axis=="Y" else p.y for p in pts]; zs=[p.z for p in pts]
            ax.plot(xs,zs,color=c,lw=lw)
    ax.set_aspect("equal");ax.grid(alpha=.3);ax.set_title(title,fontsize=9);ax.set_xlabel(xl)
    if xlim: ax.set_xlim(*xlim)
    if zlim: ax.set_ylim(*zlim)
try:
    fig,axs=plt.subplots(2,2,figsize=(15,13))
    section(axs[0][0],"X",22,"X=22 side view: lens + light-pipe tube (cyan), roof screw boss + tab at Y72, skid at rear, hood in red","Y (mm)",(-55,160),(-5,125))
    section(axs[0][1],"X",68,"X=68 side view: SMA boss + gussets at rear wall, roof tab screw","Y (mm)",(-55,100),(0,125))
    section(axs[1][0],"Y",-40,"Y=-40: INA pod cross-section (rear step)","X (mm)",(0,80),(5,70))
    section(axs[1][1],"Y",95,"Y=95: front panels, boards (green), fins (bronze)","X (mm)",(-60,140),(0,125))
    fig.savefig(O+"sections_v2.png",dpi=70,bbox_inches="tight")
    print("sections ok",flush=True)
except Exception: traceback.print_exc()
os._exit(0)
