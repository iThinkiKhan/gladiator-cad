"""Pictures of the side-window board (stage 1: freecadcmd exports meshes; stage 2: python3 render_side_pcb.py draw)."""
import sys, os, json, struct
from pathlib import Path
HERE = Path(os.path.abspath(__file__)).parent
RD = HERE / 'render'
KIND = {'Rear_Display_Frame': 'orange', 'Side_PCB_Clamp_Bar_Bottom': 'bar', 'Side_PCB_Clamp_Bar_Top': 'bar',
        'Side_PCB_30x55_Placeholder': 'pcb', 'Side_PCB_Parts_Envelope_20mm': 'zone',
        'Side_PCB_M2_Insert_1': 'brass', 'Side_PCB_M2_Insert_2': 'brass', 'Side_PCB_M2_Insert_3': 'brass', 'Side_PCB_M2_Insert_4': 'brass',
        'GH44_Tilt_Receiver': 'grey', 'GH44_Dual_Carrier': 'grey', 'Camera_Tray': 'grey', 'Camera_Cover': 'grey',
        'ToF_Sensor_Frame': 'grey', 'ST7789_Board': 'blue', 'ESP32_CAM_Reference': 'blue', 'Tilt_Horn_Reference': 'dark',
        'SG90_Tilt_Reference': 'blue', 'Tilt_Yoke': 'grey', 'Tilt_Pivot_Bolt': 'dark', 'Pan_Raised_Pedestal': 'grey'}
if len(sys.argv) < 2 or sys.argv[-1] != 'draw':
    import FreeCAD as App, Mesh
    d = App.openDocument(str(HERE / 'Gladiator_Head_v2_Side_PCB.FCStd'))
    RD.mkdir(exist_ok=True)
    for n in KIND:
        o = d.getObject(n)
        if o:
            Mesh.Mesh(o.Shape.tessellate(0.05)).write(str(RD / (n + '.stl')))
    os._exit(0)
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
COL = {'orange': (0.96, 0.55, 0.18), 'pcb': (0.10, 0.55, 0.25), 'zone': (0.98, 0.85, 0.20), 'brass': (0.85, 0.68, 0.25),
       'grey': (0.74, 0.75, 0.77), 'blue': (0.35, 0.48, 0.67), 'dark': (0.25, 0.25, 0.28), 'bar': (0.72, 0.22, 0.55)}


def read_stl(p):
    b = p.read_bytes()
    if b[:5] == b'solid' and b'facet' in b[:300]:
        v = [list(map(float, l.split()[1:4])) for l in b.decode().splitlines() if l.strip().startswith('vertex')]
        return np.array(v).reshape(-1, 3, 3)
    n = struct.unpack('<I', b[80:84])[0]
    a = np.frombuffer(b[84:84 + n * 50], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]))
    return a['v'].reshape(-1, 3, 3).astype(float)


def draw(ax, names, view, up=(0, 0, 1), light=(-0.6, -0.3, 0.75), alpha=None, tilt=0.0):
    view = np.array(view, float); view /= np.linalg.norm(view)
    upv = np.array(up, float); right = np.cross(view, upv); right /= np.linalg.norm(right); upv = np.cross(right, view)
    L = np.array(light, float); L /= np.linalg.norm(L)
    c_, s_ = np.cos(np.radians(tilt)), np.sin(np.radians(tilt)); Tax = np.array([39.5, 113.0, 247.5])
    P, C, D = [], [], []
    for n in names:
        p = RD / (n + '.stl')
        if not p.exists():
            continue
        tri = read_stl(p)
        if tilt and n not in ('Tilt_Yoke', 'SG90_Tilt_Reference', 'Tilt_Pivot_Bolt', 'Pan_Raised_Pedestal'):
            q = tri - Tax; y = q[..., 1] * c_ - q[..., 2] * s_; z = q[..., 1] * s_ + q[..., 2] * c_
            tri = np.stack([q[..., 0], y, z], axis=-1) + Tax
        nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); ln = np.linalg.norm(nrm, axis=1); ok = ln > 1e-9
        nrm[ok] /= ln[ok, None]
        shade = 0.45 + 0.55 * np.abs(nrm @ L)
        a = (alpha or {}).get(KIND[n], 0.4 if KIND[n] == 'zone' else 1.0)
        c = np.clip(np.array(COL[KIND[n]])[None, :] * shade[:, None], 0, 1)
        c = np.concatenate([c, np.full((len(c), 1), a)], axis=1)
        P.append(np.stack([tri[ok] @ right, tri[ok] @ upv], axis=-1)); C.append(c[ok]); D.append((tri[ok] @ view).mean(axis=1))
    P = np.concatenate(P); C = np.concatenate(C); D = np.concatenate(D); o = np.argsort(-D)
    ax.add_collection(PolyCollection(P[o], facecolors=C[o], edgecolors=np.clip(C[o] * [0.8, 0.8, 0.8, 1], 0, 1), linewidths=0.12))
    allp = P.reshape(-1, 2)
    ax.set_xlim(allp[:, 0].min() - 3, allp[:, 0].max() + 3); ax.set_ylim(allp[:, 1].min() - 3, allp[:, 1].max() + 3)
    ax.set_aspect('equal'); ax.axis('off')


V = json.loads((HERE / 'validation.json').read_text())
HEAD = ['Rear_Display_Frame', 'GH44_Tilt_Receiver', 'GH44_Dual_Carrier', 'Camera_Tray', 'Camera_Cover', 'ToF_Sensor_Frame',
        'ST7789_Board', 'ESP32_CAM_Reference', 'Tilt_Horn_Reference', 'SG90_Tilt_Reference', 'Tilt_Yoke', 'Tilt_Pivot_Bolt']
NEW = ['Side_PCB_30x55_Placeholder', 'Side_PCB_Clamp_Bar_Bottom', 'Side_PCB_Clamp_Bar_Top',
       'Side_PCB_M2_Insert_1', 'Side_PCB_M2_Insert_2', 'Side_PCB_M2_Insert_3', 'Side_PCB_M2_Insert_4']
fig, axs = plt.subplots(1, 3, figsize=(22, 8.5))
draw(axs[0], HEAD + NEW, (1, 0, 0))
axs[0].set_title('Side of the head away from the camera, looking straight at it:\n30 x 55 board (green) over the window, held by two printed clamp bars (magenta);\n6 mm hole on the tilt axis for the horn-screw screwdriver', fontsize=11)
draw(axs[1], HEAD + NEW + ['Side_PCB_Parts_Envelope_20mm'], (0.8, 0.45, -0.4))
axs[1].set_title('3D view. Yellow = 20 mm of parts on the outer face:\nclear of everything at every tilt and pan angle', fontsize=11)
draw(axs[2], HEAD + ['Side_PCB_M2_Insert_1', 'Side_PCB_M2_Insert_2', 'Side_PCB_M2_Insert_3', 'Side_PCB_M2_Insert_4'], (1, 0, 0))
axs[2].set_title('Board and bars removed: the window between the two frame rails (24 tall,\nabout 50 long). Brass = the 4 M2 heat-set inserts in the rails', fontsize=11)
for n in ('Side_PCB_M2_Insert_1', 'Side_PCB_M2_Insert_2', 'Side_PCB_M2_Insert_3', 'Side_PCB_M2_Insert_4'):
    pass
fig.suptitle('Masthead v2 - head distro perfboard in the screen-frame side window (DRAFT, CAD only)', fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig(HERE / 'side_pcb_review.png', dpi=100); print('ok')
