"""Render v1 vs v2 masthead pictures from the exported meshes (system python3: numpy + matplotlib)."""
import json, struct, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

RD = Path(sys.argv[1])
VAL = json.loads(Path(sys.argv[2]).read_text())['v2']
OUTP = Path(sys.argv[3])
idx = json.loads((RD / 'index.json').read_text())
COL = {'same': np.array([0.70, 0.70, 0.70]), 'changed': np.array([0.93, 0.55, 0.20]),
       'hardware': np.array([0.45, 0.60, 0.80]), 'belt': np.array([0.15, 0.15, 0.15]), 'context': np.array([0.93, 0.85, 0.85])}


def read_stl(p):
    b = p.read_bytes()
    if b[:5] == b'solid' and b'facet' in b[:300]:
        v = [list(map(float, l.split()[1:4])) for l in b.decode().splitlines() if l.strip().startswith('vertex')]
        return np.array(v).reshape(-1, 3, 3)
    n = struct.unpack('<I', b[80:84])[0]
    a = np.frombuffer(b[84:84 + n * 50], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]))
    return a['v'].reshape(-1, 3, 3).astype(float)


def load(tag):
    out = []
    for e in idx[tag]:
        out.append((e['name'], e['kind'], read_stl(RD / e['file'])))
    return out


def draw(ax, parts, view, up=(0, 0, 1), xoff=0.0, light=(-0.4, -0.5, 0.8)):
    view = np.array(view, float); view /= np.linalg.norm(view)          # from the eye toward the scene
    upv = np.array(up, float)
    right = np.cross(view, upv); right /= np.linalg.norm(right)
    upv = np.cross(right, view)
    L = np.array(light, float); L /= np.linalg.norm(L)
    polys, cols, depth = [], [], []
    for name, kind, tri in parts:
        h = tri @ right + xoff
        v = tri @ upv
        d = tri @ view
        nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        ln = np.linalg.norm(nrm, axis=1); ok = ln > 1e-9
        nrm[ok] /= ln[ok, None]
        facing = nrm @ view
        shade = 0.42 + 0.58 * np.abs(nrm @ L)
        c = COL[kind][None, :] * shade[:, None]
        keep = ok
        polys.append(np.stack([h[keep], v[keep]], axis=-1)); cols.append(np.clip(c[keep], 0, 1)); depth.append(d[keep].mean(axis=1))
    P = np.concatenate(polys); C = np.concatenate(cols); D = np.concatenate(depth)
    order = np.argsort(-D)                                                # far first
    ax.add_collection(PolyCollection(P[order], facecolors=C[order], edgecolors=C[order] * 0.85, linewidths=0.15))
    return P


fig, axs = plt.subplots(1, 3, figsize=(19, 11), gridspec_kw={'width_ratios': [1, 1, 1]})
SIDE = (1, 0, 0)          # eye on -X looking +X: the pan servo arm faces you, camera on the RIGHT
panels = [('v1', 'v1 as built (mast top Z 130)'),
          ('v2', 'v2 (mast top Z 150, pivot over the mast)'),
          ('v2_tilt', 'v2 tilted camera-UP %d deg (v1 stopped near 30)' % VAL['render_tilt_camera_up_deg'])]
for ax, (tag, title) in zip(axs, panels):
    P = draw(ax, load(tag), SIDE)
    ax.set_title(title, fontsize=12)
    ax.set_aspect('equal')
    ax.set_xlim(-200, -10)
    ax.set_ylim(0, 330)
    ax.axhline(111.9, color='#c0392b', lw=1, ls='--')
    ax.text(-198, 114, 'hood top Z 111.9', color='#c0392b', fontsize=9)
    ax.grid(alpha=0.25)
    ax.set_xlabel('mm (world Y, flipped: camera side to the right)')
axs[0].set_ylabel('world Z, mm')
fig.text(0.5, 0.015, 'Orange = parts that change in v2 (reprint).  Grey = unchanged (re-used).  Blue = bought parts '
         '(servos, screen, ESP32-CAM, bearings).  Drawn from the CAD meshes.', ha='center', fontsize=11)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUTP / 'masthead_v1_vs_v2_side.png', dpi=110)

fig, ax = plt.subplots(figsize=(11, 11))
draw(ax, load('v2'), (0.75, 0.6, -0.45))
ax.set_aspect('equal'); ax.autoscale(); ax.axis('off')
ax.set_title('Masthead v2, 3D view (orange = new parts)', fontsize=13)
fig.tight_layout(); fig.savefig(OUTP / 'masthead_v2_iso.png', dpi=110)
print('ok')
