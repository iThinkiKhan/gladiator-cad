# Mast-head review — Codex, 2026-10-05

Active isolated work: `cad/head/review-20261005/`. The current v04 generator and its outputs are being rebuilt by another process; this review preserves them and the master.

## Confirmed receiver defect after the 16.5 mm horn-height update

Jim confirmed in this review that 16.5 mm is to the **raised center hub**. Arm top is therefore 15.5 mm above the ear using the recorded approximately 1 mm hub rise.

The fixed `cx(3.5, -25.5, 7.0, T.y, TZ)` driver cut ends at x=-18.5. The new screw-bearing roof spans x=-21.1 to -19.9, so the cut removes it completely. A solid intersection against the annulus between diameter 3.4 and the assumed diameter-4 screw head reports **0.000 mm3 material remaining**, expected **4.184601 mm3**. This is not detected by the existing no-collision tests. Do not print the updated GH44 receiver on Plate 3 until corrected.

The correction stops the driver cut at `TS_X0 - (rim_l + POCKET_DEPTH + BOSS_RECESS + ROOF_T)`, currently x=-21.1, and ends the driver-access validation probe just before that face. An annular bearing-material assertion prevents recurrence. Actual screw head diameter and thread engagement still require hardware verification.

**Follow-up: the roof correction also needs a final screw-hole cut.** `left_arm` spans x=-24..-21 and is fused AFTER `horn_plate()` cuts the center hole. Stopping the driver at -21.1 therefore leaves a **0.1 mm diaphragm across the screw passage**, x=-21.1..-21.0. The restored roof alone is not sufficient. After the driver cut, cut `cx(CENTRE_HOLE / 2, -25.6, TS_X0 - rim_l + 25.7, T.y, TZ)` through the completed receiver union. A diameter-3.38 shank probe from x=-25.5 through the horn-pocket mouth must have zero intersection, in addition to the annulus being intact. This is implemented in the isolated candidate. The current v04 source observed at 10:38 has the roof correction but still lacks this final shank cut.

Also corrected in the isolated candidate: belt reference is regenerated at each carriage distance instead of remaining at nominal distance; tilt sweep is every 5 degrees; both carriage-end checks include negative tilt; release validation includes missing robot objects, STL probes/manifoldness and tilt-driver access. Candidate is not a print release. Full validation is in progress.
