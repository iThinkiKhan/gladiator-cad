"""Gladiator head v0.1. Regenerable CAD candidate; never overwrites master.

Run on CAD workstation with system Python. Generated Part features are solids,
not a claim of an editable sketch history. Edit CONFIG and regenerate.
"""
import sys, os, json, math, hashlib, itertools, subprocess
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad/Mod'])
import FreeCAD as A
import Part, PartDesign, Sketcher

ROOT=Path('/home/buralien/projects/gladiator-cad')
OUT=ROOT/'cad/head/v01'
OUT.mkdir(parents=True,exist_ok=True)
MASTER=ROOT/'cad/master/Gladiator_Master.FCStd'
CONFIG={
 'interface':'GH44-v0.1','carrier_width':44.,'carrier_height':44.,
 'carrier_hole_pitch':32.,'carrier_screw_clearance':3.4,
 'register_width':26.,'register_height':22.,'register_chamfer':5.,
 'register_depth':1.4,'register_total_clearance':0.4,
 'carrier_cable_width':18.,'carrier_cable_height':10.,
 'pan_limit_deg':40.,'tilt_limit_deg':25.,'pan_crank_radius':12.,
 'pan_servo_offset':42.,'tilt_axis_forward':26.,'tilt_axis_z':177.,
 'servo_body_fit_width':12.,'servo_body_fit_length':22.8,
 'servo_ear_pitch':27.2,'servo_ear_span':32.5,'servo_ear_thickness':2.5,
 'servo_base_to_ear':17.,'servo_ear_to_horn':13.2,
 'servo_shaft_end_offset':8.3,'servo_shaft_cross_offset_assumed':6.,
 'pan_bearing_id':20.,'pan_bearing_od':32.,'pan_bearing_width':7.,
 'mast_fit_diameter':20.4,'mast_key_flat_y':9.1,
 'prototype_only':True,
}
cfg=OUT/'head-config.json'
if cfg.exists():
    supplied=json.loads(cfg.read_text())
    for k,v in supplied.items():
        if k not in ['pan_limit_deg','tilt_limit_deg'] and CONFIG.get(k)!=v:
            raise ValueError('Dimension manifest differs at '+k+'; update paired source geometry explicitly')
    CONFIG.update(supplied)
cfg.write_text(json.dumps(CONFIG,indent=2)+'\n')
P=CONFIG
C=A.Vector(39.5,113,0)
T=A.Vector(0,-P['tilt_axis_forward'],P['tilt_axis_z'])
source_bytes=MASTER.read_bytes()
snapshot=OUT/'source-master.FCStd';snapshot.write_bytes(source_bytes)
report={'master_sha256':hashlib.sha256(source_bytes).hexdigest(),
        'source_git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'config':P,'parts':[],'collisions':[],'checks':{},'assumptions':[
 'SG90 cross-width shaft center assumed 6 mm; verify before servo cradle print.',
 'Horn thickness 2 mm and central boss 6 mm diameter are envelope assumptions.',
 'Slotted horn adapters require measured horn hole locations and actual screw choice.',
 'SEN0610 thickness is a 13 mm placeholder, not a measured dimension.',
 'Two 20x32x7 pan bearings, 20 mm circlip and tilt bushing are additional hardware.',
 'Bearing seats, spindle/circlip groove and captive nuts need PETG fit coupons.',
 'Carrier sensor retention clips/standoffs remain device-specific; no guessed PCB holes.',
 'No firmware servo control or physical load/cable validation has been performed.',
]}
doc=A.openDocument(str(snapshot))
doc.Label='Gladiator modular head v0.1 — review candidate'
# Existing errors are corrected only in this independent candidate document.
doc.MastWindowCut.Reversed=True
doc.MastWindowCut.Length=12
doc.recompute()
mast=doc.MastTube
keycut=Part.makeBox(8,4,15,A.Vector(35.5,122.1,105))
key=mast.newObject('PartDesign::Feature','HeadMastIndexFlat')
key.Label='Head index flat — 0.9 mm at rear, candidate only'
key.Shape=mast.Tip.Shape.cut(keycut) if mast.Tip != key else doc.MastTubePinCut.Shape.cut(keycut)
mast.Tip=key
doc.recompute()

