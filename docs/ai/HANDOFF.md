# Current Handoff

## Power tray v5 + INA226 cassette v2 — 2026-10-03 (Claude)

Jim printed v4 and the v1 cassette and found: the click bumps and 0.25-clearance pegs were far too tight (nothing came out and the thin
1.0 front wall tore off the tray), the tray walls were far too weak, and the cassette's pressure fit would not work (it needs a lip over the
INSIDE of the wall). Rebuilt as new versions; v4 and v1 are kept as the record of what was printed.
- **Tray v5** (`cad/power-board/v5-tray/`, `scripts/build_power_tray_v5.py`, 52 checks): no bumps or grooves anywhere (plain wells, same 0.25
  clearance Jim said fitted well before the click); front and rear walls 2.4, floor 2.4 (grown downward, board height unchanged), 2 x 2 root
  gussets, 2.5 corner blocks, post-to-wall webs. Side walls stay 1.0 (0.1 inside the rails). v4 bases still fit; v5 bases are the same without grooves.
  **Arms back to the v3 design** (no scoop) after Jim said the new arm did not clear the mast; v3/v4/first-v5 arms were all exactly 0.40 from the
  tube (so the design was not the difference). Inner face opened 0.8, gap now 1.2. Ask Jim where it actually touched if it still does.
- **Cassette v2** (`cad/power-board/ina-cassette-v2/`, `scripts/build_ina_cassette_v2.py`, 28 checks): plate + lip + two toes down the inside of the
  wall; drops on from above; no tongue, no bumps, every gap 0.3. Needs supports (build plate only) for the lip and toes. Board now overhangs the deck
  front by 14.0 (pin tips 21.0) because the wall is thicker.
- Not printed. STLs are queued in `~/3D-Printer/Incoming/Gladiator/`; Jim starts prints. The old v4/v1 STLs are still in that folder, untouched.
- Still inferred: INA hole centres (2.0 from the header edge and sides), pin tails 3.0 read as below the PCB.

## Head coupons round 3 — 2026-10-01 (Claude)

Jim asked whether there were more coupons. Built `cad/head/coupons-r3-20261001/` (commit 126fbfd, in the
incoming folder, not printed). R3a is a screen slice: the real ST7789 in the frame's pocket and window,
with the assumed hole offset. R3b is M3 nuts in 6.0 pockets printed sideways. R3c is the GH44 recess
printed face down. Also asked for, needing no print: circlip on the H3b-2 post, horn screw head on the
H6a hole, and the horn height reading for the neck.

## Head v0.4 released for printing, except the neck — 2026-10-01 (Claude)

- **Coupon results** (Jim): H3b 2-notch post (**20.05**); H6 1-notch snug pocket (**0.15**); H4b midway
  between 1 and 2 (**M2 pilot 2.35**). The generator was rebuilt with them. Only the rotor, carriage,
  yoke and display frame changed; 0 collisions.
- **Released plates**, in `cad/head/v04-pan-stack/plates/` and the printer incoming folder. None has
  been printed.
  - Plate 1: pedestal, retainer, clamp cap. Unchanged.
  - Plate 2: rotor, drive pulley, servo carriage. About 32 g, no supports.
  - Plate 3: tilt yoke, GH44 receiver, display frame. About 48 g, supports under the frame tabs.
  - Generator: `scripts/build_head_v04_plates.py`.
- **Held:**
  - **Neck_Main** waits on one reading: horn pushed fully on, ear underside to the top of the horn
    arms. The model assumes 13.25. It sets the servo pad height and so the belt alignment. The neck
    also waits on whether the circlip seated on the winning post (not reported).
  - **GH44_Dual_Carrier** waits until the sensor mounting is designed.

## Head v0.4 stage 1, the pan stack — 2026-10-01 (Claude)

Built and validated, **not printed, not released**: `cad/head/v04-pan-stack/` (README there is the
detail), generator `scripts/build_head_v04.py`, plate generator `scripts/build_head_v04_plate1.py`.
Jim said "Start building head v0.4" while printing the final coupon plate.

