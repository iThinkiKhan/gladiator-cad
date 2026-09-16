import math
import FreeCAD as App
import Part

DOC = '/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd'
doc = App.openDocument(DOC)
sheet = doc.getObject('Parameters')


def sp(row, name, val, note):
    sheet.set('A%d' % row, name)
    sheet.set('B%d' % row, '%s mm' % val)
    sheet.setAlias('B%d' % row, name)
    sheet.set('C%d' % row, note)


for row, n, v, note in [
    (105, 'drv_board_len', 49.5, 'Driver PCB length along Y'),
    (106, 'drv_board_wid', 51.0, 'Driver PCB width across the cant (heatsink runs full width)'),
    (107, 'drv_comp_h', 13.0, 'Component height off the PCB, opposite face from the heatsink'),
    (108, 'drv_hs_h', 28.0, 'Heatsink height off the PCB (measured fin-tip to PCB)'),
]:
    sp(row, n, v, note)
doc.recompute()

for nm in ('DriverBoardLeft', 'DriverBoardRight'):
    if doc.getObject(nm):
        doc.removeObject(nm)
doc.recompute()

TH = math.radians(60.0)
CS, SN = math.cos(TH), math.sin(TH)
AX, AZ = 2.0, 84.0            # frame's own base origin (w=0 here, NOT the PCB plane)
FT = 12.0                     # frame thickness; PCB bolts to the frame's outboard face (w=FT)
OUTX, OUTZ = -SN, CS          # +w direction: outboard, toward the heatsink/fins
L, WID = 49.5, 51.0
COMP_H, HS_H = 13.0, 28.0     # component depth and heatsink depth off the PCB

# PCB plane sits at w = FT (=12). Envelope spans from (FT - COMP_H) to (FT + HS_H) in w.
w0 = FT - COMP_H              # -1.0 -- starts just inboard of the frame's own base plane
w_span = COMP_H + FT - w0 + HS_H - FT  # = COMP_H + HS_H, kept explicit for clarity
w_span = COMP_H + HS_H         # 41.0, matches the measured 41 "fin tip to tallest component"

m = App.Matrix()
m.A11, m.A21, m.A31 = 0.0, 1.0, 0.0          # local X (Length) -> global Y  (the 49.5 axis)
m.A12, m.A22, m.A32 = -CS, 0.0, -SN          # local Y (Width)  -> the 51 cant axis
m.A13, m.A23, m.A33 = OUTX, 0.0, OUTZ        # local Z (Height) -> perpendicular to the PCB
ROT = App.Rotation(m)

origin = App.Vector(AX + w0 * OUTX, 90.0, AZ + w0 * OUTZ)

left = doc.addObject('Part::Box', 'DriverBoardLeft')
left.Label = 'Driver PCB + components + heatsink (reference envelope), left'
left.Length = L
left.Width = WID
left.Height = w_span
left.Placement = App.Placement(origin, ROT)
left.setExpression('.Length', 'Parameters.drv_board_len')
left.setExpression('.Width', 'Parameters.drv_board_wid')
left.setExpression('.Height', 'Parameters.drv_comp_h + Parameters.drv_hs_h')
doc.recompute()

right = doc.addObject('Part::Mirroring', 'DriverBoardRight')
right.Label = 'Driver PCB + components + heatsink (reference envelope), right'
right.Source = left
right.Normal = App.Vector(1, 0, 0)
right.Base = App.Vector(39.5, 0, 0)
right.setExpression('.Base.x', 'Parameters.deck_width / 2')
doc.recompute()
doc.save()

lb = left.Shape.BoundBox
print('DriverBoardLeft  bbox', lb)
print('  volume', round(left.Shape.Volume, 1), '  valid', left.Shape.isValid())
rb = right.Shape.BoundBox
print('DriverBoardRight bbox', rb)

print()
print('=== sanity: matches the hand-derived envelope? ===')
print('  expected X range roughly -48..14 (fin tip to component tip), got %.1f..%.1f'
      % (lb.XMin, lb.XMax))
print('  expected Z range roughly 34..102, got %.1f..%.1f' % (lb.ZMin, lb.ZMax))

print()
print('=== does the frame stay inside this envelope (sanity, not a hard requirement)? ===')
frame = doc.getObject('DriverMountLeft').Shape
print('  frame bbox ', frame.BoundBox)

print()
print('=== clashes against everything actually built (should be 0 at current 79-wide deck) ===')
names = ['UpperDeck', 'SideRailLeft', 'SideRailRight', 'MastTube', 'MastBase', 'S3Board',
         'Breadboard', 'PowerShield', 'AntennaPost', 'BatteryBox', 'ChassisDeck',
         'DriverMountLeft', 'DriverMountRight']
found = False
for side, shp in (('left', left.Shape), ('right', right.Shape)):
    for nm in names:
        v = round(shp.common(doc.getObject(nm).Shape).Volume, 4)
        if v > 0.001:
            found = True
            print('  CLASH DriverBoard%s vs %-16s %s' % (side, nm, v))
print('  none' if not found else '')

print()
print('=== does this envelope correctly RE-DETECT the earlier widen-to-85 conflict? ===')
X0, X1 = -3.0, 82.0
box85 = Part.makeBox(X1 - X0, 140.0, 4.0, App.Vector(X0, 0, 48.0))
clash = box85.common(left.Shape)
print('  clash volume vs an 85-wide test deck:', round(clash.Volume, 4),
      '(nonzero here would CONFIRM the envelope catches what pure geometry missed)')

bad = [(o.Name, o.State) for o in doc.Objects if o.State and 'Invalid' in str(o.State)]
print()
print('invalid:', bad if bad else 'none')
