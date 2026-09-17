"""Separate comparison candidate derived from v0.1; run with CAD-server Python.

Keeps the original source/master byte-for-byte. Timing drive is a pitch-envelope
concept, not printable tooth geometry. Screen is the measured board envelope.
"""
import sys, json, math, hashlib, itertools
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod'])
import FreeCAD as A
import Part, PartDesign, Sketcher

ROOT = Path('/home/buralien/projects/gladiator-cad')
SOURCE = ROOT/'cad/head/v01/Gladiator_Head_v01.FCStd'
MASTER = ROOT/'cad/master/Gladiator_Master.FCStd'
OUT = ROOT/'cad/head/v02-screen-180'
OUT.mkdir(parents=True, exist_ok=True)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
before = {str(p): digest(p) for p in [SOURCE, MASTER]}
doc = A.openDocument(str(SOURCE))
doc.Label = 'Gladiator v0.2 - rear ST7789 screen / 180 degree pan'
C = A.Vector(39.5, 113, 0)
LIFT = 28.0
T = A.Vector(0, -26, 177 + LIFT)
S = 42.0
report = {'source_sha256': before, 'release': 'COMPARISON CAD - NOT A PRINT RELEASE',
          'parts': [], 'collisions': [], 'checks': {}, 'limitations': [
    'Timing pulleys and belt are pitch/clearance envelopes, not teeth or a sourced belt.',
    '1:1 drive needs 180 degrees usable actuator travel. Actual SG90 travel/load untested.',
    '0 to 180 degree switching range; previous +/-40 degree travel scan not retained.',
    'Display is confirmed whole-board 62 x 29 x 3.2 mm, not the active screen opening.',
    'Display retention, active window, connectors, harness loop, mass and torque pending.',
    'SG90 horn attachment is inherited provisional geometry; final pulley attachment pending.',
    'Existing v0.1 bearing, sensor retention and print-fit limitations still apply.',
    'Sampled rigid-solid checks do not establish continuous or cable clearance.',
]}
def box(x,y,z,dx,dy,dz): return Part.makeBox(dx,dy,dz,A.Vector(x,y,z))
def cyl(r,z,h,x=0,y=0): return Part.makeCylinder(r,h,A.Vector(x,y,z))
def cy(r,y,h,x,z): return Part.makeCylinder(r,h,A.Vector(x,y,z),A.Vector(0,1,0))
def ring(ro,ri,z,h,x=0,y=0): return cyl(ro,z,h,x,y).cut(cyl(ri,z-.1,h+.2,x,y))
def fuse(*ss):
    s=ss[0]
    for t in ss[1:]: s=s.fuse(t)
    return s.removeSplitter()
def local(obj):
    s=obj.Shape.copy(); s.translate(-C); return s
def assign(obj, s):
    assert s.isValid() and len(s.Solids)==1, obj.Name
    w=s.copy(); w.translate(C); obj.Shape=w
def prop(obj, name, value):
    if name not in obj.PropertiesList: obj.addProperty('App::PropertyString',name,'Screen180')
    setattr(obj,name,str(value))
def add(name,s,group,motion,status):
    obj=doc.addObject('Part::Feature',name); assign(obj,s)
    prop(obj,'MotionGroup',motion); prop(obj,'DesignStatus',status)
    prop(obj,'InterfaceVersion','GH44-v0.1 / screen180-v0.2')
    doc.getObject(group).addObject(obj)
    return obj

# Remove only obsolete drive/guide objects in the independent loaded document.
for name in ['Pan_Parallel_Link','Pan_Horn_Adapter','Harness_Route_Guide','ToF_Field_Reference']:
    doc.removeObject(name)

# Keep all original tilt/carrier solids, shifted upward to clear the pan drive.
for obj in list(doc.Objects):
    if not hasattr(obj,'MotionGroup'): continue
    lift = obj.MotionGroup=='tilt' or obj.Name in ['Tilt_Yoke','SG90_Tilt_Reference','Tilt_Idler_Bushing']
    if lift:
        s=local(obj); s.translate(A.Vector(0,0,LIFT)); assign(obj,s)
        prop(obj,'RevisionChange','Original geometry raised 28 mm for pan-drive clearance')

# Preserve collar, mast key, spindle, and the existing SG90 mounting platform.
# Trim the two old narrow-range stop arms from the fixed neck.
neck=local(doc.Neck_Main)
for angle in [35,145]:
    trim=box(14.05,-3.1,119.9,15,6.2,34)
    trim.rotate(A.Vector(),A.Vector(0,0,1),angle)
    neck=neck.cut(trim)
