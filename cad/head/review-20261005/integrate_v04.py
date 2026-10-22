"""Guarded integration of the validated review fixes into the current shared v04 source."""
from pathlib import Path
import hashlib, json, shutil, datetime

ROOT = Path('/home/buralien/projects/gladiator-cad')
OUT = ROOT/'cad/head/integration-20261005'
OUT.mkdir(parents=True, exist_ok=True)
target = ROOT/'scripts/build_head_v04.py'
original = target.read_bytes()
source = original.decode('utf-8')

def replace(old, new):
    global source
    assert source.count(old)==1, (old[:120], source.count(old))
    source = source.replace(old,new)

replace("rec = rec.cut(cx(3.5, -25.5, ROOF_OUT_X - (-25.5), T.y, TZ))", """rec = rec.cut(cx(3.5, -25.5, ROOF_OUT_X - (-25.5), T.y, TZ))
# Recut the screw passage AFTER fusing the supporting arm. Its x=-21 face
# otherwise seals 0.1 mm of the hole after the horn-height correction.
rec = rec.cut(cx(CENTRE_HOLE / 2, -25.6, TS_X0 - rim_l + 25.7, T.y, TZ))
_shank = cx(CENTRE_HOLE / 2 - .01, -25.5, TS_X0 - rim_l + 25.5, T.y, TZ)
_shank_overlap = rec.common(_shank).Volume
assert _shank_overlap < 1e-6, 'tilt horn screw passage blocked after fusion'
report['checks']['tilt_screw_shank_overlap_mm3'] = _shank_overlap""")
replace("assert _left > 0.99 * _ann.Volume, 'the driver cut ate the horn screw roof'", """assert abs(_left - _ann.Volume) < 1e-6, 'the driver cut ate the horn screw roof'
report['checks']['tilt_screw_bearing_annulus_mm3'] = _left
report['checks']['tilt_screw_bearing_annulus_expected_mm3'] = _ann.Volume
report['checks']['tilt_screw_roof_thickness_mm'] = ROOF_T""")
replace("TILTS = (-25.0, 0.0, 25.0)", "TILTS = tuple(float(t) for t in range(-25, 26, 5))")
replace("    s = p['shape'].copy()\n    if C is not None", """    # A sliding servo changes both pulley spacing and the belt path. This is
    # a taut-path envelope; slack/sag and installation need physical checks.
    s = rotF(belt_for(C)) if C is not None and p.get('name') == 'Pan_Belt_Reference' else p['shape'].copy()
    if C is not None""")
replace("        for tilt in (0.0, 25.0):", "        for tilt in (-25.0, 0.0, 25.0):")
replace("""for pan in PAN_SAMPLES:
    for tilt in TILTS:
        for p in plist:
            s = posed(p, pan, tilt)
            for n, r in robot:
                tests += 1
                v = overlap(s, r)
                if v > 0.05:
                    note(p['name'], n, pan, tilt, 'robot', v)""", """for p in plist:
    # Test each distinct pose. Fixed parts ignore both axes; pan-only parts
    # ignore tilt. This preserves coverage without repeating the same Boolean.
    pans = PAN_SAMPLES if p['motion'] in ('pan', 'tilt', 'servo') else (0.0,)
    tilts = TILTS if p['motion'] == 'tilt' else (0.0,)
    for pan in pans:
        for tilt in tilts:
            s = posed(p, pan, tilt)
            for n, r in robot:
                tests += 1
                v = overlap(s, r)
                if v > 0.05:
                    note(p['name'], n, pan, tilt, 'robot', v)""")
replace("    and report['checks']['master_unchanged'])", """    and report['checks']['master_unchanged']
    and not report['checks']['robot_solids_missing']
    and not tilt_bad
    and all(r['on_z0'] and r['probes_pass'] and r['mesh_solid']
            and not r['mesh_non_manifold'] and r['mesh_volume_error_pct'] < .1 for r in exp_report))""")
