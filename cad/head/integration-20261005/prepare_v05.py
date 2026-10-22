"""Add measured, removable sensor frames to an isolated v05 head candidate."""
from pathlib import Path
import hashlib, json

ROOT = Path('/home/buralien/projects/gladiator-cad')
source = (ROOT/'scripts/build_head_v04.py').read_text()
base_hash = hashlib.sha256(source.encode()).hexdigest()

def replace(old, new):
    global source
    assert source.count(old) == 1, (old[:100], source.count(old))
    source = source.replace(old, new)

replace("OUT = ROOT / 'cad/head/v04-pan-stack'", "OUT = ROOT / 'cad/head/v05-sensor-mounts'")
source = source.replace('Gladiator_Head_v04_', 'Gladiator_Head_v05_').replace('GladiatorHeadV04', 'GladiatorHeadV05')
replace("inherit_names = ['Dual_ToF_Envelope', 'Dual_Radar_Envelope']", "inherit_names = []")
replace("variant_names = ['GH44_Blank_Carrier', 'GH44_ToF_Carrier', 'GH44_Radar_Carrier', 'GH44_Camera_Carrier',\n                 'SEN0628_Envelope', 'SEN0610_Envelope', 'ESP32_CAM_Envelope']", "variant_names = []  # old sensor variants use superseded dimensions; do not carry them forward")
replace("'sensor_mounting': 'ToF/radar attachment not yet designed; dual carrier remains held.',", "'sensor_hardware': 'Measured-pattern frames designed; verify board orientation, M3 x16 lengths and connector/wire bends at assembly.',")
replace("'source_sha256': before,", "'source_sha256': before, 'derived_from_v04_sha256': '%s'," % base_hash)
replace("'release': 'DESIGN CANDIDATE, stages 1 (pan stack) and 2 (tilt side). Not released.'", "'release': 'v05 measured sensor mounts; prototype CAD checked, physical assembly not yet verified'")
replace("dual = fuse(car_base, box(-35, -58, TZ - 21, 70, 3, 42))", "dual = fuse(car_base, box(-42, -58, TZ - 21, 84, 3, 42))")
replace("addp('GH44_Dual_Carrier', dual, 'tilt', 'tested male register; sensor mounting NOT designed yet', 'Tilt')", '''# Removable sensor adapters: screw from the carrier rear into tested M2 pilots.
# Counterbores make the rear seating datum -55 even where the central plate is 6 mm thick.
TOF_ATTACH = [(-38.5, 7.0), (-24.0, -17.0), (6.5, 16.0)]
RAD_ATTACH = [(37.5, 8.0), (37.5, -8.0), (24.0, 17.5)]
for x, dz in TOF_ATTACH + RAD_ATTACH:
    dual = dual.cut(cy(M2_CLEAR/2, -58.1, 8.2, x, TZ+dz))
    dual = dual.cut(cy(2.25, -55, 4.5, x, TZ+dz))
addp('GH44_Dual_Carrier', dual, 'tilt', '84 mm sensor plate; tested male register; removable M2 sensor adapters', 'Tilt')

# PCB planes face -Y. Upright radar is 22 wide x30 high; holes 3.5 from each edge.
# ToF hole positions are derived from the official SEN0628 dimension drawing, not photo scale.
TOF_X, RAD_X = -15.0, 24.0
TOF_HOLES_ALL = [(-17.5,10.25), (17.5,10.25), (-17.5,-4.75), (17.5,-4.75), (-7.5,-10.25), (7.5,-10.25)]
TOF_HOLES = [TOF_HOLES_ALL[k] for k in (0,1,4,5)]
RAD_HOLES = [(x,z) for x in (-7.5,7.5) for z in (-11.5,11.5)]
TOF_SEAT, RAD_SEAT = -75.0, -73.0  # 14 / 12 mm from adapter's front plane -61
SENSOR_CHECKS = []

def stroke_y(p, q, r, y=-61, thickness=3):
    dx,dz = q[0]-p[0], q[1]-p[1]
    length = math.hypot(dx,dz)
    nx,nz = -dz*r/length, dx*r/length
    v = [A.Vector(x,y,TZ+z) for x,z in [(p[0]+nx,p[1]+nz),(q[0]+nx,q[1]+nz),
                                      (q[0]-nx,q[1]-nz),(p[0]-nx,p[1]-nz)]]
    body = Part.Face(Part.makePolygon(v+[v[0]])).extrude(A.Vector(0,thickness,0))
    return fuse(body,cy(r,y,thickness,p[0],TZ+p[1]),cy(r,y,thickness,q[0],TZ+q[1]))

def sensor_frame(name, center, holes, attach, seat):
    pts = [(center+x,z) for x,z in holes]
    # Connect the top row and each side, leaving the bottom open for leads.
    top = sorted([p for p in pts if p[1]>0])
    bottom = sorted([p for p in pts if p[1]<0])
    body = fuse(stroke_y(top[0],top[1],2), stroke_y(top[0],bottom[0],2), stroke_y(top[1],bottom[1],2))
    for x,z in pts:
        # A 3.25 radius seat stays inside the 3.5 mm hole-to-edge board land.
        # Wide captive-nut feet end at -64, behind the component keepout.
        body = fuse(body,cy(5,-64,6,x,TZ+z),cy(3.25,seat,-64-seat,x,TZ+z))
    for x,z in attach:
        near = min(pts,key=lambda p:(p[0]-x)**2+(p[1]-z)**2)
        body = fuse(body,stroke_y((x,z),near,2),cy(3.25,-61,3,x,TZ+z))
    for x,z in pts:
        body = body.cut(cy(M3_CLEAR/2,seat-.1,-58-seat+.2,x,TZ+z))
        body = body.cut(hex_y(NUT_AF,-63.6,NUT_DEPTH,x,TZ+z))
        body = body.cut(box(x-5.2,-63.7,TZ+z-3,5.2,2.8,6))
    for x,z in attach:
        body = body.cut(cy(PILOT_M2/2,-61.1,3.2,x,TZ+z))
    body = body.removeSplitter()
    addp(name,body,'tilt','four M3 x16 PCB screws, 6 AF side-loaded nuts; three rear M2 x6 adapter screws','Tilt')
    for x,z in pts:
        shank = cy(1.79,seat-.1,-58-seat+.2,x,TZ+z)
        annulus = cy(3.2,seat,.25,x,TZ+z).cut(cy(1.81,seat-.1,.45,x,TZ+z))
        probe = hex_y(5.95,-63.55,2.5,x,TZ+z)
        # Sweep the actual reduced nut through its insertion slot.
        route_overlap = 0.0
        for shift in (0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10):
            moved = probe.copy(); moved.translate(A.Vector(shift,0,0))
            route_overlap = max(route_overlap,body.common(moved).Volume)
        check = {'part':name,'hole_xz_mm':[x,z], 'shank_overlap_mm3':body.common(shank).Volume,
                 'seat_annulus_mm3':body.common(annulus).Volume,'seat_annulus_expected_mm3':annulus.Volume,
                 'nut_insertion_overlap_mm3':route_overlap,
                 'm3x16_tip_y_mm':seat-1.6+16,'minimum_carrier_tip_clearance_mm':-58-(seat-1.6+16)}
        SENSOR_CHECKS.append(check)
        assert check['shank_overlap_mm3']<1e-6, check
        assert abs(check['seat_annulus_mm3']-annulus.Volume)<1e-6, check
        assert route_overlap<1e-6, check
    for x,z in attach:
        assert body.common(cy(1.165,-61.1,3.2,x,TZ+z)).Volume<1e-6
        assert dual.common(cy(1.29,-58.1,7.6,x,TZ+z)).Volume<1e-6
    return body

tof_frame = sensor_frame('ToF_Sensor_Frame',TOF_X,TOF_HOLES,TOF_ATTACH,TOF_SEAT)
rad_frame = sensor_frame('Radar_Sensor_Frame',RAD_X,RAD_HOLES,RAD_ATTACH,RAD_SEAT)

def board_keepout(center,width,height,seat,holes,hole_d,back_height,front_height):
    # These are clearance reservations, not a component-accurate PCB model.
    # ToF uses the full rectangular bounding outline including ears, conservatively.
    pcb = box(center-width/2,seat-1.6,TZ-height/2,width,1.6,height)
    rear = box(center-width/2,seat,TZ-height/2,width,back_height,height)
    front = box(center-width/2,seat-1.6-front_height,TZ-height/2,width,front_height,height)
    for x,z in holes:
        pcb = pcb.cut(cy(hole_d/2,seat-1.7,1.8,center+x,TZ+z))
        # Mounting land must be free of components within radius 3.5 of the hole.
        rear = rear.cut(cy(3.5,seat-.1,back_height+.2,center+x,TZ+z))
        front = front.cut(cy(3.5,seat-1.7-front_height,front_height+.2,center+x,TZ+z))
    return fuse(pcb,rear,front)

tof_ref = board_keepout(TOF_X,42,27.5,TOF_SEAT,TOF_HOLES_ALL,3.1,9.9,9.9)
rad_ref = board_keepout(RAD_X,22,30,RAD_SEAT,RAD_HOLES,3.0,8.0,8.0)
addp('Dual_ToF_Envelope',tof_ref,'tilt','42 x27.5; 1.6 PCB and 11.5 whole stack per SEN0628 drawing; conservative 9.9 per-side clearance','Hardware')
addp('Dual_Radar_Envelope',rad_ref,'tilt','22 x30, corner holes diameter3, edge gap2, max rear component8 measured; 1.6 PCB/front8 assumed','Hardware')
report['sensor_mounts'] = {
    'coordinate_frame':'local: X right, Y rearward, Z up; sensor face -Y; z coordinates relative to tilt axis',
    'ToF':{'board_mm':[42,27.5], 'holes_drawing_xy_from_bottom_left_mm':[[3.5,24],[38.5,24],[3.5,9],[38.5,9],[13.5,3.5],[28.5,3.5]],
           'drawing_url':'https://dfimg.dfrobot.com/62d52567aa9508d63a4247a1/wikien/778eca8cf06dcba34c8748d079867f14_0x0.jpg.webp',
           'used_holes_relative_center_mm':TOF_HOLES,'center_x_mm':TOF_X,'rear_standoff_mm':14,
           'rear_component_reservation_mm':9.9,'rear_reservation_to_nut_foot_mm':1.1,'pcb_back_y_mm':TOF_SEAT},
    'radar':{'board_mm':[22,30],'hole_diameter_mm':3,'hole_edge_gap_mm':2,'derived_pitch_mm':[15,23],
             'used_holes_relative_center_mm':RAD_HOLES,'center_x_mm':RAD_X,'rear_standoff_mm':12,
             'rear_component_height_measured_mm':8,'rear_component_to_nut_foot_mm':1,'pcb_back_y_mm':RAD_SEAT},
    'pcb_mount_screws':'8 x M3 x16 with 8 M3 nuts; nominal length includes assumed 1.6 radar PCB; verify actual hardware',
    'adapter_screws':'6 x M2 x6 from carrier rear; head diameter <=4.5, head height <=2.6; pilots 2.35',
    'nut_pockets_mm':{'across_flats':6,'depth':2.6,'insertion':'from -X side; fit nuts before installing the adapters'},
    'checks':SENSOR_CHECKS,
    'limitations':['ToF rectangular envelope intentionally over-reserves the ear cutouts.',
                   'ToF optical center and radar antenna location not measured; FOV reservations use stated board bounds.',
                   'Radar PCB thickness 1.6 and front height8 assumed. Rear height8 is Jim measured.',
                   'Both PCBs require clear radius3.5 mounting lands. Actual connector exits and cable bends need assembly checks.']}
report['checks']['sensor_mounts_pass'] = True
''')
replace("doc.Label = 'Gladiator head v0.4 - pan and tilt, corrected 2026-10-05'", "doc.Label = 'Gladiator head v0.5 - measured removable sensor mounts, 2026-10-05'")
replace("HOLD = {'GH44_Dual_Carrier'}       # the sensor mounting (Neck_Main released 2026-10-05: horn top 16.5)", "HOLD = set()  # prototype manufacturing candidates; physical assembly verification remains")
replace("'none for the interface (tested register); sensor mounting is NOT designed'", "'prototype: tested GH44 interface; measured board patterns; verify connector routing and screws at assembly'")
replace("# print orientation: a rotation applied before dropping each part onto the bed", '''for name, shape, holes, center, seat in [('ToF_Sensor_Frame',tof_frame,TOF_HOLES,TOF_X,TOF_SEAT),
                                          ('Radar_Sensor_Frame',rad_frame,RAD_HOLES,RAD_X,RAD_SEAT)]:
    x,z = holes[0]; x += center
    exports[name] = (shape,'carrier mating face DOWN, posts UP; no support; short 6 mm nut-slot bridges',
                     'prototype: tested nut and pilot fits; measured PCB pattern',
                     [((x+2.6,seat+.2,TZ+z),True),((x,seat+.2,TZ+z),False)])
# print orientation: a rotation applied before dropping each part onto the bed''')
replace("'Rear_Display_Frame': (X_AXIS, -90.0)}", "'Rear_Display_Frame': (X_AXIS, -90.0),\n       'ToF_Sensor_Frame': (X_AXIS,-90.0), 'Radar_Sensor_Frame': (X_AXIS,-90.0)}")
replace("    'Stage 2 regenerates the tilt yoke, GH44 receiver, dual carrier and display frame from code. Still '\n    'NOT designed: how the ToF and radar boards fasten to the carrier (their hole coordinates are not '\n    'measured), and the cable harness. The sensor envelopes and the other carrier variants are v0.3 '\n    'references only.',", "    'Sensor mounts use measured radar dimensions and published ToF hole positions. Complete harness, '\n    'strain relief and motion stops remain unfinished. Confirm connector orientation and wire bends in assembly.',")
replace("    and not tilt_bad", "    and not tilt_bad\n    and report['checks']['sensor_mounts_pass']")

