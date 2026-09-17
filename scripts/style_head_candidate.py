import sys,os
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad/Mod'])
sys.path.extend(['/usr/lib/freecad/Mod/Part','/usr/lib/freecad/Mod/PartDesign'])
import FreeCAD as A,FreeCADGui as G
G.showMainWindow()
import Part,PartDesign,Sketcher,PartGui,PartDesignGui
path='/home/buralien/projects/gladiator-cad/cad/head/v01/Gladiator_Head_v01.FCStd'
d=A.openDocument(path)
for o in d.Objects:
 if o.ViewObject: o.ViewObject.Visibility=False
for n in ['FixedNeck','PanAssembly','TiltAssembly','CarrierVariants','HardwareReferences']:
 if d.getObject(n).ViewObject:d.getObject(n).ViewObject.Visibility=True
names=['ChassisDeck','SideRailLeft','SideRailRight','BatteryBox','MastTube','UpperDeck','S3Board','Breadboard','PowerShield','AntennaPost','DriverMountLeft','DriverMountRight']
for n in names:
 o=d.getObject(n)
 if o and o.ViewObject:
  o.ViewObject.Visibility=True
  o.ViewObject.ShapeColor=(.58,.60,.63)
  if hasattr(o,'Tip') and o.Tip and o.Tip.ViewObject:o.Tip.ViewObject.Visibility=True
for o in d.Objects:
 if not hasattr(o,'MotionGroup') or not o.ViewObject: continue
 visible=not o.Name.startswith('GH44_') or o.Name in ['GH44_Tilt_Receiver','GH44_Dual_Carrier']
 visible=visible and o.Name not in ['SEN0628_Envelope','SEN0610_Envelope','ESP32_CAM_Envelope']
 o.ViewObject.Visibility=visible
 color=(.22,.34,.40) if o.MotionGroup=='fixed' else (.18,.56,.60)
 if 'Carrier' in o.Name: color=(.91,.57,.22)
 if 'Envelope' in o.Name or 'Reference' in o.Name: color=(.25,.35,.72);o.ViewObject.Transparency=35
 if 'Bearing' in o.Name or 'Spacer' in o.Name or 'Circlip' in o.Name:color=(.66,.68,.70)
 o.ViewObject.ShapeColor=color
 o.ViewObject.LineColor=(.12,.16,.19)
 o.ViewObject.DisplayMode='Flat Lines'
G.activeDocument().activeView().viewAxonometric()
G.activeDocument().activeView().fitAll()
d.recompute();d.save()
print('STYLED',path,flush=True)
A.closeDocument(d.Name)
os._exit(0)
