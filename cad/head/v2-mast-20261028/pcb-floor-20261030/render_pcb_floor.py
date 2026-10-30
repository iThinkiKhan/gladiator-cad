"""Close-up pictures of the PCB floor from the saved CAD (stage 1: freecadcmd exports meshes; stage 2: python3 draws).
    xvfb-run -a freecadcmd render_pcb_floor.py      (writes render/*.stl)
    python3 render_pcb_floor.py draw                (writes pcb_floor_review.png)
"""
import sys, os, json
from pathlib import Path
HERE = Path(os.path.abspath(__file__)).parent
RD = HERE / 'render'
NAMES = {'Tilt_Yoke': 'yoke', 'Pan_Raised_Pedestal': 'grey', 'Head_Distro_PCB_Placeholder': 'pcb',
         'M2_Insert_A': 'brass', 'M2_Insert_B': 'brass', 'M2_Insert_C': 'brass', 'Tilt_Lead_Route': 'lead',
         'Yoke_Bolt_Head_M3': 'dark', 'Neck_Main': 'yoke', 'Mast_Tube_v2': 'tube', 'Pan_Lead_Route': 'lead',
         'SG90_Pan_Reference': 'servo', 'Pan_Servo_Carriage': 'grey', 'Pan_Bearing_Lower': 'dark', 'Pan_Retainer': 'grey', 'SG90_Tilt_Reference': 'servo', 'Tilt_Pivot_Bolt': 'dark',
         'PCB_Part_Height_Zone_1': 'zone', 'PCB_Part_Height_Zone_2': 'zone', 'PCB_Part_Height_Zone_3': 'zone',
         'PCB_Part_Height_Zone_4': 'zone'}

if len(sys.argv) < 2 or sys.argv[-1] != 'draw':
    import FreeCAD as App, Mesh
    d = App.openDocument(str(HERE / 'Gladiator_Head_v2_PCB_Floor.FCStd'))
    RD.mkdir(exist_ok=True)
    for n in NAMES:
        o = d.getObject(n)
        if o:
            Mesh.Mesh(o.Shape.tessellate(0.05)).write(str(RD / (n + '.stl')))
    os._exit(0)

import numpy as np, struct, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
COL = {'yoke': (0.96, 0.55, 0.18), 'grey': (0.72, 0.72, 0.72), 'pcb': (0.10, 0.55, 0.25), 'brass': (0.85, 0.68, 0.25),
       'lead': (0.15, 0.35, 0.85), 'dark': (0.25, 0.25, 0.28), 'servo': (0.35, 0.48, 0.67), 'zone': (0.98, 0.85, 0.20), 'tube': (0.85, 0.45, 0.15)}


def read_stl(p):
    b = p.read_bytes()
    if b[:5] == b'solid' and b'facet' in b[:300]:
        v = [list(map(float, l.split()[1:4])) for l in b.decode().splitlines() if l.strip().startswith('vertex')]
        return np.array(v).reshape(-1, 3, 3)
    n = struct.unpack('<I', b[80:84])[0]
    a = np.frombuffer(b[84:84 + n * 50], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]))
    return a['v'].reshape(-1, 3, 3).astype(float)


def draw(ax, names, view, up=(0, 0, 1), light=(-0.4, -0.5, 0.8), zone_alpha=0.35, clip=None):
    view = np.array(view, float); view /= np.linalg.norm(view)
    upv = np.array(up, float); right = np.cross(view, upv); right /= np.linalg.norm(right); upv = np.cross(right, view)
    L = np.array(light, float); L /= np.linalg.norm(L)
    P, C, D = [], [], []
    for n in names:
        p = RD / (n + '.stl')
        if not p.exists():
            continue
        tri = read_stl(p)
        if clip is not None:
            tri = tri[clip(tri.mean(axis=1))]
            if not len(tri):
                continue
        nrm =np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); ln = np.linalg.norm(nrm, axis=1); ok = ln > 1e-9
        nrm[ok] /= ln[ok, None]
        shade = 0.45 + 0.55 * np.abs(nrm @ L)
        base = np.array(COL[NAMES[n]])
        a = zone_alpha if NAMES[n] == 'zone' else 1.0
        c = np.clip(base[None, :] * shade[:, None], 0, 1)
        c = np.concatenate([c, np.full((len(c), 1), a)], axis=1)
        P.append(np.stack([tri[ok] @ right, tri[ok] @ upv], axis=-1)); C.append(c[ok]); D.append((tri[ok] @ view).mean(axis=1))
    P = np.concatenate(P); C = np.concatenate(C); D = np.concatenate(D)
    o = np.argsort(-D)
    ax.add_collection(PolyCollection(P[o], facecolors=C[o], edgecolors=np.clip(C[o] * [0.8, 0.8, 0.8, 1], 0, 1), linewidths=0.12))
    allp = P.reshape(-1, 2)
    ax.set_xlim(allp[:, 0].min() - 3, allp[:, 0].max() + 3); ax.set_ylim(allp[:, 1].min() - 3, allp[:, 1].max() + 3)
    ax.set_aspect('equal'); ax.axis('off')


