"""Driver mount: 2.7 self-tap pilots -> 3.6 M3 clearance, for nuts and washers.

Jim, 2026-09-20: no self-tapping screws, will use nuts and washers. The space
behind every pilot is clear (a dia12 x 10 probe finds 0.0 mm3), so a through-bolt
fits, and a nut loads the 1.81 wall in compression rather than expanding it the
way a heat-set insert would.

3.6 rather than the textbook 3.4, to match `deck2_screw_dia`: round features on
this printer come out about 0.25 under, so 3.4 lands near 3.15 against a 3.0
screw. The whole design moved M3 clearance to 3.6 for exactly that reason and
these holes should not be the exception.

The four holes are literal radius constraints in DrvHoleSketch - an attempt to
bind them to the spreadsheet was backed out because the expression evaluates but
does not propagate to the body solid headless. So this sets the datum directly
and then checks the solid actually changed, rather than trusting the edit.
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

OLD, NEW = 2.7, 3.6

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup = os.path.join(DRAFTS, 'Gladiator_Master.%s.pre-drvclearance.FCStd' % stamp)
shutil.copy2(MASTER, backup)
print('backup -> %s' % backup)

doc = App.openDocument(MASTER)
body = doc.getObject('DriverMountLeft')
before_vol = body.Shape.Volume


def count(dia):
    return sum(1 for f in body.Shape.Faces
               if f.Surface.TypeId == 'Part::GeomCylinder'
               and abs(f.Surface.Radius * 2 - dia) < 0.01)


pre_new = count(NEW)     # the foot already has 2 deck-fixing holes at this size
print('before: %d holes at %.1f, %d at %.1f (deck fixings), volume %.1f'
      % (count(OLD), OLD, pre_new, NEW, before_vol))

o = doc.getObject('DrvHoleCut')
prof = getattr(o, 'Profile', None)
sk = prof[0] if isinstance(prof, (list, tuple)) and prof else prof

n = 0
for i, c in enumerate(sk.Constraints):
    if c.Type == 'Radius' and abs(c.Value - OLD / 2.0) < 1e-6:
        sk.setDatum(i, App.Units.Quantity('%f mm' % (NEW / 2.0)))
        n += 1
print('set %d radius constraints to %.2f' % (n, NEW / 2.0))
if n != 4:
    raise SystemExit('expected 4 pilot radii, found %d' % n)

sk.recompute()
o.touch()
body.touch()
doc.recompute()

after_vol = body.Shape.Volume
print('after:  %d holes at %.1f, %d at %.1f, volume %.1f'
      % (count(OLD), OLD, count(NEW), NEW, after_vol))

# a 2.7 -> 3.6 hole, 12 deep, x4
expect = 4 * 3.14159265 * ((NEW / 2.0) ** 2 - (OLD / 2.0) ** 2) * 12.0
print('removed %.1f mm3 (expected about %.1f)' % (before_vol - after_vol, expect))

ok = True
if count(NEW) != pre_new + 4 or count(OLD) != 0:
    print('*** the solid did not take the change')
    ok = False
if abs((before_vol - after_vol) - expect) > 15.0:
    print('*** removed volume does not match')
    ok = False
s = body.Shape
if not s.isValid() or len(s.Solids) != 1:
    print('*** solid invalid')
    ok = False
print('valid=%s solids=%d' % (s.isValid(), len(s.Solids)))

# the wall to the heatsink side must still be sane
print()
print('wall from the 3.6 hole to the arm edge nearest the heatsink: %.2f mm'
      % (9.26 - 5.75 - NEW / 2.0))

# and the mirrored right-hand part must follow
r = doc.getObject('DriverMountRight').Shape
nr = sum(1 for f in r.Faces if f.Surface.TypeId == 'Part::GeomCylinder'
         and abs(f.Surface.Radius * 2 - NEW) < 0.01)
print('DriverMountRight followed: %d holes at %.1f (want %d)' % (nr, NEW, pre_new + 4))
if nr != pre_new + 4:
    ok = False

if not ok:
    raise SystemExit('VERIFICATION FAILED - not saving')

doc.save()
print()
print('saved. previous state: %s' % backup)
