import sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
src = (HERE.parent / "render.py").read_text().split("fig, axs = plt.subplots")[0]
sys.argv = ["x", str(HERE.parent / "render"), str(HERE.parent / "validation.json"), str(HERE)]
exec(src)
COL["rail"] = np.array([0.85, 0.15, 0.15]); COL["pins"] = np.array([0.98, 0.80, 0.25]); COL["drv"] = np.array([0.1, 0.1, 0.9])
head = [p for p in load("v2") if p[1] != "context" and p[2][:, :, 2].max() > 165]
L = lambda n, k: (n, k, read_stl(HERE / "spots" / (n + ".stl")))
fig, axs = plt.subplots(1, 2, figsize=(17, 8.5))
ax = axs[0]; draw(ax, head + [L("S1", "rail"), L("S1_pins", "pins"), L("S1_driver", "drv")], (1, 0, 0))
ax.set_title("1) Side window of the screen frame (seen from the side opposite the camera)\n"
             "48 mm rail in the 50 x 24 opening. Blue = screwdriver path to the tilt horn screw", fontsize=11)
ax.set_xlim(-175, -40); ax.set_ylim(195, 300)
ax = axs[1]; draw(ax, head + [L("S2", "rail"), L("S2_pins", "pins")], (0, -1, 0))
ax.set_title("2) Brim on top of the screen bezel (seen from the screen side)", fontsize=11)
ax.set_xlim(-95, 20); ax.set_ylim(195, 300)
for a in axs: a.set_aspect("equal"); a.grid(alpha=0.25)
fig.text(0.5, 0.02, "Red = rail (or a small PCB), yellow = plugged-in Dupont leads. Both ride on the tilting head and clear every tilt/pan pose. "
         "Drawn on the v2 baseline (Codex balanced receiver shifts the head 2.5 mm; sweep used the balanced model).", ha="center", fontsize=10)
fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(HERE / "power_bus_recess.png", dpi=100); print("ok")
