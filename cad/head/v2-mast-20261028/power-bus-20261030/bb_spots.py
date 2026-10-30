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
 "A_side_flat_-X":  box(-6.0-W, -6.0, 113-L/2, 113+L/2, 202.5, 202.5+HP),
 "A_shelf":         box(-8.0-W, 12.5, 113-L/2-1, 113+L/2+1, 198.5, 202.5),
 "B_side_vert_-X":  box(-6.0-HP, -6.0, 113-L/2, 113+L/2, 198.0, 198.0+W),
 "C_rear_flat":     box(39.5-L/2, 39.5+L/2, 156, 156+W, 202.5, 202.5+HP),
 "C_shelf":         box(39.5-L/2-1, 39.5+L/2+1, 127, 158+W, 198.5, 202.5),
 "D_side_flat_+X":  box(86.0, 86.0+W, 113-L/2, 113+L/2, 202.5, 202.5+HP),
 "D_shelf":         box(66.5, 88.0+W, 113-L/2-1, 113+L/2+1, 198.5, 202.5),
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
