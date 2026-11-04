# Gladiator — Current Status

Last reviewed: 2026-11-04 (Claude)
Status: Masthead V2 pan stack fitted; tilt yoke broke on servo insertion, stronger yoke + carriage (plate E) ready to print
Authority: Project engineering files and Jim's confirmations

## Project

DFRobot Black Gladiator robotic platform with
ESP32-based control, custom CAD, masthead sensors,
camera, and printed structural components.

## Current Design

- Mast is FRONT (+Y); +X is right, +Z is up.
- Current masthead: `cad/head/v2-mast-20261028/release/`, built by ONE script,
  `scripts/build_head_v2_release.py` (steps 1-10). The patch folders are superseded.
  Future head changes are new steps in that script, not new folders.
- Mast tube is SOLID (Jim 2026-11-01): rear lay-in slot removed, wire windows at Z 24-36 and Z 90-102.
  The slotted tube is superseded.
- Head lock: one M3 x 35 bolt + wingnut through collar and mast. Tensioner: M3 x 20.
- Side board: Jim's 40 x 60 perfboard on the screen frame; 08_Screen_Frame_v06_Pockets_40x60 is the
  v06 frame reprinted with 4 M2 heat-set pockets (release step 7).
- Side board pockets (Jim 2026-11-04, on the printed step 7 frame): "the heat set holes are about 1.5mm too far apart. Bring each in by .75", along the 60 mm length.
  Release step 11: 56.0 -> 54.5 mm apart along the board, 36.0 across unchanged. Print file
  `08_Screen_Frame_v06_Pockets_54.5x36.stl` in `~/3D-Printer/Incoming/Gladiator_ScreenFrame_Pockets54.5_20261104/`.
- Camera case is not part of the masthead v2 print set; drafts in `cad/head/camera-service-v3/v4`.
- Servo body openings (Jim 2026-11-04): pan servo carriage (step 8) and tilt yoke ear plate (step 9) are
  12.75 x 23.8 (were 12.0 x 22.8). Tilt yoke ear plate 8 mm thick (step 10, was 3 mm). Print set:
  `~/3D-Printer/Incoming/Gladiator_Masthead_v2_ServoOpenings_20261104/PLATE_E_Carriage_Yoke_Strong.3mf`.

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

## Masthead V2 fit results (Jim, 2026-11-03)

- New rotor assembly fitted on the v2 neck: circlip fits; the pedestal turns freely and is secure.
- Rotor: the damaged v1 Pan_Rotor stays in for now on 3 good screws + the damaged one (Jim: "pretty secure").
  Jim will reprint the rotor later; the reprint should take M2 heat-set inserts (see DECISIONS 2026-11-03).
  The current rotor has no room for them (2.35 pilots at r 18.8, about 1.45 mm wall to the bearing seat,
  1.5 mm to the outside), so the screw circle or rotor diameter must change.
- Pulley: Jim, "The pulley is fine." No change wanted.
- **Collar on the mast stops about 1 mm short of home.** Jim sees an indent from the mast alignment
  flat/key, and the M3 head-lock bolt does not quite pass (collar and tube holes offset by about 1 mm).
  Jim will drill the hole rather than force the collar ("short of taking a hammer to the mast").
  CAD check (Claude): the printed STLs match the CAD. The tube flat runs world Z 111-150 and the collar
  key Z 115-147, so the key cannot bottom out on the end of the flat. The tube top seats against the
  neck's bore ceiling (the spindle base, Z 150), which prints as an unsupported 4 mm overhang ring inside
  the collar (collar on the bed, no support in the bore), so a sagged ceiling or the long 0.10 mm-gap key
  (34 mm long vs 16 mm in v1) rubbing the flat are the likely causes. Not measured. Next print of
  Neck_Main or the tube: give the bore ceiling a 45 deg chamfer or a 1 mm relief, and/or ease the key.
- **Servo horn pockets (pan pulley and tilt receiver): better than v1 but the horn still does not go fully home.**
  Jim: the round hub on top of the horn tapers down into the arms "into a type of a flat pyramid", so it meets
  the pocket before the arms bottom out. Fix (Jim 2026-11-03): taper out the edge of the circular hub recess
  on the interior, servo-facing side, extending the circular pocket along the arms. The roof and the centre
  hole stay exactly as they are: the horn screw must still clamp the part through the roof. Jim is sanding the
  printed pulley and receiver this way. CAD (horn_solid() and the hub recess: a straight 7.1 hub 1.0 above
  flat 2.0 arms, 7.65 x 1.6 recess under a 1.2 roof) gets the same taper at the next revision; the taper
  size is not measured.
