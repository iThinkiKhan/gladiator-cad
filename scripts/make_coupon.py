import os
import FreeCAD as App
import Part
import Mesh

OUT = '/home/buralien/projects/gladiator-cad/cad/coupons'
if not os.path.isdir(OUT):
    os.makedirs(OUT)

# ---------------------------------------------------------------- plate
PW, PD, PT = 80.0, 52.0, 4.0          # overall size is itself the calibration reference
solid = Part.makeBox(PW, PD, PT)

cuts = []

# ---------------------------------------------------------------- A: heat-set insert bores
# Reproduces the real deck-boss stack exactly: 9 dia boss, 6 tall, on 4 of plate = 10 of
# material, bored 7.5 deep -> 2.5 of floor left, same as UpperDeck's S3/driver bosses.
BOSS_X = [10.0, 23.0, 36.0, 49.0]
BOSS_Y = 12.0
BORES = [4.0, 4.2, 4.4, 4.6]
for x, d in zip(BOSS_X, BORES):
    solid = solid.fuse(Part.makeCylinder(4.5, 6.0, App.Vector(x, BOSS_Y, PT)))
    cuts.append(Part.makeCylinder(d / 2.0, 7.5, App.Vector(x, BOSS_Y, PT + 6.0 - 7.5)))

# ---------------------------------------------------------------- B: mast-base spigot pegs
# The real spigot is 13.8 into the aluminium deck's existing 14.0 hole, protruding 7 with
# only 1 mm to the motor underneath. Try these in the real hole before printing MastBase.
PEG_X = [12.0, 30.0, 48.0]
PEG_Y = 32.0
PEGS = [13.6, 13.8, 14.0]
for x, d in zip(PEG_X, PEGS):
    solid = solid.fuse(Part.makeCylinder(d / 2.0, 7.0, App.Vector(x, PEG_Y, PT)))

# ---------------------------------------------------------------- index pips
def pips(cx, y, n):
    out = []
    for j in range(n):
        off = (j - (n - 1) / 2.0) * 3.5
        out.append(Part.makeCylinder(1.0, PT + 2, App.Vector(cx + off, y, -1)))
    return out

for i, x in enumerate(BOSS_X):
    cuts += pips(x, 4.0, i + 1)
for i, x in enumerate(PEG_X):
    cuts += pips(x, 21.0, i + 1)

# ---------------------------------------------------------------- C: screw clearance holes
# through the full 4 mm, same as the real deck
for x, d in zip([8.0, 16.0, 24.0], [3.2, 3.4, 3.6]):          # M3
    cuts.append(Part.makeCylinder(d / 2.0, PT + 2, App.Vector(x, 46.0, -1)))
for x, d in zip([36.0, 44.0, 52.0], [2.2, 2.4, 2.6]):         # M2
    cuts.append(Part.makeCylinder(d / 2.0, PT + 2, App.Vector(x, 46.0, -1)))

# ---------------------------------------------------------------- D: rail foot adjustment slot
# 3.4 wide with 3.0 of travel, as built into the rail feet. Check an M3 screw AND nut.
cuts.append(Part.makeBox(3.4, 6.4, PT + 2, App.Vector(68.0 - 1.7, 44.0 - 3.2, -1)))

for c in cuts:
    solid = solid.cut(c)

doc = App.newDocument('Gladiator_FitCoupon_v1')
obj = doc.addObject('Part::Feature', 'FitCoupon')
obj.Label = 'Gladiator fit + calibration coupon v1'
obj.Shape = solid
doc.recompute()

print('valid=%s solids=%d vol=%.0f mm3 (~%.0f g PLA)'
      % (solid.isValid(), len(solid.Solids), solid.Volume, solid.Volume / 1000.0 * 1.24))
print('bbox:', solid.BoundBox)

doc.saveAs(os.path.join(OUT, 'Gladiator_FitCoupon_v1.FCStd'))
Part.export([obj], os.path.join(OUT, 'Gladiator_FitCoupon_v1.step'))
Mesh.export([obj], os.path.join(OUT, 'Gladiator_FitCoupon_v1.stl'))
print('wrote FCStd / step / stl to', OUT)

# ---------------------------------------------------------------- verify every feature landed
print()
print('=== verification ===')
cyl = {}
for f in solid.Faces:
    if f.Surface.TypeId != 'Part::GeomCylinder':
        continue
    d = round(f.Surface.Radius * 2, 2)
    cyl[d] = cyl.get(d, 0) + 1
print('round features by diameter:')
for d in sorted(cyl):
    print('   d%.2f  x%d' % (d, cyl[d]))

print()
print('insert bore floors (should all be 2.50):')
for x, d in zip(BOSS_X, BORES):
    z = PT + 6.0 - 7.5
    while z > -1 and not solid.isInside(App.Vector(x, BOSS_Y, z), 1e-7, True):
        z -= 0.05
    print('   bore d%.1f at X%.0f: solid from Z=%.2f -> floor %.2f' % (d, x, z, z))

print()
print('peg heights (should be 11.0 = 4 plate + 7 peg):')
for x, d in zip(PEG_X, PEGS):
    z = 12.0
    while z > 0 and not solid.isInside(App.Vector(x, PEG_Y, z), 1e-7, True):
        z -= 0.05
    print('   peg d%.1f at X%.0f: top at Z=%.2f' % (d, x, z))
