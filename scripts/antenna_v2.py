import FreeCAD as App
import Part
import Sketcher

doc = App.openDocument('/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd')
sheet = doc.getObject('Parameters')
XZ = App.Rotation(App.Vector(1, 0, 0), 90)      # u->X, v->Z, normal -Y
YZ = App.Rotation(App.Vector(1, 1, 1), 120)     # u->Y, v->Z, normal +X


def sp(row, name, val, note):
    sheet.set('A%d' % row, name)
    sheet.set('B%d' % row, '%s mm' % val)
    sheet.setAlias('B%d' % row, name)
    sheet.set('C%d' % row, note)


for row, n, v, note in [
    (109, 'deck_collar_top_z', 62.0, 'Mast bearing collar now sits ABOVE the deck; this is its top'),
    (110, 'ant_plate_y0', 2.0, 'Antenna bulkhead plate front face'),
    (111, 'ant_plate_t', 6.0, 'Plate thickness; counterbored to leave a thin clamping web'),
    (112, 'ant_web_t', 2.0, 'Clamped web at the SMA hole; standard bulkheads take <= 2.2 panel'),
    (113, 'ant_cbore_dia', 11.0, 'Counterbore clearing the connector shoulder / 8 A-F hex'),
    (114, 'ant_axis_z', 78.0, 'SMA axis height; tail runs rearward OVER the breadboard (top 73.5)'),
    (115, 'ant_hole_x', 68.0, 'SMA axis X'),
]:
    sp(row, n, v, note)

# ------------------ DECK: collar above the plate, antenna bosses relocated ------------------
cs = doc.getObject('DeckCollarSketch')
cs.Placement = App.Placement(App.Vector(0, 0, 52.0), App.Rotation())
cs.setExpression('.Placement.Base.z', 'Parameters.rail_top_z + Parameters.deck2_thickness')
cp = doc.getObject('DeckCollarPad')
cp.Reversed = False
cp.setExpression('Length',
                 'Parameters.deck_collar_top_z - Parameters.rail_top_z - Parameters.deck2_thickness')

bs = doc.getObject('DeckMastBoreSketch')
bs.Placement = App.Placement(App.Vector(0, 0, 62.0), App.Rotation())
bs.setExpression('.Placement.Base.z', 'Parameters.deck_collar_top_z')
doc.getObject('DeckMastBoreCut').setExpression(
    'Length', 'Parameters.deck_collar_top_z - Parameters.rail_top_z')

ANT_BOSS = [(60.0, 10.0), (76.0, 10.0)]
for nm, r in (('AntBossSketch', 4.5), ('AntInsertSketch', 2.2)):
    sk = doc.getObject(nm)
    while sk.GeometryCount > 0:
        sk.delGeometry(sk.GeometryCount - 1)
    for (x, y) in ANT_BOSS:
        gi = sk.addGeometry(Part.Circle(App.Vector(x, y, 0), App.Vector(0, 0, 1), r), False)
        sk.addConstraint(Sketcher.Constraint('Radius', gi, r))
doc.recompute()

# ------------------ ANTENNA MOUNT v2 ------------------
old = doc.getObject('AntennaPost')
if old:
    for c in list(old.Group):
        doc.removeObject(c.Name)
    doc.removeObject('AntennaPost')
doc.recompute()

ap = doc.addObject('PartDesign::Body', 'AntennaPost')
ap.Label = 'Antenna bulkhead mount'


def poly(name, label, pts, pl):
    sk = doc.addObject('Sketcher::SketchObject', name)
    sk.Label = label
    ap.addObject(sk)
    sk.Placement = pl
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        sk.addGeometry(Part.LineSegment(App.Vector(a[0], a[1], 0), App.Vector(b[0], b[1], 0)), False)
    for i in range(n):
        sk.addConstraint(Sketcher.Constraint('Coincident', i, 2, (i + 1) % n, 1))
    return sk


def feat(kind, name, label, prof, length, rev=False):
    f = doc.addObject('PartDesign::' + kind, name)
    f.Label = label
    ap.addObject(f)
    f.Profile = prof
    f.Type = 'Length'
    f.Length = length
    f.Reversed = rev
    doc.recompute()
    return f


# base flange, X 56..80, Y 2..13, Z 58..62
fl = poly('AntFlangeProfile', 'Base flange',
          [(56.0, 58.0), (80.0, 58.0), (80.0, 62.0), (56.0, 62.0)],
          App.Placement(App.Vector(0, 2.0, 0), XZ))
feat('Pad', 'AntFlangePad', 'Base flange', fl, 11.0, rev=True)

# bulkhead plate, X 56..80, Z 58..86, 6 thick (Y 2..8)
pl = poly('AntPlateProfile', 'Bulkhead plate',
          [(56.0, 58.0), (80.0, 58.0), (80.0, 86.0), (56.0, 86.0)],
          App.Placement(App.Vector(0, 2.0, 0), XZ))
feat('Pad', 'AntPlatePad', 'Bulkhead plate', pl, 6.0, rev=True)

# gussets bracing the plate back down onto the flange
for i, x in enumerate((56.0, 76.0)):
    g = poly('AntGussetProfile%d' % (i + 1), 'Gusset %d' % (i + 1),
             [(8.0, 62.0), (13.0, 62.0), (8.0, 80.0)],
             App.Placement(App.Vector(x, 0, 0), YZ))
    feat('Pad', 'AntGussetPad%d' % (i + 1), 'Gusset %d' % (i + 1), g, 4.0)

