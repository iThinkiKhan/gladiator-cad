"""Do the driver fins block the mast head's ToF across its pan sweep?

Frustum is the same nominal 60x60 deg cone the head workstream uses, rebuilt in
global coords and swept over the v0.3 pan range.
"""
import sys, math, json
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A, Part

O = []
def p(s): O.append(s)

C0 = A.Vector(39.5, 113.0, 0.0)          # mast axis
TZ = 205.0                                # tilt axis Z, v0.3
TY = -26.0                                # tilt axis local Y
PAN = [float(x) for x in range(-20, 181, 5)]
TILT = [-25.0, 0.0, 25.0]

CANT, X0, Z0, STANDOFF = 45.0, 8.0, 100.0, 15.0
BU, BV = 49.5, 51.0
HS_V0, HS_V1, HS_U0, HS_U1 = 9.5, 41.5, 8.75, 40.75
PCB_T, HS_PROUD = 3.2, 28.0
th = math.radians(CANT)
N = A.Vector(-math.sin(th), 0.0, math.cos(th))
VV = A.Vector(-math.cos(th), 0.0, -math.sin(th))
ORG = A.Vector(X0, 90.0, Z0)

def at(u, v, w=0.0):
    return A.Vector(ORG.x + VV.x*v + N.x*w, ORG.y + u, ORG.z + VV.z*v + N.z*w)

def fins_left():
    pts = [at(HS_U0, HS_V0, PCB_T), at(HS_U1, HS_V0, PCB_T),
           at(HS_U1, HS_V1, PCB_T), at(HS_U0, HS_V1, PCB_T)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
        A.Vector(N.x*HS_PROUD, N.y*HS_PROUD, N.z*HS_PROUD))

FL = fins_left()
FR = FL.copy()
FR.transformShape(A.Matrix(-1, 0, 0, 79.0, 0, 1, 0, 0, 0, 0, 1, 0))

def frustum():
    """60x60 deg, anchored at the optical origin, 400 mm long - no near gap."""
    def sq(y, half):
        return Part.makePolygon([A.Vector(-17 - half, y, TZ - half),
                                 A.Vector(-17 + half, y, TZ - half),
                                 A.Vector(-17 + half, y, TZ + half),
                                 A.Vector(-17 - half, y, TZ + half),
                                 A.Vector(-17 - half, y, TZ - half)])
    L = 400.0
    far = 0.5 + L * math.tan(math.radians(30))
    return Part.makeLoft([sq(-55.0, 0.5), sq(-55.0 - L, far)], True)

def hit(a, b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox):
            return 0.0
        return a.common(b).Volume
    except Exception:
        return 0.0

base = frustum()
worst = []
blocked = 0
tests = 0
for pan in PAN:
    for tilt in TILT:
        f = base.copy()
        f.rotate(A.Vector(0, TY, TZ), A.Vector(1, 0, 0), tilt)
        f.rotate(A.Vector(0, 0, 0), A.Vector(0, 0, 1), pan)
        f.translate(C0)
        for nm, fin in (('left', FL), ('right', FR)):
            v = hit(f, fin)
            tests += 1
            if v > 0.05:
                blocked += 1
                worst.append((v, pan, tilt, nm))
worst.sort(reverse=True)
p('tests %d   blocked poses %d' % (tests, blocked))
if worst:
    p('')
    p('worst intrusions (mm3 of fin inside the ToF cone):')
    for v, pan, tilt, nm in worst[:15]:
        p('   pan %6.1f  tilt %5.1f  %-5s  %9.1f mm3' % (pan, tilt, nm, v))
    pans = sorted(set(w[1] for w in worst))
    p('')
    p('pan angles affected: %.0f .. %.0f' % (min(pans), max(pans)))
    p('clear pan range: %s' % [x for x in PAN if x not in pans][:20])
else:
    p('no intrusion at any sampled pose')

p('')
p('fin envelope, left : X %.2f..%.2f  Y %.1f..%.1f  Z %.2f..%.2f'
  % (FL.BoundBox.XMin, FL.BoundBox.XMax, FL.BoundBox.YMin, FL.BoundBox.YMax,
     FL.BoundBox.ZMin, FL.BoundBox.ZMax))
p('ToF apex is at Z %.1f; fins top out at Z %.1f' % (TZ, FL.BoundBox.ZMax))

open('/tmp/fov.txt', 'w').write(chr(10).join(O))
