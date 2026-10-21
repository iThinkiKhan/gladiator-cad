"""Upper deck v5 (2026-10-19): deeper deck-screw pockets for the driver mounts.

Derived from the saved v4 deck solid; everything else is identical to v4.

The v5d driver base sinks the deck-screw head 3.3 mm into the foot, so the screw
tip now reaches 3.3 mm lower than before.  An M3 x 10 from the recess floor
(foot underside = boss top Z64.5, + 0.7 mm floor = Z65.2) ends at Z55.2, but the v4 pocket
floor is at Z57.0.  A D3.6 relief hole is added under the D4.6 insert pocket,
down to Z55.0 (0.5 mm skin over the Z54.5 underside).  The insert pocket itself
(D4.6, 7.5 deep, insert 7.05 long) is unchanged, so inserts set exactly as before.
For an already printed v4 deck: drill a 3 mm hole through the insert bore to 9.5 mm below the boss top.
"""
import FreeCAD as A, Part, MeshPart, json
from pathlib import Path

V = A.Vector
R = Path('/home/buralien/projects/gladiator-cad/cad/v2/upper-deck')
SRC = R / 'v4-20261016/Gladiator_UpperDeck_v4.FCStd'
O = R / 'v5-20261019'
O.mkdir(exist_ok=True)

BOSSES = [(14.5, 95.0), (14.5, 135.0), (64.5, 95.0), (64.5, 135.0)]
POCKET_FLOOR, RELIEF_D, RELIEF_FLOOR = 57.0, 3.6, 55.0
BOSS_TOP = 64.5
SCREW_TIP = {8: BOSS_TOP + 0.7 - 8, 10: BOSS_TOP + 0.7 - 10}   # head floor Z65.2

d = A.openDocument(str(SRC))
deck = d.getObject('UpperDeck_v4').Shape.copy()
v4 = deck.Volume
for x, y in BOSSES:
    deck = deck.cut(Part.makeCylinder(RELIEF_D / 2, POCKET_FLOOR - RELIEF_FLOOR + 0.3, V(x, y, RELIEF_FLOOR)))
deck = deck.removeSplitter()


def solid_at(x, y, z, r):
    return deck.common(Part.makeCylinder(r, 0.1, V(x, y, z))).Volume > 0.5 * 3.14159 * r * r * 0.1


chk = {
    'valid_single': deck.isValid() and len(deck.Solids) == 1,
    'removed_mm3': round(v4 - deck.Volume, 2),
    'volume_cm3': round(deck.Volume / 1000, 2),
    'skin_under_relief_mm': round(RELIEF_FLOOR - 54.5, 2),
    'insert_pocket_unchanged_probe_Z60_r2': [not solid_at(x, y, 60.0, 2.0) for x, y in BOSSES],
    'ring_around_pocket_solid_Z60_r3.5': [solid_at(x + 3.5, y, 60.0, 0.3) for x, y in BOSSES],
    'relief_open_Z56': [not solid_at(x, y, 56.0, 1.0) for x, y in BOSSES],
    'skin_solid_Z54.7': [solid_at(x, y, 54.7, 1.0) for x, y in BOSSES],
    'screw_tip_Z_and_spare_to_floor_mm': {str(k): [round(v, 2), round(v - RELIEF_FLOOR, 2)] for k, v in SCREW_TIP.items()},
}
print(json.dumps(chk, indent=1))
assert chk['valid_single'] and all(chk['relief_open_Z56']) and all(chk['skin_solid_Z54.7']) and all(chk['insert_pocket_unchanged_probe_Z60_r2'])

nd = A.newDocument('UpperDeck_v5')
o = nd.addObject('Part::Feature', 'UpperDeck_v5')
o.Shape = deck
nd.recompute()
nd.saveAs(str(O / 'Gladiator_UpperDeck_v5.FCStd'))
Part.export([o], str(O / 'Gladiator_UpperDeck_v5.step'))
s = deck.copy()
MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.0872665, Relative=False).write(str(O / 'Gladiator_UpperDeck_v5.stl'))
(O / 'validation.json').write_text(json.dumps(chk, indent=2) + '\n')
(O / 'README.md').write_text(__doc__ + '\nValidation: validation.json\n')
print('saved')