# Conservative ToF forward frustum starts at the furthest reserved front face, covers the whole PCB.
replace("frustum = Part.makeLoft([square(-71, .5, -17), square(-221, .5 + 150 * math.tan(math.radians(30)), -17)], True)", '''def rect_wire(y,cx,hw,hh):
    vs = [A.Vector(cx+x,y,TZ+z) for x,z in [(-hw,-hh),(hw,-hh),(hw,hh),(-hw,hh)]]
    return Part.makePolygon(vs+[vs[0]])
TOF_FRONT_Y = TOF_SEAT-1.6-9.9
frustum = Part.makeLoft([rect_wire(TOF_FRONT_Y,TOF_X,21,13.75),
                        rect_wire(TOF_FRONT_Y-150,TOF_X,21+150*math.tan(math.radians(30)),
                                  13.75+150*math.tan(math.radians(30)))],True)
report['tof_fov_reservation'] = {'full_angle_degrees':[60,60],'near_plane_mm':[42,27.5],
                                  'length_mm':150,'front_y_mm':TOF_FRONT_Y,
                                  'note':'conservative whole-board origin envelope; exact optical center unmeasured'}''')
replace("            if p['motion'] == 'tilt' or p['name'].startswith('GH44') or 'Envelope' in p['name']:", "            if p['name'] == 'Dual_ToF_Envelope':")
# Concise source heading; no inherited old sensor dimensions in the document.
source = source.replace('Gladiator head v0.4', 'Gladiator head v0.5').replace('v04 failed validation', 'v05 failed validation')
source = source.replace("Path('/tmp/v04_summary.txt')", "Path('/tmp/v05_summary.txt')")
target = ROOT/'scripts/build_head_v05.py'
assert not target.exists(), 'Refuse overwriting existing v05 work'
target.write_text(source)

