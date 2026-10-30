"""Head v2 focused revision: compact tilt balance and M3x20 tensioner only.
Reads preserved v2 baseline; changes one printed receiver and payload placement.
Run on cad-lab: python3 build_balance_tensioner.py
"""
import sys,json,math,hashlib,time,shutil
from pathlib import Path
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A,Part,Mesh,MeshPart
V=A.Vector
BASE=Path('/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028')
OUT=BASE/'balance-tensioner-20261030';OUT.mkdir(exist_ok=True)
(OUT/'stl').mkdir(exist_ok=True)
source=BASE/'Gladiator_Head_v2_Mast.FCStd'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_hash=sha(source)
old=json.loads((BASE/'validation.json').read_text())['v2']
p=old['params'];T=V(*old['tilt_axis_world']);SHIFT=2.5
src=A.openDocument(str(source))
S={o.Name:o.Shape.copy() for o in src.Objects if o.TypeId=='Part::Feature'}
original={n:s.copy() for n,s in S.items()}
tilt=old['groups']['tilt'];pan=old['groups']['pan'];fixed=old['groups']['fixed']
payload=[n for n in tilt if n not in ('GH44_Tilt_Receiver','Tilt_Horn_Reference')]
def ov(a,b): return a.common(b).Volume if a.BoundBox.intersect(b.BoundBox) else 0.0
# Shorten the front of the receiver while retaining its shaft/horn/pivot features.
plane=T.y-15
rec=S['GH44_Tilt_Receiver']
fore=rec.common(Part.makeBox(200,200,200,V(T.x-100,plane-200,T.z-100)))
aft=rec.common(Part.makeBox(200,200,200,V(T.x-100,plane,T.z-100)))
fore.translate(V(0,SHIFT,0));rec=aft.fuse(fore).removeSplitter()
rough=rec.copy()
# Local receiver pockets preserve the current yoke and nominal 38-up/34-down range.
# Use offset solids to allow 0.4 mm around the yoke and measured servo envelope.
def padded_box(x,y,z,dx,dy,dz,pad=.4):
 return Part.makeBox(dx+2*pad,dy+2*pad,dz+2*pad,T+V(x-pad,y-pad,z-pad))
def padded_cx(r,x,length,pad=.4):
 return Part.makeCylinder(r+pad,length+2*pad,T+V(x-pad,0,0),V(1,0,0))
# Conservative unions of the source's actual SG90 body/ear/boss primitives.
servo_bits=[padded_box(-2.8,-6,-5.9,17.5,12,22.8),padded_box(-5.3,-6,-10.8,2.5,12,32.6),padded_box(-11.3,-6,-5.9,6,12,16.9),padded_cx(5.5,-13.8,2.5),padded_cx(2.4,-17.3,3.5)]
servo_offset=servo_bits[0]
for bit in servo_bits[1:]:servo_offset=servo_offset.fuse(bit)
# Receiver approaches the ear plate/column, not the distant floor or opposite tower.
yoke_bits=[padded_box(-2.8,-10,-12,3,20,35),padded_box(-12,-3,-47,12.2,6,35)]
yoke_offset=yoke_bits[0].fuse(yoke_bits[1])
offsets={'Tilt_Yoke':yoke_offset,'SG90_Tilt_Reference':servo_offset}
for t in range(-38,35):
 for n,b in offsets.items():
  cut=b.copy();cut.rotate(T,V(1,0,0),-t)
  if ov(rec,cut)>.0001:rec=rec.cut(cut).removeSplitter()
# Preserve the complete tested horn seat, screw roof and clearance cavity.
# The front horn arm crosses the geometric split used to shorten the receiver.
bb=original['Tilt_Horn_Reference'].BoundBox
horn_zone=Part.makeBox(bb.XLength+4,bb.YLength+4,bb.ZLength+4,V(bb.XMin-2,bb.YMin-2,bb.ZMin-2))
rec=rec.cut(horn_zone).fuse(original['GH44_Tilt_Receiver'].common(horn_zone)).removeSplitter()
assert rec.isValid() and len(rec.Solids)==1
S['GH44_Tilt_Receiver']=rec
for n in payload:S[n].translate(V(0,SHIFT,0))
print('Receiver constructed; starting checks',flush=True)
# Tensioner hardware, including the full screw at its bearing position.
def frame(shape):
 s=shape.copy();s.rotate(V(),V(0,0,1),-45);s.translate(V(39.5,113,p['LIFT']));return s
