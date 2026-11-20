import sys
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as App
import FreeCADGui as Gui

path = '/home/buralien/projects/gladiator-cad/cad/power-board/v1-cradle/PowerBoardCradle_v1.FCStd'
doc = App.openDocument(path)
Gui.activeDocument().activeView().setAnimationEnabled(False)

cradle = doc.getObject('PowerBoardCradle')
board = doc.getObject('BoardReference')
under = doc.getObject('UndersideKeepout')
conn = doc.getObject('ConnectorKeepout')
cradle.ViewObject.ShapeColor = (0.20, 0.55, 0.82)
board.ViewObject.ShapeColor = (0.12, 0.42, 0.18)
board.ViewObject.Transparency = 25
under.ViewObject.ShapeColor = (0.95, 0.55, 0.10)
under.ViewObject.Transparency = 80
conn.ViewObject.ShapeColor = (0.72, 0.25, 0.20)
conn.ViewObject.Transparency = 88

view = Gui.activeDocument().activeView()
view.viewAxonometric()
view.fitAll(0.82)
Gui.updateGui()
view.saveImage('/home/buralien/projects/gladiator-cad/cad/power-board/v1-cradle/preview-installed.png', 1400, 1000, 'White')

under.Visibility = False
conn.Visibility = False
view.viewTop()
view.fitAll(0.86)
Gui.updateGui()
view.saveImage('/home/buralien/projects/gladiator-cad/cad/power-board/v1-cradle/preview-top.png', 1200, 1200, 'White')

App.closeDocument(doc.Name)
Gui.getMainWindow().close()
