# Head v2 - compact balance and tensioner revision, 2026-10-30

Jim approved only review items 1 and 2: improve tilt balance and correct tensioner reach. This is the current CAD revision for those changes. The slotted mast, yoke, cable passage, pan indexing, stop features, firmware and print queue are retained.

## Result

The carrier side of the GH44 receiver is 2.5 mm shorter, bringing the carrier, camera, ToF and fitted display frame 2.5 mm toward the tilt axis. Local receiver reliefs clear the unchanged yoke and SG90 envelope through the existing tilt range. The tested horn pocket, horn screw bearing region, and pivot interface stay in their original position. The same carrier and four M3 attachment holes are used; other payload parts are relocated without shape changes.

The compact layout limits the useful shift: at 3.0 mm the carrier/yoke gap at maximum upward tilt drops to 0.25 mm; 3.5 mm collides. Selected 2.5 mm gives approximately 0.64 mm nominal minimum carrier/yoke clearance in the sampled range. This is a modest balance improvement, not a neutrally balanced head. Larger changes would require revisiting the features Jim asked to retain.

| CAD estimate, head level | Previous v2 | Revised v2 |
|---|---:|---:|
| Tilting mass, g | 104.92 | 104.36 |
| Payload COM ahead of tilt axis, mm | 21.59 | 19.21 |
| Gravity holding moment, kg cm | 0.2266 | 0.2005 |

Estimated level holding moment is reduced by **11.5%** with the same mass assumptions as the original v2 generator (PLA 1.24 g/cc x0.85 fill; prior component masses and wire/screw allowances). These are not measured weights or servo performance results.

## Tensioner

Use **M3 x20** in place of the specified M3 x16, retaining the current captive nut and carriage. At C48, screw reach to the pad is 17.5 mm, leaving 2.5 mm between its under-head face and the lug. At C38 that gap is 12.5 mm. The screw bears on the fixed pad and stays in the same world position while the carriage/nut moves along it.

The review includes a full shaft plus conservative 6 mm diameter x3 mm screw-head envelope and 5.8 AF x2.4 mm nut envelope. Hardware clearance was checked at every 1 mm carriage setting, C38..48, along with driver access. Confirm the actual screw/nut stock before assembly.

## What to use

- `Gladiator_Head_v2_Balanced_REVIEW.FCStd`: colored complete assembly; new receiver orange and tensioner blue.
- `Gladiator_Head_v2_Balanced.FCStd`: underlying complete native CAD.
- `GH44_Tilt_Receiver_Balanced.step` and `stl/GH44_Tilt_Receiver_Balanced.stl`: new receiver, GH44 face down in print coordinates.
- `Gladiator_Head_v2_Balanced_assembly.step`: assembly exchange file.
- `balance_tensioner_review.png`: before/after view and estimated COM markers.
- `build_balance_tensioner.py`, `verify_saved.py`, `style_review.py`, `render_balance.py`, `validation.json`: construction, verification and review sources.
- `inputs/`: archived baseline native model and validation for provenance.

Only the receiver is newly revised relative to the existing v2 draft. Existing v2 print parts are still required if not yet printed; their STLs were not replaced. No slicing or G-code has been prepared by this revision.

## Checks

- Valid single receiver solid; STEP re-import matches native volume; STL closed/manifold and consistent volume.
- Four GH44 screw passages and front bearing lands retained.
- All other source parts retain geometry after accounting for the explicit payload translation.
- No home-pose interference over 0.05 mm3, except the baseline's two intentional bearing fits (excluded) and robot-context internal pairs (excluded).
- No sampled motion interference: tilt -38..34 every 2 deg; pan -20..180 every 20 deg, including the coupled 60T pulley/horn rotation. Pan stage against new hardware also checked every 5 deg.
- Tensioner hardware at every C38..48 setting and driver access clear.
- Original baseline CAD hash unchanged. Independent saved-file checks pass.

Rebuild on cad-lab using system Python: `python3 build_balance_tensioner.py`, then `python3 verify_saved.py`. Styling uses `xvfb-run -a freecad style_review.py`; mesh picture uses `python3 render_balance.py`. The builder reads the preserved baseline in the parent folder; archived input copies carry its recorded SHA256.

Not physically tested: harness bends/strain relief, fastener fit, loaded servo motion, print support, or structural stiffness. Current firmware limits remain unchanged. No printer started.
