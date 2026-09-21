"""Which way round does the frame actually expect the board?

Two hypotheses, tested against the solid:
  A  heatsink INBOARD (into the frame window), component/GPIO face outboard
  B  component/GPIO face INBOARD, heatsink outboard in free air
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
L, WID, COMP_H, HS_H = 49.5, 51.0, 13.0, 28.0

ROBOT = []
for nm in ['ChassisDeck', 'UpperDeck', 'SideRailLeft', 'SideRailRight', 'MastTube',
           'MastBase', 'PowerShield', 'AntennaPost', 'S3Board', 'Breadboard',
           'DriverMountRight', 'BatteryBox', 'DriverBoardRight']:
    o = d.getObject(nm)
    if o and getattr(o, 'Shape', None) and not o.Shape.isNull():
        ROBOT.append((nm, o.Shape))

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

p('=== how far INBOARD is the frame window clear? (u 9..41, full v) ===')
p('    against the frame, and against everything else on the robot')
for depth in [5, 10, 13, 18, 22, 25, 28, 32, 40]:
    s = slab(9.0, 41.0, 0, WID, -depth, 0.0)
    others = [(n, hit(s, sh)) for n, sh in ROBOT]
    others = [(n, v_) for n, v_ in others if v_ > 0.05]
    p('   %2d mm inboard : frame %8.1f mm3   robot: %s'
      % (depth, hit(s, frame), ', '.join('%s %.0f' % t for t in others) or 'clear'))

p('')
p('=== how far OUTBOARD is it clear? (free air check for whichever side faces out) ===')
for depth in [5, 13, 20, 28, 35, 45]:
    s = slab(0, L, 0, WID, 0.0, depth)
    others = [(n, hit(s, sh)) for n, sh in ROBOT]
    others = [(n, v_) for n, v_ in others if v_ > 0.05]
    p('   %2d mm outboard: frame %8.1f mm3   robot: %s'
      % (depth, hit(s, frame), ', '.join('%s %.0f' % t for t in others) or 'clear'))

p('')
p('=== HYPOTHESIS A: heatsink inboard, GPIO face outboard ===')
hs_in = slab(9.0, 41.0, 0, WID, -HS_H, 0.0)          # heatsink through the window
tails = slab(0, 9.0, 10.75, 42.25, -2.0, 0.0)        # solder tails beside it, in the relief
tails2 = slab(41.0, L, 10.75, 42.25, -2.0, 0.0)
comp_out = slab(0, L, 0, WID, 0.0, COMP_H)
p('   heatsink block in the window   : frame clash %8.1f mm3' % hit(hs_in, frame))
p('   2 mm tail strip, fore relief   : frame clash %8.1f mm3' % hit(tails, frame))
p('   2 mm tail strip, aft relief    : frame clash %8.1f mm3' % hit(tails2, frame))
p('   component block outboard       : frame clash %8.1f mm3' % hit(comp_out, frame))
rob = [(n, hit(hs_in, sh)) for n, sh in ROBOT]
p('   heatsink vs robot              : %s'
  % (', '.join('%s %.0f' % t for t in rob if t[1] > 0.05) or 'clear'))

p('')
p('=== HYPOTHESIS B: GPIO face inboard, heatsink outboard ===')
comp_in = slab(0, L, 0, WID, -COMP_H, 0.0)
hs_out = slab(9.0, 41.0, 0, WID, 0.0, HS_H)
p('   component block inboard        : frame clash %8.1f mm3' % hit(comp_in, frame))
p('   component block, window only   : frame clash %8.1f mm3'
  % hit(slab(9.0, 41.0, 0, WID, -COMP_H, 0.0), frame))
p('   heatsink outboard              : frame clash %8.1f mm3' % hit(hs_out, frame))
rob = [(n, hit(comp_in, sh)) for n, sh in ROBOT]
p('   components vs robot            : %s'
  % (', '.join('%s %.0f' % t for t in rob if t[1] > 0.05) or 'clear'))

p('')
p('=== where exactly are the relief pockets, in u and v ===')
p('    probing the fore arm at 1 mm depth: 0 = pocket (no material), >0 = solid')
row = '      v:'
for v in range(0, 51, 3):
    row += '%6d' % v
p(row)
row = '   solid:'
for v in range(0, 51, 3):
    row += '%6.1f' % hit(slab(0.0, 8.5, v, v+3.0, -1.2, -0.2), frame)
p(row)
p('')
p('    same arm at 3 mm depth (below the pocket floor, should be solid throughout)')
row = '   solid:'
for v in range(0, 51, 3):
    row += '%6.1f' % hit(slab(0.0, 8.5, v, v+3.0, -3.2, -2.2), frame)
p(row)

p('')
p('=== frame thickness along w, in the arm ===')
for w0 in range(0, -16, -1):
    s = slab(0.0, 8.5, 0, 10.0, w0-1.0, float(w0))
    p('   w %4d..%-4d  arm material %8.1f mm3' % (w0-1, w0, hit(s, frame)))

open('/tmp/which.txt', 'w').write(chr(10).join(O))
