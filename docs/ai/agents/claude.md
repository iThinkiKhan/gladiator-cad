# Claude Notes

Claude-owned durable observations and handoff notes.

## Master file conventions worth knowing (2026-09-27)

- Many parts that sit on the upper deck are **not** spreadsheet-driven in Z: `AntennaPost`,
  `DriverMountLeft`, `DriverBoardLeft`, `WireSlotTool`, `DrvFootReliefTool` and the `DrvV5_*`
  group. Since 2026-09-27 their `Placement.Base.z` is bound to
  `rail_top_z - upper_drawn_rail_top` (48), so they follow the rails. Same idea for the imported
  head candidate and `MastIndexFlatTool`, via `mast_top_z - head_drawn_mast_top` (120).
- Rail sketches `RailGroove`, `RailFootWells`, `RailTabs`, `RailMountSlots` and the haunch
  vertices of `RailOuterProfile` carry hard-coded geometry. `scripts/apply_first_build_fixes.py`
  rewrites them; changing `rail_soffit_z` etc. alone will not move them.
- Order matters when lifting the deck: move `WireSlotTool` **before** the first recompute, or
  `WireSlotEase` (edge-indexed chamfer) loses its edge links in between.
- The front-foot screw is driven through the open inboard side of the well; the Ø6 shafts from
  the rail top are blocked by the 2 mm raceway floor.

## Print hand-off location (2026-09-30)

`~/Desktop/3D-Printer-Incoming` is a symlink to `~/3D-Printer/Incoming`, and it now holds one
subfolder per project (e.g. `Petey/`). Gladiator files go in `~/3D-Printer/Incoming/Gladiator/`.
Jim cleared the old plates out of the incoming folder and out of `cad/print-ready/` (those
deletions are his, uncommitted; leave them). OctoPrint prints come off the SD card.

## Uncommitted work found in the master (2026-09-27)

`Gladiator_Master.FCStd` had been modified on 2026-09-21 15:49 and never committed: extra head
carrier envelopes (e.g. `GH44_Camera_Carrier`, `ESP32_CAM_Envelope`) in `HeadCandidate_v01`.
It was preserved and went into the 2026-09-27 build-2 commit along with the rail/mast changes.

## ESP32-CAM case v1 for the head carrier (2026-10-13)

Jim swapped the SEN0610 presence sensor for an AI-Thinker ESP32-CAM and supplied reference/esp32-cam/ESP3-CAM.STEP
(board 27 x 40 x 1.0, lens centre 11.4 from the SD end, SD slot on the lens face at the same end; header pins 9 mm behind).
Built cad/head/esp32-cam-case-v4/ (v1-v3 superseded and removed before printing) (tray + lid, README, validation.json, scripts/build_esp32_cam_case_v4.py): replaces the
radar frame (same three M2 pilots), board portrait SD-end up at x 26.5, 5V/GND Dupont jumpers leave by a notch in the
ToF-side wall toward the carrier cable slot. All overlap, access, FOV and 451-pose sweep checks pass; STLs are queued in
~/3D-Printer/Incoming/Gladiator/. **Not printed.** Verify on the real board: PCB thickness (pads/posts assume 1.0), Dupont housing
length (14 mm modelled), lens offset. HANDOFF.md/SHARED.md were being edited by another agent, so they were left alone.
The case front reaches global Y 18.7 and overhangs the carrier top/bottom by up to 6 mm (tray bottom edge is bevelled so
+25 deg tilt clears the yoke base plate). The enclosure concept (Codex 2026-10-13) models the radar frame, not this case.

Jim calipers on the real ESP32-CAM (2026-10-13): PCB 0.8 (STEP 1.0); PCB + ESP32 module at thickest 6.2 (STEP about 4.6);
PCB + microSD holder 4.4 (STEP 3.2). Camera lens height and barrel size NOT yet measured; Jim says they stick out
considerably more than the STEP. Case v1 lid inner face is 9.6 above the PCB back, so v1 must not be printed
until the lens height is known and the case is rebuilt (PCB_T -> 0.8, lid depth from the real lens).

Update 2026-10-13: Jim clarified his caliper values are all from the bare PCB back: camera square top 6.75 (it rests on the
SD holder, top 4.4), lens tip 9.4, lens a 7 mm circle. v2 uses them: lid inner 7.3, lid face 9.3, lens through a 9 mm hole,
PCB_T 0.8. Case depth is now 34 mm and the lens tip stays 5.5 ahead of the ToF. All checks pass. Still not printed.
Pins soldered / Dupont length remain assumptions (14 mm housing, 9 mm pins, 5 mm bend).

Update 2026-10-13 (independent review): v3 adds an SD finger recess and review probes (shank vs carrier, jumper path, card sweep, 1-degree
tilt sweep); mesh-level booleans and an overhang analysis agree with the CAD checks. Orca plate ORCA-D (tray + lid, no supports,
1 h 45 m, 20 g) built by scripts/build_esp32_cam_orca_plate.py and queued in ~/3D-Printer/Incoming/Gladiator/ with START_HERE_esp32-cam-case.txt.
Not printed. Dupont length / pins soldered / lens offset still unverified on the real board.

