"""Cut-and-drill picture for the side-window perfboard, parts facing INTO the head (python3 board_template.py)."""
import json
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / 'inward_depth.json').read_text())
BY0, BZ0, L, W = 91.5, 232.5, 55.0, 30.0          # board camera-end edge (world Y) and bottom edge (world Z)
WIN = (90.9 - BY0, 140.5 - BY0, 235.5 - BZ0, 259.5 - BZ0)   # window in board coords (u along, v up)
HOLE = (113.0 - BY0, 247.5 - BZ0)
# inward room (mm from the board's inner face) on a 1 mm grid; first/last Z rows are the rail edges
us = sorted({p[0] - BY0 for p in D}); vs = sorted({p[1] - BZ0 for p in D})
G = {(p[0] - BY0, p[1] - BZ0): p[2] - 1.0 for p in D}
inner = [(u, v, G[(u, v)]) for u in us for v in vs if WIN[2] + 0.4 < v < WIN[3] - 0.4 and u < WIN[1] - 0.6]
summ = {'min_room_whole_window': min(r for *_, r in inner),
        'min_room_bottom_strip_v4_8': min(r for u, v, r in inner if 4 <= v <= 8),
        'min_room_top_strip_v22_26': min(r for u, v, r in inner if 22 <= v <= 26),
        'min_room_bottom_strip_excl_yoke_band': min(r for u, v, r in inner if 4 <= v <= 8 and not 15 <= u <= 27 and u > 2),
        'min_room_top_strip_excl_yoke_band': min(r for u, v, r in inner if 22 <= v <= 26 and not 15 <= u <= 27 and u > 2)}
print(summ)
(HERE / 'inward_room_summary.json').write_text(json.dumps(summ, indent=1))

fig, ax = plt.subplots(figsize=(14, 11))
# room map
cmap = matplotlib.colors.ListedColormap(['#e8a33d', '#f3d36b', '#9fd59a', '#4fae6a'])
norm = matplotlib.colors.BoundaryNorm([0, 13.5, 16.5, 25.5, 99], cmap.N)
arr = np.full((len(vs), len(us)), np.nan)
for i, v in enumerate(vs):
    for j, u in enumerate(us):
        if WIN[2] + 0.4 < v < WIN[3] - 0.4:
            arr[i, j] = G[(u, v)]
ax.imshow(arr, origin='lower', extent=(us[0] - .5, us[-1] + .5, vs[0] - .5, vs[-1] + .5), cmap=cmap, norm=norm,
          interpolation='nearest', alpha=0.85, zorder=1)
# board, bar grip strips, solid-frame end
ax.add_patch(Rectangle((0, 0), L, W, fill=False, lw=2.5, ec='#1b5e20', zorder=5))
for v0 in (0, W - 3):
    ax.add_patch(Rectangle((0, v0), L, 3, fc='#b0388c', alpha=0.35, hatch='//', ec='#b0388c', zorder=3))
ax.add_patch(Rectangle((WIN[1], 3), L - WIN[1], W - 6, fc='#9e9e9e', alpha=0.6, hatch='xx', ec='#616161', zorder=3))
# hole grid, usual 3 x 7 cm board = 10 x 24 holes; factory edge kept at the camera end, cut at the far end
gu = 5.79 + 2.54 * np.arange(24); gv = 3.57 + 2.54 * np.arange(10)
gu = gu[gu < L - 0.8]
for u in gu:
    for v in gv:
        bad = (v < 4) or (v > W - 4) or (u > WIN[1] - 0.6) or np.hypot(u - HOLE[0], v - HOLE[1]) < 4.2
        ax.plot(u, v, 'o', ms=4.2, mfc='white' if not bad else '#cfcfcf', mec='#333' if not bad else '#999', mew=.8, zorder=6)
