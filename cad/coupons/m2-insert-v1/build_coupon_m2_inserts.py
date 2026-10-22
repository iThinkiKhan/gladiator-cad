"""Coupon M2-A: M2 heat-set insert bores (2026-10-21, Claude).

Run: freecadcmd build_coupon_m2_inserts.py

Jim 2026-10-21: M2 heat-set inserts from now on in every print. Like coupon A did for the M3 inserts (4.6 won), this finds the M2 bore on this printer
(round features print about 0.25 under, see measurements/printer-calibration.md), in BOTH directions the inserts will sit:
  * front row: six upright bosses (bore axis vertical, like the speaker pads and any boss that prints standing up)
  * back wall: six horizontal bores (axis along Y, like the INA bosses and the switch holder side screws, which print lying down; their tops are bridges)
Nominal bores 2.8 / 3.0 / 3.2 / 3.4 / 3.6 / 3.8 mm, LEFT to RIGHT (the clipped corner is at the 2.8 end), 6.0 mm deep: enough for a 3, 4 or 5 mm long insert.
Insert OD and length are not known yet; common M2 inserts are 3.2 to 3.6 across.
"""
import FreeCAD as A, Part, MeshPart, math, json, os
from pathlib import Path

V = A.Vector
O = Path('/home/buralien/projects/gladiator-cad/cad/coupons/m2-insert-v1')
O.mkdir(parents=True, exist_ok=True)

BORES = [2.8, 3.0, 3.2, 3.4, 3.6, 3.8]
PITCH, X0 = 9.5, 6.25
PW, PD, PT = 60.0, 30.0, 3.0          # base plate
BOSS_D, BOSS_H, DEPTH = 7.0, 6.0, 6.0
BOSS_Y = 8.0
WALL_Y, WALL_Z, HZ = (19.0, 30.0), 13.0, 8.0     # back wall, bore centre height

s = Part.makeBox(PW, PD, PT)
s = s.fuse(Part.makeBox(PW, WALL_Y[1] - WALL_Y[0], WALL_Z, V(0, WALL_Y[0], 0)))
cuts = []
for i, d in enumerate(BORES):
    x = X0 + i * PITCH
    s = s.fuse(Part.makeCylinder(BOSS_D / 2, BOSS_H, V(x, BOSS_Y, PT)))
    cuts.append(Part.makeCylinder(d / 2, DEPTH + 0.1, V(x, BOSS_Y, PT + BOSS_H - DEPTH)))                 # upright bore from the boss top
    cuts.append(Part.makeCylinder(d / 2, DEPTH + 0.1, V(x, WALL_Y[1] + 0.1, HZ), V(0, -1, 0)))          # horizontal bore from the back face
s = s.removeSplitter()
for c in cuts:
    s = s.cut(c)
tri = Part.makePolygon([V(0, 0, -1), V(5, 0, -1), V(0, 5, -1), V(0, 0, -1)])
s = s.cut(Part.Face(tri).extrude(V(0, 0, 30)))                    # clipped corner at the 2.8 end
s = s.removeSplitter()

chk = dict(bores_left_to_right=BORES, depth_mm=DEPTH, upright_boss_d=BOSS_D, wall_bore_centre_z=HZ,
           valid=s.isValid(), solids=len(s.Solids), volume_mm3=round(s.Volume, 1), grams=round(s.Volume * 1.24e-3, 1),
           min_wall_around_largest_upright_bore_mm=round((BOSS_D - max(BORES)) / 2, 2),
           wall_over_horizontal_bores_mm=round(WALL_Z - HZ - max(BORES) / 2, 2), wall_under_horizontal_bores_mm=round(HZ - max(BORES) / 2, 2))
doc = A.newDocument('Gladiator_Coupon_M2_Inserts')
o = doc.addObject('Part::Feature', 'Coupon_M2_Inserts')
o.Shape = s
doc.recompute()
doc.saveAs(str(O / 'Gladiator_Coupon_M2_Inserts.FCStd'))
m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.05, Relative=False)
m.write(str(O / 'Gladiator_Coupon_M2_Inserts.stl'))
bb = s.BoundBox
chk['stl'] = dict(is_solid=m.isSolid(), non_manifold=m.hasNonManifolds(), size_mm=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
                  orientation='plate down as modelled, no supports (the horizontal bores bridge, as they will in real parts)')
(O / 'validation.json').write_text(json.dumps(chk, indent=1))
print(json.dumps(chk, indent=1), flush=True)
os._exit(0)
