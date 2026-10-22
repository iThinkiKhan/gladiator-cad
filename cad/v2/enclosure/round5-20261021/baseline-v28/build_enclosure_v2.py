"""Gladiator enclosure v2 (2026-10-13, Claude).

Run:  freecadcmd build_enclosure_v2.py      (headless; no GUI needed)

Reads the concept document's reference solids (current chassis/head/tray/INA/switch copied from the
masters by the 20261013 concept) READ-ONLY from a /tmp copy, builds the v2 panels from parameters and
writes everything into cad/v2/enclosure/v2-20261013/.  No existing CAD source is modified.

Frame: +Y front (mast), +X right, +Z up, origin rear-left of the aluminium deck (docs/ORIENTATION.md).
"""
import FreeCAD as A, Part, MeshPart, math, json, time, hashlib, shutil, traceback
from pathlib import Path

V = A.Vector
T0 = time.time()


def log(*a):
    print("[%6.1fs]" % (time.time() - T0), *a, flush=True)


R = Path('/home/buralien/projects/gladiator-cad')
O = R / 'cad/v2/enclosure/v2-20261013'
O.mkdir(parents=True, exist_ok=True)
SRC = R / 'cad/enclosure/concept-20261013/Gladiator_Enclosure_Concept.FCStd'
W = Path('/tmp/encv2')
W.mkdir(exist_ok=True)
shutil.copy(SRC, W / 'concept.FCStd')

# ----------------------------------------------------------------------------- parameters
ROOF_DZ = 3.9        # v2.8: hood roof raised 3.9 mm behind the step (outer Z111.9, inside 55.0 mm above the deck underside)
ROOF_TOP = 108.0 + ROOF_DZ
STEP_Y = (57.0, 57.0 + ROOF_DZ)   # 45 degree step from the raised roof down to the old one, ahead of the roof lap (tabs start at Y65)
P = dict(
    wall=2.4,            # nominal wall (normal to the surface)
    skin=1.1,            # each half of the shiplap seam
    skin_gap=0.2,        # clearance between the two halves of the shiplap
    z_bottom=14.0,       # skirt lower edge; track top is about Z7
    rear_cham=6.0, front_cham=5.0,
    seam_hood=78.0,      # hood ends here (flanks are a plain 0.6 butt seam: a lap on the flare locks the panels)
    seam_front=78.6,     # front panels start here
    split_x=39.5, split_gap=0.6,
    # INA pod: the rear step that lets the header wires breathe
    pod_x=(21.5, 57.5), pod_y_back=-48.0, pod_z_top=48.0, pod_z_cham=34.0,
    # SMA bulkhead. Hole O7.0 is the modelled value of the pylon that is already on the robot. Rule (Jim, 2026-10-14): nothing
    # recessed around the nut or the flange. Flat 2.0 mm land (<= 2.2 clamp limit), open flat zone of radius sma_clear on both
    # faces, stiffness from four diagonal spoke ribs that start outside that zone (straight-in access between them).
    sma_x=68.0, sma_z=84.5, sma_hole=7.0, sma_web=2.0, sma_clear=11.0, spoke_t=3.0, spoke_len=19.0, spoke_h=5.4,
    # status-light window over the S3 (LED position is NOT known: ASSUMED, see README)
    led_x=21.0, led_y=14.0, win=(7.0, 37.0, 6.0, 22.0), rab=(5.0, 39.0, 4.0, 24.0),
    # power switch (holder v1b: knob X54.2-58.2, Z27-33, front tip Y140)
    # Switch (2026-10-15, Jim): a separate enclosure (cad/v2/switch-enclosure/v1-20261015) bolts to a shelf in the hood (shell on) or to the right rail shelf (shell off).
    box_x=71.0, box_floor_z=30.5, box_y_front=-30.0, box_insert_y=(-18.0, -9.0),
    # seam screws: vertical M3 through the roof lap into heat-set inserts in hood bosses
    screws=[(22.0, 72.0), (33.0, 72.0), (50.0, 72.0), (66.0, 72.0)],
    tab_x=[(-1.5, 37.0), (42.0, 80.5)], tab_y0=65.0,
    ins_bore=4.6, ins_depth=7.5, m3_clear=3.6,
    # v2.7 speaker (Jim 2026-10-20/21: box 28 wide x 31 high x 15 deep, ears tip to tip 44, ear holes 36.5 apart, ears 2.8 thick CENTRED between the front and rear faces, M2 screws)
    # under the roof, firing up through a grille, over the breadboard (right of centre): ears along Y, the 31 'height' along X, leads leave the OUTBOARD (+X) end and drop down beside the hood wall to the deck (the S3 stands 2.9 mm from the speaker on the inboard side)
    spk=dict(cx=64.0, cy=2.0, w=28.0, h=31.0, d=15.0, ear_tip=44.0, hole_c=36.5, ear_t=2.8, ear_mid=7.5, ear_w=10.0, pad_d=7.0, pad_h=3.5, pilot_d=1.6, pilot_depth=4.5,
             fence_t=1.6, fence_h=6.0, clr=0.3, grille_r=10.5, grille_hole=2.4, grille_pitch=3.6, lead_notch=8.0),
    # v2.7 rail-foot saddle: caps the right rail's foot shelf (CAD X61..77, Y-22..6.5, top Z12) and straddles its sides, 0.3 clear; no bolt (Jim: stabilise, bolt not every time)
    saddle=dict(x=(59.5, 81.5), y=(-21.5, -4.0), z_low=9.0, clr=0.3, lead_in=2.0),
)

