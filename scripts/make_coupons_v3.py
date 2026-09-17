import itertools
import math
import os
import FreeCAD as App
import Part
import MeshPart

REPO = '/home/buralien/projects/gladiator-cad'
INCOMING = '/home/buralien/Desktop/3D-Printer-Incoming'
DESTS = [os.path.join(REPO, 'cad', 'coupons'), os.path.join(REPO, 'cad', 'print-ready'), INCOMING]
for d in DESTS:
    if not os.path.isdir(d):
        os.makedirs(d)


def clip_corner(solid, size, t):
    """One clipped corner at the origin end, so orientation is never ambiguous."""
    tri = Part.makePolygon([App.Vector(0, 0, -1), App.Vector(size, 0, -1),
                            App.Vector(0, size, -1), App.Vector(0, 0, -1)])
    return solid.cut(Part.Face(tri).extrude(App.Vector(0, 0, t + 2)))


def finish(solid, name, label, note):
    doc = App.newDocument(name)
    o = doc.addObject('Part::Feature', 'Coupon')
    o.Label = label
    o.Shape = solid
    doc.recompute()
    doc.saveAs(os.path.join(REPO, 'cad', 'coupons', name + '.FCStd'))
    m = MeshPart.meshFromShape(Shape=solid, LinearDeflection=0.01, AngularDeflection=0.05,
                               Relative=False)
    for d in DESTS:
        m.write(os.path.join(d, name + '.stl'))
    g = solid.Volume / 1000.0 * 1.24
    bb = solid.BoundBox
    print('%-34s %6.0f mm3  ~%4.1f g  %.0f x %.0f x %.0f  solid=%s'
          % (name, solid.Volume, g, bb.XLength, bb.YLength, bb.ZLength, m.isSolid()))
    print('    %s' % note)
    return solid


def gaps_report(feats, PW, PD, tag):
    g = sorted((((a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5 - a[3] - b[3], a[0], b[0])
               for a, b in itertools.combinations(feats, 2))
    e = sorted((min(x - r, PW - (x + r), y - r, PD - (y + r)), lab) for lab, x, y, r in feats)
    print('    %s tightest feature gap %.2f (%s<->%s), tightest to edge %.2f (%s)'
          % (tag, g[0][0], g[0][1], g[0][2], e[0][0], e[0][1]))


# ============================================================== A: insert bores only
# This is the one that gates the rails and the upper deck: 16 bores between them.
PW, PD, PT = 62.0, 17.0, 4.0
BX, BY = [10.0, 24.0, 38.0, 52.0], 8.5
BORES = [4.0, 4.2, 4.4, 4.6]

a = Part.makeBox(PW, PD, PT)
cuts = []
for x, d in zip(BX, BORES):
    a = a.fuse(Part.makeCylinder(4.5, 6.0, App.Vector(x, BY, PT)))
    cuts.append(Part.makeCylinder(d / 2.0, 7.5, App.Vector(x, BY, PT + 6.0 - 7.5)))
for c in cuts:
    a = a.cut(c)
a = clip_corner(a, 6.0, PT)

finish(a, 'Gladiator_Coupon_A_InsertBores', 'Coupon A - heat-set insert bores',
       'bores 4.0 / 4.2 / 4.4 / 4.6 left to right, clipped corner at the 4.0 end')
gaps_report([('boss%d' % (i + 1), x, BY, 4.5) for i, x in enumerate(BX)], PW, PD, 'A:')

# ============================================================== B: fits, for later
# Needed before the mast base and before committing screw sizes. Not urgent.
PW2, PD2, PT2 = 68.0, 34.0, 4.0
PX, PY = [14.0, 34.0, 54.0], 12.0
PEGS = [13.6, 13.8, 14.0]
HY = 27.0
M3 = list(zip([8.0, 16.0, 24.0], [3.2, 3.4, 3.6]))
M2 = list(zip([34.0, 42.0, 50.0], [2.2, 2.4, 2.6]))
SLOT = (60.0, HY)

b = Part.makeBox(PW2, PD2, PT2)
cuts = []
for x, d in zip(PX, PEGS):
    b = b.fuse(Part.makeCylinder(d / 2.0, 7.0, App.Vector(x, PY, PT2)))
for x, d in M3 + M2:
    cuts.append(Part.makeCylinder(d / 2.0, PT2 + 2, App.Vector(x, HY, -1)))
cuts.append(Part.makeBox(3.4, 6.4, PT2 + 2, App.Vector(SLOT[0] - 1.7, SLOT[1] - 3.2, -1)))
for c in cuts:
    b = b.cut(c)
b = clip_corner(b, 6.0, PT2)

finish(b, 'Gladiator_Coupon_B_Fits', 'Coupon B - spigot pegs, screw clearance, rail slot',
       'pegs 13.6/13.8/14.0; M3 3.2/3.4/3.6 then M2 2.2/2.4/2.6; rail slot at the far end')
fb = [('peg%d' % (i + 1), x, PY, d / 2.0) for i, (x, d) in enumerate(zip(PX, PEGS))]
fb += [('M3 %.1f' % d, x, HY, d / 2.0) for x, d in M3]
fb += [('M2 %.1f' % d, x, HY, d / 2.0) for x, d in M2]
fb += [('slot', SLOT[0], SLOT[1], 3.2)]
gaps_report(fb, PW2, PD2, 'B:')

# ============================================================== retire v2
old = os.path.join(INCOMING, 'Gladiator_FitCoupon_v2.stl')
if os.path.exists(old):
    os.remove(old)
    print('\nremoved the superseded all-in-one v2 from the incoming folder')

print()
print('=== size comparison ===')
print('  all-in-one v2      25345 mm3   ~31 g')
print('  A + B together     %5.0f mm3   ~%.0f g' % (a.Volume + b.Volume,
                                                    (a.Volume + b.Volume) / 1000.0 * 1.24))
print('  A alone (the one blocking rails + deck)  %5.0f mm3  ~%.1f g'
      % (a.Volume, a.Volume / 1000.0 * 1.24))
print()
print('incoming folder:')
for f in sorted(os.listdir(INCOMING)):
    if f.lower().endswith('.stl'):
        print('   %-50s %6.0f kB' % (f, os.path.getsize(os.path.join(INCOMING, f)) / 1024.0))