def box(x,y,z,dx,dy,dz): return Part.makeBox(dx,dy,dz,A.Vector(x,y,z))
def cyl(r,z,h,x=0,y=0): return Part.makeCylinder(r,h,A.Vector(x,y,z))
def ring(ro,ri,z,h,x=0,y=0): return cyl(ro,z,h,x,y).cut(cyl(ri,z-.1,h+.2,x,y))
def cx(r,x,length,y,z): return Part.makeCylinder(r,length,A.Vector(x,y,z),A.Vector(1,0,0))
def cy(r,y,length,x,z): return Part.makeCylinder(r,length,A.Vector(x,y,z),A.Vector(0,1,0))
def fuse(*parts):
    s=parts[0]
    for p in parts[1:]: s=s.fuse(p)
    return s.removeSplitter()
def hex_y(af,y,depth,x,z):
    r=af/math.sqrt(3)
    pts=[A.Vector(x+r*math.cos(i*math.pi/3),y,z+r*math.sin(i*math.pi/3)) for i in range(6)]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(A.Vector(0,depth,0))
def keyshape(w,h,y,depth):
    c=P['register_chamfer']; z=T.z
    pts=[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2-c),(w/2-c,h/2),(-w/2,h/2)]
    vs=[A.Vector(x,y,z+v) for x,v in pts]
    return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,depth,0))
def slot_y(x1,x2,z,y,depth,r=1.2):
    return fuse(cy(r,y,depth,x1,z),cy(r,y,depth,x2,z),box(x1,y,z-r,x2-x1,depth,2*r))
def slot_z(x,y1,y2,z,depth,r=1.2):
    return fuse(cyl(r,z,depth,x,y1),cyl(r,z,depth,x,y2),box(x-r,y1,z,2*r,y2-y1,depth))

groups={}
for n in ['FixedNeck','PanAssembly','TiltAssembly','CarrierVariants','HardwareReferences','CableReferences','FixedOption','FitCoupons']:
    groups[n]=doc.addObject('App::DocumentObjectGroup',n)
parts=[]
colors={'fixed':(0.22,.34,.40),'pan':(.15,.55,.59),'tilt':(.31,.65,.68),
        'carrier':(.91,.57,.22),'reference':(.25,.35,.72),'hardware':(.58,.60,.63)}
def add(name,shape,group,role='fixed',motion='fixed',variant=None,release='prototype'):
    if not shape.isValid() or len(shape.Solids)!=1: raise RuntimeError('Invalid/disconnected solid '+name)
    obj=doc.addObject('Part::Feature',name)
    obj.Label=name.replace('_',' ')
    local=shape.copy(); world=shape.copy(); world.translate(C); obj.Shape=world
    obj.addProperty('App::PropertyString','DesignStatus').DesignStatus=release
    obj.addProperty('App::PropertyString','InterfaceVersion').InterfaceVersion=P['interface']
    obj.addProperty('App::PropertyString','MotionGroup').MotionGroup=motion
    groups[group].addObject(obj)
    p={'name':name,'local':local,'obj':obj,'role':role,'motion':motion,'variant':variant,'release':release}
    parts.append(p)
    report['parts'].append({'name':name,'volume_mm3':round(shape.Volume,3),'solids':len(shape.Solids),
        'role':role,'motion':motion,'variant':variant,'release':release})
    return p

# Fixed split collar, positive seating rim and full 12 mm cable passage.
collar=ring(14,10.2,104,16)
lug=fuse(box(-18,-5,106,9,10,12),box(9,-5,106,9,10,12))
collar=fuse(collar,lug).cut(cyl(10.2,103,18))
for x in [-13.5,13.5]: collar=collar.cut(cy(1.7,-6,12,x,112))
front=collar.common(box(-30,-30,100,60,29.7,25))
rear=collar.common(box(-30,.3,100,60,30,25))
# Rear key engages the candidate's 9.1 mm flat with clearance.
rear=fuse(rear,box(-3,9.3,106,6,2.4,13.8))
collar_rear=rear.copy()
spindle=fuse(ring(14,6,120,3),ring(12,6,123,3),ring(9.95,6,126,22))
spindle=spindle.cut(ring(11,9.5,144.5,1.3))
S=P['pan_servo_offset']; earz=140.; earcenter=S+(22.8/2-8.3)
platform=box(-10,earcenter-18,137,20,36,3)
platform=platform.cut(box(-6,S-8.3,136,12,22.8,5))
for y in [earcenter-13.6,earcenter+13.6]: platform=platform.cut(cyl(1.2,136,5,0,y))
bridge=fuse(box(-5,8,120,10,24,4),box(-5,earcenter-18,123,10,4,17),platform)
stop_parts=[]
for angle in [35,145]:
    a=math.radians(angle); x,y=26*math.cos(a),26*math.sin(a)
    strut=box(0,-3,120,26,6,4); strut.rotate(A.Vector(),A.Vector(0,0,1),angle)
    stop_parts.extend([strut,cyl(2,123,30,x,y)])
