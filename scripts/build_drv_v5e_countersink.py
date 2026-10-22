"""Driver mount base v5e (2026-10-19): the ORIGINAL v5c base plus ONE change - a 90 degree countersink at each
deck-screw hole so a flat-head (countersunk) M3 sits flush and clamps the base to the deck through the heat-set insert.

Jim: "the only thing I want different from the originals are countersunk screws"; the back wall (X17..23) makes room
for the cone; the screw must clamp the base to the deck via the insert. Wedge, deck and everything else unchanged.

Also (Jim, later): the little extra spacing is back: D3.8 screw hole, tongue sides and locator peg shaved 0.05 mm per side (clearance 0.20 -> 0.25).

Why a cone: a socket head needs 3.0 mm of the 4.0 mm foot above the boss, leaving a 0.7 mm clamp floor. A flat head
needs 1.86 mm and bears on a 45 degree cone seat, so the seat under it is 2.1 mm thick at the hole edge and the bearing
area is about 2.7 times the flat annulus.

Derived from the saved v5c base (build_drv_v5.py can no longer reproduce the printed wedge: master drift).
"""
import sys, json, math
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad-python3/lib'])
import FreeCAD as A, Part, MeshPart
from pathlib import Path

V = A.Vector
ROOT = Path('/home/buralien/projects/gladiator-cad')
OUT = ROOT / 'cad/drivers/v5-interlock'
SRC = Path('/home/buralien/backups/drv-v5c-20261019/v5-interlock/DriverMount_v5.FCStd')
DECK = ROOT / 'cad/v2/upper-deck/v4-20261016/Gladiator_UpperDeck_v4.FCStd'

FOOT_TOP, BOSS_TOP = 62.0, 58.0
WALL_X0, WALL_X1 = 17.0, 23.0
SCREWS = [(14.5, 95.0), (14.5, 135.0)]
HOLE_R = 1.9                       # deck-screw hole D3.8 (original D3.6; Jim asked for the little extra spacing back)
SHAVE = 0.05                       # per side on the tongue straight sides and the locator peg: guide clearance 0.20 -> 0.25
# M3 countersunk head, worst case of DIN 7991 / ISO 10642 (dk 6.72, k 1.86), shank D3.0
SHANK_R, DK_R, K = 1.5, 3.36, 1.86
WALL_CARVE_H = 2.5                 # the back wall is carved out above the countersink: a vertical cylinder of the seat's top diameter, this high
EXTRA = 0.2                        # head top this far below the foot top at nominal contact
SEAT_CLEAR = 0.1                   # radial clearance of the seat over the head cone (head sinks this much more)
ZB_NOM = FOOT_TOP - EXTRA - K      # head cone start (shank junction) at nominal contact
# seat cone: r(z) = SHANK_R + SEAT_CLEAR + (z - ZB_NOM); equals the hole radius at Z_SEAT0
Z_SEAT0 = ZB_NOM + (HOLE_R - SHANK_R - SEAT_CLEAR)
ZB_ACT = ZB_NOM - SEAT_CLEAR       # where the head actually rests


def seat_r(z):
    return SHANK_R + SEAT_CLEAR + (z - ZB_NOM)


def hit(a, b):
    try:
        return a.common(b).Volume if a.BoundBox.intersect(b.BoundBox) else 0.0
    except Exception:
        return 0.0


doc = A.openDocument(str(SRC))
base0 = doc.getObject('Base_Left').Shape.copy()
wedge = doc.getObject('Wedge_Left').Shape.copy()
coupon_wedge = doc.getObject('Coupon_Wedge').Shape.copy()

