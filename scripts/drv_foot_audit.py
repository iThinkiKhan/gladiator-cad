"""Same checks on v1 and v2 side by side, so probe artifacts cancel."""
import sys
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A, Part

O = []
def p(s): O.append(s)
ROOT = '/home/buralien/projects/gladiator-cad'
m = A.openDocument(ROOT + '/cad/drivers/v2-standoff/DriverMount_v2.FCStd')
v2 = m.getObject('DriverMount_v2_Left').Shape
d = A.openDocument(ROOT + '/cad/master/Gladiator_Master.FCStd')
v1 = d.getObject('DriverMountLeft').Shape
deck = d.getObject('UpperDeck').Shape

def hit(a, b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox):
            return 0.0
        return a.common(b).Volume
    except Exception:
        return 0.0

SCREWS = [(14.5, 95.0), (14.5, 135.0)]

p('Deck bosses are D9.0 at (14.5,95) and (14.5,135), Z 52..58,')
p('with D4.6 insert bores running Z 50.5..58. Measured off the deck solid.')
p('')
p('%-38s %12s %12s' % ('check', 'v1 (works)', 'v2 (new)'))
p('%-38s %12s %12s' % ('-' * 38, '-' * 12, '-' * 12))

def row(label, probe, invert=False):
    a, b = hit(probe, v1), hit(probe, v2)
    p('%-38s %12.1f %12.1f' % (label, a, b))
    return a, b

for x, y in SCREWS:
    row('screw column D3.6, Z 58..62 @Y%.0f' % y,
        Part.makeCylinder(1.8, 4.0, A.Vector(x, y, 58.0)))
for x, y in SCREWS:
    row('boss pocket D9.4, Z 52..58 @Y%.0f' % y,
        Part.makeCylinder(4.7, 6.0, A.Vector(x, y, 52.0)))
for x, y in SCREWS:
    row('driver access D7, Z 62..120 @Y%.0f' % y,
        Part.makeCylinder(3.5, 58.0, A.Vector(x, y, 62.0)))

p('')
p('=== so where IS the screw hole in each? scan a D3.6 column by height ===')
for x, y in SCREWS[:1]:
    p('   at (%.1f, %.1f):' % (x, y))
    p('   %6s %10s %10s' % ('Z', 'v1', 'v2'))
    for z in [float(i) for i in range(50, 80, 2)]:
        pr = Part.makeCylinder(1.8, 2.0, A.Vector(x, y, z))
        p('   %6.0f %10.1f %10.1f' % (z, hit(pr, v1), hit(pr, v2)))

p('')
p('=== flat area bearing on the deck top (Z 52) ===')
sl = Part.makeBox(70, 60, 0.4, A.Vector(-25, 85, 51.99))
p('   v1 %.0f mm2     v2 %.0f mm2' % (hit(sl, v1) / 0.4, hit(sl, v2) / 0.4))

p('')
p('=== does either foul the deck bosses (D9.0, Z 52..58)? ===')
for x, y in SCREWS:
    pr = Part.makeCylinder(4.5, 6.0, A.Vector(x, y, 52.0))
    a, b = hit(pr, v1), hit(pr, v2)
    p('   boss @Y%.0f : v1 %7.1f mm3   v2 %7.1f mm3   %s'
      % (y, a, b, 'v2 FOULS' if b > a + 1 else 'ok'))

p('')
p('=== v2 spine: what sits directly over each screw? ===')
for x, y in SCREWS:
    pr = Part.makeCylinder(3.5, 58.0, A.Vector(x, y, 62.0))
    try:
        c = pr.common(v2)
        if c.Volume > 0.5:
            cb = c.BoundBox
            p('   @Y%.0f : v2 material from Z %.1f to %.1f, %.0f mm3'
              % (y, cb.ZMin, cb.ZMax, c.Volume))
        else:
            p('   @Y%.0f : clear' % y)
    except Exception as e:
        p('   @Y%.0f : probe failed %s' % (y, e))

open('/tmp/foot2.txt', 'w').write(chr(10).join(O))
