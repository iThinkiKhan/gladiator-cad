"""Gladiator head v0.3 - corrected belt drive, relocated pan servo, real teeth.

Derived from the v0.2 comparison candidate. Inherits the tilt assembly, GH44
carrier and rear screen frame unchanged; rebuilds the fixed neck and the whole
pan drive from primitives.

Run with the CAD server system python (freecadcmd build_head_v03.py).
Never opens or writes the master.
"""
import sys, json, math, hashlib, itertools
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as A
import Part
import MeshPart

ROOT   = Path('/home/buralien/projects/gladiator-cad')
SOURCE = ROOT/'cad/head/v02-screen-180/Gladiator_Head_v02_Screen180.FCStd'
MASTER = ROOT/'cad/master/Gladiator_Master.FCStd'
OUT    = ROOT/'cad/head/v03-belt'
(OUT/'stl').mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- parameters
PITCH        = 2.0      # 2GT belt pitch
N_DRIVEN     = 60       # printed ring on the pan pedestal
N_DRIVE      = 40       # bought aluminium pulley on the SG90 horn
BELT_TEETH   = 90       # 180 mm closed loop, a stock length
BELT_WIDTH   = 6.0
PLD          = 0.254    # 2GT pitch line differential
TOOTH_DEPTH  = 0.75
GROOVE_R     = 0.65

HEAD_TRAVEL  = (-20.0, 180.0)   # deg; 0 = sensors forward, 180 = screen forward
SEAT_CLR     = 0.10     # rotor pocket clearance on the 32 mm bearing OD
SPINDLE_CLR  = 0.05     # spindle undersize against the 20 mm bearing bore
BEARING      = (20.0, 32.0, 7.0)
BRG_LO_Z     = 123.0    # widened from the v0.2 11 mm spacing
BRG_HI_Z     = 141.0
OUTER_RACE_ID= 28.0     # retainer must bear here only, never on the inner race

RATIO   = float(N_DRIVEN)/N_DRIVE           # head degrees per servo degree
PD_DRIVEN = N_DRIVEN*PITCH/math.pi
PD_DRIVE  = N_DRIVE*PITCH/math.pi
BELT_L    = BELT_TEETH*PITCH

def centre_distance(L, d1, d2):
    """Solve L = 2C + pi(d1+d2)/2 + (d1-d2)^2/(4C) for C."""
    b = (L - math.pi*(d1+d2)/2.0)/2.0
    k = (d1-d2)**2/8.0
    C = b
    for _ in range(60):
        C = b - k/(2*C)
    return C

S = centre_distance(BELT_L, PD_DRIVEN, PD_DRIVE)   # shaft spacing
SERVO_ANG = 225.0        # forward-LEFT diagonal: keeps the C arm to 135 deg
DELTA   = SERVO_ANG - 270.0
SERVO_Y = -S
SERVO_POS = A.Vector(S*math.cos(math.radians(SERVO_ANG)),
                     S*math.sin(math.radians(SERVO_ANG)), 0)
SERVO_TRAVEL = (HEAD_TRAVEL[1]-HEAD_TRAVEL[0])/RATIO
WRAP_SMALL = 180 - 2*math.degrees(math.asin((PD_DRIVEN-PD_DRIVE)/(2*S)))

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
before = {str(p): digest(p) for p in [SOURCE, MASTER]}

doc = A.openDocument(str(SOURCE))
doc.Label = 'Gladiator v0.3 - corrected belt pan drive'
C0 = A.Vector(39.5, 113, 0)
T  = A.Vector(0, -26, 205)      # tilt axis, local

report = {'source_sha256': before,
          'release': 'DESIGN CANDIDATE - fit coupons printable, full head is not released',
          'drive': {}, 'parts': [], 'collisions': [], 'checks': {}, 'limitations': []}