- 60T on the servo / 40T on the head, **servo on a sliding carriage** (37.0-40.4, nominal 39.75),
  **horn plate** in the drive pulley for the real cross horn. Re-based on the Z130 mast and checked
  against the **current master** (19 robot solids): 0 collisions in 13,432 + 56,088 + 8,360 poses,
  0 ToF intersections, cable bore clear. The first run found 154 collisions, all my modelling
  errors (a mirrored servo, a circlip cutting its groove). Fixed.
- Service paths checked, not just overlap: all three screw groups reachable at **pan 60** and 120-150.
  The belt clamp screws moved outboard of the pulley because the first layout put them under it.
- **Plate 1** (`plates/Gladiator_Head_v04_PLATE1_Pedestal-Retainer-Cap.3mf`, 27 g) needs no coupon
  result. Placed in `~/3D-Printer/Incoming/Gladiator/` with a START_HERE sheet. The other four
  parts are in `stl/` only and are deliberately **not** in the printer folder.
- **Placeholders until the final coupon plate is read:** post 20.05 (H3b), M2 pilot 2.2 (H4b), horn
  pocket clearance 0.15 (H6). **ASSUMED:** horn arm thickness 2.0 and boss-to-horn gap 0.25. They set
  the servo height and so the belt alignment. Leave room to shim on the first assembly.
- **Stage 2 done the same day** (Jim: "keep designing, I'll give you coupon results soon"). The tilt
  yoke, GH44 receiver, dual carrier and display frame are regenerated from code. They have the
  calibrated holes and 6.0 nut pockets, the tested register, a horn-plate tilt drive with axis
  access, an M3 pivot bolt with a captive nut (no bushing), and the real screen window at 6.2 / 1.5.
  Still 0 collisions, 0 ToF. All 11 parts are in `stl/`, none released. The yoke and display frame
  wait on H4b; the receiver waits on H6.
- **Assembly-order facts the checks found:** bolt the yoke to the pedestal before the tilt servo and
  receiver; fit the GH44 carrier before the sensors; put the screen in its frame before the frame goes on.
- **Still not designed:** sensor mounting on the carrier (ToF and radar holes not measured) and the
  cable harness.
- The master's imported `HeadCandidate_v01` is still the old v0.1. Untouched.
- Ask before starting any print.

## Power tray v4 + snap-in base — 2026-10-01 (Claude)

Jim wants a tool-free battery change. v3 tray kept, but it now plugs into two bolt-once rear bases
(`cad/power-board/v4-tray/`, `scripts/build_power_tray_v4.py`). Built and validated on solids, **not printed**.
STLs are in `~/3D-Printer/Incoming/Gladiator/` (tray, BaseLeft/Right, a fit coupon). Ask before any print.

- Cells: Jim says installed cells are negligibly over the rim. Master battery_cell_protrusion corrected 4 -> 0.5 (stand-in) and committed (e289c8e). Floor Z 24.7, about 2.7 clear.
- Base bolts are now M3 (hole 3.4, d6 head). Sockets moved 0.6 inboard to clear the head.
- Board posts 7 -> 4.5 (Jim picked this over 5.5). Board is 4.3 lower than v3. His own "trim 4, do 3 to be safe"
  would be posts about 5.8; one constant (`STANDOFF_H`).
- Rear pegs 3.0 x 8.1 (were 4 x 9.1) in 0.25-clearance sockets, click bump 0.5.
- **2026-10-01 later, strengthening pass (Jim: arms overbuilt, tabs fragile):** arms scooped to 9 deep between Y 104.5 and 123
  (tray 16.56 -> 15.62 cm3); base walls thicker (inboard 2.4, rear 2.0), tab runs past the walls with root fillets, rib on the
  bolt-side wall behind the bump groove (the groove had left 0.65), peg root fillet. "Tabs" was read as the base tab/socket and peg
  root; ask if he meant something else.
