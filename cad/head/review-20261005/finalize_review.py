"""Normalize inherited status prose and package the independently checked candidate."""
import hashlib, json, zipfile
from pathlib import Path
folder = Path(__file__).resolve().parent
out = folder/'candidate'
report_path = out/'validation.json'
r = json.loads(report_path.read_text())
assert r['checks']['sampled_geometry_pass']
assert json.loads((out/'artifact-verification.json').read_text())['native_reopened_valid']
for item in r['stl']:
    item['gate'] = 'Review candidate only; see pending items and README. No print release.'
    item['released'] = False
r['limitations'] = [
    'Sensor mounting, flex harness, strain relief and mechanical travel stops remain undesigned.',
    '16.5 mm to the raised hub is confirmed by Jim. Horn arm thickness, approximately 1 mm hub rise, lower hub geometry and actual horn screw remain partly assumed.',
    'Circlip and display pocket fits passed; display window alignment and corner screws remain unreported.',
    'Tilt pivot is an M3 bolt in printed PLA; wear and load performance are unverified.',
    'Reference inner-race spacer is not confirmed available hardware or a released printed part.',
    'Pan and tilt are sampled every 5 degrees. No continuous-motion, torque, stiffness, durability or physical fit guarantee.',
    'Belt reference follows carriage position but is a taut envelope; slack shape and installation are unverified.',
    'Nineteen saved master solids checked; actual cables, antenna whip and any absent installed hardware are not represented.',
]
r['status_normalization'] = 'finalize_review.py replaces inherited stale release/measurement prose only; numeric geometry results are unchanged.'
report_path.write_text(json.dumps(r,indent=2)+'\n')
cpath = out/'head-config.json'
c = json.loads(cpath.read_text())
c['release'] = r['review']['status']
c['settled'] = r['settled']
cpath.write_text(json.dumps(c,indent=2)+'\n')
paths = [folder/n for n in ('README.md','tilt-correction.png','baseline-audit.json',
          'build_head_v04_source.py','prepare_candidate.py','build_head_review.py',
          'audit_source.py','render_review.py','verify_and_package.py','finalize_review.py')]
paths += [p for p in out.rglob('*') if p.is_file() and not p.name.endswith('.FCStd1')]
manifest = {str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(folder/'sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
paths.append(folder/'sha256.json')
with zipfile.ZipFile(folder/'Gladiator_MastHead_Reviewed_20261005.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:
        z.write(p,p.relative_to(folder))
print('Packaged',len(paths),'files')

