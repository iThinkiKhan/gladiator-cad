"""Upper deck v3 (2026-10-15, Claude). Derived from the master UpperDeck solid; the master is NOT modified.

Run: freecadcmd build_deck_v3.py   (after build_rails_v4.py)

Jim, 2026-10-15: the deck sits in the arch rails like the power board tray sat in its feet; ONE heat-set insert per rail holds it down; re-use the printed driver mounts
(and their 20 mm standoffs) and the mast; chamfer any hole that prints on the glass bed.
What changes against the printed deck:
  * the six rail-screw holes (X12/67, Y16/68/120) are filled in: nothing has to line up any more
  * six plain through slots for the rail pegs (rail pegs 3.0 x 8.1, slots 3.6 x 8.6 locating at Y68.35, 3.6 x 12.6 slotted at Y23.85 and Y112.85), on the rail centre lines X14 and X65
  * two retention slots 6.0 (X) x 4.4 (Y) at (13, 83.5) and (66, 83.5): M3 x 12 + washer down into the single insert in each rail. Long in X so ONE slot serves the new rail insert (X14 / X65) and a hole drilled in the OLD rail (X12 / X67)
  * two wire holes O10 at (23, 44) and (56, 44)
  * every NEW hole gets a 0.8 mm x 45 degree chamfer on its underside, because the deck prints top-up with its underside on the glass bed
What does not change: outline, mast bore and Z68.5 bearing collar, the mast-front wire slot, the four driver-mount bosses (D4.6 inserts, (14.5,95) (14.5,135) (64.5,95) (64.5,135)),
the S3 bosses, the antenna-pylon bosses (60,10) (76,10). The old deck already carries 0.4 / 0.8 mm entry chamfers on its through holes.
"""
import FreeCAD as A, Part, MeshPart, math, json, os, shutil, traceback
from pathlib import Path

V = A.Vector
R = Path('/home/buralien/projects/gladiator-cad')
O = R / 'cad/v2/upper-deck/v3-20261015'
O.mkdir(parents=True, exist_ok=True)
W = Path('/tmp/deckv3')
W.mkdir(exist_ok=True)
shutil.copy(R / 'cad/enclosure/concept-20261013/Gladiator_Enclosure_Concept.FCStd', W / 'c.FCStd')

P = dict(z0=54.5, z1=58.5, peg_x=(12.25, 66.75), slots=[(23.85, 12.6), (68.35, 8.6), (112.85, 12.6)], slot_w=7.7,
         retention_y=83.5, retention_x=(12.25, 66.75), retention_slot=(7.1, 4.4), wire_holes=[(23.0, 44.0), (56.0, 44.0)], wire_d=10.0, chamfer=0.8,
         RAIL_SPREAD=3.5, old_rail_holes=[(12, 16), (12, 68), (12, 120), (67, 16), (67, 68), (67, 120)])
p = P


def plain(s):
    q = Part.Shape()
    q.importBrepFromString(s.exportBrepToString())
    return q


def fuse(*s):
    r = plain(s[0])
    for x in s[1:]:
        r = plain(r.fuse(plain(x)))
    return plain(r.removeSplitter())


def cut(a, *s):
    a = plain(a)
    for x in s:
        a = plain(a.cut(plain(x)))
    return plain(a.removeSplitter())


def rect_wire(cx, cy, w, l, z):
    vs = [V(cx - w / 2, cy - l / 2, z), V(cx + w / 2, cy - l / 2, z), V(cx + w / 2, cy + l / 2, z), V(cx - w / 2, cy + l / 2, z)]
    return Part.makePolygon(vs + [vs[0]])


def slot_with_chamfer(cx, cy, w, l):
    """through slot plus a 45 degree chamfer on the underside (the glass-bed side)"""
    z0, z1, c = p['z0'], p['z1'], p['chamfer']
    thru = Part.makeBox(w, l, z1 - z0 + 2, V(cx - w / 2, cy - l / 2, z0 - 1))
    ch = Part.makeLoft([rect_wire(cx, cy, w + 2 * c, l + 2 * c, z0 - 0.0), rect_wire(cx, cy, w, l, z0 + c)], True, True)
    ch.translate(V(0, 0, 0))
    return [thru, ch]