# Stops contact the rotor lug just outside the commanded 0..180 range.
for angle in [-15,195]:
    a=math.radians(angle)
    arm=box(10,-3,120,14,6,4); arm.rotate(A.Vector(),A.Vector(0,0,1),angle)
    neck=fuse(neck,arm,cyl(2,123,31,24*math.cos(a),24*math.sin(a)))
assign(doc.Neck_Main,neck)
prop(doc.Neck_Main,'RevisionChange','Original collar/spindle/servo mount; revised stop posts')

# Retain original bearing seats and screw pattern, remove old crank and front lug.
rotor=fuse(ring(20.5,16.1,125.7,18.3),ring(20.5,15,133,4))
retainer=ring(20.5,13,144,3)
for angle in [45,135,225,315]:
    x=18.3*math.cos(math.radians(angle)); y=18.3*math.sin(math.radians(angle))
    rotor=rotor.cut(cyl(.8,137,8,x,y))
    retainer=retainer.cut(cyl(1.1,143.5,4,x,y))
assign(doc.Pan_Rotor,rotor)
assign(doc.Pan_Retainer_Crank,retainer)
doc.Pan_Retainer_Crank.Label='Pan bearing retainer - original screw pattern'

# Central pedestal carries the original yoke above the fixed servo and belt.
# A lower 26 mm cavity clears the stationary spindle end; upper bore is 13 mm.
pedestal=fuse(ring(20.5,13,147,3),ring(14,6.5,149,5),ring(12,6.5,154,10),
              ring(20.5,6.5,164,4),box(-25,-30,164,50,30,4),
              box(18,-2,149,6,4,4),cyl(2,149,4,24,0))
pedestal=pedestal.cut(cyl(6.5,146,23)).cut(cyl(13,146.9,2.1))
for x in [-20,20]: pedestal=pedestal.cut(cyl(1.7,163,6,x,-25))
for angle in [45,135,225,315]:
    x=18.3*math.cos(math.radians(angle)); y=18.3*math.sin(math.radians(angle))
    pedestal=pedestal.cut(cyl(1.1,146.8,3.4,x,y))
add('Pan_Raised_Pedestal',pedestal,'PanAssembly','pan',
    'Concept load path, M2 retainer fasteners/M3 yoke screws; verify lengths and strength')

# Equal 50-tooth, 2 mm pitch pulley envelope: pitch radius 50/pi, centers 42 mm.
# 184 mm theoretical pitch loop length. No claim of commercial availability.
pitch_radius=50/math.pi
def pulley(y,bore):
    return fuse(ring(18,bore,155.2,.7,0,y),
                ring(pitch_radius,bore,155.9,6,0,y),
                ring(18,bore,161.9,.7,0,y))
# Driven pulley fits around the pedestal; hub attachment details remain pending.
add('Pan_Driven_Pulley_Envelope',pulley(0,12.05),'HardwareReferences','pan',
    '50T GT2 pitch envelope; hub fastening and teeth not modeled')
add('Pan_Drive_Pulley_Envelope',pulley(S,3.05),'HardwareReferences','servo',
    '50T GT2 pitch envelope; supplied SG90 horn attachment to be completed')
# A thin reference at the pitch path, kept hidden in the main view. It is not
# checked against the pulley teeth or flange contact geometry.
def capsule(r,z,h):
    return fuse(cyl(r,z,h),cyl(r,z,h,0,S),box(-r,0,z,2*r,S,h))
belt=capsule(pitch_radius+.5,156.4,5).cut(capsule(pitch_radius,156.3,5.2))
add('Pan_Belt_Path_Reference',belt,'CableReferences','belt',
    '184 mm pitch loop guide only; tooth engagement, tension and belt sourcing pending')

# Display carrier bolts to the existing 70 mm dual carrier with four new M2
# clearance holes. The original GH44 mating features remain unchanged.
carrier=local(doc.GH44_Dual_Carrier)
for x in [-32,32]:
    for dz in [-18,18]: carrier=carrier.cut(cy(1.2,-59,9,x,T.z+dz))
assign(doc.GH44_Dual_Carrier,carrier)
prop(doc.GH44_Dual_Carrier,'RevisionChange','Original carrier plus four 2.4 mm display-frame holes')
frame=box(-38,-.5,T.z-22,76,5,44).cut(box(-31.3,-1,T.z-14.8,62.6,7,29.6))
for side in [-1,1]:
    x=35 if side>0 else -38
    for dz in [-20,16]: frame=fuse(frame,box(x,-52,T.z+dz,3,52,4))
    tx=27 if side>0 else -38
    for dz in [-21,14]: frame=fuse(frame,box(tx,-55,T.z+dz,11,3,7))
for x in [-32,32]:
    for dz in [-18,18]: frame=frame.cut(cy(1.2,-56,5,x,T.z+dz))
add('Rear_Display_Frame',frame,'TiltAssembly','tilt',
    'Removable frame layout; full-board opening is provisional, module retention pending')
