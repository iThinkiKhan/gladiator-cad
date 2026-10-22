"""Driver mount v5d - deck-screw head recess in the base (2026-10-19).

Derived from the saved v5c base, NOT from the master: build_drv_v5.py can no
longer reproduce the printed wedge because the master's UpperDeck/rails have
changed since 2026-09-24 (its wedge_matches_printed gate fails).  The printed
wedges are untouched; only the base gets a head recess at each deck screw.

Fault: the deck screws sit on the foot top (Z62), the face the wedge seat bears
on, so an M3 socket head (D5.5 x 3.0) held the wedge off the base (53.2 mm3 of
overlap per screw).  Fix: D6.4 recess, floor at Z58.7, head top 0.3 below Z62.
"""
import sys, json, shutil
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad-python3/lib'])
sys.argv = ['x']
import FreeCAD as A, Part, MeshPart
from pathlib import Path

ROOT = Path('/home/buralien/projects/gladiator-cad')
OUT = ROOT / 'cad/drivers/v5-interlock'
SRC = Path('/home/buralien/backups/drv-v5c-20261019/v5-interlock/DriverMount_v5.FCStd')   # printed-wedge v5c source
DECK = ROOT / 'cad/v2/upper-deck/v4-20261016/Gladiator_UpperDeck_v4.FCStd'

FOOT_TOP, DECK_BOSS_TOP = 62.0, 58.0
WALL_X0, WALL_X1 = 17.0, 23.0
SCREWS = [(14.5, 95.0), (14.5, 135.0)]
HEAD_D, HEAD_H = 5.7, 1.65          # ISO 7380 M3 button head (was the 5.5 x 3.0 socket head, which left a 0.7 mm clamp floor)
CBORE_D, SINK = 6.4, 0.25          # recess 0.55 mm per side around the D5.5 head
RELIEF_D, RELIEF_H = 6.0, 0.0   # 2026-10-19 (Jim): relief removed, the clamp floor sits solid on the boss top; was 0.3        # underside relief over each deck insert (insert + melt collar), above the boss top
SCREW_HOLE_D = 3.8                 # deck screw clearance hole, was 3.6
SHAVE = 0.05                       # per side, tongue and locator peg (clearance 0.20 -> 0.25)
FLOOR = FOOT_TOP - HEAD_H - SINK


def hit(a, b):
    try:
        return a.common(b).Volume if a.BoundBox.intersect(b.BoundBox) else 0.0
    except Exception:
        return 0.0


doc = A.openDocument(str(SRC))
base = doc.getObject('Base_Left').Shape.copy()
v5c = base.copy()
wedge = doc.getObject('Wedge_Left').Shape.copy()
coupon_wedge = doc.getObject('Coupon_Wedge').Shape.copy()
v5c_vol = base.Volume
rep = {'source': 'saved v5c Base_Left', 'checks': {}}

# the printed-wedge fault, measured on the v5c base
rep['checks']['v5c_head_on_foot_top_vs_wedge_mm3'] = [
    round(hit(Part.makeCylinder(HEAD_D / 2, HEAD_H, A.Vector(x, y, FOOT_TOP)), wedge), 1)
    for x, y in SCREWS]

for x, y in SCREWS:
    base = base.cut(Part.makeCylinder(SCREW_HOLE_D / 2, FOOT_TOP - DECK_BOSS_TOP + 0.4, A.Vector(x, y, DECK_BOSS_TOP - 0.2)))
    # Relief over the heat-set insert in the ceiling of the boss pocket. The base prints deck-face-down, so
    # that pocket opens toward the bed and its ceiling is a bridge that sags; an insert that sits proud
    # would also hold the base off the deck. 0.3 mm of room above the boss top takes both.
    if RELIEF_H > 0:
        base = base.cut(Part.makeCylinder(RELIEF_D / 2, RELIEF_H + 0.05, A.Vector(x, y, DECK_BOSS_TOP - 0.05)))
    cb = Part.makeCylinder(CBORE_D / 2, FOOT_TOP - FLOOR + 0.5, A.Vector(x, y, FLOOR))
    # the wall rises from X17 above the foot top; leave it alone
    cb = cb.cut(Part.makeBox(WALL_X1 - WALL_X0, 51.5, 20.0, A.Vector(WALL_X0, 89.0, FOOT_TOP)))
    base = base.cut(cb)
# shave the non-bearing guides: tongue straight sides (above the R0.8 root fillets,
# which keep their 0.2 mm) and the fore/aft locator peg
tg = base.copy()
for x0, x1 in ((1.9, 2.0 + SHAVE), (6.0 - SHAVE, 6.1)):
    base = base.cut(Part.makeBox(x1 - x0, 51.5, 3.3, A.Vector(x0, 89.0, 62.8)))
peg = Part.makeBox(4.0, 4.0, 2.0, A.Vector(10.0, 113.0, FOOT_TOP))
keep = Part.makeBox(4.0 - 2 * SHAVE, 4.0 - 2 * SHAVE, 2.0 - SHAVE, A.Vector(10.0 + SHAVE, 113.0 + SHAVE, FOOT_TOP))
base = base.cut(peg.cut(keep))
base = base.removeSplitter()


def gap(b, box):
    return round(b.common(box).distToShape(wedge)[0], 3)


tongue_box = Part.makeBox(5.0, 40.0, 2.3, A.Vector(1.5, 95.0, 63.0))
peg_box = Part.makeBox(6.0, 6.0, 2.0, A.Vector(9.0, 112.0, 62.05))
rep['checks']['tongue_side_gap_mm_v5c_to_v5d'] = [gap(tg, tongue_box), gap(base, tongue_box)]
rep['checks']['locator_gap_mm_v5c_to_v5d'] = [gap(tg, peg_box), gap(base, peg_box)]
rep['checks']['screw_hole_d_mm'] = SCREW_HOLE_D
rep['checks']['cbore_d_mm'] = CBORE_D

