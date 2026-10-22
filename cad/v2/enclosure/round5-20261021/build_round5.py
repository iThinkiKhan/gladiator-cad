"""Round 5 styling derived from the SAVED enclosure v2.8. Additive only.
Run: xvfb-run -a freecad build_round5.py. No source document is saved.
"""
from pathlib import Path
import FreeCAD as A, FreeCADGui as G, Part, MeshPart
import json, math, hashlib, shutil, traceback, os, time
V=A.Vector
ROOT=Path('/home/buralien/projects/gladiator-cad')
OUT=ROOT/'cad/v2/enclosure/round5-20261021'
BASE=ROOT/'cad/v2/enclosure/v2-20261013'
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'stl').mkdir(exist_ok=True)
T0=time.time()
def log(*s):
 msg=' '.join(map(str,s)); (OUT/'progress.log').open('a').write(str(round(time.time()-T0,1))+' '+msg+'\n'); print(msg,flush=True)
CFG=dict(insert_bore=3.6,insert_depth=4.0,insert_length_assumed=3.0,
         badge_clearance_per_side=.25,cap_height=12.0,belt_z=[50.,56.],
         shield_radius=28.,shield_width=27.3,shield_height=41.6,
         note='M2 bore and insert length are provisional until existing M2-A coupon/hardware results. No structural pockets.')
GREY=(.43,.46,.50); RED=(.68,.045,.035); WHITE=(.91,.90,.86); GOLD=(.76,.53,.20); BLACK=(.075,.082,.095)
REPORT={'configuration':CFG,'source_hashes':{},'parts':{},'baseline_preservation':{},'collisions':[], 'mounts':[]}
PRINT={}; SHAPES={}; COLORS={}; OWNERS={}; HARD={}; LOCAL={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(s):
 q=Part.Shape();q.importBrepFromString(s.exportBrepToString())
 if len(q.Solids)==1:q=q.Solids[0]
 return q

def fuse(*ss):
 s=clean(ss[0])
 for q in ss[1:]:s=clean(s.fuse(clean(q),.00001))
 try:s=s.removeSplitter()
 except Part.OCCError:pass
 return clean(s)
def cut(s,*ss):
 s=clean(s)
 for q in ss:s=clean(s.cut(clean(q)))
 try:s=s.removeSplitter()
 except Part.OCCError:pass
 return clean(s)
def common(a,b):return clean(clean(a).common(clean(b)))
def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def poly(pts,z0,z1):
 vs=[V(x,y,z0) for x,y in pts];return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,z1-z0))
def disk(x,y,r,z0,z1):return Part.makeCylinder(r,z1-z0,V(x,y,z0))
def strokeline(pts,w,z0,z1):
 ss=[]
 for p,q in zip(pts,pts[1:]):
  dx,dy=q[0]-p[0],q[1]-p[1];l=math.hypot(dx,dy);nx,ny=-dy/l*w/2,dx/l*w/2
  ss.append(poly([(p[0]+nx,p[1]+ny),(q[0]+nx,q[1]+ny),(q[0]-nx,q[1]-ny),(p[0]-nx,p[1]-ny)],z0,z1))
 for x,y in pts:ss.append(disk(x,y,w/2,z0,z1))
 return fuse(*ss)
def feather(root,tip,width,z0,z1):
 # Two cubic Beziers give a continuous, pointed flight feather.
 r=V(*root,z0);t=V(*tip,z0);d=t-r;n=V(-d.y,d.x,0);n.normalize();n*=width/2
 p=r+d*.20+n*.7;q=r+d*.68+n;t2=t-d*.08+n*.18
 a=Part.BezierCurve();a.setPoles([r,p,q,t]);b=Part.BezierCurve();b.setPoles([t,t2-d*.05-n*.8,r+d*.22-n,r])
 return Part.Face(Part.Wire([a.toShape(),b.toShape()])).extrude(V(0,0,z1-z0))
def relief_feather(root,tip,width,z0,z1):
 base=feather(root,tip,width,z0,z1)
 dx,dy=tip[0]-root[0],tip[1]-root[1]
 inner=feather((root[0]+dx*.08,root[1]+dy*.08),(tip[0]-dx*.08,tip[1]-dy*.08),width*.52,z1,z1+.48)
 outerwire=next(f.OuterWire for f in base.Faces if abs(f.CenterOfMass.z-z1)<1e-7)
 innerwire=next(f.OuterWire for f in inner.Faces if abs(f.CenterOfMass.z-(z1+.48))<1e-7)
 cap=Part.makeLoft([outerwire,innerwire],True,False)
 return fuse(base,cap)