# ------------------------------------------------------------------ helpers
def box(x,y,z,dx,dy,dz): return Part.makeBox(dx,dy,dz,A.Vector(x,y,z))
def cyl(r,z,h,x=0,y=0):  return Part.makeCylinder(r,h,A.Vector(x,y,z))
def cy(r,y,h,x,z):       return Part.makeCylinder(r,h,A.Vector(x,y,z),A.Vector(0,1,0))
def ring(ro,ri,z,h,x=0,y=0): return cyl(ro,z,h,x,y).cut(cyl(ri,z-.1,h+.2,x,y))
def fuse(*ss):
    s = ss[0]
    for t in ss[1:]: s = s.fuse(t)
    return s.removeSplitter()
def wedge(r, z, h, a0, a1, x=0, y=0):
    """Annular-ish sector used for the C arm: a disc sector from a0 to a1 deg."""
    seg = cyl(r, z, h, x, y)
    keep = []
    step = 15.0
    a = a0
    while a < a1 - 1e-9:
        b = min(a+step, a1)
        tri = Part.makePolygon([A.Vector(x,y,z),
                                A.Vector(x+2*r*math.cos(math.radians(a)), y+2*r*math.sin(math.radians(a)), z),
                                A.Vector(x+2*r*math.cos(math.radians(b)), y+2*r*math.sin(math.radians(b)), z),
                                A.Vector(x,y,z)])
        keep.append(Part.Face(tri).extrude(A.Vector(0,0,h)))
        a = b
    return seg.common(fuse(*keep))
def local(obj):
    s = obj.Shape.copy(); s.translate(-C0); return s
def assign(obj, s):
    assert s.isValid() and len(s.Solids)==1, obj.Name+' invalid/disconnected'
    w = s.copy(); w.translate(C0); obj.Shape = w
def prop(obj, name, value):
    if name not in obj.PropertiesList:
        obj.addProperty('App::PropertyString', name, 'HeadV03')
    setattr(obj, name, str(value))

# ------------------------------------------------ drop the v0.2 pose mirror
grp = doc.getObject('Presentation_180deg')
if grp:
    for o in list(grp.Group): doc.removeObject(o.Name)
    doc.removeObject(grp.Name)
for n in ['Pan_Belt_Path_Reference','Pan_Driven_Pulley_Envelope','Pan_Drive_Pulley_Envelope']:
    if doc.getObject(n): doc.removeObject(n)

# ------------------------------------------------------------- 2GT geometry
def toothed(n_teeth, z, h, y=0.0, bore=None, flange=True):
    """Pulley with cut 2GT-style grooves. Approximated profile - gate on coupon."""
    pd = n_teeth*PITCH/math.pi
    od = pd - 2*PLD
    ro = od/2.0
    rc = ro - TOOTH_DEPTH + GROOVE_R          # groove centre radius
    body = cyl(ro, z, h, 0, y)
    for i in range(n_teeth):
        a = 2*math.pi*i/n_teeth
        body = body.cut(cyl(GROOVE_R, z-0.1, h+0.2,
                            rc*math.cos(a), y + rc*math.sin(a)))
    if flange:
        body = fuse(body, ring(ro+1.2, ro-1.0, z-0.7, 0.7, 0, y),
                          ring(ro+1.2, ro-1.0, z+h,   0.7, 0, y))
    if bore:
        body = body.cut(cyl(bore, z-1.5, h+3.0, 0, y))
    return body, pd, od

PULLEY_Z, PULLEY_H = 155.2, BELT_WIDTH
driven, pd1, od1 = toothed(N_DRIVEN, PULLEY_Z+0.7, PULLEY_H, 0.0, bore=6.6)
drive,  pd2, od2 = toothed(N_DRIVE,  PULLEY_Z+0.7, PULLEY_H, SERVO_Y, bore=2.6)