V = json.loads((HERE / 'validation.json').read_text())
H = V['max_part_height_above_board_mm']
fig, axs = plt.subplots(2, 2, figsize=(17, 14))
iso = (0.55, 0.75, -0.55)
draw(axs[0][0], ['Pan_Raised_Pedestal', 'Tilt_Yoke', 'Yoke_Bolt_Head_M3', 'Tilt_Lead_Route', 'M2_Insert_A', 'M2_Insert_B', 'M2_Insert_C'], iso)
axs[0][0].set_title('Yoke floor WITHOUT the board: pocket, lead-relief well, 3 M2 inserts (brass),\n'
                    'tilt-servo lead channel (blue lead) running under the board edge into the wire passage', fontsize=11)
draw(axs[0][1], ['Pan_Raised_Pedestal', 'Tilt_Yoke', 'Yoke_Bolt_Head_M3', 'Tilt_Lead_Route', 'Head_Distro_PCB_Placeholder',
                 'M2_Insert_A', 'M2_Insert_B', 'M2_Insert_C'], iso)
axs[0][1].set_title('With the placeholder board (green) seated: top is 0.6 mm above the floor;\n'
                    'notched round the yoke bolt head and the screwdriver hole to the pan retainer screw', fontsize=11)
draw(axs[1][0], ['Pan_Raised_Pedestal', 'Tilt_Yoke', 'Yoke_Bolt_Head_M3', 'Tilt_Lead_Route', 'Head_Distro_PCB_Placeholder',
                 'M2_Insert_A', 'M2_Insert_B', 'M2_Insert_C'], (0, 0, -1), up=(0, 1, 0))
axs[1][0].set_title('Top view (camera side at the bottom). Board about 23 x 29.5 mm', fontsize=11)
draw(axs[1][1], ['Pan_Raised_Pedestal', 'Tilt_Yoke', 'Yoke_Bolt_Head_M3', 'Head_Distro_PCB_Placeholder', 'SG90_Tilt_Reference',
                 'PCB_Part_Height_Zone_1', 'PCB_Part_Height_Zone_2', 'PCB_Part_Height_Zone_3', 'PCB_Part_Height_Zone_4'], iso)
axs[1][1].set_title('Yellow = tallest parts allowed on the board at every tilt angle:\n' +
                    ', '.join('%s %d mm' % (k.split(' ')[0].replace('_', ' '), v) for k, v in H.items()), fontsize=11)
fig.suptitle('Masthead v2 - head distro PCB held by the yoke floor (DRAFT, CAD only; board outline is a placeholder)', fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.97)); fig.savefig(HERE / 'pcb_floor_review.png', dpi=100)

fig, axs = plt.subplots(1, 3, figsize=(21, 8.5))
AXC = np.array([39.5, 113.0])
U = np.array([-0.70710678, -0.70710678]); W = np.array([0.70710678, -0.70710678])
r_of = lambda c: (c[:, :2] - AXC) @ U          # distance from the mast axis toward the servo
w_of = lambda c: (c[:, :2] - AXC) @ W          # sideways from that line
zwin = lambda c, z0, z1: (c[:, 2] > z0) & (c[:, 2] < z1)
# 1) cutaway on the lead's centre line: the half nearer the viewer removed, looking across the line
cut = lambda c: zwin(c, 132, 172) & (w_of(c) > 0) & (r_of(c) > -14) & (r_of(c) < 58)
draw(axs[0], ['Neck_Main', 'Mast_Tube_v2', 'Pan_Lead_Route', 'SG90_Pan_Reference', 'Pan_Servo_Carriage', 'Pan_Bearing_Lower'],
     (W[0], W[1], 0.0), clip=cut)
axs[0].set_title('Cutaway along the lead (mast on the left, servo on the right):\nlead drops off the servo end, runs under the neck flange, through\nthe collar and the tube-top notch into the bore', fontsize=11)
# 2) from below, servo side toward the viewer, servo and carriage hidden
near = lambda c: zwin(c, 136, 166) & (r_of(c) > -16) & (r_of(c) < 40) & (np.abs(w_of(c)) < 26)
draw(axs[1], ['Neck_Main', 'Mast_Tube_v2', 'Pan_Lead_Route'], (0.5, 0.5, 0.7), clip=near)
axs[1].set_title('From below on the servo side (servo hidden): 8.4 mm slot under the\nflange, tunnel into the collar, groove in the housing wall for C38', fontsize=11)
# 3) tube top alone from above on the servo side
draw(axs[2], ['Mast_Tube_v2', 'Pan_Lead_Route'], (0.5, 0.5, -0.7), clip=lambda c: zwin(c, 128, 160))
axs[2].set_title('Tube top alone: 8.4 x 5.2 notch on the servo side, opposite the key\nflat, so the notch always lines up with the tunnel', fontsize=11)
fig.suptitle('Masthead v2 - pan servo lead enters the mast under the servo (DRAFT, CAD only)', fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(HERE / 'pan_lead_review.png', dpi=100); print('ok')
