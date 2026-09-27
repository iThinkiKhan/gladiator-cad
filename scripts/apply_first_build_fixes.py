"""Apply the fixes from the first physical Gladiator build (2026-09-27) to the master.

Jim's findings after assembling rails, upper deck and mast on the real chassis:

1. Rails too short.  Battery-to-soffit clearance 8.5 -> about 75% more, so 15.0.
   Everything carried by the rails (upper deck and all that sits on it) rises by
   the same 6.5 mm.  The upper deck itself is unchanged -- only its height moves.
2. Right front foot does not quite pass its screw through the aluminium slit;
   it needs slotting 3-5 mm rearward.  The aluminium slit is 33 long, so a screw
   further back always passes -- the fix is to move the whole crosswise slot back
   3.5 (keeping its lateral play and its head bearing) and lengthen the foot to
   carry it.  A T-shaped slot was tried first and rejected: the head bore on only
   1.8 mm2 where the two slots meet.  Both rails; the right mirrors the left.
   Also fixed here: in the as-printed front foot an M3 socket head sitting over
   the slit centre overlaps the outboard skin (5.8 mm3 at X 10.5, still 1.2 mm3
   at X 11), so it could never seat flat.  A 1.3 mm head relief cures that.
3. Mast taller: proportionate to the 6.5 mm lift plus "a tad" -> top Z 120 -> 130.
4. Mast base M2 holes wider set by about 0.75 mm each (41.0 -> 42.5 apart).
   Also folds in the 2026-09-26 mast-base reprint that only lived in a side copy:
   spigot 5.0 -> 3.5 below the deck and a 0.8 mm socket entry chamfer.

The aluminium deck (ChassisDeck) is NOT touched.  Nothing is saved unless every
check passes.  Run with freecadcmd on the CAD server.
"""
import json
import math
import os
import shutil
import sys
import time

import FreeCAD as App
import MeshPart
import Part
import Sketcher

V = App.Vector