# ----------------------------------------------------------------------------- reference solids
cd = A.openDocument(str(W / 'concept.FCStd'))
REF = {o.Name: o.Shape.copy() for o in cd.Objects
       if o.Name.startswith(('Ref_', 'Head_', 'Track_Approx', 'Wheel_Approx'))}
# arch rails v4 replace the old rails (cad/v2/rails/v4-20261015): the shell is an optional add-on bolted to their hard points
rd = A.openDocument(str(R / 'cad/v2/rails/v4-20261015/Gladiator_ArchRails_v4.FCStd'))
for rn in ('Ref_SideRailLeft', 'Ref_SideRailRight', 'Ref_PowerSwitchHolder_v1b', 'Ref_Switch_Body', 'Ref_Switch_Knob_travel', 'Ref_Switch_Pins'):
    REF.pop(rn, None)
# v2.5 (2026-10-16): the rails as INSTALLED, measured by Jim: pegs 58 mm (rear) / 60 mm (front) apart over their outer faces, rails 15 mm from the mast tube each side, splay 1 mm per side over 89 mm.
# Left rail = CAD rail moved 2.0 mm out and turned about the rear peg; right = mirror. (The CAD frame width was wrong.)
SPLAY = math.atan(1.0 / 89.0)


def real_rail(side, shp):
    q = Part.Shape()
    q.importBrepFromString(shp.exportBrepToString())
    if side == 'L':
        q.translate(V(-2.0, 0, 0))
        q.rotate(V(12.0, 23.85, 0), V(0, 0, 1), math.degrees(SPLAY))
    else:
        q.translate(V(2.0, 0, 0))
        q.rotate(V(67.0, 23.85, 0), V(0, 0, 1), -math.degrees(SPLAY))
    return q


def rail_face_x(side, y):
    """X of the rail's OUTER face (CAD: 9.5 left, 69.5 right) after the move, at height Y"""
    d_ = y - 23.85
    return (9.5 - 2.0) - SPLAY * d_ if side == 'L' else (69.5 + 2.0) + SPLAY * d_


for rn in ('Ref_INA226Cassette', 'Ref_INA226BoardReference', 'Ref_INA226TerminalEnvelope', 'Ref_INA226HeaderEnvelope'):
    REF.pop(rn, None)
_ina = A.openDocument(str(R / 'cad/v2/ina-mount/v3-20261019/Gladiator_INA_Mount_v3.FCStd'))
REF['Ref_INA_Mount_v3'] = _ina.getObject('INA_Mount_v3').Shape.copy()
REF['Ref_INA226_v3_envelope'] = _ina.getObject('INA226_board_envelope').Shape.copy()
REF['Ref_ArchRail_Left_v4'] = real_rail('L', rd.getObject('Arch_Rail_Left_v4').Shape)
REF['Ref_ArchRail_Right_v4'] = real_rail('R', rd.getObject('Arch_Rail_Right_v4').Shape)
HARD = json.loads((R / 'cad/v2/rails/v4-20261015/hardpoints.json').read_text())['hardpoints']
# Real driver mounts carry 20 mm standoffs (Jim, 2026-10-15); the CAD wedge/board model was built with 15 mm (build_drv_v5.py STANDOFF = 15, provisional).
# The board and heatsink therefore sit 5 mm further out along the 45 degree board normal. The wedge/base (the printed mount) does not move.
STANDOFF_SHIFT = 20.0 - 15.0
for side_, sx_ in (('L', -1), ('R', 1)):
    n_ = V(sx_, 0, 1)
    n_.normalize()
    for part_ in ('Fins', 'Board'):
        k_ = 'Ref_DrvV5_%s_%s' % (part_, side_)
        sh_ = REF[k_].copy()
        sh_.translate(n_ * STANDOFF_SHIFT)
        REF[k_] = sh_
# upper deck v3 (rails seat + one retention screw per rail; cad/v2/upper-deck/v3-20261015)
REF['Ref_UpperDeck'] = A.openDocument(str(R / 'cad/v2/upper-deck/v4-20261016/Gladiator_UpperDeck_v4.FCStd')).getObject('UpperDeck_v4').Shape.copy()
log("refs", len(REF))


# ----------------------------------------------------------------------------- 2D helpers
def area(pts):
    return 0.5 * sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                     for i in range(len(pts)))


def offset_poly(pts, t):
    """Inward offset of a simple polygon by t (line-intersection join)."""
    n = len(pts)
    sgn = 1 if area(pts) > 0 else -1
    L = []
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        dx, dz = q[0] - p[0], q[1] - p[1]
        l = math.hypot(dx, dz)
        nx, nz = -dz / l * sgn, dx / l * sgn
        L.append(((p[0] + nx * t, p[1] + nz * t), (dx, dz)))
    out = []
    for i in range(n):
        a, da = L[i - 1]
        b, db = L[i]
        det = da[0] * db[1] - da[1] * db[0]
        if abs(det) < 1e-9:
            out.append(b)
            continue
        s = ((b[0] - a[0]) * db[1] - (b[1] - a[1]) * db[0]) / det
        out.append((a[0] + da[0] * s, a[1] + da[1] * s))
    return out


