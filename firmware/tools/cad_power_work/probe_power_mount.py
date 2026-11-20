import sys
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as App
import Part

MASTER = '/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd'
doc = App.openDocument(MASTER)

names = ['ChassisDeck', 'BatteryBox', 'MastBase', 'SideRailLeft',
         'SideRailRight', 'UpperDeck', 'PowerShield']
for name in names:
    obj = doc.getObject(name)
    bb = obj.Shape.BoundBox
    print('BOUND', name, *(round(v, 3) for v in
          (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)),
          'VOL', round(obj.Shape.Volume, 2))

# Exact thin horizontal slices, reported as the bounding box of every resulting
# solid. This exposes the mast-base profile without thousands of booleans.
for z in [2.0, 4.0, 6.0, 10.0, 16.0, 20.0, 22.0]:
    slab = Part.makeBox(79.0, 140.0, 0.2, App.Vector(0, 0, z))
    print('\nSLICE_Z', z)
    for name in ['MastBase', 'SideRailLeft', 'SideRailRight']:
        cut = slab.common(doc.getObject(name).Shape)
        boxes = []
        for solid in cut.Solids:
            bb = solid.BoundBox
            boxes.append(tuple(round(v, 2) for v in
                         (bb.XMin, bb.XMax, bb.YMin, bb.YMax)))
        print(' ', name, 'area', round(cut.Volume / 0.2, 2), 'boxes', boxes)

# Exact local clearance around the intended independent anchor coordinates.
for x, y, kind in [(25.5, 98.0, 'M3 slot L'), (53.5, 98.0, 'M3 slot R'),
                   (19.0, 128.0, 'M2 rear L'), (60.0, 128.0, 'M2 rear R')]:
    probe = Part.makeCylinder(4.0, 46.0, App.Vector(x, y, 2.0))
    hits = []
    for name in names[1:]:
        vol = probe.common(doc.getObject(name).Shape).Volume
        if vol > 0.05:
            hits.append((name, round(vol, 2)))
    print('ANCHOR', kind, x, y, hits)

App.closeDocument(doc.Name)
