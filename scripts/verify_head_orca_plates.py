import subprocess, re, json, sys
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
OUT = Path('/home/buralien/projects/gladiator-cad/cad/head/orca-plates')
W = Path('/home/buralien/scratch_claude/slice_orca'); W.mkdir(exist_ok=True)
summ = json.load(open(OUT / 'build-summary.json'))
res = {}
for key, info in summ['plates'].items():
    if len(sys.argv) > 1 and key not in sys.argv[1:]: continue
    od = W / key; od.mkdir(exist_ok=True)
    for f in od.glob('*'): f.unlink()
    r = subprocess.run(['flatpak', 'run', '--filesystem=%s' % Path.home(), 'com.orcaslicer.OrcaSlicer', '--slice', '1', '--outputdir', str(od), str(OUT / info['file'])],
                       capture_output=True, text=True, timeout=1500)
    gc = list(od.glob('*.gcode'))
    if not gc:
        print(key, 'NO GCODE rc', r.returncode, (od / 'result.json').read_text() if (od / 'result.json').exists() else r.stdout[-300:] + r.stderr[-300:]); continue
    lines = gc[0].read_text(errors='ignore').splitlines()
    hdr = '\n'.join(l for l in lines if l.startswith('; ') and any(s in l for s in ('estimated printing time', 'total filament', 'total layers', 'filament used [g]')))
    typ = None; x = y = z = 0.0; e_abs = False; rel = True
    seglen = {}; sup = []
    pe = 0.0
    for l in lines:
        if l.startswith(';TYPE:'): typ = l[6:].strip(); continue
        if l.startswith('M82'): rel = False
        if l.startswith('M83'): rel = True
        if l.startswith('G1') or l.startswith('G0'):
            mx = re.search(r' X([-\d.]+)', l); my = re.search(r' Y([-\d.]+)', l); mz = re.search(r' Z([-\d.]+)', l); me = re.search(r' E([-\d.]+)', l)
            nx = float(mx.group(1)) if mx else x; ny = float(my.group(1)) if my else y
            if mz: z = float(mz.group(1))
            e = float(me.group(1)) if me else 0.0
            ext = e if rel else e - pe
            if me and not rel: pe = e
            if ext > 0 and typ and (mx or my):
                L = np.hypot(nx - x, ny - y); seglen[typ] = seglen.get(typ, 0) + L
                if typ.startswith('Support'): sup.append((x, y, nx, ny, z, typ))
            x, y = nx, ny
    print('=' * 80); print(key, info['file']); print(hdr)
    print('  path length by type (mm):', {k: round(v) for k, v in sorted(seglen.items(), key=lambda kv: -kv[1])})
    res[key] = dict(types={k: round(v) for k, v in seglen.items()}, header=hdr)
    # picture of the support footprints
    fig, ax = plt.subplots(figsize=(9, 9))
    for p in info['parts']:
        cx, cy = p['at']; w, h = p['size']
        ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fill=False, ec='#444', lw=1))
        ax.text(cx, cy + h / 2 + 1, p['part'], ha='center', fontsize=7)
    if sup:
        zs = np.array([s[4] for s in sup])
        for (x0, y0, x1, y1, zz, tp), in zip(sup):
            ax.plot([x0, x1], [y0, y1], '-', color=plt.cm.viridis(zz / max(zs.max(), 1)), lw=.5)
        sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0, zs.max())); plt.colorbar(sm, ax=ax, label='support layer height z (mm)', shrink=.7)
    ax.set_xlim(0, 220); ax.set_ylim(0, 220); ax.set_aspect('equal'); ax.grid(alpha=.2)
    ax.set_title('Plate %s: support extrusions seen from above (outlines = part footprints)' % key)
    fig.savefig(OUT / ('support-map-%s.png' % key), dpi=90, bbox_inches='tight'); plt.close(fig)
json.dump(res, open(W / 'verify.json', 'w'), indent=1)
