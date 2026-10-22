from pathlib import Path
import json,hashlib
R=Path('/home/buralien/projects/gladiator-cad');O=R/'cad/v2/enclosure/round5-20261021'
q=json.loads((O/'independent-verification.json').read_text());assert q.get('pass') and not q.get('failures'),q
v=json.loads((O/'validation.json').read_text())
for name,sha in v['source_hashes'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==sha,name
note=(O/'codex-round5-notes.md').read_text()
(R/'docs/ai/agents/codex-round5-styling-20261021.md').write_text(note)
p=R/'docs/ai/HANDOFF.md';text=p.read_text()
heading='## Round 5 styling CAD review — 2026-10-21 (Codex)'
entry=heading+'\n\nJim requested Round 5 styling while keeping v2.8 and its fit/structural geometry untouched. New model and complete review package: cad/v2/enclosure/round5-20261021/. Additive exterior receivers, M2-retained curved scuta/tablets/aquila, sculpted eagle relief, existing vent locations preserved, removable head clamps with captive contact shoes. Independent native/STEP/STL, material-preservation, interface, interference and service-path checks pass; source hashes unchanged. Physical follow-up: existing M2-A bore calibration/insert dimensions and loaded head movement/accessory weight. No print or existing CAD changed. Details: agents/codex-round5-styling-20261021.md.\n\n'
if heading not in text:text=text.replace('# Current Handoff\n','# Current Handoff\n\n'+entry,1);p.write_text(text)
p=R/'docs/ai/DECISIONS.md';text=p.read_text()
heading='## 2026-10-21 — Round 5 styling, original structural CAD preserved'
if heading not in text:
 text+='\n'+heading+'\n\nJim selected curved scuta and a lightning-bolt aquila from the styling guide, requested firmly mounted insets and a more detailed eagle, and authorized adaptations needed to make the CAD work. The implementation must remain a separate version and preserve the original CAD and existing structural/fit interfaces. Review implementation: cad/v2/enclosure/round5-20261021/. New insert calibration and physical accessory testing are not accepted results.\n';p.write_text(text)
summary='\n## Completed saved-file checks\n\n- 22 valid single-solid printed parts; all individual meshes solid and manifold; STEP reopens with 22 solids and matching geometry under documented spatial checks.\n- Original shell material retained; 58 context shapes match the baseline; nine original enclosure files hash-match.\n- No detected new-part, existing-component or screw interference, including the camera service v2 case as context.\n- Hood 150 mm rearward, right panel 120 mm at 45 degrees, left panel 20 mm at 45 degrees then 90 mm outward at 15 degrees: additions clear at 1 mm samples against authenticated original sweep evidence. The hood-owned switch and speaker also move with the hood in this check.\n- Head additions clear eleven relative tilt poses; original pan range retained; fixed structure and sensor fields remain clear under the stated geometric bounds.\n- Existing vents/SMA access and all seven new body insert bores checked clear.\n\nSee `independent-verification.json` for values, thresholds and the distinction between CAD verification and physical confirmation.\n'
p=O/'README.md';text=p.read_text()
if '## Completed saved-file checks' not in text:p.write_text(text+summary)
for name,removed in q['baseline_material_retained'].items():
 v['baseline_preservation'][name]=dict(removed_mm3=removed,added_mm3=q['exterior_material_accounting'].get(name,{}).get('volume_increase_mm3',0.0))
v['mesh_repair']=dict(part='Front_Left',maximum_boundary_vertex_displacement_mm=.0007180138893586579,native_geometry_changed=False,solid_after_repair=True)
v['status']='Round 5 CAD REVIEW — independent geometry checks PASS; M2 calibration and loaded head physical checks pending'
v['independent_verification']='independent-verification.json'
(O/'validation.json').write_text(json.dumps(v,indent=2))
files=[O/'Gladiator_Round5.FCStd',O/'Gladiator_Round5_PrintParts.step']+sorted((O/'stl').glob('*.stl'))
manifest={str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(O/'artifact-sha256.json').write_text(json.dumps(manifest,indent=2))
# Remove only stale errors produced by this isolated build, after the final independent pass.
for name in ('BUILD_ERROR.txt','PRESENTATION_ERROR.txt'):
 p=O/name
 if p.exists():p.unlink()
print(json.dumps({'pass':q['pass'],'parts':len(q['native_and_stl']),'removed_mm3':q['baseline_material_retained'],'removal':q['removal'],'head_hits':q['head_motion_hits'],'camera_context':q['camera_context_objects'],'failures':q['failures']},indent=2))