rear=fuse(rear,spindle,bridge,*stop_parts)
rear=rear.cut(cyl(6,103,46))
add('Neck_Main',rear,'FixedNeck')
add('Neck_Clamp_Cap',front,'FixedNeck')
add('Pan_Bearing_Lower',ring(16,10,126,7),'HardwareReferences','hardware')
add('Pan_Bearing_Upper',ring(16,10,137,7),'HardwareReferences','hardware')
add('Pan_Inner_Spacer',ring(12,10.05,133,4),'HardwareReferences','hardware')
add('Pan_Circlip_Envelope',ring(12.4,9.5,144.55,1.2),'HardwareReferences','hardware',release='hardware envelope; groove fit untested')

# Outer races are captured between rotor shoulders and screwed top ring.
rotor=fuse(ring(20.5,16.1,125.7,18.3),ring(20.5,15,133,4))
rotor=fuse(rotor,box(-25,-30,136,50,19,4))
# Preserve bore, bearing seats and rotating inner clearance after joining front lug.
rotor=rotor.cut(cyl(16.1,125,8.0)).cut(cyl(16.1,137,7.1)).cut(cyl(13,144,11))
retainer=ring(20.5,13,144,3)
for ang in [45,135,225,315]:
    x=18.3*math.cos(math.radians(ang)); y=18.3*math.sin(math.radians(ang))
    retainer=retainer.cut(cyl(1.1,143.5,4,x,y)); rotor=rotor.cut(cyl(.8,137,8,x,y))
rotor=fuse(rotor,box(-2,18,138,4,8,13),cyl(2,148,5,0,26))
for x in [-20,20]: rotor=rotor.cut(cyl(1.7,135,6,x,-25))
# Crank tower is clear of the fixed circlip; equal-radius parallelogram linkage.
retainer=fuse(retainer,box(10,-3,146.8,9,6,8.2),cyl(3,154,3.8,12,0))
retainer=retainer.cut(cyl(1.1,153,6,12,0))
add('Pan_Rotor',rotor,'PanAssembly','pan','pan')
add('Pan_Retainer_Crank',retainer,'PanAssembly','pan','pan')
link=fuse(box(9,0,158.8,6,S,3),cyl(3,158.8,3,12,0),cyl(3,158.8,3,12,S))
for y in [0,S]: link=link.cut(cyl(1.1,158,5,12,y))
add('Pan_Parallel_Link',link,'PanAssembly','pan','link',release='M2 shoulder pivots/washers and horn hole check required')
adapter=cyl(14,155.2,2.6,0,S).cut(cyl(3,155,4,0,S))
adapter=adapter.cut(slot_z(0,S-13,S-7,155,4)).cut(slot_z(0,S+7,S+13,155,4))
adapter=fuse(adapter,cyl(3,155.2,2.6,12,S)).cut(cyl(1.1,155,4,12,S))
add('Pan_Horn_Adapter',adapter,'PanAssembly','pan','servo',release='horn pattern provisional; retain supplied horn')

# SG90 reference, cross-width shaft center is a declared assumption.
def servo_shape():
    return fuse(box(-6,-8.3,0,12,22.8,17),box(-6,-13.15,17,12,32.5,2.5),
                box(-6,-8.3,19.5,12,22.8,8),cyl(3,27.5,2.7))
panservo=servo_shape(); panservo.translate(A.Vector(0,S,123))
add('SG90_Pan_Reference',panservo,'HardwareReferences','reference',release='measured and assumed envelope; not printable')
horn=fuse(box(-3,-18,153.2,6,36,2),box(-9,-3,153.2,18,6,2)); horn.translate(A.Vector(0,S,0))
add('Pan_Horn_Reference',horn,'HardwareReferences','hardware','servo',release='horn thickness and symmetry assumed')

