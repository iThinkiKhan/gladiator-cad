"""Picture of the two power-bus spots on the v2 head (system python3)."""
import sys, json
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
src = (HERE.parent / "render.py").read_text().split("fig, axs = plt.subplots")[0]
sys.argv = ["x", str(HERE.parent / "render"), str(HERE.parent / "validation.json"), str(HERE)]
exec(src)
COL["rail"] = np.array([0.85, 0.15, 0.15]); COL["pins"] = np.array([0.98, 0.80, 0.25]); COL["shelf"] = np.array([0.20, 0.65, 0.35])
head = [p for p in load("v2") if p[1] != "context" and p[2][:, :, 2].max() > 165]
def spot(tag):
    o = []
    for n, k in ((tag, "rail"), (tag + "_pins", "pins"), (tag + "_shelf", "shelf")):
        o.append((n, k, read_stl(HERE / "spots" / (n + ".stl"))))
    return o
fig, axs = plt.subplots(2, 2, figsize=(16, 15))
for row, (tag, title) in enumerate((("rail_R1", "A) cut-down power rail (34 mm, 2 x 10 holes): shelf sticks out 30 mm"),
                                    ("bb_A", "B) full mini breadboard (46 x 36): shelf sticks out 56 mm"))):
    parts = head + spot(tag)
    ax = axs[row][0]; draw(ax, parts, (0, 1, 0))
    ax.set_title(title + "\nseen from the camera side", fontsize=11)
    ax.set_xlim(-95, 115); ax.set_ylim(160, 290)
    ax = axs[row][1]; draw(ax, parts, (0, 0, -1), up=(0, 1, 0))
    ax.set_title("top view (camera at the bottom)", fontsize=11)
    ax.set_xlim(-95, 115); ax.set_ylim(35, 165)
    for a in axs[row]: a.set_aspect("equal"); a.grid(alpha=0.25)
fig.text(0.5, 0.012, "Red = bus board, yellow = space for plugged-in Dupont leads (21.5 mm total, from your deck breadboard), "
         "green = new shelf on the yoke floor (turns with pan). Orange/grey/blue = v2 head. Both spots: no change to tilt (38 up / 34 down) "
         "or pan.", ha="center", fontsize=10.5, wrap=True)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(HERE / "power_bus_spots.png", dpi=100); print("ok")
