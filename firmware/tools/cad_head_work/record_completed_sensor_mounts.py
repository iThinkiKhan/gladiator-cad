from pathlib import Path
import hashlib,json
root=Path('/home/buralien/projects/gladiator-cad')
out=root/'cad/head/v05-sensor-mounts'
r=json.loads((out/'validation.json').read_text())
assert r['checks']['sampled_geometry_pass']
a=json.loads((out/'artifact-verification.json').read_text())
assert a['native_reopened_valid'] and a['step_valid'] and a['preview_matches_final_native']
archive=root/'cad/head/integration-20261005/Gladiator_MastHead_v05_20261005.zip'
sha=hashlib.sha256(archive.read_bytes()).hexdigest()
with (root/'docs/ai/agents/codex-head-review-20261005.md').open('a') as f:
    f.write('''
## Completed v05 measured sensor mounts and delivery

Final candidate: cad/head/v05-sensor-mounts/README.md. Source scripts/build_head_v05.py;
Plate5 builder scripts/build_head_v05_plate5.py. The84 mm carrier preserves the tested
GH44 male key. Removable ToF and radar frames use four captive M3 nuts and three rear
M2x6 screws each. ToF uses top two/bottom two of its six official holes; radar pitch15x23
comes from Jim's diameter3 and2 mm edge-gap measurements. Rear stand-offs: ToF14 with
M3x16, radar22 with M3x25. Radar advanced10 to clear the assumed whole-board field
reservation at25 degrees down;9 still intersected0.1293 mm3 in a targeted check.
Actual optical/antenna planes and RF performance remain unverified.

Final validation PASS:145,817 covered part/pose comparisons, zero collisions/ToF/radar
field-reservation intersections; clear11.9 mm axial cable probe;26 valid single solids;
13 valid solid/manifold STL exports. After advancing radar,27,867 comparisons were
fresh;117,950 unchanged comparisons reused only after exact BRep identity of24 solids
and unchanged source-master dependencies. All radar field poses rechecked. Runner and
baseline hashes plus exact differences are in validation_reuse. Initial rejected native,
STEP/STLs/validation/source remain under integration-20261005/v05-before-radar-shift/.

Independent native/STEP reopen and expected-five-object comparison to reviewed v04
passed. Final preview rendered from hashed saved native. Plate5 is3 objects,27 g solid
PLA estimate,25 mm tall, no off-bed parts/overlaps, all canonical STL topology matches.
Eight screw passages/seating annuli/nut sweeps and11 assembly tool paths pass. Assembly
order: ToF frame -> carrier -> radar frame -> display frame -> PCBs. Full instructions
specify4.8 mm maximum display driver shaft and actual screw/head fit checks.

Delivery archive includes current native/STEP,13 STL,Plate5 and corrected v04 Plates1–4,
source,measurement provenance,preview,validation and SHA256 manifest. Local delivery:
C:/PlatformIO/Projects/Gladiator/docs/mast-head/v05-sensor-mounts/.
No live GUI edit, printer-queue change, print start or new coupon. Complete harness,
strain relief/stops, horn screw fit,belt fit,spacer availability and display alignment
remain physical/unfinished checks, explicitly documented. No torque/payload rating.
''')
    f.write('\nArchive SHA256: '+sha+'\n')
with (root/'docs/ai/HANDOFF.md').open('a') as f:
    f.write('''
### Head continuation completed — 2026-10-05 (Codex)

The in-progress v05 state above is now **complete and validated**. Current prototype:
cad/head/v05-sensor-mounts/README.md; native/STEP,13 STL and3-part Plate5 are delivered.
Corrected canonical v04 Plates1–4 are included; receiver shank/roof blocker closed.
Measured radar hole pitch15x23. Final rear stand-offs14 ToF/22 radar, nominal screws
4 M3x16/4 M3x25. Radar was advanced10 for full modeled downward-field clearance.
145,817 comparisons covered with documented exact-geometry reuse; all final gates and
native/STEP/plate/preview verification pass. Archive:
cad/head/integration-20261005/Gladiator_MastHead_v05_20261005.zip.

Next work depends on actual assembly: connector leads/flex harness,strain relief/stops,
horn screw fit,belt fit,9 mm inner-race spacer availability,screen alignment/screws and
loaded stiffness. Optical/antenna planes/radar RF performance are unmeasured. No new
coupon or print initiated. Preserve backups and concurrent agents' work.
''')
shared=root/'docs/ai/SHARED.md'
if 'Current measured head prototype — 2026-10-05' not in shared.read_text():
    with shared.open('a') as f:
        f.write('''
## Current measured head prototype — 2026-10-05

cad/head/v05-sensor-mounts/README.md: reviewed v04 mechanics with corrected tilt screw
roof/passage,42x27.5 ToF and22x30 radar on removable frames. CAD/meshes/plates validated;
canonical v04 Plates1–4 plus sensor Plate5 delivered. Measurement provenance in
measurements/mast-head.md; remaining physical/harness work in HANDOFF.md.
''')
print(json.dumps({'completed':True,'archive_sha256':sha},indent=2))
