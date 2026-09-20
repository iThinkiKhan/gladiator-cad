"""Move the breadboard envelope clear of the expander's bosses.

s3_pattern.py set `bb.Placement.Base.x` and FreeCAD reported success, but the
value did not change - Placement returns a copy, so mutating Base on it is a
no-op. It happened to work for S3Board and not for Breadboard, which is exactly
the kind of silent half-success worth asserting on rather than printing.

The expander's right boss now reaches X 46.10, so a breadboard still sitting at
44.0 would be resting on it.
"""
import sys

import FreeCAD as App

_p = print


def print(*a, **k):
    _p(*a, **k)
    sys.stdout.flush()


REPO = '/home/buralien/projects/gladiator-cad'
MASTER = REPO + '/cad/master/Gladiator_Master.FCStd'
WANT_X = 46.10

doc = App.openDocument(MASTER)
bb = doc.getObject('Breadboard')
deck = doc.getObject('UpperDeck')

print('breadboard is at X %.2f, wants %.2f' % (bb.Placement.Base.x, WANT_X))

print('breadboard expressions: %s' % [(p, e) for p, e in (bb.ExpressionEngine or [])])
# Its X is driven by Parameters.bb_x0, so assigning Placement does nothing at all -
# the recompute just puts it back. Two earlier attempts reported success and moved
# nothing. Set the parameter.
sp = doc.getObject('Parameters')
rowof = {}
for r in range(1, 250):
    try:
        rowof[str(sp.get('A%d' % r))] = r
    except Exception:
        continue
if 'bb_x0' not in rowof:
    raise SystemExit('bb_x0 not found in the spreadsheet')
sp.set('B%d' % rowof['bb_x0'], '%g mm' % WANT_X)
doc.recompute()

got = bb.Placement.Base.x
print('breadboard now at X %.2f .. %.2f' % (got, got + bb.Length.Value))
if abs(got - WANT_X) > 1e-6:
    raise SystemExit('the move did not take - still %.2f' % got)

# it must clear the deck's bosses and stay on the deck
s = deck.Shape
bosses = [(round(f.Surface.Center.x, 2), round(f.Surface.Center.y, 2))
          for f in s.Faces if f.Surface.TypeId == 'Part::GeomCylinder'
          and abs(f.Surface.Radius * 2 - 9.0) < 0.01]
worst = None
for x, y in sorted(set(bosses)):
    if x > 50:
        continue                      # driver/antenna bosses on the far side
    edge = x + 4.5
    if worst is None or edge > worst:
        worst = edge
print('rightmost expander boss edge: X %.2f  -> %.2f of clearance' % (worst, got - worst))
ok = got - worst >= -1e-6

clash = s.common(bb.Shape).Volume
print('breadboard vs deck solid: %.1f mm3 %s' % (clash, '(sitting on it, fine)' if clash >= 0 else ''))

right = got + bb.Length.Value
print('breadboard right edge X %.2f, deck ends %.2f -> %.2f to spare'
      % (right, s.BoundBox.XMax, s.BoundBox.XMax - right))
if right > s.BoundBox.XMax + 1e-6:
    print('*** breadboard runs off the deck')
    ok = False

if not ok:
    raise SystemExit('VERIFICATION FAILED - not saving')

doc.save()
print()
print('saved')
