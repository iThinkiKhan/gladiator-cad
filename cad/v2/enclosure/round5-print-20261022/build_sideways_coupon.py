from pathlib import Path
import FreeCAD as A,Part,MeshPart,json,os,traceback,math
V=A.Vector;R=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-print-20261022');O=R/'fit-test-stl';O.mkdir(exist_ok=True)
try:
 s=Part.makeBox(40,6,6.5);cutters=[]
 for x,d in zip([5,15,25,35],[2.8,2.9,3.0,3.1]):
  c=Part.makeCylinder(d/2,3.7,V(x,-.1,3.25),V(0,1,0));lead=Part.makeCone(d/2+.15,d/2,.15,V(x,0,3.25),V(0,1,0));s=s.cut(c).cut(lead)
  text=[]
  for ch in Part.makeWireString(f'{d:.1f}','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',2.4,0):
   if ch:text.append(Part.makeFace(ch,'Part::FaceMakerBullseye').extrude(V(0,0,.45)))
  t=Part.makeCompound(text);b=t.BoundBox;t.translate(V(x-b.Center.x,3-b.Center.y,6.15));s=s.cut(t)
 # Corner key at the left end, away from the working bores.
 tri=Part.Face(Part.makePolygon([V(0,0,0),V(1.2,0,0),V(0,1.2,0),V(0,0,0)])).extrude(V(0,0,6.6));s=s.cut(tri).removeSplitter()
 assert s.isValid() and len(s.Solids)==1
 tests=[]
 for x,d in zip([5,15,25,35],[2.8,2.9,3.0,3.1]):
  probe=Part.makeCylinder(d/2-.04,3.45,V(x,.1,3.25),V(0,1,0));assert s.common(probe).Volume<.0001
  assert s.isInside(V(x,3.7,3.25),1e-6,True)
  tests.append({'diameter_mm':d,'axis':'horizontalY','working_depth_mm':3.6,'void_clear':True,'blind_floor_present':True})
 doc=A.newDocument('M2MiniSideways');o=doc.addObject('Part::Feature','M2_D3_L3_Sideways_Optional');o.Shape=s;doc.recompute();doc.saveAs(str(O/'M2_D3_L3_Sideways_Optional.FCStd'));Part.export([o],str(O/'M2_D3_L3_Sideways_Optional.step'))
 m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.015,AngularDeflection=.07,Relative=False);assert m.isSolid() and not m.hasNonManifolds();m.write(str(O/'M2_D3_L3_Sideways_Optional.stl'))
 (R/'optional-horizontal-coupon.json').write_text(json.dumps({'nominal_listing_data':'M2,D3,L3; physical stock measurement still pending','orientation':'horizontal bores; flat40x6 base down','bore_tests':tests,'shape_valid':True,'solid_count':1,'mesh_solid':True,'physical_winner_pending':True},indent=2))
except BaseException:(R/'HORIZONTAL_COUPON_ERROR.txt').write_text(traceback.format_exc())
os._exit(0)
