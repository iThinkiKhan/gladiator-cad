"""Colored review file + pictures (run: xvfb-run -a freecad style_pcb_floor.py)."""
import os, json, traceback
from pathlib import Path
import FreeCAD as A, FreeCADGui as Gui
D = Path(__file__).resolve().parent
try:
    d = A.openDocument(str(D / 'Gladiator_Head_v2_PCB_Floor.FCStd'))
    tilt = json.loads((D.parent / 'validation.json').read_text())['v2']['groups']['tilt']
    for o in d.Objects:
        if o.TypeId != 'Part::Feature':
            continue
        vo = o.ViewObject
        vo.ShapeColor = (.76, .77, .79)
        vo.LineColor = (.15, .17, .2)
        vo.DisplayMode = 'Flat Lines'
        n = o.Name
        if n == 'Tilt_Yoke':
            vo.ShapeColor = (.96, .55, .18)
        elif n == 'Head_Distro_PCB_Placeholder':
            vo.ShapeColor = (.10, .55, .25)
        elif n.startswith('M2_Insert_'):
            vo.ShapeColor = (.80, .65, .25)
        elif n == 'Tilt_Lead_Route':
            vo.ShapeColor = (.15, .35, .85)
        elif n == 'Yoke_Bolt_Head_M3':
            vo.ShapeColor = (.25, .25, .28)
        elif n.startswith('PCB_Part_Height_Zone_'):
            vo.ShapeColor = (.98, .85, .20); vo.Transparency = 70
        elif n in ('SG90_Pan_Reference', 'SG90_Tilt_Reference') or n.startswith('Tensioner_'):
            vo.ShapeColor = (.35, .48, .67)
        elif n in ('Rear_Hood', 'Front_Left', 'Front_Right', 'Lens_Plate') or n.startswith('Ref_'):
            vo.Transparency = 85
    Gui.activateWorkbench('PartWorkbench')
    v = Gui.activeDocument().activeView()
    v.viewIsometric(); v.fitAll()
    d.saveAs(str(D / 'Gladiator_Head_v2_PCB_Floor_REVIEW.FCStd'))
    v.saveImage(str(D / 'freecad_review_full.png'), 1600, 1200, 'White')
    # close-up of the floor with the tilting head hidden (pictures only; the saved file shows everything)
    hide = tilt + ['Rear_Hood', 'Front_Left', 'Front_Right', 'Lens_Plate', 'SG90_Tilt_Reference', 'Tilt_Pivot_Bolt']
    for n in hide:
        o = d.getObject(n)
        if o: o.ViewObject.Visibility = False
    Gui.Selection.clearSelection()
    for n in ('Head_Distro_PCB_Placeholder', 'Tilt_Lead_Route', 'M2_Insert_A', 'M2_Insert_C'):
        Gui.Selection.addSelection(d.getObject(n))
    v.viewIsometric(); Gui.SendMsgToActiveView('ViewSelection')
    v.saveImage(str(D / 'freecad_floor_closeup_iso.png'), 1600, 1200, 'White')
    v.viewTop(); Gui.SendMsgToActiveView('ViewSelection')
    v.saveImage(str(D / 'freecad_floor_closeup_top.png'), 1600, 1200, 'White')
    pcb = d.getObject('Head_Distro_PCB_Placeholder'); pcb.ViewObject.Visibility = False
    for n in ('PCB_Part_Height_Zone_1', 'PCB_Part_Height_Zone_2', 'PCB_Part_Height_Zone_3', 'PCB_Part_Height_Zone_4'):
        o = d.getObject(n)
        if o: o.ViewObject.Visibility = False
    v.viewIsometric(); Gui.SendMsgToActiveView('ViewSelection')
    v.saveImage(str(D / 'freecad_floor_pocket_no_board.png'), 1600, 1200, 'White')
    Gui.Selection.clearSelection()
    (D / 'style.log').write_text('ok\n')
    os._exit(0)
except Exception:
    (D / 'style.log').write_text(traceback.format_exc())
    os._exit(1)