def hole_with_chamfer(cx, cy, d):
    z0, z1, c = p['z0'], p['z1'], p['chamfer']
    thru = Part.makeCylinder(d / 2, z1 - z0 + 2, V(cx, cy, z0 - 1))
    ch = Part.makeCone(d / 2 + c, d / 2, c, V(cx, cy, z0), V(0, 0, 1))
    return [thru, ch]


d0 = A.openDocument(str(W / 'c.FCStd'))
deck0 = plain(d0.getObject('Ref_UpperDeck').Shape)
vol0 = deck0.Volume
# 1. fill the six old rail-screw holes (Z54.5..58.5, a little oversize so the fill bonds to the plate)
fills = [Part.makeCylinder(2.5, p['z1'] - p['z0'], V(x, y, p['z0'])) for (x, y) in p['old_rail_holes']]
deck = fuse(deck0, *fills)
# 2. new through features
tools = []
for px in p['peg_x']:
    for (sy, sl) in p['slots']:
        tools += slot_with_chamfer(px, sy, p['slot_w'], sl)
for rx in p['retention_x']:
    tools += slot_with_chamfer(rx, p['retention_y'], p['retention_slot'][0], p['retention_slot'][1])
for (wx, wy) in p['wire_holes']:
    tools += hole_with_chamfer(wx, wy, p['wire_d'])
deck = cut(deck, *tools)

chk = dict(status='v3 DRAFT - not printed, not fitted', parameters=P, valid=deck.isValid(), solids=len(deck.Solids), volume_mm3=round(deck.Volume, 1),
           old_deck_volume_mm3=round(vol0, 1))
bb = deck.BoundBox
chk['bbox'] = [round(v, 1) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)]

# 3. probes: slots open, fills solid, driver bosses and mast bore untouched
probe = {}
for lab, pt, expect in [('slot L Y23.85 open', (14, 23.85, 56.5), False), ('slot L Y68.35 open', (14, 68.35, 56.5), False), ('slot L Y112.85 open', (14, 112.85, 56.5), False),
                        ('slot R Y68.35 open', (65, 68.35, 56.5), False), ('retention slot L open (old-rail end X10.2)', (10.5, 83.5, 56.5), False), ('retention slot L open (new-rail end X15.8)', (15.5, 83.5, 56.5), False), ('retention slot R open', (66, 83.5, 56.5), False), ('plate beside retention slot solid', (13, 79.0, 56.5), True),
                        ('wire hole L open', (23, 44, 56.5), False), ('wire hole R open', (56, 44, 56.5), False),
                        ('old rail hole (12,16) filled', (12, 16, 56.5), True), ('old rail hole (67,120) filled', (67, 120, 56.5), True),
                        ('plate beside slot solid', (14, 78, 56.5), True), ('underside chamfer opens the slot (14,23.85,54.8) beyond the slot edge x=14+2.1', (16.1, 23.85, 54.7), False),
                        ('mast bore open', (39.5, 113 + 6, 56.5), False), ('driver boss (14.5,95) solid ring', (14.5 + 3.3, 95, 61.0), True),
                        ('driver boss insert pocket open', (14.5, 95, 62.0), False)]:
    inside = deck.isInside(V(*pt), 1e-6, True)
    probe[lab] = dict(point=pt, result='solid' if inside else 'empty', ok=(inside == expect))
chk['probes'] = probe