replace("before = {str(MASTER): digest(MASTER), str(SOURCE): digest(SOURCE)}", "before = {str(MASTER): digest(MASTER), str(SOURCE): digest(SOURCE), str(Path(__file__)): digest(__file__)}")
replace("report['pending'] = {}", """report['pending'] = {
    'sensor_mounting': 'ToF/radar attachment not yet designed; dual carrier remains held.',
    'harness_and_stops': 'Flex routing, strain relief and mechanical stops are not designed.',
    'horn_screws': 'Actual screw head and available thread engagement need full assembly checks.',
    'bearing_spacer': 'The modeled 9 mm inner-race spacer is not confirmed available hardware.',
    'screen': 'Pocket fit passed; final window alignment and corner screws remain unreported.',
}""")
replace("report['drive'] = {", """report['checks']['belt_path_at_carriage_ends'] = {
    str(c): {'pitch_path_length_mm': belt_len(c, R_DRIVE_P, R_DRIVEN_P),
             'available_belt_length_mm': BELT_TEETH * PITCH,
             'note': 'Taut envelope only; set tension on the actual belt, not at a prescribed stop.'}
    for c in (C_MIN, C_NOM, C_MAX)}
report['drive'] = {""")
replace("doc.Label = 'Gladiator head v0.4 - pan stack (stage 1)'", "doc.Label = 'Gladiator head v0.4 - pan and tilt, corrected 2026-10-05'")
replace("'GH44 face DOWN (register recess on the bed, relieved), arms up; no support'", "'GH44 face DOWN (through register opening on the bed, relieved), arms up; no support'")
replace("'HORN_C %.2f (H6). Not reported: whether the circlip seated on the winning post.'", "'HORN_C %.2f (H6). Circlip seating confirmed by Jim, 2026-10-03.'")
replace("""'The horn arm thickness (%.1f) and the boss-to-horn gap (%.2f) are ASSUMED. They set the servo height, so '
    'they set the belt alignment. The first assembly should leave room to shim it.' % (ARM_T, HORN_G),""", """'The installed horn hub top is measured at 16.5 above the ear underside. Arm thickness %.1f, '
    'approximately 1 mm hub rise and lower hub geometry remain partly assumed; derived gap %.2f. '
    'Verify the complete screw and belt fit at first assembly.' % (ARM_T, HORN_G),""")
replace("'Sampled rigid-solid checks every 5 degrees of pan. They do not prove clearance between samples, nor '", "'Sampled rigid-solid checks every 5 degrees of pan and tilt. They do not prove clearance between samples, nor '")
replace("'assumed': report['assumed'], 'release': report['release']", "'assumed': report['assumed'], 'settled': report['settled'], 'release': report['release']")
replace("Path('/tmp/v04_summary.txt').write_text(NL.join(lines))", "(OUT / 'build-summary.txt').write_text(NL.join(lines))\nPath('/tmp/v04_summary.txt').write_text(NL.join(lines))")
replace("A.closeDocument(doc.Name)", """A.closeDocument(doc.Name)
if not report['checks']['sampled_geometry_pass']:
    raise RuntimeError('v04 failed validation; do not regenerate or replace print plates.')""")
# Correct obsolete prose without changing geometry.
start = source.index('What it INHERITS from v0.3')
end = source.index('\nFrame:', start)
source = source[:start] + 'Stage 2 regenerates the tilt yoke, GH44 receiver, carrier and display frame.\nOnly sensor clearance envelopes and unused carrier variants remain inherited references.' + source[end:]

plate_target = ROOT/'scripts/build_head_v04_plates.py'
plate_original = plate_target.read_bytes()
plate = plate_original.decode('utf-8')
anchor = "NL = chr(10)"
assert plate.count(anchor)==1
plate = plate.replace(anchor, """validation = json.loads((OUT / 'validation.json').read_text())
assert validation['checks']['sampled_geometry_pass'], 'Head build must pass before plate generation'
approved = {r['part']: r for r in validation['stl']}
for names in PLATES.values():
    for name in names:
        assert approved[name]['released'], name + ' is held'
        assert approved[name]['mesh_solid'] and not approved[name]['mesh_non_manifold'], name
NL = chr(10)""")
anchor = "    path = OUT / 'plates' / fname"
assert plate.count(anchor)==1
plate = plate.replace(anchor, "    assert offbed == 0 and overlaps == 0, fname + ' layout failed'\n" + anchor)

stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
backup = OUT/'before'/stamp
backup.mkdir(parents=True)
paths = [target, plate_target, ROOT/'cad/head/v04-pan-stack/README.md']
paths += [p for p in (ROOT/'cad/head/v04-pan-stack').rglob('*') if p.is_file()]
manifest = {}
for p in dict.fromkeys(paths):
    if not p.exists(): continue
    rel = p.relative_to(ROOT)
    dest = backup/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,dest)
    manifest[str(rel)] = hashlib.sha256(p.read_bytes()).hexdigest()
(backup/'sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Guard against edits since reading the shared files.
assert target.read_bytes()==original and plate_target.read_bytes()==plate_original, 'Concurrent source change; retry from current source'
target.write_text(source)
plate_target.write_text(plate)
(OUT/'source-integration.json').write_text(json.dumps({'backup':str(backup),
    'old_source_sha256':hashlib.sha256(original).hexdigest(),
    'new_source_sha256':hashlib.sha256(target.read_bytes()).hexdigest()},indent=2)+'\n')
print('Integrated guarded source fixes; previous files preserved at',backup)

