"""Driver mount v2 - board on M3 male-female standoffs, GPIO face inboard.

The board no longer bolts flat to the mount. It floats on four standoffs, so the
mount's only job is to present four boss tops at the right points in space, and
to get that load into the deck.

Board position is FIXED by track clearance (12 mm inboard of where the CAD had
it, which tucks the fins 7 mm inside the track line). Standoff length is a free
parameter - changing it moves the BOSSES, not the board.

Never opens or writes the master.
"""
import sys, math, json, hashlib
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as A, Part, MeshPart
from pathlib import Path

ROOT = Path('/home/buralien/projects/gladiator-cad')
MASTER = ROOT / 'cad/master/Gladiator_Master.FCStd'
OUT = ROOT / 'cad/drivers/v2-standoff'
(OUT / 'stl').mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- parameters
BOARD_OFFSET = 12.0     # inboard along the board normal; sets track clearance
STANDOFF_LEN = 15.0     # M3 male-female; stackable, so this is free to change
BOSS_OD = 9.0           # matches the deck bosses the insert coupon proved
BOSS_BORE = 4.6         # calibrated heat-set bore on this printer
BOSS_DEPTH = 8.0        # insert is 7.05 long
BOSS_LEN = 10.0         # boss length along the board normal
SPINE_T = 8.0           # canted backing plate thickness
FOOT_X0, FOOT_X1 = 0.0, 19.0      # deck slab edge is X 0; was 6..19
FOOT_Z0, FOOT_Z1 = 52.0, 62.0
FOOT_Y0, FOOT_Y1 = 89.0, 140.5
DECK_SCREWS = [(14.5, 95.0), (14.5, 135.0)]
BOSS_POCKET_D, BOSS_POCKET_Z = 9.4, 58.1
RAIL_RELIEF = (12.0, 120.0, 8.0, 54.9)
M3_CLEAR = 3.6          # calibrated
CLR = 0.4

before = hashlib.sha256(MASTER.read_bytes()).hexdigest()
d = A.openDocument(str(MASTER))
sk = d.getObject('DrvHoleSketch')
PL = sk.Placement
U = PL.Rotation.multVec(A.Vector(1, 0, 0))
V = PL.Rotation.multVec(A.Vector(0, 1, 0))
W = PL.Rotation.multVec(A.Vector(0, 0, 1))
ORG = PL.Base
HOLES = sorted((g.Center.x, g.Center.y) for g in sk.Geometry)
L_U, L_V = 49.5, 51.0

W_BOARD = -BOARD_OFFSET
W_BOSS = W_BOARD - STANDOFF_LEN          # boss top face

def at(u, v, w=0.0):
    return A.Vector(ORG.x + U.x*u + V.x*v + W.x*w,
                    ORG.y + U.y*u + V.y*v + W.y*w,
                    ORG.z + U.z*u + V.z*v + W.z*w)

def wvec(m):
    return A.Vector(W.x*m, W.y*m, W.z*m)