screen=add('ST7789_Board_62x29x3_2',box(-31,0,T.z-14.5,62,3.2,29),
    'HardwareReferences','tilt','Measured board envelope; active window and connector unknown')
prop(screen,'MeasuredSize','62 x 29 x 3.2 mm, Jim, 2026-09-17')

active_names=['Neck_Main','Neck_Clamp_Cap','Pan_Bearing_Lower','Pan_Bearing_Upper',
 'Pan_Inner_Spacer','Pan_Circlip_Envelope','Pan_Rotor','Pan_Retainer_Crank',
 'Pan_Raised_Pedestal','Pan_Driven_Pulley_Envelope','Pan_Drive_Pulley_Envelope',
 'SG90_Pan_Reference','Pan_Horn_Reference','Tilt_Yoke','SG90_Tilt_Reference',
 'Tilt_Horn_Reference','Tilt_Idler_Bushing','GH44_Tilt_Receiver','GH44_Dual_Carrier',
 'Dual_ToF_Envelope','Dual_Radar_Envelope','Rear_Display_Frame','ST7789_Board_62x29x3_2']
parts=[]
for name in active_names:
    obj=doc.getObject(name)
    parts.append({'name':name,'obj':obj,'shape':local(obj),'motion':obj.MotionGroup})
    report['parts'].append({'name':name,'volume_mm3':obj.Shape.Volume,
       'valid':obj.Shape.isValid(),'solids':len(obj.Shape.Solids),'motion':obj.MotionGroup})
def posed(p,pan=0,tilt=0):
    s=p['shape'].copy()
    if p['motion']=='tilt': s.rotate(T,A.Vector(1,0,0),tilt)
    if p['motion'] in ['pan','tilt']: s.rotate(A.Vector(),A.Vector(0,0,1),pan)
    if p['motion']=='servo': s.rotate(A.Vector(0,S,0),A.Vector(0,0,1),pan)
    return s
def overlap(a,b):
    if not a.BoundBox.intersect(b.BoundBox): return 0.
    return a.common(b).Volume
def collision(a,b,sa,sb,pan,tilt,kind):
    vol=overlap(sa,sb)
    if vol>.05: report['collisions'].append({'a':a,'b':b,'pan':pan,'tilt':tilt,'mm3':round(vol,4),'kind':kind})

# Same-motion fit once; relative tilt at three samples; full pan against fixed
# neck/hardware at 10 degree intervals, including both intended endpoints.
tests=0
for a,b in itertools.combinations(parts,2):
    if a['motion']==b['motion']:
        poses=[(0,0)]
    elif a['motion'] in ['pan','tilt'] and b['motion'] in ['pan','tilt']:
        poses=[(0,t) for t in [-25,0,25]]
    else:
        poses=[(p,t) for p in range(0,181,10) for t in ([-25,0,25] if 'tilt' in [a['motion'],b['motion']] else [0])]
    for pan,tilt in poses:
        collision(a['name'],b['name'],posed(a,pan,tilt),posed(b,pan,tilt),pan,tilt,'head')
        tests+=1
report['checks']['head_pair_pose_tests']=tests
robot=[]
for name in ['MastTube','MastBase','UpperDeck','S3Board','Breadboard','DriverMountLeft','DriverMountRight','AntennaPost']:
    obj=doc.getObject(name)
    if obj: robot.append((name,local(obj)))
tests=0
for pan in range(0,181,10):
    for tilt in [-25,0,25]:
        for p in parts:
            s=posed(p,pan,tilt)
            for name,r in robot:
                collision(p['name'],name,s,r,pan,tilt,'robot'); tests+=1
report['checks']['robot_pair_pose_tests']=tests
report['checks']['mast_neck_pedestal_11_9mm_passage_overlap_mm3']=sum(
    overlap(cyl(5.95,105,64),p['shape']) for p in parts)
report['checks']['all_active_parts_single_valid_solid']=all(p['shape'].isValid() and len(p['shape'].Solids)==1 for p in parts)
report['checks']['display_board_dimensions_mm']=[screen.Shape.BoundBox.XLength,screen.Shape.BoundBox.ZLength,screen.Shape.BoundBox.YLength]
report['checks']['theoretical_stop_contact_deg']=[-15+math.degrees(2*math.asin(4/48)),195-math.degrees(2*math.asin(4/48))]
report['checks']['stop_overlap_samples_mm3']={}
ped=next(p for p in parts if p['name']=='Pan_Raised_Pedestal')
for pan in [-6,0,180,186]:
    report['checks']['stop_overlap_samples_mm3'][str(pan)]=overlap(posed(ped,pan,0),neck)

