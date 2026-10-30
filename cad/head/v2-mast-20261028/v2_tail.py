
# ====================================================================================================
# v2 section. Everything above is the v05 generator with the "v2" patches. Local frame as v05:
# mast axis at the origin, tube top drawn at Z 120; world = local + (39.5, 113, LIFT=50).
# ====================================================================================================
import time
t_start = time.time()
V = A.Vector
report['release'] = 'MASTHEAD v2 DRAFT 2026-10-28: CAD and checks only; nothing printed or sliced'
R2 = report.setdefault('v2', {})
R2['changes'] = {
    'mast': 'tube 20 mm taller (Z 6..150; +40 until Jim raised tipping 2026-10-29); 7 mm lay-in wire slot on the -Y (rear) side Z 22..162; the v1 wire window opened',
    'lock': 'one-piece 37 mm collar, tested key on the flat, ONE M3 through-bolt + wingnut across X through collar and tube',
    'belt': 'carriage travel 38..48 (v1 37..40.4; Jim dremeled v1 to the screw holes) + M3 x16 push-screw tensioner',
    'horns': 'horn pockets 2.2 deep (v1 1.2): the 2.0 arm is fully buried (pan pulley and tilt receiver)',
    'balance': 'yoke + whole tilting head 26 mm rearward: tilt pivot directly over the mast axis',
    'tilt_stop': 'yoke 10 mm taller (same floor) ear plate (12.2 x 6) and pivot tower (10 x 6) narrowed to columns below the servo',
}
R2['params'] = {'LIFT': LIFT, 'C_MIN': C_MIN, 'C_MAX': C_MAX, 'C_NOM': C_NOM, 'POCKET_DEPTH': POCKET_DEPTH,
                'TOP_PLATE_Z': TOP_PLATE_Z, 'YOKE_DY': YOKE_DY, 'YOKE_H': YOKE_H, 'COLLAR_Z0': COLLAR_Z0, 'COLLAR_H': COLLAR_H,
                'BOLT_Z_local': BOLT_Z, 'BOLT_Z_world': BOLT_Z + LIFT, 'NUT_Y': NUT_Y, 'PAD_Y0': PAD_Y0,
                'LUG_IN': LUG_IN, 'TS_Z': TS_Z}

# ---------------------------------------------------------------- 1. as-built head: no radar, ESP32-CAM instead
dropped = [n for n in list(parts) if 'Radar' in n]
for n in dropped:
    del parts[n]
R2['dropped_parts'] = dropped


