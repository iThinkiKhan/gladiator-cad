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
| 5 | screen frame v07: the v06 frame + 2 posts on the side-window face, 4 M2 heat-set inserts; Jim's 30 x 70 perfboard screws straight on, uncut, 5 mm off the frame (Jim 2026-11-02). Superseded by step 6; still runs as the record | `side-window-pcb-20261030/` (clamp bars, 30 x 55 board) |
| 6 | screen frame v08: the v06 frame + a post filling the camera end of the side window + a pad bringing the screen-end post up to the rail face, 4 M2 heat-set inserts; the board is CUT to 30 x 61 and lies flat on the rails (Jim 2026-11-02) | step 5 (v07). Superseded by step 7 |
| 7 | screen frame = v06 + 4 M2 heat-set pockets (2.8 x 4.5) for Jim's 40 x 60 board, centred on the frame, corner holes 2 mm in from each edge; nothing else changes (Jim 2026-11-02) | step 6 (v08) |

**Future changes: add a step 8, 9 ... to the script. Do not start a new patch folder.**

Outputs:
- `Gladiator_Head_v2_RELEASE.FCStd` / `_assembly.step`: the whole head at its world position.
- `stl/01..08_*.stl`: the 8 print parts in print orientation; `MANIFEST.json` has size, grams, bed chamfers, sha256.
- `validation.json`: step equivalence, home clashes, tensioner travel (C 38-48), tilt -38..34 x pan -20..180 sweep,
  and the two known end stops (receiver at -40, camera tray at +36).

Bed chamfers (0.5 mm on hole edges that print on the bed, Jim 2026-10-15) are applied to all 7 parts. The patch
folders had dropped them on the tube, yoke and receiver. The pulley now gets both bed circles chamfered; the v2
export's chamfer loop had skipped one (-12 mm3).

Not included: camera case (left off this print, drafts in `cad/head/camera-service-v3/v4`). Nothing here has been printed.

## Side board (step 7, 2026-11-02) - current

- Jim found a 40 x 60 perfboard that fits the v06 frame as it is: centred on the frame, flat on the -X rail face, solder side
  out. Its factory corner holes are 2.0 mm in from each edge (Jim's measurement). Pressing inserts into the printed frame
  without pockets filled them with plastic, so `08_Screen_Frame_v06_Pockets_40x60.stl` is the v06 frame reprinted with 4 M2 heat-set pockets under those holes.
- Pockets: dia 2.8 x 4.5 deep (insert 4 + 0.5 for the plastic it pushes ahead), 2.6 and
  58.6 mm from the camera end of the frame, 4.0 mm in from its top
  and bottom. Thinnest wall 1.2 mm (camera end). Print bezel face down, no support. Test slice on Jim's presets: 2 h 07 m,
  22.6 g, safety check passed. Picture: `screen_frame_v06_pockets.png`.
- Hardware: 4 x M2 heat-set inserts + 4 x M2 x 5 (or M2 x 6).
- The board covers the side window, so reaching the tilt horn screw needs the board off (4 screws) or a 6 mm hole in the board
  on the tilt axis (halfway up the board, 25.9 mm from its camera end).
- validation.json for this build came from `--quick` (Jim: no extra checks; he has the board on the frame). The motion sweep
  was not rerun; the 40 x 60 board was checked clear of tilt -38..34 x pan -20..180 by `probe_4060.py` in cad-lab scratch.
- Steps 5 (v07) and 6 (v08) still run in the script as the record; their STLs and pictures are in `superseded_step5_v07/` and
  `superseded_step6_v08/`.

## Side board (step 6, 2026-11-02) - superseded by step 7

- `08_Screen_Frame_v08_CutBoard.stl` replaces the fitted v06 frame (v06 + 2.03 g: a post filling the camera end of
  the side window, and a pad bringing the screen-end post up to the rail face; v06 had it 1.5 mm below). Print bezel face down,
  no support: the new post bridges 24 mm between the rails. Test slice on Jim's presets: 2 h 10 m, 24 g, safety check passed.
- Board: Jim's 30 x 70 perfboard cut to 30 x 61.0 (9 mm off one end: score through hole column 2, snap, sand; never longer).
  Factory edge at the screen end, flush with the screen face; the cut end stops 0.2 mm short of the frame end, so nothing is
  over the camera carrier or the ToF. It lies flat on the rails, no standoff.
- Parts go on the inner face, into the head. Solder side out. 17 free columns (6-22, counted on the uncut board). Rows 1-3 and
  8-10: 17-30 mm of room; rows 4-7: 11.5-17 mm (tilt receiver behind). Rows 1 and 10 sit at the rail edge: pins and wires only.
- Drill 4 x 2.2 mm: grid holes in the 2nd column from the cut end and the 1st column from the factory end (4.4 and 55.2 mm from
  the cut end), 2nd row in from each long edge (6.1 and 23.9 mm from the bottom edge). Rows 2 and 9 keep the screen-end holes
  clear of the factory corner holes. One 6 mm hole 26.3 mm from the cut end, 15 mm up (screwdriver to the tilt horn screw).
  Positions assume the usual 10 x 24 grid centred on the board: check Jim's board before drilling.
- Hardware: 4 x M2 heat-set inserts (bore 2.8 x 4.5, from the board side, 1.0 mm floor behind) + 4 x M2 x 6.
- Checks (validation.json step 6): board + 6 mm outside envelope clear at home and over tilt -38..34 x pan -20..180; screwdriver
  path clear; only the insert bores cut into v06 material; 1.5 mm wall round every insert. Picture: `side_board_v08.png`
  (from `probe_v08.py` / `draw_v08.py` in cad-lab scratch).
- Not verified: nothing printed. Why v06 had its screen-end post 1.5 mm below the rail face is not known; nothing in the CAD uses
  that space.
- Step 5 (v07: uncut board on 5 mm posts) still runs in the script as the record. Its STL and picture are in
  `superseded_step5_v07/`. A v07 that is already printed still works with an uncut board.
