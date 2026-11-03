"""Camera service v4 (2026-10-31): v3 (cover on M2 heat-set inserts) + flash-LED window + Dupont plug retention.
Run on cad-lab:  xvfb-run -a freecad cad/head/camera-service-v4-20261031/build_camera_service_v4.py
Baseline is camera-service-v2-20261021/generated-build.py (the full v2 source); this script patches it with the
v3 changes (same patches as build_camera_service_v3.py) and then the v4 changes.

v3 changes (unchanged here): 2 x M2 into heat-set inserts in the lug tops, smaller lugs, snap bumps, lens chamfer.

v4 changes:
- Flash LED (the 5 x 5 mm white LED on GPIO4, far corner of the camera side): window in the cover, with a light
  tube from the cover down to 0.33 mm above the LED so the light does not fill the case. Tube walls cut the beam
  at about 42 deg half-angle, a bit wider than the camera view (about 32 deg). Bed-side chamfer on the window.
- Dupont retention: one printed plug clip per header row (2 identical clips). The clip turns the 8 single plugs into
  one block and has a comb at its rear: one lane per wire, open at the back and on the outer side, so each wire
  drops in sideways and turns out toward its wall exit. Backstop pads on the tray floor sit 0.4 mm behind the clip,
  so with the case closed the plugs cannot back off the pins. The pads avoid the carrier screws and driver holes.
"""
from pathlib import Path
import hashlib, json, os, traceback
ROOT = Path('/home/buralien/projects/gladiator-cad')
OUT = ROOT / 'cad/head/camera-service-v4-20261031'
(OUT / 'stl').mkdir(parents=True, exist_ok=True)
(OUT / 'preview').mkdir(parents=True, exist_ok=True)
V2 = ROOT / 'cad/head/camera-service-v2-20261021'
V3 = ROOT / 'cad/head/camera-service-v3-20261030'
source = (V2 / 'generated-build.py').read_text()


def rep(old, new):
    global source
    assert source.count(old) == 1, (old[:80], source.count(old))
    source = source.replace(old, new)


def rep_span(start, end, new):
    global source
    assert source.count(start) == 1, start
    a = source.index(start)
    b = source.index(end, a)
    source = source[:a] + new + source[b:]


rep("OUT = ROOT / 'cad/head/camera-service-v2-20261021'", "OUT = ROOT / 'cad/head/camera-service-v4-20261031'")
rep('EAR_R, EAR_DX = 4.4, 10.0', 'EAR_R, EAR_DX = 3.6, 11.8')

rep_span('NUT_AF, NUT_DEPTH = 6.0, 2.8', '\n# Chamfer the wire-contact edges', '''# v3: M2 heat-set inserts in the lug tops (Jim's accepted bore 2.8, 4.0 deep; inserts about 3 long).
INS_BORE, INS_DEPTH, INS_L = 2.8, 4.0, 3.0
TAIL_D, TAIL_L = 2.2, 4.0            # screw-tip relief below the insert: M2x6 and M2x8 both fit
for x, z in ears:
    tray = tray.cut(cy(INS_BORE / 2, Y_LID_IN - 0.1, Y_LID_IN + INS_DEPTH, x, z))
    tray = tray.cut(cy(TAIL_D / 2, Y_LID_IN + INS_DEPTH - 0.05, Y_LID_IN + INS_DEPTH + TAIL_L, x, z))
    # 3.6 x 2.4 tie passage through the exposed rear end of each lug (as v2).
    tray = tray.cut(lbox(x-EAR_R-.1, x+EAR_R+.1, Y_FACE-7, Y_FACE-3.4, z-1.2, z+1.2))
''')

