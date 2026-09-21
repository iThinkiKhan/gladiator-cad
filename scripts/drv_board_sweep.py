"""Where should the board sit, now that standoff length is free?

Sweeps the board plane inboard along its own normal and reports, at each step:
the heatsink's outboard reach against the track line, where the four holes land,
and how far each hole is from real structure to root a post on.
"""
import sys, math
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A, Part

O = []
def p(s): O.append(s)

TRACK_OUTER_X = -50.0     # tracks occupy X -50..0, measured 2026-09-16
DECK_EDGE_X = -3.0        # UpperDeck v2 spans X -3..82
DECK_TOP_Z = 62.0

d = A.openDocument('/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd')
sk = d.getObject('DrvHoleSketch')
PL = sk.Placement
U = PL.Rotation.multVec(A.Vector(1, 0, 0))
V = PL.Rotation.multVec(A.Vector(0, 1, 0))
Wv = PL.Rotation.multVec(A.Vector(0, 0, 1))
ORG = PL.Base

anchors = []
for nm in ['UpperDeck', 'SideRailLeft', 'ChassisDeck']:
    o = d.getObject(nm)
    if o and getattr(o, 'Shape', None) and not o.Shape.isNull():
        anchors.append((nm, o.Shape))

def at(u, v, w=0.0):
    return A.Vector(ORG.x + U.x*u + V.x*v + Wv.x*w,
                    ORG.y + U.y*u + V.y*v + Wv.y*w,
                    ORG.z + U.z*u + V.z*v + Wv.z*w)

def hit(a, b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox):
            return 0.0
        return a.common(b).Volume
    except Exception:
        return 0.0

holes = sorted((g.Center.x, g.Center.y) for g in sk.Geometry)
HI = [h for h in holes if h[1] < 25]      # inboard-high pair, v 5.75
LO = [h for h in holes if h[1] > 25]      # outboard-low pair, v 45.25

p('Sweeping the board plane inboard along its own normal.')
p('Offset 0 = where the CAD has it now. Positive = further inboard.')
p('Track outer edge X %.1f. Upper deck edge X %.1f, top Z %.1f.'
  % (TRACK_OUTER_X, DECK_EDGE_X, DECK_TOP_Z))
p('')
p('%6s  %9s  %8s   %-22s  %-22s' %
  ('offset', 'fin tip X', 'vs track', 'inboard-high hole', 'outboard-low hole'))
p('%6s  %9s  %8s   %-22s  %-22s' % ('mm', '', 'mm', 'X / Z', 'X / Z'))

for off in [0, 3, 6, 9, 12, 15, 18, 21, 24]:
    w = -float(off)
    # heatsink: 32 wide on v, centred, 28 proud of the board face
    pts = [at(8.75, 9.5, w), at(40.75, 9.5, w), at(40.75, 41.5, w), at(8.75, 41.5, w)]
    face = Part.Face(Part.makePolygon(pts + [pts[0]]))
    hs = face.extrude(A.Vector(Wv.x*28, Wv.y*28, Wv.z*28))
    tip = hs.BoundBox.XMin
    qh = at(HI[0][0], HI[0][1], w)
    ql = at(LO[0][0], LO[0][1], w)
    p('%6d  %9.2f  %+8.1f   X%7.2f Z%7.2f   X%7.2f Z%7.2f'
      % (off, tip, tip - TRACK_OUTER_X, qh.x, qh.z, ql.x, ql.z))

p('')
p('   "vs track" negative = the heatsink sticks out past the track. Positive = tucked inside.')

p('')
p('=== at each offset, how far is each hole from something to root a post on? ===')
p('   (horizontal reach inboard to the deck edge plane X %.1f)' % DECK_EDGE_X)
p('')
p('%6s  %-34s  %-34s' % ('offset', 'inboard-high pair', 'outboard-low pair'))
for off in [0, 3, 6, 9, 12, 15, 18, 21, 24]:
    w = -float(off)
    qh = at(HI[0][0], HI[0][1], w)
    ql = at(LO[0][0], LO[0][1], w)
    def desc(q):
        dx = DECK_EDGE_X - q.x                 # + = hole is outboard of the deck edge
        dz = q.z - DECK_TOP_Z                  # + = above the deck top
        return 'reach %5.1f out, %5.1f %s deck' % (dx, abs(dz), 'above' if dz >= 0 else 'BELOW')
    p('%6d  %-34s  %-34s' % (off, desc(qh), desc(ql)))

p('')
p('=== does the board or heatsink foul anything at each offset? ===')
for off in [0, 6, 12, 18, 24]:
    w = -float(off)
    pts = [at(0, 0, w), at(49.5, 0, w), at(49.5, 51, w), at(0, 51, w)]
    face = Part.Face(Part.makePolygon(pts + [pts[0]]))
    board = face.extrude(A.Vector(Wv.x*3.2, Wv.y*3.2, Wv.z*3.2))
    pts2 = [at(8.75, 9.5, w), at(40.75, 9.5, w), at(40.75, 41.5, w), at(8.75, 41.5, w)]
    hs = Part.Face(Part.makePolygon(pts2 + [pts2[0]])).extrude(
        A.Vector(Wv.x*28, Wv.y*28, Wv.z*28))
    bad = []
    for nm, sh in anchors:
        for lbl, s in (('board', board), ('fins', hs)):
            v_ = hit(s, sh)
            if v_ > 0.05:
                bad.append('%s/%s %.0f' % (lbl, nm, v_))
    p('   offset %2d : %s' % (off, ', '.join(bad) if bad else 'clear'))

p('')
p('=== what has to fit in the gap between board and mount ===')
p('   The GPIO header is now on the INBOARD face, so the gap has to take the')
p('   plugged connector and its wire bend, not just the bare header.')
p('   A 0.1 inch male header is about 8.5 mm tall; a pushed-on Dupont shell adds')
p('   roughly 6 more, and the wire wants a bend radius on top of that.')
p('   Those are catalogue figures, NOT measured off Jim\'s board or his connectors.')
p('   Standoff length should be set from a real plugged measurement.')

open('/tmp/sweep.txt', 'w').write(chr(10).join(O))