# ---------------------------------------------------------------- 2. v06 rear display frame (fitted on the robot)
def frame_v06(tz):
    """screen-mount-v06-review/frame_v06.py new(), verbatim geometry, at tilt-axis height tz (local)."""
    BED_CHAMFER = 0.5
    vz_hi_ = tz + BOARD_H / 2 - VIS_TOP
    vz_lo_ = vz_hi_ - VIS_H
    fr = box(-37, -1.0, tz - 22, 74, 1.0 + BOARD_T + LIP, 44)
    fr = fr.cut(box(-BOARD_L / 2 - POCKET_CLR, -1.1, tz - BOARD_H / 2 - POCKET_CLR,
                    BOARD_L + 2 * POCKET_CLR, 1.1 + BOARD_T, BOARD_H + 2 * POCKET_CLR))
    fr = fr.cut(box(vx_lo - WIN_MARGIN, BOARD_T - 0.1, vz_lo_ - WIN_MARGIN, VIS_W + 2 * WIN_MARGIN, LIP + 0.2,
                    VIS_H + 2 * WIN_MARGIN))
    face = BOARD_T + LIP
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * HOLE_DX / 2, tz + sz * HOLE_DZ / 2
            fr = fr.cut(cy(PILOT_M2 / 2, BOARD_T - 0.1, LIP + 0.3, x, z))
            fr = fr.cut(Part.makeCone(PILOT_M2 / 2, PILOT_M2 / 2 + BED_CHAMFER + 0.1, BED_CHAMFER + 0.1,
                                      V(x, face - BED_CHAMFER, z), V(0, 1, 0)))
    RAIL_IN, RAIL_OUT, RAIL_DZ0, RAIL_DZ1, RAIL_Y0, RAIL_Y1 = 34.0, 38.5, 12.0, 21.5, -55.0, 6.2
    SHELF_IN, SHELF_T0, SHELF_CAP = 29.2, 3.0, 4.0
    for side in (-1, 1):
        x0 = RAIL_IN if side > 0 else -RAIL_OUT
        for sz in (-1, 1):
            zlo = tz + RAIL_DZ0 if sz > 0 else tz - RAIL_DZ1
            fr = fuse(fr, box(x0, RAIL_Y0, zlo, RAIL_OUT - RAIL_IN, RAIL_Y1 - RAIL_Y0, RAIL_DZ1 - RAIL_DZ0))
            pr = [(SHELF_IN, RAIL_Y0), (RAIL_IN + 0.5, RAIL_Y0), (RAIL_IN + 0.5, RAIL_Y0 + SHELF_CAP),
                  (SHELF_IN + SHELF_CAP - SHELF_T0, RAIL_Y0 + SHELF_CAP), (SHELF_IN, RAIL_Y0 + SHELF_T0)]
            if side < 0:
                pr = [(-x, y) for x, y in pr]
            w = Part.makePolygon([V(x, y, tz + sz * 18 - 3.5) for x, y in pr] + [V(pr[0][0], pr[0][1], tz + sz * 18 - 3.5)])
            fr = fuse(fr, Part.Face(w).extrude(V(0, 0, 7)))
    for x in (-32, 32):
        for dz in (-18, 18):
            fr = fr.cut(cy(PILOT_M2 / 2, RAIL_Y0 - 0.1, SHELF_CAP + 1.6, x, tz + dz))
    return fr


TZ_V1 = 206.5
v06 = frame_v06(TZ)
parts['Rear_Display_Frame'] = {'shape': v06, 'motion': 'tilt', 'note': 'v06 rails, as fitted; NOT reprinted', 'group': 'Tilt'}
R2['v06_frame_volume_mm3'] = round(v06.Volume, 1)

# ---------------------------------------------------------------- 3. ESP32-CAM service case v2 (fitted)
CAM_DOC = ROOT / 'cad/head/camera-service-v2-20261021/Gladiator_Camera_Service_v2_REVIEW.FCStd'
cam_v1_world = {}
cd = A.openDocument(str(CAM_DOC))
for lab, nm, grp in (('Mount_Tray', 'Camera_Tray', 'Tilt'), ('Screw_Cover', 'Camera_Cover', 'Tilt'),
                     ('ESP32_CAM_measured_reference', 'ESP32_CAM_Reference', 'Hardware')):
    o = [x for x in cd.Objects if x.Label == lab][0]
    s = o.Shape.copy()
    s.rotate(V(39.5, 113, 0), V(0, 0, 1), 180)        # the review file shows the pan180 viewing pose
    cam_v1_world[nm] = s.copy()                       # v1 world, construction pose
    s.translate(V(-39.5, -113, -10.0 + (TZ - TZ_V1)))  # v1 world -> v2 local (the tilt side rose 1.0)
    parts[nm] = {'shape': s, 'motion': 'tilt', 'note': 'camera service v2, as fitted; NOT reprinted', 'group': grp}
A.closeDocument(cd.Name)

# ---------------------------------------------------------------- 3b. Round 5 head accessories + final shell
R5 = ROOT / 'cad/v2/enclosure/round5-calibrated-28-20261022/style/Gladiator_Round5.FCStd'
CREST = ()   # Jim 2026-10-30: the Round 5 crest/neck guard/clamps were never printed; dropped from v2
SHELL = ('Rear_Hood', 'Front_Left', 'Front_Right', 'Lens_Plate', 'Ref_DrvV5_Fins_L', 'Ref_DrvV5_Fins_R',
         'Ref_DrvV5_Board_L', 'Ref_DrvV5_Board_R', 'Ref_UpperDeck', 'Ref_MastBase')
