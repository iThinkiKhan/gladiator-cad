"""True CAD sections of the pan-lead route (stage 1: freecadcmd -> pan_lead_sections.json; stage 2: python3 ... draw)."""
import sys, os, json, math
from pathlib import Path
HERE = Path(os.path.abspath(__file__)).parent
J = HERE / 'pan_lead_sections.json'
AX = (39.5, 113.0)
U = (-math.sqrt(0.5), -math.sqrt(0.5))        # mast axis -> servo
W = (math.sqrt(0.5), -math.sqrt(0.5))
NAMES = ['Neck_Main', 'Mast_Tube_v2', 'Pan_Lead_Route', 'SG90_Pan_Reference', 'Pan_Servo_Carriage', 'Pan_Bearing_Lower',
         'Pan_Rotor', 'Pan_Drive_Pulley']

if len(sys.argv) < 2 or sys.argv[-1] != 'draw':
    import FreeCAD as App, Part
    V = App.Vector
    d = App.openDocument(str(HERE / 'Gladiator_Head_v2_PCB_Floor.FCStd'))
    out = {'vertical': {}, 'plan': {}}

    def polys(wires, conv):
        res = []
        for w in wires:
            pts = w.discretize(Deflection=0.02)
            res.append([conv(p) for p in pts])
        return res

    dv = W[0] * AX[0] + W[1] * AX[1]
    for n in NAMES:
        s = d.getObject(n).Shape
        ws = s.slice(V(W[0], W[1], 0), dv)
        out['vertical'][n] = polys(ws, lambda p: ((p.x - AX[0]) * U[0] + (p.y - AX[1]) * U[1], p.z))
        for z, key in ((146.8, 'plan'),):
            wz = s.slice(V(0, 0, 1), z)
            out[key][n] = polys(wz, lambda p: ((p.x - AX[0]) * U[0] + (p.y - AX[1]) * U[1],
                                               (p.x - AX[0]) * W[0] + (p.y - AX[1]) * W[1]))
    # servo outline in plan at Z 152 for the three carriage settings (only the servo moves)
    sv = d.getObject('SG90_Pan_Reference').Shape
    out['servo_plan'] = {}
    for C in (38.0, 44.0, 48.0):
        s = sv.copy(); s.translate(V(U[0] * (C - 44.0), U[1] * (C - 44.0), 0))
        out['servo_plan']['C%d' % C] = polys(s.slice(V(0, 0, 1), 152.0), lambda p: ((p.x - AX[0]) * U[0] + (p.y - AX[1]) * U[1],
                                                                                   (p.x - AX[0]) * W[0] + (p.y - AX[1]) * W[1]))
    J.write_text(json.dumps(out))
    os._exit(0)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
COL = {'Neck_Main': '#e8873a', 'Mast_Tube_v2': '#b5561d', 'Pan_Lead_Route': '#2050d0', 'SG90_Pan_Reference': '#5a7bb0',
       'Pan_Servo_Carriage': '#9a9a9a', 'Pan_Bearing_Lower': '#444444', 'Pan_Rotor': '#bbbbbb', 'Pan_Drive_Pulley': '#cfcfcf'}
LBL = {'Neck_Main': 'neck (changed)', 'Mast_Tube_v2': 'mast tube (changed)', 'Pan_Lead_Route': 'pan servo lead',
       'SG90_Pan_Reference': 'pan servo (C44)', 'Pan_Servo_Carriage': 'carriage', 'Pan_Bearing_Lower': 'lower bearing',
       'Pan_Rotor': 'pan rotor (turns)', 'Pan_Drive_Pulley': 'drive pulley'}
S = json.loads(J.read_text())
fig, axs = plt.subplots(1, 2, figsize=(19, 9), gridspec_kw={'width_ratios': [1.35, 1]})
ax = axs[0]
order = ['Pan_Rotor', 'Pan_Drive_Pulley', 'Pan_Bearing_Lower', 'Pan_Servo_Carriage', 'SG90_Pan_Reference', 'Mast_Tube_v2', 'Neck_Main', 'Pan_Lead_Route']
for n in order:
    for i, p in enumerate(S['vertical'].get(n, [])):
        if len(p) > 2:
            ax.add_patch(Polygon(p, closed=True, fc=COL[n], ec='k', lw=0.5, alpha=0.95, label=LBL[n] if i == 0 else None))
ax.axvline(0, color='k', ls='-.', lw=0.8); ax.text(0.4, 128.5, 'mast axis', fontsize=9)
for C, ls in ((38, ':'), (48, '--')):
    ax.axvline(C - 5.9, ymin=0, ymax=1, color='#5a7bb0', ls=ls, lw=1.2)
    ax.text(C - 5.9 + 0.3, 171, 'servo end at C%d' % C, color='#5a7bb0', fontsize=8, rotation=90, va='top')
ax.set_xlim(-14, 60); ax.set_ylim(128, 186); ax.set_aspect('equal'); ax.grid(alpha=0.25)
ax.set_xlabel('mm from the mast axis toward the pan servo'); ax.set_ylabel('world Z, mm')
ax.set_title('Vertical section through the mast axis along the servo line\n(lead drops off the servo end, runs under the neck flange, through the collar and the tube-top notch)', fontsize=11)
ax.legend(loc='upper left', fontsize=9, framealpha=0.95)
ax = axs[1]
for n in ('Neck_Main', 'Mast_Tube_v2', 'Pan_Lead_Route'):
    for i, p in enumerate(S['plan'].get(n, [])):
        if len(p) > 2:
            ax.add_patch(Polygon(p, closed=True, fc=COL[n], ec='k', lw=0.5, alpha=0.9, label=LBL[n] if i == 0 else None))
for k, ls in (('C38', ':'), ('C44', '-'), ('C48', '--')):
    for i, p in enumerate(S['servo_plan'][k]):
        ax.add_patch(Polygon(p, closed=True, fill=False, ec='#5a7bb0', ls=ls, lw=1.3, label='servo outline %s' % k if i == 0 else None))
ax.set_xlim(-16, 62); ax.set_ylim(-24, 24); ax.set_aspect('equal'); ax.grid(alpha=0.25)
ax.set_xlabel('mm from the mast axis toward the pan servo'); ax.set_ylabel('mm sideways')
ax.set_title('Plan section at Z 146.8 (through the tunnel), servo outlines at Z 152\nfor the three tensioner settings', fontsize=11)
ax.legend(loc='lower right', fontsize=9, framealpha=0.95)
fig.suptitle('Masthead v2 - pan servo lead enters the mast under the servo (DRAFT, CAD sections)', fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.95)); fig.savefig(HERE / 'pan_lead_review.png', dpi=100); print('ok')
