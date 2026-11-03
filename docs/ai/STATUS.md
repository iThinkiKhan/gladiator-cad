# Gladiator — Current Status

Last reviewed: 2026-11-03 (Claude)
Status: Masthead V2 printed in part; physical assembly and fit test in progress
Authority: Project engineering files and Jim's confirmations

## Project

DFRobot Black Gladiator robotic platform with
ESP32-based control, custom CAD, masthead sensors,
camera, and printed structural components.

## Current Design

- Mast is FRONT (+Y); +X is right, +Z is up.
- Current masthead: `cad/head/v2-mast-20261028/release/`, built by ONE script,
  `scripts/build_head_v2_release.py` (steps 1-7). The patch folders are superseded.
  Future head changes are new steps in that script, not new folders.
- Mast tube is SOLID (Jim 2026-11-01): rear lay-in slot removed, wire windows at Z 24-36 and Z 90-102.
  The slotted tube is superseded.
- Head lock: one M3 x 35 bolt + wingnut through collar and mast. Tensioner: M3 x 20.
- Side board: Jim's 40 x 60 perfboard on the screen frame; 08_Screen_Frame_v06_Pockets_40x60 is the
  v06 frame reprinted with 4 M2 heat-set pockets (release step 7).
- Camera case is not part of the masthead v2 print set; drafts in `cad/head/camera-service-v3/v4`.

## Masthead V2 as built (Jim, 2026-11-03)

- The v1 head is disassembled. Parts on hand for reuse, in Jim's words: "the rotor, spindle,
  c clip, carrier board, ToF holder", plus "the new v2 cam case".
  Which camera case revision that is (camera-service-v2 tray/cover or v4) is not confirmed.
- Re-use list in the release (do not reprint): Pan_Rotor, Pan_Retainer, GH44_Dual_Carrier,
  ToF_Sensor_Frame. All four are on hand (retainer recovered, rotor damaged; see below).
- In every CAD version (v04, v05, v2) the spindle post is part of Neck_Main; there is no separate
  spindle part. Jim (2026-11-03): the separate "spindle" is the v1 neck's post, broken clean off.
  It is not re-used; the v2 Neck_Main carries its own post (20.05, circlip groove).
- Pan_Retainer recovered (Jim 2026-11-03): it was stuck to the underside of the v1 pedestal and was
  the missing piece under the new pedestal.
- Pan_Rotor is damaged (Jim 2026-11-03): one of its four M2 holes is compromised; Jim believes it is
  still usable. The holes are 2.35 self-tap pilots at r 18.8, about 1.45 mm of wall to the bearing seat
  and 1.5 mm to the outside, so a heat-set insert (2.8 bore) does not fit there. Options: run on three
  screws, CA-glue and re-drive the stripped hole, or reprint the unchanged v05 Pan_Rotor STL.

## Open issues (2026-11-03)

- **RESOLVED 2026-11-03: pedestal did not sit level on the rotor.** Cause: the Pan_Retainer was missing
  (stuck to the v1 pedestal, which made the v1 pocket look 5 mm deep). The pedestal pocket is identical
  in v04, v05 and v2 (r 6.5-13, 2.0 deep). Stack: rotor -> Pan_Retainer (3 mm ring, 29 mm bore) ->
  pedestal, on the same 4 M2 screws; the spindle post top is 3.1 mm above the rotor top, so the retainer
  is required (1.9 mm clearance with it, about 1.1 mm interference without). Jim confirmed the retainer
  was the missing piece; full stack seat and pan rotation not yet reported.
- **Pan_Rotor: one of four M2 holes damaged** (see above). Decide 3 screws / repair / reprint.
- **06_Pan_Drive_Pulley STL is exported upside down.** `build_head_v2_release.py` pose() rotates the
  pulley 180 deg about X, so the release STL and Plate B have the horn plate on top (manifest says
  "horn plate on the bed"). The pre-release v2 STL is correct. The release checks compare size and
  volume only, so they miss a flip. Geometry is unchanged (cup 9.1 deep, horn pocket 2.2, plate 5.0):
  fit the printed part horn-pocket side down on the servo horn. Not fixed; Jim to decide.
- `~/3D-Printer/Incoming/Gladiator_Masthead_v2_20261031/START_HERE.txt` still lists the v06 screen frame
  as re-used; step 7 replaced it with the 08 pocket frame.

## Waiting on Jim

- Finish assembling and fit-testing Masthead V2; record physical results (pedestal seat, collar on tube,
  belt tension at C 38-48, wingnut clamp, wire feed through the solid tube).
- Report how the pan stack seats and turns with the retainer fitted and the damaged rotor hole.
- Decide whether to fix the pulley export orientation.
- Print and evaluate camera case v4 and its three clip variants when ready.
- Camera flash LED firmware (CAM masthead-1.3.0 / C6 gateway-2.4.10) built on the PC, not flashed.

## Printer Safety

Printer: Ender-3 Neo with Pro hotend and
Sprite direct-drive extruder. Authoritative rules: `docs/safety/PRINTER.md`.

Jim slices delivered models using his own presets.
Do not use legacy generated G-code.
Hand-offs go to cad-lab `~/3D-Printer/Incoming/<Project>_<Batch>_<date>/` (one folder per batch).

## Sources

- docs/ORIENTATION.md
- docs/GLADIATOR_DESIGN.md
- cad/head/v2-mast-20261028/release/README.md and MANIFEST.json
- docs/ai/DECISIONS.md
- docs/ai/HISTORY.md
- measurements/printer-calibration.md

## Agent Instructions

Read this file first for project status.
Consult engineering documentation for technical details.
Verify live hardware state before claiming operation.
Update this file after meaningful project changes.
