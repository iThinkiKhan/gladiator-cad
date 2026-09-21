"""Driver mount v3 - 45 degree wedge, standoffs, uses the deck bosses as printed.

Fastening is Option A, settled from the deck solid: the heat-set insert goes into
the deck's own D4.6 boss pocket and the screw comes DOWN from the mount. The
mount therefore needs a D3.6 clearance hole and a clear column above it. The
wedge is kept outboard of X 12 so both screws have open sky.

45 degrees so every overhanging face is at the printable limit.

Built in stages with a solid check after each, because the previous attempt
fused everything at once and produced 11 disjoint solids.
"""
import sys, math, json, hashlib
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as A, Part, MeshPart
from pathlib import Path

ROOT = Path('/home/buralien/projects/gladiator-cad')
MASTER = ROOT / 'cad/master/Gladiator_Master.FCStd'
OUT = ROOT / 'cad/drivers/v3-wedge45'
(OUT / 'stl').mkdir(parents=True, exist_ok=True)

CANT = 45.0
X0, Z0 = 8.0, 100.0          # board (u=0,v=0) corner
STANDOFF = 15.0
BOSS_OD, BOSS_BORE, BOSS_DEPTH, BOSS_LEN = 9.0, 4.6, 8.0, 9.0
DECK_TOP, FOOT_TOP = 52.0, 62.0
DECK_BOSS_D, DECK_BOSS_TOP = 9.0, 58.0
SCREWS = [(14.5, 95.0), (14.5, 135.0)]
M3_CLEAR = 3.6
RAIL_RELIEF = (12.0, 120.0, 8.0, 54.9)
CLR = 0.4
TRACK_X = -50.0
BU, BV = 49.5, 51.0
HOLES = [(u, v) for u in (5.0, 44.5) for v in (5.75, 45.25)]
HS_V0, HS_V1, HS_U0, HS_U1 = 9.5, 41.5, 8.75, 40.75
PCB_T, HS_PROUD = 3.2, 28.0
RIBS = [(89.0, 97.0), (110.5, 119.0), (132.5, 140.5)]
WEDGE_X_IN = 12.0            # wedge stays outboard of this, so screws stay open

th = math.radians(CANT)
N = A.Vector(-math.sin(th), 0.0, math.cos(th))
VV = A.Vector(-math.cos(th), 0.0, -math.sin(th))
ORG = A.Vector(X0, 90.0, Z0)

def at(u, v, w=0.0):
    return A.Vector(ORG.x + VV.x*v + N.x*w, ORG.y + u, ORG.z + VV.z*v + N.z*w)

def hit(a, b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox):
            return 0.0
        return a.common(b).Volume
    except Exception:
        return 0.0

before = hashlib.sha256(MASTER.read_bytes()).hexdigest()
d = A.openDocument(str(MASTER))
rep = {'cant_deg': CANT, 'standoff_mm': STANDOFF, 'board_origin': [X0, 90.0, Z0],
       'stages': [], 'checks': {}, 'notes': []}

def stage(name, shape):
    ok = shape.isValid() and len(shape.Solids) == 1
    rep['stages'].append({'stage': name, 'solids': len(shape.Solids),
                          'valid': shape.isValid(), 'single': ok,
                          'vol_cm3': round(shape.Volume / 1000.0, 2)})
    return ok

W_BOSS = -STANDOFF
# boss plane in XZ is the 45 deg line Z = X + C
C_LINE = at(0, 0, W_BOSS).z - at(0, 0, W_BOSS).x
rep['checks']['boss_line_Z_eq_X_plus'] = round(C_LINE, 3)
X_LOW = DECK_TOP - C_LINE                     # where the boss plane meets the deck top

# ---- stage 1: foot -------------------------------------------------------
foot = Part.makeBox(19.0, 51.5, FOOT_TOP - DECK_TOP, A.Vector(0.0, 89.0, DECK_TOP))
for x, y in SCREWS:
    foot = foot.cut(Part.makeCylinder(DECK_BOSS_D / 2 + CLR,
                                      DECK_BOSS_TOP - DECK_TOP + 0.05,
                                      A.Vector(x, y, DECK_TOP - 0.05)))
