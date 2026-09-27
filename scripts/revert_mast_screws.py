"""Revert mast_screw_spacing to the printed v1 value (41) after Jim's 2026-09-27 correction:
the real deck pilots are CLOSER together than the printed base's holes, not wider.
Held at 41 until the pilot pair is measured."""
import sys, shutil, time
import FreeCAD as App


def p(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n'); sys.stdout.flush()


M = '/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd'
shutil.copy2(M, '/home/buralien/projects/gladiator-cad/cad/master/drafts/Gladiator_Master.pre-mast-screw-revert.%s.FCStd'
             % time.strftime('%Y%m%d-%H%M%S'))
doc = App.openDocument(M)
sh = doc.getObject('Parameters')
c = sh.getCellFromAlias('mast_screw_spacing')
sh.set(c, '=41 mm')
sh.set('C' + c[1:], 'Mast base M2 holes c-t-c. HELD at printed v1 value: real pilots are closer together '
       '(half a pilot visible through each printed hole, 2026-09-27). Awaiting caliper measurement.')
# Installed cells stand 4 above the holder (Jim, 2026-09-27). Envelope over the whole footprint.
r = max(int(x[1:]) for x in sh.getNonEmptyCells()) + 1
sh.set('A%d' % r, 'battery_cell_protrusion')
sh.set('B%d' % r, '=4 mm')
sh.setAlias('B%d' % r, 'battery_cell_protrusion')
sh.set('C%d' % r, 'Installed 18650 cells stand this far above the holder top (Jim, 2026-09-27)')
cells = doc.getObject('BatteryCells') or doc.addObject('Part::Box', 'BatteryCells')
cells.Label = 'Battery cells above holder (reference envelope)'
cells.setExpression('Length', 'Parameters.battery_width')
cells.setExpression('Width', 'Parameters.battery_length')
cells.setExpression('Height', 'Parameters.battery_cell_protrusion')
cells.setExpression('.Placement.Base.y', 'Parameters.battery_front_gap')
cells.setExpression('.Placement.Base.z', 'Parameters.deck_thickness + Parameters.battery_box_height')
doc.recompute()
rails = [doc.getObject(n).Shape for n in ('SideRailLeft', 'SideRailRight')]
p('cells box Z %.2f..%.2f, rail overlap %.4f, clearance to soffit %.2f' % (
    cells.Shape.BoundBox.ZMin, cells.Shape.BoundBox.ZMax,
    sum(cells.Shape.common(s).Volume for s in rails),
    min(s.distToShape(cells.Shape)[0] for s in rails)))


def holes(o):
    return sorted({(round(e.Curve.Center.x, 3), round(e.Curve.Center.y, 3)) for e in doc.getObject(o).Shape.Edges
                   if hasattr(e, 'Curve') and e.Curve.TypeId == 'Part::GeomCircle' and abs(e.Curve.Radius - 1.3) < 1e-6})


mb, ps = holes('MastBase'), holes('PowerShield')
ok = mb == [(19.0, 111.0), (60.0, 111.0)] and set(ps) >= set(mb)
p('MastBase', mb, 'PowerShield', ps)
bad = [o.Name for o in doc.Objects if 'Invalid' in o.State or 'Error' in o.State]
if not ok or bad or not doc.getObject('MastBase').Shape.isValid():
    p('REFUSING TO SAVE', bad); sys.exit(2)
doc.save()
p('SAVED')