def rect_xy_wire(z, x0, x1, y0, y1):
    vs = [V(x0, y0, z), V(x1, y0, z), V(x1, y1, z), V(x0, y1, z)]
    return Part.makePolygon(vs + [vs[0]])


def roof_hole_chamfer(x, y, d, c=0.7, z_top=108.0):
    """cone that widens a round through hole toward the outer roof face (Z108, or Z106.7 inside the tab recess), which prints on the glass bed"""
    return Part.makeCone(d / 2, d / 2 + c, c, V(x, y, z_top - c), V(0, 0, 1))


def roof_rect_chamfer(x0, x1, y0, y1, c=0.6):
    return Part.makeLoft([rect_xy_wire(ROOF_TOP - c, x0, x1, y0, y1), rect_xy_wire(ROOF_TOP, x0 - c, x1 + c, y0 - c, y1 + c)], True, True)


def wire_xz(y, pts):
    vs = [V(x, y, z) for x, z in pts]
    return Part.makePolygon(vs + [vs[0]])


def prism_yz(pts, x0, x1):
    vs = [V(x0, y, z) for y, z in pts]
    f = Part.Face(Part.makePolygon(vs + [vs[0]]))
    return f.extrude(V(x1 - x0, 0, 0))


def prism_xz(pts, y0, y1):
    vs = [V(x, y0, z) for x, z in pts]
    f = Part.Face(Part.makePolygon(vs + [vs[0]]))
    return f.extrude(V(0, y1 - y0, 0))


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cylz(x, y, z0, z1, d):
    return Part.makeCylinder(d / 2.0, z1 - z0, V(x, y, z0))


def cyly(x, z, y0, y1, d):
    return Part.makeCylinder(d / 2.0, y1 - y0, V(x, y0, z), V(0, 1, 0))


def plain(s):
    """Round-trip through BREP: drops FreeCAD 1.0 element maps, which crash some later booleans."""
    p = Part.Shape()
    p.importBrepFromString(s.exportBrepToString())
    return p


def fuse(*s):
    r = plain(s[0])
    for x in s[1:]:
        r = plain(r.fuse(plain(x)))
    return plain(r.removeSplitter())


def cut(a, *s):
    a = plain(a)
    for x in s:
        a = plain(a.cut(plain(x)))
    return plain(a.removeSplitter())


def com(a, b):
    return plain(plain(a).common(plain(b)).removeSplitter())


# ----------------------------------------------------------------------------- body sections
N = [(-9, 0), (88, 0), (88, 28), (88, 50), (88, 96), (82, 108), (-3, 108), (-9, 96), (-9, 50), (-9, 28)]
NH = [(-9, 0), (88, 0), (88, 28), (88, 50), (88, 96 + ROOF_DZ), (82, ROOF_TOP), (-3, ROOF_TOP), (-9, 96 + ROOF_DZ), (-9, 50), (-9, 28)]   # v2.8 raised hood section
SH = 4.0       # shoulders widened 4 mm: the boards moved 5 mm out with the 20 mm standoffs
B = [(-9, 0), (88, 0), (88, 28), (116 + SH, 50), (116 + SH, 96), (82, 108), (-3, 108), (-37 - SH, 96), (-37 - SH, 50), (-9, 28)]
K45 = math.tan(math.radians(22.5))
CH, CF, WALL = P['rear_cham'], P['front_cham'], P['wall']
POD_OUT = [(-24, 0), (P['pod_y_back'], 0), (P['pod_y_back'], P['pod_z_cham']),
           (P['pod_y_back'] + (P['pod_z_top'] - P['pod_z_cham']), P['pod_z_top']), (-24, P['pod_z_top'])]
POD_BASE_IN = [(-6, 0), (P['pod_y_back'], 0), (P['pod_y_back'], P['pod_z_cham']),
               (P['pod_y_back'] + (P['pod_z_top'] - P['pod_z_cham']), P['pod_z_top']), (-6, P['pod_z_top'])]


def main_body(d):
    """d = 0: outer skin. d > 0: the surface offset inward by d (45 degree chamfers handled exactly)."""
    if d == 0:
        st = [(-32, NH, CH), (-26, NH, 0), (STEP_Y[0], NH, 0), (STEP_Y[1], N, 0), (72, N, 0), (90, B, 0), (143, B, 0), (148, B, CF)]
    else:
        st = [(-32 + d, NH, CH + K45 * d), (-32 + CH + K45 * d, NH, d), (STEP_Y[0] + K45 * d, NH, d), (STEP_Y[1] + K45 * d, N, d), (72, N, d), (90, B, d),
              (148 - CF - K45 * d, B, d), (148 - d, B, CF + K45 * d)]
    wires = [wire_xz(y, offset_poly(p, s) if s else p) for y, p, s in st]
    return Part.makeLoft(wires, True, True)


def pod_body(d):
    x0, x1 = P['pod_x']
    if d == 0:
        return prism_yz(POD_OUT, x0, x1)
    return prism_yz(offset_poly(POD_BASE_IN, d), x0 + d, x1 - d)


