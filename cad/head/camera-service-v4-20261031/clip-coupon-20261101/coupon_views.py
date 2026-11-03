"""FreeCAD GUI renders for the clip coupon. Run on cad-lab: xvfb-run -a freecad coupon_views.py"""
import os, traceback
from pathlib import Path
D = Path('/home/buralien/projects/gladiator-cad/cad/head/camera-service-v4-20261031/clip-coupon-20261101')
try:
    import FreeCAD as App, FreeCADGui as Gui, Mesh
    doc = App.newDocument('coupon')
    objs = {}

    def add(name, fn, col, transp=0, dx=0.0):
        m = Mesh.Mesh(str(fn)); m.translate(dx, 0, 0)
        o = doc.addObject('Mesh::Feature', name); o.Mesh = m
        objs[name] = o
        return o
    stl = sorted((D / 'stl').glob('*.stl'))
    for i, f in enumerate(stl[:3]):
        add('clip%d' % (i + 1), f, (.2, .5, .9), dx=200 + 9 * i)
    add('gap', stl[3], (.6, .62, .66))
    for nm, col in (('board', (.1, .5, .25)), ('plugs', (.15, .15, .15)), ('clips', (.2, .5, .9)), ('wires', (.85, .2, .15))):
        add(nm, D / 'preview' / ('on_coupon_%s.stl' % nm), col)
    doc.recompute()
    Gui.showMainWindow() if not Gui.getMainWindow() else None
    gdoc = Gui.getDocument(doc.Name)
    cols = {'gap': (.6, .62, .66), 'board': (.1, .5, .25), 'plugs': (.15, .15, .15), 'clips': (.2, .5, .9), 'wires': (.85, .2, .15)}
    for n, o in objs.items():
        vo = gdoc.getObject(n)
        vo.ShapeColor = cols.get(n, (.2, .5, .9))
        try:
            vo.LineColor = vo.ShapeColor
        except Exception:
            pass
    v = gdoc.ActiveView or Gui.ActiveDocument.ActiveView

    def shot(visible, fn, rot, transp=None):
        for n, o in objs.items():
            gdoc.getObject(n).Visibility = n in visible
        for n, t in (transp or {}).items():
            gdoc.getObject(n).Transparency = t
        v.setCameraType('Perspective') if False else v.setCameraType('Orthographic')
        v.setCameraOrientation(rot)
        v.fitAll()
        v.saveImage(str(D / fn), 1400, 1050, 'White')

    iso_hi = App.Rotation(App.Vector(0, 0, 1), -35).multiply(App.Rotation(App.Vector(1, 0, 0), 55))
    iso_lo = App.Rotation(App.Vector(0, 0, 1), -30).multiply(App.Rotation(App.Vector(1, 0, 0), 68))
    top = App.Rotation(App.Vector(0, 0, 1), 0)
    shot({'gap'}, 'view_tray_coupon.png', iso_hi)
    shot({'gap', 'plugs', 'clips', 'wires'}, 'view_in_use_board_hidden.png', iso_hi)
    shot({'gap', 'plugs', 'clips', 'wires', 'board'}, 'view_in_use.png', iso_lo, {'board': 55, 'gap': 0})
    shot({'clip1', 'clip2', 'clip3'}, 'view_clips_top.png', top)
    shot({'clip1', 'clip2', 'clip3'}, 'view_clips_iso.png', iso_lo)
    (D / 'views.log').write_text('ok\n')
except Exception:
    (D / 'views.log').write_text(traceback.format_exc())
os._exit(0)
