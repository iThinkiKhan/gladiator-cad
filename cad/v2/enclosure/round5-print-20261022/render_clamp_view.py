from pathlib import Path
import FreeCAD as A,FreeCADGui as G,os,traceback
R=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-print-20261022');V=A.Vector
try:
 src=A.openDocument(str(R/'Gladiator_Round5_Print.FCStd'));d=A.newDocument('ClampView')
 for n in ['Crest_Clamp','Crest_Clamp_Shoe']:
  o=d.addObject('Part::Feature',n);o.Shape=src.getObject(n).Shape.copy();o.ViewObject.ShapeColor=(.28,.30,.32);o.ViewObject.LineColor=(.08,.08,.08);o.ViewObject.DisplayMode='Flat Lines'
 d.recompute();A.setActiveDocument(d.Name);G.setActiveDocument(d.Name);G.getMainWindow().resize(1500,1200);G.updateGui()
 view=G.activeDocument().activeView();view.setCameraType('Orthographic');dv=V(-.55,1,-.4);dv.normalize();right=dv.cross(V(0,0,1));right.normalize();up=right.cross(dv);view.setCameraOrientation(A.Rotation(right,up,-dv,'ZXY'));G.updateGui();view.fitAll();G.updateGui();view.fitAll();G.updateGui();view.saveImage(str(R/'previews/crest-clamp-reinforced.png'),1200,1000,'White')
except BaseException:(R/'CLAMP_VIEW_ERROR.txt').write_text(traceback.format_exc())
os._exit(0)