def ellipse(cx,cy,rx,ry,z0,z1):
 c=Part.makeCylinder(1,z1-z0,V(0,0,z0));m=A.Matrix();m.A11=rx;m.A22=ry
 c=c.transformGeometry(m);c.translate(V(cx,cy,0));return clean(c)
def dome3(cx,cy,cz,rx,ry,rz):
 s=Part.makeSphere(1);m=A.Matrix();m.A11=rx;m.A22=ry;m.A33=rz
 s=s.transformGeometry(m);s.translate(V(cx,cy,cz));return clean(s)

def frame(origin,U,N):
 U=V(*U);N=V(*N);W=V(0,0,1)
 assert (U.cross(W)-N).Length<1e-6
 return A.Placement(V(*origin),A.Rotation(U,W,N,'ZXY'))
def world(s,f):
 s=clean(s);s.Placement=f.multiply(s.Placement);return clean(s)
def add(name,shape,color,owner,local=None,placement=None,printit=True):
 name=name.replace('.','_')
 assert shape.isValid() and len(shape.Solids)==1,(name,'invalid or disconnected',len(shape.Solids))
 SHAPES[name]=shape;COLORS[name]=color;OWNERS[name]=owner
 if printit:PRINT[name]=shape
 if local is not None:LOCAL[name]=(local,placement)
 return shape

def bolt_local(x,y,seat,length):
 # Screw solids are illustrative envelope dimensions, never manufacturing geometry.
 head=cut(disk(x,y,1.9,seat,seat+1.6),disk(x,y,.75,seat+.8,seat+1.7))
 return fuse(disk(x,y,.98,seat-length,seat+.01),head)
def hardware(name,x,y,seat,length,f,owner):
 HARD[name]=world(bolt_local(x,y,seat,length),f);OWNERS[name]=owner
 REPORT['mounts'].append(dict(name=name,owner=owner,screw='M2x%g'%length,seat_local_mm=seat,tip_local_mm=seat-length))

def boss(x,y):
 # Entire insert bore is in newly ADDED material. At least .8 mm above original skin.
 return cut(disk(x,y,3.5,-.10,4.8),disk(x,y,CFG['insert_bore']/2,.8,4.91),
            Part.makeCone(CFG['insert_bore']/2,CFG['insert_bore']/2+.3,.3,V(x,y,4.5)))

def add_to_owner(owner,local,f):
 global PARTS
 added=world(local,f)
 # This is the central invariant: no cutter may remove baseline shell material.
 log('pre-fuse',owner,PARTS[owner].isNull(),PARTS[owner].Volume,added.isNull(),added.Volume)
 q=fuse(PARTS[owner],added)
 assert common(q,BASESH[owner]).Volume>=BASESH[owner].Volume-1e-4,owner
 PARTS[owner]=q
 return added

