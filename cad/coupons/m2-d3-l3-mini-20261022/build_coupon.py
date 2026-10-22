"""FreeCAD GUI Python. Outputs beside script. All lengths mm."""
from pathlib import Path
import json, os, traceback
import FreeCAD as A
import FreeCADGui as Gui
import Part, MeshPart, Draft
O = Path(__file__).resolve().parent
V = A.Vector
BORES = [2.8, 2.9, 3.0, 3.1]
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
DEPTH, LEAD, TOP = 3.6, .15, 6.0

def label(doc, text, x, y, z, size=2.2, center=True):
    obj = Draft.makeShapeString(String=text, FontFile=FONT, Size=size, Tracking=0)
    doc.recompute()
    shape = obj.Shape.copy()
    bb = shape.BoundBox
    shape.translate(V(x-(bb.XMin+bb.XMax)/2 if center else x-bb.XMin, y-bb.YMin, z-bb.ZMin))
    result = shape.extrude(V(0,0,.4))
    doc.removeObject(obj.Name)
    return result

try:
    doc = A.newDocument('M2_D3_L3_Fit_Coupon')
    s = Part.makeBox(40,13,1.8)
    sites = []
    for i, diameter in enumerate(BORES):
        s = s.fuse(Part.makeCylinder(3.5,4.2,V(5+10*i,8,1.8)))
    clip = Part.Face(Part.makePolygon([V(0,0,-1),V(2,0,-1),V(0,2,-1),V(0,0,-1)]))
    s = s.cut(clip.extrude(V(0,0,13)))
    for i, diameter in enumerate(BORES):
        x, r = 5+10*i, diameter/2
        s = s.cut(Part.makeCylinder(r,DEPTH+.02,V(x,8,TOP-DEPTH)))
        s = s.cut(Part.makeCone(r,r+LEAD,LEAD+.001,V(x,8,TOP-LEAD)))
        s = s.fuse(label(doc,f'{diameter:.1f}',x,1.7,1.79))
        sites += [dict(id=f'V{i+1}',diameter_mm=diameter,axis=[0,0,-1],entry_mm=[x,8,6],depth_mm=DEPTH)]
    s = s.removeSplitter()
    assert s.isValid() and len(s.Solids)==1
    obj = doc.addObject('PartDesign::Feature','Coupon')
    obj.Label = 'M2 D3 L3 - 2.80 to 3.10 - depth 3.60'
    obj.Shape = s
    for key,val in [('InsertOD',3.0),('InsertLength',3.0),('BoreDepth',DEPTH),('EntryChamfer',LEAD),('BossOD',7.0)]:
        obj.addProperty('App::PropertyLength',key,'Coupon dimensions'); setattr(obj,key,val)
    obj.addProperty('App::PropertyString','Provenance','Coupon dimensions')
    obj.Provenance = 'User listing screenshot 2026-10-22: M2 x D3 x L3. Provisional until stock checked.'
    obj.ViewObject.ShapeColor = (.82,.59,.23)
    doc.recompute()
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    Gui.activeDocument().activeView().saveImage(str(O/'preview.png'),1800,1000,'White')
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    doc.saveAs(str(O/'M2_D3_L3_Coupon.FCStd'))
    Part.export([obj],str(O/'M2_D3_L3_Coupon.step'))
    mesh = MeshPart.meshFromShape(Shape=s,LinearDeflection=.005,AngularDeflection=.05,Relative=False)
    assert mesh.isSolid() and not mesh.hasNonManifolds()
    mesh.write(str(O/'M2_D3_L3_Coupon.stl'))
    result = dict(status='CAD verified; physical fit pending',bores_mm=BORES,sites=sites,
                  entry_chamfer_mm=LEAD,cylindrical_land_mm=DEPTH-LEAD,
                  upright_floor_mm=TOP-DEPTH,
                  min_boss_radial_wall_mm=(7-max(BORES))/2,
                  size_mm=[s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength],
                  valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,
                  solid_mesh=mesh.isSolid(),nonmanifold=mesh.hasNonManifolds())
    (O/'validation.json').write_text(json.dumps(result,indent=2))
except BaseException:
    (O/'BUILD_ERROR.txt').write_text(traceback.format_exc())
    print(traceback.format_exc(),flush=True)
os._exit(0)

