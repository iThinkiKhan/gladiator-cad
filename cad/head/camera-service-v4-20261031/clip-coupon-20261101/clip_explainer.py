"""How the v4 plug clip works: section through one plug + view of the comb face. Numbers from the v4 build."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import numpy as np

D = Path(__file__).resolve().parent
# v4 numbers (mm). r = distance behind the PCB back face (toward the tray floor); u = sideways from the pin,
# + toward the board centre, - toward the side wall where the wire leaves.
HDR, LC, COMB, GAP, FLOOR_R = 2.66, 14.0, 1.0, 0.4, 19.66
R_CL0, R_DEND = HDR + 2.0, HDR + LC
R_CLB = R_DEND + COMB
HOUS, POCK = 1.3, 1.33
LANE_IN = 0.75
PIN_Z = [15.58 - 2.54 * k for k in range(8)]
CL_Z0, CL_Z1 = PIN_Z[7] - 2.1, PIN_Z[0] + 2.1
BLUE, BLUE_D, GREY, PLUG, RED, GREEN = '#3a7bd5', '#1d4f99', '#9aa1a8', '#2b2b2b', '#d33', '#2e7d4f'

fig, (a1, a2) = plt.subplots(1, 2, figsize=(19, 10), gridspec_kw={'width_ratios': [1.45, 1]})
fig.suptitle('How the v4 plug clip works (section through one plug, to scale)', fontsize=18, weight='bold')


def box(ax, u0, u1, r0, r1, c, **k):
    ax.add_patch(Rectangle((u0, r0), u1 - u0, r1 - r0, facecolor=c, edgecolor=k.pop('ec', 'none'), **k))


# ---- left: side section through the centre of one plug
ax = a1
box(ax, -6, 6, -0.8, 0, GREEN)                                   # PCB
box(ax, -1.27, 1.27, 0, HDR, '#555')                             # header plastic
box(ax, -HOUS, HOUS, HDR, R_DEND, PLUG)                          # Dupont housing
box(ax, -0.32, 0.32, -0.8, HDR + 6.5, '#d4af37')                 # pin
# clip in this plane: outer wall + plate (wire side), inner plate, and the spine of the comb behind the plug
box(ax, -2.0, -POCK, R_CL0, R_DEND - 0.05, BLUE)
box(ax, POCK, 2.1, R_CL0, R_CLB, BLUE)
box(ax, LANE_IN, 2.1, R_DEND, R_CLB, BLUE_D)
# pad behind the spine, then the floor
box(ax, 1.1, 2.6, R_CLB + GAP, FLOOR_R, GREY, hatch='//', ec='#666')
box(ax, -9, 6, FLOOR_R, FLOOR_R + 3, GREY)
# wire: straight out of the plug end, through the open lane, then a sideways turn along the floor to the wall
t = np.linspace(0, np.pi / 2, 30); rb = 1.6
wx = np.concatenate([[0, 0], -rb + rb * np.cos(t), [-8.8]])
wy = np.concatenate([[R_DEND - 2.5, R_DEND + 0.4], R_DEND + 0.4 + rb * np.sin(t), [R_DEND + 0.4 + rb]])
ax.plot(wx, wy, color=RED, lw=9, solid_capstyle='round', zorder=5)
ax.add_patch(FancyArrowPatch((-0.3, R_DEND - 4), (-0.3, R_DEND - 0.4), arrowstyle='-|>', mutation_scale=22, color='orange', lw=3, zorder=6))
ax.add_patch(FancyArrowPatch((1.7, R_CLB - 0.2), (1.7, R_CLB + GAP + 0.1), arrowstyle='-|>', mutation_scale=18, color='orange', lw=3, zorder=6))
lab = dict(fontsize=12.5, va='center')
ax.text(6.3, -0.4, 'PCB (board back face)', **lab)
ax.text(6.3, 1.3, 'header plastic', **lab)
ax.text(6.3, 8, 'Dupont plug on its pin', **lab)
ax.text(6.3, 11.3, 'clip: a sleeve round the 8 plugs\n(blue). Slides on from behind\nafter the plugs are on.', **lab)
ax.text(6.3, R_DEND + 0.5, 'comb: the plug END pushes\non this edge (dark blue)', **lab)
ax.text(6.3, R_CLB + 1.0, 'floor pad, 0.4 mm behind the clip', **lab)
ax.text(6.3, FLOOR_R + 1.5, 'tray floor', **lab)
ax.text(-15.5, R_DEND - 7.5, 'If a plug starts to back off\nits pin, it pushes the clip\nback 0.4 mm onto the pad\nand stops there.', fontsize=12.5, color='#b35c00')
ax.text(-15.5, FLOOR_R - 4.6, 'wire leaves the plug end\nthrough an open slot in\nthe comb, turns sideways\nand runs out the side wall', fontsize=12.5, color=RED)
for x0, x1 in ((6.1, 2.2), (6.1, 1.4), (6.1, 1.4), (6.1, 2.2), (6.1, 2.2), (6.1, 2.7), (6.1, 1)):
    pass
ax.set_xlim(-16, 15.5); ax.set_ylim(FLOOR_R + 3.3, -1.5); ax.set_aspect('equal')
ax.set_xlabel('mm sideways from the pin (left = toward the side wall)'); ax.set_ylabel('mm behind the PCB')
ax.set_title('Side section (board on top, tray floor at the bottom)', fontsize=14)

# ---- right: looking at the comb face from the tray floor, one row of 8 plugs
ax = a2
box(ax, -1.7, 2.1, CL_Z0, CL_Z1, BLUE_D)                          # comb body (end walls + spine + teeth)
for pz in PIN_Z:                                                 # open lanes, one per wire, open on the wall side
    box(ax, -2.3, LANE_IN, pz - 0.87, pz + 0.87, 'white')
    ax.add_patch(plt.Circle((0, pz), 0.7, color=RED, zorder=4))  # wire
    ax.add_patch(Rectangle((-1.27, pz - 1.27), 2.54, 2.54, fill=False, ls='--', lw=1.4, ec=PLUG, zorder=5))
    # where the plug end bears on the comb: the spine strip and the two tooth edges
    box(ax, LANE_IN, 1.27, pz - 1.27, pz + 1.27, 'orange', alpha=.85, zorder=3)
    box(ax, -1.27, LANE_IN, pz + 0.87, pz + 1.27, 'orange', alpha=.85, zorder=3)
    box(ax, -1.27, LANE_IN, pz - 1.27, pz - 0.87, 'orange', alpha=.85, zorder=3)
for z0, z1, u0, u1 in ((CL_Z0 - 0.5, CL_Z0 + 0.6, -1.7, 2.1), (12.5, 15.5, 1.1, 2.6), (CL_Z1 - 0.6, CL_Z1 + 0.5, -1.7, 2.1)):
    box(ax, u0, u1, z0, z1, 'none', hatch='//', ec='#555', lw=1.2, zorder=6)
ax.text(2.9, PIN_Z[0], 'orange: plug end touching\nthe comb (rim round the wire)', fontsize=12.5, va='center')
ax.text(2.9, 14, 'hatched: floor pads behind', fontsize=12.5, va='center')
ax.text(2.9, PIN_Z[4], 'red: wire, in its own slot;\nslots open to the left, so\nwires drop in sideways', fontsize=12.5, va='center')
ax.text(2.9, PIN_Z[7], 'dashed: plug outline', fontsize=12.5, va='center')
ax.set_xlim(-3, 11); ax.set_ylim(CL_Z0 - 1.5, CL_Z1 + 1.5); ax.set_aspect('equal')
ax.set_xlabel('mm (left = toward the side wall)'); ax.set_title('Comb face, seen from the tray floor (one row of 8)', fontsize=14)
ax.set_yticks([])
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(D / 'clip_how_it_works.png', dpi=85)
print('ok')