report['drive'] = {
    'concept': 'step-up 2GT belt; SG90 works in its middle band',
    'teeth_driven': N_DRIVEN, 'teeth_drive': N_DRIVE,
    'ratio_head_per_servo_deg': round(RATIO, 4),
    'pitch_mm': PITCH, 'belt_teeth': BELT_TEETH, 'belt_pitch_length_mm': BELT_L,
    'belt_width_mm': BELT_WIDTH,
    'pitch_dia_driven_mm': round(pd1,3), 'pitch_dia_drive_mm': round(pd2,3),
    'shaft_spacing_mm': round(S,3),
    'servo_angle_deg_local': SERVO_ANG,
    'servo_centre_local_xy': [round(S*math.cos(math.radians(SERVO_ANG)),2),
                              round(S*math.sin(math.radians(SERVO_ANG)),2)],
    'head_travel_deg': list(HEAD_TRAVEL),
    'required_servo_travel_deg': round(SERVO_TRAVEL,2),
    'wrap_angle_small_pulley_deg': round(WRAP_SMALL,2),
    'teeth_engaged_small_pulley': round(N_DRIVE*WRAP_SMALL/360.0, 2),
}

# ------------------------------------------------- fixed neck, rebuilt
# Z stack (local): collar 104..119.5 | C-arm 114.5..120 | shoulder 119.5..121
#                  spindle 121..147 | bearings 121..128 and 137..144
# Bearing centres 124.5 / 140.5 -> 16 mm apart, was 11 mm, with no height change.
BRG_LO_Z, BRG_HI_Z = 121.0, 137.0
BRG_ID, BRG_OD, BRG_W = BEARING
SPINDLE_R = (BRG_ID - SPINDLE_CLR)/2.0
SEAT_R    = (BRG_OD + SEAT_CLR)/2.0
BRG_SPACING = (BRG_HI_Z + BRG_W/2) - (BRG_LO_Z + BRG_W/2)

collar = ring(14, 10.2, 104, 16)      # seats on the mast top rim at Z 120
lug = fuse(box(-18,-5,104.5,9,10,9), box(9,-5,104.5,9,10,9))
collar = fuse(collar, lug).cut(cyl(10.2, 103, 18))
for x in [-13.5, 13.5]:
    collar = collar.cut(cy(1.7, -6, 12, x, 109))
front = collar.common(box(-30,-30,100,60,29.7,25))     # removable clamp cap
rear  = collar.common(box(-30,.3,100,60,30,25))        # body half
rear  = fuse(rear, box(-3, 9.3, 106, 6, 2.4, 13.5))    # key into the mast index flat

# Servo carried FORWARD on a C arm that passes outboard of the rotor, below it.
# Arm clears the removable cap radially (inner R15 vs cap R14) everywhere except
# the rear sector, where a web drops to R10.2 to actually join the collar.
arm = wedge(26, 114.5, 5.5, 88, 247).cut(cyl(15, 114, 7))
web = wedge(26, 114.5, 5.5, 95, 170).cut(cyl(10.2, 114, 7))
arm = fuse(arm, web)
EARC = SERVO_Y - 3.1                                    # servo reversed on its pads
platform = box(-10, EARC-17.5, 137, 20, 35, 3)
platform = platform.cut(box(-6, SERVO_Y-14.5, 136, 12, 22.8, 5))
for y in [EARC-13.6, EARC+13.6]:
    platform = platform.cut(cyl(1.2, 136, 5, 0, y))
riser = fuse(box(-7, -31, 119, 14, 8.5, 21), box(-9, -46, 134, 18, 24, 6))
riser = riser.cut(box(-6, SERVO_Y-14.5, 133, 12, 22.8, 9))

# Shoulder is stepped so nothing reaches below the mast top rim at Z 120.
spindle = fuse(ring(11.5, 10.2, 119, 2.0).common(box(-30,.3,100,60,30,25)),
               ring(11.5, 6, 120, 1.0),
               ring(SPINDLE_R, 6, 120.8, 26.2))
spindle = spindle.cut(ring(11, 9.5, 144.5, 1.4))        # circlip groove