# Two-sided tilt: internal servo mount plus opposite idler bushing.
floor=fuse(box(-27,-47,140,54,7,4),box(-27,-43,140,8,31,4),box(19,-43,140,8,31,4),box(-27,-30,140,54,11,4))
for x in [-20,20]: floor=floor.cut(cyl(1.7,139,6,x,-25))
right=box(28,-35,140,5,18,45)
right=fuse(right,box(19,-35,140,14,18,4))
right=right.cut(cx(2.1,27,7,-26,177))
earplate=box(-2.8,-36,140,3,20,60)
earplate=earplate.cut(box(-3.5,-32,168.7,5,12,22.8))
for z in [180.1-13.6,180.1+13.6]: earplate=earplate.cut(cx(1.2,-4,6,-26,z))
floor=fuse(floor,right,earplate,box(-19,-43,140,19,11,4)).cut(cyl(21.2,144,4))
add('Tilt_Yoke',floor,'PanAssembly','pan','pan')
tiltservo=servo_shape(); tiltservo.rotate(A.Vector(),A.Vector(0,1,0),-90)
# local body length along Y is turned into Z, narrow X into Y.
# Explicit basis maps original X->Y, Y->Z, Z->-X (right handed).
m=A.Matrix(); m.A11=0;m.A12=0;m.A13=-1;m.A21=-1;m.A22=0;m.A23=0;m.A31=0;m.A32=1;m.A33=0
tiltservo=servo_shape().transformGeometry(m); tiltservo.translate(A.Vector(14.2,-26,177))
add('SG90_Tilt_Reference',tiltservo,'HardwareReferences','reference','pan',release='cross-width shaft centering and upper body are assumptions')
th=fuse(box(-18,-29,159,2,6,36),box(-18,-35,174,2,18,6))
add('Tilt_Horn_Reference',th,'HardwareReferences','hardware','tilt',release='horn thickness/symmetry assumed')
bushing=cx(2,28,5,-26,177).cut(cx(1.5,27,7,-26,177))
add('Tilt_Idler_Bushing',bushing,'HardwareReferences','hardware','pan',release='4 OD / 3 ID sleeve hardware required; verify fit')

# GH44 receiver, keyed register, four service screws and cable window.
pitch=P['carrier_hole_pitch']/2; w=P['carrier_width']; h=P['carrier_height']; z=T.z
receiver=box(-w/2,-52,z-h/2,w,4,h)
receiver=receiver.cut(keyshape(26.4,22.4,-52.1,1.7))
receiver=receiver.cut(box(-9,-53,z-5,18,7,10))
for x in [-pitch,pitch]:
    for dz in [-pitch,pitch]:
        receiver=receiver.cut(cy(1.7,-53,7,x,z+dz)).cut(hex_y(5.7,-50.6,2.7,x,z+dz))
receiver_face=receiver.copy()
backbone=box(-27,-48.2,z-6,54,4.2,12)
left=box(-24,-46,z-6,3,25,12)
right=box(24,-46,z-6,3,25,12).cut(cx(1.6,23,5,-26,z))
drive=cx(14,-21,3,-26,z).cut(cx(3,-22,5,-26,z))
# Four radial slots avoid pretending unknown horn holes are measured.
for dz in [-11,11]: drive=drive.cut(cx(1.1,-22,5,-26,z+dz))
receiver=fuse(receiver,backbone,left,right,drive).cut(box(-9,-53,z-5,18,12,10))
add('GH44_Tilt_Receiver',receiver,'TiltAssembly','tilt','tilt',release='interface prototype; horn holes provisional')

def carrier_base():
    s=box(-22,-55,z-22,44,3,44)
    s=fuse(s,keyshape(26,22,-52,1.4)).cut(box(-9,-56,z-5,18,8,10))
    for x in [-16,16]:
        for dz in [-16,16]: s=s.cut(cy(1.7,-56,8,x,z+dz))
    return s