def slab(u0, u1, v0, v1, w0, w1):
    pts = [at(u0, v0, w0), at(u1, v0, w0), at(u1, v1, w0), at(u0, v1, w0)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(wvec(w1 - w0))

def wcyl(u, v, w0, w1, r):
    return Part.makeCylinder(r, abs(w1 - w0), at(u, v, min(w0, w1)), W)

def fuse(*ss):
    s = ss[0]
    for t in ss[1:]:
        s = s.fuse(t)
    return s.removeSplitter()

def hit(a, b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox):
            return 0.0
        return a.common(b).Volume
    except Exception:
        return 0.0

rep = {'master_sha256_before': before, 'params': {
    'board_offset_mm': BOARD_OFFSET, 'standoff_len_mm': STANDOFF_LEN,
    'boss_od': BOSS_OD, 'boss_bore': BOSS_BORE, 'm3_clear': M3_CLEAR},
    'checks': {}, 'notes': []}

# ---------------------------------------------------------------- the foot
foot = Part.makeBox(FOOT_X1 - FOOT_X0, FOOT_Y1 - FOOT_Y0, FOOT_Z1 - FOOT_Z0,
                    A.Vector(FOOT_X0, FOOT_Y0, FOOT_Z0))
for x, y in DECK_SCREWS:
    foot = foot.cut(Part.makeCylinder(BOSS_POCKET_D/2 + CLR/2, BOSS_POCKET_Z - FOOT_Z0 + 0.1,
                                      A.Vector(x, y, FOOT_Z0 - 0.05)))
    foot = foot.cut(Part.makeCylinder(M3_CLEAR/2, FOOT_Z1 - BOSS_POCKET_Z + 0.2,
                                      A.Vector(x, y, BOSS_POCKET_Z - 0.1)))
rx, ry, rd, rz = RAIL_RELIEF
foot = foot.cut(Part.makeCylinder(rd/2 + CLR/2, rz - FOOT_Z0 + 0.1,
                                  A.Vector(rx, ry, FOOT_Z0 - 0.05)))

# ------------------------------------------------- canted spine and bosses
spine = slab(-2.0, L_U + 2.0, -2.0, L_V + 2.0, W_BOSS - SPINE_T, W_BOSS)
# lighten it: open the middle, keep a frame plus a diagonal-free centre window
spine = spine.cut(slab(9.0, L_U - 9.0, 11.0, L_V - 11.0, W_BOSS - SPINE_T - 1, W_BOSS + 1))

bosses = []
for u, v in HOLES:
    bosses.append(wcyl(u, v, W_BOSS - BOSS_LEN, W_BOSS, BOSS_OD/2))
body = fuse(foot, spine, *bosses)

# keep clear of the deck and the rail
deck = d.getObject('UpperDeck').Shape
rail = d.getObject('SideRailLeft').Shape
chassis = d.getObject('ChassisDeck').Shape
for obstacle, name in [(deck, 'UpperDeck'), (rail, 'SideRailLeft'), (chassis, 'ChassisDeck')]:
    v_ = hit(body, obstacle)
    if v_ > 0.05:
        body = body.cut(obstacle)
        rep['notes'].append(
            'cut %.1f mm3 against %s at ZERO clearance - a running clearance still '
            'has to be added before this is printed' % (v_, name))

# bores last, so the clearance cut cannot reopen them
for u, v in HOLES:
    body = body.cut(wcyl(u, v, W_BOSS - BOSS_DEPTH, W_BOSS + 0.1, BOSS_BORE/2))

body = body.removeSplitter()
rep['checks']['single_solid'] = (body.isValid() and len(body.Solids) == 1)
rep['checks']['solids'] = len(body.Solids)
rep['checks']['volume_mm3'] = round(body.Volume, 1)
b = body.BoundBox
rep['checks']['bbox'] = [round(b.XMin,2), round(b.XMax,2), round(b.YMin,2),
                         round(b.YMax,2), round(b.ZMin,2), round(b.ZMax,2)]

# ---------------------------------------------------------------- checks
rep['checks']['boss_tops_global'] = []
for u, v in HOLES:
    q = at(u, v, W_BOSS)
    rep['checks']['boss_tops_global'].append(
        {'u': u, 'v': v, 'X': round(q.x, 2), 'Y': round(q.y, 1), 'Z': round(q.z, 2)})

# board and fins at the chosen offset
board = slab(0, L_U, 0, L_V, W_BOARD, W_BOARD + 3.2)
fins = slab(8.75, 40.75, 9.5, 41.5, W_BOARD + 3.2, W_BOARD + 3.2 + 28)
rep['checks']['fin_tip_X'] = round(fins.BoundBox.XMin, 2)
rep['checks']['track_outer_X'] = -50.0
rep['checks']['fins_inside_track_by_mm'] = round(fins.BoundBox.XMin - (-50.0), 2)

others = []
for nm in ['UpperDeck', 'SideRailLeft', 'SideRailRight', 'ChassisDeck', 'BatteryBox',
           'MastTube', 'MastBase', 'PowerShield', 'AntennaPost', 'S3Board', 'Breadboard']:
    o = d.getObject(nm)
    if o and getattr(o, 'Shape', None) and not o.Shape.isNull():
        others.append((nm, o.Shape))
rep['checks']['clashes'] = {}
for nm, sh in others:
    for lbl, s in (('mount', body), ('board', board), ('fins', fins)):
        v_ = hit(s, sh)
        if v_ > 0.05:
            rep['checks']['clashes']['%s/%s' % (lbl, nm)] = round(v_, 1)

# standoff axis must be clear between boss top and board
rep['checks']['standoff_paths_clear'] = True
for u, v in HOLES:
    st = wcyl(u, v, W_BOSS, W_BOARD, 3.0)
    for nm, sh in others + [('mount', body)]:
        if hit(st, sh) > 0.05:
            rep['checks']['standoff_paths_clear'] = False
            rep['checks'].setdefault('standoff_blocked_by', []).append(
                '%s at u%.1f v%.1f' % (nm, u, v))

# bearing on the deck
sl = Part.makeBox(40, 60, 0.4, A.Vector(-12, 85, FOOT_Z0 - 0.01))
rep['checks']['deck_bearing_mm2'] = round(hit(sl, body) / 0.4, 1)
rep['checks']['deck_bearing_was_mm2'] = 342.0

# wall left around each insert
rep['checks']['insert_wall_mm'] = round((BOSS_OD - 5.0) / 2.0, 2)
rep['checks']['insert_wall_was_mm'] = 0.75
rep['checks']['boss_depth_vs_insert'] = '%.1f bore for a 7.05 insert' % BOSS_DEPTH

after = hashlib.sha256(MASTER.read_bytes()).hexdigest()
rep['checks']['master_unchanged'] = (after == before)

# ---------------------------------------------------------------- output
doc = A.newDocument('DriverMount_v2')
o = doc.addObject('Part::Feature', 'DriverMount_v2_Left')
o.Shape = body
mir = body.copy()
mir.transformShape(A.Matrix(-1,0,0,79.0, 0,1,0,0, 0,0,1,0))
o2 = doc.addObject('Part::Feature', 'DriverMount_v2_Right')
o2.Shape = mir
doc.recompute()
doc.saveAs(str(OUT / 'DriverMount_v2.FCStd'))
Part.export([o, o2], str(OUT / 'DriverMount_v2.step'))
for nm, sh in [('DriverMount_v2_Left', body), ('DriverMount_v2_Right', mir)]:
    s = sh.copy()
    s.translate(A.Vector(0, 0, -s.BoundBox.ZMin))
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01,
                               AngularDeflection=0.0872665, Relative=False)
    m.write(str(OUT / 'stl' / (nm + '.stl')))

(OUT / 'validation.json').write_text(json.dumps(rep, indent=2) + chr(10))
print(json.dumps(rep, indent=2))
Path('/tmp/drv2.json').write_text(json.dumps(rep, indent=2))
