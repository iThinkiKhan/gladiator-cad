"""Recessed spots for a cut breadboard power rail (2 rows x 3 groups of 5, taken as 48 x 9.5 x 9.3; Dupont
leads plugged in reach 21.5 total). Base: Codex balanced v2. Sweeps: tilt -38..34 every 2 at pan -20..180 every 20."""
import FreeCAD as App, Part, json
V = App.Vector
BASE = "/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/"
d = App.openDocument(BASE + "balance-tensioner-20261030/Gladiator_Head_v2_Balanced.FCStd")
g = json.load(open(BASE + "validation.json"))["v2"]["groups"]
g["fixed"] += ["Tensioner_M3x20_Envelope", "Tensioner_Nut_Envelope"]
S = {n: d.getObject(n).Shape for k in g for n in g[k] if d.getObject(n)}
T = V(39.5, 113, 247.5); P = V(39.5, 113, 0)
RL, RW, RH, HP = 48.0, 9.5, 9.3, 21.5
def box(x0, x1, y0, y1, z0, z1): return Part.makeBox(x1-x0, y1-y0, z1-z0, V(x0, y0, z0))
spots = {   # name: (rail body, lead space, rides on)
 "S1_screen_side_window": (box(1.0, 1.0+RH, 113-RL/2, 113+RL/2, 247.5-RW/2, 247.5+RW/2),
                           box(1.0-(HP-RH), 1.0, 113-RL/2, 113+RL/2, 247.5-RW/2, 247.5+RW/2), "tilt"),
 "S2_screen_top_brim":    (box(39.5-RL/2, 39.5+RL/2, 138.2, 147.7, 269.5, 269.5+RH),
                           box(39.5-RL/2, 39.5+RL/2, 138.2, 147.7, 269.5+RH, 269.5+HP), "tilt"),
 "S3_collar_side":        (box(24.5-RH, 24.5, 113-RW/2, 113+RW/2, 113.0, 113.0+RL),
                           box(24.5-HP, 24.5-RH, 113-RW/2, 113+RW/2, 113.0, 113.0+RL), "fixed"),
}
out = {}
for n, (body, leads, ride) in spots.items():
    env = body.fuse(leads)
    own = set(g[ride])
    stat = sorted(k for k in S if k not in own and env.common(S[k]).Volume > 0.05)
    hits = set()
    for pan in range(-20, 181, 20):
        for t in range(-38, 35, 2):
            def pose(s, grp):
                s = s.copy()
                if grp == "tilt": s.rotate(T, V(1,0,0), t)
                if grp in ("tilt", "pan"): s.rotate(P, V(0,0,1), pan)
                return s
            e = pose(env, ride)
            for k in S:
                if k in own: continue
                grp = next(gg for gg in g if k in g[gg])
                if e.common(pose(S[k], grp)).Volume > 0.05: hits.add((k, pan, t))
    first = sorted({k for k, _, _ in hits})
    out[n] = dict(home_overlap=stat, motion_hits=first, n_hit_poses=len(hits))
    print(n, out[n])
# tilt horn screw path: is there a screwdriver path along +X to the spline end at the tilt axis?
line = Part.makeCylinder(1.5, 60, V(-30, 113, 247.5), V(1, 0, 0))
for k in ("Rear_Display_Frame", "GH44_Tilt_Receiver", "Tilt_Horn_Reference", "SG90_Tilt_Reference", "GH44_Dual_Carrier"):
    c = line.common(S[k])
    print("driver line vs", k, round(c.Volume, 1), [round(c.BoundBox.XMin, 1), round(c.BoundBox.XMax, 1)] if c.Volume > 0 else "")
json.dump(out, open(BASE + "power-bus-20261030/recess_spots.json", "w"), indent=1)
