"""Draw a plate from its G-code: top view and a side cut, lines at real extrusion width.
Usage: render_plate.py file.gcode out.png "Title" [cutY]   Colours: by colour band if M600s present, else by model/support."""
import re, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
g, out, title = sys.argv[1], sys.argv[2], sys.argv[3]
cuty = float(sys.argv[4]) if len(sys.argv) > 4 else None
CRADLE = len(sys.argv) > 5 and sys.argv[5] == 'cradle'
segs = []; x = y = z = 0.; role = ''; w = .4; h = .2; band = 0; bands = ['start colour']; changes = []
for l in open(g, errors='ignore'):
    if l.startswith(';TYPE:'): role = l[6:].strip(); continue
    if l.startswith(';WIDTH:'): w = float(l[7:]); continue
    if l.startswith(';HEIGHT:'): h = float(l[8:]); continue
    if l.startswith(';GLAD_COLOUR_CHANGE'):
        band += 1; bands.append(l.split()[2]); changes.append((l.split()[2], z)); continue
    if not l.startswith(('G1 ', 'G0 ')): continue
    v = {a: float(b) for a, b in re.findall(r'([XYZE])([-\d.]+)', l.split(';')[0])}
    nx, ny, nz = v.get('X', x), v.get('Y', y), v.get('Z', z)
    if v.get('E', 0) > 0 and (nx != x or ny != y) and role not in ('Custom', ''):
        segs.append((x, y, nx, ny, nz, w, h, role, band))
    x, y, z = nx, ny, nz
start = re.search(r'Load (\w+)', open(g, errors='ignore').read(2000))
COL = {'RED': '#c62828', 'GREY': '#8a8f94', 'WHITE': '#d9d4c7', 'BLACK': '#222'}
first = 'RED' if changes else None
names = [first] + [c for c, _ in changes] if changes else None
def is_cradle(s):
    xm = (s[0] + s[2]) / 2; cx = 90.35 if xm < 110 else 129.65; zm = s[4] - s[6] / 2
    return ((xm - cx) ** 2 + (zm + 23.988) ** 2) ** .5 < 27.5
def colour(s):
    if names: return COL.get(names[s[8]], '#555')
    if CRADLE and s[7] != 'Brim': return '#3a7bd5' if is_cradle(s) else '#e0a030'
    if s[7].startswith('Support'): return '#3a7bd5'
    if s[7] == 'Brim': return '#bbbbbb'
    return '#e0a030'
fig_w = 15
fig, axs = plt.subplots(1, 2, figsize=(fig_w, 7.6), gridspec_kw=dict(width_ratios=[1, 1.15]))
ax = axs[0]; L = 225.
ax.set_xlim(-2, 222); ax.set_ylim(-2, 222); ax.set_aspect('equal')
fig.canvas.draw(); bb = ax.get_window_extent(); ptmm = bb.width / fig.dpi * 72 / 224
top = sorted(segs, key=lambda s: s[4])
ax.add_collection(LineCollection([((s[0], s[1]), (s[2], s[3])) for s in top], colors=[colour(s) for s in top], linewidths=[s[5] * ptmm for s in top], capstyle='butt'))
ax.add_patch(Rectangle((0, 0), 220, 220, fill=False, ec='k', lw=1.2))
ax.plot([10, 10.5], [20, 180], color='#2e7d32', lw=2); ax.text(12, 185, 'purge', color='#2e7d32', fontsize=8)
if changes: ax.plot(5, 200, 'k*', ms=12); ax.text(8, 203, 'M600 park X5 Y200', fontsize=8)
if cuty is not None: ax.axhline(cuty, color='m', ls='--', lw=.8); ax.text(150, cuty + 2, 'side cut', color='m', fontsize=8)
ax.set_title('Top view (real bed 220 x 220)', fontsize=10); ax.set_xlabel('X mm'); ax.set_ylabel('Y mm')
ax = axs[1]
cy = cuty if cuty is not None else 110
xs = [s for s in segs if (min(s[1], s[3]) - s[5] / 2 <= cy <= max(s[1], s[3]) + s[5] / 2)]
rects = []
for s in xs:
    x0, y0, x1, y1 = s[:4]
    if abs(y1 - y0) < 1e-6: xa, xb = sorted((x0, x1))
    else:
        t = (cy - y0) / (y1 - y0) if y1 != y0 else 0; t = min(max(t, 0), 1); xc = x0 + t * (x1 - x0); xa, xb = xc - s[5] / 2, xc + s[5] / 2
    ax.add_patch(Rectangle((xa, s[4] - s[6]), xb - xa, s[6], color=colour(s), lw=0))
zs = [s[4] for s in segs]; xa_ = [min(s[0], s[2]) for s in segs]; xb_ = [max(s[0], s[2]) for s in segs]
ax.set_xlim(min(xa_) - 3, max(xb_) + 3) if not CRADLE else ax.set_xlim(74, 107); ax.set_ylim(0, max(zs) + 1); ax.set_aspect('equal')
for c, zc in changes: ax.axhline(zc, color='k', lw=.6, ls=':'); ax.text(max(xb_) + 1, zc, ' ' + c + ' from here', fontsize=8, va='bottom')
ax.set_title('Side cut at Y=%.0f (layers as printed)' % cy, fontsize=10); ax.set_xlabel('X mm'); ax.set_ylabel('Z mm')
t = re.search(r'estimated printing time \(normal mode\) = (.*)', open(g, errors='ignore').read())
fig.suptitle(title + ('   |   ' + t.group(1) if t else ''), fontsize=12)
if names:
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=COL[n], label=n) for n in dict.fromkeys(names)], loc='lower center', ncol=4)
else:
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color='#e0a030', label='emblem' if CRADLE else 'part'), Patch(color='#3a7bd5', label='cradle (snap off after)' if CRADLE else 'support'), Patch(color='#bbbbbb', label='brim')], loc='lower center', ncol=3)
fig.tight_layout(rect=(0, .04, 1, .96)); fig.savefig(out, dpi=110)
print(out)
