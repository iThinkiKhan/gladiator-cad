"""Colored review file (run: xvfb-run -a freecad style_side_pcb.py)."""
import os, traceback
from pathlib import Path
import FreeCAD as A, FreeCADGui as Gui
D = Path(__file__).resolve().parent
try:
    d = A.openDocument(str(D / 'Gladiator_Head_v2_Side_PCB.FCStd'))
    for o in d.Objects:
        if o.TypeId != 'Part::Feature':
            continue
        vo = o.ViewObject
        vo.ShapeColor = (.76, .77, .79); vo.LineColor = (.15, .17, .2); vo.DisplayMode = 'Flat Lines'
        n = o.Name
        if n in ('Neck_Main', 'Mast_Tube_v2', 'Rear_Display_Frame') or False:
            vo.ShapeColor = (.96, .55, .18)
        elif n.startswith('Side_PCB_Clamp_Bar'):
            vo.ShapeColor = (.72, .22, .55)
        elif n == 'Side_PCB_30x55_Placeholder':
            vo.ShapeColor = (.10, .55, .25)
        elif n.startswith('Side_PCB_M2_Insert'):
            vo.ShapeColor = (.80, .65, .25)
        elif n == 'Pan_Lead_Route':
            vo.ShapeColor = (.15, .35, .85)
        elif n == 'Side_PCB_Parts_Envelope_20mm':
            vo.ShapeColor = (.98, .85, .20); vo.Transparency = 75
        elif n in ('SG90_Pan_Reference', 'SG90_Tilt_Reference') or n.startswith('Tensioner_'):
            vo.ShapeColor = (.35, .48, .67)
        elif n in ('Rear_Hood', 'Front_Left', 'Front_Right', 'Lens_Plate') or n.startswith('Ref_'):
            vo.Transparency = 85
    Gui.activateWorkbench('PartWorkbench')
    v = Gui.activeDocument().activeView(); v.viewIsometric(); v.fitAll()
    d.saveAs(str(D / 'Gladiator_Head_v2_Side_PCB_REVIEW.FCStd'))
    (D / 'style.log').write_text('ok\n')
    os._exit(0)
except Exception:
    (D / 'style.log').write_text(traceback.format_exc()); os._exit(1)