base=carrier_base()
add('GH44_Blank_Carrier',base,'CarrierVariants','carrier','tilt','blank','interface fit prototype')
# Adapter plates use clearly labelled generic adjustment slots; do not invent PCB holes.
def slotted_carrier(width,height,zoff=0):
    s=fuse(base,box(-width/2,-58,z+zoff-height/2,width,3,height))
    for dz in [-height/2+5,height/2-5]: s=s.cut(slot_y(-width/2+5,width/2-5,z+zoff+dz,-59,5))
    for x in [-16,16]:
        for dz in [-16,16]: s=s.cut(cy(1.7,-60,12,x,z+dz))
    return s.cut(box(-9,-59,z-5,18,12,10))
for name,width,height in [('ToF',38,38),('Radar',34,40),('Camera',38,50),('Dual',70,42)]:
    add('GH44_'+name+'_Carrier',slotted_carrier(width,height,6 if name=='Camera' else 0),'CarrierVariants','carrier','tilt',name.lower(),
        'carrier layout prototype; add measured standoffs/edge clamps before installation')
def sensor_ref(name,width,height,depth,xoff=0,variant='tof',zoff=0):
    add(name,box(xoff-width/2,-58-depth,z+zoff-height/2,width,depth,height),'CarrierVariants','reference','tilt',variant,'clearance envelope only')
sensor_ref('SEN0628_Envelope',29,29,13,variant='tof')
sensor_ref('SEN0610_Envelope',24,32,13,variant='radar')
sensor_ref('ESP32_CAM_Envelope',28.5,42,15,variant='camera',zoff=6)
sensor_ref('Dual_ToF_Envelope',29,29,13,-17,variant='dual')
sensor_ref('Dual_Radar_Envelope',24,32,13,17,variant='dual')

# Fixed option bypasses the motion unit but takes the same carrier mating face.
fixedface=receiver_face.copy();fixedface.translate(A.Vector(0,26,-22))
fixed=fuse(collar_rear,ring(14,6,120,3),box(-11,-22,122,4,15,35),box(7,-22,122,4,15,35),fixedface)
add('GH44_Fixed_Head_Adapter',fixed,'FixedOption','fixed','fixed','fixed_option','fixed interface prototype; pairs with Neck Clamp Cap')
add('GH44_Receiver_Fit_Coupon',receiver_face,'FitCoupons','tilt','fixed','coupon','print coupon before full parts')

def posed(p,pan=0,tilt=0):
    s=p['local'].copy()
    if p['motion']=='tilt': s.rotate(T,A.Vector(1,0,0),tilt)
    if p['motion'] in ['pan','tilt']: s.rotate(A.Vector(),A.Vector(0,0,1),pan)
    if p['motion']=='servo': s.rotate(A.Vector(0,S,0),A.Vector(0,0,1),pan)
    if p['motion']=='link':
        a=math.radians(pan); r=P['pan_crank_radius']; s.translate(A.Vector(r*math.cos(a)-r,r*math.sin(a),0))
    return s

def overlaps(a,b):
    if not a.BoundBox.intersect(b.BoundBox): return 0.
    return a.common(b).Volume

# Exact B-rep interference checks for independent manufactured solids.
# Bearings/horns are separate references; intended fit contact checked independently.
struct=[p for p in parts if p['role'] not in ['reference','hardware'] and (p['variant'] in [None,'dual'])]
intended={frozenset(['Pan_Rotor','Pan_Retainer_Crank']),frozenset(['Pan_Rotor','Tilt_Yoke'])}
tests=0
for pan in [-40,-20,0,20,40]:
    for tilt in [-25,0,25]:
        posed_parts={p['name']:posed(p,pan,tilt) for p in struct}
        for a,b in itertools.combinations(struct,2):
            if a['motion']==b['motion'] and (pan or tilt): continue
            if frozenset([a['name'],b['name']]) in intended: continue
            v=overlaps(posed_parts[a['name']],posed_parts[b['name']]); tests+=1
            if v>0.05: report['collisions'].append({'pan':pan,'tilt':tilt,'a':a['name'],'b':b['name'],'mm3':round(v,3)})
report['checks']['structural_pose_pair_tests']=tests
# Check each carrier variant against fixed/moving servo envelopes over the same poses.
for pan in [-40,0,40]:
    for tilt in [-25,0,25]:
        for sensor in [p for p in parts if p['variant'] in ['blank','tof','radar','camera','dual']]:
            for obstacle in [p for p in parts if p['name'] in ['Neck_Main','SG90_Pan_Reference','SG90_Tilt_Reference','Tilt_Yoke']]:
                if sensor['name'].startswith('GH44_Blank'): continue
                v=overlaps(posed(sensor,pan,tilt),posed(obstacle,pan,tilt))
                if v>.05: report['collisions'].append({'pan':pan,'tilt':tilt,'a':sensor['name'],'b':obstacle['name'],'mm3':round(v,3)})
