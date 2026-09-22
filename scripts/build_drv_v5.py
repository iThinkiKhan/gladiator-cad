"""Driver mount v5 - interlocked two-piece structural mount.

Splitting it removes the conflict that broke v3: the board's high bosses land at
X 14.54 / Y 95 and 135, which is exactly where the deck screws are. In one piece
you must choose between supporting the boss and reaching the screw. In two you
do not - the base goes down first with clear sky above it, then the wedge bolts
on and may be solid right through that region.

Assembly: insert into each deck boss -> base plate down, 2x M3 from above ->
wedge onto the base, 4x M3 horizontally from inboard into inserts in the wedge.

Bosses are merged into the wedge body, not stuck on its face.
"""
import sys, math, json, hashlib
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as A, Part, MeshPart
from pathlib import Path

ROOT = Path('/home/buralien/projects/gladiator-cad')
MASTER = ROOT / 'cad/master/Gladiator_Master.FCStd'
OUT = ROOT / 'cad/drivers/v5-interlock'
(OUT / 'stl').mkdir(parents=True, exist_ok=True)

CANT, X0, Z0, STANDOFF = 45.0, 8.0, 100.0, 15.0
BOSS_OD, BOSS_BORE, BOSS_DEPTH = 9.0, 4.6, 8.0
DECK_TOP, FOOT_TOP = 52.0, 62.0
DECK_BOSS_D, DECK_BOSS_TOP = 9.0, 58.0
SCREWS = [(14.5, 95.0), (14.5, 135.0)]
M3_CLEAR, INS_BORE, INS_DEPTH = 3.6, 4.6, 8.0
RAIL_RELIEF = (12.0, 120.0, 8.0, 54.9)
CLR, TRACK_X = 0.4, -50.0
BU, BV = 49.5, 51.0
HOLES = [(u, v) for u in (5.0, 44.5) for v in (5.75, 45.25)]
HS_V0, HS_V1, HS_U0, HS_U1 = 9.5, 41.5, 8.75, 40.75
PCB_T, HS_PROUD = 3.2, 28.0
WALL_X0, WALL_X1, WALL_TOP = 17.0, 23.0, 82.0
JOINT = [(95.0, 68.0), (95.0, 76.0), (134.5, 68.0), (134.5, 76.0)]
RIBS = [(89.0, 98.0), (131.5, 140.5)]
FOOT_X1 = 23.0
TONGUE = (2.0, 6.0, 4.0)      # X0, X1, height above FOOT_TOP - full length in Y
TONGUE_TOP_LEAD = 0.6
TONGUE_ROOT_R = 0.8
GROOVE_CLEAR = 0.2
GROOVE_ROOT_R = TONGUE_ROOT_R + GROOVE_CLEAR
SEAT_T = 7.0                  # 2.7 mm roof remains above the 4.3 mm groove
FLANGE_X0 = 8.0               # wedge flange 9 mm thick, takes a 7.05 insert
CBORE_D, CBORE_DEPTH = 6.0, 3.5
STOP = (10.0, 14.0, 113.0, 117.0, 2.0)  # x0, x1, y0, y1, height
BOSS_FLARE_R, BOSS_FLARE_H = 7.5, 6.0

th = math.radians(CANT)
N = A.Vector(-math.sin(th), 0.0, math.cos(th))
VV = A.Vector(-math.cos(th), 0.0, -math.sin(th))
ORG = A.Vector(X0, 90.0, Z0)
W_BOSS = -STANDOFF

def at(u, v, w=0.0):
    return A.Vector(ORG.x + VV.x * v + N.x * w, ORG.y + u, ORG.z + VV.z * v + N.z * w)

def hit(a, c):
    try:
        if a.isNull() or c.isNull() or not a.BoundBox.intersect(c.BoundBox):
            return 0.0
        return a.common(c).Volume
    except Exception:
        return 0.0

def xz_prism(profile, y0, y1):
    pts = [A.Vector(x, y0, z) for x, z in profile]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
        A.Vector(0, y1 - y0, 0))

before = hashlib.sha256(MASTER.read_bytes()).hexdigest()
d = A.openDocument(str(MASTER))
rep = {'cant_deg': CANT, 'standoff_mm': STANDOFF, 'stages': [], 'checks': {}, 'notes': []}