# 3b. tie-down screw checks: new rail insert at X14 / X65, old-rail insert (drilled) at X12 / X67, same slot for both
ties = {}
try:
    cdoc = A.openDocument(str(W / 'c.FCStd'))
    skip = ('Ref_UpperDeck', 'Ref_SideRail', 'Ref_ChassisDeck', 'Ref_Battery', 'Ref_PowerBoardTray', 'Ref_Base', 'Ref_INA226', 'Ref_BoardReference', 'Ref_PowerSwitch', 'Ref_Switch', 'Ref_MastBase')
    above = {o.Name: plain(o.Shape) for o in cdoc.Objects if o.Name.startswith(('Ref_', 'Head_')) and not o.Name.startswith(skip) and o.Shape.Volume > 0}
    oldL = plain(cdoc.getObject('Ref_SideRailLeft').Shape)
    for lab, sx in (('new rail L (insert X14)', 14.0), ('old rail L (drill X12)', 12.0), ('new rail R (insert X65)', 65.0), ('old rail R (drill X67)', 67.0)):
        y = p['retention_y']
        shank = Part.makeCylinder(1.5, 16.0, V(sx, y, 49.0))
        bear = Part.makeCylinder(3.5, 1.0, V(sx, y, 57.5))
        sup = deck.common(bear).Volume / (math.pi * 3.5 ** 2 * 1.0)
        col = Part.makeCylinder(4.5, 300.0, V(sx, y, 58.5))
        first = None
        for nm, sh in above.items():
            try:
                cm = col.common(sh)
            except Exception:
                continue
            if cm.Volume > 0.01 and (first is None or cm.BoundBox.ZMin < first[1]):
                first = (nm, round(cm.BoundBox.ZMin, 1))
        ties[lab] = dict(screw_x=sx, screw_y=y, shank_vs_deck_mm3=round(deck.common(shank).Volume, 3), washer_bearing_fraction=round(sup, 2),
                         first_thing_above_in_the_screwdriver_column=first, clear_height_above_deck_mm=None if first is None else round(first[1] - 58.5, 1))
    ties['old rail solid at the drill spot'] = {str(pt): oldL.isInside(V(*pt), 1e-6, True) for pt in [(12.0, 83.5, 47.0), (12.0, 83.5, 53.0), (9.7, 83.5, 50.0), (14.3, 83.5, 50.0), (12.0, 81.2, 50.0), (12.0, 85.8, 50.0)]}
except Exception:
    traceback.print_exc()
chk['tie_down_checks'] = ties

# 3c. rail spacing: Jim measured the installed rails 46.5 mm apart (inner faces) instead of 43.0. Unknown split between the two rails: test pegs and
#     the tie-down screw at every split from "left rail did not move" to "right rail did not move"
spread = {}
try:
    rd3 = A.openDocument(str(R / 'cad/v2/rails/v4-20261015/Gladiator_ArchRails_v4.FCStd'))
    rl, rr = plain(rd3.getObject('Arch_Rail_Left_v4').Shape), plain(rd3.getObject('Arch_Rail_Right_v4').Shape)
    for a in (0.0, 1.75, 3.5):                       # left rail moves out by a, right by 3.5 - a
        l2, r2 = plain(rl), plain(rr)
        l2.translate(V(-a, 0, 0))
        r2.translate(V(p['RAIL_SPREAD'] - a, 0, 0))
        col = []
        for nm, sh, sx in (('L', l2, 14.0 - a), ('R', r2, 65.0 + p['RAIL_SPREAD'] - a)):
            ov = round(deck.common(sh).Volume, 3)
            screw = Part.makeCylinder(1.5, 16.0, V(sx, p['retention_y'], 49.0))
            col.append(dict(rail=nm, rail_vs_deck_mm3=ov, tie_down_screw_x=sx, screw_vs_deck_mm3=round(deck.common(screw).Volume, 3)))
        spread['left rail out %.2f, right rail out %.2f' % (a, p['RAIL_SPREAD'] - a)] = col
except Exception:
    traceback.print_exc()
chk['rail_spacing_worst_cases'] = spread
print(json.dumps(spread, indent=1), flush=True)