PAD=p['PAD_Y0'];Z=p['TS_Z'];LENGTH=20
screw=Part.makeCylinder(1.5,LENGTH,V(0,PAD-LENGTH,Z),V(0,1,0)).fuse(Part.makeCylinder(3,3,V(0,PAD-LENGTH-3,Z),V(0,1,0)))
screw=frame(screw)
def nut_at(C):
 outer=-C-5.5+p['LUG_IN']-7
 cy=outer+3.5;rr=5.8/math.sqrt(3)
 vs=[V(rr*math.cos(math.radians(30+60*k)),cy-1.2,Z+rr*math.sin(math.radians(30+60*k))) for k in range(6)]
 nut=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,2.4,0))
 nut=nut.cut(Part.makeCylinder(1.5,2.6,V(0,cy-1.3,Z),V(0,1,0)))
 return frame(nut)
S['Tensioner_M3x20_Envelope']=screw
S['Tensioner_Nut_Envelope']=nut_at(p['C_NOM'])
report={'status':'CAD revision; not sliced or physically tested','scope':['Tilt balance','Tensioner screw reach'],
 'source_sha256':source_hash,'payload_shift_rearward_mm':SHIFT,'receiver_relief_allowance_mm':.4,
 'receiver_relief_removed_mm3':round(rough.Volume-rec.Volume,4),'checks':{},'limitations':[
 'Mass and gravity moments are estimates using the previous CAD assumptions, not weighed payloads.',
 'Harness flexibility, fastener fit, servo calibration, strength and print support still require physical checks.',
 'Screw head envelope is conservative 6 mm diameter x3 mm; nut envelope 5.8 AF x2.4 mm. Verify actual stock.',
 'No firmware limits, pan indexing, yoke passage, stop features, slotted tube or other printed geometry changed.']}
# Baseline and revised mass properties computed with identical assumptions.
printed=['Rear_Display_Frame','GH44_Tilt_Receiver','GH44_Dual_Carrier','ToF_Sensor_Frame','Camera_Tray','Camera_Cover','Tilt_Yoke','Pan_Raised_Pedestal','Pan_Rotor','Pan_Retainer']
point={'ESP32_CAM_Reference':10,'Dual_ToF_Envelope':5,'ST7789_Board':7,'SG90_Tilt_Reference':9,'Tilt_Horn_Reference':1,'Tilt_Pivot_Bolt':1}
def com(s):
 acc=V()
 for solid in s.Solids:acc+=solid.CenterOfMass*solid.Volume
 return acc/s.Volume
def summary(shapes):
 items=[(n,shapes[n].Volume*.00124*.85,com(shapes[n])) for n in printed]
 items +=[(n,g,com(shapes[n])) for n,g in point.items()]
 items += [('GH44_Dual_Carrier',8,com(shapes['GH44_Dual_Carrier'])),('Camera_Tray',4,com(shapes['Camera_Tray']))]
 tm=sum(g for n,g,c in items if n in tilt)
 moment=sum(g*(T.y-c.y) for n,g,c in items if n in tilt)
 hm=sum(g for n,g,c in items);hmy=sum(g*(T.y-c.y) for n,g,c in items)
 return {'tilting_mass_g':round(tm,3),'tilting_com_ahead_of_pivot_mm':round(moment/tm,3),'level_holding_kgcm':round(moment/10000,5),'head_mass_g':round(hm,3),'head_com_ahead_of_mast_mm':round(hmy/hm,3)}
report['balance']={'before':summary(original),'after':summary(S)}
report['balance']['holding_moment_reduction_percent']=round(100*(1-report['balance']['after']['level_holding_kgcm']/report['balance']['before']['level_holding_kgcm']),2)
# Other printed geometries are preserved (payload parts are only relocated).
def signature(s):
 return (round(s.Volume,5),round(s.Area,5),len(s.Faces),len(s.Edges),sorted(tuple(round(v,6) for v in (p.Point.x,p.Point.y,p.Point.z)) for p in s.Vertexes))
preserved={}
for n in original:
 if n=='GH44_Tilt_Receiver':continue
 q=S[n].copy()
 if n in payload:q.translate(V(0,-SHIFT,0))
 preserved[n]=signature(q)==signature(original[n])