base = base0.copy()
H = 2.6
for x, y in SCREWS:
    base = base.cut(Part.makeCylinder(HOLE_R, FOOT_TOP - BOSS_TOP + 0.4, V(x, y, BOSS_TOP - 0.2)))
    cone = Part.makeCone(HOLE_R, HOLE_R + H, H, V(x, y, Z_SEAT0), V(0, 0, 1))
    # The back wall rises from X17 above the foot top. Below Z62 the cone is allowed to cut under it (the
    # wall makes room); above Z62 the wall is left alone.
    cone = cone.cut(Part.makeBox(WALL_X1 - WALL_X0, 51.5, 30.0, V(WALL_X0, 89.0, FOOT_TOP)))
    base = base.cut(cone)
    # Back wall carved out (Jim): the cone continues up as a cylinder of the seat's top diameter through the wall root,
    # so the head and driver have a clean circular opening and no lip is left hanging over the cone.
    base = base.cut(Part.makeCylinder(seat_r(FOOT_TOP), WALL_CARVE_H, V(x, y, FOOT_TOP)))
# the little extra spacing: shave the non-bearing guides (tongue straight sides above the R0.8 root fillets,
# which keep their 0.2 mm; the fore/aft locator peg incl. its top)
pre_shave = base.copy()
for x0, x1 in ((1.9, 2.0 + SHAVE), (6.0 - SHAVE, 6.1)):
    base = base.cut(Part.makeBox(x1 - x0, 51.5, 3.3, V(x0, 89.0, 62.8)))
peg = Part.makeBox(4.0, 4.0, 2.0, V(10.0, 113.0, FOOT_TOP))
keep = Part.makeBox(4.0 - 2 * SHAVE, 4.0 - 2 * SHAVE, 2.0 - SHAVE, V(10.0 + SHAVE, 113.0 + SHAVE, FOOT_TOP))
base = base.cut(peg.cut(keep))
base = base.removeSplitter()


def gap(b, box):
    return round(b.common(box).distToShape(wedge)[0], 3)


tongue_box = Part.makeBox(5.0, 40.0, 2.3, V(1.5, 95.0, 63.0))
peg_box = Part.makeBox(6.0, 6.0, 2.0, V(9.0, 112.0, 62.05))

c = {}
c['guide_clearance_mm_v5c_to_v5e'] = dict(tongue_sides=[gap(pre_shave, tongue_box), gap(base, tongue_box)],
                                          locator_peg=[gap(pre_shave, peg_box), gap(base, peg_box)])
c['screw_hole_d_mm'] = [3.6, 2 * HOLE_R]
c['base_single_valid'] = base.isValid() and len(base.Solids) == 1
c['volume_cm3_v5c_to_v5e'] = [round(base0.Volume / 1000, 3), round(base.Volume / 1000, 3)]
c['removed_mm3'] = round(base0.Volume - base.Volume, 1)
c['seat_cone'] = dict(top_diameter_at_Z62=round(2 * seat_r(FOOT_TOP), 2), hole_edge_Z=round(Z_SEAT0, 2),
                      seat_thickness_over_boss_top_at_hole_edge_mm=round(Z_SEAT0 - BOSS_TOP, 2),
                      reaches_X=round(SCREWS[0][0] + seat_r(FOOT_TOP), 2), wall_face_X=WALL_X0)
slant = (seat_r(61.7) - HOLE_R) * math.sqrt(2)
c['bearing_area_mm2_cone_vs_old_flat_annulus'] = [round(math.pi * (min(seat_r(ZB_ACT + K), DK_R) + HOLE_R) * (min(seat_r(ZB_ACT + K), DK_R) - HOLE_R) * math.sqrt(2), 1), 12.4]

# the flat head, resting on the seat
heads, shanks = [], {}
for x, y in SCREWS:
    heads.append(Part.makeCone(SHANK_R, DK_R, K, V(x, y, ZB_ACT), V(0, 0, 1)))
