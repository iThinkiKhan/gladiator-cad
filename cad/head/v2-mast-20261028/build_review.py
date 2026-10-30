"""Masthead v2 review file for FreeCAD (colours need the GUI):
    xvfb-run -a freecad cad/head/v2-mast-20261028/build_review.py
Writes Gladiator_Head_v2_REVIEW.FCStd: the assembled v2 head on the robot (real position, shell see-through),
the 9 print parts laid out beside it in print orientation, and v1 as built (hidden) for comparison."""
import json, os, traceback
from pathlib import Path
import FreeCAD as A
import FreeCADGui as Gui
import Mesh

D = Path('/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028')
LOG = D / 'review-build.log'
lines = []
def log(*a):
    lines.append(' '.join(str(x) for x in a)); LOG.write_text('\n'.join(lines) + '\n')

COL = {'changed': ((0.93, 0.55, 0.20), 0), 'camera': ((0.30, 0.65, 0.58), 0), 'same': ((0.72, 0.72, 0.74), 0),
       'hardware': ((0.40, 0.55, 0.80), 45), 'belt': ((0.15, 0.15, 0.15), 0), 'context': ((0.93, 0.82, 0.82), 80)}
try:
    val = json.loads((D / 'validation.json').read_text())['v2']
    idx = json.loads((D / 'render' / 'index.json').read_text())
    kind = {e['name']: e['kind'] for e in idx['v2']}
    for n in ('Camera_Tray', 'Camera_Cover'):
        kind[n] = 'camera'
    src = A.openDocument(str(D / 'Gladiator_Head_v2_Mast.FCStd'))
    doc = A.newDocument('Gladiator_Head_v2_REVIEW')
    top = doc.addObject('App::DocumentObjectGroup', 'Assembled_v2_on_robot')
    sub = {}
    made = []
    for o in src.Objects:
        if o.TypeId != 'Part::Feature':
            continue
        g = o.getParentGroup().Label if o.getParentGroup() else 'Other'
        if g not in sub:
            sub[g] = doc.addObject('App::DocumentObjectGroup', g)
            top.addObject(sub[g])
        f = doc.addObject('Part::Feature', o.Name)
        f.Label = o.Label
        f.Shape = o.Shape.copy()
        sub[g].addObject(f)
        made.append((f, kind.get(o.Name, 'same')))
    A.closeDocument(src.Name)

    lay = doc.addObject('App::DocumentObjectGroup', 'Print_Parts_9_laid_out')
    x = 200.0
    for s in val['print_stl']:
        m = Mesh.Mesh(str(D / 'stl' / s['file']))
        b = m.BoundBox
        m.translate(x - b.XMin, 40 - b.YMin, -b.ZMin)
        mf = doc.addObject('Mesh::Feature', 'PRINT_' + s['part'])
        mf.Mesh = m
        mf.Label = 'PRINT %s (%s x %s x %s)' % (s['part'], *s['size_mm'])
        lay.addObject(mf)
        made.append((mf, 'camera' if s['part'].startswith('Camera') else 'changed'))
        x += b.XLength + 15
    v1 = doc.addObject('App::DocumentObjectGroup', 'v1_as_built_for_comparison_hidden')
    for e in idx['v1']:
        m = Mesh.Mesh(str(D / 'render' / e['file']))
        m.translate(-200, 0, 0)
        mf = doc.addObject('Mesh::Feature', 'v1_' + e['name'])
        mf.Mesh = m
        v1.addObject(mf)
        made.append((mf, 'hidden_' + e['kind']))
    doc.recompute()
    for f, k in made:
        vo = f.ViewObject
        hidden = k.startswith('hidden_')
        c, t = COL.get(k.replace('hidden_', ''), COL['same'])
        vo.ShapeColor = c
        vo.Transparency = t
        if hidden:
            vo.Visibility = False
    Gui.activateWorkbench('PartWorkbench')
    gd = Gui.getDocument(doc.Name)
    view = gd.ActiveView
    view.viewIsometric(); view.fitAll()
    view.saveImage(str(D / 'preview' / 'review-file-iso.png'), 1600, 1000, 'White')
    doc.saveAs(str(D / 'Gladiator_Head_v2_REVIEW.FCStd'))
    log('saved', D / 'Gladiator_Head_v2_REVIEW.FCStd', len(made), 'objects')
    os._exit(0)
except Exception:
    log(traceback.format_exc())
    os._exit(1)
