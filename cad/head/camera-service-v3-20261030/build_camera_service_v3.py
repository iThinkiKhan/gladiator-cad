"""Camera service v3 (2026-10-30): camera service v2 with the cover held by M2 heat-set inserts.
Run on cad-lab:  xvfb-run -a freecad cad/head/camera-service-v3-20261030/build_camera_service_v3.py
Baseline is camera-service-v2-20261021/generated-build.py (the full v2 source); this script patches it.

Changes from v2:
- Cover: 2 x M2 screws into 2 M2 heat-set inserts in the tray lug tops (bore 2.8, 4.0 deep, upright in print,
  pressed in from the cover seam). Replaces 2 x M3x12 + side-loaded M3 nuts. Screw-tip relief 2.2 x 4 more,
  so M2x6 and M2x8 both fit. Cover holes M2 clearance 2.6 with a bed-side chamfer.
- Lugs radius 4.4 -> 3.6 (no nut to house): smaller and lighter on the front-heavy head. Lugs moved out
  1.8 mm (EAR_DX 10 -> 11.8) to keep 1 mm of solid plastic between the SD-side insert and the SD finger recess.
- Board retention: one small snap bump on each long wall, just in front of the PCB, so the board stays in
  the tray with the cover off. 0.6 proud = about 0.2 mm grip per side; file it down if too tight.
- Lens hole: 0.4 mm chamfer on the bed side.
"""
from pathlib import Path
import hashlib, json, os, traceback
ROOT = Path('/home/buralien/projects/gladiator-cad')
OUT = ROOT / 'cad/head/camera-service-v3-20261030'
(OUT / 'stl').mkdir(parents=True, exist_ok=True)
(OUT / 'preview').mkdir(parents=True, exist_ok=True)
V2 = ROOT / 'cad/head/camera-service-v2-20261021'
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


rep("OUT = ROOT / 'cad/head/camera-service-v2-20261021'", "OUT = ROOT / 'cad/head/camera-service-v3-20261030'")
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
lid = lid.cut(Part.makeCone(4.9,4.5,.4,A.Vector(LENS_X,Y_LID_OUT,LENS_Z),A.Vector(0,1,0)))''')

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
''')
rep("report['service_v2']=service", "report['service_v3']=service")
rep('Camera_Service_v2_%s.stl', 'Camera_Service_v3_%s.stl')

ns = {'__name__': '__camera_build__'}
try:
    (OUT / 'generated-build.py').write_text(source)
    exec(compile(source, str(OUT / 'generated-build.py'), 'exec'), ns)
    import FreeCAD as A, FreeCADGui as Gui, Part, Import, math
    rpt = json.loads((OUT / 'validation.json').read_text())
    v2 = json.loads((V2 / 'validation.json').read_text())
    PLA = 1.24e-3
    rpt['v3_vs_v2'] = {p: {'v2_mm3': v2['case'][p]['volume_mm3'], 'v3_mm3': rpt['case'][p]['volume_mm3'],
                           'solid_PLA_g_change': round((rpt['case'][p]['volume_mm3'] - v2['case'][p]['volume_mm3']) * PLA, 2)}
                       for p in ('tray', 'lid')}
    rpt['service_v3'] = {k: v for k, v in ns['report']['service_v3'].items()}
    (OUT / 'validation.json').write_text(json.dumps(rpt, indent=1, default=str))
    doc = A.newDocument('Camera_Service_v3_Review')
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
    for name, s, col in [('Camera_Tray_v3', ns['tray'], (.22, .26, .31)), ('Camera_Cover_v3', ns['lid'], (.95, .49, .13))]:
        ob = add(name, pose(gl(s)), 'PrintedParts', col); printed.append(ob)
        ob.addProperty('App::PropertyString', 'ReviewStatus'); ob.ReviewStatus = 'CAD review draft 2026-10-30; not printed'
    add('ESP32_CAM_measured_reference', pose(gl(ns['board_comp'])), 'BoardAndWiring', (.1, .5, .24))
    for i, d in enumerate(ns['dups']): add('Dupont_%02d' % i, pose(gl(d)), 'BoardAndWiring', (.16, .16, .16), False)
    for i, w in enumerate(ns['wire_shapes']): add('Wire_route_%02d' % i, pose(gl(w)), 'BoardAndWiring', (.8, .15, .1), False)
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
    doc.recompute()
    v = Gui.activeDocument().activeView()

    def iso(direction):
        d = A.Vector(*direction); d.normalize()
        right = A.Vector(0, 0, 1).cross(d); right.normalize(); up = d.cross(right)
        v.setCameraOrientation(A.Rotation(right, up, d, 'ZXY').Q); v.fitAll()

    iso((1, 1, .75))
    doc.saveAs(str(OUT / 'Gladiator_Camera_Service_v3_REVIEW.FCStd'))
    Import.export(printed, str(OUT / 'Gladiator_Camera_Service_v3.step'))
    v.saveImage(str(OUT / 'assembled.png'), 1600, 1200, 'White')
    # exploded: cover 40 forward, screws 55 forward, context hidden (robot front is +Y after pose)
    for ob in groups['HeadContext'].Group: ob.ViewObject.Visibility = False
    printed[1].Placement.Base += A.Vector(0, 40, 0)
    for ob in groups['Fasteners'].Group:
        if ob.Name.startswith('M2x6'): ob.Placement.Base += A.Vector(0, 55, 0)
    iso((1, 1, .75))
    v.saveImage(str(OUT / 'exploded.png'), 1600, 1200, 'White')
    # looking into the open tray: inserts + snap bumps (cover, screws, board hidden)
    printed[1].ViewObject.Visibility = False
    for ob in groups['Fasteners'].Group:
        ob.ViewObject.Visibility = ob.Name.startswith('M2_heatset')
    doc.getObject('ESP32_CAM_measured_reference').ViewObject.Visibility = False
    iso((.35, 1, .5))
    v.saveImage(str(OUT / 'open_tray.png'), 1600, 1200, 'White')
    # section through the SD-side lug
    for g in ('PrintedParts', 'BoardAndWiring', 'Fasteners'):
        for ob in groups[g].Group: ob.ViewObject.Visibility = False
    for ob in groups['Sections'].Group: ob.ViewObject.Visibility = True
    printed[1].Placement.Base -= A.Vector(0, 40, 0)
    iso((-1, 0.001, 0.001))
    v.saveImage(str(OUT / 'section_lug.png'), 1600, 1200, 'White')
    for ob in groups['Sections'].Group: ob.ViewObject.Visibility = False
    for ob in groups['PrintedParts'].Group + groups['Fasteners'].Group: ob.ViewObject.Visibility = True
    doc.getObject('ESP32_CAM_measured_reference').ViewObject.Visibility = True
    printed[1].Placement.Base += A.Vector(0, 40, 0)
    iso((1, 1, .75))
    doc.saveAs(str(OUT / 'Gladiator_Camera_Service_v3_EXPLODED.FCStd'))
    manifest = {str(p.relative_to(OUT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*'))
                if p.is_file() and '__pycache__' not in str(p) and not p.name.endswith('.FCBak') and p.name != 'manifest.json'}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print('SERVICE_V3_COMPLETE', str(OUT), flush=True)
except Exception:
    (OUT / 'error.txt').write_text(traceback.format_exc())
    traceback.print_exc()
    import sys; sys.stdout.flush(); sys.stderr.flush()
    os._exit(1)
import sys; sys.stdout.flush(); sys.stderr.flush()
os._exit(0)