assert all(preserved.values()),[n for n,v in preserved.items() if not v]
report['checks']['all_other_parts_geometry_preserved']=True
# Check interface fastener paths and bearing material at the four GH44 holes.
interfaces=[]
for x in (-16,16):
 for z in (-16,16):
  c=V(T.x+x,T.y-26+SHIFT,T.z+z)
  hole=Part.makeCylinder(1.79,4.2,c-V(0,.1,0),V(0,1,0))
  seat=Part.makeCylinder(2.8,.4,c,V(0,1,0)).cut(Part.makeCylinder(1.81,.6,c-V(0,.1,0),V(0,1,0)))
  entry={'xz':[x,z],'hole_overlap_mm3':round(ov(rec,hole),6),'front_bearing_fraction':round(ov(rec,seat)/seat.Volume,6)}
  interfaces.append(entry)
  assert entry['hole_overlap_mm3']<1e-5 and entry['front_bearing_fraction']>.999,entry
report['checks']['GH44_four_holes_and_seats']=interfaces
# Model complete hardware and thread contact throughout carriage travel.
unit=V(-math.sqrt(.5),-math.sqrt(.5),0)
carriage_names=('Pan_Servo_Carriage','SG90_Pan_Reference','Pan_Drive_Pulley','Pan_Horn_Reference')
hardware=[]
for C in range(38,49):
 current={n:s.copy() for n,s in S.items()}
 for n in carriage_names:current[n].translate(unit*(C-p['C_NOM']))
 current['Tensioner_Nut_Envelope']=nut_at(C)
 hits=[]
 for a in ('Tensioner_M3x20_Envelope','Tensioner_Nut_Envelope'):
  for b in current:
   if a==b:continue
   vol=ov(current[a],current[b])
   if vol>.01:hits.append([a,b,round(vol,5)])
 reach=PAD-(-C-5.5+p['LUG_IN']-7)
 hardware.append({'C_mm':C,'underhead_to_pad_mm':round(reach,3),'head_gap_to_lug_mm':round(20-reach,3),'collisions':hits})
 assert not hits,(C,hits)
report['checks']['tensioner_full_travel']=hardware
# Driver access behind the tensioner head, conservative 5-mm shaft.
probe=frame(Part.makeCylinder(2.5,35,V(0,PAD-20-3-35,Z),V(0,1,0)))
driver_hits=[n for n,s in S.items() if ov(s,probe)>.01]
report['checks']['tensioner_driver_blockers']=driver_hits
assert not driver_hits,driver_hits
# Recheck every assembly pair at home. Preserve only the two intentional bearing fits.
intent={frozenset(('Pan_Bearing_Lower','Neck_Main')),frozenset(('Pan_Bearing_Upper','Neck_Main'))}
robot_context={o.Name for o in src.Objects if o.TypeId=='Part::Feature' and o.getParentGroup().Name=='Robot_Context'}
names=list(S);static=[]
for i,a in enumerate(names):
 for b in names[i+1:]:
  if a in robot_context and b in robot_context:continue
  if a not in tilt+pan+fixed and not a.startswith('Tensioner_'):continue
  if frozenset((a,b)) in intent:continue
  vol=ov(S[a],S[b])
  if vol>.05:static.append([a,b,round(vol,4)])
report['checks']['home_collisions']=static
assert not static,static
print('Static/hardware checks passed; checking motion',flush=True)
# Tilt-vs-pan is invariant to pan angle. For fixed obstacles, rotate the
# obstacle into the head frame, avoiding repeated transforms of detailed PCBs.
# Z is invariant under pan; discard only provably separated Z intervals.
new_fixed=fixed+['Tensioner_M3x20_Envelope','Tensioner_Nut_Envelope']
tilt_angles=list(range(-38,35,2))
min_z=1e9;max_z=-1e9
for n in tilt:
 bb=S[n].BoundBox
 for t in tilt_angles:
  ang=math.radians(t)
  for y in (bb.YMin-T.y,bb.YMax-T.y):
   for z in (bb.ZMin-T.z,bb.ZMax-T.z):
    zz=T.z+math.sin(ang)*y+math.cos(ang)*z
    min_z=min(min_z,zz);max_z=max(max_z,zz)
active_fixed=[n for n in new_fixed if S[n].BoundBox.ZMax>=min_z and S[n].BoundBox.ZMin<=max_z]
fixed_in_head={};servo_axis=V(39.5,113,0)+unit*p['C_NOM']
for pn in range(-20,181,20):
 fixed_in_head[pn]={}
 for n in active_fixed:
  q=S[n].copy()
  if n in ('Pan_Drive_Pulley','Pan_Horn_Reference'):q.rotate(servo_axis,V(0,0,1),pn/1.5)
  q.rotate(V(39.5,113,0),V(0,0,1),-pn)
  fixed_in_head[pn][n]=q
