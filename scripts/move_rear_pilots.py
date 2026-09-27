"""Move the rear M2 pilot holes 1.2 outboard (both pairs), per Jim 2026-09-27, and tie the
mast base screw holes to the same deck formula so they cannot drift apart again.

Jim, after the first build: the printed mast base's holes (19 / 60) sit inboard of the real
pilots by about 3/4 of a pilot diameter (1.2); half of each pilot is visible through them.
The Y 128 pair is exactly aligned with the Y 111 pair in X.  Correction to the reverse-model's
hole POSITIONS at Jim's direction -- no feature is added to the aluminium.
"""
import os
import shutil
import sys
import time

import FreeCAD as App
import MeshPart
import Part

V = App.Vector
REPO = '/home/buralien/projects/gladiator-cad'
M = REPO + '/cad/master/Gladiator_Master.FCStd'
OUTDIR = REPO + '/cad/build2-20260927'
INCOMING = '/home/buralien/3D-Printer/Incoming'
STL = 'Gladiator_MastBase_v2-holes-43p4_print-spigot-UP.stl'
FAILS = []


def p(*a):
    sys.stdout.write(' '.join(str(x) for x in a) + '\n'); sys.stdout.flush()


def check(ok, msg):
    p(('PASS ' if ok else 'FAIL ') + msg)
    if not ok:
        FAILS.append(msg)


shutil.copy2(M, REPO + '/cad/master/drafts/Gladiator_Master.pre-rear-pilots.%s.FCStd' % time.strftime('%Y%m%d-%H%M%S'))
doc = App.openDocument(M)
O = doc.getObject
sh = O('Parameters')
old_deck_vol = O('ChassisDeck').Shape.Volume
old_mb_vol = O('MastBase').Shape.Volume


def cell(a):
    return sh.getCellFromAlias(a)


c = cell('rear_pilot_outside_bias')
sh.set(c, '=1.7 mm')
sh.set('C' + c[1:], 'Rear pilots: X bias toward the outer slit from the gap midpoint. 0.5 until 2026-09-27; '
       'Jim: real pilots 3/4 of a pilot diameter (1.2) further outboard, both pairs')
c = cell('mast_screw_spacing')
sh.set(c, '=2 * (center_hole_diameter / 2 + inner_slit_hole_gap + (slit_width + outer_slit_center_spacing) / 2 + rear_pilot_outside_bias)')
sh.set('C' + c[1:], 'Mast base M2 holes c-t-c; follows the deck rear pilots at Y 111 by formula')
c = cell('mast_screw_y')
sh.set(c, '=deck_length - rear_pilot_edge_gap - rear_pilot_spacing')
sh.set('C' + c[1:], 'Mast base M2 holes Y; follows the deck rear pilots at Y 111 by formula')
doc.recompute()

bad = [o.Name for o in doc.Objects if 'Invalid' in o.State or 'Error' in o.State]
check(not bad, 'no objects in error %s' % bad)
deck = O('ChassisDeck').Shape
check(deck.isValid() and len(deck.Solids) == 1, 'deck one valid solid')
check(abs(deck.Volume - old_deck_vol) < 0.01, 'deck volume unchanged (holes moved, none added)')


def circles(shape, r, z=None):
    return sorted({(round(e.Curve.Center.x, 3), round(e.Curve.Center.y, 3)) for e in shape.Edges
                   if hasattr(e, 'Curve') and e.Curve.TypeId == 'Part::GeomCircle'
                   and abs(e.Curve.Radius - r) < 1e-6 and (z is None or abs(e.Curve.Center.z - z) < 1e-6)})


pil = circles(deck, 0.8, 2.0)
p('deck pilots', pil)
for q in [(17.8, 111.0), (17.8, 128.0), (61.2, 111.0), (61.2, 128.0), (15.5, 15.8), (63.5, 15.8)]:
    check(q in pil, 'deck pilot at %s' % (q,))
mb = O('MastBase').Shape
check(mb.isValid() and len(mb.Solids) == 1 and abs(mb.Volume - old_mb_vol) < 0.01, 'mast base valid, volume unchanged')
mbh = circles(mb, 1.3, 6.0)
check(mbh == [(17.8, 111.0), (61.2, 111.0)], 'mast base holes over the pilots %s' % mbh)
check(set(circles(O('PowerShield').Shape, 1.3)) >= set(mbh), 'power shield follows')
for x in (17.8, 61.2):
    screw = Part.makeCylinder(1.0, 9.0, V(x, 111, -1))     # M2 shank down into the pilot
    check(mb.common(screw).Volume < 1e-6, 'M2 at X %.1f passes the mast base clean' % x)
    check(abs(deck.common(Part.makeCylinder(0.8, 2.0, V(x, 111, 0))).Volume) < 1e-6, 'pilot at X %.1f is open under it' % x)
# the Y 128 pair vs the printed rails' rear feet (the power board tray uses that pair)
for nm, x in (('SideRailLeft', 17.8), ('SideRailRight', 61.2)):
    r = O(nm).Shape
    v = r.common(Part.makeCylinder(1.0, 10.0, V(x, 128, 2))).Volume
    h = r.common(Part.makeCylinder(1.9, 1.6, V(x, 128, 2))).Volume
    p('INFO Y128 pilot at X %.1f under %s: M2 shank overlap %.2f mm3, M2 head footprint overlap %.2f mm3' % (x, nm, v, h))
others = [o for o in ('SideRailLeft', 'SideRailRight', 'BatteryBox', 'PowerShield', 'MastTube') if O(o)]
for o in others:
    check(mb.common(O(o).Shape).Volume < 0.01 or o == 'MastTube', 'mast base clear of %s' % o)

if FAILS:
    p('REFUSING TO SAVE', FAILS)
    sys.exit(2)
doc.save()
p('SAVED')

s = mb.copy()
s.Placement = App.Placement(V(), App.Rotation(V(0, 0, 1), V(0, 0, -1))).multiply(s.Placement)
b = s.BoundBox
s.translate(V(-b.XMin, -b.YMin, -b.ZMin))
m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.05, Relative=False)
ok = (m.isSolid() and not m.hasNonManifolds() and not m.hasSelfIntersections() and abs(m.BoundBox.ZMin) < 1e-6
      and abs(m.BoundBox.ZLength - 23.5) < 0.01 and abs(m.Volume - mb.Volume) / mb.Volume < 0.005)
check(ok, 'mesh solid/manifold/on bed/volume %s' % m.BoundBox)
if FAILS:
    sys.exit(3)
m.write(OUTDIR + '/' + STL)
shutil.copy2(OUTDIR + '/' + STL, INCOMING + '/' + STL)
p('STL', STL, m.BoundBox, m.CountFacets)
