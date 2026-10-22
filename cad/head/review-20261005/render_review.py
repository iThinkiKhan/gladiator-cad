"""Render true solid sections showing the corrected tilt horn screw seat."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

folder = Path(__file__).resolve().parent
source = (folder / 'build_head_review.py').read_text()
exec(compile(source.split('# ================================================================== collision sweeps')[0], 'candidate_geometry', 'exec'))
fixed = parts['GH44_Tilt_Receiver']['shape']
old = fixed.cut(cx(3.5, -25.5, 7.0, T.y, TZ))
slab = box(-26, T.y-.005, TZ-8, 16, .01, 16)

def draw_section(ax, shape, color):
    vertices, triangles = shape.common(slab).tessellate(.015)
    pts = np.array([[v.x, v.z-TZ] for v in vertices])
    polys = []
    for tri in triangles:
        q = pts[list(tri)]
        area = abs(np.linalg.det(np.column_stack([q[1]-q[0], q[2]-q[0]])))
        if area > 1e-9:
            polys.append(q)
    ax.add_collection(PolyCollection(polys, facecolor=color, edgecolor='none'))

fig, axes = plt.subplots(1, 2, figsize=(13, 6), dpi=150)
fig.patch.set_facecolor('#f4f6f8')
for ax, shape, title in zip(axes, (old, fixed), ('Before: screw seat cut away', 'Corrected: 1.2 mm screw seat retained')):
    ax.set_facecolor('#ffffff')
    draw_section(ax, parts['Tilt_Horn_Reference']['shape'], '#4b79bd')
    draw_section(ax, shape, '#d98a32')
    ax.set(xlim=(-25.5,-12), ylim=(-7.5,7.5), xlabel='X relative to mast axis (mm)', ylabel='Height relative to tilt axis (mm)', title=title)
    ax.set_aspect('equal')
    ax.grid(alpha=.18)
    ax.axhline(0, color='#8592a3', lw=.7, linestyle='--')
    ax.annotate('Screw / driver entry', xy=(-23.3,0), xytext=(-25, -5.5), fontsize=9,
                arrowprops={'arrowstyle':'->', 'color':'#364759'})
axes[0].annotate('7 mm access cut removes\nthe entire retaining web', xy=(-20.5,1.9), xytext=(-25,5.5), fontsize=9,
                 arrowprops={'arrowstyle':'->', 'color':'#364759'})
axes[1].annotate('3.4 mm screw hole\nthrough intact roof', xy=(-20.5,1.9), xytext=(-25,5.5), fontsize=9,
                 arrowprops={'arrowstyle':'->', 'color':'#364759'})
fig.suptitle('Gladiator mast head | tilt coupling correction', fontsize=18, x=.06, ha='left')
fig.text(.06,.03,'Actual CAD sections through the tilt axis. Orange: receiver. Blue: installed horn.\n16.5 mm measured to the raised hub; actual screw size and engagement still need fit verification.',fontsize=10,color='#364759')
fig.subplots_adjust(left=.065,right=.98,top=.84,bottom=.19,wspace=.23)
fig.savefig(folder/'tilt-correction.png')
print(folder/'tilt-correction.png')