def skin_solid(d):
    # v2.6/2.7 (Jim 2026-10-20): the rear INA pod is gone; the INA stands upright inside the body (cad/v2/ina-mount/v3-20261019)
    return main_body(d)


OUTER = skin_solid(0)
log("outer", OUTER.isValid(), OUTER.Volume)
IN_FULL = skin_solid(WALL)
M_OUT = skin_solid(P['skin'])                      # outer half skin  = OUTER - M_OUT
log("inners built")
BOTTOM = box(-80, 160, -80, 200, -50, P['z_bottom'])

# ----------------------------------------------------------------------------- shared cuts
AP = []
PULL = 30.0       # the aperture is the board's whole swept path along the panel's 45 degree pull (relative motion: the board moves back along -n), not just its outline


def sweep(shape, dirv, length=PULL, step=3.0):
    out = [shape]
    k = 1
    while k * step <= length:
        c = plain(shape)
        c.translate(dirv * (k * step))
        out.append(c)
        k += 1
    return fuse(*out)


for n in ('Ref_DrvV5_Fins_L', 'Ref_DrvV5_Fins_R', 'Ref_DrvV5_Board_L', 'Ref_DrvV5_Board_R'):
    off = REF[n].makeOffsetShape(4 if 'Fins' in n else 2, 0.05)
    back = V(1, 0, -1) if n.endswith('_L') else V(-1, 0, -1)       # -n: toward the inside and down
    back.normalize()
    AP.append(sweep(off, back))
    if 'Fins' in n:
        # v2.8 (Jim 2026-10-21): seen from the side, the shoulder top (Z90) hid the bottom 8 mm of each heatsink; the aperture also runs straight DOWN under the fins
        # (a 15 mm vertical sweep of the fin outline + 4 mm), which drops the shoulder edge to about Z75 where the fins are
        AP.append(sweep(off, V(0, 0, -1), length=15.0))
MAST = fuse(cylz(39.5, 113, -5, 160, 26), Part.makeCone(13.0, 13.7, 0.7, V(39.5, 113, 107.3), V(0, 0, 1)))
log("apertures")

WALLS = cut(OUTER, IN_FULL, BOTTOM, *AP, MAST)
OSKIN = cut(OUTER, M_OUT, BOTTOM, *AP, MAST)       # outer half skin
log("skins", WALLS.Volume, OSKIN.Volume)

BIG = 400


def ybox(y0, y1):
    return box(-BIG, BIG, y0, y1, -BIG, BIG)


# ----------------------------------------------------------------------------- HOOD
hood = com(WALLS, ybox(-BIG, P['seam_hood']))

# Fastening (Jim 2026-10-14/15): the shell is an OPTIONAL add-on bolted to hard points spread along the arch rails (cad/v2/rails/v4-20261015/hardpoints.json):
# the hood at the rear and middle pads (Y35.5, Y59), each front panel at the front pad (Y100.5), left and right = 6 points. Each point is a tapered boss
# (a fan: wide at the wall, narrower at the rail) reaching to 0.2 mm short of the rail face; M3 x 25 screws go in from the outside.
FXL, FXR = HARD[0]['face_x_left'], HARD[0]['face_x_right']
HOOD_HP = [(h['y'], h['z']) for h in HARD if h['owner'] == 'hood']
FRONT_HP = [(h['y'], h['z']) for h in HARD if h['owner'] == 'front']


def standoff(x_from, x_to, y, z, r_base, r_tip):
    L = abs(x_to - x_from)
    d = 1 if x_to > x_from else -1
    return Part.makeCone(r_base, r_tip, L, V(x_from, y, z), V(d, 0, 0))


feat = []
for (hy, hz) in HOOD_HP:
    feat.append(standoff(-7.6, rail_face_x('L', hy) - 0.2, hy, hz, 6.0, 4.0))
    feat.append(standoff(86.6, rail_face_x('R', hy) + 0.2, hy, hz, 6.0, 4.0))
# fans under the switch shelf: two triangular webs from the shelf down the rear wall
for (fx0, fx1) in ((P['box_x'] - 7.0, P['box_x'] - 4.0), (P['box_x'] + 4.0, P['box_x'] + 7.0)):
    feat.append(prism_yz([(-31.0, 14.5), (-31.0, P['box_floor_z'] - 10.0), (-12.0, P['box_floor_z'] - 10.0)], fx0, fx1))
feat.append(box(P['box_x'] - 9.5, P['box_x'] + 9.5, -31.0, P['box_insert_y'][0] + 6.0, P['box_floor_z'] - 10.0, P['box_floor_z']))   # shelf for the switch holder
# holder cradle (2026-10-16): two guides along the holder's sides locate it in X exactly (0.25 clearance each side); the window is cut from the same centre line, so the holder drops in ONE way and its flush face sits in the window
for sg_ in (-1, 1):
    x0_, x1_ = (P['box_x'] - 9.5, P['box_x'] - 7.5) if sg_ < 0 else (P['box_x'] + 7.5, P['box_x'] + 9.5)
    feat.append(box(x0_, x1_, -30.0, P['box_y_front'] + 19.0, P['box_floor_z'], P['box_floor_z'] + 7.0))
