"""Mast tube v2, SOLID (Jim 2026-11-01): lay-in slot removed, bottom wire window kept, matching window near the top.
Source: pcb-floor-20261030 tube (v2 tube + pan-lead notch). Run: python3 build_solid_tube.py (system python3, FreeCAD 1.0)."""
import sys, json, hashlib, os
sys.path.append("/usr/lib/freecad/lib")
from pathlib import Path
import FreeCAD as A, Part, Mesh, MeshPart
V = A.Vector
HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "pcb-floor-20261030/Gladiator_Head_v2_PCB_Floor.FCStd"
AX = V(39.5, 113.0, 0)                       # mast axis (world)
d = A.openDocument(str(SRC))
t0 = d.getObject("Mast_Tube_v2").Shape.copy()
assert abs(t0.BoundBox.ZMin - 6) < .01 and abs(t0.BoundBox.ZMax - 150) < .01

def box(x0, x1, y0, y1, z0, z1): return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, AX + V(x0, y0, z0))
ring = Part.makeCylinder(10, 144, AX + V(0, 0, 6)).cut(Part.makeCylinder(6, 146, AX + V(0, 0, 5)))
# 1) fill the rear lay-in slot (7 wide, -Y wall, Z 22..142) back to the plain 20/12 ring
fill = ring.common(box(-3.6, 3.6, -10.5, -4.0, 21.9, 142.1))
t1 = t0.fuse(fill).removeSplitter()
# 2) top wire window: same 10 x 12 as the bottom one (+Y wall, Z 24..36), at Z 90..102, inside the body
#    under the top panel (panel underside about Z 104, collar from Z 113)
WIN_TOP = (90.0, 102.0)
t2 = t1.cut(box(-5, 5, 0, 11, *WIN_TOP)).removeSplitter()
assert t2.isValid() and len(t2.Solids) == 1
R = {"source": str(SRC.relative_to(HERE.parent.parent.parent.parent)), "volume_before_mm3": round(t0.Volume, 1),
     "volume_after_mm3": round(t2.Volume, 1), "slot_filled_mm3": round(t1.Volume - t0.Volume, 1),
     "top_window_removed_mm3": round(t1.Volume - t2.Volume, 1), "top_window_world_z": WIN_TOP, "bottom_window_world_z": [24, 36]}
# slot really gone: no hole through the -Y wall anywhere from 22 to 142
R["rear_wall_open_mm3"] = round(ring.common(box(-3.5, 3.5, -10, -6, 22, 142)).cut(t2).Volume, 3)
# bottom window still open, top window open
for k, z0, z1 in (("bottom_window_open_mm3", 24, 36), ("top_window_open_mm3", *WIN_TOP)):
    R[k] = round(ring.common(box(-4.9, 4.9, 6.1, 10, z0 + .1, z1 - .1)).cut(t2).Volume, 1)
# everything else unchanged: the only differences are inside the slot and the new window
diff = t0.cut(t2).fuse(t2.cut(t0))
R["changes_outside_slot_and_window_mm3"] = round(diff.cut(box(-3.6, 3.6, -10.5, -4.0, 21.9, 142.1)).cut(box(-5, 5, 0, 11, *WIN_TOP)).Volume, 3)
# clash with every other part at the saved pose
hits = {}
for o in d.Objects:
    if o.TypeId == "Part::Feature" and o.Name != "Mast_Tube_v2" and o.Shape.Solids and o.Shape.BoundBox.intersect(t2.BoundBox):
        v0, v2 = o.Shape.common(t0).Volume, o.Shape.common(t2).Volume
        if v2 > 0.01 or v0 > 0.01: hits[o.Name] = [round(v0, 2), round(v2, 2)]
R["overlap_before_after_mm3"] = hits
R["mass_g_pla_solid_est"] = [round(t0.Volume * 1.24e-3, 2), round(t2.Volume * 1.24e-3, 2)]
# export at the origin, print pose (bottom on the bed)
p = t2.copy(); p.translate(V(-AX.x, -AX.y, -6.0))
p.exportStep(str(HERE / "Mast_Tube_v2_Solid.step"))
m = MeshPart.meshFromShape(Shape=p, LinearDeflection=0.02, AngularDeflection=0.2, Relative=False)
m.write(str(HERE / "stl/Gladiator_Head_v2_Mast_Tube_v2_Solid.stl"))
R["stl_closed"] = bool(m.isSolid()) and not m.hasNonManifolds()
R["stl_sha256"] = hashlib.sha256((HERE / "stl/Gladiator_Head_v2_Mast_Tube_v2_Solid.stl").read_bytes()).hexdigest()
(HERE / "validation.json").write_text(json.dumps(R, indent=1))
print(json.dumps(R, indent=1), flush=True)
os._exit(0)
