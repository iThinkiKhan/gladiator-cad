import FreeCAD as App, Part, json
import numpy as np
V = App.Vector
B = "/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/"
d = App.openDocument(B + "balance-tensioner-20261030/Gladiator_Head_v2_Balanced.FCStd")
g = json.load(open(B + "validation.json"))["v2"]["groups"]
sh = lambda n: d.getObject(n).Shape
def sl(n, z):
    c = sh(n).common(Part.makeBox(400, 400, 0.2, V(-150, -50, z)))
    return sorted([(round(s.BoundBox.XMin,1), round(s.BoundBox.XMax,1), round(s.BoundBox.YMin,1), round(s.BoundBox.YMax,1)) for s in c.Solids])
print("== pan side, Z 140..185")
for z in (140, 145, 148, 151, 153, 155, 158, 162, 166):
    print(z, "neck", sl("Neck_Main", z), "| car", sl("Pan_Servo_Carriage", z), "| sg90", sl("SG90_Pan_Reference", z), "| tube", sl("Mast_Tube_v2", z))
b = sh("SG90_Pan_Reference").BoundBox; print("sg90 bbox", b)
# yoke floor holes at z 203
f = sh("Tilt_Yoke").common(Part.makeBox(200, 200, 0.2, V(-50, 0, 203.0)))
face = [fc for fc in f.Faces if abs(fc.normalAt(0, 0).z) > 0.9][0]
print("== yoke floor outer", [round(v, 1) for v in (face.BoundBox.XMin, face.BoundBox.XMax, face.BoundBox.YMin, face.BoundBox.YMax)])
for w in face.Wires:
    if w.isSame(face.OuterWire): continue
    bb = w.BoundBox; print(" hole X %.1f..%.1f Y %.1f..%.1f" % (bb.XMin, bb.XMax, bb.YMin, bb.YMax))
# lower envelope of the tilting parts over the floor: min Z per 2 mm cell over tilt -38..34
T = np.array([39.5, 113, 247.5])
pts = []
for n in g["tilt"]:
    o = d.getObject(n)
    if not o: continue
    v, t = o.Shape.tessellate(0.3); v = np.array([[p.x, p.y, p.z] for p in v]); t = np.array(t)
    for k in range(8):
        for l in range(8 - k):
            a, bb_ = (k + 0.5) / 8, (l + 0.5) / 8
            pts.append(v[t[:, 0]] * (1 - a - bb_) + v[t[:, 1]] * a + v[t[:, 2]] * bb_)
P = np.concatenate(pts)
xs = np.arange(0, 84, 2.0); ys = np.arange(84, 146, 2.0)
low = np.full((len(xs), len(ys)), 999.0)
for ang in range(-38, 35, 1):
    r = np.radians(ang); c, s = np.cos(r), np.sin(r)
    y = T[1] + (P[:, 1] - T[1]) * c - (P[:, 2] - T[2]) * s
    z = T[2] + (P[:, 1] - T[1]) * s + (P[:, 2] - T[2]) * c
    ix = ((P[:, 0] - xs[0]) // 2).astype(int); iy = ((y - ys[0]) // 2).astype(int)
    ok = (ix >= 0) & (ix < len(xs)) & (iy >= 0) & (iy < len(ys))
    np.minimum.at(low, (ix[ok], iy[ok]), z[ok])
np.save("/home/buralien/scratch_claude/lowenv.npy", low)
print("== free height above the floor top (Z 206) by cell, X rows 12..72, Y cols 92..126")
print("     Y:" + "".join("%5d" % y for y in ys if 90 <= y <= 128))
for i, x in enumerate(xs):
    if 10 <= x <= 74:
        print("X%4d " % x + "".join("%5.0f" % (low[i, j] - 206) for j, y in enumerate(ys) if 90 <= y <= 128))