# fixing holes through the flange into the deck bosses
fh = doc.addObject('Sketcher::SketchObject', 'AntFixHoles')
fh.Label = 'Fixing holes'
ap.addObject(fh)
fh.Placement = App.Placement(App.Vector(0, 0, 62.0), App.Rotation())
for (x, y) in ANT_BOSS:
    gi = fh.addGeometry(Part.Circle(App.Vector(x, y, 0), App.Vector(0, 0, 1), 1.7), False)
    fh.addConstraint(Sketcher.Constraint('Radius', gi, 1.7))
doc.recompute()
feat('Pocket', 'AntFixHoleCut', 'Fixing holes', fh, 4.0)

# counterbore from the REAR face: the connector shoulder seats here,
# leaving a 2 mm clamping web that a standard bulkhead nut can actually clamp
cb = doc.addObject('Sketcher::SketchObject', 'AntCboreSketch')
cb.Label = 'Connector counterbore'
ap.addObject(cb)
cb.Placement = App.Placement(App.Vector(0, 8.0, 0), XZ)
gi = cb.addGeometry(Part.Circle(App.Vector(68.0, 78.0, 0), App.Vector(0, 0, 1), 5.5), False)
cb.renameConstraint(cb.addConstraint(Sketcher.Constraint('Radius', gi, 5.5)), 'CboreR')
cb.setExpression('.Constraints.CboreR', 'Parameters.ant_cbore_dia / 2')
doc.recompute()
feat('Pocket', 'AntCboreCut', 'Connector counterbore', cb, 4.0)

# the SMA through-hole
sm = doc.addObject('Sketcher::SketchObject', 'AntSmaSketch')
sm.Label = 'SMA bulkhead hole'
ap.addObject(sm)
sm.Placement = App.Placement(App.Vector(0, 8.0, 0), XZ)
gi = sm.addGeometry(Part.Circle(App.Vector(68.0, 78.0, 0), App.Vector(0, 0, 1), 3.25), False)
sm.renameConstraint(sm.addConstraint(Sketcher.Constraint('Radius', gi, 3.25)), 'SmaR')
sm.setExpression('.Constraints.SmaR', 'Parameters.ant_sma_dia / 2')
doc.recompute()
feat('Pocket', 'AntSmaCut', 'SMA bulkhead hole', sm, 8.0)
ap.Tip = doc.getObject('AntSmaCut')
doc.recompute()
doc.save()

print('=== deck: collar moved above the plate ===')
d = doc.getObject('UpperDeck').Shape
print('  bbox:', d.BoundBox)
print('  off-axis probe (X 51.5, Y 113) 46=under 50=plate 54/58/60=collar 64=above:')
print('   ', ' '.join('%d:%s' % (z, 'S' if d.isInside(App.Vector(51.5, 113.0, float(z)), 1e-7, True) else 'o')
                      for z in (46, 50, 54, 58, 60, 64)))
print('  on-axis (bore must be open all the way):')
print('   ', ' '.join('%d:%s' % (z, 'S' if d.isInside(App.Vector(39.5, 113.0, float(z)), 1e-7, True) else 'o')
                      for z in (46, 50, 54, 58, 61, 64)))

print()
print('=== antenna mount v2 ===')
a = doc.getObject('AntennaPost').Shape
print('  valid=%s solids=%d shells=%d vol=%.0f' % (a.isValid(), len(a.Solids), len(a.Shells), a.Volume))
print('  bbox:', a.BoundBox)
print('  clamping web, probe along Y on the hole axis (X68, Z78) - all should be open:')
print('   ', ' '.join('%.1f:%s' % (y, 'S' if a.isInside(App.Vector(68.0, float(y), 78.0), 1e-7, True) else 'o')
                      for y in (1.5, 2.5, 3.5, 4.5, 6.0, 8.0, 10.0)))
print('  web + counterbore, probe off-axis (X 72, Z 78): expect S,S then o through the cbore:')
print('   ', ' '.join('%.1f:%s' % (y, 'S' if a.isInside(App.Vector(72.0, float(y), 78.0), 1e-7, True) else 'o')
                      for y in (2.5, 3.5, 5.0, 7.0, 9.0)))

print()
print('=== clashes ===')
names = ['ChassisDeck', 'BatteryBox', 'SideRailLeft', 'SideRailRight', 'MastBase', 'MastTube',
         'UpperDeck', 'S3Board', 'Breadboard', 'PowerShield', 'DriverMountLeft', 'DriverMountRight',
         'AntennaPost', 'DriverBoardLeft', 'DriverBoardRight', 'Neck_Main', 'GH44_Dual_Carrier']
bad = 0
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        oi, oj = doc.getObject(names[i]), doc.getObject(names[j])
        if not oi or not oj:
            continue
        v = oi.Shape.common(oj.Shape).Volume
        if v > 0.001:
            bad += 1
            pair = names[i] + names[j]
            note = ' (expected)' if 'DriverBoard' in pair and 'DriverMount' in pair else ''
            print('  CLASH %-18s vs %-18s %.3f%s' % (names[i], names[j], v, note))
print('  total: %d' % bad)
