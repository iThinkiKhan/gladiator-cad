"""Isolated mast wiring review, FreeCAD 1.0. Dimensions in mm; source CAD untouched."""
import sys,json,math,hashlib
from pathlib import Path
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A
import Part,Mesh,MeshPart
V=A.Vector
ROOT=Path('/home/buralien/projects/gladiator-cad')
BASE=ROOT/'cad/head/v2-mast-20261028'
OUT=BASE/'closed-tube-review-20261030'
OUT.mkdir(exist_ok=True)
WORLD=V(39.5,113,0)
def cyl(r,z,h): return Part.makeCylinder(r,h,V(0,0,z))
def cross(r,z): return Part.makeCylinder(r,24,V(-12,0,z),V(1,0,0))
def profile(y,w,h,r):
    x0,x1,z0,z1=-w/2,w/2,30-h/2,30+h/2
    k=1-math.sqrt(.5)
    def p(x,z): return V(x,y,z)
    es=[Part.makeLine(p(x0+r,z0),p(x1-r,z0)),Part.Arc(p(x1-r,z0),p(x1-r*k,z0+r*k),p(x1,z0+r)).toShape(),Part.makeLine(p(x1,z0+r),p(x1,z1-r)),Part.Arc(p(x1,z1-r),p(x1-r*k,z1-r*k),p(x1-r,z1)).toShape(),Part.makeLine(p(x1-r,z1),p(x0+r,z1)),Part.Arc(p(x0+r,z1),p(x0+r*k,z1-r*k),p(x0,z1-r)).toShape(),Part.makeLine(p(x0,z1-r),p(x0,z0+r)),Part.Arc(p(x0,z0+r),p(x0+r*k,z0+r*k),p(x0+r,z0)).toShape()]
    return Part.Wire(es)
source=BASE/'Gladiator_Head_v2_Mast.FCStd'
before=hashlib.sha256(source.read_bytes()).hexdigest()
src=A.openDocument(str(source))
old=src.getObject('Mast_Tube_v2').Shape.copy(); old.translate(-WORLD)
shell=cyl(10,6,144).cut(cyl(6,5,146))
shell=shell.cut(Part.makeBox(30,10,42,V(-15,9.1,111)))
shell=shell.cut(Part.makeCone(6.7,6,.7,V(0,0,6)))
shell=shell.cut(Part.makeCone(6,6.7,.7,V(0,0,149.3)))
inlet=Part.makeLoft([profile(3,11.6,13.6,2.8),profile(7.5,10,12,2),profile(11.5,11.6,13.6,2.8)],True,True)
shell=shell.cut(inlet)
plain=shell.cut(cross(1.8,13)).cut(cross(1.8,123)).removeSplitter()
# Smooth elliptical sleeve around the unchanged head bolt. 1.0-mm minimum wall.
ellipse=Part.Ellipse(V(-10,0,129),V(-10,2.8,123),V(-10,0,123)).toShape()
guard=Part.Face(Part.Wire([ellipse])).extrude(V(20,0,0)).common(cyl(10,116,14))
protected=shell.fuse(guard).cut(cross(1.8,13)).cut(cross(1.8,123)).removeSplitter()
variants={'Closed_Tube':plain,'Closed_Tube_Bolt_Guard':protected}
report={'status':'CAD REVIEW ONLY; not sliced or physically tested','source_sha256':before,'world_z':[6,150],'od_mm':20,'bore_mm':12,'lower_inlet_throat_mm':[10,12],'lower_inlet_max_world_z':[23.2,36.8],'bolt_axis_world_z':123,'guard_min_wall_mm':1.0,'guard_wire_round_gauge_each_side_mm':3.2,'variants':{},'limitations':['Guard is optional and divides the bore locally into two crescents; multiway connectors may not pass.','Actual harness count, connector clearance, abrasion, bridging and stiffness are untested.','No stiffness multiplier claimed and no load analysis performed.','Only saved home-pose assembly interference checked here; old head travel checks not rerun.']}
doc=A.newDocument('Gladiator_Closed_Mast_Review')
group=doc.addObject('App::DocumentObjectGroup','Assembly_Protected_Candidate')
for o in src.Objects:
    if o.TypeId!='Part::Feature': continue
    s=protected.copy() if o.Name=='Mast_Tube_v2' else o.Shape.copy()
    if o.Name=='Mast_Tube_v2': s.translate(WORLD)
    f=doc.addObject('Part::Feature',o.Name); f.Shape=s; group.addObject(f)
comparison=doc.addObject('App::DocumentObjectGroup','Comparison_Parts')
for name,s,x in [('Previous_Slotted_Tube',old,105),('Closed_Tube',plain,140),('Closed_Tube_Bolt_Guard',protected,175)]:
    assert s.isValid() and len(s.Solids)==1,name
    obj=doc.addObject('Part::Feature',name); obj.Shape=s.copy(); comparison.addObject(obj)
    obj.Placement.Base=V(x,113,0)
    m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.03,AngularDeflection=.15,Relative=False)
    m.write(str(OUT/(name+'.stl')))
    if name not in variants: continue
    back=Mesh.Mesh(str(OUT/(name+'.stl')))
    sw=s.copy(); sw.translate(WORLD)
    collisions=[]
    for o in src.Objects:
        if o.TypeId!='Part::Feature' or o.Name=='Mast_Tube_v2': continue
        if sw.BoundBox.intersect(o.Shape.BoundBox):
            vol=sw.common(o.Shape).Volume
            if vol>.05: collisions.append([o.Name,round(vol,4)])
    probes=[]
    for side in (-1,1):
        plug=Part.makeBox(2.84,2.84,20,V(-1.42,side*4.4-1.42,113))
        probes.append(round(s.common(plug).Volume,4))
    report['variants'][name]={'valid_solid':True,'mesh_solid':back.isSolid(),'mesh_non_manifold':back.hasNonManifolds(),'solid_pla_g':round(s.Volume*.00124,2),'added_solid_pla_g':round((s.Volume-old.Volume)*.00124,2),'home_collisions':collisions,'single_2p54_square_housing_with_0p15_clearance_overlap_mm3':probes}
    assert not collisions,(name,collisions)
    assert back.isSolid() and not back.hasNonManifolds()
    # Export a part at origin, independent of comparison object placement.
    tmp=doc.addObject('Part::Feature','Export_'+name);tmp.Shape=s.copy()
    Part.export([tmp],str(OUT/(name+'.step')));doc.removeObject(tmp.Name)
cut=protected.cut(Part.makeBox(30,40,160,V(0,-20,0)))
f=doc.addObject('Part::Feature','Guard_Cutaway');f.Shape=cut;f.Placement.Base=V(210,113,0)
doc.recompute();doc.saveAs(str(OUT/'Gladiator_Closed_Mast_Review.FCStd'))
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
report['original_cad_unchanged']=True
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
preview={}
for name,s in [('Slotted',old),('Closed',plain),('Protected',protected),('Cutaway',cut)]:
    m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.1,AngularDeflection=.25,Relative=False)
    preview[name]=[[list(v) for v in f.Points] for f in m.Facets]
(OUT/'preview_meshes.json').write_text(json.dumps(preview))
A.closeDocument(doc.Name);A.closeDocument(src.Name)
print(json.dumps(report,indent=2))

