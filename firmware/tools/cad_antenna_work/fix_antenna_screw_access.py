"""Create an editable antenna mount candidate with clear fixing-screw access.

Run on the CAD workstation with /usr/bin/python3. The saved master is read only.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as App
import MeshPart
import Part
import Sketcher

ROOT = Path('/home/buralien/projects/gladiator-cad')
MASTER = ROOT / 'cad/master/Gladiator_Master.FCStd'
OUT = ROOT / 'cad/antenna/v3-screw-access'
OUT.mkdir(parents=True, exist_ok=True)

RADIUS = 3.2  # 6.4 mm approach for an M3 head and driver
CENTRES = [(60.0, 10.0), (76.0, 10.0)]
FLANGE_TOP = 62.0
ACCESS_TOP = 86.0

before_hash = hashlib.sha256(MASTER.read_bytes()).hexdigest()
doc = App.openDocument(str(MASTER))
body = doc.getObject('AntennaPost')
original = body.Shape.copy()

# The old holes stop at the flange top. A top-down pocket opens the screw-head
# and tool path through both side gussets and the rear edge of the upright plate.
sketch = doc.addObject('Sketcher::SketchObject', 'AntFixAccessSketch')
sketch.Label = 'M3 fixing screw access, 6.4 mm diameter'
body.addObject(sketch)
sketch.Placement = App.Placement(App.Vector(0, 0, ACCESS_TOP), App.Rotation())
for x, y in CENTRES:
    index = sketch.addGeometry(
        Part.Circle(App.Vector(x, y, 0), App.Vector(0, 0, 1), RADIUS), False)
    sketch.addConstraint(Sketcher.Constraint('Radius', index, RADIUS))
doc.recompute()

pocket = doc.addObject('PartDesign::Pocket', 'AntFixAccessCut')
pocket.Label = 'Clear both fixing screws above flange'
body.addObject(pocket)
pocket.Profile = sketch
pocket.Type = 'Length'
pocket.Length = ACCESS_TOP - FLANGE_TOP
pocket.Reversed = False
body.Tip = pocket
doc.recompute()
shape = body.Shape

def overlap(x, y, r, z0, z1, solid=shape):
    probe = Part.makeCylinder(r, z1-z0, App.Vector(x, y, z0))
    return solid.common(probe).Volume

checks = {
    'source_sha256': before_hash,
    'master_unchanged': hashlib.sha256(MASTER.read_bytes()).hexdigest() == before_hash,
    'radius_mm': RADIUS,
    'screw_centres_mm': CENTRES,
    'clearance_z_mm': [FLANGE_TOP, ACCESS_TOP],
    'original_volume_mm3': round(original.Volume, 3),
    'corrected_volume_mm3': round(shape.Volume, 3),
    'valid': shape.isValid(),
    'solid_count': len(shape.Solids),
    'body_tip': body.Tip.Name,
    'screw_checks': {},
}
for x, y in CENTRES:
    checks['screw_checks'][str(x)] = {
        'original_blockage_above_flange_mm3': round(
            overlap(x, y, RADIUS, FLANGE_TOP, ACCESS_TOP, original), 3),
        'remaining_blockage_above_flange_mm3': round(
            overlap(x, y, RADIUS, FLANGE_TOP, ACCESS_TOP), 6),
        'remaining_shank_blockage_in_flange_mm3': round(
            overlap(x, y, 1.7, 58.0, FLANGE_TOP), 6),
    }

# The clearance cut is entirely above the mounting flange, which must retain
# its original bearing material and existing 3.4 mm through holes.
flange = Part.makeBox(24.0, 11.0, 4.0, App.Vector(56, 2, 58))
checks['flange_material_change_mm3'] = round(
    original.common(flange).Volume - shape.common(flange).Volume, 6)

assert checks['valid'] and checks['solid_count'] == 1
assert checks['flange_material_change_mm3'] < 0.001
assert all(v['remaining_blockage_above_flange_mm3'] < 0.001 and
           v['remaining_shank_blockage_in_flange_mm3'] < 0.001
           for v in checks['screw_checks'].values())

doc.saveAs(str(OUT / 'Gladiator_Master_antenna_v3_candidate.FCStd'))
Part.export([body], str(OUT / 'AntennaMount_v3_screw-access.step'))

# Match the existing antenna print orientation: its front face (negative Y)
# goes against the bed. Keep a distinct filename so the old STL is preserved.
print_shape = shape.copy()
down = App.Vector(0, -1, 0)
rotation = App.Rotation(down, App.Vector(0, 0, -1))
print_shape.Placement = App.Placement(App.Vector(), rotation).multiply(print_shape.Placement)
bb = print_shape.BoundBox
print_shape.translate(App.Vector(-bb.XMin, -bb.YMin, -bb.ZMin))
mesh = MeshPart.meshFromShape(Shape=print_shape, LinearDeflection=0.01,
                              AngularDeflection=0.05, Relative=False)
mesh_path = OUT / 'AntennaMount_v3_print-on-front-face.stl'
mesh.write(str(mesh_path))
checks['mesh_solid'] = mesh.isSolid()
checks['mesh_nonmanifold'] = mesh.hasNonManifolds()
checks['mesh_self_intersections'] = mesh.hasSelfIntersections()
checks['print_bbox_mm'] = [round(mesh.BoundBox.XLength, 3),
                           round(mesh.BoundBox.YLength, 3),
                           round(mesh.BoundBox.ZLength, 3)]
checks['mesh_sha256'] = hashlib.sha256(mesh_path.read_bytes()).hexdigest()
checks['master_unchanged'] = hashlib.sha256(MASTER.read_bytes()).hexdigest() == before_hash
assert checks['mesh_solid'] and not checks['mesh_nonmanifold']
assert not checks['mesh_self_intersections'] and checks['master_unchanged']

(OUT / 'validation.json').write_text(json.dumps(checks, indent=2) + '\n')
print(json.dumps(checks, indent=2))
App.closeDocument(doc.Name)