def p(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n')
    sys.stdout.flush()


FAILS = []


def check(ok, msg):
    p(('PASS ' if ok else 'FAIL ') + msg)
    if not ok:
        FAILS.append(msg)


REPO = '/home/buralien/projects/gladiator-cad'
MASTER = REPO + '/cad/master/Gladiator_Master.FCStd'
OUTDIR = REPO + '/cad/build2-20260927'
INCOMING = '/home/buralien/3D-Printer/Incoming'
DRY = os.environ.get('GP_DRY') == '1'   # freecadcmd rejects unknown CLI flags

DZ = 6.5            # rail/upper-structure lift
MAST_TOP = 130.0    # was 120
SLOT_BACK = 3.5     # front foot slot moved this far rearward (screw Y 10 -> 13.5)
WELL_END = 16.5     # front well rear wall (was 13); SHCS head at Y 13.5 reaches 16.25
FOOT_END = 18.5     # front foot / post rear face (was 13); 2.5 to battery at Y 21
SOFFIT_START = 20.5 # full soffit height before the battery front edge at Y 21
RELIEF = 1.3        # head relief into the outboard skin (skin 2.5 -> 1.2 locally)
RELIEF_H = 3.5      # relief height above the well floor (M3 SHCS head is 3.0)

ts = time.strftime('%Y%m%d-%H%M%S')
if not DRY:
    bk = REPO + '/cad/master/drafts/Gladiator_Master.pre-build2-fixes.%s.FCStd' % ts
    shutil.copy2(MASTER, bk)
    p('BACKUP', bk)

doc = App.openDocument(MASTER)
sheet = doc.getObject('Parameters')
O = doc.getObject

# ---------------------------------------------------------------- snapshot
CLASH_SET = ['ChassisDeck', 'BatteryBox', 'SideRailLeft', 'SideRailRight', 'MastBase',
             'MastTube', 'UpperDeck', 'S3Board', 'Breadboard', 'PowerShield', 'AntennaPost',
             'DrvV5_Base_L', 'DrvV5_Wedge_L', 'DrvV5_Base_R', 'DrvV5_Wedge_R',
             'DrvV5_Board_L', 'DrvV5_Fins_L', 'DrvV5_Board_R', 'DrvV5_Fins_R']
HEAD_GROUP = O('HeadCandidate_v01')


def head_parts():
    out = []
    for g in HEAD_GROUP.Group:
        for o in getattr(g, 'Group', [g]):
            if o.TypeId == 'Part::Feature':
                out.append(o)
    return out


HEAD = head_parts()
HEAD_SOLID = [o.Name for o in HEAD if o.Shape.Solids and o.Name not in
              ('ToF_Field_Reference', 'Harness_Route_Guide')]
CLASH_SET += HEAD_SOLID


def shapes():
    return {n: O(n).Shape.copy() for n in CLASH_SET}


def overlaps(sh):
    names = list(sh)
    res = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if not sh[a].BoundBox.intersect(sh[b].BoundBox):
                continue
            try:
                v = sh[a].common(sh[b]).Volume
            except Exception:
                v = -1
            if abs(v) > 0.01:
                res[(a, b)] = v
    return res


before = shapes()
before_ov = overlaps(before)
old_deck = O('UpperDeck').Shape.copy()
old_ant = O('AntennaPost').Shape.copy()
old_dml = O('DriverMountLeft').Shape.copy()
old_board = O('DriverBoardLeft').Shape.copy()
old_head = {o.Name: o.Shape.copy() for o in HEAD}
old_v5 = {n: O(n).Shape.copy() for n in CLASH_SET if n.startswith('DrvV5_')}
old_tube_vol = O('MastTube').Shape.Volume

# ---------------------------------------------------------------- spreadsheet


def cell_of(alias):
    try:
        c = sheet.getCellFromAlias(alias)
        if c:
            return c
    except Exception:
        pass
    for c in sheet.getNonEmptyCells():
        if sheet.getAlias(c) == alias:
            return c
    raise KeyError(alias)


def setp(alias, value, note=None):
    c = cell_of(alias)
    sheet.set(c, '=%s mm' % repr(float(value)).rstrip('0').rstrip('.'))
    if note is not None:
        sheet.set('C' + c[1:], note)


next_row = [max(int(c[1:]) for c in sheet.getNonEmptyCells()) + 1]


def addp(alias, value, note):
    r = next_row[0]
    next_row[0] += 1
    sheet.set('A%d' % r, alias)
    sheet.set('B%d' % r, '=%s mm' % repr(float(value)).rstrip('0').rstrip('.'))
    sheet.setAlias('B%d' % r, alias)
    sheet.set('C%d' % r, note)


setp('rail_soffit_z', 30 + DZ, 'Arch soffit; battery top Z 21.5 so 15 clear (8.5 until the 2026-09-27 build asked for ~75% more)')
setp('rail_groove_z0', 32 + DZ, 'Raceway floor; 2 above the soffit and the foot-well ceilings')
setp('rail_groove_z1', 39 + DZ, 'Raceway ceiling; top slab runs from here to rail_top_z')
setp('rail_top_z', 48 + DZ, 'Top of rails = underside of upper deck (48 until the 2026-09-27 build lifted it 6.5)')
setp('rail_front_foot_end', FOOT_END, 'Front foot/post rear face; lengthened from 13 for the rearward screw slot, 2.5 clear of the battery at Y 21')
setp('rail_soffit_start', SOFFIT_START, 'Arch reaches full soffit height here, facets up from the post')
setp('deck_collar_top_z', 62 + DZ, 'Mast bearing collar sits ABOVE the deck; this is its top')
setp('deck_collar_bot_z', 38 + DZ, 'Legacy (collar is above the deck now); kept in step with the lift')
setp('mast_top_z', MAST_TOP, 'Mast top; 120 until the 2026-09-27 build (+6.5 lift plus a little more)')
setp('mast_spigot_below', 3.5, 'Spigot protrusion below the deck; 3.5 since the 2026-09-26 reprint (was 5)')
addp('upper_drawn_rail_top', 48, 'rail_top_z the hard-drawn upper parts (antenna post, driver mounts, wire slot tool) were modelled at; they are placed at +(rail_top_z - this)')
addp('head_drawn_mast_top', 120, 'mast_top_z the imported head candidate was modelled at; it is placed at +(mast_top_z - this)')
addp('rail_front_well_end', WELL_END, 'Front foot well rear wall; M3 head clears it at full rearward travel')
addp('rail_front_slot_back', SLOT_BACK, 'Front foot slot moved rearward by this (screw Y 10 -> 13.5); Jim: 3-5 back, 2026-09-27')
addp('rail_head_relief', RELIEF, 'Head relief into the outboard skin of the front well; SHCS head fouled the skin over the slit')
addp('mast_screw_spacing', 42.5, 'Mast base M2 holes centre to centre; 41 widened 0.75 each side after the 2026-09-27 build (fit, not caliper)')
addp('mast_screw_y', 111, 'Mast base M2 holes Y')
addp('mast_entry_chamfer', 0.8, 'Mast socket entry chamfer, from the 2026-09-26 reprint')
for a in ('ant_base_z', 'ant_top_z', 'ant_cavity_z0', 'ant_cavity_z1', 'ant_axis_z', 'drv_inner_z'):
    c = cell_of(a)
    note = sheet.getContents('C' + c[1:])
    if 'drawn frame' not in note:
        sheet.set('C' + c[1:], note + ' [drawn frame at rail top 48; add rail_top_z - upper_drawn_rail_top]')
# no recompute yet: the deck must not move before WireSlotTool does, or the
# WireSlotEase chamfer loses its edge links in between

# ---------------------------------------------------------------- rail sketches
L = Part.LineSegment


def poly(pts):
    return [L(V(*pts[i], 0), V(*pts[(i + 1) % len(pts)], 0)) for i in range(len(pts))]


top = 48 + DZ
soff = 30 + DZ
prof = [(2, 2), (FOOT_END, 2), (FOOT_END, 28), (19.1, 31), (19.8, 34), (SOFFIT_START, soff),
        (112, soff), (113.7, 27.25), (115.4, 18), (117.2, 9), (119, 2), (135, 2), (135, top), (2, top)]
sk = O('RailOuterProfile')
assert len(sk.Geometry) == 14
sk.Geometry = poly(prof)

sk = O('RailFootWells')
assert len(sk.Geometry) == 8
ceil = soff
sk.Geometry = poly([(5, 6), (WELL_END, 6), (WELL_END, ceil), (5, ceil)]) + \
    poly([(119, 6), (132, 6), (132, ceil), (119, ceil)])

sk = O('RailGroove')
g = sk.Geometry
assert len(g) == 6 and len(sk.Constraints) == 0
new = []
for e in g:
    if isinstance(e, Part.LineSegment):
        new.append(L(V(e.StartPoint.x, e.StartPoint.y - 32, 0), V(e.EndPoint.x, e.EndPoint.y - 32, 0)))
    else:
        c = e.Center
        circ = Part.Circle(V(c.x, c.y - 32, 0), V(0, 0, 1), e.Radius)
        new.append(Part.ArcOfCircle(circ, e.FirstParameter, e.LastParameter))
sk.Geometry = new
sk.setExpression('Placement.Base.z', 'Parameters.rail_groove_z0')

sk = O('RailTabs')
g = sk.Geometry
assert len(g) == 32
new = []
for i, e in enumerate(g):
    dz = DZ if i < 24 else 0      # 0..23 raceway tabs move; 24..31 foot-well tabs stay
    new.append(L(V(e.StartPoint.x, e.StartPoint.y + dz, 0), V(e.EndPoint.x, e.EndPoint.y + dz, 0)))
sk.Geometry = new

sk = O('RailMountSlots')
sk.deleteAllGeometry()
fy = 10 + SLOT_BACK
front = [(7.3, fy - 1.7), (13.7, fy - 1.7), (13.7, fy + 1.7), (7.3, fy + 1.7)]
rear = [(10.3, 125.3), (16.7, 125.3), (16.7, 128.7), (10.3, 128.7)]
for loop in (front, rear):
    first = len(sk.Geometry)
    sk.addGeometry(poly(loop), False)
    n = len(loop)
    for i in range(n):
        sk.addConstraint(Sketcher.Constraint('Coincident', first + i, 2, first + (i + 1) % n, 1))

# ---------------------------------------------------------------- upper structure lift
UP = 'Parameters.rail_top_z - Parameters.upper_drawn_rail_top'
O('AntInsertSketch').setExpression('.Placement.Base.z', 'Parameters.rail_top_z + Parameters.deck2_thickness + Parameters.s3_boss_h')
O('AntBossPad').setExpression('Length', 'Parameters.s3_boss_h')
O('AntennaPost').setExpression('Placement.Base.z', UP)
O('WireSlotTool').setExpression('Placement.Base.z', UP)
for n in old_v5:
    O(n).setExpression('Placement.Base.z', UP)
O('DriverBoardLeft').setExpression('Placement.Base.z', '%r mm + %s' % (O('DriverBoardLeft').Placement.Base.z, UP))
O('DriverMountLeft').setExpression('Placement.Base.z', UP)
O('DrvFootReliefTool').setExpression('Placement.Base.z', UP)

HEAD_UP = 'Parameters.mast_top_z - Parameters.head_drawn_mast_top'
for o in HEAD:
    o.setExpression('Placement.Base.z', '%r mm + %s' % (o.Placement.Base.z, HEAD_UP))
O('MastIndexFlatTool').setExpression('Placement.Base.z', HEAD_UP)

# ---------------------------------------------------------------- mast base
O('MastBaseEntryChamfer').setExpression('Size', 'Parameters.mast_entry_chamfer')
for skn in ('MastPlateScrews', 'ShieldScrewSketch'):
    s = O(skn)
    assert len(s.Geometry) == 2
    tag = 'M2' if skn == 'MastPlateScrews' else 'Sh'
    for gi, sign in ((0, '-'), (1, '+')):
        c = s.Geometry[gi].Center
        ix = s.addConstraint(Sketcher.Constraint('DistanceX', -1, 1, gi, 3, c.x))
        s.renameConstraint(ix, '%sX%d' % (tag, gi + 1))
        s.setExpression('.Constraints.%sX%d' % (tag, gi + 1),
                        'Parameters.center_hole_x %s Parameters.mast_screw_spacing / 2' % sign)
        iy = s.addConstraint(Sketcher.Constraint('DistanceY', -1, 1, gi, 3, c.y))
        s.renameConstraint(iy, '%sY%d' % (tag, gi + 1))
        s.setExpression('.Constraints.%sY%d' % (tag, gi + 1), 'Parameters.mast_screw_y')

# ---------------------------------------------------------------- head relief
# YZ sketch on the front well's outboard wall (X 8.5), pocketed outboard
body = O('SideRailLeft')
rs = body.newObject('Sketcher::SketchObject', 'RailHeadReliefSketch')
rs.Label = 'Front foot head relief'
rs.Placement = O('RailFootWells').Placement
rs.setExpression('.Placement.Base.x', 'Parameters.rail_outer_x + Parameters.rail_width - Parameters.rail_well_depth')
rs.addGeometry(poly([(fy - 3.0, 6), (WELL_END, 6), (WELL_END, 6 + RELIEF_H), (fy - 3.0, 6 + RELIEF_H)]), False)
for i in range(4):
    rs.addConstraint(Sketcher.Constraint('Coincident', i, 2, (i + 1) % 4, 1))
rp = body.newObject('PartDesign::Pocket', 'RailHeadRelief')
rp.Label = 'Front foot head relief'
rp.Profile = rs
rp.Type = 'Length'
rp.Length = RELIEF
rp.setExpression('Length', 'Parameters.rail_head_relief')
rp.Reversed = False
rs.Visibility = False
doc.recompute()
# direction check: relief must remove material outboard of X 8.5, not inboard
if body.Shape.isInside(V(8.5 - RELIEF / 2, fy, 7.5), 1e-6, True):
    rp.Reversed = True
    doc.recompute()
check(not body.Shape.isInside(V(8.5 - RELIEF / 2, fy, 7.5), 1e-6, True)
      and body.Shape.isInside(V(8.5 - RELIEF - 0.3, fy, 7.5), 1e-6, True), 'head relief cut outboard, skin left behind it')

# DrvFootReliefCut is a PartDesign::Boolean inside DriverMountLeft.  Whether its
# tool must move with the body depends on how the Boolean maps a global tool into
# a moved body, so try the tool both ways and keep the one that leaves the part intact.
def dml_intact():
    t = old_dml.copy(); t.translate(V(0, 0, DZ))
    n = O('DriverMountLeft').Shape
    return abs(n.Volume - old_dml.Volume) < 0.05 and abs(t.common(n).Volume - n.Volume) < 0.1


if not dml_intact():
    O('DrvFootReliefTool').setExpression('Placement.Base.z', None)
    O('DrvFootReliefTool').Placement.Base.z = 0
    doc.recompute()
    p('INFO DrvFootReliefTool left in place: the Boolean follows its body placement')

# ================================================================ checks
bad = [o.Name for o in doc.Objects if 'Invalid' in o.State or 'Error' in o.State]
check(not bad, 'no objects in error after recompute %s' % bad)

rail = O('SideRailLeft').Shape
railR = O('SideRailRight').Shape
check(rail.isValid() and len(rail.Solids) == 1, 'left rail one valid solid')
check(railR.isValid() and len(railR.Solids) == 1, 'right rail one valid solid')
bb = rail.BoundBox
check(abs(bb.ZMax - top) < 1e-6 and abs(bb.ZMin - 2) < 1e-6, 'rail Z 2..%g (got %.3f..%.3f)' % (top, bb.ZMin, bb.ZMax))
check(abs(bb.YMin - 2) < 1e-6 and abs(bb.YMax - 135) < 1e-6, 'rail Y 2..135 unchanged')

bat = O('BatteryBox').Shape
for nm, r in (('L', rail), ('R', railR)):
    check(r.common(bat).Volume < 1e-6, 'rail %s does not touch the battery' % nm)
# lowest rail material above the battery footprint = the soffit clearance
over = rail.common(Part.makeBox(79, 75.5, 60, V(0, 21, 2)))
zlow = min(v.Point.z for v in over.Vertexes) if over.Volume > 0 else None
check(zlow is not None and abs(zlow - soff) < 0.51, 'lowest rail over the battery footprint Z %.2f (soffit %.1f)' % (zlow, soff))
p('INFO battery-to-soffit clearance %.2f (was 8.50)' % (zlow - 21.5))
dfront = rail.distToShape(bat)[0]
p('INFO min rail-to-battery distance %.2f' % dfront)
check(dfront >= 2.49, 'rail keeps >= 2.5 from the battery holder (%.2f)' % dfront)

# screw path, front foot (left; right is a mirror) -- head, shank, bearing
deck = O('ChassisDeck').Shape


def screw_ok(r, x, y, mirror=False):
    if mirror:
        x = 79 - x
    head = Part.makeCylinder(2.8, 3.0, V(x, y, 6.0))       # M3 SHCS 5.5 + 0.05 radial
    shank = Part.makeCylinder(1.5, 12.0, V(x, y, -4.0))
    # bearing = area of the head's footprint that has solid floor under it,
    # sampled as a 0.01 slab just below the floor top
    slab = Part.makeCylinder(2.75, 0.01, V(x, y, 5.985))
    b_area = r.common(slab).Volume / 0.01
    return (r.common(head).Volume, r.common(shank).Volume, deck.common(shank).Volume, b_area)


# Bearing: a 5.5 head across a 3.4 slot bears on two lunes, ~6.3 mm2.  That is
# what every slotted foot has had since v1; require no less.
BEAR_MIN = 6.0
fails = 0
# every X the shank can take inside the modelled 4 mm front slit (centre 10.5)
for x in (10.0, 10.25, 10.5, 10.75, 11.0):
    for nm, r, m in (('L', rail, False), ('R', railR, True)):
        hv, sv, dv, ba = screw_ok(r, x, fy, m)
        ok = hv < 1e-6 and sv < 1e-6 and dv < 1e-6 and ba >= BEAR_MIN
        if not ok:
            fails += 1
        p('  front %s screw at (%.2f, %.2f): head %.3f shank-rail %.3f shank-deck %.3f bearing %.1f mm2 %s'
          % (nm, 79 - x if m else x, fy, hv, sv, dv, ba, 'ok' if ok else 'BAD'))
check(fails == 0, 'M3 seats and passes at every X across the modelled front slit, both rails')
rfails = 0
for x in (12.0, 13.5, 15.0):
    hv, sv, dv, ba = screw_ok(rail, x, 127.0)
    p('  rear L screw at (%.2f, 127): head %.3f shank-rail %.3f bearing %.1f mm2' % (x, hv, sv, ba))
    rfails += 0 if (hv < 1e-6 and sv < 1e-6 and ba >= BEAR_MIN) else 1
check(rfails == 0, 'rear-foot M3 seats as before')
# how far back the real right-front slit can start and still take the screw
p('INFO front screw shank front edge now at Y %.1f (was 8.5); passes any real slit starting up to %.1f behind the modelled Y 7.5'
  % (fy - 1.5, fy - 1.5 - 7.5))
# wall between the front well and the post face
wall = rail.common(Part.makeBox(9.5, FOOT_END - WELL_END, 24, V(8.5, WELL_END, 6)))
check(abs(wall.Volume - 9.5 * (FOOT_END - WELL_END) * 24) < 1.0, 'front well rear wall is solid %.1f thick' % (FOOT_END - WELL_END))
# raceway still sealed from the wells (2 mm floor over each well)
for y in (10.0, 125.0):
    seg = rail.common(Part.makeCylinder(0.5, 2.0, V(12.0, y, soff)))
    check(abs(seg.Volume - math.pi * 0.25 * 2.0) < 1e-3, 'raceway floor solid over well at Y %g' % y)

# upper deck: same part, only lifted
nd = O('UpperDeck').Shape
check(abs(nd.Volume - old_deck.Volume) < 0.01, 'upper deck volume unchanged (%.2f vs %.2f)' % (nd.Volume, old_deck.Volume))
od = old_deck.copy(); od.translate(V(0, 0, DZ))
check(abs(od.common(nd).Volume - nd.Volume) < 0.05, 'upper deck is the old deck moved up %.1f' % DZ)
for nm, old, new in (('AntennaPost', old_ant, O('AntennaPost').Shape),
                     ('DriverMountLeft', old_dml, O('DriverMountLeft').Shape),
                     ('DriverBoardLeft', old_board, O('DriverBoardLeft').Shape)):
    t = old.copy(); t.translate(V(0, 0, DZ))
    check(abs(new.Volume - old.Volume) < 0.05 and abs(t.common(new).Volume - new.Volume) < 0.1,
          '%s moved up %.1f intact' % (nm, DZ))
for n, old in old_v5.items():
    t = old.copy(); t.translate(V(0, 0, DZ))
    check(abs(t.BoundBox.ZMin - O(n).Shape.BoundBox.ZMin) < 1e-6, '%s moved up %.1f' % (n, DZ))
for o in HEAD:
    t = old_head[o.Name]
    if t.isNull() or not t.Vertexes:
        continue
    check(abs(o.Shape.BoundBox.ZMin - (t.BoundBox.ZMin + MAST_TOP - 120)) < 1e-6, 'head %s moved up %.0f' % (o.Name, MAST_TOP - 120))

tube = O('MastTube').Shape
check(tube.isValid() and len(tube.Solids) == 1, 'mast tube one valid solid')
check(abs(tube.BoundBox.ZMax - MAST_TOP) < 1e-6 and abs(tube.BoundBox.ZMin - 6) < 1e-6, 'mast tube Z 6..%g' % MAST_TOP)
flat = O('MastIndexFlatTool').Shape
check(abs(tube.common(flat).Volume) < 1e-3 and abs(flat.BoundBox.ZMax - MAST_TOP) < 1e-6, 'index flat cut at the new mast top')
exp_vol = old_tube_vol + math.pi * (10 ** 2 - 6 ** 2) * (MAST_TOP - 120)
check(abs(tube.Volume - exp_vol) < 0.5, 'mast tube volume = old + %g of tube (%.1f vs %.1f)' % (MAST_TOP - 120, tube.Volume, exp_vol))

mb = O('MastBase').Shape
check(mb.isValid() and len(mb.Solids) == 1, 'mast base one valid solid')
check(abs(mb.BoundBox.ZMin + 3.5) < 1e-6, 'mast spigot 3.5 below deck')
holes = sorted([(round(e.Curve.Center.x, 3), round(e.Curve.Center.y, 3)) for e in mb.Edges
                if hasattr(e, 'Curve') and e.Curve.TypeId == 'Part::GeomCircle'
                and abs(e.Curve.Radius - 1.3) < 1e-6 and abs(e.Curve.Center.z - 6) < 1e-6])
check(holes == [(18.25, 111.0), (60.75, 111.0)], 'mast base M2 holes at %s' % holes)
circles = [(round(e.Curve.Radius * 2, 3), round(e.CenterOfMass.z, 3)) for e in mb.Edges
           if hasattr(e, 'Curve') and e.Curve.TypeId == 'Part::GeomCircle']
check((22.0, 20.0) in circles and (20.4, 19.2) in circles, 'socket entry chamfer 0.8')
sh_holes = sorted([(round(e.Curve.Center.x, 3), round(e.Curve.Center.y, 3)) for e in O('PowerShield').Shape.Edges
                   if hasattr(e, 'Curve') and e.Curve.TypeId == 'Part::GeomCircle' and abs(e.Curve.Radius - 1.3) < 1e-6])
check(set(sh_holes) >= {(18.25, 111.0), (60.75, 111.0)}, 'power shield legs follow the mast screws %s' % sorted(set(sh_holes)))

# mast still clears the upper-deck bore and the deck still clears the rails' screw pattern
check(tube.common(nd).Volume < 1e-6, 'mast tube clears the upper deck bearing')

after = shapes()
after_ov = overlaps(after)
newer = []
for k, v in after_ov.items():
    old = before_ov.get(k, 0.0)
    if v > old + 0.05:
        newer.append((k, round(old, 2), round(v, 2)))
for k, v in before_ov.items():
    if k not in after_ov:
        p('INFO overlap gone', k, round(v, 2))
check(not newer, 'no new or grown overlaps across %d solids %s' % (len(after), newer))

if FAILS:
    p('REFUSING TO SAVE: %d checks failed' % len(FAILS))
    for f in FAILS:
        p('  -', f)
    sys.exit(2)
if DRY:
    p('DRY RUN OK, not saved')
    sys.exit(0)

doc.save()
p('SAVED', MASTER)

# ================================================================ print meshes
os.makedirs(OUTDIR, exist_ok=True)


def orient(shape, down):
    s = shape.copy()
    rot = App.Rotation(down, V(0, 0, -1))
    s.Placement = App.Placement(V(), rot).multiply(s.Placement)
    b = s.BoundBox
    s.translate(V(-b.XMin, -b.YMin, -b.ZMin))
    return s


def bed_area(s):
    a = 0.0
    for f in s.Faces:
        if f.Surface.TypeId == 'Part::GeomPlane' and abs(f.BoundBox.ZMax) < 1e-6:
            a += f.Area
    return a


def export(shape, down, fname, note):
    s = orient(shape, down)
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.05, Relative=False)
    ok = (m.isSolid() and not m.hasNonManifolds() and not m.hasSelfIntersections()
          and abs(m.BoundBox.ZMin) < 1e-6 and m.BoundBox.XLength < 220 and m.BoundBox.YLength < 220
          and m.BoundBox.ZLength < 250 and abs(m.Volume - shape.Volume) / shape.Volume < 0.005)
    check(ok, 'mesh %s solid/manifold/on bed/volume' % fname)
    path = OUTDIR + '/' + fname
    m.write(path)
    return {'file': fname, 'note': note, 'bounds': [round(m.BoundBox.XLength, 2), round(m.BoundBox.YLength, 2),
            round(m.BoundBox.ZLength, 2)], 'bed_area_mm2': round(bed_area(s), 1),
            'volume_mm3': round(shape.Volume, 1), 'pla_g_solid': round(shape.Volume * 1.24e-3, 1),
            'facets': m.CountFacets}


