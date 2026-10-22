from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part,MeshPart,math,json,os,traceback
V=A.Vector;O=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-20261021')
try:
 d=A.openDocument(str(O/'Gladiator_Round5.FCStd'));A.setActiveDocument(d.Name);G.setActiveDocument(d.Name)
 G.getMainWindow().resize(1800,1400);G.updateGui()
 vis={}
 for o in d.Objects:
  if not hasattr(o,'Shape'):continue
  n=o.Name
  o.ViewObject.Visibility=not(n in ('Rear_Hood','Front_Left','Front_Right') or n.startswith(('Ref_Board','Ref_S3','Ref_Bread')) or 'envelope' in n.lower() or n.endswith('Reference'))
  if n=='Aquila_Relief':o.ViewObject.LineColor=(.32,.22,.07);o.ViewObject.LineWidth=1.0
  if n.startswith('Letters_'):o.ViewObject.LineColor=(.5,.04,.02);o.ViewObject.DisplayMode='Flat Lines'
  vis[n]=o.ViewObject.Visibility
 view=G.activeDocument().activeView();view.setCameraType('Orthographic')
 def shot(filename,direction,only=None):
  for o in d.Objects:
   if hasattr(o,'Shape'):o.ViewObject.Visibility=vis[o.Name] if only is None else o.Name in only
  dv=V(*direction);dv.normalize();up=V(0,0,1);right=dv.cross(up);right.normalize();top=right.cross(dv);top.normalize()
  view.setCameraOrientation(A.Rotation(right,top,-dv,'ZXY'));G.updateGui();view.fitAll();G.updateGui();view.fitAll();view.saveImage(str(O/filename),1600,1200,'White')
 shot('round5-front.png',(-1,-1.4,-.7))
 # Save the native document with its usable fitted front view and intended visibility.
 d.recompute();d.save()
 shot('round5-rear.png',(1,1.5,-.65))
 shot('round5-side.png',(-1,0,-.12))
 shot('aquila-detail.png',(0,1,-.25),['Aquila_Relief','Aquila_Centre_M2'])
 shot('scutum-detail.png',(-.3,-1,-.2),['Scutum_Field_R','Scutum_Emblem_R','Scutum_Boss_R','Scutum_R_M2'])
 shot('head-detail.png',(-1,-1,-.5),[o.Name for o in d.Objects if o.Name.startswith('Head_') or (hasattr(o,'AssemblyOwner') and o.AssemblyOwner.startswith('Head'))])
 # Export the captive shoes on their broad contact faces, rather than their narrow bottom edges.
 report=json.loads((O/'validation.json').read_text())
 for oldname in list(report['parts']):
  newname=oldname.replace('.','_')
  if newname!=oldname:
   report['parts'][newname]=report['parts'].pop(oldname)
   oldpath=O/'stl'/(oldname+'.stl');newpath=O/'stl'/(newname+'.stl')
   if oldpath.exists():os.replace(oldpath,newpath)
 for n in report['parts']:
  if '_Shoe' not in n:continue
  s=d.getObject(n).Shape.copy();s.rotate(V(),V(1,0,0),90);b=s.BoundBox;s.translate(V(-b.XMin,-b.YMin,-b.ZMin))
  m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.015,AngularDeflection=.07,Relative=False);m.write(str(O/'stl'/(n+'.stl')))
  b=s.BoundBox;report['parts'][n].update(size_mm=[b.XLength,b.YLength,b.ZLength],mesh_solid=m.isSolid(),mesh_nonmanifold=m.hasNonManifolds())
 report['status']='Round 5 CAD review; independent saved-file verification alongside'
 (O/'validation.json').write_text(json.dumps(report,indent=2))
 (O/'presentation-complete.txt').write_text('Saved fitted front view and updated flat-oriented clamp shoes.\n')
except BaseException:(O/'PRESENTATION_ERROR.txt').write_text(traceback.format_exc())
os._exit(0)

