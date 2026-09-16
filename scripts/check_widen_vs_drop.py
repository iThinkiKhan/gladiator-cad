import math
import FreeCAD as App
import Part

doc = App.openDocument('/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd')
g = doc.getObject

deck = g('UpperDeck').Shape
left = g('DriverMountLeft').Shape

print('=== current state ===')
print('deck bbox', deck.BoundBox)
print('driver mount (left) bbox', left.BoundBox)
print('current clash deck/driver:', round(deck.Shape.common(left).Volume if hasattr(deck,'Shape') else deck.common(left).Volume, 4))

print()
print('=== build a test deck at width 85, same Z, check clash with the CURRENT driver mount ===')
W = 85.0
X0, X1 = 39.5 - W / 2.0, 39.5 + W / 2.0   # -3 .. 82
box = Part.makeBox(X1 - X0, 140.0, 4.0, App.Vector(X0, 0, 48.0))
print('test deck (85 wide, simple box) X %.1f..%.1f' % (X0, X1))
clash = box.common(left)
print('clash volume vs current driver mount:', round(clash.Volume, 4))
if clash.Volume > 0.001:
    print('clash bbox:', clash.BoundBox)

print()
print('=== component envelope (not modelled solid) vs deck edge, algebraic check ===')
th = math.radians(60.0)
cs, sn = math.cos(th), math.sin(th)
ax, az = 2.0, 84.0
dirx, dirz = -cs, -sn
cnx, cnz = math.sin(th), -math.cos(th)
bx, bz = ax + 49.5 * dirx, az + 49.5 * dirz
pA = (ax + 13 * cnx, az + 13 * cnz)
pB = (bx + 13 * cnx, bz + 13 * cnz)
print('component envelope line: A=(%.2f,%.2f)  B=(%.2f,%.2f)' % (pA[0], pA[1], pB[0], pB[1]))


def z_at_x(x_target):
    t = (pA[0] - x_target) / (pA[0] - pB[0])
    return pA[1] + t * (pB[1] - pA[1])


for x_edge in (0.0, -3.0):
    z = z_at_x(x_edge)
    print('  at deck edge X=%.1f: component Z=%.2f, deck top Z=52, margin=%.2f'
          % (x_edge, z, z - 52.0))

print()
print('=== what AZ would restore the ORIGINAL 2.5 margin at the WIDENED (X=-3) edge? ===')
# shifting AZ shifts the whole line by the same amount (rigid vertical translation)
target_margin = 2.5
current_margin_at_new_edge = z_at_x(-3.0) - 52.0
needed_shift = target_margin - current_margin_at_new_edge
print('  current margin at X=-3 (AZ=84): %.2f' % current_margin_at_new_edge)
print('  AZ shift needed to restore 2.5 margin: %+.2f  -> new AZ = %.1f'
      % (needed_shift, 84.0 + needed_shift))

print()
print('=== effect of THAT AZ change on the FOV question (driver top vs mast top Z120) ===')
mast_top = 120.0
old_top = left.BoundBox.ZMax
new_top = old_top + needed_shift
print('  driver top height: %.1f (now) -> %.1f (if raised to satisfy the wider deck)' % (old_top, new_top))
print('  clearance to mast top: %.1f (now) -> %.1f (worse, not better)'
      % (mast_top - old_top, mast_top - new_top))

print()
print('=== conversely: how much can AZ DROP before the CURRENT (79) deck clearance hits zero? ===')
current_margin_at_x0 = z_at_x(0.0) - 52.0
print('  current margin at X=0 (AZ=84, deck still 79 wide): %.2f' % current_margin_at_x0)
print('  max drop before clearance = 0 at the CURRENT deck edge: %.2f  -> AZ could go to %.1f'
      % (current_margin_at_x0, 84.0 - current_margin_at_x0))

print()
print('=== track clearance at that lower AZ (does it break the other constraint?) ===')
fx, fz = -math.sin(th), math.cos(th)
fin_b = (bx + 28 * fx, bz + 28 * fz)
print('  current outboard fin tip: X=%.1f, track edge X=-50, margin=%.1f'
      % (fin_b[0], fin_b[0] - (-50.0)))
print('  (dropping AZ does not change X, only Z -- fin tip X is unaffected by AZ changes)')
