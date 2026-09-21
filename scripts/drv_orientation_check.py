"""Driver mount keep-out map, with w = 0 at the PCB plane.

+w is outboard/up (heatsink side, free air). Components project in -w, INTO the
frame, so the frame window and its relief pockets decide what fits where.
"""
import sys, math
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

def at(u, v, w):
    return A.Vector(ORG.x + U.x * u + V.x * v + Wv.x * w,
                    ORG.y + U.y * u + V.y * v + Wv.y * w,
                    ORG.z + U.z * u + V.z * v + Wv.z * w)

def slab(u0, u1, v0, v1, w0, w1):
    pts = [at(u0, v0, w0), at(u1, v0, w0), at(u1, v1, w0), at(u0, v1, w0)]
    f = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return f.extrude(A.Vector(Wv.x * (w1 - w0), Wv.y * (w1 - w0), Wv.z * (w1 - w0)))

def hit(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return 0.0

p('w = 0 is the PCB plane. +w outboard (fins, free air). -w inboard, into the frame.')
p('u = 0..49.5 fore-aft.  v = 0..51 along the cant, v=0 INBOARD-LOW, v=51 OUTBOARD-HIGH.')
p('  (check: v axis is (%.3f,%.3f,%.3f); its Z component is negative, so v grows downward-inboard)'
  % (V.x, V.y, V.z))
p('')
p('=== how deep can a component sit at each spot before it fouls the frame? ===')
p('    numbers are mm of clearance inboard of the PCB face')
p('')
NU, NV = 11, 12
p('          v=' + ''.join('%5.0f' % (WID * j / NV) for j in range(NV)))
for i in range(NU):
    u0, u1 = L * i / NU, L * (i + 1) / NU
    row = '   u %4.1f  ' % u0
    for j in range(NV):
        v0, v1 = WID * j / NV, WID * (j + 1) / NV
        clear = 0.0
        for probe in [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0]:
            if hit(slab(u0, u1, v0, v1, -probe, 0.0), frame) > 0.05:
                break
            clear = probe
        row += '%5.1f' % clear
    p(row)
p('')
p('   13.0 = clear right through the frame window')
p('    2.0 = only the relief pocket depth')
p('    0.0 = solid arm, the board would sit proud')

p('')
p('=== what the frame is made of, in board coordinates ===')
for lbl, u0, u1 in [('fore arm', 0.0, 8.5), ('window', 8.5, 41.0), ('aft arm', 41.0, 49.5)]:
    depth = []
    for probe in [0.5, 2.0, 13.0]:
        depth.append(hit(slab(u0, u1, 0, WID, -probe, 0.0), frame))
    p('   %-9s u %4.1f..%4.1f   material within 0.5 / 2 / 13 mm inboard: %8.1f %8.1f %8.1f mm3'
      % (lbl, u0, u1, depth[0], depth[1], depth[2]))

p('')
p('=== relief pocket extent, measured off the solid ===')
for j in range(0, 52, 1):
    a = hit(slab(0.0, 8.5, j, j + 1.0, -1.5, -0.2), frame)
    b = hit(slab(0.0, 8.5, j, j + 1.0, -3.0, -2.2), frame)
    if j == 0:
        p('   v    shallow(0.2-1.5)  deeper(2.2-3.0)   <- relief is where shallow is empty')
    if j % 2 == 0:
        p('   %-4d %12.1f %15.1f' % (j, a, b))

p('')
p('=== straight-line insertion along -w, full 49.5 x 51 x 13 component block ===')
comp = slab(0, L, 0, WID, -COMP_H, 0.0)
hs = slab(0, L, 0, WID, 0.0, HS_H)
board = comp.fuse(hs)
for back in [40, 25, 15, 8, 4, 2, 1, 0.5, 0]:
    s = board.copy()
    s.translate(A.Vector(Wv.x * back, Wv.y * back, Wv.z * back))
    p('   backed off %5.1f mm : frame clash %9.1f mm3' % (back, hit(s, frame)))
p('   (a full-rectangle block always clashes at the arms; the map above is what matters)')

p('')
p('=== does the seated board clash with anything else on the robot? ===')
for nm in ['ChassisDeck', 'UpperDeck', 'SideRailLeft', 'SideRailRight', 'MastTube',
           'MastBase', 'PowerShield', 'AntennaPost', 'S3Board', 'Breadboard',
           'DriverMountRight', 'BatteryBox']:
    o = d.getObject(nm)
    if not o or not getattr(o, 'Shape', None) or o.Shape.isNull():
        continue
    v_ = hit(board, o.Shape)
    if v_ > 0.05:
        p('   %-18s clash %.1f mm3' % (nm, v_))
p('   (nothing listed = clear)')

p('')
p('=== hole pattern ===')
h = sorted((round(g.Center.x, 2), round(g.Center.y, 2)) for g in sk.Geometry)
p('   %s' % h)
p('   pitch u %.2f   pitch v %.2f' % (h[2][0] - h[0][0], h[1][1] - h[0][1]))
p('   180 deg in-plane flip maps to %s'
  % sorted((round(L - a, 2), round(WID - b, 2)) for a, b in h))
p('   symmetric: %s' % (sorted((round(L - a, 2), round(WID - b, 2)) for a, b in h) == h))
p('   holes sit at v = %.2f and %.2f, i.e. %.2f from each cant edge'
  % (h[0][1], h[1][1], h[0][1]))

open('/tmp/drvins2.txt', 'w').write(chr(10).join(O))