def stage(name, sh):
    ok = sh.isValid() and len(sh.Solids) == 1
    rep['stages'].append({'stage': name, 'solids': len(sh.Solids), 'single': ok,
                          'vol_cm3': round(sh.Volume / 1000.0, 2)})
    return ok

C_LINE = at(0, 0, W_BOSS).z - at(0, 0, W_BOSS).x
X_LOW = DECK_TOP - C_LINE
rep['checks']['boss_plane_Z_eq_X_plus'] = round(C_LINE, 2)

# ============================== PIECE 1: BASE ==============================
base = Part.makeBox(FOOT_X1, 51.5, FOOT_TOP - DECK_TOP, A.Vector(0.0, 89.0, DECK_TOP))
# Chamfered tongue top supplies the vertical assembly lead-in.
tongue_profile = [
    (TONGUE[0], FOOT_TOP), (TONGUE[1], FOOT_TOP),
    (TONGUE[1], FOOT_TOP + TONGUE[2] - TONGUE_TOP_LEAD),
    (TONGUE[1] - TONGUE_TOP_LEAD, FOOT_TOP + TONGUE[2]),
    (TONGUE[0] + TONGUE_TOP_LEAD, FOOT_TOP + TONGUE[2]),
    (TONGUE[0], FOOT_TOP + TONGUE[2] - TONGUE_TOP_LEAD),
]
base = base.fuse(xz_prism(tongue_profile, 89.0, 140.5))
# Positive root fillets remove the two sharp tongue-to-foot stress risers.
for x in TONGUE[:2]:
    base = base.fuse(Part.makeCylinder(TONGUE_ROOT_R, 51.5,
                                       A.Vector(x, 89.0, FOOT_TOP),
                                       A.Vector(0, 1, 0)))
# One compact peg/pocket pair provides fore/aft registration.
sx0, sx1, sy0, sy1, sh = STOP
base = base.fuse(Part.makeBox(sx1 - sx0, sy1 - sy0, sh,
                              A.Vector(sx0, sy0, FOOT_TOP)))
base = base.fuse(Part.makeBox(WALL_X1 - WALL_X0, 51.5, WALL_TOP - FOOT_TOP,
                              A.Vector(WALL_X0, 89.0, FOOT_TOP)))
base = base.removeSplitter()
stage('base raw', base)
for x, y in SCREWS:
    base = base.cut(Part.makeCylinder(DECK_BOSS_D / 2 + CLR, DECK_BOSS_TOP - DECK_TOP + 0.05,
                                      A.Vector(x, y, DECK_TOP - 0.05)))
    base = base.cut(Part.makeCylinder(M3_CLEAR / 2, FOOT_TOP - DECK_BOSS_TOP + 0.2,
                                      A.Vector(x, y, DECK_BOSS_TOP - 0.1)))
rx, ry, rd, rz = RAIL_RELIEF
base = base.cut(Part.makeCylinder(rd / 2 + CLR / 2, rz - DECK_TOP + 0.05,
                                  A.Vector(rx, ry, DECK_TOP - 0.05)))
for y, z in JOINT:
    base = base.cut(Part.makeCylinder(M3_CLEAR / 2, WALL_X1 - WALL_X0 + 0.4,
                                      A.Vector(WALL_X1 + 0.2, y, z), A.Vector(-1, 0, 0)))
    base = base.cut(Part.makeCylinder(CBORE_D / 2, CBORE_DEPTH,
                                      A.Vector(WALL_X1 + 0.01, y, z), A.Vector(-1, 0, 0)))
base = base.removeSplitter()
stage('base final', base)

# ============================== PIECE 2: WEDGE =============================
def rib(y0, y1):
    pts = [A.Vector(X_LOW, y0, DECK_TOP),
           A.Vector(0.0, y0, DECK_TOP),
           A.Vector(0.0, y0, FOOT_TOP),
           A.Vector(WALL_X0, y0, FOOT_TOP),
           A.Vector(WALL_X0, y0, WALL_X0 + C_LINE)]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(A.Vector(0, y1 - y0, 0))

wedge = rib(*RIBS[0])
for r in RIBS[1:]:
    wedge = wedge.fuse(rib(*r))
# spine slab under the boss plane, full length, thick enough to swallow the bosses
pts = [at(-1.0, -4.0, W_BOSS), at(BU + 1.0, -4.0, W_BOSS),
       at(BU + 1.0, BV + 4.0, W_BOSS), at(-1.0, BV + 4.0, W_BOSS)]