# No printed hard stops on the pan axis. A post at the travel limit has to sit
# at a radius the C arm does not reach, and a plastic lug driven into a plastic
# post is worse than the servo reaching its own internal limit. Travel is held
# by the servo end stops plus firmware limits; see validation.json.
for sh in [riser, platform]:
    sh.rotate(A.Vector(), A.Vector(0,0,1), DELTA)
neck = fuse(rear, arm, riser, platform, spindle)
neck = neck.cut(cyl(6, 103, 48))                        # keep the 12 mm cable bore
assign(doc.Neck_Main, neck)
prop(doc.Neck_Main,'RevisionChange',
     'Servo moved forward on a C arm; bearing seats widened to %.1f mm centres' % BRG_SPACING)
assign(doc.Neck_Clamp_Cap, front)

assign(doc.Pan_Bearing_Lower, ring(BRG_OD/2, BRG_ID/2, BRG_LO_Z, BRG_W))
assign(doc.Pan_Bearing_Upper, ring(BRG_OD/2, BRG_ID/2, BRG_HI_Z, BRG_W))
assign(doc.Pan_Inner_Spacer, ring(12, SPINDLE_R+0.075, BRG_LO_Z+BRG_W,
                                  BRG_HI_Z-BRG_LO_Z-BRG_W))
assign(doc.Pan_Circlip_Envelope, ring(12.4, 9.5, 144.6, 1.2))

# Rotor: outer races only. Retainer bore raised to clear the fixed inner race.
rotor = cyl(20.5, BRG_LO_Z, 23.0)
rotor = rotor.cut(cyl(SEAT_R, BRG_LO_Z-0.1, BRG_W+0.2))
rotor = rotor.cut(cyl(15.0, BRG_LO_Z+BRG_W, BRG_HI_Z-BRG_LO_Z-BRG_W))
rotor = rotor.cut(cyl(SEAT_R, BRG_HI_Z, BRG_W+0.2))
retainer = ring(20.5, OUTER_RACE_ID/2 + 0.5, 144, 3)
for ang in [45,135,225,315]:
    x = 18.3*math.cos(math.radians(ang)); y = 18.3*math.sin(math.radians(ang))
    rotor    = rotor.cut(cyl(.8, BRG_HI_Z, 8, x, y))
    retainer = retainer.cut(cyl(1.1, 143.5, 4, x, y))
assign(doc.Pan_Rotor, rotor)
assign(doc.Pan_Retainer_Crank, retainer)
doc.Pan_Retainer_Crank.Label = 'Pan bearing retainer'
prop(doc.Pan_Retainer_Crank,'RevisionChange',
     'Bore opened to %.1f mm so it bears on the outer race only' % (OUTER_RACE_ID+1))

# --------------------------------------------------- pulleys, belt, servo
def add(name, s, group, motion, status):
    obj = doc.getObject(name) or doc.addObject('Part::Feature', name)
    assign(obj, s)
    prop(obj,'MotionGroup',motion); prop(obj,'DesignStatus',status)
    prop(obj,'InterfaceVersion','GH44-v0.1 / belt180-v0.3')
    g = doc.getObject(group)
    if g and obj not in g.Group: g.addObject(obj)
    return obj

driven, pd1, od1 = toothed(N_DRIVEN, PULLEY_Z, PULLEY_H, 0.0, bore=None)
drive,  pd2, od2 = toothed(N_DRIVE,  PULLEY_Z, PULLEY_H, SERVO_Y,  bore=3.05)
drive.rotate(A.Vector(), A.Vector(0,0,1), DELTA)
add('Pan_Drive_Pulley', drive,'HardwareReferences','servo',
    'BUY: %dT 2GT pulley, %d mm belt width, bolted to the supplied SG90 horn' % (N_DRIVE, BELT_WIDTH))