# v2.7 rail-foot saddle: a cap with cheeks over the right rail's foot shelf, hung from the switch shelf; lead-in at its front so it slides on with the hood
sd = P['saddle']
_shelf = box(61.0 - sd['clr'], 77.0 + sd['clr'], -22.0 - 5.0, 6.5 + 5.0, 2.0 - 5.0, 12.0 + sd['clr'])     # the shelf (CAD), grown by the clearance, open past both ends
_shelf = real_rail('R', _shelf)
SADDLE = cut(box(sd['x'][0], sd['x'][1], sd['y'][0], sd['y'][1], sd['z_low'], P['box_floor_z'] - 10.0 + 0.01), _shelf,
             prism_yz([(sd['y'][1] + 0.01, sd['z_low'] - 0.01), (sd['y'][1] + 0.01, 12.3 + sd['lead_in']), (sd['y'][1] - sd['lead_in'], 12.3), (sd['y'][1] - sd['lead_in'], sd['z_low'] - 0.01)],
                      sd['x'][0] - 1, sd['x'][1] + 1))
feat.append(SADDLE)
# v2.7 speaker cradle under the roof: two ear pads with M2 pilots, two end fences (the inboard one notched for the leads)
sp_ = P['spk']
ROOF_IN = ROOF_TOP - P['wall']
SPK_FRONT_Z = ROOF_IN - sp_['pad_h']
EAR_TOP_Z = SPK_FRONT_Z - (sp_['ear_mid'] - sp_['ear_t'] / 2)      # the ears sit 6.1..8.9 behind the cone face
EARS = [(sp_['cx'], sp_['cy'] - sp_['hole_c'] / 2), (sp_['cx'], sp_['cy'] + sp_['hole_c'] / 2)]
for (ex, ey) in EARS:
    feat.append(cylz(ex, ey, EAR_TOP_Z, ROOF_IN + 0.5, sp_['pad_d']))
hx_ = sp_['h'] / 2 + sp_['clr']
hy_ = sp_['w'] / 2 + sp_['clr']
for sgn in (-1, 1):
    x0_ = sp_['cx'] + sgn * hx_
    x1_ = x0_ + sgn * sp_['fence_t']
    fence = box(min(x0_, x1_), max(x0_, x1_), sp_['cy'] - hy_, sp_['cy'] + hy_, SPK_FRONT_Z - sp_['fence_h'], ROOF_IN + 0.5)
    if sgn > 0:
        fence = cut(fence, box(min(x0_, x1_) - 1, max(x0_, x1_) + 1, sp_['cy'] - sp_['lead_notch'] / 2, sp_['cy'] + sp_['lead_notch'] / 2, SPK_FRONT_Z - sp_['fence_h'] - 1, SPK_FRONT_Z - 2.0))
    feat.append(fence)
# SMA mount: four diagonal spoke ribs on the inside of the rear wall, starting at the clear radius (no ring, no pocket)
sx, sz = P['sma_x'], P['sma_z']
for ang in (45, 135, 225, 315):
    sp = box(P['sma_clear'], P['sma_clear'] + P['spoke_len'], -31.0, -29.6 + P['spoke_h'], -P['spoke_t'] / 2, P['spoke_t'] / 2)
    sp.rotate(V(0, 0, 0), V(0, 1, 0), ang)
    sp.translate(V(sx, 0, sz))
    feat.append(com(sp, IN_FULL))
# seam screw bosses under the roof lap
for (bx, by) in P['screws']:
    feat.append(cylz(bx, by, 95.6, 106.2, 9.0))
    feat.append(Part.makeCone(6.0, 4.5, 3.0, V(bx, by, 106.2), V(0, 0, -1)))        # fan where the boss meets the roof
hood = fuse(hood, *feat)

hole = []
for (hy, hz) in HOOD_HP:
    hole.append(Part.makeCylinder(P['m3_clear'] / 2, rail_face_x('L', hy) + 12.0, V(-12.0, hy, hz), V(1, 0, 0)))                # left screw path (through wall and boss)
    hole.append(Part.makeCylinder(P['m3_clear'] / 2, 92.0 - (rail_face_x('R', hy) - 3.0), V(rail_face_x('R', hy) - 3.0, hy, hz), V(1, 0, 0)))    # right screw path
# switch enclosure on a shelf inside the hood (shell on); with the shell off it bolts to the right rail's shelf instead (cad/v2/switch-enclosure/v1-20261015)
hole.append(box(P['box_x'] - 7.7, P['box_x'] + 7.7, -36, -29.0, P['box_floor_z'] - 0.3, P['box_floor_z'] + 17.9 + 0.3))   # holder window (holder v3: 14.5 wide, 0.75 mm of margin each side); the holder's 2.0 front wall sits 1.4 mm inside the outer face
for iy in P['box_insert_y'][:1]:
    hole.append(Part.makeCylinder(2.3, 9.1, V(P['box_x'], iy, P['box_floor_z'] - 8.1)))                        # M3 heat-set insert pocket in the shelf: opens toward the bed (roof-down print), so its closed end is a bridge; 0.6 mm extra depth (floor 1.9) so bridge sag cannot leave the insert proud
