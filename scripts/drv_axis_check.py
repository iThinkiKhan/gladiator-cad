"""Which axis do the driver-mount arms actually sit on? Global coordinates only.

The board is 49.5 along global Y (fore-aft) and 51 along the cant.
"""
import sys
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A, Part

O = []
def p(s): O.append(s)

d = A.openDocument('/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd')
frame = d.getObject('DriverMountLeft').Shape
sk = d.getObject('DrvHoleSketch')
PL = sk.Placement
U = PL.Rotation.multVec(A.Vector(1, 0, 0))
V = PL.Rotation.multVec(A.Vector(0, 1, 0))
Wv = PL.Rotation.multVec(A.Vector(0, 0, 1))
ORG = PL.Base
L, WID = 49.5, 51.0

p('u axis = (%.3f,%.3f,%.3f)  spans 0..49.5' % (U.x, U.y, U.z))
p('v axis = (%.3f,%.3f,%.3f)  spans 0..51'   % (V.x, V.y, V.z))
p('So u IS global Y (fore-aft) and v IS the cant axis.')
p('Board corners in global coords:')
for uu, vv in [(0, 0), (L, 0), (0, WID), (L, WID)]:
    q = A.Vector(ORG.x + U.x*uu + V.x*vv, ORG.y + U.y*uu + V.y*vv, ORG.z + U.z*uu + V.z*vv)
    p('   u=%5.1f v=%5.1f  ->  X %7.2f  Y %6.1f  Z %6.2f' % (uu, vv, q.x, q.y, q.z))

def at(u, v, w):
    return A.Vector(ORG.x + U.x*u + V.x*v + Wv.x*w,
                    ORG.y + U.y*u + V.y*v + Wv.y*w,
                    ORG.z + U.z*u + V.z*v + Wv.z*w)

def slab(u0, u1, v0, v1, w0, w1):
    pts = [at(u0, v0, w0), at(u1, v0, w0), at(u1, v1, w0), at(u0, v1, w0)]
    f = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return f.extrude(A.Vector(Wv.x*(w1-w0), Wv.y*(w1-w0), Wv.z*(w1-w0)))

def hit(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return 0.0

p('')
p('=== frame material touching the board face, swept along u (the 49.5 / global Y axis) ===')
p('    each strip is full-width in v (0..51), 1 mm deep')
for i in range(0, 50, 2):
    m = hit(slab(float(i), float(i+2), 0, WID, -1.0, 0.0), frame)
    gy = ORG.y + U.y * i
    p('   u %4.1f..%-4.1f (global Y %6.1f)  material %8.1f  %s'
      % (i, i+2, gy, m, '#' * int(m / 10)))

p('')
p('=== same sweep along v (the 51 / cant axis) ===')
p('    each strip is full-length in u (0..49.5), 1 mm deep')
for j in range(0, 51, 2):
    m = hit(slab(0, L, float(j), float(j+2), -1.0, 0.0), frame)
    q = at(0, j, 0)
    p('   v %4.1f..%-4.1f (global X %7.2f Z %6.2f)  material %8.1f  %s'
      % (j, j+2, q.x, q.z, m, '#' * int(m / 10)))

p('')
p('=== independent check: the frame faces normal to global Y ===')
for f in frame.Faces:
    if f.Surface.__class__.__name__ != 'Plane':
        continue
    n = f.Surface.Axis
    if abs(abs(n.y) - 1.0) > 1e-6:
        continue
    b = f.BoundBox
    if f.Area < 50:
        continue
    p('   face at Y=%6.1f  area %7.1f  X %6.1f..%6.1f  Z %6.1f..%6.1f'
      % (b.YMin, f.Area, b.XMin, b.XMax, b.ZMin, b.ZMax))

p('')
p('=== so: what does the window constrain? ===')
open_u = []
for i in range(0, 50):
    if hit(slab(float(i), float(i+1), 0, WID, -1.0, 0.0), frame) < 0.05:
        open_u.append(i)
open_v = []
for j in range(0, 51):
    if hit(slab(0, L, float(j), float(j+1), -1.0, 0.0), frame) < 0.05:
        open_v.append(j)
p('   u values with NO frame material across the full width: %s'
  % ('%d..%d' % (min(open_u), max(open_u) + 1) if open_u else 'none'))
p('   v values with NO frame material across the full length: %s'
  % ('%d..%d' % (min(open_v), max(open_v) + 1) if open_v else 'none'))
p('')
p('   -> the clear opening is bounded in the axis that has a range above.')
p('   -> heatsink measured 32 "across the 51 axis" = across v.')
p('   -> the heatsink dimension along u is what must fit the u opening, and that')
p('      dimension has never been measured.')

open('/tmp/axis.txt', 'w').write(chr(10).join(O))