coupon_src = railR.common(Part.makeBox(24, 22, 10, V(55, 0, 2)))
check(len(coupon_src.Solids) == 1, 'front-foot coupon is one solid')
prints = [
    export(rail, V(-1, 0, 0), 'Gladiator_SideRail_L_v2-tall_print-on-outboard-face.stl',
           'Outboard (-X) face down, raceway opens upward.'),
    export(railR, V(1, 0, 0), 'Gladiator_SideRail_R_v2-tall_print-on-outboard-face.stl',
           'Outboard (+X) face down, raceway opens upward.'),
    export(tube, V(0, 0, -1), 'Gladiator_MastTube_v2-Z130_print-vertical.stl',
           'Vertical as modelled, 124 tall. Brim recommended.'),
    export(mb, V(0, 0, 1), 'Gladiator_MastBase_v2-holes-42p5_print-spigot-UP.stl',
           'Upside down, spigot up; thin collar ring on the bed - brim, support under the outer plate.'),
    export(coupon_src, V(0, 0, -1), 'Gladiator_Coupon_RailFrontFoot_R_v2_deck-face-down.stl',
           'Bottom 10 mm of the new right front foot. Screw it to the real right front slit before printing rails.'),
]
if FAILS:
    p('MESH CHECKS FAILED -- master saved, meshes not handed off')
    sys.exit(3)
for pr in prints:
    shutil.copy2(OUTDIR + '/' + pr['file'], INCOMING + '/' + pr['file'])
json.dump({'generated': ts, 'script': 'scripts/apply_first_build_fixes.py', 'prints': prints,
           'overlaps_before': {'|'.join(k): round(v, 3) for k, v in before_ov.items()},
           'overlaps_after': {'|'.join(k): round(v, 3) for k, v in after_ov.items()}},
          open(OUTDIR + '/validation.json', 'w'), indent=1)
for pr in prints:
    p('PRINT', json.dumps(pr))
p('DONE')
