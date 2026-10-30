"""Top-view outlines on the yoke floor for the PCB envelope drawing (freecadcmd)."""
import FreeCAD as App, Part, json
V = App.Vector
B = "/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/"
d = App.openDocument(B + "balance-tensioner-20261030/Gladiator_Head_v2_Balanced.FCStd")
def outl(n, z):
    c = d.getObject(n).Shape.common(Part.makeBox(400, 400, 0.2, V(-150, -50, z)))
    out = []
    for f in c.Faces:
        if abs(f.normalAt(0, 0).z) < 0.9: continue
        for w in f.Wires:
            out.append([[p.x, p.y] for p in w.discretize(Deflection=0.05)])
    return out
res = {"floor": outl("Tilt_Yoke", 205.5), "columns": outl("Tilt_Yoke", 212.0),
       "tilt_servo": outl("SG90_Tilt_Reference", 250.0)}
json.dump(res, open(B + "power-bus-20261030/floor_polys.json", "w"))
print("ok", {k: len(v) for k, v in res.items()})
