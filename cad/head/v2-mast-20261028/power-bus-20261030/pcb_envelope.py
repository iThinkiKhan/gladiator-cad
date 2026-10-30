"""Draft PCB envelope on the yoke floor (system python3). Proposal only, nothing modelled."""
import json
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
H = Path(__file__).resolve().parent
low = np.load(H / "lowenv.npy") - 206.0            # free height above the floor top, worst over tilt -38..34
P = json.loads((H / "floor_polys.json").read_text())
xs = np.arange(0, 84, 2.0); ys = np.arange(84, 146, 2.0)
fig, ax = plt.subplots(figsize=(13, 9.5))
im = ax.pcolormesh(np.append(xs, xs[-1] + 2), np.append(ys, ys[-1] + 2), np.clip(low, 0, 40).T, cmap="RdYlGn", vmin=0, vmax=30, alpha=0.55, shading="flat")
cb = fig.colorbar(im, ax=ax, shrink=0.8); cb.set_label("free height above the yoke floor top, mm (worst case over all tilt; 30+ = green)")
for w in P["floor"]: ax.add_patch(Polygon(w, closed=True, fill=False, ec="k", lw=1.2))
for w in P["columns"]: ax.add_patch(Polygon(w, closed=True, fc="#888", ec="k", lw=1, alpha=0.9))
for w in P["tilt_servo"]: ax.add_patch(Polygon(w, closed=True, fill=False, ec="#2255aa", lw=1, ls="--"))
for sx in (-1, 1):
    for sy in (-1, 1):
        ax.add_patch(Circle((39.5 + 13.3 * sx, 113 + 13.3 * sy), 3.5, fill=False, ec="purple", lw=1.5))
ax.add_patch(Rectangle((40.3, 107), 5.7, 12, fc="none", ec="blue", lw=2, hatch="///"))
bx0, bx1, by0, by1 = 40.6, 61.9, 97.0, 122.5
ax.add_patch(Rectangle((bx0, by0), bx1 - bx0, by1 - by0, fc="none", ec="red", lw=2.5))
ax.add_patch(Rectangle((bx0, 109), bx1 - bx0, 10, fc="red", alpha=0.12, ec="none"))
ax.add_patch(Circle((52.8, 99.7), 4.0, fc="white", ec="red", lw=1.5))
for p in ((44.0, 99.5), (58.8, 119.8)): ax.add_patch(Circle(p, 1.4, fc="k"))
ax.annotate("", xy=(41.5, 113), xytext=(33.5, 113), arrowprops=dict(arrowstyle="->", color="#2255aa", lw=2))
T = lambda x, y, s, **k: ax.text(x, y, s, **{"fontsize": 9, **k})
T(62.5, 123.5, "PCB about 21 x 25 (red)", color="red", weight="bold")
T(41, 110.5, "connector band\nY 109-119: 30+ mm", color="darkred")
T(41, 102.5, "low parts\n<= 4 mm above\nboard", color="darkred")
T(47, 120.0, "board only", color="darkred", fontsize=8)
T(48.0, 93.6, "notch: driver to the\nretainer screw", color="purple", fontsize=8)
T(12.8, 104.5, "tilt servo lead comes\ndown the ear column,\nslips under the board edge\ninto the wire passage", color="#2255aa", fontsize=8)
T(46.5, 107.6, "wire passage\n(trunk + tilt lead)", color="blue", fontsize=8)
T(62.3, 99.0, "2 x M2 heat-set\n(black dots)", fontsize=8)
T(10.5, 89.0, "Front right (X 50-62, Y < 97): the camera case sweeps to ~2 mm above the floor at 34 deg camera-down, so the board stops at Y 97.\n"
  "A 2 mm pocket in the floor for the board gains 2 mm everywhere.", fontsize=8, color="k", backgroundcolor="white")
T(12.8, 128.5, "purple circles = driver holes to the 4 pan retainer screws (keep open)", color="purple", fontsize=8)
ax.set_xlim(10, 76); ax.set_ylim(88, 132); ax.set_aspect("equal"); ax.grid(alpha=0.2)
ax.set_xlabel("world X, mm (camera case on the right)"); ax.set_ylabel("world Y, mm (camera at the bottom, screen at the top)")
ax.set_title("Masthead v2 yoke floor, top view: draft envelope for the head distro PCB (PROPOSAL, not modelled)\n"
             "Grey = yoke columns, dashed blue = tilt servo above. Floor top Z 206; tilt pivot directly over Y 113.", fontsize=11)
fig.tight_layout(); fig.savefig(H / "pcb_envelope_on_yoke_floor.png", dpi=110); print("ok")
