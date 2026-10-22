"""Create a review candidate from the preserved v04 source; never edit v04 in place."""
from pathlib import Path

folder = Path(__file__).resolve().parent
source = (folder / 'build_head_v04_source.py').read_text(encoding='utf-8-sig')

def replace(old, new):
    global source
    assert source.count(old) == 1, (old[:100], source.count(old))
    source = source.replace(old, new)

replace("OUT = ROOT / 'cad/head/v04-pan-stack'", "OUT = ROOT / 'cad/head/review-20261005/candidate'")
replace("before = {str(MASTER): digest(MASTER), str(SOURCE): digest(SOURCE)}", "before = {str(MASTER): digest(MASTER), str(SOURCE): digest(SOURCE), str(Path(__file__)): digest(__file__)}")
replace("rec = rec.cut(cx(3.5, -25.5, 7.0, T.y, TZ))                       # driver access to the horn screw", """# Stop the driver counterbore at the actual screw-bearing face. The former
# hard-coded x=-18.5 endpoint removed the entire roof after the horn-height update.
TILT_ROOF_X = TS_X0 - (rim_l + POCKET_DEPTH + BOSS_RECESS + ROOF_T)
assert -25.5 < TILT_ROOF_X
rec = rec.cut(cx(3.5, -25.5, TILT_ROOF_X + 25.5, T.y, TZ))
# The left arm is fused AFTER horn_plate() cuts its hole. Recut the shank path
# through the completed union so the arm cannot seal the center of the roof.
rec = rec.cut(cx(CENTRE_HOLE / 2, -25.6, TS_X0 - rim_l + 25.7, T.y, TZ))
shank_probe = cx(CENTRE_HOLE / 2 - .01, -25.5, TS_X0 - rim_l + 25.5, T.y, TZ)
shank_overlap = rec.common(shank_probe).Volume
assert shank_overlap < 1e-6, 'Tilt horn screw shank blocked'
report['checks']['tilt_screw_shank_overlap_mm3'] = shank_overlap
# Probe the whole load-bearing annulus, not just whether the object remains valid.
roof_probe = cx(2.0, TILT_ROOF_X, ROOF_T, T.y, TZ).cut(
    cx(CENTRE_HOLE / 2, TILT_ROOF_X - .1, ROOF_T + .2, T.y, TZ))
roof_actual = rec.common(roof_probe).Volume
assert abs(roof_actual - roof_probe.Volume) < 1e-6, 'Tilt horn screw bearing face lost'
report['checks']['tilt_screw_bearing_annulus_mm3'] = roof_actual
report['checks']['tilt_screw_bearing_annulus_expected_mm3'] = roof_probe.Volume
report['checks']['tilt_screw_roof_thickness_mm'] = ROOF_T""")
replace("TILTS = (-25.0, 0.0, 25.0)", "TILTS = tuple(float(t) for t in range(-25, 26, 5))")
replace("    s = p['shape'].copy()\n    if C is not None", """    # Changing the carriage must also change the belt path in collision checks.
    # At slack travel this is a taut-path envelope, not a simulation of a sagging belt.
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
    # Fixed parts do not change with pan or tilt. Pan-only parts do not change
    # with tilt. Test every DISTINCT rigid pose, avoiding redundant Booleans.
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
replace("tilt_cyl = cx(3.4, -90.0, 90.0 - 19.2, T.y, TZ)", "tilt_cyl = cx(3.4, -90.0, 90.0 + TILT_ROOF_X - .01, T.y, TZ)")
replace("    and report['checks']['master_unchanged'])", "    and report['checks']['master_unchanged']\n    and not report['checks']['robot_solids_missing']\n    and not tilt_bad\n    and all(r['on_z0'] and r['probes_pass'] and r['mesh_solid']\n            and not r['mesh_non_manifold'] and r['mesh_volume_error_pct'] < .1 for r in exp_report))")
replace("'released': name not in HOLD", "'released': False")
replace("report['pending'] = {}", """report['pending'] = {
    'sensor_mounting': 'Carrier mounting for the actual sensors is not designed.',
    'harness_and_stops': 'Flex harness, strain relief and mechanical travel stops are not designed.',
    'horn_screw': 'Verify real head diameter and usable thread engagement through both horn plates.',
    'spacer': 'The 9 mm inner-race spacer is reference geometry, not an available-hardware confirmation.',
    'screen': 'Pocket fit passed; final window alignment and corner screws remain unreported.',
}
report['review'] = {
    'date': '2026-10-05',
    'status': 'ISOLATED REVIEW CANDIDATE; no print release or printer-queue changes',
    'horn_height': 'Jim confirmed 16.5 mm to the raised center hub in this review.',
}""")
replace("'tilt_horn_screw_along_axis'] = {", "'tilt_horn_screw_along_axis'] = {\n    'driver_end_x': TILT_ROOF_X - .01,")
replace("report['drive'] = {", """report['checks']['belt_path_at_carriage_ends'] = {
    str(c): {'pitch_path_length_mm': belt_len(c, R_DRIVE_P, R_DRIVEN_P),
             'available_belt_length_mm': BELT_TEETH * PITCH,
             'note': 'Taut envelope only; slack/sag and belt installation need physical verification.'}
    for c in (C_MIN, C_NOM, C_MAX)}
report['drive'] = {""")
replace("doc.Label = 'Gladiator head v0.4 - pan stack (stage 1)'", "doc.Label = 'Gladiator head - corrected review 2026-10-05'")
replace("Path('/tmp/v04_summary.txt').write_text(NL.join(lines))", "(OUT / 'build-summary.txt').write_text(NL.join(lines))")
replace("A.closeDocument(doc.Name)", """A.closeDocument(doc.Name)
if not report['checks']['sampled_geometry_pass']:
    raise RuntimeError('Review candidate failed; inspect validation.json. Not released.')""")
(folder / 'build_head_review.py').write_text(source, encoding='utf-8')
print(folder / 'build_head_review.py')