crest_v1_world = {}
rd_ = A.openDocument(str(R5))
for n in CREST:
    s = rd_.getObject(n).Shape.copy()
    s.rotate(V(39.5, 113, 0), V(0, 0, 1), 180)        # the styling file shows the head at the pan180 viewing pose
    crest_v1_world[n] = s.copy()
    s.translate(V(-39.5, -113, -10.0 + (TZ - TZ_V1)))
    parts[n] = {'shape': s, 'motion': 'tilt', 'note': 'Round 5 head accessory (printed); clamps to the tilt group', 'group': 'Crest'}
for n in SHELL:
    s = rd_.getObject(n).Shape.copy()
    s.translate(V(-WORLD.x, -WORLD.y, -WORLD.z))
    parts[n] = {'shape': s, 'motion': 'robot', 'note': 'final shell / robot context (fixed)', 'group': 'Robot_Context'}
A.closeDocument(rd_.Name)

# ---------------------------------------------------------------- 4. tilting head + yoke 26 mm rearward
TILT_SIDE = [n for n, p in parts.items() if p['motion'] == 'tilt'] + ['Tilt_Yoke', 'Tilt_Pivot_Bolt', 'SG90_Tilt_Reference']
for n in TILT_SIDE:
    parts[n]['shape'].translate(V(0, YOKE_DY, 0))
T = T + V(0, YOKE_DY, 0)
R2['tilt_axis_local'] = [T.x, T.y, T.z]
R2['tilt_axis_world'] = [T.x + WORLD.x, T.y + WORLD.y, T.z + WORLD.z]

# the yoke floor now covers the pedestal bore and the retainer screws: wire passage + driver holes
yk = parts['Tilt_Yoke']['shape']
yk = yk.cut(box(0.8, -6.0, F0 - 1, 5.8, 12.0, 6.0).common(cyl(6.5, F0 - 1, 6.0)))   # beside the ear plate (x -2.8..0.2)
for a in SCREW_ANGLES:
    x, y = R_SCREW * math.cos(math.radians(a)), R_SCREW * math.sin(math.radians(a))
    yk = yk.cut(cyl(3.5, F0 - 1, 6.0, x, y))
assert yk.isValid() and len(yk.Solids) == 1
parts['Tilt_Yoke']['shape'] = yk
parts['Tilt_Yoke']['note'] = 'v2: v05 yoke, towers +10, ear plate and pivot tower narrowed to columns below the servo, + wire passage over the pan bore + 4 driver holes; sits 26 mm rearward'

# ---------------------------------------------------------------- 5. the v2 mast tube (printed)
TUBE_Z0 = 6.0 - LIFT
SLOT_Z0, SLOT_Z1, SLOT_HW = 22.0 - LIFT, SPLIT_TOP, 3.5          # slot ends under the collar's closed band
tube = ring(10.0, 6.0, TUBE_Z0, 120.0 - TUBE_Z0)
tube = tube.cut(box(-15, FLAT_Y, COLLAR_Z0 - 2, 30, 10, 120 - COLLAR_Z0 + 3))     # key flat, under the whole collar
tube = tube.cut(cx_(1.8, -11, 22, 0, 13.0 - LIFT))                                  # base pin, as v1 (world Z 13)
tube = tube.cut(cx_(1.8, -11, 22, 0, BOLT_Z))                                       # v2 head bolt
tube = tube.cut(box(-5, 0, 24.0 - LIFT, 10, 11, 12))                                # v1 wire window, now really open
tube = tube.cut(box(-SLOT_HW, -11, SLOT_Z0, 2 * SLOT_HW, 6, SLOT_Z1 - SLOT_Z0))     # lay-in slot, rear side
assert tube.isValid() and len(tube.Solids) == 1
parts['Mast_Tube_v2'] = {'shape': tube, 'motion': 'fixed', 'note': 'printed, 20 OD / 12 bore, Z 6..170', 'group': 'Mast'}
R2['tube'] = {'world_z': [6.0, 170.0], 'slot_world_z': [SLOT_Z0 + LIFT, SLOT_Z1 + LIFT], 'slot_width': 2 * SLOT_HW,
              'flat_world_z': [COLLAR_Z0 - 2 + LIFT, 170.0], 'base_pin_world_z': 13.0, 'head_bolt_world_z': BOLT_Z + LIFT,
              'window_world_z': [24.0, 36.0],
              'torsion_note': 'the open slot makes the tube ~15x softer in twist; worst case about 1.3 deg over 150 mm at '
                              'the SG90 stall torque (0.18 N m), PLA G~1300 MPa. Estimate, not tested.'}