rep('tray = tray.removeSplitter()\n\n# ---------------------------------------------------------------- lid', '''tray = tray.removeSplitter()
# v4: Dupont plug clips (one per header row) and backstop pads on the tray floor behind them.
HOUS = 1.3                                  # half width of the modelled 2.6 mm Dupont housing
CL_IN, CL_OUT, CL_END_OUT, CL_END = 0.8, 0.7, 0.4, 0.8   # inner plate, outer plate, end-wall outer reach, end wall
COMB_T, TOOTH, SPINE_IN = 1.0, 0.8, 0.75    # comb depth, tooth width (lane 1.74), spine edge from the pin axis
Y_DEND = Y_BACK + HDR_PLASTIC + LC          # rear end of the plugs
Y_CL0 = Y_BACK + HDR_PLASTIC + 2.0          # clip front edge (2 mm behind the header plastic)
Y_CLB = Y_DEND + COMB_T                     # clip rear face
PAD_GAP = 0.4                               # clip rear face to backstop pads
ROWS = [(xb(25.2), -1), (xb(2.2), 1)]       # (pin axis x, outward sign): wires leave toward the nearest long wall
CL_Z0, CL_Z1 = PIN_Z[7] - HOUS - CL_END, PIN_Z[0] + HOUS + CL_END


def xs(px, so, a, b):                       # offsets measured toward the board centre (inner side) -> x range
    u, w = px - so * a, px - so * b
    return min(u, w), max(u, w)


# pad z ranges per row: end pads under the clip end walls, spine pads under the inner spine, clear of the
# carrier M2 screws (37.5, +-8), the M3 driver holes (16, +-16) and the display screws (32, +-18)
PAD_SPEC = {-1: [('end', CL_Z0 - 0.5, CL_Z0 + 0.6), ('spine', 10.0, 12.6)],
            1: [('end', CL_Z0 - 0.5, CL_Z0 + 0.6), ('spine', 12.5, 15.5), ('end', CL_Z1 - 0.6, CL_Z1 + 0.5)]}
backstops = []
for px, so in ROWS:
    for kind, z0, z1 in PAD_SPEC[so]:
        x0, x1 = xs(px, so, -(HOUS + CL_END_OUT), HOUS + CL_IN) if kind == 'end' else xs(px, so, 1.1, 2.6)
        backstops.append(lbox(x0, x1, Y_CLB + PAD_GAP, Y_FLOOR_IN + 0.01, z0, z1))
tray = fuse(tray, *backstops)
tray = tray.removeSplitter()
tray_nonub = tray.copy()
# v3: snap bumps on both long walls, in front of the PCB, so the board stays put with the cover off.
# Flat catch face 0.15 mm in front of the PCB (a 0.6 mm overhang in print), 1:3 lead-in ramp toward the seam.
NUB, NUB_Z = 0.6, (-11.5, -5.5)
Y_NUB = Y_BACK - PCB_T - 0.15
nubs = []
for xw, sgn in ((CX0, 1), (CX1, -1)):
    vv = [A.Vector(xw - sgn*0.05, Y_NUB, NUB_Z[0]), A.Vector(xw + sgn*NUB, Y_NUB, NUB_Z[0]),
          A.Vector(xw - sgn*0.05, Y_NUB - 3*NUB, NUB_Z[0])]
    nb = Part.Face(Part.makePolygon(vv + [vv[0]])).extrude(A.Vector(0, 0, NUB_Z[1] - NUB_Z[0]))
    nubs.append(nb)
    tray = tray.fuse(nb)
tray = tray.removeSplitter()

# ---------------------------------------------------------------- lid''')