collisions=[];closest_carrier=1e9
for t in tilt_angles:
 for n in tilt:
  q=S[n].copy();q.rotate(T,V(1,0,0),t)
  for b in pan:
   v=ov(q,S[b])
   if v>.05:collisions.append([n,b,0,t,round(v,4)])
  if n=='GH44_Dual_Carrier':closest_carrier=min(closest_carrier,q.distToShape(S['Tilt_Yoke'])[0])
  for pn,obstacles in fixed_in_head.items():
   for b,obstacle in obstacles.items():
    v=ov(q,obstacle)
    if v>.05:collisions.append([n,b,pn,t,round(v,4)])
 print('Tilt checked',t,flush=True)
report['checks']['motion_collisions']=collisions
report['checks']['motion_grid']={'pan_deg':[-20,180,20],'tilt_deg':[-38,34,2]}
report['checks']['fixed_obstacles_in_tilt_height_band']=active_fixed
report['checks']['carrier_to_yoke_min_sampled_mm']=round(closest_carrier,4)
assert not collisions,collisions
# Pan stage unchanged, but new hardware must be outside its complete motion.
pan_hits=[]
for pn in range(-20,181,5):
 for n in pan:
  q=S[n].copy();q.rotate(V(39.5,113,0),V(0,0,1),pn)
  for b in ('Tensioner_M3x20_Envelope','Tensioner_Nut_Envelope'):
   v=ov(q,S[b])
   if v>.05:pan_hits.append([n,b,pn,round(v,4)])
report['checks']['pan_vs_new_hardware_collisions']=pan_hits
assert not pan_hits
# Export only the new receiver for manufacture, and the complete assembly for review.
doc=A.newDocument('Gladiator_Head_v2_Balanced')
groups={}
for n,s in S.items():
 g='Hardware' if n.startswith('Tensioner_') else src.getObject(n).getParentGroup().Name
 if g not in groups:groups[g]=doc.addObject('App::DocumentObjectGroup',g)
 o=doc.addObject('Part::Feature',n);o.Shape=s.copy();groups[g].addObject(o)
doc.recompute();doc.saveAs(str(OUT/'Gladiator_Head_v2_Balanced.FCStd'))
Part.export([doc.getObject(n) for n in S if n in tilt+pan+fixed and not n.startswith('Ref_')],str(OUT/'Gladiator_Head_v2_Balanced_assembly.step'))
print_rec=rec.copy();print_rec.translate(-T);print_rec.rotate(V(),V(1,0,0),90)
b=print_rec.BoundBox;print_rec.translate(V(-b.XMin,-b.YMin,-b.ZMin))
assert print_rec.isValid() and len(print_rec.Solids)==1
obj=doc.addObject('Part::Feature','Receiver_Print_Export');obj.Shape=print_rec
Part.export([obj],str(OUT/'GH44_Tilt_Receiver_Balanced.step'))
mesh=MeshPart.meshFromShape(Shape=print_rec,LinearDeflection=.01,AngularDeflection=.0872665,Relative=False)
path=OUT/'stl/GH44_Tilt_Receiver_Balanced.stl';mesh.write(str(path));back=Mesh.Mesh(str(path))
assert back.isSolid() and not back.hasNonManifolds()
report['checks']['receiver_mesh']={'solid':back.isSolid(),'non_manifold':back.hasNonManifolds(),'size_mm':[round(print_rec.BoundBox.XLength,3),round(print_rec.BoundBox.YLength,3),round(print_rec.BoundBox.ZLength,3)]}
doc.removeObject(obj.Name)
# Reusable preview meshes: original and revised side-by-side, no robot shell clutter.
preview={}
for tag,shapes in [('before',original),('after',S)]:
 preview[tag]={}
 for n,s in shapes.items():
  if n in ('Rear_Hood','Front_Left','Front_Right','Lens_Plate') or n.startswith('Ref_'):continue
  m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.15,AngularDeflection=.3,Relative=False)
  preview[tag][n]=[[list(v) for v in f.Points] for f in m.Facets]
(OUT/'preview_meshes.json').write_text(json.dumps(preview))
assert sha(source)==source_hash
report['checks']['baseline_file_unchanged']=True
report['reprint_parts']=['GH44_Tilt_Receiver_Balanced']
report['hardware_change']='Replace M3x16 tensioner with M3x20; retain the current nut and carriage.'
report['build_source_sha256']=sha(Path(__file__))
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
A.closeDocument(doc.Name);A.closeDocument(src.Name)
print('BUILD PASSED',json.dumps(report['balance']),flush=True)
