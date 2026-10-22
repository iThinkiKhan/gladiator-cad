# Mast-head review — Codex, 2026-10-05

Active isolated work: `cad/head/review-20261005/`. The current v04 generator and its outputs are being rebuilt by another process; this review preserves them and the master.

## Confirmed receiver defect after the 16.5 mm horn-height update

Jim confirmed in this review that 16.5 mm is to the **raised center hub**. Arm top is therefore 15.5 mm above the ear using the recorded approximately 1 mm hub rise.

The fixed `cx(3.5, -25.5, 7.0, T.y, TZ)` driver cut ends at x=-18.5. The new screw-bearing roof spans x=-21.1 to -19.9, so the cut removes it completely. A solid intersection against the annulus between diameter 3.4 and the assumed diameter-4 screw head reports **0.000 mm3 material remaining**, expected **4.184601 mm3**. This is not detected by the existing no-collision tests. Do not print the updated GH44 receiver on Plate 3 until corrected.

The correction stops the driver cut at `TS_X0 - (rim_l + POCKET_DEPTH + BOSS_RECESS + ROOF_T)`, currently x=-21.1, and ends the driver-access validation probe just before that face. An annular bearing-material assertion prevents recurrence. Actual screw head diameter and thread engagement still require hardware verification.

**Follow-up: the roof correction also needs a final screw-hole cut.** `left_arm` spans x=-24..-21 and is fused AFTER `horn_plate()` cuts the center hole. Stopping the driver at -21.1 therefore leaves a **0.1 mm diaphragm across the screw passage**, x=-21.1..-21.0. The restored roof alone is not sufficient. After the driver cut, cut `cx(CENTRE_HOLE / 2, -25.6, TS_X0 - rim_l + 25.7, T.y, TZ)` through the completed receiver union. A diameter-3.38 shank probe from x=-25.5 through the horn-pocket mouth must have zero intersection, in addition to the annulus being intact. This is implemented in the isolated candidate. The current v04 source observed at 10:38 has the roof correction but still lacks this final shank cut.

Also corrected in the isolated candidate: belt reference is regenerated at each carriage distance instead of remaining at nominal distance; tilt sweep is every 5 degrees; both carriage-end checks include negative tilt; release validation includes missing robot objects, STL probes/manifoldness and tilt-driver access. Candidate is not a print release. Full validation is in progress.


## Completed validation

The isolated candidate passed 117,950 head/robot/carriage-end comparisons with no detected collision, modeled ToF obstruction or axial cable overlap. All 24 assembly solids and 11 STL exports pass. Independent native/STEP reopen and exact solid comparison pass: only the receiver changes. Saved receiver annulus 4.1846014146 mm3, shank overlap 0.000000 mm3. Master unchanged. Full evidence, README and archive: `cad/head/review-20261005/`. No printer queue modifications or print starts. See HANDOFF.md for the still-required shank fix in concurrent v04 work.

## Canonical integration completed, measured sensor candidate underway

The v04 generator now includes both receiver fixes, not only the retaining-roof fix.
Canonical build passed117,950 sampled comparisons; Plates2–4 rebuilt with initialized
freecadcmd. Independent reopen compared every canonical assembly solid to the isolated
review: zero geometric difference. STEP valid24 solids and all Plates1–4 have exact
canonical STL topology with only placement and <=0.00013 mm XML/float precision error.
Backup of pre-integration source/output/documentation is in cad/head/integration-20261005/.
The old Plate3 shank-diaphragm blocker is resolved. No printer queue change or print start.

Jim confirmed ToF42 x27.5 including ears; radar22 x30, corner diameter3 holes with2 mm
gap to their outer edges, maximum rear components8. Measurements and manufacturer-drawing
derivation are recorded in measurements/mast-head.md. Isolated v05 source builds84 mm
carrier, separate four-post sensor frames, tested nut/pilot fits,14/12 mm rear stand-offs.
Initial nut-entry route intercepted the neighboring ToF post; entries now face outboard.
Assembly access is explicitly checked; radar frame fits after carrier but before display.
ToF frame is attached before carrier installation. Complete v05 sweeps are in progress;
do not treat its parts as validated until validation.json sampled_geometry_pass is true
and the saved-artifact/plate verification has completed. No new fit coupon was made.

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

Archive SHA256: 335431b8971dd04327f13a4ae7c1c213cfd4cd50c54a7ed306550b2bb747c6cb