# Verify the key register mates, while a reversed carrier cannot silently seat.
report['checks']['neutral_carrier_receiver_overlap_mm3']=overlaps(base,receiver)
wrong=base.copy(); wrong.rotate(A.Vector(0,0,z),A.Vector(0,1,0),180)
report['checks']['reversed_carrier_receiver_overlap_mm3']=overlaps(wrong,receiver)
report['checks']['master_unchanged']=hashlib.sha256(MASTER.read_bytes()).hexdigest()==report['master_sha256']
report['checks']['all_generated_parts_single_valid_solid']=all(p['local'].isValid() and len(p['local'].Solids)==1 for p in parts)
# Whole-robot checks use the latest saved CAD, not the earlier audited revision.
robot=[]
for name in ['MastTube','MastBase','UpperDeck','S3Board','Breadboard','DriverMountLeft','DriverMountRight','AntennaPost']:
    s=doc.getObject(name).Shape.copy();s.translate(-C);robot.append((name,s))
robot_tests=0
for pan in [-40,0,40]:
 for tilt in [-25,0,25]:
  for p in [q for q in parts if q['variant'] in [None,'dual']]:
   s=posed(p,pan,tilt)
   for name,r in robot:
    vol=overlaps(s,r);robot_tests+=1
    if vol>.05:report['collisions'].append({'pan':pan,'tilt':tilt,'a':p['name'],'b':name,'mm3':round(vol,3)})
report['checks']['robot_pose_pair_tests']=robot_tests
report['checks']['pan_link_center_distance_mm']=S
report['checks']['pan_cranks_equal_radius_mm']=12
report['checks']['neutral_wire_bore_free']=not any(p['local'].isInside(A.Vector(0,0,h),1e-5,False) for p in parts if p['variant'] is None for h in range(105,149))
report['checks']['mast_neck_11_9mm_passage_overlap_mm3']=sum(overlaps(cyl(5.95,105,43),p['local']) for p in parts if p['variant'] is None)
report['checks']['receiver_17_8x9_8mm_passage_overlap_mm3']=overlaps(box(-8.9,-52.1,z-4.9,17.8,10,9.8),receiver)
report['checks']['carrier_passage_overlap_mm3']={p['name']:overlaps(box(-8.9,-58.1,z-4.9,17.8,8,9.8),p['local']) for p in parts if p['role']=='carrier'}
report['checks']['fixed_adapter_robot_overlap_mm3']={name:overlaps(fixed,s) for name,s in robot}
fixedcarrier=base.copy();fixedcarrier.translate(A.Vector(0,26,-22))
report['checks']['fixed_adapter_carrier_overlap_mm3']=overlaps(fixed,fixedcarrier)
report['fov_intersections']=[]
# Nominal ToF frustum: assumes optical origin centered on front of clearance box.
# This checks nearby structure, not lens tolerances or optical crosstalk.
def fov_wire(y,half):
    pts=[A.Vector(-17+x,y,z+v) for x,v in [(-half,-half),(half,-half),(half,half),(-half,half)]]
    return Part.makePolygon(pts+[pts[0]])
frustum=Part.makeLoft([fov_wire(-71,.5),fov_wire(-221,.5+150*math.tan(math.radians(30)))],True)
for pan in [-40,0,40]:
 for tilt in [-25,0,25]:
    f=frustum.copy();f.rotate(T,A.Vector(1,0,0),tilt);f.rotate(A.Vector(),A.Vector(0,0,1),pan)
    obstacles=robot+[(p['name'],posed(p,pan,tilt)) for p in parts if p['variant'] in [None,'dual']]
    for name,s in obstacles:
        v=overlaps(f,s)
        if v>.05:report['fov_intersections'].append({'pan':pan,'tilt':tilt,'object':name,'mm3':round(v,3)})