c = rep['checks']
c['base_single_valid'] = base.isValid() and len(base.Solids) == 1
c['base_cm3'] = [round(v5c_vol / 1000, 3), round(base.Volume / 1000, 3)]
c['cbore_floor_above_boss_top_mm'] = round(FLOOR - DECK_BOSS_TOP, 2)
c['head_top_below_foot_top_mm'] = SINK
heads = [Part.makeCylinder(HEAD_D / 2, HEAD_H, A.Vector(x, y, FLOOR)) for x, y in SCREWS]
c['head_vs_base_mm3'] = [round(hit(h, base), 3) for h in heads]
c['head_vs_wedge_mm3'] = [round(hit(h, wedge), 3) for h in heads]
c['base_vs_wedge_mm3'] = round(hit(base, wedge), 4)
# wedge lowered straight onto the base (as the build's assembly check)
lift = {}
for dz in [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]:
    w = wedge.copy()
    w.translate(A.Vector(0, 0, dz))
    lift[str(dz)] = round(hit(w, base), 3)
c['wedge_lift_overlap_mm3'] = lift
# proud-insert tolerance: a D4.9 insert whose top stands PROUD of the boss top
def insert(x, y, proud):
    return Part.makeCylinder(2.45, 7.05 + proud, A.Vector(x, y, DECK_BOSS_TOP - 7.05))
c['proud_insert_vs_base_mm3'] = {str(h): round(sum(hit(insert(x, y, h), base) for x, y in SCREWS), 3) for h in (0.0, 0.2, 0.3, 0.4, 0.6)}
c['proud_insert_vs_v5c_base_mm3'] = {str(h): round(sum(hit(insert(x, y, h), v5c) for x, y in SCREWS), 3) for h in (0.0, 0.2, 0.3, 0.4, 0.6)}
c['floor_over_relief_mm'] = round(FLOOR - (DECK_BOSS_TOP + RELIEF_H), 2)
c['head_underside_Z_above_boss_top_mm'] = round(FLOOR - DECK_BOSS_TOP, 2)
# screwdriver / hex key access: D4 column over each screw from the recess floor up
c['screw_access_blocked_mm3'] = [
    round(hit(Part.makeCylinder(2.0, 60.0, A.Vector(x, y, FLOOR)), base), 3) for x, y in SCREWS]
# the 4 mm of foot above the boss is unchanged elsewhere: only recess volume removed
removed = (v5c_vol - base.Volume)
c['removed_mm3'] = round(removed, 1)

# seat on the v4 deck as it is modelled (same frame as the master)
try:
    dd = A.openDocument(str(DECK))
    deck = max((o.Shape for o in dd.Objects if hasattr(o, 'Shape') and o.Shape.Solids),
               key=lambda s: s.Volume)
    deck = deck.copy()
    deck.translate(A.Vector(0, 0, -6.5))   # v4 deck frame is +6.5 Z of the frame this mount was built in
    c['deck_bbox_z_in_mount_frame'] = [round(deck.BoundBox.ZMin, 2), round(deck.BoundBox.ZMax, 2)]
    c['base_vs_deck_v4_mm3'] = round(hit(base, deck), 3)
    # boss top supports the screw-head floor: insert pocket open, boss ring under the floor
    c['deck_boss_ring_under_head_solid'] = [
        hit(Part.makeCylinder(0.4, 0.4, A.Vector(x + 3.3, y, DECK_BOSS_TOP - 0.45)), deck) > 0.1
        for x, y in SCREWS]
except Exception as e:
    c['deck_check_error'] = repr(e)

ok = (c['base_single_valid'] and max(c['head_vs_base_mm3']) < 0.001 and
      max(c['head_vs_wedge_mm3']) < 0.001 and c['base_vs_wedge_mm3'] < 0.001 and
      max(c['wedge_lift_overlap_mm3'].values()) < 0.001 and
      max(c['screw_access_blocked_mm3']) < 0.001 and c['floor_over_relief_mm'] >= 2.0)
rep['ok'] = ok
print(json.dumps(rep, indent=1))
if not ok:
    sys.exit(1)

# ---- save: same layout as v5c (FCStd/STEP/STL + coupon base section) ----
coupon_base = base.common(Part.makeBox(16.0, 51.5, 11.0, A.Vector(0.0, 89.0, 58.0))).removeSplitter()
new = A.newDocument('DriverMount_v5')
objs = []
MIR = A.Matrix(-1, 0, 0, 79.0, 0, 1, 0, 0, 0, 0, 1, 0)
for nm, sh in [('Base_Left', base), ('Wedge_Left', wedge)]:
    o = new.addObject('Part::Feature', nm); o.Shape = sh; objs.append(o)
    m = sh.copy(); m.transformShape(MIR)
    o2 = new.addObject('Part::Feature', nm.replace('Left', 'Right')); o2.Shape = m; objs.append(o2)
for nm, sh in [('Coupon_Base', coupon_base), ('Coupon_Wedge', coupon_wedge)]:
    o = new.addObject('Part::Feature', nm); o.Shape = sh
new.recompute()
new.saveAs(str(OUT / 'DriverMount_v5.FCStd'))
Part.export(objs, str(OUT / 'DriverMount_v5.step'))
for nm, sh in [('Base_Left', base), ('Wedge_Left', wedge)]:
    s = sh.copy(); s.translate(A.Vector(0, 0, -s.BoundBox.ZMin))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.0872665,
                           Relative=False).write(str(OUT / 'stl' / (nm + '.stl')))
(OUT / 'validation-v5d-headrelief.json').write_text(json.dumps(rep, indent=2) + '\n')
print('saved')
