import FreeCAD as App, Part, json
V = App.Vector
d = App.openDocument("/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/Gladiator_Head_v2_Mast.FCStd")
g = json.load(open("/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/validation.json"))["v2"]["groups"]
S = {n: d.getObject(n).Shape for k in g for n in g[k] if d.getObject(n)}
T = V(39.5, 113, 247.5); P = V(39.5, 113, 0)
y = S["Tilt_Yoke"]
print("yoke floor slice:")
for z in (200.6, 202, 204, 206, 208, 212, 216, 220):
    c = y.common(Part.makeBox(200, 200, 0.2, V(-60, 20, z)))
    print(" z %.1f" % z, [(round(s.BoundBox.XMin,1), round(s.BoundBox.XMax,1), round(s.BoundBox.YMin,1), round(s.BoundBox.YMax,1)) for s in c.Solids])
L, W, H, HP = 46.3, 35.5, 9.3, 21.5
def box(x0, x1, y0, y1, z0, z1): return Part.makeBox(x1-x0, y1-y0, z1-z0, V(x0, y0, z0))

cands = {
 "R1_side_-X":   box(-5.5-9.5, -5.5, 113-17, 113+17, 202.5, 202.5+HP),
 "R1_shelf":     box(-7.5-9.5, 12.5, 113-18, 113+18, 198.5, 202.5),
 "R2_side_+X":   box(86.0, 86.0+9.5, 113-17, 113+17, 202.5, 202.5+HP),
 "R2_shelf":     box(66.5, 88.0+9.5, 113-18, 113+18, 198.5, 202.5),
 "R3_rear":      box(39.5-17, 39.5+17, 155, 155+9.5, 202.5, 202.5+HP),
 "R3_shelf":     box(39.5-18, 39.5+18, 127, 157+9.5, 198.5, 202.5),
 "R4_floor_mid": box(41.0, 50.5, 113-17, 113+17, 204.5, 204.5+HP),
 "R4_floor_rear":box(41.0, 50.5, 117, 127, 204.5, 204.5+HP),
}
res = {}
for n, c in cands.items():
    stat = [k for k in g["pan"] if k in S and c.common(S[k]).Volume > 0.05]
    hits = {}
    for t in range(-90, 91, 2):
        for k in g["tilt"]:
            s = S[k].copy(); s.rotate(T, V(1,0,0), t)
            if c.common(s).Volume > 0.05: hits.setdefault(t, []).append(k)
    up = [t for t in hits if t < 0]; dn = [t for t in hits if t > 0]
    fixed = set()
    for p in range(-20, 181, 10):
        s = c.copy(); s.rotate(P, V(0,0,1), p)
        for k in g["fixed"]:
            if k in S and s.common(S[k]).Volume > 0.05: fixed.add(k)
    res[n] = dict(static=stat, first_up=max(up) if up else None, first_down=min(dn) if dn else None,
                  at0=hits.get(0), fixed=sorted(fixed))
    print(n, res[n])
