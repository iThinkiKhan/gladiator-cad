"""Upper deck v4 (2026-10-16, Claude): rebuilt on the MEASURED installed rails (Jim): rear pegs 58 mm and front pegs 60 mm apart over their outer faces, tie-down holes 52 mm apart over their inner faces,
rails 15 mm from the mast tube each side, peg-to-peg 96.7 mm. Rails splay 2 mm toward the mast end, symmetric about the mast (X39.5). Outline widened. Derived from the v3 script.
Upper deck v3 (2026-10-15, Claude). Derived from the master UpperDeck solid; the master is NOT modified.

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
O = R / 'cad/v2/upper-deck/v4-20261016'
O.mkdir(parents=True, exist_ok=True)
W = Path('/tmp/deckv4')
W.mkdir(exist_ok=True)
shutil.copy(R / 'cad/enclosure/concept-20261013/Gladiator_Enclosure_Concept.FCStd', W / 'c.FCStd')

P = dict(z0=54.5, z1=58.5, slot_w=6.0, mast_x=39.5,
         # (Y, left peg X, right peg X, left slot length Y, right slot length Y): pegs 3.0 x 8.1 on the real rails; the left middle slot locates in Y (0.4 each end), all others are slotted
         peg_rows=[(23.85, 12.5, 67.0, 12.6, 12.6), (68.35, 11.75, 67.75, 12.6, 12.6), (112.85, 11.0, 68.5, 12.6, 12.6)],
         retention_y=83.5, TIES={'L': (11.8, 83.5, 6.8, 5.4), 'R': (68.0, 83.5, 6.8, 5.4)}, retention_x=(11.8, 68.0), retention_slot=(6.8, 5.4), wire_holes=[(23.0, 44.0), (56.0, 44.0)], wire_d=10.0, chamfer=0.8,
         widen=0.0,       # outline widening: 3.0 per side hits the driver wedges (204 mm3 each) between Y89 and 140, so the outline is unchanged until Jim gives the body width
         old_rail_holes=[(12, 16), (12, 68), (12, 120), (67, 16), (67, 68), (67, 120)])
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
ext = []
edge_solid = None
if p['widen'] > 0:
    ext = [Part.makeBox(p['widen'], 140.0, p['z1'] - p['z0'], V(-3.0 - p['widen'], 0, p['z0'])), Part.makeBox(p['widen'], 140.0, p['z1'] - p['z0'], V(82.0, 0, p['z0']))]
    edge_solid = [round(deck.common(Part.makeBox(1.0, 140.0, 4.0, V(-3.0, 0, 54.5))).Volume, 1), round(deck.common(Part.makeBox(1.0, 140.0, 4.0, V(81.0, 0, 54.5))).Volume, 1)]   # 560 = plain full edge
    deck = fuse(deck, *ext)
# 2. new through features
tools = []
for (sy, lx, rx_, ll, rl) in p['peg_rows']:
    tools += slot_with_chamfer(lx, sy, p['slot_w'], ll)
    tools += slot_with_chamfer(rx_, sy, p['slot_w'], rl)
for side_, (cx_, cy_, w_, l_) in p['TIES'].items():          # w along X, l along Y; chamfered on the glass side
    tools += slot_with_chamfer(cx_, cy_, w_, l_)
for (wx, wy) in p['wire_holes']:
    tools += hole_with_chamfer(wx, wy, p['wire_d'])
deck = cut(deck, *tools)

chk = dict(status='v3 DRAFT - not printed, not fitted', parameters=P, valid=deck.isValid(), solids=len(deck.Solids), volume_mm3=round(deck.Volume, 1),
           old_deck_volume_mm3=round(vol0, 1))
bb = deck.BoundBox
chk['bbox'] = [round(v, 1) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)]

# 3. probes: slots open, fills solid, driver bosses and mast bore untouched
probe = {}
for lab, pt, expect in [('slot L Y23.85 open', (12.5, 23.85, 56.5), False), ('slot L Y68.35 open', (11.75, 68.35, 56.5), False), ('slot L Y112.85 open', (11.0, 112.85, 56.5), False),
                        ('slot R Y23.85 open', (67.0, 23.85, 56.5), False), ('slot R Y68.35 open', (67.75, 68.35, 56.5), False), ('slot R Y112.85 open', (68.5, 112.85, 56.5), False),
                        ('tie-down L open (X)', (10.0, 83.5, 56.5), False), ('tie-down L open (Y end)', (11.25, 86.0, 56.5), False), ('tie-down R open (X end)', (65.0, 83.5, 56.5), False), ('tie-down R open (X far end)', (70.5, 83.5, 56.5), False),
                        ('plate beside tie-down L solid', (11.25, 79.5, 56.5), True), ('plate beside tie-down R solid', (67.75, 79.5, 56.5), True),
                        ('wire hole L open', (23, 44, 56.5), False), ('wire hole R open', (56, 44, 56.5), False),
                        ('old rail hole (12,16) filled', (12, 16, 56.5), True), ('old rail hole (67,120) filled', (67, 120, 56.5), True),
                        ('plate beside peg slot solid', (12.0, 78, 56.5), True), ('underside chamfer opens the slot', (15.9, 23.85, 54.7), False),
                        ('mast bore open', (39.5, 113 + 6, 56.5), False), ('driver boss (14.5,95) solid ring', (14.5 + 3.3, 95, 61.0), True),
                        ('driver boss insert pocket open', (14.5, 95, 62.0), False)]:
    inside = deck.isInside(V(*pt), 1e-6, True)
    probe[lab] = dict(point=pt, result='solid' if inside else 'empty', ok=(inside == expect))
chk['probes'] = probe

# 3b. real rail positions: both rails shifted/rotated to the measured layout (pegs at X12 / 11 rear-to-front on the left, 67 / 68 on the right; splay 1 mm per side over 89 mm)
SPLAY = math.degrees(math.atan(1.0 / 89.0))


def real_pos(nm, shp):
    q = plain(shp)
    if 'Left' in nm:
        q.translate(V(-2.0, 0, 0))
        q.rotate(V(12.0, 23.85, 0), V(0, 0, 1), SPLAY)
    else:
        q.translate(V(2.0, 0, 0))
        q.rotate(V(67.0, 23.85, 0), V(0, 0, 1), -SPLAY)
    return q


def insert_x(side, y=83.5):
    d_ = (y - 23.85) / 89.0
    return 12.0 - d_ if side == 'L' else 67.0 + d_


ties = {}
try:
    cdoc = A.openDocument(str(W / 'c.FCStd'))
    skip = ('Ref_UpperDeck', 'Ref_SideRail', 'Ref_ChassisDeck', 'Ref_Battery', 'Ref_PowerBoardTray', 'Ref_Base', 'Ref_INA226', 'Ref_BoardReference', 'Ref_PowerSwitch', 'Ref_Switch', 'Ref_MastBase')
    above = {o.Name: plain(o.Shape) for o in cdoc.Objects if o.Name.startswith(('Ref_', 'Head_')) and not o.Name.startswith(skip) and o.Shape.Volume > 0}
    ties['widening_vs_references_mm3'] = {nm: round(e.common(sh).Volume, 3) for e in ext for nm, sh in above.items() if e.common(sh).Volume > 0.001} or 'none'
    ties['original_edge_is_plain_full_thickness (560 = yes)'] = edge_solid
    for lab, side in (('left insert', 'L'), ('right insert', 'R')):
        sx = insert_x(side)
        y = p['retention_y']
        shank = Part.makeCylinder(1.5, 16.0, V(sx, y, 49.0))
        bear = Part.makeCylinder(4.5, 1.0, V(sx, y, 57.5))
        sup = deck.common(bear).Volume / (math.pi * 4.5 ** 2 * 1.0)
        col = Part.makeCylinder(4.5, 300.0, V(sx, y, 58.5))
        first = None
        for nm, sh in above.items():
            try:
                cm = col.common(sh)
            except Exception:
                continue
            if cm.Volume > 0.01 and (first is None or cm.BoundBox.ZMin < first[1]):
                first = (nm, round(cm.BoundBox.ZMin, 1))
        ties[lab] = dict(screw_x=round(sx, 2), screw_y=y, shank_vs_deck_mm3=round(deck.common(shank).Volume, 3), fender_washer_9mm_bearing_fraction=round(sup, 2),
                         first_thing_above_in_the_screwdriver_column=first, clear_height_above_deck_mm=None if first is None else round(first[1] - 58.5, 1),
                         slot_margin_mm=round(min(sx - (p['retention_x'][0 if side == 'L' else 1] - p['retention_slot'][0] / 2 + 1.5), (p['retention_x'][0 if side == 'L' else 1] + p['retention_slot'][0] / 2 - 1.5) - sx), 2))
except Exception:
    traceback.print_exc()
for lab_, side_ in (('left insert', 'L'), ('right insert', 'R')):
    if lab_ in ties:
        cx_, cy_, w_, l_ = p['TIES'][side_]
        sx_ = insert_x(side_)
        ties[lab_].pop('slot_margin_mm', None)
        ties[lab_]['slot_margin_mm'] = dict(x=round(w_ / 2 - 1.5 - abs(sx_ - cx_), 2), y=round(l_ / 2 - 1.5 - abs(p['retention_y'] - cy_), 2))
bore_r = None
for k_ in range(0, 200):
    x_ = 39.5 + k_ * 0.1
    if deck.isInside(V(x_, 113.0, 56.5), 1e-6, True):
        bore_r = round(x_ - 39.5, 2)
        break
ties['mast_bore_radius_mm (tube 10.0)'] = bore_r
chk['tie_down_checks'] = ties

# 4. fit against the arch rails (pegs through the slots) and the chassis references
try:
    rd = A.openDocument(str(R / 'cad/v2/rails/v4-20261015/Gladiator_ArchRails_v4.FCStd'))
    fit = {}
    for nm in ('Arch_Rail_Left_v4', 'Arch_Rail_Right_v4'):
        rs = real_pos(nm, rd.getObject(nm).Shape)
        try:
            ov = round(deck.common(rs).Volume, 3)
        except Exception:
            ov = None
        fit[nm] = dict(overlap_mm3=ov, gap_mm=round(deck.distToShape(rs)[0], 3))
    chk['fit_with_rails'] = fit
    # peg to slot clearance: peg 3.0 x 8.1 in 3.6 x 8.6 / 12.6
    chk['peg_clearance_mm'] = dict(x_each_side=round((p['slot_w'] - 3.0) / 2, 2), locating_slot_y_each_end=round((8.9 - 8.1) / 2, 2), slotted_y_each_end=round((12.6 - 8.1) / 2, 2))
except Exception:
    traceback.print_exc()

doc = A.newDocument('Gladiator_UpperDeck_v4')
o = doc.addObject('Part::Feature', 'UpperDeck_v4')
o.Shape = deck
doc.recompute()
doc.saveAs(str(O / 'Gladiator_UpperDeck_v4.FCStd'))
Part.export([o], str(O / 'Gladiator_UpperDeck_v4.step'))
m = MeshPart.meshFromShape(Shape=deck, LinearDeflection=0.03, AngularDeflection=math.radians(8))
m.write(str(O / 'Gladiator_UpperDeck_v4.stl'))
c = plain(deck)
chk['stl'] = dict(file='Gladiator_UpperDeck_v4.stl', is_solid=m.isSolid(), non_manifold=m.hasNonManifolds(), size_mm=[round(c.BoundBox.XLength, 1), round(c.BoundBox.YLength, 1), round(c.BoundBox.ZLength, 1)],
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
        for w in real_pos(nm, rd2.getObject(nm).Shape).slice(V(0, 0, 1), 56.5):   # pegs only exist above 54.5
            pts = w.discretize(60)
            axs[0].plot([q.x for q in pts], [q.y for q in pts], color=col, lw=1.0)
    axs[0].set_aspect('equal'); axs[0].grid(alpha=.3)
    axs[0].set_title('Deck v3 plan at Z56.5: slots (peg outlines red/blue inside them), retention slots, wire holes, mast slot, driver bosses', fontsize=9)
    for w in deck.slice(V(1, 0, 0), 11.5):
        pts = w.discretize(150)
        axs[1].plot([q.y for q in pts], [q.z for q in pts], color='#34495e', lw=1.2)
    for w in real_pos('Arch_Rail_Left_v4', rd2.getObject('Arch_Rail_Left_v4').Shape).slice(V(1, 0, 0), 11.5):
        pts = w.discretize(150)
        axs[1].plot([q.y for q in pts], [q.z for q in pts], color='#c0392b', lw=1.0)
    axs[1].set_ylim(30, 70); axs[1].set_aspect('equal'); axs[1].grid(alpha=.3)
    axs[1].set_title('Side section X=14: deck (dark) on the left arch (red); pegs rise into the slots', fontsize=9)
    fig.savefig(str(O / 'deck_v4_sections.png'), dpi=65, bbox_inches='tight')
except Exception:
    traceback.print_exc()
os._exit(0)