rep('''lid = lid.cut(cy(1.8,Y_LID_OUT-.1,Y_LID_IN+.1,x,z))
    lid = lid.cut(Part.makeCone(2.15,1.8,.35,A.Vector(x,Y_LID_OUT,z),A.Vector(0,1,0)))''',
    '''lid = lid.cut(cy(M2_CLEAR/2,Y_LID_OUT-.1,Y_LID_IN+.1,x,z))
    lid = lid.cut(Part.makeCone(M2_CLEAR/2+.35,M2_CLEAR/2,.35,A.Vector(x,Y_LID_OUT,z),A.Vector(0,1,0)))
# v3: bed-side chamfer on the lens hole (the cover prints outer face down)
lid = lid.cut(Part.makeCone(4.9,4.5,.4,A.Vector(LENS_X,Y_LID_OUT,LENS_Z),A.Vector(0,1,0)))
# v4: flash LED window + light tube. LED (STEP solid 73): Xb 29.50..34.90, Zb 1.17..6.23, top Yb 2.92.
LED_X = (xb(6.23), xb(1.17)); LED_Z = (zb(34.90), zb(29.50)); LED_TOP_Y = Y_BACK - 2.92
WIN_M, TUBE_W, TUBE_GAP = 0.6, 0.8, 0.33     # window margin round the LED, tube wall, tube end above the LED
WIN = (LED_X[0] - WIN_M, LED_X[1] + WIN_M, LED_Z[0] - WIN_M, LED_Z[1] + WIN_M)
Y_TUBE_END = LED_TOP_Y - TUBE_GAP
tube = lbox(WIN[0] - TUBE_W, CX1 - 0.25, Y_LID_IN - 0.01, Y_TUBE_END, WIN[2] - TUBE_W, WIN[3] + TUBE_W)
# notch over the camera flex where it meets its connector (flex Zb 7.26.., Xb ..28.65, top Yb 3.69)
tube = tube.cut(lbox(WIN[0] - 2, xb(7.26) + 0.5, Y_BACK - 3.69 - 0.4, Y_TUBE_END + 0.1, zb(28.65) - 0.5, WIN[3] + 2))
lid = lid.fuse(tube)
lid = lid.cut(lbox(WIN[0], WIN[1], Y_LID_OUT - 0.1, Y_TUBE_END + 0.1, WIN[2], WIN[3]))
def _rect(y, g):
    return Part.makePolygon([A.Vector(WIN[0]-g, y, WIN[2]-g), A.Vector(WIN[1]+g, y, WIN[2]-g),
                             A.Vector(WIN[1]+g, y, WIN[3]+g), A.Vector(WIN[0]-g, y, WIN[3]+g), A.Vector(WIN[0]-g, y, WIN[2]-g)])
lid = lid.cut(Part.makeLoft([_rect(Y_LID_OUT - 0.01, 0.41), _rect(Y_LID_OUT + 0.4, 0.0)], True))''')

rep('b.common(tray).Volume)', 'b.common(tray_nonub).Volume)')

