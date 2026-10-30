import FreeCAD as App, Part, Mesh, os
V = App.Vector
OUT = os.path.dirname(os.path.abspath(__file__)) + "/spots"
def box(x0, x1, y0, y1, z0, z1): return Part.makeBox(x1-x0, y1-y0, z1-z0, V(x0, y0, z0))
RL, RW, RH, HP = 48.0, 9.5, 9.3, 21.5
sp = {"S1": box(1.0, 1.0+RH, 113-RL/2, 113+RL/2, 247.5-RW/2, 247.5+RW/2),
      "S1_pins": box(1.0-(HP-RH), 1.0, 113-RL/2, 113+RL/2, 247.5-RW/2, 247.5+RW/2),
      "S1_driver": Part.makeCylinder(1.5, 50, V(-30, 113, 247.5), V(1, 0, 0)),
      "S2": box(39.5-RL/2, 39.5+RL/2, 138.2, 147.7, 269.5, 269.5+RH),
      "S2_pins": box(39.5-RL/2, 39.5+RL/2, 138.2, 147.7, 269.5+RH, 269.5+HP)}
for n, s in sp.items(): Mesh.Mesh(s.tessellate(0.1)).write(OUT + "/" + n + ".stl")