- **The hole facing the rear of the tilt servo is the tilt pivot, not a servo screw.** Jim asked whether the
  arm with a hole facing the rear of the installed tilt servo was meant for a screw to hold the servo. CAD:
  behind the servo body (rear at x 14.7) are the GH44_Tilt_Receiver pivot arm (x 24-27, 3.6 hole) and the
  Tilt_Yoke pivot tower (x 28-33). An M3 x 12 bolt goes in from outside the tower, through an M3 nut captive in
  the hex pocket on the tower's inner face; its shank is the axle the receiver turns on, and its tip stops
  about 7 mm short of the servo. The servo is held only by its two ear screws.
- **Servo ear screws get M2 heat-set inserts eventually** (Jim 2026-11-03): Tilt_Yoke ear plate and
  Pan_Servo_Carriage, both now M2 self-tap pilots (2.35). At their next revision, under the fastener rule.

- **Pan servo carriage: the SG90 body only just went in** (Jim 2026-11-04: "I can get this one in. lets go 3/4mm
  wider and at least 1mm longer"). Release step 8: opening 12.0 x 22.8 -> 12.75 x 23.8, centred on the body.
  Read as 0.75 mm (three quarters). The ear pilots keep their place: 0.5 mm wall to the opening (was 1.0).
- **Tilt yoke broke putting the tilt servo in** (Jim 2026-11-04: "The yoke needs to be made bigger too, i just broke
  the yoke trying to get the tilt servo in" ... "Only one of the arms for the servo holding enclosure survived, the
  rest snapped off"). The servo hangs on the 3 mm ear plate alone; the four bars round its opening (sides 3.6 x 3)
  print upright and bend across the layers. Step 9: same 12.75 x 23.8 opening. Step 10: ear plate 8 mm thick (5 mm
  added on the servo-body side; ear face unchanged), 45 deg underside, pilots through; the new material is trimmed
  where the receiver and carrier swing (front edge, tilt -28..-40), so the printed receiver still fits. Front
  edge keeps two small 3 mm notches; everywhere else round the opening is 8 mm. Full build + motion sweep pass.
  Not printed yet.

## Open issues (2026-11-03)

- **RESOLVED 2026-11-03: pedestal did not sit level on the rotor.** Cause: the Pan_Retainer was missing
  (stuck to the v1 pedestal, which made the v1 pocket look 5 mm deep). The pedestal pocket is identical
  in v04, v05 and v2 (r 6.5-13, 2.0 deep). Stack: rotor -> Pan_Retainer (3 mm ring, 29 mm bore) ->
  pedestal, on the same 4 M2 screws; the spindle post top is 3.1 mm above the rotor top, so the retainer
  is required (1.9 mm clearance with it, about 1.1 mm interference without). Jim confirmed the retainer
  was the missing piece; full stack seat and pan rotation not yet reported.
- **Pan_Rotor: one of four M2 holes damaged.** Jim's choice: keep it on 3 good screws for now, reprint later.
- **Collar about 1 mm high on the mast; head-lock bolt hole being drilled by Jim** (see fit results).
- 06_Pan_Drive_Pulley STL is exported upside down by `build_head_v2_release.py` pose() (horn plate up,
  manifest says "horn plate on the bed"); the release checks compare size and volume only. Jim: the printed
  pulley is fine, no change wanted. Fix the pose only if the script is touched for another step.
- `~/3D-Printer/Incoming/Gladiator_Masthead_v2_20261031/START_HERE.txt` still lists the v06 screen frame
  as re-used; step 7 replaced it with the 08 pocket frame. (Its 04 and 07 are now flagged as replaced by plate E.)
- `Part.makeCompound` segfaults on cad-lab as of 2026-11-04 (even 4 plain cylinders; cause not found, no package
  changed). Step 6 now uses `Part.Compound` (same result). Use `Part.Compound` in new scripts.
- The committed release validation (before 2026-11-04) came from a `--quick` build (no motion sweep); the
  2026-11-04 build is a full one.

## Waiting on Jim

- Finish assembling and fit-testing Masthead V2; record physical results (pedestal seat, collar on tube,
  belt tension at C 38-48, wingnut clamp, wire feed through the solid tube).
- After drilling the head-lock hole: report how the collar clamps and whether the head sits square.
- Reprint the rotor (with M2 heat-set pockets) when convenient.
- Optional, for the CAD: how far the hub recess had to be sanded out along the arms.
- Print plate E (carriage + stronger yoke) and report the servo fit in both and whether the yoke holds.
- Next head revision (release step 11 or later, not started): hub recess tapered out along the arms (roof and
  screw hole unchanged), M2 heat-sets for the servo ears (no room now: 0.5 mm wall to the wider openings, so
  that needs a different ear fixing or a measured servo), collar bore-ceiling relief / eased key, heat-set rotor.
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
