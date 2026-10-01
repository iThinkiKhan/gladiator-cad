"""Create the 2026-09-26 mast-base reprint from the current CAD master.

Run on the CAD lab with FreeCAD's Python modules available.  The master is read
only; the revised editable assembly and oriented STL are separate artifacts.
"""
import os
import shutil
import sys

sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod'])
import FreeCAD as App
import MeshPart

REPO = '/home/buralien/projects/gladiator-cad'
MASTER = REPO + '/cad/master/Gladiator_Master.FCStd'
OUTDIR = REPO + '/cad/mast-base/reprint-20260926'
CAD = OUTDIR + '/Gladiator_Master_MastBase_short-spigot.FCStd'
STL = OUTDIR + '/Gladiator_MastBase_spigot-3p5_chamfer-0p8_UP.stl'
INCOMING = '/home/buralien/3D-Printer/Incoming'
SPIGOT_BELOW = 3.5
CHAMFER = 0.8

os.makedirs(OUTDIR, exist_ok=True)
shutil.copy2(MASTER, CAD)
doc = App.openDocument(CAD)
sheet = doc.getObject('Parameters')
base = doc.getObject('MastBase')
ch = doc.getObject('MastBaseEntryChamfer')
assert base and ch and base.Tip == ch
original = base.Shape.copy()
assert original.isValid() and len(original.Solids) == 1
assert abs(original.BoundBox.ZMin + 5.0) < 0.01
assert abs(ch.Size.Value - 0.35) < 0.01

spigot_cell = None
for cell in sheet.getNonEmptyCells():
    if sheet.getAlias(cell) == 'mast_spigot_below':
        spigot_cell = cell
        break
assert spigot_cell, 'mast_spigot_below alias missing'
sheet.set(spigot_cell, '%g mm' % SPIGOT_BELOW)
ch.setExpression('Size', None)
ch.Size = CHAMFER
doc.recompute()

shape = base.Shape
assert shape.isValid() and len(shape.Solids) == 1
assert abs(shape.BoundBox.ZMin + 3.5) < 0.01, shape.BoundBox
assert abs(shape.BoundBox.ZMax - 20.0) < 0.01
assert abs(ch.Size.Value - CHAMFER) < 0.001
assert abs(doc.getObject('MastSpigotPad').Length.Value - 5.5) < 0.001
circles = [(e.Curve.Radius*2, e.CenterOfMass.z) for e in shape.Edges
           if len(e.Vertexes) == 1 and hasattr(e, 'Curve')
           and e.Curve.TypeId == 'Part::GeomCircle']
assert any(abs(d-22.0) < 0.01 and abs(z-20.0) < 0.01 for d,z in circles), circles
assert any(abs(d-20.4) < 0.01 and abs(z-19.2) < 0.01 for d,z in circles), circles
assert any(abs(d-20.4) < 0.01 and abs(z-6.0) < 0.01 for d,z in circles), circles
assert any(abs(d-14.0) < 0.01 and abs(z+3.5) < 0.01 for d,z in circles), circles

doc.recompute()
doc.save()

# The collar's open rim is on the bed; spigot points upward.
oriented = shape.copy()
rotation = App.Rotation(App.Vector(0,0,1), App.Vector(0,0,-1))
oriented.Placement = App.Placement(App.Vector(), rotation).multiply(oriented.Placement)
bb = oriented.BoundBox
oriented.translate(App.Vector(-bb.XMin, -bb.YMin, -bb.ZMin))
mesh = MeshPart.meshFromShape(Shape=oriented, LinearDeflection=0.01,
                              AngularDeflection=0.05, Relative=False)
assert mesh.isSolid() and not mesh.hasNonManifolds() and not mesh.hasSelfIntersections()
assert abs(mesh.BoundBox.ZMin) < 1e-6
assert mesh.BoundBox.XLength < 220 and mesh.BoundBox.YLength < 220
assert abs(mesh.BoundBox.ZLength - 23.5) < 0.01
assert abs(mesh.Volume - shape.Volume) / shape.Volume < 0.005
mesh.write(STL)
shutil.copy2(STL, INCOMING + '/' + os.path.basename(STL))

with open(OUTDIR + '/README.md', 'w') as f:
    f.write('# Mast base reprint — 2026-09-26\n\n'
            'Source: current `cad/master/Gladiator_Master.FCStd`, copied before editing. '
            'The master was not changed.\n\n'
            '- Spigot below deck: 5.0 → 3.5 mm (1.5 mm shorter); diameter remains 14.0 mm.\n'
            '- Mast socket upper entry: 0.35 → 0.8 mm by 45°; straight bore remains 20.4 mm.\n'
            '- Print orientation: upside down with spigot up. The thin collar ring touches '
            'the bed; use a brim and support under the outer plate.\n'
            '- Editable source: `Gladiator_Master_MastBase_short-spigot.FCStd` (whole assembly).\n'
            '- Print mesh: `Gladiator_MastBase_spigot-3p5_chamfer-0p8_UP.stl`.\n'
            '- An identical mesh was placed in `~/3D-Printer/Incoming`.\n')
print('CAD', CAD)
print('STL', STL)
print('INCOMING', INCOMING + '/' + os.path.basename(STL))
print('BOUNDS', mesh.BoundBox)
print('VOLUME', shape.Volume, mesh.Volume)
print('FACETS', mesh.CountFacets)
print('VALID', shape.isValid(), mesh.isSolid(), not mesh.hasNonManifolds())
App.closeDocument(doc.Name)