hole.append(cyly(sx, sz, -40, -20, P['sma_hole']))
# v2.7 speaker grille: hex pattern of holes over the cone, chamfered on the roof face (the hood prints roof-down), and the two M2 pilots
_gp = sp_['grille_pitch']
for i_ in range(-6, 7):
    for j_ in range(-6, 7):
        gx = sp_['cx'] + _gp * (i_ + (0.5 if j_ % 2 else 0.0))
        gy = sp_['cy'] + _gp * 0.866 * j_
        if math.hypot(gx - sp_['cx'], gy - sp_['cy']) <= sp_['grille_r']:
            hole.append(cylz(gx, gy, ROOF_IN - 1.0, ROOF_TOP + 2.0, sp_['grille_hole']))
            hole.append(roof_hole_chamfer(gx, gy, sp_['grille_hole'], 0.4, ROOF_TOP))
for (ex, ey) in EARS:
    hole.append(cylz(ex, ey, EAR_TOP_Z - 0.1, EAR_TOP_Z + sp_['pilot_depth'], sp_['pilot_d']))
hole.append(cyly(sx, sz, -32 + P['sma_web'], -20, 2 * P['sma_clear']))   # 0.4 mm spot-face inside: 2.0 land, flat and open
for k in range(3):                                    # rear vent louvers
    z0 = 88.0 + 4.8 * k
    hole.append(box(5, 47, -36, -28, z0, z0 + 2.4))
x0, x1, y0, y1 = P['win']
hole.append(box(x0, x1, y0, y1, 104 + ROOF_DZ, 110 + ROOF_DZ))             # status window
hole.append(roof_rect_chamfer(x0, x1, y0, y1))                 # window edge chamfered on the bed side
x0, x1, y0, y1 = P['rab']
hole.append(box(x0, x1, y0, y1, 105.0 + ROOF_DZ, 106.8 + ROOF_DZ))         # lens rabbet from inside
for (bx, by) in P['screws']:
    hole.append(cylz(bx, by, 94, 103.1 + 0.0, P['ins_bore']))          # insert pocket from below
    hole.append(cylz(bx, by, 103.0, 112, P['m3_clear']))               # screw clearance up through
    hole.append(roof_hole_chamfer(bx, by, P['m3_clear'], 0.7, 106.7))        # the hood roof is recessed to Z106.7 under the tabs
for k, (tx0, tx1) in enumerate(P['tab_x']):        # recess the hood roof; open to the OUTBOARD roof edge so the tab lifts out
    if k == 0:
        hole.append(box(-30, tx1 + 0.2, P['tab_y0'] - 0.2, P['seam_hood'] + 1.0, 106.7, 120))
    else:
        hole.append(box(tx0 - 0.2, 120, P['tab_y0'] - 0.2, P['seam_hood'] + 1.0, 106.7, 120))
hood = cut(hood, *hole)
log("hood", hood.isValid(), len(hood.Solids), hood.Volume)

# ----------------------------------------------------------------------------- FRONT (both halves)
front = com(WALLS, ybox(P['seam_front'], BIG))
for (tx0, tx1) in P['tab_x']:                       # roof lap tabs: outer half skin reaching back over the hood roof
    front = fuse(front, com(OSKIN, box(tx0, tx1, P['tab_y0'], P['seam_front'] + 0.2, -BIG, BIG)))
bore = [cylz(bx, by, 100, 112, P['m3_clear']) for (bx, by) in P['screws']]
bore += [roof_hole_chamfer(bx, by, P['m3_clear'], 0.7) for (bx, by) in P['screws']]
front_feat = []
for (hy, hz) in FRONT_HP:
    front_feat.append(com(standoff(-36.0, FXL - 0.2, hy, hz, 5.0, 4.0), OUTER))     # left panel boss, clipped to the outer skin
    front_feat.append(com(standoff(115.0, FXR + 0.2, hy, hz, 5.0, 4.0), OUTER))     # right panel boss
front = fuse(front, *front_feat)
for (hy, hz) in FRONT_HP:
    bore.append(Part.makeCylinder(P['m3_clear'] / 2, FXL + 3.0 + 36.0, V(-36.0, hy, hz), V(1, 0, 0)))
    bore.append(Part.makeCylinder(P['m3_clear'] / 2, 115.0 - (FXR - 3.0), V(FXR - 3.0, hy, hz), V(1, 0, 0)))
front = cut(front, *bore)
sx0 = P['split_x']
g = P['split_gap'] / 2
FL = com(front, box(-BIG, sx0 - g, -BIG, BIG, -BIG, BIG))
FR = com(front, box(sx0 + g, BIG, -BIG, BIG, -BIG, BIG))
log("front L/R", FL.isValid(), len(FL.Solids), FR.isValid(), len(FR.Solids))

# ----------------------------------------------------------------------------- lens plate with light-pipe tube
rx0, rx1, ry0, ry1 = P['rab']
plate = box(rx0 + 0.2, rx1 - 0.2, ry0 + 0.2, ry1 - 0.2, 105.6 + ROOF_DZ, 106.7 + ROOF_DZ)
tube = cylz(P['led_x'], P['led_y'], 94.0 + ROOF_DZ, 106.0 + ROOF_DZ, 8.0)
lens = fuse(plate, tube)
lens = cut(lens, cylz(P['led_x'], P['led_y'], 93.0 + ROOF_DZ, 106.2 + ROOF_DZ, 5.2))
log("lens", lens.isValid(), lens.Volume)

PARTS = {'Rear_Hood': hood, 'Front_Left': FL, 'Front_Right': FR, 'Lens_Plate': lens}