note = '''
## Sensor measurements and corrected drawing — 2026-10-05 (current)

Supersedes the historical square ToF envelope and missing radar hole coordinates above.

Jim measured/confirmed SEN0628 ToF **42 wide x27.5 high, including ears**. The official
DFRobot drawing (https://wiki.dfrobot.com/sen0628/; dimensional image copied as evidence
in cad/head/integration-20261005/SEN0628-manufacturer-dimensions.webp) gives PCB1.6,
total stack11.5 and six diameter3.1 holes. Derived from its dimension chains and R3.5
lobes, hole centers from bounding bottom-left: (3.5,24),(38.5,24),(3.5,9),(38.5,9),
(13.5,3.5),(28.5,3.5). These coordinates come from the drawing, not new caliper readings.

Jim measured the presence detector **30 long x22 wide**, highest pieces **8**, four
corner holes **diameter3**. The outside/top hole edges are **2 from the PCB edge**.
Interpreted symmetrically at all four corners: centers3.5 in from each edge, derived
pitch15 x23. PCB mounted upright22 wide x30 high. Height8 is used for the rear-component
reservation, as requested in the preceding question; radar PCB thickness1.6 and front
reservation8 remain assumptions, not measurements. Connector projection with plugs
and wire bend radius remain unmeasured.

v05 adapters use four of the six ToF holes (top two and bottom two), all four radar
holes, calibrated diameter3.6 printed M3 passages and tested6.0AF/2.6deep nut pockets.
Rear stand-offs14 ToF/12 radar include room for captive-nut feet plus component clearance;
they are design allowances. Eight M3x16 PCB screws and six M2x6 adapter screws are nominal
assembly specifications to check against actual stock. No new coupon or print requested.
'''
measure = ROOT/'measurements/mast-head.md'
if 'Sensor measurements and corrected drawing — 2026-10-05 (current)' not in measure.read_text():
    with measure.open('a') as f: f.write(note)
print(json.dumps({'v05_source':str(target),'derived_v04_sha256':base_hash,'recorded_sensor_measurements':True},indent=2))