- **INA226 cassette v1 built 2026-10-01, ready to print** (`cad/power-board/ina-cassette-v1/`, `scripts/build_ina_cassette_v1.py`, STL queued in
  `~/3D-Printer/Incoming/Gladiator/`, **not printed; Jim starts it**). Removable shelf that hangs on the tray front wall (lip over the wall,
  tongue under the floor, bumps), board front-to-back, header pins out the front, terminals at the rear, wings between the rail front
  posts. Jim chose a **10 mm wire gap** behind the terminals (6 was too tight for wire bends): board overhangs the deck front by 12.2,
  pin tips 19.2. Posts 4 tall; Jim measured about 3 mm pin tails (read as below the PCB). **Hole centres (2.0 from header edge and
  sides) are INFERRED**, not calipered. Fit is 0.1 mm gaps and can only be tried on the printed tray.
- Considered and dropped: hanging the board from the upper deck (Jim: keep the current board design for v1).

## Head round-2 coupons — 2026-09-30 (Claude)

Jim is done printing the body and wants the head right and ready to print. The mast is the
**printed v2 tube, top Z 130**; buying a tube is dropped (see DECISIONS.md).

- Five one-question coupons (nine pieces) are built and placed in
  `~/3D-Printer/Incoming/Gladiator/`: H1 belt centre distance (60T + 40T printed, slotted bar),
  H2 neck collar on the real mast (two key gaps plus a cap), H3 circlip post, H4 M2 pilots, and
  H5 M3 nut sockets.
- Source: `scripts/build_head_coupons_r2.py`. Test steps, what to report, and the six
  measurements still missing are in `cad/head/coupons-r2-20260930/README.md`. That README also
  tables what is already recorded.
- **Measurements are split across files.** The ST7789 hole pattern (26.00 x 58.25, confirmed)
  and visible area (51.2 x 25.6) are in `measurements/components.md` under Display, not in
  mast-head.md. Grep every measurement file before asking Jim for a number.
- Codex's 09-21/22 additions to `measurements/mast-head.md` are still **uncommitted** (Claude
  added a screen cross-reference there too).
- **2026-10-01:** Jim is printing the first nine (the 9-piece plate). **H6a/H6b** (horn pocket)
  were added afterwards as separate STLs in the same incoming folder, not on that plate. They are
  built from Jim's cross-horn calipers (36 / 19 long/short tip to tip, arms 6.8-4.8 and 3.8, hub
  7.1, boss about 1 proud). Arm thickness is not given; pocket depth 1.2 is an assumption.
- **SG90 numbers, Jim 2026-10-01 (measured):** spline top 32, case boss top 28.5, ear underside
  17.5, body length 22.7 (ears not counted). So a seated horn underside is about 11.0-11.5 above the
  ear underside. The old 13.2 and the old 8.3 shaft offset are **superseded** (shaft centre about
  5.9 +-0.6). v0.3 modelled the servo too short and put the horn about 1.5 high. Rebuild v0.4 from
  these.
- Fixed a mistake in the H6 README: the horn goes in **boss-down**, not boss-up.
- **2026-10-01, later:** the first nine coupons are printed and tested (results in
  `measurements/mast-head.md` and DECISIONS.md). The **final coupon plate** is built:
  `cad/head/coupons-r2-20260930/Gladiator_HeadR2_FINAL-COUPON-PLATE_6-pieces.3mf` (H3b x3 bearing
  posts 19.95/20.05/20.15, H4b M2 pilots, H6a/H6b horn pockets; 12.1 cm3). H6 now has a 3.4 centre
  hole so the horn screw's head holds the plate. Placed in the printer incoming folder, not printed.
  **Next: build head v0.4** from the settled inputs in DECISIONS.md, while Jim prints the plate.
  Three results are still pending (H3b post size, H4b pilot size, H6 horn pocket).
- A 40 mm round flange printed only 0.04 small, so the 0.25 calibration may depend on radius. Not
  proven. Nothing in the master has changed.
- Ask before starting any print.

