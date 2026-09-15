import os
import FreeCAD as App
import Part

DOC_PATH = '/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd'
STEP_PATH = os.path.splitext(DOC_PATH)[0] + '.step'

doc = App.openDocument(DOC_PATH)

# Export the final shape of each PartDesign body plus any standalone solids
# (e.g. BatteryBox), but skip a body's own internal features (DeckPad,
# TowerHole, ...) -- each of those also carries a full intermediate solid,
# and including them alongside the body would duplicate the same geometry
# many times over in the STEP file.
bodies = [o for o in doc.Objects if o.TypeId == 'PartDesign::Body']
internal_feature_names = set()
for b in bodies:
    internal_feature_names.update(o.Name for o in b.Group)

solids = [
    o for o in doc.Objects
    if o.Name not in internal_feature_names
    and hasattr(o, 'Shape') and o.Shape.Solids
]

if not solids:
    raise RuntimeError('No solid objects found; refusing to export an empty STEP')

for o in solids:
    if not o.Shape.isValid():
        raise RuntimeError(f'{o.Name} shape is invalid; refusing to export STEP')

Part.export(solids, STEP_PATH)
print('EXPORTED', STEP_PATH, os.path.getsize(STEP_PATH), 'bytes')
print('Included objects:', [o.Name for o in solids])