# Nominal forward ToF field at travel pose only. Screen pose is parked.
def square(y,half):
    vs=[A.Vector(-17+x,y,T.z+v) for x,v in [(-half,-half),(half,-half),(half,half),(-half,half)]]
    return Part.makePolygon(vs+[vs[0]])
frustum=Part.makeLoft([square(-71,.5),square(-221,.5+150*math.tan(math.radians(30)))],True)
report['fov_intersections']=[]
for tilt in [-25,0,25]:
    f=frustum.copy(); f.rotate(T,A.Vector(1,0,0),tilt)
    for name,s in robot+[(p['name'],posed(p,0,tilt)) for p in parts]:
        v=overlap(f,s)
        if v>.05: report['fov_intersections'].append({'tilt':tilt,'object':name,'mm3':round(v,4)})

# Store a second full assembly pose as a hidden group, so both endpoints can be
# inspected inside a single second file without altering the original candidate.
posegroup=doc.addObject('App::DocumentObjectGroup','Presentation_180deg')
posegroup.Label='ALTERNATE POSE - screen forward 180 deg (hide main head first)'
for p in parts:
    o=doc.addObject('Part::Feature','ScreenPose_'+p['name'])
    assign(o,posed(p,180,0)); posegroup.addObject(o)
    prop(o,'SourcePart',p['name'])
    prop(o,'DesignStatus','Alternate pose reference; same physical parts, not additional hardware')
meta=doc.addObject('App::FeaturePython','Screen180_Design_Notes')
prop(meta,'DisplayEnvelope','62 x 29 x 3.2 mm confirmed whole board')
prop(meta,'PanPoses','0 deg sensors forward; 180 deg screen forward; reverse to unwind')
prop(meta,'Preserved','Original mast, collar interface, bearing seats, GH44 interface, tilt geometry, sensors')
prop(meta,'Changes','28 mm raised tilt assembly; 1:1 belt-drive envelopes; revised stops; rear screen frame')
prop(meta,'Release','Comparison candidate only; screen retention and pulley/horn hardware unresolved')

# Geometry for deterministic local previews (no image synthesis).
colors={
 'Rear_Display_Frame':(.90,.56,.22), 'ST7789_Board_62x29x3_2':(.10,.17,.22),
 'GH44_Dual_Carrier':(.90,.56,.22)}
mesh=[]
for p in parts:
    name=p['name']
    color=colors.get(name,(.22,.34,.40) if p['motion']=='fixed' else (.18,.56,.60))
    if 'Reference' in name or 'Envelope' in name: color=(.25,.35,.72)
    if any(s in name for s in ['Bearing','Spacer','Circlip','Bushing','Horn']): color=(.65,.67,.70)
    vs,fs=p['shape'].tessellate(.35)
    mesh.append({'name':name,'color':color,'motion':p['motion'],
       'vertices':[[v.x,v.y,v.z] for v in vs],'faces':fs})
for name,s in robot:
    vs,fs=s.tessellate(.7)
    mesh.append({'name':name,'color':(.56,.59,.62),'motion':'fixed','context':True,
       'vertices':[[v.x,v.y,v.z] for v in vs],'faces':fs})
(OUT/'head-preview-mesh.json').write_text(json.dumps(mesh,separators=(',',':')))
config={'source':str(SOURCE),'display_mm':[62,29,3.2],'display_orientation':'landscape',
 'pan_operating_deg':[0,180],'tilt_review_deg':[-25,25],'tilt_axis_z':T.z,
 'tilt_raise_mm':LIFT,'display_frame_outer_mm':[76,44],
 'drive':'1:1 timing belt pitch envelopes','pulley_teeth_each':50,'pitch_mm':2,
 'shaft_spacing_mm':S,'theoretical_pitch_loop_mm':184,'manufacturing_release':False}
(OUT/'head-config.json').write_text(json.dumps(config,indent=2)+'\n')
doc.recompute()
doc.saveAs(str(OUT/'Gladiator_Head_v02_Screen180.FCStd'))
Part.export([p['obj'] for p in parts],str(OUT/'Gladiator_Head_v02_Screen180.step'))
Part.export(list(posegroup.Group),str(OUT/'Gladiator_Head_v02_Screen180_Presented.step'))
report['checks']['source_and_master_unchanged']=all(digest(Path(p))==h for p,h in before.items())
report['checks']['sampled_geometry_pass']=(not report['collisions'] and not report['fov_intersections']
    and report['checks']['all_active_parts_single_valid_solid']
    and report['checks']['mast_neck_pedestal_11_9mm_passage_overlap_mm3']<.01
    and report['checks']['source_and_master_unchanged'])
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'out':str(OUT),'collisions':report['collisions'],'fov':report['fov_intersections'],'checks':report['checks']},indent=2),flush=True)
A.closeDocument(doc.Name)
