"""Deck v2: correct the expander boss pattern and back it into the left corner.

Expander is 48 x 74, holes 4.6 dia, c-t-c 40.10 x 64.10 - confirmed by Jim
measuring about 1.6 of board material outside a hole against a prediction of 1.65.
The deck as printed has 30.9 x 55.0, which is why the real board would not fit.

X: backed into the left corner as far as the BOSSES allow - boss outer edge flush
   with the deck edge at X -3, so the left hole centre is 1.50.
Y: unchanged. Moving it forward too would land the front-left boss on the deck's
   12 mm corner hole at (3, 6).
"""
import datetime
import os
import shutil
import sys
import traceback

import FreeCAD as App

_p = print


def print(*a, **k):
    _p(*a, **k)
    sys.stdout.flush()


def step(label, fn):
    try:
        r = fn()
        print('   ok   %s' % label)
        return r
    except BaseException:
        print('   FAIL %s' % label)
        traceback.print_exc()
        sys.stdout.flush()
        raise


REPO = '/home/buralien/projects/gladiator-cad'
MASTER = REPO + '/cad/master/Gladiator_Master.FCStd'
DRAFTS = REPO + '/cad/master/drafts'

CTC_X, CTC_Y = 40.10, 64.10
BOARD_W, BOARD_L = 48.0, 74.0
X_L, Y_C = 1.50, 52.0
X_R = X_L + CTC_X
Y_F, Y_B = Y_C - CTC_Y / 2.0, Y_C + CTC_Y / 2.0
NEW = [(X_L, Y_F), (X_R, Y_F), (X_L, Y_B), (X_R, Y_B)]
OLD = [(5.05, 24.5), (35.95, 24.5), (5.05, 79.5), (35.95, 79.5)]

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup = os.path.join(DRAFTS, 'Gladiator_Master.%s.pre-s3pattern.FCStd' % stamp)
shutil.copy2(MASTER, backup)
print('backup -> %s' % backup)

doc = App.openDocument(MASTER)
deck = doc.getObject('UpperDeck')

print()
print('moving the boss pattern to %.2f x %.2f' % (CTC_X, CTC_Y))
for feat in ('S3BossPad', 'S3InsertCut'):
    o = doc.getObject(feat)
    prof = getattr(o, 'Profile', None)
    sk = prof[0] if isinstance(prof, (list, tuple)) and prof else prof
    order = []
    for g in sk.Geometry:
        cx, cy = g.Center.x, g.Center.y
        order.append(min(range(4), key=lambda k: (OLD[k][0] - cx) ** 2 + (OLD[k][1] - cy) ** 2))
    if sorted(order) != [0, 1, 2, 3]:
        raise SystemExit('%s: circles do not map onto the old pattern' % feat)
    step('%s movePoint' % feat,
         lambda: [sk.movePoint(gi, 3, App.Vector(NEW[i][0], NEW[i][1], 0))
                  for gi, i in enumerate(order)])
    step('%s sketch recompute' % feat, sk.recompute)
step('doc recompute after the sketches', doc.recompute)

print()
print('moving the reference envelopes')
b = doc.getObject('S3Board')
bb = doc.getObject('Breadboard')
print('   S3Board    Length=%s Width=%s' % (b.Length, b.Width))
step('S3Board Length', lambda: setattr(b, 'Length', App.Units.Quantity('%f mm' % BOARD_W)))
step('S3Board Width', lambda: setattr(b, 'Width', App.Units.Quantity('%f mm' % BOARD_L)))
step('S3Board x', lambda: setattr(b.Placement.Base, 'x', X_L - (BOARD_W - CTC_X) / 2.0))
step('Breadboard x', lambda: setattr(bb.Placement.Base, 'x', X_R + 4.5))
step('doc recompute after the envelopes', doc.recompute)

print()
print('   S3Board  now X %.2f..%.2f  (Length %s)'
      % (b.Placement.Base.x, b.Placement.Base.x + b.Length.Value, b.Length))
print('   Breadboard now X %.2f' % bb.Placement.Base.x)

# ---- verify ----
s = deck.Shape
ok = s.isValid() and len(s.Solids) == 1
print()
print('deck valid=%s solids=%d volume %.1f' % (s.isValid(), len(s.Solids), s.Volume))
got = sorted(set((round(f.Surface.Center.x, 2), round(f.Surface.Center.y, 2))
                 for f in s.Faces if f.Surface.TypeId == 'Part::GeomCylinder'
                 and abs(f.Surface.Radius * 2 - 4.6) < 0.01))
want = sorted((round(x, 2), round(y, 2)) for x, y in NEW)
print('expander bores found: %s' % [p for p in got if p in want])
missing = [p for p in want if p not in got]
if missing:
    print('*** missing: %s' % missing)
    ok = False
if len(got) != 10:
    print('*** expected 10 insert bores on the deck, found %d' % len(got))
    ok = False

db = s.BoundBox
print()
print('deck X %.2f..%.2f, left boss outer edge %.2f' % (db.XMin, db.XMax, X_L - 4.5))
if X_L - 4.5 < db.XMin - 0.01:
    ok = False
for hx, hy, hd, lbl in ((3.0, 6.0, 12.0, 'corner hole (3,6)'),):
    for x, y in NEW:
        if ((x - hx) ** 2 + (y - hy) ** 2) ** 0.5 < 4.5 + hd / 2.0:
            print('*** boss at (%.2f,%.2f) fouls the %s' % (x, y, lbl))
            ok = False
print('rear boss edge Y %.2f, wire opening starts Y 90.0 -> %.2f clear'
      % (Y_B + 4.5, 90.0 - (Y_B + 4.5)))
if Y_B + 4.5 > 90.0:
    ok = False

if not ok:
    raise SystemExit('VERIFICATION FAILED - not saving')

doc.save()
print()
print('saved. previous state: %s' % backup)