# access hole + keep-out ring
ax.add_patch(Circle(HOLE, 3.0, fc='white', ec='k', lw=2, zorder=7))
ax.add_patch(Circle(HOLE, 4.0, fill=False, ec='k', lw=1, ls='--', zorder=7))
ax.annotate('drill 6 mm\n21.5 from camera end\n15 up (centre of board)\nscrewdriver to the tilt horn\ngoes through here: keep\nparts 1 mm off the hole', HOLE,
            xytext=(10, -7.5), ha='center', va='top', fontsize=9.5, arrowprops=dict(arrowstyle='->'), zorder=8)
# suggested spots
def tag(u0, u1, v0, v1, txt, c):
    ax.add_patch(Rectangle((u0, v0), u1 - u0, v1 - v0, fill=False, ec=c, lw=2, ls='-', zorder=8))
    ax.text((u0 + u1) / 2, (v0 + v1) / 2, txt, ha='center', va='center', fontsize=8.5, color=c, weight='bold', zorder=9,
            bbox=dict(fc='white', ec='none', alpha=0.85, pad=1.5))
tag(2.5, 16.0, 21.5, 26.2, 'pigtails / plugs', '#0d47a1')
tag(27.5, 48.0, 21.5, 26.2, 'pigtails / plugs', '#0d47a1')
tag(2.5, 16.0, 3.8, 8.5, 'pigtails / plugs', '#0d47a1')
tag(27.5, 48.0, 3.8, 8.5, 'pigtails / plugs', '#0d47a1')
tag(26.0, 33.0, 10.5, 19.5, 'trunk in\n5V GND\nSDA SCL', '#b71c1c')
tag(35.0, 48.0, 10.5, 19.5, 'cap, pull-ups,\nflat parts\n(10 mm max)', '#4a148c')
# dimensions
ax.annotate('', (0, -3.2), (L, -3.2), arrowprops=dict(arrowstyle='<->'))
ax.text(L / 2, -4.6, '55 mm  (your 70 mm board, cut 15 mm off the far end)', ha='center', fontsize=10)
ax.annotate('', (-3.2, 0), (-3.2, W), arrowprops=dict(arrowstyle='<->'))
ax.text(-4.3, W / 2, '30 mm (as is)', rotation=90, va='center', ha='right', fontsize=10)
ax.text(0.3, W + 1.2, 'CAMERA END\n(against the camera-carrier plate)', fontsize=9.5, va='bottom', weight='bold')
ax.text(L - 0.3, W + 1.2, 'SCREEN END\n(end of the frame)', fontsize=9.5, va='bottom', ha='right', weight='bold')
ax.text(L / 2, W - 1.5, 'clamp bar grips this 3 mm strip: no parts, no solder blobs (top and bottom)', ha='center', va='center',
        fontsize=8.5, color='#6a1b4a', zorder=9)
ax.text((WIN[1] + L) / 2, W / 2, 'over solid\nframe:\nnothing\nthrough\nthe board\nhere', ha='center', va='center',
        fontsize=8.5, zorder=9)
# legend
from matplotlib.patches import Patch
ax.legend(handles=[Patch(fc='#e8a33d', label='10 mm of room inward (receiver face)'),
                   Patch(fc='#f3d36b', label='12-14 mm'), Patch(fc='#9fd59a', label='15-17 mm'),
                   Patch(fc='#4fae6a', label='24 mm or more'),
                   Patch(fc='white', ec='#333', label='usable hole (usual 10 x 24 hole board)'),
                   Patch(fc='#cfcfcf', ec='#999', label='hole lost (bar strip, hole, solid frame)')],
          loc='upper right', bbox_to_anchor=(1.0, 0.27), fontsize=9.5, frameon=False, ncol=2,
          title='Room for parts on the inner face\n(2 mm clearance already taken off)', title_fontsize=10)
ax.set_xlim(-8, L + 2); ax.set_ylim(-24, W + 6); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Side-window perfboard, PARTS SIDE (faces into the head), seen from inside the head.\n'
             'Pads/solder side faces out against the rails. Draft from CAD, not measured.', fontsize=12)
fig.tight_layout(); fig.savefig(HERE / 'board_cut_drill_inward.png', dpi=110)
print('ok')
