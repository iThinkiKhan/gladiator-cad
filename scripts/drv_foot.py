"""Driver mount: drop the foot onto the deck plate instead of floating it on two bosses.

The foot was a 13 x 49.5 plate at Z 58..62, resting only on the two Ø9 deck boss
tops - about 107 mm2 of bearing carrying ~108 g on an 18 mm lever, with the bosses
acting as 6 mm cantilever pillars.

This extends the foot down to Z 52 so it sits flat on the deck plate, and pockets
it around the bosses. Three consequences:

  - bearing area goes from ~107 mm2 to ~450 mm2
  - the bosses stop being cantilevers and become shear pins captured in sockets
  - the heat-set inserts stay exactly where they are, in the joint the coupon
    already proved (insert in a Ø9 boss, 6 tall on 4 of plate - "could not pull it
    out")

So it is a FOOT change with no deck change at all.

Not widened outboard to X 0, though the lever arm would improve: the deck's
rear-left corner fillet (R6, centred 6,134) curves away there, and the foot runs
to Y 139.5 - it would overhang. The screw tension is a few newtons anyway; the
preload is what matters, and that is unaffected by the lever arm.
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

Z_DECK, Z_OLD = 52.0, 58.0
BOSS_D, BOSS_CLEAR = 9.0, 0.4
BOSSES = [(14.5, 95.0), (14.5, 135.0)]
RAIL_SCREW = (12.0, 120.0)
RAIL_RELIEF_D, RAIL_RELIEF_H = 8.0, 3.0

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup = os.path.join(DRAFTS, 'Gladiator_Master.%s.pre-drvfoot.FCStd' % stamp)
shutil.copy2(MASTER, backup)
print('backup -> %s' % backup)

doc = App.openDocument(MASTER)
body = doc.getObject('DriverMountLeft')
before = body.Shape.Volume

# 1. drop the foot profile from Z 58 down to Z 52
o = doc.getObject('DrvFootPad')
prof = getattr(o, 'Profile', None)
sk = prof[0] if isinstance(prof, (list, tuple)) and prof else prof
moved = 0
for gi, g in enumerate(sk.Geometry):
    if g.TypeId != 'Part::GeomLineSegment':
        continue
    for pos, pt in ((1, g.StartPoint), (2, g.EndPoint)):
        if abs(pt.y - Z_OLD) < 1e-6:          # sketch Y is global Z here
            sk.movePoint(gi, pos, App.Vector(pt.x, Z_DECK, 0))
            moved += 1
sk.recompute()
doc.recompute()
print()
print('foot profile: moved %d point(s) from Z %.1f to Z %.1f' % (moved, Z_OLD, Z_DECK))
lows = sorted(set(round(p.y, 2) for g in sk.Geometry
                  if g.TypeId == 'Part::GeomLineSegment'
                  for p in (g.StartPoint, g.EndPoint)))
print('   profile now spans sketch Y (= global Z) %s' % lows)
if lows[0] != Z_DECK:
    raise SystemExit('the profile did not drop')

# 2. pocket it around the deck bosses, and relieve the rail screw head
tools = []
for x, y in BOSSES:
    tools.append(Part.makeCylinder((BOSS_D + BOSS_CLEAR) / 2.0, (Z_OLD - Z_DECK) + 0.2,
                                   App.Vector(x, y, Z_DECK - 0.1)))
tools.append(Part.makeCylinder(RAIL_RELIEF_D / 2.0, RAIL_RELIEF_H,
                               App.Vector(RAIL_SCREW[0], RAIL_SCREW[1], Z_DECK - 0.1)))
tool = tools[0]
for t in tools[1:]:
    tool = tool.fuse(t)
tool = tool.removeSplitter()

feat = doc.addObject('Part::Feature', 'DrvFootReliefTool')
feat.Shape = tool
doc.recompute()
cut = doc.addObject('PartDesign::Boolean', 'DrvFootReliefCut')
body.addObject(cut)
cut.Type = 'Cut'
cut.Group = [feat]
doc.recompute()

s = body.Shape
after = s.Volume
print()
print('volume %.1f -> %.1f  (added %.1f mm3, about %.1f g)'
      % (before, after, after - before, (after - before) * 1.24 / 1000.0))

# ---- verify ----
ok = s.isValid() and len(s.Solids) == 1
print('valid=%s solids=%d' % (s.isValid(), len(s.Solids)))

band = s.common(Part.makeBox(200, 200, 0.5, App.Vector(-60, 85, Z_DECK)))
area = sum(x.Volume for x in band.Solids) / 0.5
on_deck = 0.0
for x in band.Solids:
    b = x.BoundBox
    if b.XMin >= -0.01 and b.XMax <= 79.01:
        on_deck += x.Volume / 0.5
print()
print('foot bearing at Z %.1f: %.1f mm2 total, %.1f mm2 of it on the deck (X 0..79)'
      % (Z_DECK, area, on_deck))
print('   was ~107 mm2 on two boss tops -> %.1fx improvement' % (on_deck / 107.0))
if on_deck < 350.0:
    print('*** less bearing than expected')
    ok = False

deck = doc.getObject('UpperDeck').Shape
clash = s.common(deck).Volume
print()
print('mount vs deck solid: %.2f mm3 %s' % (clash, 'CLEAR' if clash < 1.0 else '*** CLASH'))
if clash >= 1.0:
    ok = False

for x, y in BOSSES:
    probe = Part.makeCylinder(BOSS_D / 2.0, 5.0, App.Vector(x, y, Z_DECK + 0.5))
    v = s.common(probe).Volume
    print('   boss socket at (%.1f, %.1f): mount material inside it %.2f mm3' % (x, y, v))
    if v > 1.0:
        ok = False

probe = Part.makeCylinder(3.5, 2.0, App.Vector(RAIL_SCREW[0], RAIL_SCREW[1], Z_DECK + 0.2))
v = s.common(probe).Volume
print('   rail screw head relief at (%.1f, %.1f): material %.2f mm3' % (RAIL_SCREW + (v,)))
if v > 1.0:
    ok = False

r = doc.getObject('DriverMountRight').Shape
print()
print('right-hand mirror followed: valid=%s volume %.1f' % (r.isValid(), r.Volume))
if abs(r.Volume - after) > 1.0:
    ok = False

if not ok:
    raise SystemExit('VERIFICATION FAILED - not saving')

doc.save()
print()
print('saved. previous state: %s' % backup)
