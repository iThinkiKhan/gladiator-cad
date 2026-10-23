import re, sys
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
g, out = sys.argv[1], sys.argv[2]; X0, X1 = float(sys.argv[3]), float(sys.argv[4])
x = y = z = 0.; role = ''; h = .2; segs = []
for l in open(g, errors='ignore'):
    if l.startswith(';TYPE:'): role = l[6:].strip(); continue
    if l.startswith(';HEIGHT:'): h = float(l[8:]); continue
    if not l.startswith('G1 '): continue
    v = {a: float(b) for a, b in re.findall(r'([XYZE])([-\d.]+)', l.split(';')[0])}
    nx, ny, z = v.get('X', x), v.get('Y', y), v.get('Z', z)
    if v.get('E', 0) > 0 and X0 <= (x + nx) / 2 <= X1 and z < 70: segs.append((min(y, ny), max(y, ny), z, h, role))
    x, y = nx, ny
fig, ax = plt.subplots(figsize=(12, 6))
for a, b, zz, hh, r in segs:
    ax.add_patch(Rectangle((a, zz - hh), max(b - a, .4), hh, color='#3a7bd5' if r.startswith('Support') else '#c62828', lw=0))
ax.set_xlim(60, 150); ax.set_ylim(0, 70); ax.set_aspect('equal'); ax.set_xlabel('Y mm (along the wall)'); ax.set_ylabel('Z mm')
ax.set_title('%s: everything printed between X %.0f and %.0f (wall seen face-on). red=part blue=support' % (g.split('/')[-1], X0, X1), fontsize=9)
fig.tight_layout(); fig.savefig(out, dpi=100); print(out)
