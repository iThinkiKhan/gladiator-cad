from pathlib import Path
import json, re, shutil, zipfile, hashlib
O=Path(__file__).resolve().parent
R=Path('/home/buralien/projects/gladiator-cad')
result=json.loads((O/'sliced/result.json').read_text())
assert result['return_code']==0 and not result['sliced_plates'][0]['warning_message']
gcode=(O/'sliced/plate_1.gcode').read_text()
stats=[l for l in gcode.splitlines() if any(k in l.lower() for k in ['estimated printing time','filament used [','total filament'])]
p=O/'plate-validation.json';report=json.loads(p.read_text());report.update(status='OrcaSlicer 2.4.2 slice passed without warnings',slice_result=result,statistics=stats)
p.write_text(json.dumps(report,indent=2))
(O/'slice-statistics.txt').write_text('\n'.join(stats)+'\n')
readme=O/'README.md';readme.write_text(readme.read_text()+'\nOrcaSlicer 2.4.2 validation slice succeeded without warnings. Slicer statistics:\n\n```\n'+'\n'.join(stats)+'\n```\n')
# Remove only the obsolete diagnostic produced by this build's repaired first attempt.
stale=O/'BUILD_ERROR.txt'
if stale.exists():stale.unlink()
incoming=Path.home()/'3D-Printer/Incoming/Gladiator'/ 'Gladiator_COUPON_M2_D3_L3_20261022.3mf'
shutil.copy2(O/'M2_D3_L3_Coupon_EnderNeo_PLA.3mf',incoming)
note='''# M2 D3 L3 coupon — Codex, 2026-10-22

Jim supplied a listing screenshot: M2 x D3 x L3 (100 pcs). Treat 3 mm OD and 3 mm length as nominal listing data pending stock measurement. The listing's 2 mm item diameter / 2.2 mm groove are not pilot-bore dimensions.

New isolated package: cad/coupons/m2-d3-l3-20261022/. 80 x 25 x 9.89 mm coupon, 2.60–3.30 mm diameters in 0.10 steps, 8 vertical + 8 horizontal blind bores, 3.60 depth, 0.15 entry chamfer. Labels over each bore. Existing M2-A and production CAD preserved.

Native/STEP reopen, all 16 bore void/floor/wall checks, manifold STL, 3MF/STL agreement, and OrcaSlicer 2.4.2 slice without warnings passed. EnderNeo PLA profile, 0.20 layers, 4 walls, 25% infill, no supports. New named 3MF copied to Incoming; no print started. Editable builder, README, results CSV and verification JSON included.

Next: check stock OD/length; print and test using intended project material/profile; report separate upright and horizontal winners and installation conditions. Confirm repeatability with fresh inserts before applying bore values. No winner recorded as measured and no project bore changed.
'''
(R/'docs/ai/agents/codex-m2-d3-l3-coupon-20261022.md').write_text(note)
handoff=R/'docs/ai/HANDOFF.md';text=handoff.read_text();heading='## M2 D3 L3 coupon — 2026-10-22 (Codex)'
if heading not in text:
    intro='\n\n'+heading+'\n\nInsert-specific coupon delivered at cad/coupons/m2-d3-l3-20261022/; new 3MF in Incoming. Listing nominal M2 x OD3 x L3. Tests 2.60–3.30 by 0.10, 3.60 deep, upright and sideways. CAD/mesh/plate and warning-free Orca slice verified. Physical winners pending; do not apply bore changes yet. Existing M2-A and project parts preserved. See agents/codex-m2-d3-l3-coupon-20261022.md.\n'
    first,sep,rest=text.partition('\n');handoff.write_text(first+intro+'\n'+rest)
files=[p for p in O.iterdir() if p.is_file() and p.suffix not in ['.log','.zip']]
(O/'sha256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
with zipfile.ZipFile(O/'M2_D3_L3_Coupon_Package.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(O.iterdir()):
        if p.is_file() and p.suffix not in ['.zip','.log'] and not p.name.endswith('ERROR.txt'):z.write(p,p.name)
    z.write(O/'sliced/result.json','slice-validation/result.json')
print('\n'.join(stats))
print('Delivered:',incoming)