**Next:**
1. Read the coupon results and measurements.
2. Round 3: the horn-to-pulley adapter and the screen frame, which need the horn and screen
   numbers first.
3. Then v0.4. Its direction is 60T on the servo and 40T on the head, with a tension slot on the
   servo carriage and calibrated holes. The bearing fit is 32.35 / 20.20 with a bed-relief
   counterbore.
4. Also in v0.4: a replacement for the M2 self-tap pilots (there are no self-tappers), and a
   removal-path check for the clamp cap against the C arm.

The 60T horn-slot coupon in `cad/head/drive-coupons-20260922/` is **not** in this batch. Its
6.0 channel rubs a 6 mm belt, and its top flange is an unsupported 1.2 overhang.

## Heights changed in the master — 2026-09-27 (Claude)

After Jim's first physical build: rails +6.5 (rail top / upper deck underside **Z 54.5**, was 48),
**mast top Z 130** (was 120). Deck rear pilots corrected to X 17.8 / 61.2 (both rows, per Jim),
and the mast base holes follow them by formula. The Y 128 pilots are now under the rail feet;
power board tray v3 (`cad/power-board/v3-cradle/`) drops them and uses the rear slit bolts only.
The master's `PowerShield` body is legacy (superseded by the tray) and overlaps it. Installed cells
stand 4 above the holder (`BatteryCells` reference). The imported `HeadCandidate_v01`
parts and the mast index flat were moved +10 with the mast top (placement expressions on
`mast_top_z - head_drawn_mast_top`). Anything in `cad/head/` that assumes mast top 120 or deck
top 52 needs re-basing, and the ToF-over-S3 sightline should be re-run (the S3 rose 6.5 too).
Parts awaiting Jim's print decision: `cad/build2-20260927/`. Open measurement requests:
`measurements/chassis.md`, "First-build fit observations".

Use this file for active unfinished work, blockers, and the next useful action.

Do not use it as permanent history; move durable facts or decisions to the
appropriate engineering documentation or DECISIONS.md.

No cross-agent handoff has been recorded yet.

## Head preprint blocker — 2026-09-22

See docs/ai/agents/codex-head-preprint-20260922.md. The v0.3 40T drive / 60T driven belt ratio is inverted in code: 200 degrees head travel needs 300 degrees servo travel, beyond the measured 160 degrees. The fixed belt center distance also has a 0.512 mm pitch-path mismatch. Keep full moving-head STLs out of the print queue; the 3-up belt mesh coupon remains useful. Rebuild a corrected candidate after the belt and drive hardware are checked.

### Update — 2026-09-22

Jim confirmed the delivered belt fits the two-notch mesh coupon (0.65 mm groove radius). He has bearings, circlips, and belts, but no timing pulleys. The printed tooth-profile gate is closed. The next candidate can choose pulley tooth counts freely; do not merely swap 60T/40T in v0.3 because the 40T driven grooves would overlap the inherited pedestal waist and the 60T drive needs a checked SG90 horn interface and side clearance. Horn details are pending from Jim.

Jim clarified that single-arm and cross SG90 horns are available and the shaft-to-long-tip dimension was already recorded as 17 mm. Prefer exploring a cross-horn printed-pulley coupon with radial slots; do not infer screw-hole spacing from the 17 mm tip measurement. The v0.3 9 mm round horn reference is not a faithful model of the available horns.

### 60T horn fit coupon — 2026-09-22

Jim reports five holes in each arm of the cross horn. An isolated 60T printed drive-pulley coupon was generated at cad/head/drive-coupons-20260922/ with radial M2 slots covering 7–14 mm center radius, the accepted two-notch GT2 groove, and a 5.5 mm center-screw access hole. Saved CAD, STEP, STL, preview, README, and validation are present; the STL is one solid, 40.09 x 40.09 x 7.4 mm, with ~1145 mm2 bed contact. This is an unpowered horn/belt fit piece, not a full-drive release. Source: scripts/build_head_drive_coupon.py. Await physical horn-hole/screw/clearance check before integrating it into a corrected head candidate.