# Belt band between the true external tangents of the two pitch circles.
r1, r2 = pd1/2.0, pd2/2.0
g = math.asin((r1-r2)/S)
def band(off):
    a, b = r1+off, r2+off
    pts = [A.Vector( a*math.cos(g),  a*math.sin(g), 0),
           A.Vector( b*math.cos(g), SERVO_Y + b*math.sin(g), 0),
           A.Vector(-b*math.cos(g), SERVO_Y + b*math.sin(g), 0),
           A.Vector(-a*math.cos(g),  a*math.sin(g), 0)]
    quad = Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(A.Vector(0,0,BELT_WIDTH))
    s = fuse(cyl(a,0,BELT_WIDTH), cyl(b,0,BELT_WIDTH,0,SERVO_Y), quad)
    s.translate(A.Vector(0,0,PULLEY_Z)); return s
belt = band(0.9).cut(band(-0.1))
belt.rotate(A.Vector(), A.Vector(0,0,1), DELTA)
add('Pan_Belt_Reference', belt,'CableReferences','belt',
    'BUY: 2GT closed loop, %d teeth / %d mm, %d mm wide' % (BELT_TEETH, BELT_L, BELT_WIDTH))

servo = fuse(box(-6,-8.3,0,12,22.8,17), box(-6,-13.15,17,12,32.5,2.5),
             box(-6,-8.3,19.5,12,22.8,8), cyl(3,27.5,2.7))
servo.rotate(A.Vector(), A.Vector(0,0,1), 180)
servo.translate(A.Vector(0, SERVO_Y, 123))
servo.rotate(A.Vector(), A.Vector(0,0,1), DELTA)
assign(doc.SG90_Pan_Reference, servo)
horn = doc.getObject('Pan_Horn_Reference')
if horn:
    h = cyl(9, 153.2, 2, 0, SERVO_Y)   # round horn under the pulley, not a long arm
    h.rotate(A.Vector(), A.Vector(0,0,1), DELTA)
    assign(horn, h)

# Pedestal carries the yoke and now the driven ring itself, so there is no
# slip-fit hub to key or fasten.
ped = fuse(ring(20.5,13,147,3), ring(14,6.5,149,5), ring(12,6.5,154,10),
           ring(20.5,6.5,164,4), box(-25,-30,164,50,30,4))
ped = fuse(ped, driven)
ped = ped.cut(cyl(6.5,146,23)).cut(cyl(13,146.9,2.1))
for x in [-20,20]: ped = ped.cut(cyl(1.7,163,6,x,-25))
for ang in [45,135,225,315]:
    x = 18.3*math.cos(math.radians(ang)); y = 18.3*math.sin(math.radians(ang))
    ped = ped.cut(cyl(1.1,146.8,3.4,x,y))
assign(doc.Pan_Raised_Pedestal, ped)
prop(doc.Pan_Raised_Pedestal,'RevisionChange',
     'Driven %dT 2GT ring is now integral, not a separate hub' % N_DRIVEN)

# ------------------------------------------------------------- validation
active = ['Neck_Main','Neck_Clamp_Cap','Pan_Bearing_Lower','Pan_Bearing_Upper',
 'Pan_Inner_Spacer','Pan_Circlip_Envelope','Pan_Rotor','Pan_Retainer_Crank',
 'Pan_Raised_Pedestal','Pan_Drive_Pulley','Pan_Belt_Reference',
 'SG90_Pan_Reference','Pan_Horn_Reference','Tilt_Yoke','SG90_Tilt_Reference',
 'Tilt_Horn_Reference','Tilt_Idler_Bushing','GH44_Tilt_Receiver','GH44_Dual_Carrier',
 'Dual_ToF_Envelope','Dual_Radar_Envelope','Rear_Display_Frame','ST7789_Board_62x29x3_2']