try:
 # Freeze exact source bytes before building; source FCStd is opened only from the copy.
 protected=list(BASE.glob('*.FCStd'))+list(BASE.glob('*.stl'))+[BASE/'build_enclosure_v2.py',BASE/'verify_enclosure_v2.py',BASE/'validation.json',BASE/'removal-sweeps.json']
 snap=OUT/'baseline-v28';snap.mkdir(exist_ok=True)
 for p in protected:
  REPORT['source_hashes'][str(p.relative_to(ROOT))]=sha(p)
  dst=snap/p.name
  if dst.exists():assert sha(dst)==sha(p),'Baseline changed after snapshot'
  else:shutil.copy2(p,dst)
 G.activateWorkbench('PartWorkbench')
 source=A.openDocument(str(snap/'Gladiator_Enclosure_v2.FCStd'))
 BASESH={o.Name:clean(o.Shape) for o in source.Objects if hasattr(o,'Shape') and not o.Shape.isNull()}
 PARTS={n:BASESH[n].copy() for n in ('Rear_Hood','Front_Left','Front_Right','Lens_Plate')}
 log('frozen source',len(BASESH))
 # Side tablets: raised receiver with real 1.0-deep locating pocket, no wall recess.
 tp=[(-23,-8),(23,-8),(23,-4.5),(31,-6),(31,6),(23,4.5),(23,8),(-23,8),(-23,4.5),(-31,6),(-31,-6),(-23,-4.5)]
 tp_outer=[(x*1.016,y*1.08) for x,y in tp]
 for side,x,U,N in [('L',-9,(0,-1,0),(-1,0,0)),('R',88,(0,1,0),(1,0,0))]:
  f=frame((x,21,70),U,N)
  seat=poly(tp_outer,-.08,5.8)
  pocket=poly([(x*1.008,y*1.035) for x,y in tp],4.8,6.0)
  seat=cut(seat,pocket)
  for u in(-27,27):seat=fuse(seat,boss(u,0))
  for u in(-27,27):seat=cut(seat,disk(u,0,CFG['insert_bore']/2,.8,4.91))
  add_to_owner('Rear_Hood',seat,f)
  tablet=poly(tp,4.8,6.3)
  for u in(-27,27):tablet=cut(tablet,disk(u,0,1.3,4.7,6.5))
  add('Tablet_'+side,world(tablet,f),WHITE,'Rear_Hood',tablet,f)
  # Outline font is CAD geometry. Closed counterforms remain white, not loose parts.
  font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
  wires=Part.makeWireString('GLADIATOR',font,6.0,0)
  glyphs=[]
  for char in wires:
   if char:
    faces=Part.makeFace(char,'Part::FaceMakerBullseye')
    glyphs.append(faces.extrude(V(0,0,.6)))
  text=Part.makeCompound(glyphs);bb=text.BoundBox
  m=A.Matrix();m.A11=40.5/bb.XLength;m.A22=5.9/bb.YLength
  text=text.transformGeometry(m);bb=text.BoundBox;text.translate(V(-bb.Center.x,-bb.Center.y,6.3))
  SHAPES['Letters_'+side]=world(text,f);COLORS['Letters_'+side]=RED;OWNERS['Letters_'+side]='Rear_Hood'
  # Letters are fused through a buried 0.6 web, permitting one face-up colour swap.
  backing=poly(tp,4.8,6.3)
  for u in(-27,27):backing=cut(backing,disk(u,0,1.3,4.7,7.0))
  lettered=fuse(backing,text)
  PRINT['Tablet_'+side]=world(lettered,f)
  LOCAL['Tablet_'+side]=(lettered,f)
  for j,u in enumerate((-27,27)):hardware('Tablet_%s_M2_%d'%(side,j),u,0,6.3,4,f,'Rear_Hood')
 log('tablets')
 # Scutum red fields, white pre-curved winged fulmen and silk bosses.
 w,h=27.3,41.6
 outline=[(-w/2+2,-h/2), (w/2-2,-h/2),(w/2,-h/2+2),(w/2,h/2-2),(w/2-2,h/2),(-w/2+2,h/2),(-w/2,h/2-2),(-w/2,-h/2+2)]
 cycenter=6.25-28.0
 def curved_cyl(radius):return Part.makeCylinder(radius,h+8,V(0,-h/2-4,cycenter),V(0,1,0))
 outerc=curved_cyl(28.0);whiteouter=curved_cyl(28.6);whiteinner=curved_cyl(27.6)
 # Rim and ring plus four arrow-tipped bolts. All are joined to the rim/ring.
 rim=cut(poly(outline,0,10),poly([(x*.845,y*.90) for x,y in outline],-.1,10.1))
 ring=cut(disk(0,0,5.0,0,10),disk(0,0,3.0,-.1,10.1))
 pattern=[rim,ring]
 for sx in(-1,1):
  for sy in(-1,1):
   pts=[(sx*3,sy*3),(sx*6,sy*7),(sx*4.8,sy*9),(sx*8.5,sy*13),(sx*8,sy*15),(sx*11.9,sy*19.5)]
   pattern.append(strokeline(pts,1.15,0,10))
   pattern.append(poly([(sx*11.9,sy*19.9),(sx*8.2,sy*18.3),(sx*11.6,sy*15.7)],0,10))
  for j in range(4):
   pattern.append(feather((sx*3.5,1.5+j*.45),(sx*(11.8-j*.65),5.5+j*1.55),1.65,0,10))
 pattern=fuse(*pattern)
 clearance_parts=[cut(poly(outline,0,10),poly([(x*.834,y*.892) for x,y in outline],-.1,10.1)),cut(disk(0,0,5.15,0,10),disk(0,0,2.85,-.1,10.1))]
 for sx in(-1,1):
  for sy in(-1,1):
   pts=[(sx*3,sy*3),(sx*6,sy*7),(sx*4.8,sy*9),(sx*8.5,sy*13),(sx*8,sy*15),(sx*11.9,sy*19.5)]
   clearance_parts.append(strokeline(pts,1.45,0,10))
   arr=[(sx*11.9,sy*19.9),(sx*8.2,sy*18.3),(sx*11.6,sy*15.7)]
   clearance_parts.append(fuse(poly(arr,0,10),strokeline(arr+[arr[0]],.30,0,10)))
  for j in range(4):
   tip=(sx*(11.8-j*.65),5.5+j*1.55)
   clearance_parts.append(fuse(feather((sx*3.5,1.5+j*.45),tip,1.95,0,10),disk(tip[0],tip[1],.15,0,10)))
 clearance_pattern=fuse(*clearance_parts)
 white=common(pattern,cut(whiteouter,whiteinner))
 # A continuous central annulus joins every feature and is mechanically clamped by the boss.
 white=cut(white,disk(0,0,1.3,0,11))
 for side,cx,owner in [('L',16,'Front_Left'),('R',63,'Front_Right')]:
  f=frame((cx,148,79),( -1,0,0),(0,1,0))
  field=common(poly(outline,1.2,8),outerc)
  field=cut(field,common(clearance_pattern,cut(outerc,whiteinner)),disk(0,0,3.75,1.1,4.95),disk(0,0,1.3,4.8,8))
  # Full outline lower seat plus .25 per-side pocket border; .3 lead-in at the back of the field.
  lower=poly([(x*1.025,y*1.018) for x,y in outline],-.08,1.2)
  border=cut(poly([(x*1.025,y*1.018) for x,y in outline],1.19,2.0),poly([(x*1.018,y*1.012) for x,y in outline],1.1,2.2))
  seat=fuse(lower,border,boss(0,0))
  seat=cut(seat,disk(0,0,CFG['insert_bore']/2,.8,4.91))
  add_to_owner(owner,seat,f)
  add('Scutum_Field_'+side,world(field,f),RED,owner,field,f)
  add('Scutum_Emblem_'+side,world(white,f),WHITE,owner,white,f)
  # Silk dome's bearing face follows the same cylinder as the white ring.
  dome=Part.makeSphere(4.25,V(0,0,6.55))
  dome=common(dome,box(-5,5,-5,5,6.5,9.2))
  dome=cut(dome,whiteouter,disk(0,0,1.3,5,10),disk(0,0,2.25,7.15,10))
  add('Scutum_Boss_'+side,world(dome,f),GOLD,owner,dome,f)
  hardware('Scutum_%s_M2'%side,0,0,7.15,6,f,owner)
 log('curved scuta')
 # Aquila: smooth curved primary feathers, shoulder coverts, layered breast, tail and hooked beak.
 eagleparts=[]
 for sx in(-1,1):
  for j in range(7):
   eagleparts.append(relief_feather((sx*(3.0+j*.42),1.3-j*.38),(sx*(20.8-j*1.35),8.7-j*1.65),2.6,4.8,6.15+j*.09))
  for j in range(5):
   eagleparts.append(relief_feather((sx*2.1,1.2),(sx*(13.8-j*1.3),7.2-j*1.5),2.65,6.0,6.85+j*.10))
  eagleparts.append(ellipse(sx*4.8,2.1,3.5,3.4,4.8,6.8))
 eagleparts.append(ellipse(0,.3,3.35,5.4,4.8,5.8))
 eagleparts.append(common(dome3(0,.3,5.7,3.35,5.4,2.6),box(-5,5,-6,6,4.8,9)))
 for x in(-1.65,0,1.65):eagleparts.append(feather((x,0),(x*1.3,-7.0+abs(x)*.4),2.2,4.8,6.3))
 # Curved neck swept to one side, a brow, hooked beak, and a recessed .7 mm eye.
 eagleparts.append(strokeline([(0,3.4),(.15,4.6),(.6,5.8),(.5,6.7)],2.7,4.8,7.2))
 eagleparts.append(ellipse(.35,6.85,2.15,1.75,4.8,6.0))
 eagleparts.append(common(dome3(.35,6.85,6.0,2.15,1.75,1.8),box(-3,3,4.5,9,4.8,8.5)))
 eagleparts.append(poly([(-.4,8.25),(-3.0,7.7),(-3.2,6.1),(-2.1,6.7),(-.8,6.8)],5.3,7.65))
 # Sculpted breast scallops are relief, not isolated screen-like etched squares.
 for row in range(0):
  for j in range(3):
   u=(j-1)*1.35+(row%2)*.3
   eagleparts.append(feather((u,3.3-row*1.5),(u+.1,1.35-row*1.5),1.55,6.8,7.35+(.22 if j==1 else 0)))
 # Fulmen spindle gripped by two feet, symmetric four forked lightning strokes.
 eagleparts.append(poly([(-4,-6.0),(-2,-4.9),(2,-4.9),(4,-6.0),(2,-6.9),(-2,-6.9)],4.8,6.8))
 for sx in(-1,1):
  eagleparts.append(strokeline([(sx*1.7,-2.7),(sx*2.5,-4.8),(sx*1.5,-6.1)],1.2,4.8,7.25))
  for dy in(-1,1):
   pts=[(sx*3.2,-6),(sx*6,-6+dy*1.3),(sx*7.4,-6+dy*.4),(sx*10.5,-6+dy*2.3)]
   eagleparts.append(strokeline(pts,1.2,4.8,6.5))
   eagleparts.append(poly([(sx*11.4,-6+dy*2.9),(sx*8.7,-6+dy*2.5),(sx*10.4,-6+dy*.7)],4.8,6.5))
 eagle=fuse(*eagleparts)
 eagle=cut(eagle,disk(-.25,7.15,.35,7.35,8.3))
 for row in range(3):
  for sign in(-1,1):
   groove=strokeline([(sign*.35,2.5-row*1.6),(sign*1.4,1.9-row*1.6),(sign*2.4,2.2-row*1.6)],.45,7.25,8.5)
   eagle=cut(eagle,groove)
 for u in(-6,6):eagle=cut(eagle,disk(u,2,1.45,4.7,5.95))
 eagle=cut(eagle,disk(0,0,1.3,4.7,9),disk(0,0,2.25,7.4,9))
 ef=frame((26,-32,68.5),(1,0,0),(0,-1,0))
 es=fuse(boss(0,0),disk(-6,2,3.0,-.08,4.8),disk(6,2,3.0,-.08,4.8),box(-6,6,.8,3.2,-.08,4.8))
 for u in(-6,6):es=fuse(es,disk(u,2,1.2,4.7,5.8))
 # Three broad support lands stop the wings and tail rocking, independently of slip-fit clearance.
 for u,v,r in[(-14,3,2),(14,3,2),(0,-5,2)]:es=fuse(es,disk(u,v,r,-.08,4.8),strokeline([(0,2),(u,v)],1.6,-.08,1.1))
 es=cut(es,disk(0,0,CFG['insert_bore']/2,.8,4.91))
 add_to_owner('Rear_Hood',es,ef)
 add('Aquila_Relief',world(eagle,ef),GOLD,'Rear_Hood',eagle,ef)
 hardware('Aquila_Centre_M2',0,0,7.4,6,ef,'Rear_Hood')
 log('aquila relief')
 # Lorica lips: preserve every original vent's size, position and full straight airflow opening.
 # Original openings Z88..90.4,92.8..95.2,97.6..100; bands adapt around those.
 rf=frame((0,-32,0),(1,0,0),(0,-1,0))
 for i,(z0,z1) in enumerate([(81,87.4),(90.4,92.2),(95.2,97.0),(100,103)]):
  # Local cross section in (height, outward depth), 45-degree roof-down lead.
  lx=1.0 if i==3 else -3.0
  pts=[V(lx,z0,-.08),V(lx,z1,-.08),V(lx,z1,0),V(lx,max(z0,z1-1.2),1.2),V(lx,z0,1.2)]
  lam=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(55-lx,0,0))
  add_to_owner('Rear_Hood',lam,rf)
 log('lorica')
 # Head adornments are new removable clamps. Existing yoke/receiver/display are not edited.
 # The guide's 'top bar of yoke' does not exist in this model: clamp actual receiver/carrier top instead.
 # Crest clamp: rear jaw with sideways M2 insert, front lip above the ToF frame, bridge .2 above head.
 saddle=fuse(box(33.5,45.5,155.8,160.75,236.8,241.1),box(33.5,45.5,171.25,173.25,236.8,241.1),
             box(33.5,45.5,155.8,173.25,238.7,241.1),box(36,43,156,169,241.09,244.0))
 saddle=cut(saddle,Part.makeCylinder(CFG['insert_bore']/2,4.1,V(39.5,155.7,237.8),V(0,1,0)),
            Part.makeCylinder(CFG['insert_bore']/2,4,V(39.5,163,240.1)))
 # Dovetail-like longitudinal register: no spring bumps and no modifications to head.
 saddle=cut(saddle,box(37.3,41.7,157,167,242.0,244.1))
 saddle=fuse(saddle,disk(39.5,163,3.4,238.7,244.0))
 saddle=cut(saddle,disk(39.5,163,CFG['insert_bore']/2,240.1,244.1))
 saddle=cut(saddle,box(37.15,41.85,159.9,161.1,236.15,239.45),Part.makeCylinder(1.3,1,V(39.5,159.7,237.8),V(0,1,0)))
 add('Crest_Clamp',saddle,BLACK,'Head_tilt',saddle,None)
 shoe=box(37.3,41.7,160,161,236.3,239.3)
 add('Crest_Clamp_Shoe',shoe,BLACK,'Head_tilt',shoe,None)
 # Red brush, front-to-back arch. Every groove remains >=.7, with a 1.2 mm perimeter.
 yz=[(110,244),(171,244),(171,249),(165,258),(153,269),(142,272),(130,269),(119,260),(110,250)]
 pts=[V(37.1,y,z) for y,z in yz]
 crest=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(4.8,0,0))
 crest=fuse(crest,box(37.5,41.5,157.3,166.7,242.2,244.1))
 crest=cut(crest,box(36.9,42.1,109,117,243.9,245.2))
 for y in range(113,170,2):
  # .65 wide, shallow grooves; no sub-nozzle individual bristles.
  crest=cut(crest,box(37.0,37.65,y,y+.65,249,273),box(41.35,42,y,y+.65,249,273))
 crest=cut(crest,Part.makeCylinder(1.3,12,V(39.5,163,241)),Part.makeCylinder(2.25,30,V(39.5,163,246.5)),disk(39.5,163,3.65,242,244.0))
 add('Galea_Crest',crest,RED,'Head_tilt',crest,None)
 # Thin silk holder cover is decorative; black clamp carries the screw load.
 holder=cut(box(34.7,44.3,155.0,170.0,241.1,244.0),box(35.7,43.3,155.8,169.2,241,244.2))
 # Open-ended U cover requires a rear bridge to remain a single printed part.
 add('Crest_Holder_Trim',holder,GOLD,'Head_tilt',holder,None)
 hf=frame((39.5,163,0),(1,0,0),(0,-1,0)) # unused: crest hardware is world-Z below
 HARD['Crest_Top_M2']=bolt_local(39.5,163,246.5,6);OWNERS['Crest_Top_M2']='Head_tilt'
 clampbolt=bolt_local(39.5,237.8,0,5)
 cf=frame((0,155.0,0),(1,0,0),(0,-1,0))
 HARD['Crest_Clamp_M2']=world(clampbolt,cf);OWNERS['Crest_Clamp_M2']='Head_tilt'
 # Rear neck guard: two clamps on the actual display top rail, no screen obstruction.
 guards=[]
 for x in(21.5,57.5):
  q=fuse(box(x-4,x+4,101.8,106.55,234,243.2),box(x-4,x+4,114.25,116.25,234,243.2),box(x-4,x+4,101.8,116.25,238.7,243.2))
  q=cut(q,Part.makeCylinder(CFG['insert_bore']/2,4.1,V(x,101.7,236.7),V(0,1,0)),disk(x,110,CFG['insert_bore']/2,239.2,243.3))
  q=cut(q,box(x-2.65,x+2.65,105.65,106.9,235.05,238.35))
  guards.append(q)
  shoe=box(x-2.5,x+2.5,105.8,106.8,235.2,238.2)
  add('Neck_Clamp_Shoe_%g'%x,shoe,BLACK,'Head_tilt',shoe,None)
  HARD['Neck_Clamp_M2_%g'%x]=world(bolt_local(x,236.7,0,5),frame((0,100.8,0),(1,0,0),(0,-1,0)));OWNERS['Neck_Clamp_M2_%g'%x]='Head_tilt'
  HARD['Neck_Guard_M2_%g'%x]=bolt_local(x,110,244.2,4);OWNERS['Neck_Guard_M2_%g'%x]='Head_tilt'
 for i,q in enumerate(guards):add('Neck_Clamp_%d'%i,q,BLACK,'Head_tilt',q,None)
 guard=fuse(box(8,71,101.3,116.2,243.2,244.2),box(8,71,101.3,102.3,235.8,243.3))
 # Corners of the flare are simple 45-degree cuts, all hardware above the active screen.
 for x in(21.5,57.5):
  guard=cut(guard,disk(x,110,1.3,243,245),box(x-4.15,x+4.15,101.2,102.45,235.7,243.2))
 add('Neck_Guard',guard,GOLD,'Head_tilt',guard,None)
 log('head adornments')
 # Register shell parts after all additive updates.
 for n,s in PARTS.items():add(n,s,WHITE if n=='Lens_Plate' else GREY,n,printit=True)
 # Build document with exact unchanged context shapes.
 doc=A.newDocument('Gladiator_Round5')
 for group in('Styled_Shell','Insets','Head_Adornments','Hardware','Context'):
  doc.addObject('App::DocumentObjectGroup',group)
 for n,s in SHAPES.items():
  o=doc.addObject('Part::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=COLORS[n];o.ViewObject.LineColor=(.1,.1,.1);o.ViewObject.DisplayMode='Flat Lines'
  o.addProperty('App::PropertyString','AssemblyOwner','Round 5');o.AssemblyOwner=OWNERS[n]
  o.addProperty('App::PropertyString','ManufacturingNotes','Round 5')
  o.ManufacturingNotes='Review geometry; M2 insert calibration pending. Additive seats preserve baseline wall.'
  group='Styled_Shell' if n in PARTS else ('Head_Adornments' if OWNERS[n].startswith('Head') else 'Insets')
  doc.getObject(group).addObject(o)
 for n,s in HARD.items():
  o=doc.addObject('Part::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.25,.24,.22);doc.Hardware.addObject(o)
 for n,s in BASESH.items():
  if n in PARTS:continue
  o=doc.addObject('Part::Feature',n);o.Shape=s;doc.Context.addObject(o)
  o.ViewObject.ShapeColor=BLACK if n.startswith('Head_') or n=='Ref_MastTube' else ((.65,.68,.70) if 'Fins' in n else (.24,.27,.30))
  if 'envelope' in n.lower() or 'Envelope' in n or 'Board' in n or 'Reference' in n:o.ViewObject.Visibility=False
  if n.startswith(('Track','Wheel')):o.ViewObject.ShapeColor=(.1,.11,.12)
 # Per-face colours for cap and belt: no redundant overlay solids or altered fit surfaces.
 for n in('Rear_Hood','Front_Left','Front_Right'):
  o=doc.getObject(n);roof=111.9 if n=='Rear_Hood' else 108.0
  cols=[]
  for face in o.Shape.Faces:
   z=face.CenterOfMass.z
   cols.append(RED if (z>=roof-12 or 50<=z<=56) else GREY)
  o.ViewObject.DiffuseColor=cols
 doc.Comment='Round 5 styling of frozen enclosure v2.8; original wall and interfaces retained. Additive external receivers, screw-retained badges, removable head clamps. See validation.json.'
 doc.recompute();G.setActiveDocument(doc.Name);A.setActiveDocument(doc.Name)
 G.getMainWindow().resize(1800,1400);G.updateGui()
  # Display only: partition exact shell geometry into colour regions. Manufacturing meshes remain one solid.
 appearance=doc.addObject('App::DocumentObjectGroup','Colour_Regions')
 for owner in('Rear_Hood','Front_Left','Front_Right'):
  roof=111.9 if owner=='Rear_Hood' else 108.0
  ranges=[('Lower',-20,50,GREY),('Belt',50,56,RED),('Wall',56,roof-12,GREY),('Cap',roof-12,130,RED)]
  for tag,z0,z1,col in ranges:
   region=common(PARTS[owner],box(-200,200,-200,250,z0,z1))
   if region.Volume<1e-6:continue
   obj=doc.addObject('Part::Feature','Appearance_'+owner+'_'+tag);obj.Shape=region;obj.ViewObject.ShapeColor=col
   obj.ViewObject.DisplayMode='Flat Lines';obj.ViewObject.LineColor=(.13,.14,.15);appearance.addObject(obj)
  doc.getObject(owner).ViewObject.Visibility=False
 # Shell's source object stays available for exact checks and export, hidden behind exact colour-region display.
 doc.recompute()
 doc.saveAs(str(OUT/'Gladiator_Round5.FCStd'))
 # Export shell and separate parts in world coordinates and print-oriented individual meshes.
 exportdoc=A.newDocument('Round5_Manufacturing_Export');exportobjects=[]
 for n,s in PRINT.items():
  obj=exportdoc.addObject('Part::Feature',n);obj.Shape=s;exportobjects.append(obj)
 Part.export(exportobjects,str(OUT/'Gladiator_Round5_PrintParts.step'))
 A.setActiveDocument(doc.Name);G.setActiveDocument(doc.Name)
 for n,s in PRINT.items():
  if n in LOCAL and LOCAL[n][1] is not None:
   s=LOCAL[n][0].copy()
   # Curved fields/emblems stand on the lower shield edge; all others have flat backs down.
   if n.startswith(('Scutum_Field','Scutum_Emblem')):s.rotate(V(),V(1,0,0),90)
  else:
   s=s.copy()
   if n in PARTS:s.rotate(V(),V(1,0,0),180)
   elif n=='Galea_Crest':s.rotate(V(),V(0,1,0),90)
   elif '_Shoe' in n:s.rotate(V(),V(1,0,0),90)
  b=s.BoundBox;s.translate(V(-b.XMin,-b.YMin,-b.ZMin))
  mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.015,AngularDeflection=.07,Relative=False)
  if not mesh.isSolid():
   import Mesh,collections
   pts,faces=mesh.Topology
   edges=collections.Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3))
   ids=sorted({j for e,c in edges.items() if c==1 for j in e})
   assert ids and max((pts[j]-pts[ids[0]]).Length for j in ids)<.001,'Mesh boundary exceeds microscopic repair limit: '+n
   rep={j:ids[0] for j in ids};tri=[]
   for f in faces:
    ff=tuple(rep.get(j,j) for j in f)
    if len(set(ff))==3:tri.append([pts[j] for j in ff])
   mesh=Mesh.Mesh(tri);mesh.harmonizeNormals()
  assert mesh.isSolid() and not mesh.hasNonManifolds(),n
  mesh.write(str(OUT/'stl'/('%s.stl'%n)))
  b=s.BoundBox
  REPORT['parts'][n]=dict(valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,mesh_solid=mesh.isSolid(),mesh_nonmanifold=mesh.hasNonManifolds(),size_mm=[b.XLength,b.YLength,b.ZLength])
 # Exact material-preservation tests plus exterior-only addition tests.
 for n in PARTS:
  lost=cut(BASESH[n],PARTS[n]).Volume
  REPORT['baseline_preservation'][n]=dict(removed_mm3=lost,added_mm3=cut(PARTS[n],BASESH[n]).Volume)
  assert lost<1e-4,(n,lost)
 for p in protected:assert sha(p)==REPORT['source_hashes'][str(p.relative_to(ROOT))],str(p)
 REPORT['source_files_unchanged']=True
 REPORT['status']='Geometry built; independent verification required'
 (OUT/'validation.json').write_text(json.dumps(REPORT,indent=2))
 # Previews, including eagle detail in isolation, without saving visibility changes.
 view=G.activeDocument().activeView()
 def shot(name,direction,only=None):
  for o in doc.Objects:
   if not hasattr(o,'Shape'):continue
   o.ViewObject.Visibility=only is None or o.Name in only
   if o.Name in('Rear_Hood','Front_Left','Front_Right'):o.ViewObject.Visibility=False
   if only is None and (o.Name.startswith(('Ref_Board','Ref_S3','Ref_Bread')) or 'envelope' in o.Name.lower() or o.Name.endswith('Reference')):o.ViewObject.Visibility=False
  dv=V(*direction);dv.normalize();up=V(0,0,1);right=dv.cross(up);right.normalize();top=right.cross(dv);top.normalize()
  view.setCameraType('Orthographic');view.setCameraOrientation(A.Rotation(right,top,-dv,'ZXY'));G.updateGui();view.fitAll();G.updateGui();view.fitAll();view.saveImage(str(OUT/name),1600,1200,'White')
 shot('round5-front.png',(-1,-1.4,-.7))
 shot('round5-rear.png',(1,1.5,-.65))
 shot('round5-side.png',(-1,0,-.12))
 shot('aquila-detail.png',(0,1,-.22),['Aquila_Relief','Aquila_Centre_M2'])
 shot('scutum-detail.png',(-.3,-1,-.2),['Scutum_Field_R','Scutum_Emblem_R','Scutum_Boss_R'])
 shot('head-detail.png',(-1,-1,-.5),[n for n in BASESH if n.startswith('Head_')]+[n for n in SHAPES if OWNERS[n].startswith('Head')])
 log('DONE',len(PRINT),'print parts')
except BaseException:
 (OUT/'BUILD_ERROR.txt').write_text(traceback.format_exc());traceback.print_exc()
os._exit(0)