rx, ry, rd, rz = RAIL_RELIEF
foot = foot.cut(Part.makeCylinder(rd / 2 + CLR / 2, rz - DECK_TOP + 0.05,
                                  A.Vector(rx, ry, DECK_TOP - 0.05)))
stage('foot', foot)

# ---- stage 2: wedge ribs -------------------------------------------------
def rib(y0, y1):
    pts = [A.Vector(X_LOW, y0, DECK_TOP),
           A.Vector(WEDGE_X_IN, y0, WEDGE_X_IN + C_LINE),
           A.Vector(WEDGE_X_IN, y0, DECK_TOP)]
    f = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return f.extrude(A.Vector(0.0, y1 - y0, 0.0))

body = foot
for y0, y1 in RIBS:
    body = body.fuse(rib(y0, y1))
body = body.removeSplitter()
stage('foot+ribs', body)

# ---- stage 3: boss plate on the 45 deg plane -----------------------------
pts = [at(-2.0, -3.0, W_BOSS), at(BU + 2.0, -3.0, W_BOSS),
       at(BU + 2.0, BV + 3.0, W_BOSS), at(-2.0, BV + 3.0, W_BOSS)]
plate = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
    A.Vector(-N.x * 5.0, -N.y * 5.0, -N.z * 5.0))
# keep the plate out of the screw columns and off the deck
plate = plate.cut(Part.makeBox(40.0, 60.0, 80.0, A.Vector(WEDGE_X_IN, 85.0, DECK_TOP)))
plate = plate.cut(Part.makeBox(80.0, 60.0, 40.0, A.Vector(-60.0, 85.0, DECK_TOP - 40.0)))
# lighten
win = Part.Face(Part.makePolygon([
    at(9.0, 9.0, W_BOSS + 1), at(BU - 9.0, 9.0, W_BOSS + 1),
    at(BU - 9.0, BV - 9.0, W_BOSS + 1), at(9.0, BV - 9.0, W_BOSS + 1),
    at(9.0, 9.0, W_BOSS + 1)])).extrude(A.Vector(-N.x * 8, -N.y * 8, -N.z * 8))
plate = plate.cut(win)
body = body.fuse(plate).removeSplitter()
stage('foot+ribs+plate', body)

# ---- stage 4: bosses -----------------------------------------------------
for u, v in HOLES:
    body = body.fuse(Part.makeCylinder(BOSS_OD / 2, BOSS_LEN,
                                       at(u, v, W_BOSS - BOSS_LEN), N))
body = body.removeSplitter()
stage('with bosses', body)

# ---- stage 5: clearance against what is printed --------------------------
for nm in ['UpperDeck', 'SideRailLeft', 'ChassisDeck']:
    o = d.getObject(nm)
    if o and hit(body, o.Shape) > 0.05:
        v_ = hit(body, o.Shape)
        body = body.cut(o.Shape)
        rep['notes'].append('cut %.1f mm3 against %s at zero offset' % (v_, nm))
body = body.removeSplitter()
stage('after clearance cuts', body)

# ---- stage 6: bores ------------------------------------------------------
for u, v in HOLES:
    body = body.cut(Part.makeCylinder(BOSS_BORE / 2, BOSS_DEPTH + 0.2,
                                      at(u, v, W_BOSS - BOSS_DEPTH), N))
for x, y in SCREWS:
    body = body.cut(Part.makeCylinder(M3_CLEAR / 2, FOOT_TOP - DECK_BOSS_TOP + 0.2,
                                      A.Vector(x, y, DECK_BOSS_TOP - 0.1)))
body = body.removeSplitter()
stage('final', body)

# ---- checks ---------------------------------------------------------------
rep['checks']['single_solid'] = body.isValid() and len(body.Solids) == 1
rep['checks']['volume_cm3'] = round(body.Volume / 1000.0, 2)
b = body.BoundBox
rep['checks']['bbox'] = [round(q, 2) for q in
                         (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)]