# ----------------------------------------------------------------------------- validation
CHK = {'status': 'v2 REVIEW MODEL - NOT PRINT RELEASED (STLs are for review/slicing; Jim starts prints)',
       'parameters': {k: (list(v) if isinstance(v, tuple) else v) for k, v in P.items()},
       'parts': {}, 'collisions': [], 'min_distance': {}, 'thin_feature_probe': {}}
for name, s in PARTS.items():
    bb = s.BoundBox
    CHK['parts'][name] = dict(valid=s.isValid(), solids=len(s.Solids), volume_mm3=round(s.Volume, 1),
                              bbox=[round(v, 1) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)])
refs_static = {k: v for k, v in REF.items() if not k.startswith(('Track_Approx', 'Wheel_Approx'))}
for name, s in PARTS.items():
    rows = []
    for rn, rs in refs_static.items():
        if not s.BoundBox.intersect(rs.BoundBox):
            gap = max(rs.BoundBox.XMin - s.BoundBox.XMax, s.BoundBox.XMin - rs.BoundBox.XMax,
                      rs.BoundBox.YMin - s.BoundBox.YMax, s.BoundBox.YMin - rs.BoundBox.YMax,
                      rs.BoundBox.ZMin - s.BoundBox.ZMax, s.BoundBox.ZMin - rs.BoundBox.ZMax)
            if gap > 25:
                continue
        else:
            try:
                v = plain(s).common(plain(rs)).Volume
            except Exception as e:                      # boolean failed: fall back to distance and say so
                dd = s.distToShape(rs)[0]
                CHK.setdefault('boolean_failures', []).append(dict(part=name, ref=rn, distance_mm=round(dd, 3)))
                log("BOOLEAN FAILED", name, rn, "distance", round(dd, 3))
                if dd > 0.01:
                    rows.append((dd, rn))
                else:
                    CHK['collisions'].append(dict(part=name, ref=rn, volume_mm3='boolean failed; distance %.3f' % dd))
                continue
            if v > 0.01:
                CHK['collisions'].append(dict(part=name, ref=rn, volume_mm3=round(v, 3)))
                continue
        rows.append((s.distToShape(rs)[0], rn))
    rows.sort()
    CHK['min_distance'][name] = [(round(d, 2), n) for d, n in rows[:8]]
    log(name, "min gaps", CHK['min_distance'][name][:4], "collisions so far", len(CHK['collisions']))
# tracks vs skirt (static)
for name in ('Rear_Hood', 'Front_Left', 'Front_Right'):
    d = min(PARTS[name].distToShape(v)[0] for k, v in REF.items() if k.startswith('Track_Approx'))
    CHK['min_distance'][name + '_to_track'] = round(d, 2)
# thin-feature probe: erode by 0.4 and count pieces (more than one = a web thinner than 0.8)
for name in ('Rear_Hood', 'Front_Left', 'Front_Right'):
    try:
        er = PARTS[name].makeOffsetShape(-0.4, 0.01)
        CHK['thin_feature_probe'][name] = dict(solids_after_0p4_erosion=len(er.Solids), volume_ratio=round(er.Volume / PARTS[name].Volume, 3))
    except Exception as e:
        CHK['thin_feature_probe'][name] = 'erosion failed: %s' % e
log("thin probe", CHK['thin_feature_probe'])

# ----------------------------------------------------------------------------- switch enclosure placed on the hood shelf (fit check, and shown in the model)
SWBOX = {}
try:
    sb = A.openDocument(str(R / 'cad/v2/switch-enclosure/v3-20261016/Gladiator_SwitchHolder_v3.FCStd'))
    CHK['switch_enclosure_on_hood'] = {}
    for nm in ('Switch_Holder_v3',):
        c = plain(sb.getObject(nm).Shape)
        c.translate(V(P['box_x'], P['box_y_front'], P['box_floor_z']))
        SWBOX['Hood_' + nm] = c
        try:
            ov = round(plain(hood).common(c).Volume, 3)
        except Exception:
            ov = None
        others = []
        for rn, rs in refs_static.items():
            if c.BoundBox.intersect(rs.BoundBox):
                try:
                    v = plain(c).common(plain(rs)).Volume
                except Exception:
                    v = None
                if v is None or v > 0.01:
                    others.append((rn, v))
        CHK['switch_enclosure_on_hood'][nm] = dict(overlap_with_hood_mm3=ov, overlaps_with_other_references=others or 'none',
                                                   gap_to_hood_mm=round(plain(hood).distToShape(c)[0], 2))
    log("switch enclosure on hood", CHK['switch_enclosure_on_hood'])
except Exception:
    traceback.print_exc()

