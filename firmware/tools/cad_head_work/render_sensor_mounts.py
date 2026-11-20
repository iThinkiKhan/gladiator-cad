"""Render the saved CAD, without using the interactive FreeCAD session."""
import sys,json,hashlib
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad/Mod'])
import FreeCAD as A
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path('/home/buralien/projects/gladiator-cad')
OUT=ROOT/'cad/head/v05-sensor-mounts'
native_path=Path(sys.argv[1] if len(sys.argv)>1 else str(OUT/'Gladiator_Head_v05_PanStack.FCStd'))
doc=A.openDocument(str(native_path))
WORLD=A.Vector(39.5,113,10)
TZ=206.5
colors={'GH44_Dual_Carrier':'#a5b2bf','ToF_Sensor_Frame':'#eaa246','Radar_Sensor_Frame':'#40a891',
        'Dual_ToF_Envelope':'#5979ab','Dual_Radar_Envelope':'#485966','GH44_Tilt_Receiver':'#a8b4bf',
        'Rear_Display_Frame':'#82939f','Tilt_Yoke':'#ccd3d8'}

def tess(name):
    s=doc.getObject(name).Shape.copy();s.translate(-WORLD)
    vertices,triangles=s.tessellate(.08)
    points=np.array([[v.x,v.y,v.z-TZ] for v in vertices])
    return points[np.array(triangles)]

fig=plt.figure(figsize=(14,7),dpi=160)
fig.patch.set_facecolor('#f4f6f8')
ax=fig.add_subplot(121)
layers=[]
for name in ('GH44_Dual_Carrier','ToF_Sensor_Frame','Radar_Sensor_Frame','Dual_ToF_Envelope','Dual_Radar_Envelope'):
    t=tess(name)
    for q in t:
        poly=q[:,[0,2]]
        area=abs(np.linalg.det(np.column_stack([poly[1]-poly[0],poly[2]-poly[0]])))
        if area>1e-9:layers.append((q[:,1].mean(),poly,colors[name]))
layers.sort(key=lambda x:-x[0])
ax.add_collection(PolyCollection([x[1] for x in layers],facecolors=[x[2] for x in layers],edgecolor='none'))
ax.set(xlim=(-46,46),ylim=(-30,30),xlabel='Width from mast axis (mm)',ylabel='Height from tilt axis (mm)',title='Front view — measured PCB bounds')
ax.set_aspect('equal');ax.grid(alpha=.16)
ax.annotate('ToF 42 × 27.5 mm\n4 of 6 holes used',xy=(-15,1),xytext=(-41,25),fontsize=10,
            arrowprops={'arrowstyle':'->','color':'#263746'})
ax.annotate('Radar 22 × 30 mm\nØ3 holes, 15 × 23 pitch',xy=(24,1),xytext=(8,-27),fontsize=10,
            arrowprops={'arrowstyle':'->','color':'#263746'})
ax.plot([-36,6],[18.5,18.5],color='#5979ab',lw=1.3)
ax.plot([-36,-36],[17.5,19.5],color='#5979ab');ax.plot([6,6],[17.5,19.5],color='#5979ab')
ax.text(-15,19.2,'42',ha='center',color='#405a80',fontsize=10)

bx=fig.add_subplot(122,projection='3d')
for name in ('GH44_Tilt_Receiver','GH44_Dual_Carrier','ToF_Sensor_Frame','Radar_Sensor_Frame'):
    triangles=tess(name)
    if name=='ToF_Sensor_Frame':triangles[:, :,1]-=8
    if name=='Radar_Sensor_Frame':triangles[:, :,1]-=8
    bx.add_collection3d(Poly3DCollection(triangles,facecolor=colors[name],edgecolor='none',alpha=1))
bx.set(xlim=(-45,45),ylim=(-100,-15),zlim=(-26,26),xlabel='X (mm)',ylabel='Y (mm)',zlabel='Z (mm)',title='Saved CAD — adapters pulled forward 8 mm')
bx.set_box_aspect((90,85,52));bx.view_init(elev=22,azim=-66)
bx.tick_params(labelsize=8)
fig.suptitle('Gladiator mast head | removable sensor mounts',fontsize=19,x=.04,ha='left')
fig.text(.04,.055,'Orange: ToF frame, 14 mm rear stand-off. Green: radar frame, 22 mm rear stand-off.\nFour captive M3 nuts per frame; three M2 screws attach each adapter. Connectors and flex harness still require assembly checks.',fontsize=10,color='#354757')
fig.subplots_adjust(left=.06,right=.97,bottom=.19,top=.86,wspace=.13)
fig.savefig(OUT/'sensor-mounts.png')
(OUT/'sensor-preview-source.json').write_text(json.dumps({'native_file':str(native_path),
    'native_sha256':hashlib.sha256(native_path.read_bytes()).hexdigest(),
    'image_sha256':hashlib.sha256((OUT/'sensor-mounts.png').read_bytes()).hexdigest()},indent=2)+'\n')
print(OUT/'sensor-mounts.png')
