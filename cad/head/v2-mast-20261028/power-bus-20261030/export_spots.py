"""Export the two winning bus spots as meshes for the picture (freecadcmd)."""
import FreeCAD as App, Part, Mesh, os
V = App.Vector
OUT = os.path.dirname(os.path.abspath(__file__)) + "/spots"
os.makedirs(OUT, exist_ok=True)
def box(x0, x1, y0, y1, z0, z1): return Part.makeBox(x1-x0, y1-y0, z1-z0, V(x0, y0, z0))
L, W, HP = 46.3, 35.5, 21.5
sp = {
 "rail_R1":  box(-5.5-9.5, -5.5, 113-17, 113+17, 202.5, 202.5+9.3),
 "rail_R1_pins": box(-5.5-9.5, -5.5, 113-17, 113+17, 202.5+9.3, 202.5+HP),
 "rail_R1_shelf": box(-7.5-9.5, 12.5, 113-18, 113+18, 198.5, 202.5),
 "bb_A":  box(-6.0-W, -6.0, 113-L/2, 113+L/2, 202.5, 202.5+9.3),
 "bb_A_pins":  box(-6.0-W, -6.0, 113-L/2, 113+L/2, 202.5+9.3, 202.5+HP),
 "bb_A_shelf": box(-8.0-W, 12.5, 113-L/2-1, 113+L/2+1, 198.5, 202.5),
}
for n, s in sp.items():
    m = Mesh.Mesh(s.tessellate(0.1)); m.write(OUT + "/" + n + ".stl")
print("ok")
