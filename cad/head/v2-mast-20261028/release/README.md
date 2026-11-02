# Masthead v2 - RELEASE (current head)

**This folder is the current masthead.** Built by ONE script: `scripts/build_head_v2_release.py`
(consolidated 2026-11-01 at Jim's request, replacing four patch folders that each modified the last).

    python3 scripts/build_head_v2_release.py          # full build + motion sweep (cad-lab, about 10+ min)
    python3 scripts/build_head_v2_release.py --quick  # skip the motion sweep

Input: the v2 base, `scripts/build_head_v2_mast.py` -> `../Gladiator_Head_v2_Mast.FCStd` (unchanged).
Steps applied in order (each one is proven identical to the folder it replaces, see `validation.json` "steps"):

| step | change | replaces |
|---|---|---|
| 1 | tilt balance (receiver front -2.5 mm, payload 2.5 mm rearward) + M3x20 tensioner | `balance-tensioner-20261030/` |
| 2 | pan-servo lead path: slot under the neck flange, collar tunnel, groove, tube-top notch | `pcb-floor-20261030/` (its yoke PCB pocket was rejected and is NOT applied) |
| 3 | solid tube: rear slot filled, 10 x 12 window at Z 90-102 (bottom window Z 24-36 kept) | `solid-tube-20261101/` |
| 4 | yoke: 45 deg tapers under the plate ledges (joint 30 -> 89 / 18 -> 59 mm2) | `yoke-taper-20261101/` |
| 5 | screen frame v07: the v06 frame + 2 posts on the side-window face, 4 M2 heat-set inserts; Jim's 30 x 70 perfboard screws straight on, uncut, 5 mm off the frame (Jim 2026-11-02) | `side-window-pcb-20261030/` (clamp bars, 30 x 55 board) |

**Future changes: add a step 5, 6 ... to the script. Do not start a new patch folder.**

Outputs:
- `Gladiator_Head_v2_RELEASE.FCStd` / `_assembly.step`: the whole head at its world position.
- `stl/01..08_*.stl`: the 8 print parts in print orientation; `MANIFEST.json` has size, grams, bed chamfers, sha256.
- `validation.json`: step equivalence, home clashes, tensioner travel (C 38-48), tilt -38..34 x pan -20..180 sweep,
  and the two known end stops (receiver at -40, camera tray at +36).

Bed chamfers (0.5 mm on hole edges that print on the bed, Jim 2026-10-15) are applied to all 7 parts. The patch
folders had dropped them on the tube, yoke and receiver. The pulley now gets both bed circles chamfered; the v2
export's chamfer loop had skipped one (-12 mm3).

Not included: camera case (left off this print, drafts in `cad/head/camera-service-v3/v4`). Nothing here has been printed.

## Side board (step 5, 2026-11-02)

- `08_Screen_Frame_v07_SideBoard.stl` replaces the fitted v06 frame (same frame + 5.2 g of posts). Print it bezel face down, as the v06 frame.
- Board: Jim's 30 x 70 perfboard, uncut. It ends level with the screen face and overhangs the camera end of the frame by 8.8 mm.
- Parts go on the inner face, pointing into the head. Solder side out.
- Drill 4 x 2.2 mm (drill out grid holes column 4 and 24 from the camera end, first and last row; 13.4 and 64.2 mm from the camera end,
  3.6 mm from each long edge) and one 6 mm hole 35.3 mm from the camera end, 15 mm up (screwdriver to the tilt horn screw).
  Positions assume the usual 10 x 24 grid centred on the board: check Jim's board before drilling.
- Hardware: 4 x M2 heat-set inserts (bore 2.8 x 4.6, from the board side) + 4 x M2 x 6.
- Checks (validation.json step 5): board + 6 mm outside envelope clear at home and over tilt -38..34 x pan -20..180; screwdriver path clear;
  nothing of the v06 frame cut away. Room for parts on the inner face: `side_board_v07.png` (from `probe_v07.py` in scratch).

