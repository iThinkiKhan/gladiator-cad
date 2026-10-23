import re, sys
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
fig, axs = plt.subplots(1, len(sys.argv) - 2, figsize=(7 * (len(sys.argv) - 2), 7))
for ax, g in zip(axs if len(sys.argv) > 3 else [axs], sys.argv[2:]):
    x = y = 0.; role = ''; w = .45; segs = []; layer = 0
    for l in open(g, errors='ignore'):
        if l.startswith(';LAYER_CHANGE'):
            layer += 1
            if layer > 1: break
        if l.startswith(';TYPE:'): role = l[6:].strip(); continue
        if l.startswith(';WIDTH:'): w = float(l[7:]); continue
        if not l.startswith('G1 '): continue
        v = {a: float(b) for a, b in re.findall(r'([XYE])([-\d.]+)', l.split(';')[0])}
        nx, ny = v.get('X', x), v.get('Y', y)
        if v.get('E', 0) > 0 and layer == 1 and role != 'Custom': segs.append(((x, y), (nx, ny), w, role))
        x, y = nx, ny
    xs = [p[0] for s in segs for p in s[:2]]; ys = [p[1] for s in segs for p in s[:2]]
    ax.set_xlim(min(xs) - 3, max(xs) + 3); ax.set_ylim(min(ys) - 3, max(ys) + 3); ax.set_aspect('equal')
    fig.canvas.draw(); ptmm = ax.get_window_extent().width / fig.dpi * 72 / (max(xs) - min(xs) + 6)
    ax.add_collection(LineCollection([s[:2] for s in segs], linewidths=[s[2] * ptmm for s in segs],
        colors=['#9e9e9e' if s[3] == 'Brim' else '#3a7bd5' if s[3].startswith('Support') else '#c62828' for s in segs]))
    ax.set_title(g.split('/')[-1] + ' - first layer (grey brim, red part, blue support)', fontsize=8)
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=90)