rep_span('hardware=[]', "service['closed_exit_height_mm']=4.5", '''hardware=[]; inserts=[]
SCREW_L = 6.0
CTX = ('GH44_Dual_Carrier','ToF_Sensor_Frame','Dual_ToF_Envelope','Rear_Display_Frame','GH44_Tilt_Receiver')
for x,z in ears:
    # M2x6 with a 3.8 x 1.3 head; insert modelled as a 3.0 OD x 3.0 tube seated 0.3 below the seam
    screw=cy(1.0,Y_LID_OUT,Y_LID_OUT+SCREW_L,x,z).fuse(cy(1.9,Y_LID_OUT-1.3,Y_LID_OUT,x,z))
    hardware.append(screw)
    inserts.append(cy(1.5,Y_LID_IN+.3,Y_LID_IN+.3+INS_L,x,z).cut(cy(1.0,Y_LID_IN,Y_LID_IN+INS_L+1,x,z)))
    service.setdefault('screw_vs_print_mm3',[]).append(screw.common(tray).Volume+screw.common(lid).Volume)
    service.setdefault('m2x8_tip_vs_tray_mm3',[]).append(cy(1.0,Y_LID_OUT,Y_LID_OUT+8.0,x,z).common(tray).Volume)
    drv = cy(2.5,Y_LID_OUT-35,Y_LID_OUT-1.4,x,z)
    service.setdefault('driver_vs_case_mm3',[]).append(drv.common(tray.fuse(lid)).Volume)
    service.setdefault('driver_vs_head_context_mm3',[]).append(max(glob(drv).common(G[n]).Volume for n in CTX))
    ring = cy(INS_BORE/2+1.0,Y_LID_IN,Y_LID_IN+INS_DEPTH,x,z).cut(cy(INS_BORE/2,Y_LID_IN-.1,Y_LID_IN+INS_DEPTH+.1,x,z))
    service.setdefault('insert_1mm_wall_missing_mm3',[]).append(ring.Volume-ring.common(tray).Volume)
    service.setdefault('screw_head_vs_fovs_mm3',[]).append(glob(screw).common(tof_fov).Volume+glob(screw).common(cam_fov).Volume)
    service.setdefault('screw_vs_head_context_mm3',[]).append(max(glob(screw).common(G[n]).Volume for n in CTX))
service['fastener']='2 x M2x6 (M2x8 also fits) into 2 M2 heat-set inserts; bore 2.8 x 4.0 deep, upright, pressed in from the seam'
service['thread_engagement_m2x6_mm']=round(SCREW_L-(Y_LID_IN-Y_LID_OUT),2)
service['insert_bottom_to_tie_passage_mm']=round((Y_FACE-7)-(Y_LID_IN+INS_DEPTH+TAIL_L),2)
service['nub_grip_per_side_mm']=round(NUB-CLR,3)
service['nub_catch_gap_to_pcb_front_mm']=0.15
service['nub_vs_seated_board_mm3']=max(nb.common(board_comp).Volume for nb in nubs)
_bp = board_comp.copy(); _bp.translate(A.Vector(0,-0.6,0))   # board pulled 0.6 toward the seam: must catch
service['nub_catch_when_pulled_info']=round(max(nb.common(_bp).Volume for nb in nubs),4)
assert service['nub_catch_when_pulled_info'] > 0.01, 'snap bumps do not catch the board'

# ---- v4: flash LED window
led_s = [s for s in board if abs(s.BoundBox.XLength-5.06)<.05 and abs(s.BoundBox.YLength-1.64)<.05 and abs(s.BoundBox.ZLength-5.4)<.05]
assert len(led_s) == 1, 'flash LED not found in the board model'
led = led_s[0]; lb = led.BoundBox
assert max(abs(lb.XMin-LED_X[0]),abs(lb.XMax-LED_X[1]),abs(lb.ZMin-LED_Z[0]),abs(lb.ZMax-LED_Z[1]),abs(lb.YMin-LED_TOP_Y))<.02, lb
PLAY = 0.4                                   # board play in the tray used for the shifted checks
shifts = [A.Vector(dx,0,dz) for dx in (-PLAY,0,PLAY) for dz in (-PLAY,0,PLAY)]
led_view, tube_gap, cov_ov = [], [], []
for sh in shifts:
    sight = lbox(lb.XMin, lb.XMax, Y_LID_OUT-1, lb.YMin, lb.ZMin, lb.ZMax); sight.translate(sh)
    led_view.append(sight.common(lid).Volume)          # straight-ahead view of the whole LED top through the window
    b = board_comp.copy(); b.translate(sh)
    cov_ov.append(b.common(lid).Volume)
    tube_gap.append(tube.distToShape(b)[0])
service['led_top_blocked_by_cover_with_play_mm3'] = max(led_view)
service['board_vs_cover_with_play_mm3'] = max(cov_ov)
service['led_tube_to_board_min_with_play_mm'] = round(min(tube_gap), 3)
assert min(tube_gap) > 0.15, tube_gap
depth = LED_TOP_Y - Y_LID_OUT
hx, hz = (WIN[1]-WIN[0])/2, (WIN[3]-WIN[2])/2
service['led_beam_cutoff_half_angle_deg'] = [round(math.degrees(math.atan((lb.XLength/2+hx)/depth)),1),
                                             round(math.degrees(math.atan((lb.ZLength/2+hz)/depth)),1)]
service['led_full_brightness_half_angle_deg'] = [round(math.degrees(math.atan((hx-lb.XLength/2)/depth)),1),
                                                 round(math.degrees(math.atan((hz-lb.ZLength/2)/depth)),1)]
service['led_window_mm'] = [round(2*hx,2), round(2*hz,2)]
service['led_centre_to_lens_axis_mm'] = round(math.hypot(lb.Center.x-LENS_X, lb.Center.z-LENS_Z),2)
th = math.radians(max(service['led_beam_cutoff_half_angle_deg'])); L_ = 80.0
def _brect(y, g):
    return Part.makePolygon([A.Vector(WIN[0]-g, y, WIN[2]-g), A.Vector(WIN[1]+g, y, WIN[2]-g),
                             A.Vector(WIN[1]+g, y, WIN[3]+g), A.Vector(WIN[0]-g, y, WIN[3]+g), A.Vector(WIN[0]-g, y, WIN[2]-g)])
beam = Part.makeLoft([_brect(Y_LID_OUT-0.05, 0.0), _brect(Y_LID_OUT-L_, L_*math.tan(th))], True)
beam_g = glob(beam)
service['led_beam_vs_head_parts_mm3_info'] = {n: round(beam_g.common(G[n]).Volume,3) for n in CTX}
service['led_beam_vs_case_mm3'] = beam.common(tray).Volume + beam.common(lid).Volume
service['led_beam_vs_cover_screws_mm3'] = max(beam.common(h).Volume for h in hardware)

# ---- v4: Dupont plug clips (2 identical; one per header row) and the floor backstops
clips = []
for px, so in ROWS:
    c_ = lbox(*xs(px, so, -(HOUS+CL_END_OUT), HOUS+CL_IN), Y_CL0, Y_CLB, CL_Z0, CL_Z1)
    c_ = c_.fuse(lbox(*xs(px, so, -(HOUS+CL_OUT), -(HOUS+CL_END_OUT)+.01), Y_CL0, Y_DEND, CL_Z0+CL_END+.3, CL_Z1-CL_END-.3))   # stays inside the open wire channel
    c_ = c_.cut(lbox(*xs(px, so, -HOUS-.03, HOUS+.03), Y_CL0-.1, Y_DEND, CL_Z0+CL_END-.05, CL_Z1-CL_END+.05))   # plug pocket (2.66 x 20.43; prints ~0.1 under)
    for pz in PIN_Z:                                                                              # wire lanes
        hw_ = (2.54 - TOOTH) / 2
        c_ = c_.cut(lbox(*xs(px, so, -(HOUS+CL_OUT)-.2, SPINE_IN), Y_DEND-.05, Y_CLB+.1, pz-hw_, pz+hw_))
    c_ = c_.removeSplitter()
    assert c_.isValid() and len(c_.Solids) == 1, 'clip'
    clips.append(c_)
clip_cmp = Part.makeCompound(clips)
bs_cmp = Part.makeCompound(backstops)
service['clip_vs_board_mm3'] = clip_cmp.common(board_comp).Volume
service['clip_vs_plugs_mm3'] = max(clip_cmp.common(d).Volume for d in dups)
service['clip_vs_wires_mm3'] = max(clip_cmp.common(w).Volume for w in wire_shapes)
service['backstops_vs_wires_mm3'] = max(bs_cmp.common(w).Volume for w in wire_shapes)
service['backstops_vs_plugs_mm3'] = max(bs_cmp.common(d).Volume for d in dups)
ct, cl = [], []
for sh in shifts:
    q = clip_cmp.copy(); q.translate(sh)
    _ct = q.common(tray); ct.append(_ct.Volume); cl.append(q.common(lid).Volume)
    if _ct.Volume > 1e-4:
        _b = _ct.BoundBox
        print('CLIP_TRAY_HIT', [sh.x, sh.z], round(_ct.Volume, 3), [round(t, 2) for t in (_b.XMin, _b.XMax, _b.YMin, _b.YMax, _b.ZMin, _b.ZMax)], flush=True)
service['clip_vs_tray_with_play_mm3'] = max(ct)
service['clip_vs_cover_with_play_mm3'] = max(cl)
service['clip_insertion_vs_tray_mm3'] = 0.0
for off in (-1,-3,-6,-10,-20,-35):
    q = clip_cmp.copy(); q.translate(A.Vector(0,off,0))
    service['clip_insertion_vs_tray_mm3'] = max(service['clip_insertion_vs_tray_mm3'], q.common(tray_nonub).Volume)
service['clip_rear_to_backstops_mm'] = round(clip_cmp.distToShape(bs_cmp)[0], 3)
service['clip_to_tray_min_mm'] = round(clip_cmp.distToShape(tray)[0], 3)
service['clip_to_cover_min_mm'] = round(clip_cmp.distToShape(lid)[0], 3)
service['clip_wire_lane_mm'] = round(2.54 - TOOTH, 2)
_bear = []
for c_ in clips:                              # clip rear face projected onto the pads
    face_band = lbox(-999, 999, Y_CLB - 0.05, Y_CLB, -999, 999).common(c_)
    face_band.translate(A.Vector(0, PAD_GAP + 0.05, 0))
    _bear.append(round(face_band.common(bs_cmp).Volume / 0.05, 2))
service['clip_backstop_contact_area_mm2'] = _bear
clip_vol = clips[0].Volume
service['clip_volume_mm3_each'] = round(clip_vol, 1)
''')
rep("report['service_v2']=service", "report['service_v4']=service")
rep('Camera_Service_v2_%s.stl', 'Camera_Service_v4_%s.stl')

