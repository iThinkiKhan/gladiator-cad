"""Render the corrected antenna mount without changing the CAD document."""
import FreeCAD as App
import FreeCADGui as Gui

path = '/home/buralien/projects/gladiator-cad/cad/antenna/v3-screw-access/Gladiator_Master_antenna_v3_candidate.FCStd'
out = '/home/buralien/projects/gladiator-cad/cad/antenna/v3-screw-access'
doc = App.openDocument(path)
for obj in doc.Objects:
    if hasattr(obj, 'ViewObject'):
        obj.ViewObject.Visibility = False
body = doc.getObject('AntennaPost')
body.ViewObject.Visibility = True
body.Tip.ViewObject.Visibility = True
body.ViewObject.ShapeColor = (0.95, 0.68, 0.18)
view = Gui.activeDocument().activeView()
view.setAnimationEnabled(False)
view.viewAxonometric()
view.fitAll()
Gui.updateGui()
view.saveImage(out + '/preview-axo.png', 1200, 900, 'White')
view.viewTop()
view.fitAll()
Gui.updateGui()
view.saveImage(out + '/preview-screw-access.png', 1200, 900, 'White')
App.closeDocument(doc.Name)
Gui.getMainWindow().close()
