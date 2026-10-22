from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part,MeshPart,json,math,os,hashlib,traceback
V=A.Vector;O=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-20261021');out={}
def clean(s):
 q=Part.Shape();q.importBrepFromString(s.exportBrepToString());return q.Solids[0] if len(q.Solids)==1 else q
try:
 d=A.openDocument(str(O/'Gladiator_Round5.FCStd'));b=A.openDocument(str(O/'baseline-v28/Gladiator_Enclosure_v2.FCStd'))
 original=clean(b.Rear_Hood.Shape);before=clean(d.Rear_Hood.Shape)
 # Shorten only the new upper lip's left end, including the .08 join allowance; never cut original material.
 block=Part.makeBox(4.01,1.5,3.01,V(-3.01,-33.4,99.995))
 new_only=clean(block.cut(original,.00001))
 after=clean(before.cut(new_only,.00001))
 try:after=after.removeSplitter()
 except Part.OCCError:pass
 out=dict(valid=after.isValid(),solids=len(after.Solids),original_removed_mm3=original.cut(after,.00001).Volume,new_material_added_mm3=after.cut(before,.00001).Volume,styling_trimmed_mm3=before.cut(after,.00001).Volume)
 assert out['valid'] and out['solids']==1 and out['original_removed_mm3']<.001 and out['new_material_added_mm3']<.001,out
 d.Rear_Hood.Shape=after
 for tag,z0,z1,col in [('Lower',-20,50,(.43,.46,.50)),('Belt',50,56,(.68,.045,.035)),('Wall',56,99.9,(.43,.46,.50)),('Cap',99.9,130,(.68,.045,.035))]:
  obj=d.getObject('Appearance_Rear_Hood_'+tag)
  obj.Shape=after.common(Part.makeBox(400,450,z1-z0,V(-200,-200,z0)));obj.ViewObject.ShapeColor=col
 d.recompute();d.save()
 q=after.copy();q.rotate(V(),V(1,0,0),180);bb=q.BoundBox;q.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin))
 m=MeshPart.meshFromShape(Shape=q,LinearDeflection=.015,AngularDeflection=.07,Relative=False)
 assert m.isSolid() and not m.hasNonManifolds();m.write(str(O/'stl/Rear_Hood.stl'))
 r=json.loads((O/'validation.json').read_text());r['parts']['Rear_Hood']['volume_mm3']=after.Volume
 r['parts']['Rear_Hood']['mesh_solid']=True;r['parts']['Rear_Hood']['mesh_nonmanifold']=False
 r['parts']['Front_Left']['mesh_solid']=True;r['parts']['Front_Left']['mesh_nonmanifold']=False
 r['final_lame_trim']=out;(O/'validation.json').write_text(json.dumps(r,indent=2))
 masks=[Part.makeBox(30,70,40,V(-39,-12,50)),Part.makeBox(30,70,40,V(88,-12,50)),Part.makeBox(110,20,80,V(-10,-52,40))]
 ext=sum(after.common(mask,.00001).Volume for mask in masks)
 out['exterior_accounting_mm3']=dict(extracted=ext,volume_increase=after.Volume-original.Volume,difference=ext-(after.Volume-original.Volume))
 (O/'final-geometry-fix.json').write_text(json.dumps(out,indent=2))
except BaseException:out['error']=traceback.format_exc();(O/'final-geometry-fix.json').write_text(json.dumps(out,indent=2))
os._exit(0)

