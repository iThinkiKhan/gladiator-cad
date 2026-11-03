# Gladiator camera case v3 (camera service v3) - CAD draft, 2026-10-30

Camera service v2 with the cover held on M2 heat-set inserts. Not printed, not sliced.

## What changed from v2

| | v2 (Oct 21) | v3 |
|---|---|---|
| Cover fasteners | 2 x M3x12 + 2 side-loaded M3 nuts | 2 x M2x6 into 2 M2 heat-set inserts (M2x8 also fits) |
| Insert bore | - | 2.8 mm x 4.0 deep in the top of each tray lug, then a 2.2 x 4 screw-tip relief |
| Cover holes | 3.6 + bed chamfer | 2.6 (M2 clearance) + 0.35 bed chamfer |
| Lugs | radius 4.4, 10 mm off centre | radius 3.6, 11.8 mm off centre (keeps 1 mm of plastic between the SD-side insert and the SD finger recess) |
| Board retention with cover off | none (cover posts only) | one snap bump per long wall, catch face 0.15 mm in front of the PCB, about 0.2 mm grip per side |
| Lens hole | plain | 0.4 mm bed-side chamfer |
| Mass | tray 11514 mm3, cover 4569 mm3 | tray 10872, cover 4511 (about 0.9 g less, solid PLA) |

Unchanged: lay-in wire channels and closing skirts, 4.5 mm wire exits, tie passages, SD window and recess, lens
position, ToF gap (2.275), three M2x6 carrier screws and their driver access.

## Print and assembly

- Tray prints floor down, so both insert bores are upright at the top of the print. Press the inserts in from the
  cover seam with the iron before fitting the board.
- Cover prints outer face down (the bed side gets the chamfers).
- Snap bumps: push the board straight in past them; it clicks behind them. If too tight, shave the bumps with a file
  or Dremel. They sit on the long walls near the far (non-SD) end, away from the header pins.
- Hardware: 2 x M2 heat-set inserts, 2 x M2x6 (or M2x8), 3 x M2x6 carrier screws as before.

## Checks (all pass)

- `validation.json`: board/case/Dupont/wire-lay-in/board-insertion/cover-removal clearances, carrier and display
  screw access, M2 screw and driver vs case and head parts, 1 mm solid wall round each insert, screw heads vs ToF and
  camera fields of view, 231 pan/tilt poses + 1-degree tilt sweep in the v05 head (same checks as v2).
- `check_in_head_v2.json`: v3 swapped into the current head (Codex balanced model,
  `v2-mast-20261028/balance-tensioner-20261030`): no contact at home or over tilt -38..34 / pan -20..180.
  First contact is at 36 deg camera-down, tray vs yoke, the same as v2.

## Not verified

- Insert OD/length assumed 3.0 x 3.0 (the 2.8 bore is Jim's tested value; stock not measured).
- Snap-bump grip depends on the real board width (CAD assumes 27.2; AI-Thinker is 27.0 +-0.2) and on wall print
  accuracy. They might be loose or tight; that is a physical check.
- Dupont seating and the earlier power/ground drop-outs are a harness issue the case does not fix.
- The v2 mast print set still lists the v2 tray/cover STLs; swap in `stl/Camera_Service_v3_*.stl` if v3 is accepted.

## Files

- `Gladiator_Camera_Service_v3_REVIEW.FCStd` - assembled with head context, inserts, screws, board; `Sections` group
  holds a cut through the SD-side lug (hidden).
- `Gladiator_Camera_Service_v3_EXPLODED.FCStd`, `Gladiator_Camera_Service_v3.step`, `stl/` (print orientation).
- `review_sheet.png`, `exploded.png`, `open_tray.png`, `assembled.png`, `section_lug.png`.
- `build_camera_service_v3.py` (patches `camera-service-v2-20261021/generated-build.py`), `generated-build.py`,
  `check_in_head_v2.py`, `review_sheet.py`.

Rebuild on cad-lab from the repo root:

    xvfb-run -a freecad cad/head/camera-service-v3-20261030/build_camera_service_v3.py
    python3 cad/head/camera-service-v3-20261030/check_in_head_v2.py
    python3 cad/head/camera-service-v3-20261030/review_sheet.py
