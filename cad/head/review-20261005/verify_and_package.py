"""Reopen delivered artifacts and compare the correction to captured baseline solids."""
import json, hashlib, sys, zipfile
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod', '/usr/lib/freecad-python3/lib'])
import FreeCAD as A
import Part
import Mesh

folder = Path(__file__).resolve().parent
out = folder/'candidate'
validation = json.loads((out/'validation.json').read_text())
assert validation['checks']['sampled_geometry_pass'], 'Build has not passed'
source = (folder/'build_head_v04_source.py').read_text(encoding='utf-8-sig')
source = source.replace("OUT = ROOT / 'cad/head/v04-pan-stack'", "OUT = ROOT / 'cad/head/review-20261005/baseline'")
exec(compile(source.split('# ================================================================== collision sweeps')[0], 'captured_v04', 'exec'))
baseline_parts = parts
candidate_dir = folder/'candidate'  # the captured prefix rebinds OUT
native = A.openDocument(str(candidate_dir/'Gladiator_Head_v04_PanStack.FCStd'))
comparison = {}
for name,p in baseline_parts.items():
    saved = native.getObject(name).Shape.copy()
    assert saved.isValid() and len(saved.Solids)==1, name
    saved.translate(-WORLD)
    original = p['shape']
    difference = original.cut(saved).Volume + saved.cut(original).Volume
    comparison[name] = round(difference, 8)
    if name != 'GH44_Tilt_Receiver':
        assert difference < 1e-5, (name,difference)
receiver = native.GH44_Tilt_Receiver.Shape.copy()
receiver.translate(-WORLD)
roof_x = TS_X0 - (rim_l+POCKET_DEPTH+BOSS_RECESS+ROOF_T)
annulus = cx(2,roof_x,ROOF_T,T.y,TZ).cut(cx(CENTRE_HOLE/2,roof_x-.1,ROOF_T+.2,T.y,TZ))
assert abs(receiver.common(annulus).Volume-annulus.Volume)<1e-6
shank = cx(CENTRE_HOLE/2-.01,-25.5,TS_X0-rim_l+25.5,T.y,TZ)
assert receiver.common(shank).Volume<1e-6
step = Part.Shape()
step.read(str(candidate_dir/'Gladiator_Head_v04_PanStack.step'))
native_volume = sum(native.getObject(n).Shape.Volume for n in baseline_parts)
assert step.isValid() and len(step.Solids)==len(baseline_parts)
relative_error = abs(step.Volume-native_volume)/native_volume
assert relative_error < 1e-6
result = {'native_reopened_valid':True,'step_valid':True,'step_solids':len(step.Solids),
          'step_relative_volume_error':relative_error,
          'changed_geometry_only':['GH44_Tilt_Receiver'],
          'symmetric_difference_mm3':comparison,
          'saved_receiver_screw_seat_mm3':receiver.common(annulus).Volume,
          'saved_receiver_screw_passage_overlap_mm3':receiver.common(shank).Volume}
(candidate_dir/'artifact-verification.json').write_text(json.dumps(result,indent=2)+'\n')
A.closeDocument(native.Name)
print(json.dumps(result,indent=2))

