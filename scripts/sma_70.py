"""Coupon D result: the SMA bulkhead wants the LARGEST bore. 6.75 -> 7.0.

The 6.75 was an extrapolation from this printer's 0.25 curve shrink against a
6.35 thread spec, and it was one step small. The coupon existed precisely because
nothing had tested it, and it earned its 3.6 g.
"""
import datetime
import os
import shutil
import sys

import FreeCAD as App

_p = print


def print(*a, **k):
    _p(*a, **k)
    sys.stdout.flush()


REPO = '/home/buralien/projects/gladiator-cad'
MASTER = REPO + '/cad/master/Gladiator_Master.FCStd'
DRAFTS = REPO + '/cad/master/drafts'
OLD, NEW = 6.75, 7.0

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup = os.path.join(DRAFTS, 'Gladiator_Master.%s.pre-sma70.FCStd' % stamp)
shutil.copy2(MASTER, backup)
print('backup -> %s' % backup)

doc = App.openDocument(MASTER)
sp = doc.getObject('Parameters')
body = doc.getObject('AntennaPost')


def count(d):
    return sum(1 for f in body.Shape.Faces
               if f.Surface.TypeId == 'Part::GeomCylinder'
               and abs(f.Surface.Radius * 2 - d) < 0.01)


before_vol = body.Shape.Volume
print('before: %d bore(s) at %.2f, %d at %.2f, volume %.1f'
      % (count(OLD), OLD, count(NEW), NEW, before_vol))

cur = sp.get('ant_sma_dia')
curv = cur.Value if hasattr(cur, 'Value') else float(cur)
if abs(curv - OLD) > 1e-6:
    raise SystemExit('ant_sma_dia is %.3f, expected %.3f' % (curv, OLD))

rowof = {}
for r in range(1, 250):
    try:
        rowof[str(sp.get('A%d' % r))] = r
    except Exception:
        continue
sp.set('B%d' % rowof['ant_sma_dia'], '%g mm' % NEW)
doc.recompute()

after_vol = body.Shape.Volume
print('after:  %d bore(s) at %.2f, %d at %.2f, volume %.1f'
      % (count(OLD), OLD, count(NEW), NEW, after_vol))

# the bore runs through the 2.0 clamping web only - the counterbore is separate
expect = 3.14159265 * ((NEW / 2.0) ** 2 - (OLD / 2.0) ** 2) * 2.0
print('removed %.2f mm3 (expected about %.2f for a 2.0 deep web)'
      % (before_vol - after_vol, expect))

ok = count(NEW) == 1 and count(OLD) == 0
s = body.Shape
ok = ok and s.isValid() and len(s.Solids) == 1
print('valid=%s solids=%d' % (s.isValid(), len(s.Solids)))
if abs((before_vol - after_vol) - expect) > 2.0:
    print('*** removed volume does not match a 2.0 deep web')
    ok = False

# the web either side of the bore must survive
print()
print('remaining web at the bore: counterbore %.2f, bore %.2f -> %.2f of shoulder all round'
      % (11.0, NEW, (11.0 - NEW) / 2.0))
if (11.0 - NEW) / 2.0 < 1.5:
    print('*** the shoulder the connector seats against is getting thin')
    ok = False

if not ok:
    raise SystemExit('VERIFICATION FAILED - not saving')

doc.save()
print()
print('saved. previous state: %s' % backup)