## Enclosure v2 lessons (2026-10-13)

- FreeCAD 1.0 `freecadcmd`: booleans on shapes that carry element maps can SEGFAULT or return Null shapes. Round-trip through BREP
  (`Part.Shape().importBrepFromString(s.exportBrepToString())`) after each boolean. A script that raises is re-run once by the host, so its log appears twice.
  `makeOffsetShape(-0.4)` erosion fails on these shells, so there is no thin-wall probe yet.
- Removal sweeps must run at 1 mm steps. A 3 mm sweep passed a roof tab that actually caught on its recess wall for the first millimetre.
- Anything above the upper-deck edge (lips) collides with the S3 bosses and the breadboard when the hood slides back, so the weight rests on skids on the aluminium deck.
- A lap across the flared flank acts as a wedge and locks the panels. Keep laps on flat roof surfaces and make flank seams plain butts.
- The front panels are threaded onto the driver boards by their heatsink apertures: removal is only along the board normal (45 degrees outboard and up), and the head
  neck's left servo arm limits the left panel to about 23 mm on that line. Revisit with the neck design before changing the apertures.
- Evidence and limits: cad/enclosure/v2-20261013/validation.json and removal-sweeps.json.

Update 2026-10-13 (v4): Jim needs all 16 header pins and found the case too deep. He chose straight pins with side slots (not bent pins).
v4: wire slots in both long walls (two per wall, 0.8 mm strut), bend room 5 -> 3 mm (case about 2 mm shallower, ~32 mm deep), 16 wire probes
clear. Depth is dominated by header pin + Dupont housing (14 mm assumed): bending the pins 90 deg outward would save about 14 mm, offered to Jim,
declined for now. Plate ORCA-D v4 (1 h 40 m, 18.9 g, no supports) in ~/3D-Printer/Incoming/Gladiator/. Not printed.
- SMA/antenna mounts (Jim, 2026-10-14): never sink the connector in a pocket. The old pylon's round O11 x 4 pocket could not hold the flange and left no room for fingers or
  a spanner. Use a 2.0 mm flat land, an open flat zone of r11 on both faces, and ribs that start outside it. In FreeCAD, `Shape.rotate(.., Y axis, ang)` carries +X to
  (cos, 0, -sin): check which way a rotated rib points before trusting it (a section plot caught mine pointing up and clipped away).
- Rails/shell build order matters: build_rails_v3.py reads the Codex concept FCStd (untouched source of the chassis references); build_enclosure_v2.py then reads cad/rails/v3-20261014/ for the rails.
  The sweep caught the switch arm (2.5 mm proud of the rail face) blocking the hood's standoffs at 28 mm; keep anything fixed to the frame flush with the rail outer faces.
- Never `pkill -f` a pattern that appears in your own ssh command line; use `pkill -f "[p]attern"`.

## Arch rails lessons (2026-10-15)

- Put the inner faces of a rail pair on one plane (X18 left, X61 right) so the part prints flat on that face and the arch needs no supports; bosses and pads stay on the other side.
- The arch must not cross a socket or insert bore: keep peg sockets on the band centreline (X14) with 2.2 mm side walls, and give inserts a boss rather than cutting the band.
- Rough frame estimates need numpy: it exists on cad-lab (python3) but not in the Windows Python used locally.
- When one script reads another's FCStd (rails -> switch box -> shell), run them in that order; the shell script reads cad/rails/v4-20261015/ and cad/switch-enclosure/v1-20261015/.
- Front-panel anchors: anything fixed to a front panel and reaching the rails crosses the space under the deck and the driver wedge, so it traps the panel on its forced 45 degree pull-out. Anchor the front panels
  to the hood (roof tabs) and keep rail hard points on the hood side, or redesign the apertures first. Always re-run verify_enclosure_v2.py after adding a boss.
- To keep pads from overhanging air, fill the pad box and subtract the space under the arch (the 'void'); that gives a fan above the extrados without ever intruding under the arch.

## Aperture sweeps and glass-bed lessons (2026-10-15)

- A heatsink/board aperture cut as a plain offset of the board outline only works while no shell material lies in the board's path as the panel is pulled along its normal. If a board pierces a roof or shoulder at an angle,
  cut the aperture as the outline swept along -n for the whole pull (build_enclosure_v2.py `sweep`). Moving the boards 5 mm out (20 mm standoffs) exposed this; the sweep found it at 2 mm.
- Parts that print top-up with their underside on the glass cannot carry pegs underneath: put the pegs on the mating part and give the plate through slots with chamfered underside openings.
- The deck v3 is a Boolean edit of the master deck BREP (fill, slot, chamfer): no PartDesign recompute needed, the master is untouched.