for x, y in SCREWS:
    pr = Part.makeCylinder(M3_CLEAR / 2 - 0.3, FOOT_TOP - DECK_BOSS_TOP - 0.2,
                           A.Vector(x, y, DECK_BOSS_TOP + 0.1))
    rep['checks']['screw_hole_open_%.0f' % y] = hit(pr, body) < 0.3
    pk = Part.makeCylinder(DECK_BOSS_D / 2 - 0.3, DECK_BOSS_TOP - DECK_TOP - 0.2,
                           A.Vector(x, y, DECK_TOP + 0.1))
    rep['checks']['boss_pocket_clear_%.0f' % y] = hit(pk, body) < 0.3
    ac = Part.makeCylinder(3.5, 70.0, A.Vector(x, y, FOOT_TOP))
    rep['checks']['driver_access_%.0f_mm3' % y] = round(hit(ac, body), 1)

board = Part.Face(Part.makePolygon([at(0, 0), at(BU, 0), at(BU, BV), at(0, BV),
                                    at(0, 0)])).extrude(
    A.Vector(N.x * PCB_T, N.y * PCB_T, N.z * PCB_T))
fins = Part.Face(Part.makePolygon([
    at(HS_U0, HS_V0, PCB_T), at(HS_U1, HS_V0, PCB_T),
    at(HS_U1, HS_V1, PCB_T), at(HS_U0, HS_V1, PCB_T),
    at(HS_U0, HS_V0, PCB_T)])).extrude(
    A.Vector(N.x * HS_PROUD, N.y * HS_PROUD, N.z * HS_PROUD))
rep['checks']['fin_tip_X'] = round(fins.BoundBox.XMin, 2)
rep['checks']['fins_inside_track_mm'] = round(fins.BoundBox.XMin - TRACK_X, 2)
rep['checks']['fin_top_Z'] = round(fins.BoundBox.ZMax, 2)

rep['checks']['clashes'] = {}
for nm in ['UpperDeck', 'SideRailLeft', 'SideRailRight', 'ChassisDeck', 'BatteryBox',
           'MastTube', 'MastBase', 'PowerShield', 'AntennaPost', 'S3Board',
           'Breadboard', 'DriverMountRight']:
    o = d.getObject(nm)
    if not o or not getattr(o, 'Shape', None) or o.Shape.isNull():
        continue
    for lbl, s in (('mount', body), ('board', board), ('fins', fins)):
        v_ = hit(s, o.Shape)
        if v_ > 0.05:
            rep['checks']['clashes']['%s/%s' % (lbl, nm)] = round(v_, 1)

rep['checks']['standoff_clear'] = all(
    hit(Part.makeCylinder(3.0, STANDOFF, at(u, v, W_BOSS), N), body) < 0.05
    for u, v in HOLES)
sl = Part.makeBox(70, 60, 0.4, A.Vector(-25, 85, DECK_TOP - 0.01))
rep['checks']['deck_bearing_mm2'] = round(hit(sl, body) / 0.4, 1)
rep['checks']['master_unchanged'] = (
    hashlib.sha256(MASTER.read_bytes()).hexdigest() == before)

if rep['checks']['single_solid']:
    doc = A.newDocument('DriverMount_v3')
    o1 = doc.addObject('Part::Feature', 'DriverMount_v3_Left')
    o1.Shape = body
    mir = body.copy()
    mir.transformShape(A.Matrix(-1, 0, 0, 79.0, 0, 1, 0, 0, 0, 0, 1, 0))
    o2 = doc.addObject('Part::Feature', 'DriverMount_v3_Right')
    o2.Shape = mir
    doc.recompute()
    doc.saveAs(str(OUT / 'DriverMount_v3.FCStd'))
    Part.export([o1, o2], str(OUT / 'DriverMount_v3.step'))
    for nm, sh in [('DriverMount_v3_Left', body), ('DriverMount_v3_Right', mir)]:
        s = sh.copy()
        s.translate(A.Vector(0, 0, -s.BoundBox.ZMin))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01,
                               AngularDeflection=0.0872665, Relative=False
                               ).write(str(OUT / 'stl' / (nm + '.stl')))
    (OUT / 'validation.json').write_text(json.dumps(rep, indent=2) + chr(10))

Path('/tmp/drv3.json').write_text(json.dumps(rep, indent=2))
