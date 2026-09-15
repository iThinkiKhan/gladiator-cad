import os
import FreeCAD as App
import Part

DOC_PATH = '/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd'
STEP_PATH = os.path.splitext(DOC_PATH)[0] + '.step'

doc = App.openDocument(DOC_PATH)
body = doc.getObject('ChassisDeck')
shape = body.Shape

if not shape.isValid():
    raise RuntimeError('ChassisDeck shape is invalid; refusing to export STEP')

Part.export([body], STEP_PATH)
print('EXPORTED', STEP_PATH, os.path.getsize(STEP_PATH), 'bytes')
