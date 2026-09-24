"""Driver mount v5 - interlocked two-piece structural mount.

Splitting it removes the conflict that broke v3: the board's high bosses land at
X 14.54 / Y 95 and 135, which is exactly where the deck screws are. In one piece
you must choose between supporting the boss and reaching the screw. In two you
do not - the base goes down first with clear sky above it, then the wedge bolts
on and may be solid right through that region.

Assembly: insert into each deck boss -> base plate down, 2x M3 from above ->
wedge dropped straight onto the base, 4x M3 from inboard into inserts in the
wedge (upper pair splayed 22 deg to clear the mast). Removal reverses this with
the mast left in place; the checks at the end prove each path is clear.

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
BOSS_COLUMN_H = BOSS_DEPTH + 3.0
BOSS_BASE_CLEARANCE = 0.4     # trims the wedge only; see CUP_RELIEF_* for the base
# v5b base (2026-09-24): printed wedges could not seat because the upper cups
# struck the base slots, which left only 0.25-0.3 mm at the tilted exit edge.
# The cups locate nothing (the tongue does), so the base slot is opened well
# beyond the cup in the seating directions (down, inboard, along the axis) and
# less toward the side joint screws, whose counterbore walls set the limit.
CUP_RELIEF_RADIAL = 1.7
CUP_RELIEF_SIDE = 0.6         # toward the upper joint screw only
CUP_RELIEF_AXIAL = 1.0
MIN_SIDE_WEB = 1.6            # to the splayed upper joint counterbores
# v5c base (2026-09-24, Jim): the wall behind and beside each cup is not
# structural. The bore continues down its own 45 deg axis out through the
# inboard face, and the wall ends beyond the cups are dropped, instead of the
# wall rising behind the cup. The floor stops 1 mm above the lower joint
# counterbore under each cup; that screw's head seats on the counterbore
# floor, which is untouched.
CUP_RELIEF_BACK = 10.0
LOWER_CBORE_WEB = 1.0
RELIEF_FLOOR_Z = 68.0 + 3.0 + LOWER_CBORE_WEB
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
# (Y, Z, yaw deg).  The upper pair sits between the boss slots and the mast
# tube's shadow, so it is splayed in plan: the driver path runs beside the mast
# and the mount comes off with the mast still fitted.
JOINT_YAW = 22.0
JOINT = [(95.0, 68.0, 0.0), (105.0, 76.0, -JOINT_YAW),
         (134.5, 68.0, 0.0), (124.5, 76.0, JOINT_YAW)]
ASSEMBLY_LIFT = 5.0           # vertical travel to engage tongue and locator
SLOT_RISE = 14.0              # vertical sweep of the boss clearance to the wall top
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
GUSSET_WIDTH = BOSS_OD       # full-width solid pedestal under each high boss

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

def joint_dir(yaw):
    """Unit vector from the seat toward the screw head (inboard)."""
    a = math.radians(yaw)
    return A.Vector(math.cos(a), math.sin(a), 0.0)

def joint_point(y, z, yaw, x):
    """Point on a joint screw axis at the given X."""
    D = joint_dir(yaw)
    return A.Vector(WALL_X1, y, z) + D * ((x - WALL_X1) / D.x)

def xz_prism(profile, y0, y1):
    pts = [A.Vector(x, y0, z) for x, z in profile]
    return Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(
        A.Vector(0, y1 - y0, 0))

before = hashlib.sha256(MASTER.read_bytes()).hexdigest()
# The 2026-09-23 wedges are already printed with inserts set; the rebuild must
# reproduce them exactly.
_printed = A.openDocument(str(OUT / 'DriverMount_v5.FCStd'))
PRINTED_WEDGE = _printed.getObject('Wedge_Left').Shape.copy()
A.closeDocument(_printed.Name)
d = A.openDocument(str(MASTER))
rep = {'cant_deg': CANT, 'standoff_mm': STANDOFF, 'stages': [], 'checks': {}, 'notes': []}

def stage(name, sh):
    ok = sh.isValid() and len(sh.Solids) == 1
    row = {'stage': name, 'solids': len(sh.Solids), 'single': ok,
           'vol_cm3': round(sh.Volume / 1000.0, 2)}
    if not ok:
        row['solid_vol_cm3'] = [round(s.Volume / 1000.0, 3) for s in sh.Solids]
    rep['stages'].append(row)
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
joint_cuts = []
for y, z, yaw in JOINT:
    D = joint_dir(yaw)
    run = (WALL_X1 - WALL_X0) / D.x
    hole = Part.makeCylinder(M3_CLEAR / 2, run + 0.4, A.Vector(WALL_X1, y, z) + D * 0.2, -D)
    # Start the counterbore outside the face so a splayed mouth is fully open;
    # its floor is CBORE_DEPTH below the face along the screw axis.
    lead = CBORE_D / 2 * math.tan(abs(math.radians(yaw))) + 0.01
    cbore = Part.makeCylinder(CBORE_D / 2, CBORE_DEPTH + lead,
                              A.Vector(WALL_X1, y, z) + D * lead, -D)
    joint_cuts.append(hole.fuse(cbore))
    base = base.cut(hole).cut(cbore)
# Open the base wall around the two upper boss columns.  The clearance is swept
# straight up to the wall top, because the wedge is lowered vertically onto the
# tongue: a tilted pocket traps the tilted column and blocks assembly.
def swept_up(cyl, axis_mid, rise):
    """Exact volume swept by a tilted cylinder moving straight up by *rise*.

    For a convex solid the sweep is the solid plus a prism of every face that
    faces the direction of travel: the upper half of the lateral face (split
    on the silhouette plane) and the upper end disc.
    """
    V = A.Vector(0, 0, rise)
    w = A.Vector(-VV.x, 0.0, -VV.z)        # radial direction pointing up
    half_space = Part.makeBox(60.0, 60.0, 30.0, A.Vector(-30.0, -30.0, 0.0))
    half_space.Placement = A.Placement(axis_mid, A.Rotation(A.Vector(0, 0, 1), w))
    upper = cyl.common(half_space)
    out = cyl
    for f in upper.Faces:
        u0, u1, v0, v1 = f.ParameterRange
        n = f.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
        if n.dot(V) > 1e-6:
            out = out.fuse(f.extrude(V))
    return out.removeSplitter()

boss_slots = []
for u in (5.0, 44.5):
    h = BOSS_COLUMN_H + 0.4
    p0 = at(u, 5.75, W_BOSS - BOSS_COLUMN_H - 0.2)
    c = Part.makeCylinder(BOSS_OD / 2 + BOSS_BASE_CLEARANCE, h, p0, N)
    slot = swept_up(c, p0 + N * (h / 2), SLOT_RISE)
    boss_slots.append(slot)
    base = base.cut(slot)
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

# Boss columns have a full wall for the insert pocket and 3 mm of backing.
for u, v in HOLES:
    wedge = wedge.fuse(Part.makeCylinder(BOSS_OD / 2, BOSS_COLUMN_H,
                                         at(u, v, W_BOSS - BOSS_COLUMN_H), N))
# The high pair carries the longer lever arm. The web stays at X <= 16.5,
# clear of the removable base wall at X >= 17, and joins the wedge flange below
# Z82. Its upper edge bites into the boss while staying behind the board face.
high_pedestals = []
for u in (5.0, 44.5):
    v = 5.75
    face_center = at(u, v, W_BOSS)
    wall_side = WALL_X0 - 0.5
    pedestal_profile = [
        (face_center.x - 2.1, face_center.z - 2.4),
        (wall_side, face_center.z - 1.0),
        (wall_side, WALL_TOP - 4.0),
    ]
    pedestal = xz_prism(
        pedestal_profile,
        face_center.y - GUSSET_WIDTH / 2,
        face_center.y + GUSSET_WIDTH / 2)
    high_pedestals.append(pedestal)
    wedge = wedge.fuse(pedestal)
wedge = wedge.removeSplitter()
stage('wedge + boss pedestals', wedge)

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
for y, z, yaw in JOINT:
    D = joint_dir(yaw)
    wedge = wedge.cut(Part.makeCylinder(INS_BORE / 2, INS_DEPTH + 1.0,
                                        joint_point(y, z, yaw, WALL_X0) + D * 1.0, -D))
wedge = wedge.removeSplitter()
stage('wedge final', wedge)

# Cup relief is cut from the base only after the wedge is final: the wedge was
# trimmed against the tighter base above, so it cannot grow into the relief.
# Each relief is a larger cylinder clipped in Y to a smaller side clearance,
# swept straight up like the original slot so the wedge still drops on.
cup_reliefs = []
Y_AX = A.Vector(0, 1, 0)
for u, outward in ((5.0, -1.0), (44.5, 1.0)):
    rr = BOSS_OD / 2 + CUP_RELIEF_RADIAL
    h = BOSS_COLUMN_H + CUP_RELIEF_AXIAL + CUP_RELIEF_BACK
    p0 = at(u, 5.75, W_BOSS - BOSS_COLUMN_H - CUP_RELIEF_BACK)
    cyl = Part.makeCylinder(rr, h, p0, N)
    # Everything above the cylinder's lower half: the axis-plane rectangle
    # extruded straight up.  This is the exact vertical sweep of the cylinder
    # (bar the far ends, which lie outside the base), with no face filtering.
    rect = Part.Face(Part.makePolygon([p0 - Y_AX * rr, p0 + Y_AX * rr,
                                       p0 + N * h + Y_AX * rr, p0 + N * h - Y_AX * rr,
                                       p0 - Y_AX * rr]))
    relief = cyl.fuse(rect.extrude(A.Vector(0, 0, 30.0)))
    yc = ORG.y + u
    half_y = BOSS_OD / 2 + CUP_RELIEF_SIDE
    y_in = yc - outward * half_y
    y_far = yc + outward * 20.0
    relief = relief.common(Part.makeBox(80.0, abs(y_far - y_in), 60.0,
                                        A.Vector(-20.0, min(y_in, y_far), RELIEF_FLOOR_Z)))
    # Past the cup's outer edge the wall end drops to the floor, taking the fin.
    y_edge = yc + outward * BOSS_OD / 2
    relief = relief.fuse(Part.makeBox(WALL_X1 - WALL_X0 + 2.0, abs(y_far - y_edge), 60.0,
                                      A.Vector(WALL_X0 - 1.0, min(y_edge, y_far),
                                               RELIEF_FLOOR_Z)))
    relief = relief.removeSplitter()
    cup_reliefs.append(relief)
    base = base.cut(relief)
base = base.removeSplitter()
boss_slots = cup_reliefs
stage('base with cup relief', base)

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
rep['checks']['boss_wall_fraction_by_depth'] = {}
for u, v in HOLES:
    b0 = at(u, v, W_BOSS - 3.0)
    ring = Part.makeCylinder(9.0, 3.0, b0, N).cut(
        Part.makeCylinder(4.5, 4.0, at(u, v, W_BOSS - 3.5), N))
    rep['checks']['boss_support_mm3']['u%.0f_v%.0f' % (u, v)] = round(hit(ring, wedge), 1)
    fractions = {}
    for depth in (0.2, 2.0, 4.0, 6.0, 8.0):
        ring_slice = Part.makeCylinder(
            BOSS_OD / 2, 0.2, at(u, v, W_BOSS - depth - 0.1), N).cut(
                Part.makeCylinder(BOSS_BORE / 2, 0.4,
                                  at(u, v, W_BOSS - depth - 0.2), N))
        fractions[str(depth)] = round(hit(ring_slice, wedge) / ring_slice.Volume, 3)
    rep['checks']['boss_wall_fraction_by_depth']['u%.0f_v%.0f' % (u, v)] = fractions

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
for y, z, yaw in JOINT:
    D = joint_dir(yaw)
    p0 = joint_point(y, z, yaw, WALL_X0)
    wall = 0.0
    for i in range(0, 60):
        if hit(Part.makeCylinder(3.0, 0.25, p0 - D * (0.25 * i), -D), wedge) > 0.05:
            wall += 0.25
    rep['checks']['insert_room']['Y%.0f_Z%.0f' % (y, z)] = round(wall, 2)
rep['checks']['counterbore_depth_mm'] = CBORE_DEPTH
rep['checks']['high_pedestal_base_overlap_mm3'] = round(
    sum(hit(pedestal, base) for pedestal in high_pedestals), 3)
rep['checks']['high_pedestal_retained_mm3'] = [
    round(hit(pedestal, wedge), 1) for pedestal in high_pedestals]
# Measured on the solids: thinnest web between any joint screw cut and a boss slot.
rep['checks']['joint_to_boss_slot_web_mm'] = {
    'Y%.1f_Z%.0f' % (y, z): round(min(jc.distToShape(s)[0] for s in boss_slots), 2)
    for (y, z, _), jc in zip(JOINT, joint_cuts)}
upper_webs = [w for (y, z, _), w in zip(JOINT, rep['checks']['joint_to_boss_slot_web_mm'].values())
              if z > 70.0]
lower_webs = [w for (y, z, _), w in zip(JOINT, rep['checks']['joint_to_boss_slot_web_mm'].values())
              if z <= 70.0]
rep['checks']['joint_webs_ok'] = (min(upper_webs) >= MIN_SIDE_WEB - 0.01 and
                                  min(lower_webs) >= LOWER_CBORE_WEB - 0.01)
rep['checks']['joint_yaw_deg'] = {'Y%.1f_Z%.0f' % (y, z): yaw for y, z, yaw in JOINT}
rep['checks']['wedge_vs_printed_diff_mm3'] = round(
    wedge.cut(PRINTED_WEDGE).Volume + PRINTED_WEDGE.cut(wedge).Volume, 4)
rep['checks']['wedge_matches_printed'] = rep['checks']['wedge_vs_printed_diff_mm3'] < 0.01

# Seated cup clearance: how far each upper cup can move before touching the base.
def cup_travel(cup, vec):
    for i in range(1, 81):
        s = cup.copy()
        s.translate(vec * (0.05 * i))
        if hit(s, base) > 0.01:
            return round(0.05 * i, 2)
    return 4.0
rep['checks']['cup_clearance_mm'] = {}
for u in (5.0, 44.5):
    cup = wedge.common(Part.makeCylinder(BOSS_OD / 2, BOSS_COLUMN_H,
                                         at(u, 5.75, W_BOSS - BOSS_COLUMN_H), N))
    rep['checks']['cup_clearance_mm']['Y%.1f' % (ORG.y + u)] = {
        name: cup_travel(cup, vec) for name, vec in [
            ('down', A.Vector(0, 0, -1)), ('inboard', A.Vector(1, 0, 0)),
            ('axial', A.Vector(-N.x, 0, -N.z)),
            ('+Y', A.Vector(0, 1, 0)), ('-Y', A.Vector(0, -1, 0))]}
rep['checks']['min_cup_clearance_mm'] = min(
    v for row in rep['checks']['cup_clearance_mm'].values() for v in row.values())

# ---- assembly and service paths -------------------------------------------
# Obstacles: the robot as modelled in the master (including the head candidate
# above the mast) plus the mirrored right-hand mount.  Stale DrvV5_* copies in
# the master are deliberately excluded.
OBST_NAMES = ['UpperDeck', 'SideRailLeft', 'SideRailRight', 'ChassisDeck', 'BatteryBox',
              'MastTube', 'MastBase', 'PowerShield', 'AntennaPost', 'S3Board', 'Breadboard',
              'Neck_Main', 'Neck_Clamp_Cap', 'Pan_Rotor', 'Pan_Retainer_Crank',
              'Pan_Parallel_Link', 'Pan_Horn_Adapter', 'Tilt_Yoke', 'GH44_Tilt_Receiver',
              'Pan_Bearing_Lower', 'Pan_Bearing_Upper', 'Pan_Inner_Spacer',
              'Pan_Circlip_Envelope', 'SG90_Pan_Reference', 'Pan_Horn_Reference',
              'SG90_Tilt_Reference', 'Tilt_Horn_Reference', 'GH44_Fixed_Head_Adapter']
MIRROR = A.Matrix(-1, 0, 0, 79.0, 0, 1, 0, 0, 0, 0, 1, 0)
def mirrored(sh):
    s = sh.copy()
    s.transformShape(MIRROR)
    return s
robot = [(nm, d.getObject(nm).Shape) for nm in OBST_NAMES
         if d.getObject(nm) and not d.getObject(nm).Shape.isNull()]
right_mount = [('Base_Right', mirrored(base)), ('Wedge_Right', mirrored(wedge)),
               ('Board_Right', mirrored(board)), ('Fins_Right', mirrored(fins))]
rep['checks']['service_obstacles'] = [nm for nm, _ in robot] + [nm for nm, _ in right_mount]

def blockers(sh, obstacles):
    return {nm: round(hit(sh, o), 2) for nm, o in obstacles if hit(sh, o) > 0.01}

def moved(sh, v):
    s = sh.copy()
    s.translate(v)
    return s

# 1. The wedge must drop straight onto the base (tongue, locator, boss slots).
lift = {}
for i in range(1, int((ASSEMBLY_LIFT + SLOT_RISE) / 0.5) + 1):
    dz = 0.5 * i
    lift[str(dz)] = round(hit(moved(wedge, A.Vector(0, 0, dz)), base), 3)
rep['checks']['assembly_lift_overlap_mm3'] = lift
rep['checks']['assembly_lift_clear'] = max(lift.values()) < 0.001

# 2. Every joint screw reachable with the robot fully assembled.
access = {}
for y, z, yaw in JOINT:
    D = joint_dir(yaw)
    run = None
    for i in range(1, 81):
        L = 0.5 * i
        if blockers(Part.makeCylinder(3.0, L, A.Vector(WALL_X1, y, z), D),
                    robot + right_mount):
            run = L
            break
    access['Y%.1f_Z%.0f' % (y, z)] = run if run else 40.0
rep['checks']['joint_driver_free_run_mm'] = access

# 3. Wedge (with board and heatsink attached) comes off: up off the tongue,
#    then out along the board normal, clear of the robot and the base.
unit = wedge.fuse(board).fuse(fins)
path = {}
for i in range(1, 13):
    v = A.Vector(0, 0, 0.5 * i)
    path['up %.1f' % (0.5 * i)] = blockers(moved(unit, v), robot + right_mount + [('base', base)])
for i in range(1, 9):
    v = A.Vector(0, 0, 6.0) + N * (5.0 * i)
    path['up 6 + out %.0f' % (5.0 * i)] = blockers(moved(unit, v), robot + right_mount + [('base', base)])
rep['checks']['wedge_removal_path'] = {k: v for k, v in path.items() if v}
rep['checks']['wedge_removal_clear'] = not any(path.values())

# 4. With the wedge off: deck screws reachable from above and base lifts out.
deck_run = {}
for x, y in SCREWS:
    run = None
    for i in range(1, 121):
        L = 0.5 * i
        if blockers(Part.makeCylinder(3.0, L, A.Vector(x, y, FOOT_TOP), A.Vector(0, 0, 1)),
                    robot + right_mount):
            run = L
            break
    deck_run['Y%.0f' % y] = run if run else 60.0
rep['checks']['deck_screw_driver_free_run_mm'] = deck_run
base_path = {}
for i in range(1, 25):
    v = A.Vector(0, 0, 0.5 * i)
    base_path['up %.1f' % (0.5 * i)] = blockers(moved(base, v), robot + right_mount)
rep['checks']['base_removal_path'] = {k: v for k, v in base_path.items() if v}
rep['checks']['base_removal_clear'] = not any(base_path.values())
rep['checks']['high_boss_support'] = {
    'style': 'constant-diameter boss with planar triangular web',
    'pedestal_width_mm': GUSSET_WIDTH,
    'boss_diameter_mm': BOSS_OD,
    'insert_pocket_diameter_mm': BOSS_BORE,
    'insert_pocket_depth_mm': BOSS_DEPTH + 0.2,
    'solid_backing_mm': round(BOSS_COLUMN_H - (BOSS_DEPTH + 0.2), 2),
}
rep['checks']['upper_counterbore_wall_above_mm'] = round(
    WALL_TOP - (max(z for _, z, _ in JOINT) + CBORE_D / 2), 2)
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
        rep['checks']['high_pedestal_base_overlap_mm3'] < 0.001 and
        min(rep['checks']['high_pedestal_retained_mm3']) > 25.0 and
        rep['checks']['joint_webs_ok'] and
        rep['checks']['wedge_matches_printed'] and
        rep['checks']['min_cup_clearance_mm'] >= 0.6 and
        rep['checks']['assembly_lift_clear'] and
        rep['checks']['wedge_removal_clear'] and rep['checks']['base_removal_clear'] and
        min(rep['checks']['joint_driver_free_run_mm'].values()) >= 30.0 and
        all(min(fractions.values()) >= 0.99 for fractions in
            rep['checks']['boss_wall_fraction_by_depth'].values()) and
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