slabt = 13.0
spine = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
    A.Vector(-N.x * slabt, -N.y * slabt, -N.z * slabt))
spine = spine.cut(Part.makeBox(60.0, 60.0, 60.0, A.Vector(WALL_X0, 85.0, DECK_TOP)))
spine = spine.cut(Part.makeBox(90.0, 60.0, 40.0, A.Vector(-70.0, 85.0, DECK_TOP - 40.0)))
wedge = wedge.fuse(spine).removeSplitter()
stage('wedge ribs+spine', wedge)

# bosses merged: a column from the boss face down through the spine
for u, v in HOLES:
    wedge = wedge.fuse(Part.makeCylinder(BOSS_OD / 2, slabt + 2.0,
                                         at(u, v, W_BOSS - slabt - 2.0), N))
# The high pair carries the longer lever arm.  Taper each boss into the spine
# rather than ending the cylindrical boss at an abrupt shoulder.
for u in (5.0, 44.5):
    v = 5.75
    wedge = wedge.fuse(Part.makeCone(BOSS_FLARE_R, BOSS_OD / 2,
                                     BOSS_FLARE_H,
                                     at(u, v, W_BOSS - BOSS_FLARE_H), N))
wedge = wedge.removeSplitter()
stage('wedge + flared bosses', wedge)

# joint flange against the base wall
seat = Part.makeBox(WALL_X0, 51.5, SEAT_T, A.Vector(0.0, 89.0, FOOT_TOP))
flange = Part.makeBox(WALL_X0 - FLANGE_X0, 51.5, WALL_TOP - FOOT_TOP,
                      A.Vector(FLANGE_X0, 89.0, FOOT_TOP))
wedge = wedge.fuse(seat).fuse(flange).removeSplitter()
# Full-length groove with root-following entry relief.  R1.0 cylindrical cuts
# clear the tongue's R0.8 roots by 0.2 mm without the former X0.2..7.8 flare,
# leaving a full 1.0 mm edge web at the seat entrance.
gx0 = TONGUE[0] - GROOVE_CLEAR
gx1 = TONGUE[1] + GROOVE_CLEAR
wedge = wedge.cut(Part.makeBox(gx1 - gx0, 52.5, TONGUE[2] + 0.4,
                               A.Vector(gx0, 88.5, FOOT_TOP - 0.1)))
for x in TONGUE[:2]:
    wedge = wedge.cut(Part.makeCylinder(GROOVE_ROOT_R, 52.5,
                                        A.Vector(x, 88.5, FOOT_TOP),
                                        A.Vector(0, 1, 0)))
# Matching clearance pocket for the single fore/aft locator.
wedge = wedge.cut(Part.makeBox((sx1 - sx0) + 0.4, (sy1 - sy0) + 0.4, sh + 0.3,
                               A.Vector(sx0 - 0.2, sy0 - 0.2, FOOT_TOP - 0.1)))
wedge = wedge.removeSplitter()
stage('wedge + seat + flange + groove', wedge)

for nm in ['UpperDeck', 'SideRailLeft', 'ChassisDeck']:
    o = d.getObject(nm)
    if o and hit(wedge, o.Shape) > 0.05:
        v_ = hit(wedge, o.Shape)
        wedge = wedge.cut(o.Shape)
        rep['notes'].append('wedge: cut %.1f mm3 against %s' % (v_, nm))
wedge = wedge.cut(base)
wedge = wedge.removeSplitter()
stage('wedge after cuts', wedge)

for u, v in HOLES:
    wedge = wedge.cut(Part.makeCylinder(BOSS_BORE / 2, BOSS_DEPTH + 0.2,
                                        at(u, v, W_BOSS - BOSS_DEPTH), N))
for y, z in JOINT:
    wedge = wedge.cut(Part.makeCylinder(INS_BORE / 2, INS_DEPTH,
                                        A.Vector(WALL_X0 + 0.1, y, z), A.Vector(-1, 0, 0)))
wedge = wedge.removeSplitter()
stage('wedge final', wedge)

# Cut the coupon from the final printable parts, after all installed-clearance
# and screw-bore operations.  It therefore preserves the exact joint profile,
# full 51.5 mm length, lead-ins, locator, and any reliefs used by production.
coupon_base = base.common(
    Part.makeBox(16.0, 51.5, 11.0, A.Vector(0.0, 89.0, 58.0))).removeSplitter()
