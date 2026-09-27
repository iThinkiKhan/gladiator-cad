# Power board tray v3 — 2026-09-27

Built by `scripts/build_power_cradle_v3.py`. The script reads the master without changing it,
checks everything against solids, and refuses to export if any check fails. Results are in
`validation.json`, and `tray-v3-vs-v2.png` compares v3 with v2.

Print: `Gladiator_PowerBoardTray_v3_print-on-rear-face.stl`. It prints rear face down, the same
way as v2, and stands 111 mm tall on a 364 mm² base, so use a brim. About 22 g solid PLA. The
front wall and the rear wall between the arms print as bridges (about 41 and 15 mm), as they did
on v2.

## What changed from v2, and why

| Jim's finding | v3 |
| --- | --- |
| Rear pilot tabs can't reach the holes: the real pilots are 1.2 further out, under the rail rear feet | Pilot tabs removed. The two rear slit bolts, unchanged, are the only deck fixings (Jim's choice) |
| v2 is fragile; make it stronger | Arms, root, flares and rear posts grow upward to Z 40. The arm web sits on the mast collar rim from Z 20. The floor goes from 1.0 to 1.6 |
| The extra length was filled solid; it should be open wire room | The wall stands 2.9 clear of each board end (0.4 before). The board and its screw holes are unmoved |
| Found in the model: v2's floor sat 3.3 into the installed cells | The whole tray is lifted 4.3, so the floor clears the cells by 1.0 |

Strength at the sections that matter, cut area and (depth):

| Section | v2 | v3 |
| --- | --- | --- |
| Arm beside the mast (Y 115) | 21 mm² (6.0) | 82 mm² (20.0) |
| Root behind the board (Y 96) | 56 mm² (7.8) | 136 mm² (13.5) |
| Rear flare (Y 125) | 34 mm² (6.0) | 115 mm² (20.0) |

Bending strength scales with depth squared and stiffness with depth cubed, so the arms are
roughly an order of magnitude stronger. That still holds in this print orientation, where the
arm length runs across the layers.

## Kept as v2 had it

- The pack leads leave the rear of the pack and run over the mast base. Nothing that was air
  below or beside v2's arms is filled; the growth is upward only, inside v2's plan footprint.
  These regions are checked empty:
  - the outboard lanes, X 18.2–21.9 and its mirror, over Y 93–127;
  - the centre gap in front of the mast;
  - everything below Z 20 behind the board.
- The mast cross pin is reachable from both sides with the tray on. The mast base M2 screws
  are untouched.
- The tray drops straight down onto the mast base with the mast tube in place, with no
  contact over 40 mm of travel.
- Rear tabs are unchanged (Z 2.2–5.2), so the existing M2 slit bolts fit. There is a Ø6 driver
  shaft clear above each bolt.
- Clearances: cells 1.0, mast tube 0.4 (as v2), rails 0.1 (as v2).
- There is 17.8 mm of connector room above the board, up to the upper deck (v2 had 16.2).