ns = {'__name__': '__camera_build__'}
try:
    (OUT / 'generated-build.py').write_text(source)
    exec(compile(source, str(OUT / 'generated-build.py'), 'exec'), ns)
    import FreeCAD as A, FreeCADGui as Gui, Part, Import, math
    rpt = json.loads((OUT / 'validation.json').read_text())
    v2 = json.loads((V2 / 'validation.json').read_text())
    v3 = json.loads((V3 / 'validation.json').read_text())
    PLA = 1.24e-3
    rpt['v4_vs_v3'] = {p: {'v3_mm3': v3['case'][p]['volume_mm3'], 'v4_mm3': rpt['case'][p]['volume_mm3'],
                           'solid_PLA_g_change': round((rpt['case'][p]['volume_mm3'] - v3['case'][p]['volume_mm3']) * PLA, 2)}
                       for p in ('tray', 'lid')}
    rpt['v4_vs_v2_mm3'] = {p: [v2['case'][p]['volume_mm3'], rpt['case'][p]['volume_mm3']] for p in ('tray', 'lid')}
    rpt['service_v4'] = {k: v for k, v in ns['report']['service_v4'].items()}
    # clip STL: comb (rear) face on the bed, plug pockets open upward; both clips are the same part
    c0 = ns['clips'][0].copy(); c0.rotate(A.Vector(0, 0, 0), A.Vector(1, 0, 0), -90)
    bb = c0.BoundBox; c0.translate(A.Vector(-bb.XMin, -bb.YMin, -bb.ZMin))
    c1 = ns['clips'][1].copy(); c1.rotate(A.Vector(0, 0, 0), A.Vector(1, 0, 0), -90)
    c1.rotate(c1.BoundBox.Center, A.Vector(0, 0, 1), 180)
    bb1 = c1.BoundBox; c1.translate(A.Vector(-bb1.XMin, -bb1.YMin, -bb1.ZMin))
    same = abs(c0.common(c1).Volume - c0.Volume) < 0.01 and abs(c0.Volume - c1.Volume) < 0.01
    assert same, 'the two clips are not the same part'
    ns['mesh'](c0).write(str(OUT / 'stl' / 'Camera_Service_v4_Plug_Clip_print2.stl'))
    rpt['case']['plug_clip'] = {'valid': c0.isValid(), 'solids': len(c0.Solids), 'volume_mm3': round(c0.Volume, 1),
                                'count': 2, 'both_identical': same, 'stl': 'Camera_Service_v4_Plug_Clip_print2.stl',
                                'print_bbox_mm': [round(c0.BoundBox.XLength, 2), round(c0.BoundBox.YLength, 2), round(c0.BoundBox.ZLength, 2)]}
    (OUT / 'validation.json').write_text(json.dumps(rpt, indent=1, default=str))
    doc = A.newDocument('Camera_Service_v4_Review')
    groups = {n: doc.addObject('App::DocumentObjectGroup', n)
              for n in ('PrintedParts', 'BoardAndWiring', 'Fasteners', 'HeadContext', 'Sections')}

    def pose(shape):
        s = shape.copy(); s.rotate(A.Vector(39.5, 113, 0), A.Vector(0, 0, 1), 180); return s

    def add(name, shape, group, color, visible=True, alpha=0):
        ob = doc.addObject('Part::Feature', name); ob.Shape = shape; groups[group].addObject(ob)
        ob.ViewObject.ShapeColor = color; ob.ViewObject.Transparency = alpha; ob.ViewObject.Visibility = visible
        return ob

    gl = ns['glob']
    printed = []
    for name, s, col in [('Camera_Tray_v4', ns['tray'], (.22, .26, .31)), ('Camera_Cover_v4', ns['lid'], (.95, .49, .13)),
                         ('Plug_Clip_A', ns['clips'][0], (.2, .55, .9)), ('Plug_Clip_B', ns['clips'][1], (.2, .55, .9))]:
        ob = add(name, pose(gl(s)), 'PrintedParts', col); printed.append(ob)
        ob.addProperty('App::PropertyString', 'ReviewStatus'); ob.ReviewStatus = 'CAD review draft 2026-10-31; not printed'
    add('ESP32_CAM_measured_reference', pose(gl(ns['board_comp'])), 'BoardAndWiring', (.1, .5, .24))
    add('Flash_LED_GPIO4', pose(gl(ns['led'])), 'BoardAndWiring', (1.0, .95, .2))
    for i, d in enumerate(ns['dups']): add('Dupont_%02d' % i, pose(gl(d)), 'BoardAndWiring', (.16, .16, .16), False)
    for i, w in enumerate(ns['wire_shapes']): add('Wire_route_%02d' % i, pose(gl(w)), 'BoardAndWiring', (.8, .15, .1), False)
    add('LED_beam_42deg', pose(gl(ns['beam'])), 'BoardAndWiring', (1.0, .95, .4), False, 80)
    for i, s in enumerate(ns['hardware']): add('M2x6_screw_%d' % i, pose(gl(s)), 'Fasteners', (.72, .72, .76))
    for i, s in enumerate(ns['inserts']): add('M2_heatset_insert_%d' % i, pose(gl(s)), 'Fasteners', (.85, .65, .2))
    G = ns['G']
    for n in ('GH44_Dual_Carrier', 'ToF_Sensor_Frame', 'Dual_ToF_Envelope', 'Rear_Display_Frame', 'GH44_Tilt_Receiver'):
        add(n, pose(G[n]), 'HeadContext', (.45, .53, .6), n in ('GH44_Dual_Carrier', 'ToF_Sensor_Frame'), 65)
    # section through the SD-side lug (plane x = lug x), keeping the -x half
    ex, ez = ns['ears'][0]
    half = Part.makeBox(200, 400, 400, A.Vector(ex, -200, -200))
    crop = Part.makeBox(400, 400, 20, A.Vector(-200, -200, ez - 12)) if ez > 0 else None
    def sec(s):
        return s.common(crop).cut(half)
    add('Section_Tray_through_SD_lug', pose(gl(sec(ns['tray']))), 'Sections', (.22, .26, .31), False)
    add('Section_Cover_through_SD_lug', pose(gl(sec(ns['lid']))), 'Sections', (.95, .49, .13), False)
    add('Section_Insert', pose(gl(sec(ns['inserts'][0]))), 'Sections', (.85, .65, .2), False)
    add('Section_Screw', pose(gl(sec(ns['hardware'][0]))), 'Sections', (.72, .72, .76), False)
    # section through the LED and its light tube (plane z = LED centre, keeping the lower half)
    lz = ns['led'].BoundBox.Center.z
    keep_low = Part.makeBox(400, 400, 200, A.Vector(-200, -200, lz - 200))
    for nm, s, col in (('Section_Cover_through_LED', ns['lid'], (.95, .49, .13)), ('Section_Tray_through_LED', ns['tray'], (.22, .26, .31)),
                       ('Section_Board_through_LED', ns['board_comp'], (.1, .5, .24)), ('Section_LED', ns['led'], (1.0, .95, .2))):
        add(nm, pose(gl(s.common(keep_low))), 'Sections', col, False)
    # section through a plug row (plane x = pin axis of the LED-side row), keeping the outer half
    rx = ns['ROWS'][1][0]
    keep_out = Part.makeBox(200, 400, 400, A.Vector(rx, -200, -200))
    for nm, s, col in (('Section_Tray_through_plugs', ns['tray'], (.22, .26, .31)), ('Section_Clip', ns['clips'][1], (.2, .55, .9)),
                       ('Section_Board_through_plugs', ns['board_comp'], (.1, .5, .24))):
        add(nm, pose(gl(s.common(keep_out))), 'Sections', col, False)
    for i, d in enumerate(ns['dups']):
        if abs(d.BoundBox.Center.x - rx) < 1:
            add('Section_Plug_%02d' % i, pose(gl(d.common(keep_out))), 'Sections', (.16, .16, .16), False)
    doc.recompute()
    v = Gui.activeDocument().activeView()

    def iso(direction):
        d = A.Vector(*direction); d.normalize()
        right = A.Vector(0, 0, 1).cross(d); right.normalize(); up = d.cross(right)
        v.setCameraOrientation(A.Rotation(right, up, d, 'ZXY').Q); v.fitAll()

    def show(pred):
        for ob in doc.Objects:
            if ob.TypeId == 'Part::Feature':
                ob.ViewObject.Visibility = bool(pred(ob.Name))

    default_vis = {ob.Name: ob.ViewObject.Visibility for ob in doc.Objects if ob.TypeId == 'Part::Feature'}
    iso((1, 1, .75))
    doc.saveAs(str(OUT / 'Gladiator_Camera_Service_v4_REVIEW.FCStd'))
    Import.export(printed[:2], str(OUT / 'Gladiator_Camera_Service_v4.step'))
    Import.export(printed, str(OUT / 'Gladiator_Camera_Service_v4_with_clips.step'))
    v.saveImage(str(OUT / 'assembled.png'), 1600, 1200, 'White')
    # front of the case: LED window next to the lens
    show(lambda n: n in ('Camera_Tray_v4', 'Camera_Cover_v4', 'ESP32_CAM_measured_reference', 'Flash_LED_GPIO4') or n.startswith('M2x6'))
    iso((.25, 1, .3))
    v.saveImage(str(OUT / 'front_led_window.png'), 1600, 1200, 'White')
    # cover from the inside: light tube
    show(lambda n: n == 'Camera_Cover_v4')
    iso((.35, -1, .45))
    v.saveImage(str(OUT / 'cover_inside.png'), 1600, 1200, 'White')
    # LED section
    show(lambda n: n in ('Section_Cover_through_LED', 'Section_Tray_through_LED', 'Section_Board_through_LED', 'Section_LED'))
    iso((0.001, 0.001, 1))
    v.saveImage(str(OUT / 'section_led.png'), 1600, 1200, 'White')
    # back of the board: plugs, clips, wire routes (tray and cover hidden)
    show(lambda n: n.startswith('Dupont_') or n.startswith('Wire_route') or n.startswith('Plug_Clip') or n == 'ESP32_CAM_measured_reference')
    iso((.3, -1, .55))
    v.saveImage(str(OUT / 'plugs_rear.png'), 1600, 1200, 'White')
    # open tray with plugs + clips in place (board and cover hidden): backstop pads under the clips
    show(lambda n: n == 'Camera_Tray_v4' or n.startswith('Plug_Clip') or n.startswith('Dupont_') or n.startswith('M2_heatset'))
    iso((.35, 1, .5))
    v.saveImage(str(OUT / 'open_tray_clips.png'), 1600, 1200, 'White')
    show(lambda n: n == 'Camera_Tray_v4' or n.startswith('M2_heatset'))
    iso((.35, 1, .5))
    v.saveImage(str(OUT / 'open_tray.png'), 1600, 1200, 'White')
    # plug row section
    show(lambda n: n.startswith('Section_Tray_through_plugs') or n.startswith('Section_Clip') or n.startswith('Section_Board_through_plugs') or n.startswith('Section_Plug'))
    iso((1, 0.001, 0.001))
    v.saveImage(str(OUT / 'section_plugs.png'), 1600, 1200, 'White')
    # exploded: cover 40 forward, screws 55 forward, context hidden (robot front is +Y after pose)
    show(lambda n: default_vis.get(n) and not n.startswith('GH44') and not n.startswith('ToF') and not n.startswith('Dual') and not n.startswith('Rear'))
    printed[1].Placement.Base += A.Vector(0, 40, 0)
    for ob in groups['Fasteners'].Group:
        if ob.Name.startswith('M2x6'): ob.Placement.Base += A.Vector(0, 55, 0)
    iso((1, 1, .75))
    v.saveImage(str(OUT / 'exploded.png'), 1600, 1200, 'White')
    show(lambda n: default_vis.get(n))
    iso((1, 1, .75))
    doc.saveAs(str(OUT / 'Gladiator_Camera_Service_v4_EXPLODED.FCStd'))
    manifest = {str(p.relative_to(OUT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*'))
                if p.is_file() and '__pycache__' not in str(p) and not p.name.endswith('.FCBak') and p.name != 'manifest.json'}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print('SERVICE_V4_COMPLETE', str(OUT), flush=True)
except Exception:
    (OUT / 'error.txt').write_text(traceback.format_exc())
    traceback.print_exc()
    import sys; sys.stdout.flush(); sys.stderr.flush()
    os._exit(1)
import sys; sys.stdout.flush(); sys.stderr.flush()
os._exit(0)
