"""Correct the BatteryCells envelope after Jim's 2026-10-01 observation that installed cells are
negligibly over the holder rim.  The 2026-09-27 value (4 above the holder) is superseded.
0.5 is a conservative stand-in for "negligible", not a measurement.  Only the spreadsheet cell
changes; BatteryCells already follows it by expression."""
import shutil
import sys
import time
import FreeCAD as App


def p(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n'); sys.stdout.flush()


M = '/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd'
shutil.copy2(M, '/home/buralien/projects/gladiator-cad/cad/master/drafts/Gladiator_Master.pre-cell-height.%s.FCStd'
             % time.strftime('%Y%m%d-%H%M%S'))
doc = App.openDocument(M)
sh = doc.getObject('Parameters')
cell = sh.getCellFromAlias('battery_cell_protrusion')
before = sh.get(cell)
sh.set(cell, '=0.5 mm')
sh.set('C' + cell[1:], 'Installed 18650 cells stand this far above the holder top. Jim 2026-10-01: negligibly over the rim; '
       '0.5 is a conservative stand-in, not a measurement. Was 4 (Jim 2026-09-27), superseded.')
doc.recompute()
cells = doc.getObject('BatteryCells')
bb = cells.Shape.BoundBox
p('before', before, '-> cells box Z %.2f..%.2f' % (bb.ZMin, bb.ZMax))
bad = [o.Name for o in doc.Objects if 'Invalid' in o.State or 'Error' in o.State]
ok = abs(bb.ZMin - 21.5) < 1e-6 and abs(bb.ZMax - 22.0) < 1e-6 and cells.Shape.isValid()
rails = [doc.getObject(n).Shape for n in ('SideRailLeft', 'SideRailRight')]
p('rail overlap %.4f' % sum(cells.Shape.common(s).Volume for s in rails))
if not ok or bad:
    p('REFUSING TO SAVE', bad); sys.exit(2)
doc.save()
p('SAVED')
