"""Move the expander into its FRONT corner.

The first pass only moved it left and kept the Y centre, so when the pattern grew
from 55.0 to 64.10 the REAR boss moved 4.55 toward the mast - the opposite of what
Jim wanted.

It was held back by a claim that the deck's 12 mm "corner hole" at (3, 6) blocked
the move. That was wrong twice: those Ø12 features are the deck's corner FILLETS
(deck2_corner_r = 6), not holes, and they do not block it. The probe that appeared
to show a boss hanging off the plate was actually catching the insert bore, which
runs Z 50.5..58 - testing at Z 48..50, below the bore, shows the boss fully on the
plate all the way down to Y 8.

Front holes go to Y 8.00, putting the board at Y 3.05..77.05: 11.95 forward, and
it opens 12.95 behind the board to the wire slot at Y 90.
"""
import datetime
import os
import shutil
import sys

import FreeCAD as App
import Part

_p = print


def print(*a, **k):
    _p(*a, **k)
    sys.stdout.flush()


REPO = '/home/buralien/projects/gladiator-cad'
MASTER = REPO + '/cad/master/Gladiator_Master.FCStd'
DRAFTS = REPO + '/cad/master/drafts'

CTC_X, CTC_Y = 40.10, 64.10
BOARD_W, BOARD_L = 48.0, 74.0
X_L, Y_F = 1.50, 8.00
X_R, Y_B = X_L + CTC_X, Y_F + CTC_Y
NEW = [(X_L, Y_F), (X_R, Y_F), (X_L, Y_B), (X_R, Y_B)]
OLD = [(1.50, 19.95), (41.60, 19.95), (1.50, 84.05), (41.60, 84.05)]

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup = os.path.join(DRAFTS, 'Gladiator_Master.%s.pre-s3front.FCStd' % stamp)
shutil.copy2(MASTER, backup)
print('backup -> %s' % backup)

doc = App.openDocument(MASTER)
deck = doc.getObject('UpperDeck')

print()
print('moving the expander forward: front holes %.2f -> %.2f' % (OLD[0][1], Y_F))
for feat in ('S3BossPad', 'S3InsertCut'):
    o = doc.getObject(feat)
    prof = getattr(o, 'Profile', None)
    sk = prof[0] if isinstance(prof, (list, tuple)) and prof else prof
    order = []
    for g in sk.Geometry:
        cx, cy = g.Center.x, g.Center.y
        order.append(min(range(4), key=lambda k: (OLD[k][0] - cx) ** 2 + (OLD[k][1] - cy) ** 2))
    if sorted(order) != [0, 1, 2, 3]:
        raise SystemExit('%s: circles do not map onto the current pattern' % feat)
    for gi, i in enumerate(order):
        sk.movePoint(gi, 3, App.Vector(NEW[i][0], NEW[i][1], 0))
    for gi, i in enumerate(order):
        c = sk.Geometry[gi].Center
        if abs(c.x - NEW[i][0]) > 1e-6 or abs(c.y - NEW[i][1]) > 1e-6:
            raise SystemExit('%s circle %d did not move' % (feat, gi))
    sk.recompute()
doc.recompute()

# board envelope: X is unchanged, Y follows the pattern
b = doc.getObject('S3Board')
e = (BOARD_L - CTC_Y) / 2.0
cur = b.Placement
b.Placement = App.Placement(App.Vector(cur.Base.x, Y_F - e, cur.Base.z), cur.Rotation)
doc.recompute()
print('   board envelope now X %.2f..%.2f  Y %.2f..%.2f'
      % (b.Placement.Base.x, b.Placement.Base.x + b.Length.Value,
         b.Placement.Base.y, b.Placement.Base.y + b.Width.Value))
if abs(b.Placement.Base.y - (Y_F - e)) > 1e-6:
    raise SystemExit('the envelope did not move')

# ---- verify ----
s = deck.Shape
ok = s.isValid() and len(s.Solids) == 1
print()
print('deck valid=%s solids=%d volume %.1f' % (s.isValid(), len(s.Solids), s.Volume))

got = sorted(set((round(f.Surface.Center.x, 2), round(f.Surface.Center.y, 2))
                 for f in s.Faces if f.Surface.TypeId == 'Part::GeomCylinder'
                 and abs(f.Surface.Radius * 2 - 4.6) < 0.01))
want = sorted((round(x, 2), round(y, 2)) for x, y in NEW)
print('expander bores at: %s' % [p for p in got if p in want])
if [p for p in want if p not in got]:
    print('*** missing %s' % [p for p in want if p not in got])
    ok = False
if len(got) != 10:
    print('*** expected 10 insert bores, found %d' % len(got))
    ok = False

# every boss must sit fully on the plate - test BELOW the bores at Z 48..50
plate = s.common(Part.makeBox(120, 200, 2.0, App.Vector(-10, -10, 48.0)))
print()
for x, y in NEW:
    cyl = Part.makeCylinder(4.5, 2.0, App.Vector(x, y, 48.0))
    frac = cyl.common(plate).Volume / cyl.Volume
    print('   boss at (%6.2f, %6.2f) on the plate %7.3f%%' % (x, y, frac * 100.0))
    if frac < 0.99999:
        ok = False

# and clear of the deck's own holes and other bosses
print()
OTHER = [(12.0, 16.0, 3.6, 'rail fixing'), (12.0, 68.0, 3.6, 'rail fixing'),
         (67.0, 16.0, 3.6, 'rail fixing'), (60.0, 10.0, 9.0, 'antenna boss'),
         (76.0, 10.0, 9.0, 'antenna boss'), (14.5, 95.0, 9.0, 'driver boss')]
worst = None
for x, y in NEW:
    for ox, oy, od, lbl in OTHER:
        d = ((x - ox) ** 2 + (y - oy) ** 2) ** 0.5 - 4.5 - od / 2.0
        if worst is None or d < worst[0]:
            worst = (d, lbl, x, y)
        if d < 0:
            print('*** boss at (%.2f,%.2f) fouls a %s' % (x, y, lbl))
            ok = False
print('tightest gap to any other deck feature: %.2f mm (%s)' % (worst[0], worst[1]))
print('rear boss edge Y %.2f, wire slot starts Y 90.0 -> %.2f clear' % (Y_B + 4.5, 90.0 - (Y_B + 4.5)))
if Y_B + 4.5 > 90.0:
    ok = False

if not ok:
    raise SystemExit('VERIFICATION FAILED - not saving')

doc.save()
print()
print('saved. previous state: %s' % backup)
