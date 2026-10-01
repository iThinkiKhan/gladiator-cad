# Current Handoff

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
- **INA226 cassette v1 built 2026-10-01** (`cad/power-board/ina-cassette-v1/`, `scripts/build_ina_cassette_v1.py`, not printed). Removable
  shelf that hangs on the tray front wall (lip over the wall, tongue under the floor, bumps), board front-to-back, header pins out
  the front, terminals at the rear, wings between the rail front posts. **Hole centres (2.0 from header edge and sides) are
  INFERRED from Jim's description, not calipered.** Pin tail 2.2 is derived. Board overhangs the deck front by 8.2.
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