# ---------------------------------------------------------------- 6. posing
SERVO_SIDE = ('SG90_Pan_Reference', 'Pan_Servo_Carriage', 'Pan_Drive_Pulley', 'Pan_Horn_Reference', 'Pan_Belt_Reference')
U_SERVO = V(math.cos(math.radians(SERVO_ANG)), math.sin(math.radians(SERVO_ANG)), 0)


def posed2(n, pan=0.0, tilt=0.0, C=None):
    p = parts[n]
    m = p['motion']
    if n == 'Pan_Belt_Reference' and C is not None:
        s = rotF(belt_for(C))
    else:
        s = p['shape'].copy()
    if C is not None and n in SERVO_SIDE and n != 'Pan_Belt_Reference':
        s.translate(U_SERVO * (C - C_NOM))
    if m == 'tilt':
        s.rotate(T, V(1, 0, 0), tilt)
    if m in ('pan', 'tilt'):
        s.rotate(V(), V(0, 0, 1), pan)
    if m == 'servo':
        centre = SERVO_POS + (U_SERVO * (C - C_NOM) if C is not None else V())
        s.rotate(centre, V(0, 0, 1), pan / RATIO)
    return s


def ov(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    return a.common(b).Volume


INTENDED2 = {frozenset(['Pan_Bearing_Lower', 'Neck_Main']), frozenset(['Pan_Bearing_Upper', 'Neck_Main'])}
TILT_N = [n for n, p in parts.items() if p['motion'] == 'tilt']
PAN_N = [n for n, p in parts.items() if p['motion'] == 'pan']
FIX_N = [n for n, p in parts.items() if p['motion'] in ('fixed', 'belt', 'servo', 'robot')]
R2['groups'] = {'tilt': TILT_N, 'pan': PAN_N, 'fixed': FIX_N}

# 6a. everything at the home pose
static = []
names = list(parts)
for i, a in enumerate(names):
    sa = posed2(a)
    for b in names[i + 1:]:
        if parts[a]['motion'] == 'robot' and parts[b]['motion'] == 'robot':
            continue
        if frozenset([a, b]) in INTENDED2:
            continue
        v = ov(sa, posed2(b))
        if v > 0.05:
            static.append([a, b, round(v, 3)])
R2['static_collisions'] = static
print('static collisions', static)

# 6b. tilt sweep, -60..60 (positive = camera DOWN, negative = camera UP), against the pan side
TILTS_W = [float(t) for t in range(-90, 91, 2)]
PANS_W = [float(p) for p in range(int(HEAD_TRAVEL[0]), int(HEAD_TRAVEL[1]) + 1, 20)]
hit_pan_side = {}
for t in TILTS_W:
    hs = []
    for a in TILT_N:
        sa = posed2(a, 0.0, t)
        for b in PAN_N:
            v = ov(sa, posed2(b))
            if v > 0.05:
                hs.append([a, b, round(v, 2)])
    hit_pan_side[t] = hs
# 6c. tilt sweep against the fixed neck (pan matters: the neck and pan servo do not turn)
hit_fixed = {}
for pn in PANS_W:
    fixed_shapes = {b: posed2(b, pn, 0.0) for b in FIX_N}
    for t in TILTS_W:
        hs = []
        for a in TILT_N:
            sa = posed2(a, pn, t)
            for b, sb in fixed_shapes.items():
                v = ov(sa, sb)
                if v > 0.05:
                    hs.append([a, b, round(v, 2)])
        hit_fixed[(pn, t)] = hs


def free_range(pn):
    up = down = 0.0
    for t in sorted([t for t in TILTS_W if t > 0]):
        if hit_pan_side[t] or hit_fixed[(pn, t)]:
            break
        down = t
    for t in sorted([t for t in TILTS_W if t < 0], reverse=True):
        if hit_pan_side[t] or hit_fixed[(pn, t)]:
            break
        up = t
    return up, down


ranges = {pn: free_range(pn) for pn in PANS_W}
R2['tilt_free_range_by_pan'] = {str(int(pn)): {'camera_up_deg': -u, 'camera_down_deg': d} for pn, (u, d) in ranges.items()}
R2['tilt_free_range_worst'] = {'camera_up_deg': min(-u for u, d in ranges.values()),
                               'camera_down_deg': min(d for u, d in ranges.values())}
R2['tilt_first_contacts'] = {}
for pn in PANS_W:
    u, d = ranges[pn]
    for t, lab in ((u - 2, 'up'), (d + 2, 'down')):
        if t in TILTS_W:
            R2['tilt_first_contacts']['pan %d %s %d' % (pn, lab, t)] = hit_pan_side[t] + hit_fixed[(pn, t)]
print('tilt free range worst', R2['tilt_free_range_worst'])

# 6d. v1 geometry for comparison: tilting head back 26 mm, against the v1 top plate + seat (camera-up only)
v1_top = fuse(ring(R_ROT, 6.5, TOP_PLATE_Z, TOP_PLATE_T), box(-25, -30, TOP_PLATE_Z, 50, 30, TOP_PLATE_T))
v1_up = None
for t in [-float(k) for k in range(0, 61)]:
    hit = False
    for a in TILT_N:
        s = posed2(a, 0.0, 0.0)
        s.translate(V(0, -YOKE_DY, 0))
        s.rotate(T - V(0, YOKE_DY, 0), V(1, 0, 0), t)
        if ov(s, v1_top) > 0.05:
            hit = True
            break
    if hit:
        v1_up = -t
        break
R2['v1_camera_up_contact_deg_same_parts'] = v1_up
print('v1-like camera-up contact at', v1_up)

# 6e. pan side against the fixed neck, every 5 degrees
pf = []
for pn in [float(p) for p in range(int(HEAD_TRAVEL[0]), int(HEAD_TRAVEL[1]) + 1, 5)]:
    for a in PAN_N:
        sa = posed2(a, pn)
        for b in FIX_N:
            if frozenset([a, b]) in INTENDED2:
                continue
            v = ov(sa, posed2(b, pn))
            if v > 0.05:
                pf.append([a, b, pn, round(v, 2)])
R2['pan_vs_fixed_collisions'] = pf

# 6f. carriage at both ends of its travel
ce = []
others = [n for n in parts if n not in SERVO_SIDE]
for C in (C_MIN, C_MAX):
    for pn in [float(p) for p in range(-20, 181, 20)]:
        for t in (-25.0, 0.0, 25.0):
            for a in SERVO_SIDE:
                sa = posed2(a, pn, t, C)
                for b in others:
                    if frozenset([a, b]) in INTENDED2:
                        continue
                    v = ov(sa, posed2(b, pn, t))
                    if v > 0.05:
                        ce.append([a, b, C, pn, t, round(v, 2)])
R2['carriage_end_collisions'] = ce
print('carriage-end collisions', len(ce))

# 6g. driver access to the 4 pan retainer screws from above, head level, pan 0
acc = {}
for a in SCREW_ANGLES:
    x, y = R_SCREW * math.cos(math.radians(a)), R_SCREW * math.sin(math.radians(a))
    probe = cyl(2.4, F0 + 4.05, 80, x, y)
    acc[str(a)] = [n for n in parts if n != 'Pan_Raised_Pedestal' and ov(posed2(n), probe) > 0.01]
R2['retainer_screw_driver_blockers_head_level'] = acc
# wingnut room: M3 wingnut ~ 20 wide x 10 tall, on +X beside the collar
wing = box(LUG_X, -10, BOLT_Z - 7, 8, 20, 14)
R2['wingnut_envelope_blockers'] = [n for n in parts if n not in ('Mast_Tube_v2',) and ov(posed2(n), wing) > 0.01]

# ---------------------------------------------------------------- 7. balance (ESTIMATE, not weighed)
RHO, FILL = 1.24e-3, 0.85
POINT = {'ESP32_CAM_Reference': 10.0, 'Dual_ToF_Envelope': 5.0, 'ST7789_Board': 7.0, 'SG90_Tilt_Reference': 9.0,
         'Tilt_Horn_Reference': 1.0, 'Tilt_Pivot_Bolt': 1.0}
PRINTED = list(CREST) + ['Rear_Display_Frame', 'GH44_Tilt_Receiver', 'GH44_Dual_Carrier', 'ToF_Sensor_Frame', 'Camera_Tray',
           'Camera_Cover', 'Tilt_Yoke', 'Pan_Raised_Pedestal', 'Pan_Rotor', 'Pan_Retainer']


def com(s):
    m, acc_ = 0.0, V()
    for so in s.Solids:
        m += so.Volume
        acc_ += so.CenterOfMass * so.Volume
    return acc_ * (1.0 / m)


items = []
for n in PRINTED:
    items.append((n, parts[n]['motion'], RHO * FILL * parts[n]['shape'].Volume, com(parts[n]['shape'])))
for n, g in POINT.items():
    items.append((n, parts[n]['motion'], g, com(parts[n]['shape'])))
items.append(('screws/nuts at the carrier (lump)', 'tilt', 8.0, com(parts['GH44_Dual_Carrier']['shape'])))
items.append(('Duponts/wires at the camera (lump)', 'tilt', 4.0, com(parts['Camera_Tray']['shape'])))


def summary(dy_tilt_side):
    tm, tmy, tmz, hm, hmy = 0.0, 0.0, 0.0, 0.0, 0.0
    for n, m_, g, c in items:
        on_tilt = m_ == 'tilt'
        shifted = on_tilt or n in ('Tilt_Yoke', 'SG90_Tilt_Reference', 'Tilt_Pivot_Bolt')
        y = c.y + (dy_tilt_side if shifted else 0.0)
        if on_tilt:
            tm += g
            tmy += g * y
            tmz += g * c.z
        hm += g
        hmy += g * y
    ty = (T.y + dy_tilt_side)
    return {'tilting_mass_g': round(tm, 1), 'tilting_com_ahead_of_pivot_mm': round(ty - tmy / tm, 1),
            'tilt_servo_holding_kgcm': round(tm * (ty - tmy / tm) / 10000.0, 3),
            'moving_head_mass_g': round(hm, 1), 'head_com_ahead_of_mast_axis_mm': round(-hmy / hm, 1)}


R2['balance_estimate'] = {
    'assumptions': 'PLA 1.24 g/cc x 0.85 fill; ESP32-CAM 10 g, ToF 5 g, ST7789 7 g, SG90 9 g, +8 g screws, +4 g wires. '
                   'NOT weighed. "ahead" = toward the camera/sensor face.',
    'v1': summary(-YOKE_DY), 'v2': summary(0.0),
    'parts_g': {n: round(g, 1) for n, m_, g, c in items}}
print('balance', json.dumps(R2['balance_estimate'], indent=1))

# ---------------------------------------------------------------- 8. print STLs for the parts that change
LIN, ANG = 0.01, 0.0872665


def bed_chamfer(shape, size=BED_RELIEF):
    z0 = shape.BoundBox.ZMin
    edges = [e for e in shape.Edges if len(e.Vertexes) == 1 and e.Curve.TypeId == 'Part::GeomCircle'
             and abs(e.BoundBox.ZMin - z0) < 1e-6 and abs(e.BoundBox.ZMax - z0) < 1e-6]
    out, n = shape, 0
    for e in edges:
        try:
            cand = out.makeChamfer(size, [e])
            if cand.isValid() and len(cand.Solids) == 1:
                out, n = cand, n + 1
        except Exception:
            pass
    return out, n


carF_print = car_F.copy()
carF_print.rotate(V(), V(1, 0, 0), 180)
rec_print = parts['GH44_Tilt_Receiver']['shape'].copy()
rec_print.rotate(V(), V(1, 0, 0), 90)
PRINT = {
    'Mast_Tube_v2': (tube, 'upright, base (pin) end on the bed; no support. 164 mm tall'),
    'Neck_Main': (parts['Neck_Main']['shape'], 'collar on the bed; supports under the C arm, riser and pad (as v1)'),
    'Pan_Servo_Carriage': (carF_print, 'top face on the bed, tensioner lug up; no support'),
    'Pan_Drive_Pulley': (drive_local, 'horn plate on the bed; no support'),
    'Pan_Raised_Pedestal': (ped, 'base plate on the bed; support under the top plate only, keep the belt channel clear'),
    'Tilt_Yoke': (parts['Tilt_Yoke']['shape'], 'floor on the bed; no support'),
    'GH44_Tilt_Receiver': (rec_print, 'GH44 face down, arms up; no support'),
}
stl_rep = []
for name, (shape, how) in PRINT.items():
    s = shape.copy()
    b0 = s.BoundBox
    s.translate(V(-b0.XMin, -b0.YMin, -b0.ZMin))
    s, nch = bed_chamfer(s)
    assert s.isValid() and len(s.Solids) == 1, name
    path = OUT / 'stl' / ('Gladiator_Head_v2_%s.stl' % name)
    MeshPart.meshFromShape(Shape=s, LinearDeflection=LIN, AngularDeflection=ANG, Relative=False).write(str(path))
    back = Mesh.Mesh(str(path))
    bb = s.BoundBox
    stl_rep.append({'part': name, 'file': path.name, 'print_orientation': how,
                    'size_mm': [round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
                    'grams_solid_pla': round(s.Volume * 0.00124, 1), 'bed_relief_edges': nch,
                    'mesh_solid': back.isSolid(), 'mesh_non_manifold': back.hasNonManifolds(),
                    'fits_220x220x250': bb.XLength <= 220 and bb.YLength <= 220 and bb.ZLength <= 250})
import shutil
CAM_STL = ROOT / 'cad/head/camera-service-v2-20261021/stl'
for src_, nm in (('Camera_Service_v2_Tray.stl', 'Camera_Tray'), ('Camera_Service_v2_Lid.stl', 'Camera_Cover')):
    dst = OUT / 'stl' / ('Gladiator_Head_v2_%s.stl' % nm)
    shutil.copy(CAM_STL / src_, dst)
    m_ = Mesh.Mesh(str(dst)); bb = m_.BoundBox
    stl_rep.append({'part': nm, 'file': dst.name, 'print_orientation': 'as released in camera-service-v2-20261021/stl (unchanged)',
                    'size_mm': [round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
                    'grams_solid_pla': round(m_.Volume * 0.00124, 1), 'bed_relief_edges': 0,
                    'mesh_solid': m_.isSolid(), 'mesh_non_manifold': m_.hasNonManifolds(),
                    'fits_220x220x250': bb.XLength <= 220 and bb.YLength <= 220 and bb.ZLength <= 250})
R2['print_stl'] = stl_rep
R2['not_reprinted'] = ['Pan_Rotor', 'Pan_Retainer', 'GH44_Dual_Carrier', 'ToF_Sensor_Frame', 'Rear_Display_Frame (v06)']
R2['dropped_decor'] = 'Round 5 crest, holder trim, neck guard and head clamps: never printed (Jim 2026-10-30)'
R2['hardware'] = {'head_bolt': 'M3 x 35 + M3 wingnut (collar is 30 across the bolt pads)', 'camera_case': '2 x M3 x 12 + 2 M3 nuts (cover), 3 x M2 x 6 (carrier)',
                  'tensioner': 'M3 x 16 + M3 nut (nut drops into the carriage lug from the top)',
                  'removed': 'v1 Neck_Clamp_Cap and its 2 x M3 clamp screws'}

# ---------------------------------------------------------------- 9. FreeCAD file at world position + render meshes
doc = A.newDocument('Gladiator_Head_v2_Mast')
grp_objs = {}
for n, p in parts.items():
    g = p['group']
    if g not in grp_objs:
        grp_objs[g] = doc.addObject('App::DocumentObjectGroup', g)
    s = p['shape'].copy()
    s.translate(WORLD)
    o = doc.addObject('Part::Feature', n)
    o.Shape = s
    grp_objs[g].addObject(o)
doc.recompute()
doc.saveAs(str(OUT / 'Gladiator_Head_v2_Mast.FCStd'))
Part.export([doc.getObject(n) for n in PRINT], str(OUT / 'Gladiator_Head_v2_Mast_printed-parts.step'))

RD = OUT / 'render'
RD.mkdir(exist_ok=True)
CHANGED = set(PRINT)
render_index = {'v2': [], 'v2_tilt': [], 'v1': []}


def dump(tag, n, s, kind):
    path = RD / ('%s__%s.stl' % (tag, n))
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.08, AngularDeflection=0.3, Relative=False).write(str(path))
    render_index[tag].append({'name': n, 'file': path.name, 'kind': kind})


UP_DEG = min(45.0, R2['tilt_free_range_worst']['camera_up_deg'])   # picture pose
R2['render_tilt_camera_up_deg'] = UP_DEG
for n, p in parts.items():
    if p['motion'] == 'robot':
        kind = 'context'
    elif n in ('Pan_Belt_Reference',):
        kind = 'belt'
    elif n in CHANGED:
        kind = 'changed'
    elif p['group'] == 'Hardware':
        kind = 'hardware'
    else:
        kind = 'same'
    s = posed2(n)
    s.translate(WORLD)
    dump('v2', n, s, kind)
    s = posed2(n, 0.0, -float(UP_DEG))
    s.translate(WORLD)
    dump('v2_tilt', n, s, kind)

# v1 as built, for the comparison picture: v05 file + v06 frame + camera case + the master mast tube
v05 = A.openDocument(str(ROOT / 'cad/head/v05-sensor-mounts/Gladiator_Head_v05_PanStack.FCStd'))
for o in v05.Objects:
    if not hasattr(o, 'Shape') or o.Shape.isNull() or o.TypeId == 'App::DocumentObjectGroup' or o.Shape.Volume < 1:
        continue
    if o.Label in ('Rear_Display_Frame',) or 'Radar' in o.Label or o.Label not in parts and o.Label != 'Neck_Clamp_Cap':
        continue
    dump('v1', o.Label, o.Shape.copy(), 'hardware' if parts.get(o.Label, {}).get('group') == 'Hardware' else 'same')
A.closeDocument(v05.Name)
f1 = frame_v06(TZ_V1)
f1.translate(V(39.5, 113, 10))
dump('v1', 'Rear_Display_Frame', f1, 'same')
for nm, s in list(cam_v1_world.items()) + list(crest_v1_world.items()):
    dump('v1', nm, s, 'hardware' if nm.startswith('ESP32') else 'same')
mst = A.openDocument(str(MASTER))
dump('v1', 'MastTube', mst.getObject('MastTube').Shape.copy(), 'same')
A.closeDocument(mst.Name)
(RD / 'index.json').write_text(json.dumps(render_index, indent=1))

R2['runtime_s'] = round(time.time() - t_start)
(OUT / 'validation.json').write_text(json.dumps(report, indent=2, default=str) + '\n')
print('V2 DONE', R2['runtime_s'], 's')
