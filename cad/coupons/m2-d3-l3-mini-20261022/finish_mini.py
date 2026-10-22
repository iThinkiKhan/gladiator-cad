from pathlib import Path
import json, shutil, zipfile
O=Path(__file__).resolve().parent
R=Path('/home/buralien/projects/gladiator-cad')
assert json.loads((O/'saved-file-verification.json').read_text())['all_4_blind_bores_verified']
result=json.loads((O/'sliced/result.json').read_text())
assert result['return_code']==0 and not result['sliced_plates'][0]['warning_message']
gcode=(O/'sliced/plate_1.gcode').read_text()
stats=[l for l in gcode.splitlines() if 'estimated printing time' in l or 'filament used [g]' in l]
plate=O/'M2_D3_L3_Mini_EnderNeo_PLA.3mf'
shutil.copy2(O/'M2_D3_L3_Coupon_EnderNeo_PLA.3mf',plate)
p=O/'plate-validation.json';report=json.loads(p.read_text());report.update(status='OrcaSlicer slice passed without warnings',statistics=stats,slice_result=result);p.write_text(json.dumps(report,indent=2))
readme='''# Four-hole M2 D3 L3 coupon — current revision

Jim requested a smaller first-pass coupon, 2026-10-22. This replaces the 16-hole test as the current print choice.

Open M2_D3_L3_Mini_EnderNeo_PLA.3mf. Four labeled upright blind holes: 2.8, 2.9, 3.0, 3.1 mm CAD diameters, each 3.6 mm deep with a 0.15 mm entry chamfer. Envelope 40 x 13 x 6 mm; 7 mm bosses, 2.4 mm floor. Clipped corner marks the 2.8 end.

Print flat base down at 100% scale. Existing EnderNeo PLA profile, 0.20 mm layers, four walls, 25% infill, no supports or brim. Native/STEP reopen, four bore/floor checks, manifold STL and warning-free Orca slicing verified. No print started.

Check delivered inserts against the listing's nominal M2 thread, 3 mm knurled OD, 3 mm length. Try 3.0 first; go smaller if loose or larger if installation needs excessive pressure. Install flush using the supplier's PLA guidance and consistent temperature/dwell. Cool completely. Reject bulging, cracks, tilt, spinning or pullout. Keep the test screw tip clear of the blind floor. Record the winning CAD label in results.csv; confirm with a fresh insert before applying it widely. This small coupon tests the vertical print orientation; sideways holes need confirmation if used later. A physical fit result is still pending.

build_coupon.py is the editable source; dimensions on the saved FreeCAD solid are descriptive metadata. Existing project geometry is preserved.

Slicer estimates:
'''
(O/'README.md').write_text(readme+'\n'.join(stats)+'\n')
shutil.copy2(plate,Path.home()/'3D-Printer/Incoming/Gladiator/Gladiator_COUPON_M2_D3_L3_20261022.3mf')
note=R/'docs/ai/agents/codex-m2-d3-l3-coupon-20261022.md'
note.write_text(note.read_text()+'''\n## Simplified at Jim's request, 2026-10-22

Current choice: cad/coupons/m2-d3-l3-mini-20261022/, four upright bores 2.8/2.9/3.0/3.1, depth 3.6, 40 x 13 x 6 mm. Native/STEP/STL and four blind-bore checks pass; Orca slice without warnings. Replaced only the previously generated named Incoming coupon with this smaller version. The earlier full package remains preserved. Physical winner pending; horizontal fit untested by the mini coupon.
''')
handoff=R/'docs/ai/HANDOFF.md';t=handoff.read_text();key='## M2 D3 L3 coupon — 2026-10-22 (Codex)';t=t.replace(key,key+'\n\n**Current revision:** Jim requested a smaller first pass. Use cad/coupons/m2-d3-l3-mini-20261022/ (four upright holes 2.8/2.9/3.0/3.1 mm). Incoming coupon updated to mini. Geometry and warning-free slice verified; physical winner pending. The larger version below is retained as history.',1);handoff.write_text(t)
with zipfile.ZipFile(O/'M2_D3_L3_Mini_Package.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(O.iterdir()):
        if p.is_file() and p.suffix not in ['.zip','.log'] and p.name!='M2_D3_L3_Coupon_EnderNeo_PLA.3mf':z.write(p,p.name)
print('\n'.join(stats))