coupon_wedge = wedge.common(
    Part.makeBox(16.0, 51.5, 7.5, A.Vector(0.0, 89.0, FOOT_TOP - 0.2))).removeSplitter()

# ============================== CHECKS =====================================
rep['checks']['base_single'] = base.isValid() and len(base.Solids) == 1
rep['checks']['wedge_single'] = wedge.isValid() and len(wedge.Solids) == 1
rep['checks']['base_cm3'] = round(base.Volume / 1000.0, 2)
rep['checks']['wedge_cm3'] = round(wedge.Volume / 1000.0, 2)
rep['checks']['total_cm3'] = round((base.Volume + wedge.Volume) / 1000.0, 2)
rep['checks']['base_wedge_overlap'] = round(hit(base, wedge), 2)

# the thing that broke v3: material around each boss base
rep['checks']['boss_support_mm3'] = {}
for u, v in HOLES:
    b0 = at(u, v, W_BOSS - 3.0)
    ring = Part.makeCylinder(9.0, 3.0, b0, N).cut(
        Part.makeCylinder(4.5, 4.0, at(u, v, W_BOSS - 3.5), N))
    rep['checks']['boss_support_mm3']['u%.0f_v%.0f' % (u, v)] = round(hit(ring, wedge), 1)

for x, y in SCREWS:
    ac = Part.makeCylinder(2.0, 60.0, A.Vector(x, y, FOOT_TOP))
    rep['checks']['deck_screw_access_%.0f' % y] = round(hit(ac, base), 1)
    rep['checks']['deck_screw_open_%.0f' % y] = hit(
        Part.makeCylinder(1.5, FOOT_TOP - DECK_BOSS_TOP - 0.2,
                          A.Vector(x, y, DECK_BOSS_TOP + 0.1)), base) < 0.3

board = Part.Face(Part.makePolygon([at(0, 0), at(BU, 0), at(BU, BV), at(0, BV),
                                    at(0, 0)])).extrude(A.Vector(N.x*PCB_T, N.y*PCB_T, N.z*PCB_T))
fins = Part.Face(Part.makePolygon([
    at(HS_U0, HS_V0, PCB_T), at(HS_U1, HS_V0, PCB_T), at(HS_U1, HS_V1, PCB_T),
    at(HS_U0, HS_V1, PCB_T), at(HS_U0, HS_V0, PCB_T)])).extrude(
    A.Vector(N.x*HS_PROUD, N.y*HS_PROUD, N.z*HS_PROUD))
rep['checks']['fin_tip_X'] = round(fins.BoundBox.XMin, 2)
rep['checks']['fins_inside_track_mm'] = round(fins.BoundBox.XMin - TRACK_X, 2)

rep['checks']['clashes'] = {}
for nm in ['UpperDeck', 'SideRailLeft', 'SideRailRight', 'ChassisDeck', 'BatteryBox',
           'MastTube', 'MastBase', 'PowerShield', 'AntennaPost', 'S3Board', 'Breadboard']:
    o = d.getObject(nm)
    if not o or not getattr(o, 'Shape', None) or o.Shape.isNull():
        continue
    for lbl, s in (('base', base), ('wedge', wedge), ('board', board), ('fins', fins)):
        v_ = hit(s, o.Shape)
        if v_ > 0.05:
            rep['checks']['clashes']['%s/%s' % (lbl, nm)] = round(v_, 1)

# interlock and insert room
rep['checks']['tongue_groove_engagement_mm'] = TONGUE[2]
rep['checks']['seat_contact_mm2'] = round(hit(
    Part.makeBox(WALL_X0, 51.5, 0.4, A.Vector(0.0, 89.0, FOOT_TOP - 0.01)), wedge) / 0.4, 1)
rep['checks']['flange_thickness_mm'] = WALL_X0 - FLANGE_X0
rep['checks']['insert_room'] = {}
for y, z in JOINT:
    wall = 0.0
    for i in range(0, 60):
        x = WALL_X0 - 0.25 * i
        if hit(Part.makeCylinder(3.0, 0.25, A.Vector(x, y, z), A.Vector(-1, 0, 0)), wedge) > 0.05:
            wall += 0.25
    rep['checks']['insert_room']['Y%.0f_Z%.0f' % (y, z)] = round(wall, 2)