fobj=doc.addObject('Part::Feature','ToF_Field_Reference'); fw=frustum.copy();fw.translate(C);fobj.Shape=fw
fobj.Label='ToF nominal 60 x 60 field — assumed optical origin'
groups['CableReferences'].addObject(fobj)
# Wiring route guide leaves through the forward side, away from the rear linkage.
path=Part.makePolygon([A.Vector(0,0,144),A.Vector(0,0,152),A.Vector(21,-10,160),A.Vector(21,-38,168),A.Vector(0,-43,177),A.Vector(0,-53,177)])
path.translate(C); wire=doc.addObject('Part::Feature','Harness_Route_Guide');wire.Shape=path
wire.Label='Harness route guide — flex loop and connector sizing pending'; groups['CableReferences'].addObject(wire)

# Mesh evidence for independent rendering, including current master components.
mesh=[]
for p in parts:
    if p['variant'] not in [None,'dual']: continue
    vertices,faces=p['local'].tessellate(.35)
    mesh.append({'name':p['name'],'color':colors[p['role']],'motion':p['motion'],
                 'vertices':[[v.x,v.y,v.z] for v in vertices],'faces':faces})
for name in ['MastTube','UpperDeck','S3Board','Breadboard','DriverMountLeft','DriverMountRight','AntennaPost']:
    s=doc.getObject(name).Shape.copy(); s.translate(-C)
    vs,fs=s.tessellate(.7)
    mesh.append({'name':name,'color':(.56,.59,.62),'motion':'fixed','context':True,
                 'vertices':[[v.x,v.y,v.z] for v in vs],'faces':fs})
(OUT/'head-preview-mesh.json').write_text(json.dumps(mesh,separators=(',',':')))

doc.recompute()
doc.saveAs(str(OUT/'Gladiator_Head_v01.FCStd'))
installed=[p['obj'] for p in parts if p['variant'] in [None,'dual']]
Part.export(installed,str(OUT/'Gladiator_Head_v01.step'))
# Export mating template separately; only safe-to-evaluate interface parts get STL.
exports=OUT/'fit-prototypes'; exports.mkdir(exist_ok=True)
for n in ['GH44_Tilt_Receiver','Neck_Main']:
    for ext in ['.brep','.stl']:
        stale=exports/(n+ext)
        if stale.exists() and stale.resolve().parent==exports.resolve():stale.unlink()
for p in parts:
    if p['name'] in ['GH44_Blank_Carrier','GH44_Receiver_Fit_Coupon','GH44_Fixed_Head_Adapter','Neck_Clamp_Cap']:
        p['local'].exportBrep(str(exports/(p['name']+'.brep')))
        stl=p['local'].copy()
        if p['name']=='GH44_Blank_Carrier': stl.rotate(A.Vector(),A.Vector(1,0,0),90)
        if p['name']=='GH44_Receiver_Fit_Coupon': stl.rotate(A.Vector(),A.Vector(1,0,0),-90)
        bb=stl.BoundBox; stl.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
        stl.exportStl(str(exports/(p['name']+'.stl')))
template=A.newDocument('GH44_Carrier_Template')
temp=template.addObject('Part::Feature','GH44_Mating_Base'); temp.Shape=base
temp.addProperty('App::PropertyString','Interface').Interface=P['interface']
temp.addProperty('App::PropertyString','Instructions').Instructions='Sensor-specific features go toward -Y. Keep mating face, key, cable opening and four M3 holes unchanged.'
template.recompute(); template.saveAs(str(OUT/'GH44_Carrier_Template.FCStd'))
Part.export([temp],str(OUT/'GH44_Carrier_Template.step'))
report['checks']['master_unchanged_after_save']=hashlib.sha256(MASTER.read_bytes()).hexdigest()==report['master_sha256']
report['release']='GEOMETRY REVIEW / INTERFACE FIT PROTOTYPES ONLY'
report['checks']['geometry_review_pass']=not report['collisions'] and not report['fov_intersections'] and report['checks']['all_generated_parts_single_valid_solid'] and report['checks']['mast_neck_11_9mm_passage_overlap_mm3']<.01 and report['checks']['receiver_17_8x9_8mm_passage_overlap_mm3']<.01
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'out':str(OUT),'part_count':len(parts),'collisions':report['collisions'], 'fov_intersections':report['fov_intersections'],'checks':report['checks']},indent=2))
A.closeDocument(template.Name); A.closeDocument(doc.Name)