# 4. fit against the arch rails (pegs through the slots) and the chassis references
try:
    rd = A.openDocument(str(R / 'cad/v2/rails/v4-20261015/Gladiator_ArchRails_v4.FCStd'))
    fit = {}
    for nm in ('Arch_Rail_Left_v4', 'Arch_Rail_Right_v4'):
        rs = plain(rd.getObject(nm).Shape)
        try:
            ov = round(deck.common(rs).Volume, 3)
        except Exception:
            ov = None
        fit[nm] = dict(overlap_mm3=ov, gap_mm=round(deck.distToShape(rs)[0], 3))
    chk['fit_with_rails'] = fit
    # peg to slot clearance: peg 3.0 x 8.1 in 3.6 x 8.6 / 12.6
    chk['peg_clearance_mm'] = dict(x_each_side=round((p['slot_w'] - 3.0) / 2, 2), locating_slot_y_each_end=round((8.6 - 8.1) / 2, 2), slotted_y_each_end=round((12.6 - 8.1) / 2, 2))
except Exception:
    traceback.print_exc()

doc = A.newDocument('Gladiator_UpperDeck_v3')
o = doc.addObject('Part::Feature', 'UpperDeck_v3')
o.Shape = deck
doc.recompute()
doc.saveAs(str(O / 'Gladiator_UpperDeck_v3.FCStd'))
Part.export([o], str(O / 'Gladiator_UpperDeck_v3.step'))
m = MeshPart.meshFromShape(Shape=deck, LinearDeflection=0.03, AngularDeflection=math.radians(8))
m.write(str(O / 'Gladiator_UpperDeck_v3.stl'))
c = plain(deck)
chk['stl'] = dict(file='Gladiator_UpperDeck_v3.stl', is_solid=m.isSolid(), non_manifold=m.hasNonManifolds(), size_mm=[round(c.BoundBox.XLength, 1), round(c.BoundBox.YLength, 1), round(c.BoundBox.ZLength, 1)],
                  orientation='as modelled: top up, underside (Z54.5) flat on the glass bed')
(O / 'validation.json').write_text(json.dumps(chk, indent=1, default=str))
print(json.dumps({k: chk[k] for k in ('valid', 'solids', 'volume_mm3', 'old_deck_volume_mm3', 'bbox', 'fit_with_rails', 'peg_clearance_mm', 'stl')}, indent=1, default=str), flush=True)
print(json.dumps(ties, indent=1, default=str), flush=True)
print('probes not ok:', [k for k, v in probe.items() if not v['ok']], flush=True)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(16, 9))
    for w in deck.slice(V(0, 0, 1), 56.5):
        pts = w.discretize(150)
        axs[0].plot([q.x for q in pts], [q.y for q in pts], color='#34495e', lw=1.2)
    rd2 = A.openDocument(str(R / 'cad/v2/rails/v4-20261015/Gladiator_ArchRails_v4.FCStd'))
    for nm, col in (('Arch_Rail_Left_v4', '#c0392b'), ('Arch_Rail_Right_v4', '#1565c0')):
        for w in plain(rd2.getObject(nm).Shape).slice(V(0, 0, 1), 56.5):   # pegs only exist above 54.5
            pts = w.discretize(60)
            axs[0].plot([q.x for q in pts], [q.y for q in pts], color=col, lw=1.0)
    axs[0].set_aspect('equal'); axs[0].grid(alpha=.3)
    axs[0].set_title('Deck v3 plan at Z56.5: slots (peg outlines red/blue inside them), retention slots, wire holes, mast slot, driver bosses', fontsize=9)
    for w in deck.slice(V(1, 0, 0), 14.0):
        pts = w.discretize(150)
        axs[1].plot([q.y for q in pts], [q.z for q in pts], color='#34495e', lw=1.2)
    for w in plain(rd2.getObject('Arch_Rail_Left_v4').Shape).slice(V(1, 0, 0), 14.0):
        pts = w.discretize(150)
        axs[1].plot([q.y for q in pts], [q.z for q in pts], color='#c0392b', lw=1.0)
    axs[1].set_ylim(30, 70); axs[1].set_aspect('equal'); axs[1].grid(alpha=.3)
    axs[1].set_title('Side section X=14: deck (dark) on the left arch (red); pegs rise into the slots', fontsize=9)
    fig.savefig(str(O / 'deck_v3_sections.png'), dpi=65, bbox_inches='tight')
except Exception:
    traceback.print_exc()
os._exit(0)
