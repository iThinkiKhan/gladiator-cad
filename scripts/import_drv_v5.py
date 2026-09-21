import sys, math, shutil, datetime, json
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad/Mod','/usr/lib/freecad-python3/lib'])
import FreeCAD as A, Part
from pathlib import Path
ROOT=Path('/home/buralien/projects/gladiator-cad')
MASTER=ROOT/'cad/master/Gladiator_Master.FCStd'
V5=ROOT/'cad/drivers/v5-interlock/DriverMount_v5.FCStd'
O=[]
def p(s): O.append(s)
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
bak=ROOT/('cad/master/drafts/Gladiator_Master.%s.pre-drv-v5.FCStd'%stamp)
bak.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(MASTER,bak)
p('backup -> %s'%bak.name)

CANT,X0,Z0,STANDOFF=45.0,8.0,100.0,15.0
BU,BV=49.5,51.0; HS_V0,HS_V1,HS_U0,HS_U1=9.5,41.5,8.75,40.75
PCB_T,HS_PROUD=3.2,28.0
th=math.radians(CANT)
N=A.Vector(-math.sin(th),0,math.cos(th)); VV=A.Vector(-math.cos(th),0,-math.sin(th))
ORG=A.Vector(X0,90.0,Z0)
def at(u,v,w=0.0):
    return A.Vector(ORG.x+VV.x*v+N.x*w, ORG.y+u, ORG.z+VV.z*v+N.z*w)
def mirror(s):
    m=s.copy(); m.transformShape(A.Matrix(-1,0,0,79.0, 0,1,0,0, 0,0,1,0)); return m

src=A.openDocument(str(V5))
base=src.getObject('Base_Left').Shape.copy()
wedge=src.getObject('Wedge_Left').Shape.copy()
board=Part.Face(Part.makePolygon([at(0,0),at(BU,0),at(BU,BV),at(0,BV),at(0,0)])).extrude(
    A.Vector(N.x*PCB_T,N.y*PCB_T,N.z*PCB_T))
fins=Part.Face(Part.makePolygon([at(HS_U0,HS_V0,PCB_T),at(HS_U1,HS_V0,PCB_T),
    at(HS_U1,HS_V1,PCB_T),at(HS_U0,HS_V1,PCB_T),at(HS_U0,HS_V0,PCB_T)])).extrude(
    A.Vector(N.x*HS_PROUD,N.y*HS_PROUD,N.z*HS_PROUD))

d=A.openDocument(str(MASTER))
grp=d.getObject('DriverV5') or d.addObject('App::DocumentObjectGroup','DriverV5')
grp.Label='Driver mount v5 - two piece, 45 deg, standoffs'
added=[]
for nm,lab,sh,col in [
    ('DrvV5_Base_L','v5 base, left',base,(0.35,0.45,0.55)),
    ('DrvV5_Wedge_L','v5 wedge, left',wedge,(0.18,0.56,0.60)),
    ('DrvV5_Base_R','v5 base, right',mirror(base),(0.35,0.45,0.55)),
    ('DrvV5_Wedge_R','v5 wedge, right',mirror(wedge),(0.18,0.56,0.60)),
    ('DrvV5_Board_L','v5 driver PCB, left',board,(0.25,0.35,0.72)),
    ('DrvV5_Fins_L','v5 heatsink, left',fins,(0.65,0.67,0.70)),
    ('DrvV5_Board_R','v5 driver PCB, right',mirror(board),(0.25,0.35,0.72)),
    ('DrvV5_Fins_R','v5 heatsink, right',mirror(fins),(0.65,0.67,0.70))]:
    old=d.getObject(nm)
    if old: d.removeObject(nm)
    o=d.addObject('Part::Feature',nm); o.Label=lab; o.Shape=sh
    if 'ViewObject' in dir(o) and o.ViewObject: 
        try: o.ViewObject.ShapeColor=col
        except Exception: pass
    grp.addObject(o); added.append(nm)
p('added %d objects into group DriverV5'%len(added))

hidden=[]
for nm in ['DriverMountLeft','DriverMountRight','DriverBoardLeft','DriverBoardRight']:
    o=d.getObject(nm)
    if o and o.ViewObject:
        try:
            o.ViewObject.Visibility=False; hidden.append(nm)
        except Exception: pass
p('hidden (NOT deleted): %s'%hidden)

d.recompute()
d.save()
p('saved master')

# sanity: new parts must not clash with the robot
def hit(a,b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox): return 0.0
        return a.common(b).Volume
    except Exception: return 0.0
bad={}
for nm in added:
    s=d.getObject(nm).Shape
    for on in ['UpperDeck','SideRailLeft','SideRailRight','ChassisDeck','BatteryBox',
               'MastTube','MastBase','PowerShield','AntennaPost','S3Board','Breadboard']:
        oo=d.getObject(on)
        if not oo or not getattr(oo,'Shape',None) or oo.Shape.isNull(): continue
        v=hit(s,oo.Shape)
        if v>0.05: bad['%s/%s'%(nm,on)]=round(v,1)
p('clashes against the robot: %s'%(bad or 'none'))
open('/tmp/imp.txt','w').write(chr(10).join(O))
