"""Reuse proven comparisons only after exact solid identity, retest all changed geometry."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path('/home/buralien/projects/gladiator-cad')
builder=ROOT/'scripts/build_head_v05.py'
runner=Path(__file__)
s=builder.read_text()
old=ROOT/'cad/head/integration-20261005/v05-before-radar-shift'
baseline=json.loads((old/'validation.json').read_text())
assert not baseline['collisions'] and not baseline['fov_intersections']
assert baseline['radar_fov_reservation']['intersections']  # only rejected field condition
assert baseline['checks']['master_unchanged'] and baseline['checks']['all_parts_single_valid_solid']
assert not baseline['checks']['robot_solids_missing']
assert baseline['checks']['cable_passage_11_9mm_overlap_mm3']==0
assert all(r['mesh_solid'] and not r['mesh_non_manifold'] and r['probes_pass'] and r['mesh_volume_error_pct']<.1 for r in baseline['stl'])

def replace(a,b):
    global s
    assert s.count(a)==1,(a[:100],s.count(a))
    s=s.replace(a,b)

proof='''
CHANGED = {'Radar_Sensor_Frame','Dual_Radar_Envelope'}
_old=A.openDocument(str(REUSE_BASE/'Gladiator_Head_v05_PanStack.FCStd'))
_differences={}
for _name,_p in parts.items():
    _before=_old.getObject(_name).Shape.copy();_before.translate(-WORLD)
    _difference=_before.cut(_p['shape']).Volume+_p['shape'].cut(_before).Volume
    _differences[_name]=_difference
    if _name not in CHANGED:assert _difference<1e-5,(_name,'cannot reuse changed solid',_difference)
for _path,_sha in BASELINE['source_sha256'].items():
    if _path!=str(ROOT/'scripts/build_head_v05.py'):assert digest(_path)==_sha,(_path,'baseline dependency changed')
A.closeDocument(_old.Name)
REUSED={'head':0,'robot':0,'carriage':0}
report['validation_reuse']={'strategy':'Retest all pairs involving changed solids; exact BRep symmetric-difference verifies every reused solid',
    'changed_parts':sorted(CHANGED),'solid_difference_vs_before_radar_shift_mm3':_differences,
    'baseline_native_sha256':digest(REUSE_BASE/'Gladiator_Head_v05_PanStack.FCStd'),
    'baseline_validation_sha256':digest(REUSE_BASE/'validation.json'),
    'runner_sha256':RUNNER_SHA,'baseline_rigid_and_tof_checks_pass':True}
print('Exact geometry identity passed for24 unchanged solids; checking changed radar geometry',flush=True)
'''
replace('# ================================================================== collision sweeps',proof+'\n# ================================================================== collision sweeps')
replace('    for pan, tilt in poses:\n        v = overlap(posed(a, pan, tilt), posed(b, pan, tilt))',
        '''    if a['name'] not in CHANGED and b['name'] not in CHANGED:
        tests+=len(poses);REUSED['head']+=len(poses);continue
    for pan, tilt in poses:
        v = overlap(posed(a, pan, tilt), posed(b, pan, tilt))''')
replace("    tilts = TILTS if p['motion'] == 'tilt' else (0.0,)\n    for pan in pans:",
        "    tilts = TILTS if p['motion'] == 'tilt' else (0.0,)\n    if p['name'] not in CHANGED:\n        _count=len(pans)*len(tilts)*len(robot);tests+=_count;REUSED['robot']+=_count;continue\n    for pan in pans:")
replace("                    tests += 1\n                    v = overlap(sa, posed(b, float(pan), tilt))",
        "                    tests += 1\n                    if b['name'] not in CHANGED:\n                        REUSED['carriage']+=1;continue\n                    v = overlap(sa, posed(b, float(pan), tilt))")
replace("                    tests += 1\n                    v = overlap(sa, r)",
        "                    tests += 1\n                    REUSED['carriage']+=1;continue\n                    v = overlap(sa, r)")
# ToF reservation itself is unchanged; only intersections against the two changed solids need repeating.
replace("        for n, s in robot:\n            v = overlap(f, s)",
        "        for n, s in robot:\n            continue  # identical ToF reservation and exact-identity robot geometry\n            v = overlap(f, s)")
replace("            if p['name'] == 'Dual_ToF_Envelope':",
        "            if p['name'] not in CHANGED:continue\n            if p['name'] == 'Dual_ToF_Envelope':")
replace("report['checks']['sampled_geometry_pass'] = (",'''report['validation_reuse']['reused_comparison_counts']=REUSED
report['validation_reuse']['fresh_comparison_counts']={
    'head':report['checks']['head_pair_pose_tests']-REUSED['head'],
    'robot':report['checks']['robot_pair_pose_tests']-REUSED['robot'],
    'carriage':report['checks']['carriage_end_pose_tests']-REUSED['carriage']}
assert report['checks']['head_pair_pose_tests']==BASELINE['checks']['head_pair_pose_tests']
assert report['checks']['robot_pair_pose_tests']==BASELINE['checks']['robot_pair_pose_tests']
assert report['checks']['carriage_end_pose_tests']==BASELINE['checks']['carriage_end_pose_tests']
report['checks']['sampled_geometry_pass'] = (''')
REUSE_BASE=old
BASELINE=baseline
RUNNER_SHA=hashlib.sha256(runner.read_bytes()).hexdigest()
__file__=str(builder)
exec(compile(s,str(builder)+' [changed geometry validation]','exec'))
