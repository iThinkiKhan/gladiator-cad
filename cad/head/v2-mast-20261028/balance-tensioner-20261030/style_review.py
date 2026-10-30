import os,json,traceback
from pathlib import Path
import FreeCAD as A,FreeCADGui as Gui
D=Path(__file__).resolve().parent
try:
 d=A.openDocument(str(D/'Gladiator_Head_v2_Balanced.FCStd'))
 for o in d.Objects:
  if o.TypeId!='Part::Feature':continue
  o.ViewObject.ShapeColor=(.76,.77,.79)
  if o.Name=='GH44_Tilt_Receiver':o.ViewObject.ShapeColor=(.96,.55,.18)
  elif o.Name.startswith('Tensioner_'):o.ViewObject.ShapeColor=(.25,.48,.78)
  elif o.Name in ('SG90_Pan_Reference','SG90_Tilt_Reference'):o.ViewObject.ShapeColor=(.35,.48,.67)
  elif o.Name in ('Rear_Hood','Front_Left','Front_Right','Lens_Plate') or o.Name.startswith('Ref_'):
   o.ViewObject.Transparency=85
  o.ViewObject.LineColor=(.15,.17,.2)
  o.ViewObject.DisplayMode='Flat Lines'
 Gui.activateWorkbench('PartWorkbench')
 v=Gui.activeDocument().activeView();v.viewIsometric();v.fitAll()
 d.saveAs(str(D/'Gladiator_Head_v2_Balanced_REVIEW.FCStd'))
 v.saveImage(str(D/'freecad_review.png'),1600,1200,'White')
 (D/'style.log').write_text('Saved colored native review.\n')
 os._exit(0)
except:
 (D/'style.log').write_text(traceback.format_exc());os._exit(1)