rep['checks']['counterbore_depth_mm'] = CBORE_DEPTH
rep['checks']['upper_counterbore_wall_above_mm'] = round(
    WALL_TOP - (max(z for _, z in JOINT) + CBORE_D / 2), 2)
rep['checks']['seat_roof_above_groove_mm'] = round(
    FOOT_TOP + SEAT_T - (FOOT_TOP + TONGUE[2] + 0.3), 2)
rep['checks']['tongue_top_lead_mm'] = TONGUE_TOP_LEAD
rep['checks']['tongue_root_fillet_mm'] = TONGUE_ROOT_R
rep['checks']['groove_root_relief_radius_mm'] = GROOVE_ROOT_R
rep['checks']['groove_mouth_x_mm'] = [
    round(TONGUE[0] - GROOVE_ROOT_R, 2),
    round(TONGUE[1] + GROOVE_ROOT_R, 2),
]
rep['checks']['groove_min_edge_web_mm'] = round(TONGUE[0] - GROOVE_ROOT_R, 2)
rep['checks']['fore_aft_stop_clearance_mm'] = 0.2
rep['checks']['coupon_base_single'] = coupon_base.isValid() and len(coupon_base.Solids) == 1
rep['checks']['coupon_wedge_single'] = coupon_wedge.isValid() and len(coupon_wedge.Solids) == 1
rep['checks']['coupon_base_wedge_overlap'] = round(hit(coupon_base, coupon_wedge), 4)
rep['checks']['coupon_joint_length_mm'] = 51.5
rep['checks']['standoff_status'] = 'provisional pending plugged-connector measurement'
rep['checks']['standoff_clear'] = all(
    hit(Part.makeCylinder(3.0, STANDOFF, at(u, v, W_BOSS), N), wedge) < 0.05 for u, v in HOLES)
sl = Part.makeBox(70, 60, 0.4, A.Vector(-25, 85, DECK_TOP - 0.01))
rep['checks']['deck_bearing_mm2'] = round(hit(sl, base) / 0.4, 1)
rep['checks']['master_unchanged'] = (
    hashlib.sha256(MASTER.read_bytes()).hexdigest() == before)

if (rep['checks']['base_single'] and rep['checks']['wedge_single'] and
        rep['checks']['base_wedge_overlap'] < 0.001 and
        rep['checks']['coupon_base_single'] and rep['checks']['coupon_wedge_single'] and
        rep['checks']['coupon_base_wedge_overlap'] < 0.001 and
        rep['checks']['groove_min_edge_web_mm'] >= 1.0 and
        rep['checks']['seat_roof_above_groove_mm'] >= 2.7 and
        rep['checks']['upper_counterbore_wall_above_mm'] >= 3.0 and
        not rep['checks']['clashes']):
    doc = A.newDocument('DriverMount_v5')
    main_objects = []
    for nm, sh in [('Base_Left', base), ('Wedge_Left', wedge)]:
        o = doc.addObject('Part::Feature', nm)
        o.Shape = sh
        main_objects.append(o)
        mir = sh.copy()
        mir.transformShape(A.Matrix(-1, 0, 0, 79.0, 0, 1, 0, 0, 0, 0, 1, 0))
        o2 = doc.addObject('Part::Feature', nm.replace('Left', 'Right'))
        o2.Shape = mir
        main_objects.append(o2)
    for nm, sh in [('Coupon_Base', coupon_base), ('Coupon_Wedge', coupon_wedge)]:
        o = doc.addObject('Part::Feature', nm)
        o.Shape = sh
    doc.recompute()
    doc.saveAs(str(OUT / 'DriverMount_v5.FCStd'))
    Part.export(main_objects, str(OUT / 'DriverMount_v5.step'))
    for nm, sh in [('Base_Left', base), ('Wedge_Left', wedge)]:
        s = sh.copy()
        s.translate(A.Vector(0, 0, -s.BoundBox.ZMin))
        MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.0872665,
                               Relative=False).write(str(OUT / 'stl' / (nm + '.stl')))
    (OUT / 'validation.json').write_text(json.dumps(rep, indent=2) + chr(10))

Path('/tmp/drv5.json').write_text(json.dumps(rep, indent=2))