# Motion groups, corrected: the servo BODY is bolted to the fixed neck and does
# not turn. v0.2 rotated it with the drive, which flattered the clearance check.
for n, m in [('Neck_Main','fixed'),('Neck_Clamp_Cap','fixed'),
             ('SG90_Pan_Reference','fixed'),('Pan_Bearing_Lower','fixed'),
             ('Pan_Bearing_Upper','fixed'),('Pan_Inner_Spacer','fixed'),
             ('Pan_Circlip_Envelope','fixed'),('Pan_Rotor','pan'),
             ('Pan_Retainer_Crank','pan'),('Pan_Raised_Pedestal','pan'),
             ('Pan_Drive_Pulley','servo'),('Pan_Horn_Reference','servo'),
             ('Pan_Belt_Reference','belt')]:
    o = doc.getObject(n)
    if o: prop(o,'MotionGroup',m)

parts = []
for n in active:
    o = doc.getObject(n)
    if o is None: raise RuntimeError('missing active part '+n)
    parts.append({'name':n,'obj':o,'shape':local(o),'motion':o.MotionGroup})
    report['parts'].append({'name':n,'volume_mm3':round(o.Shape.Volume,2),
        'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'motion':o.MotionGroup})

PAN_SAMPLES = [float(a) for a in range(int(HEAD_TRAVEL[0]), int(HEAD_TRAVEL[1])+1, 5)]
def posed(p, pan=0.0, tilt=0.0):
    s = p['shape'].copy()
    if p['motion']=='tilt': s.rotate(T, A.Vector(1,0,0), tilt)
    if p['motion'] in ['pan','tilt']: s.rotate(A.Vector(), A.Vector(0,0,1), pan)
    if p['motion']=='belt':  s.rotate(A.Vector(), A.Vector(0,0,1), 0)
    if p['motion']=='servo': s.rotate(SERVO_POS, A.Vector(0,0,1), -pan/RATIO)
    return s
def overlap(a,b):
    if not a.BoundBox.intersect(b.BoundBox): return 0.
    return a.common(b).Volume
def note(a,b,sa,sb,pan,tilt,kind):
    v = overlap(sa,sb)
    if v > .05:
        report['collisions'].append({'a':a,'b':b,'pan':pan,'tilt':tilt,
                                     'mm3':round(v,4),'kind':kind})

tests = 0
for a,b in itertools.combinations(parts,2):
    if a['motion']==b['motion']: poses=[(0.,0.)]
    elif a['motion'] in ['pan','tilt'] and b['motion'] in ['pan','tilt']:
        poses=[(0.,t) for t in [-25.,0.,25.]]
    else:
        poses=[(p,t) for p in PAN_SAMPLES
               for t in ([-25.,0.,25.] if 'tilt' in [a['motion'],b['motion']] else [0.])]
    for pan,tilt in poses:
        note(a['name'],b['name'],posed(a,pan,tilt),posed(b,pan,tilt),pan,tilt,'head'); tests+=1
report['checks']['head_pair_pose_tests'] = tests

robot = []
for n in ['MastTube','MastBase','UpperDeck','S3Board','Breadboard',
          'DriverMountLeft','DriverMountRight','AntennaPost','ChassisDeck',
          'SideRailLeft','SideRailRight','PowerShield']:
    o = doc.getObject(n)
    if o: robot.append((n, local(o)))
report['checks']['robot_solids_compared'] = [n for n,_ in robot]
tests = 0
for pan in PAN_SAMPLES:
    for tilt in [-25.,0.,25.]:
        for p in parts:
            s = posed(p,pan,tilt)
            for n,r in robot:
                note(p['name'],n,s,r,pan,tilt,'robot'); tests+=1
report['checks']['robot_pair_pose_tests'] = tests

# Cable bore must stay clear all the way up the fixed neck and rotating stack.
report['checks']['cable_passage_11_9mm_overlap_mm3'] = round(sum(
    overlap(cyl(5.95,105,63), p['shape']) for p in parts), 4)
report['checks']['all_active_parts_single_valid_solid'] = all(
    p['shape'].isValid() and len(p['shape'].Solids)==1 for p in parts)
report['checks']['bearing_centre_spacing_mm'] = BRG_SPACING
report['checks']['rotor_seat_bore_mm'] = round(SEAT_R*2,3)
report['checks']['spindle_dia_mm'] = round(SPINDLE_R*2,3)
report['checks']['retainer_bore_mm'] = round(OUTER_RACE_ID+1,3)

# Rear overhang: the thing v0.2 lost most on.
rear_edge = 140.0 - C0.y
report['checks']['rear_overhang_mm'] = {}
for n in ['Neck_Main','SG90_Pan_Reference','Pan_Drive_Pulley','Pan_Belt_Reference']:
    p = next(x for x in parts if x['name']==n)
    ymax = max(posed(p,pan,0.).BoundBox.YMax for pan in PAN_SAMPLES)
    report['checks']['rear_overhang_mm'][n] = round(ymax-rear_edge, 2)

# Nominal 60 x 60 deg ToF frustum, now swept across the whole pan range.
def square(y, half, cx):
    vs=[A.Vector(cx+x, y, T.z+v) for x,v in
        [(-half,-half),(half,-half),(half,half),(-half,half)]]
    return Part.makePolygon(vs+[vs[0]])
frustum = Part.makeLoft([square(-71,.5,-17), square(-221,.5+150*math.tan(math.radians(30)),-17)], True)
report['fov_intersections'] = []
for pan in PAN_SAMPLES:
    for tilt in [-25.,0.,25.]:
        f = frustum.copy()
        f.rotate(T, A.Vector(1,0,0), tilt)
        f.rotate(A.Vector(), A.Vector(0,0,1), pan)
        for n,s in robot:
            v = overlap(f,s)
            if v>.05: report['fov_intersections'].append(
                {'pan':pan,'tilt':tilt,'object':n,'mm3':round(v,2)})
        for p in parts:
            if p['motion'] in ['tilt']: continue
            v = overlap(f, posed(p,pan,tilt))
            if v>.05: report['fov_intersections'].append(
                {'pan':pan,'tilt':tilt,'object':p['name'],'mm3':round(v,2)})

# ------------------------------------------------------------ belt coupon
# One question: do printed 2GT grooves mesh with a real 2GT belt?
# 60 degree arc of the driven ring, printed axis-vertical like the real part.
disc, _, _ = toothed(N_DRIVEN, 0.0, BELT_WIDTH, 0.0, bore=None, flange=False)
coupon = disc.common(wedge(30, -1, BELT_WIDTH+2, -30, 30)).cut(cyl(12, -1, BELT_WIDTH+2))
assert coupon.isValid() and len(coupon.Solids)==1, 'coupon'
report['checks']['coupon_volume_mm3'] = round(coupon.Volume, 1)

# ------------------------------------------------------------ STL export
def stl(shape, name, note):
    s = shape.copy()
    s.translate(A.Vector(0,0,-s.BoundBox.ZMin))
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01,
                               AngularDeflection=0.0872665, Relative=False)
    m.write(str(OUT/'stl'/(name+'.stl')))
    b = s.BoundBox
    report.setdefault('stl',[]).append(
        {'file':name+'.stl','size_mm':[round(b.XLength,1),round(b.YLength,1),
         round(b.ZLength,1)],'volume_cm3':round(shape.Volume/1000.,2),'orientation':note})

stl(coupon,'Gladiator_HeadCoupon_BeltMesh_60deg',
    'PRINT READY - flat bottom on the bed, teeth outward, axis vertical, no support')
for n, note_ in [
    ('Neck_Main','as-modelled, mast axis vertical; C arm and servo platform need support - orientation NOT validated'),
    ('Neck_Clamp_Cap','as-modelled; lay on the split face before slicing - orientation NOT validated'),
    ('Pan_Rotor','as-modelled, axis vertical; bearing seats print as true bores - orientation NOT validated'),
    ('Pan_Retainer_Crank','as-modelled, flat - orientation NOT validated'),
    ('Pan_Raised_Pedestal','as-modelled, axis vertical so the 2GT teeth print like the coupon - orientation NOT validated'),
    ('Tilt_Yoke','inherited from v0.2 - orientation NOT validated'),
    ('GH44_Tilt_Receiver','inherited from v0.2 - orientation NOT validated'),
    ('GH44_Dual_Carrier','inherited from v0.2 - orientation NOT validated'),
    ('Rear_Display_Frame','inherited from v0.2 - orientation NOT validated')]:
    p = next(x for x in parts if x['name']==n)
    stl(p['shape'], 'Gladiator_Head_'+n, note_)

# ------------------------------------------------------------ write it out
report['limitations'] = [
 'Ratio and travel are parameters. RATIO=%.3f assumes the SG90 delivers %.0f deg '
 'of usable, repeatable travel. That has never been measured on Jim units.' % (RATIO, SERVO_TRAVEL),
 '2GT groove profile is an approximation (groove r=%.2f, depth %.2f). The mesh '
 'coupon gates it. Do not print the pedestal before the coupon passes.' % (GROOVE_R, TOOTH_DEPTH),
 'Bearing seat %.2f mm and spindle %.2f mm are nominal clearances, not print-verified. '
 'They need their own fit coupon once the bearings arrive.' % (SEAT_CLR, SPINDLE_CLR),
 'Belt tension, tensioner and the pedestal-to-belt preload path are not designed.',
 'Mast index flat is still the inherited 0.9 mm feature; the deeper dimple/grub '
 'proposal would be a change to the real master and was NOT made here.',
 'Harness is still undesigned. About 14 conductors must pass the 12 mm bore and '
 'twist over %.0f deg of pan.' % (HEAD_TRAVEL[1]-HEAD_TRAVEL[0]),
 'Screen active window, mount holes and connector exit remain unmeasured.',
 'Sampled rigid-solid checks at %d deg pan steps do not prove continuous clearance.' % 5,
 'No load, stiffness, creep or payload rating is claimed.',
]
cfg = {'source': str(SOURCE), 'derived_from': 'v02-screen-180',
       'drive': report['drive'], 'head_travel_deg': list(HEAD_TRAVEL),
       'bearing': {'designation_hint':'6804 / 20x32x7', 'centres_mm': BRG_SPACING,
                   'seat_bore_mm': round(SEAT_R*2,3), 'spindle_dia_mm': round(SPINDLE_R*2,3),
                   'retainer_bore_mm': OUTER_RACE_ID+1},
       'tilt_axis_z': T.z, 'manufacturing_release': False,
       'print_ready': ['Gladiator_HeadCoupon_BeltMesh_60deg.stl']}
(OUT/'head-config.json').write_text(json.dumps(cfg, indent=2)+'\n')

doc.recompute()
doc.saveAs(str(OUT/'Gladiator_Head_v03_Belt.FCStd'))
Part.export([p['obj'] for p in parts], str(OUT/'Gladiator_Head_v03_Belt.step'))

report['checks']['source_and_master_unchanged'] = all(digest(Path(p))==h for p,h in before.items())
report['checks']['sampled_geometry_pass'] = (
    not report['collisions'] and not report['fov_intersections']
    and report['checks']['all_active_parts_single_valid_solid']
    and report['checks']['cable_passage_11_9mm_overlap_mm3'] < .01
    and report['checks']['source_and_master_unchanged'])
(OUT/'validation.json').write_text(json.dumps(report, indent=2)+'\n')

summary = {'out': str(OUT), 'drive': report['drive'],
           'checks': report['checks'],
           'collisions': report['collisions'][:12],
           'collision_count': len(report['collisions']),
           'fov': report['fov_intersections'][:12],
           'fov_count': len(report['fov_intersections']),
           'stl': report.get('stl', [])}
Path('/tmp/v03_summary.json').write_text(json.dumps(summary, indent=2))
A.closeDocument(doc.Name)