c['head_top_Z'] = round(ZB_ACT + K, 2)
c['head_top_below_foot_top_mm'] = round(FOOT_TOP - (ZB_ACT + K), 2)
c['head_vs_base_mm3'] = [round(hit(h, base), 3) for h in heads]
c['head_vs_wedge_mm3'] = [round(hit(h, wedge), 3) for h in heads]
c['smaller_head_dk6.0_sinks_to_top_Z'] = round(ZB_ACT + K - (DK_R - 3.0) , 2)
c['base_vs_wedge_mm3'] = round(hit(base, wedge), 4)
lift = {}
for dz in [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]:
    w = wedge.copy()
    w.translate(V(0, 0, dz))
    lift[str(dz)] = round(hit(w, base), 3)
c['wedge_lift_overlap_mm3'] = lift
c['wall_carve'] = dict(diameter=round(2 * seat_r(FOOT_TOP), 2), height_above_foot_top=WALL_CARVE_H, reaches_X=round(SCREWS[0][0] + seat_r(FOOT_TOP), 2),
                       web_to_joint_hole_bottom_mm=round((68.0 - 1.8) - (FOOT_TOP + WALL_CARVE_H), 2),
                       wall_face_bearing_lost_mm2_each=round(2 * math.sqrt(seat_r(FOOT_TOP) ** 2 - (WALL_X0 - SCREWS[0][0]) ** 2) * WALL_CARVE_H, 1))
c['screw_access_blocked_mm3'] = [round(hit(Part.makeCylinder(2.0, 60.0, V(x, y, ZB_ACT + K)), base), 3) for x, y in SCREWS]

# wall-root band and sections against the original
def band(sh, y):
    t = 0.1
    return round(sh.common(Part.makeBox(6, t, 8, V(17, y - t / 2, 58))).Volume / t, 2)
c['wall_root_band_X17_23_Z58_66_mm2_v5c_to_v5e'] = [[band(base0, y), band(base, y)] for y in (95, 135)]

# screw lengths against the deck as printed (v4 deck is +6.5 Z of the mount frame)
try:
    dd = A.openDocument(str(DECK))
    deck = max((o.Shape for o in dd.Objects if hasattr(o, 'Shape') and o.Shape.Solids), key=lambda s: s.Volume).copy()
    deck.translate(V(0, 0, -6.5))
    c['base_vs_deck_v4_mm3'] = round(hit(base, deck), 3)
    tips = {}
    for L in (8, 10, 12):
        top = ZB_ACT + K
        sh = [Part.makeCylinder(SHANK_R, L, V(x, y, top - L), V(0, 0, 1)) for x, y in SCREWS]
        tips[str(L)] = dict(tip_Z=round(top - L, 2), engaged_in_insert_mm=round(BOSS_TOP - (top - L), 2),
                            hits_deck_mm3=round(sum(hit(s, deck) for s in sh), 3))
    c['screw_lengths_vs_printed_deck'] = tips
    c['insert_bottom_Z_(7.05_long)'] = round(BOSS_TOP - 7.05, 2)
except Exception as e:
    c['deck_check_error'] = repr(e)

ok = (c['base_single_valid'] and max(c['head_vs_base_mm3']) < 0.001 and max(c['head_vs_wedge_mm3']) < 0.001 and
      c['base_vs_wedge_mm3'] < 0.001 and max(c['wedge_lift_overlap_mm3'].values()) < 0.001 and
      max(c['screw_access_blocked_mm3']) < 0.001 and c.get('base_vs_deck_v4_mm3', 1) < 0.001)
rep = dict(source='saved v5c Base_Left', ok=ok, checks=c)
print(json.dumps(rep, indent=1))
if not ok:
    sys.exit(1)

coupon_base = base.common(Part.makeBox(16.0, 51.5, 11.0, V(0.0, 89.0, 58.0))).removeSplitter()
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
    s = sh.copy(); s.translate(V(0, 0, -s.BoundBox.ZMin))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.0872665, Relative=False).write(str(OUT / 'stl' / (nm + '.stl')))
(OUT / 'validation-v5e-countersink.json').write_text(json.dumps(rep, indent=2) + '\n')
print('saved')