# v2.7 speaker envelope (box + ears + a lead stub) vs everything static, and vs the hood itself
try:
    hz_ = SPK_FRONT_Z
    spk_env = fuse(box(sp_['cx'] - sp_['h'] / 2, sp_['cx'] + sp_['h'] / 2, sp_['cy'] - sp_['w'] / 2, sp_['cy'] + sp_['w'] / 2, hz_ - sp_['d'], hz_),
                   box(sp_['cx'] - sp_['ear_w'] / 2, sp_['cx'] + sp_['ear_w'] / 2, sp_['cy'] - sp_['ear_tip'] / 2, sp_['cy'] + sp_['ear_tip'] / 2, hz_ - (sp_['ear_mid'] + sp_['ear_t'] / 2), hz_ - (sp_['ear_mid'] - sp_['ear_t'] / 2)),
                   box(sp_['cx'] + sp_['h'] / 2, sp_['cx'] + sp_['h'] / 2 + 4.0, sp_['cy'] - 2.5, sp_['cy'] + 2.5, hz_ - sp_['d'], hz_ - sp_['d'] + 5.0))
    for (ex, ey) in EARS:
        spk_env = cut(spk_env, cylz(ex, ey, hz_ - 5, hz_ + 1, 2.2))
    SWBOX['Hood_Speaker_envelope'] = spk_env
    res_ = {rn: round(plain(spk_env).common(plain(rs)).Volume, 3) for rn, rs in refs_static.items() if spk_env.BoundBox.intersect(rs.BoundBox)}
    CHK['speaker'] = dict(front_z=round(hz_, 2), centre=(sp_['cx'], sp_['cy']), overlap_with_hood_mm3=round(plain(hood).common(spk_env).Volume, 3),
                          overlaps_with_references={k: v for k, v in res_.items() if v > 0.01} or 'none',
                          nearest=sorted([(round(spk_env.distToShape(rs)[0], 2), rn) for rn, rs in refs_static.items() if spk_env.distToShape(rs)[0] < 12])[:5],
                          grille_holes=sum(1 for i_ in range(-6, 7) for j_ in range(-6, 7) if math.hypot(_gp * (i_ + (0.5 if j_ % 2 else 0.0)), _gp * 0.866 * j_) <= sp_['grille_r']))
    log("speaker", CHK['speaker'])
except Exception:
    traceback.print_exc()
try:
    rr_ = REF['Ref_ArchRail_Right_v4']
    CHK['saddle'] = dict(overlap_with_rail_mm3=round(plain(SADDLE).common(plain(rr_)).Volume, 3), gap_to_rail_mm=round(SADDLE.distToShape(rr_)[0], 2),
                         drop_to_contact_mm=next((round(0.05 * k, 2) for k in range(1, 40) if plain(SADDLE).translated(V(0, 0, -0.05 * k)).common(rr_).Volume > 0.01), None),
                         side_play_mm=next((round(0.05 * k, 2) for k in range(1, 40) if plain(SADDLE).translated(V(0.05 * k, 0, 0)).common(rr_).Volume > 0.01), None))
    log("saddle", CHK['saddle'])
except Exception:
    traceback.print_exc()
try:
    CHK['deck_shift_check'] = {}
    for dx in (-2.0, 2.0):
        dk = plain(REF['Ref_UpperDeck'])
        dk.translate(V(dx, 0, 0))
        CHK['deck_shift_check']['deck_x%+.0f' % dx] = {n: dict(overlap_mm3=round(plain(sp).common(dk).Volume, 3), gap_mm=round(sp.distToShape(dk)[0], 2)) for n, sp in PARTS.items()}
    log("deck shift", CHK['deck_shift_check'])
except Exception:
    traceback.print_exc()

# ----------------------------------------------------------------------------- save
d = A.newDocument('Gladiator_Enclosure_v2')
for name, s in PARTS.items():
    o = d.addObject('Part::Feature', name)
    o.Shape = s
for rn, rs in REF.items():
    o = d.addObject('Part::Feature', rn)
    o.Shape = rs
for rn, rs in SWBOX.items():
    o = d.addObject('Part::Feature', rn)
    o.Shape = rs
d.Comment = 'v2 review model. Reference solids are copied from the 20261013 concept document (itself from the masters); panels are generated by build_enclosure_v2.py.'
d.recompute()
d.saveAs(str(O / 'Gladiator_Enclosure_v2.FCStd'))
Part.export([d.getObject(n) for n in PARTS], str(O / 'Gladiator_Enclosure_v2_Panels.step'))

# STL in print orientation: shells roof-down, lens plate face-down
STL = {}
for name, s in PARTS.items():
    c = s.copy()
    c.rotate(V(0, 0, 0), V(1, 0, 0), 90 if name == 'Switch_Bezel' else 180)
    c.translate(V(0, 0, -c.BoundBox.ZMin))
    c.translate(V(-c.BoundBox.XMin, -c.BoundBox.YMin, 0))
    m = MeshPart.meshFromShape(Shape=c, LinearDeflection=0.03, AngularDeflection=math.radians(10))
    path = O / ('Gladiator_Enclosure_v2_%s.stl' % name)
    m.write(str(path))
    bb = c.BoundBox
    STL[name] = dict(file=path.name, triangles=m.CountFacets, is_solid=m.isSolid(),
                     non_manifold=m.hasNonManifolds(),
                     size_mm=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
                     bed_fit_220x220x250=bool(bb.XLength < 218 and bb.YLength < 218 and bb.ZLength < 248))
CHK['stl'] = STL
log("stl", STL)
CHK['source_sha256'] = {'concept/Gladiator_Enclosure_Concept.FCStd': hashlib.sha256((W / 'concept.FCStd').read_bytes()).hexdigest()}
(O / 'validation.json').write_text(json.dumps(CHK, indent=2))
log("done")
import os
os._exit(0)
