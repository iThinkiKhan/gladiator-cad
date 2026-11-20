import sys,zipfile,xml.etree.ElementTree as E
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad/Mod'])
import FreeCAD,FreeCADGui
print('GUI_METHODS',[n for n in dir(FreeCADGui) if 'setup' in n.lower() or 'document' in n.lower() or 'window' in n.lower()])
p='/home/buralien/projects/gladiator-cad/cad/head/v01/Gladiator_Head_v01.FCStd'
with zipfile.ZipFile(p) as z:
 print('ZIP',z.namelist()[:6])
 if 'GuiDocument.xml' in z.namelist():
  t=E.fromstring(z.read('GuiDocument.xml'))
  print('GUI_ROOT',E.tostring(t,encoding='unicode')[:4500])
