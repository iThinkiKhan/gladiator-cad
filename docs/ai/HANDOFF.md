# Current Handoff

## CURRENT: shell back to 0.28 mm layers - 2026-10-23 (Claude)

Jim asked for a thicker layer to cut time. Hood 9h39, panels 7h24 at 0.28 (first layer 0.25), normal snug 45 deg supports, M600 x3 each (GREY 12.29, RED 56.25/52.33, GREY 62.13/58.21). 0 unsupported cells, 0 fastener-path hits, SAFE pass. Files: X:/3D Printer and Incoming GLAD_FINAL_20261022; 0.20 mm shell files superseded. Script: jim-settings-reslice/source/slice_028.py.

## CURRENT: final print set, M600, emblem cradle - 2026-10-22 evening (Claude)

Supersedes the GLAD_*_JIMSET files below. Final set in X:/3D Printer (and cad-lab ~/3D-Printer/Incoming/Gladiator/GLAD_FINAL_20261022), each with a G-code-drawn .png:
1 white emblems on cradle 46m, 2 silk 20m, 3 black clamps 26m, 4 hood 12h13 (M600 x3), 5 front panels 8h55 (M600 x3).
- White emblems kept balling up even on Jim's own GUI slice: the arch stands on two 0.5 mm edge lines and the lattice hangs over sparse tree tips. Fix: printed cradle (emblem-v2/build_cradle.py) filling the arch, 0.2 mm radial gap, 0.4 mm clear of edges; supports off. Emblem geometry unchanged.
- Colour changes converted from the R5 M0 two-click blocks to `M600 X5 Y200 Z10` after `;_SET_FAN_SPEED_CHANGING_LAYER` of the first new-colour layer (to_m600.py; diff = inserted lines only).
- Hood/panels: Jim's tree supports left the top of a 40 mm window in each panel side wall unsupported and put a branch through the SMA hole. Using normal(auto) + snug + 45 deg threshold (Codex's validated combo) with all other Jim values: 0 unsupported model cells, 0 hits on 24 fastener paths.
- Full config of std jobs equals Jim's GUI export display2.gcode except supports. Scripts: jim-settings-reslice/source (undercheck.py, render_plate.py, wallview.py, supcheck.py, to_m600.py, slice_normal.py, slice_cradle.py).

## CURRENT: print files re-sliced on Jim's own Orca presets - 2026-10-22 (Claude)

Jim: "there is something wrong with the gcode, it keeps failing. Make sure you are using my settings." Root cause: all Round 5 G-code (GLAD_01..05) was sliced from hand-edited project settings, not Jim's presets: 0.20 first layer instead of his 0.25 "FIrst Layer Comp" on the small jobs, 0.12/0.16/0.28 layers, slower walls, normal/snug supports, post_process (SAFE guard) blank. **Do not print or reuse those settings.**

Re-sliced all five jobs (same geometry, positions, support blockers, SD colour targets) with his flattened presets written into each 3MF: EnderNeo SAFE + `0.20mm Standard - FIrst Layer Comp` (silk: `0.20mm Silk Toys @ First Print - SAFE`) + `Generic PLA @System - First Print` (silk: `Generic PLA Silk @System - First Print`). Only deviation: supports on (his tree(auto) values) where needed. Flattening validated against Jim's own GUI export (`~/Desktop/3D-Printer-Outgoing/display2.gcode`): executed start/end code line-identical.

Checks: SAFE guard pass x5; all moves inside 220 bed; 6 SD pauses replayed, state restored exactly, park 5 mm above print; fastener-path support check (Codex's 22 hood + 2 panel paths, control reproduces Codex's zero hits on the old files): all clear except tree branch through the 7 mm SMA antenna hole - clear by hand after printing. Times: emblems 47m, silk 20m, clamps 26m, hood 12h22 (pauses ~3h25/8h44/9h12), panels 6h22 (~2h22/4h23/4h40).

Delivered: X:/3D Printer/GLAD_0*_JIMSET.gcode + GLAD_START_HERE.txt (old files moved to GLAD_OLD_not_Jim_settings_20261022; GLAD_OPTIONAL is old settings). cad-lab ~/3D-Printer/Incoming/Gladiator/GLAD_JIM_SETTINGS_20261022/ (CURRENT_PRINTS.txt updated). Repo: cad/v2/enclosure/round5-print-20261022/jim-settings-reslice/ (scripts jimflat.py, jimslice.py, audit2.py, supcheck.py, pausecheck.py; 3MFs; reports). Orca CLI notes: CLI refuses post_process (-19), user presets lack `type` (-5), and --load-settings with inherited user presets fails compatibility (-17) - write flattened settings into the 3MF instead. No print started.

## CURRENT: mount-checked hood/CAD - 2026-10-22 (Codex)

Hood corrected and delivered:two legacy speaker pilots now2.8mm M2 pockets;use M2x6,fit with hood OFF. Six local3.6mm reliefs follow actual rail splay;use6xM3x20 (25mm bottoms). Antenna nut/tool access passes;all22 checked fastener paths support-clear. New native/STEP22/STL and Neo SAFE/SD replay checks pass. Current source cad/v2/enclosure/round5-calibrated-28-20261022/mount-checked-release/DELIVERY;Incoming Round5_MOUNT_CHECKED_20261022;Windows mount-checked-release-20261022. Same main hood filename replaced in X:/3D Printer,old archived. Hood9h39m04;combined panels unchanged7h00m34,total16h39m38 plus handling. See agent note and release START_HERE. No printer started or physical fit newly claimed. Older hood/current-CAD entries below superseded.


## CURRENT: combined panels, faster supports - 2026-10-22 (Codex)

Jim keeps both panels on one plate; single-panel plan below is optional. Support-only optimization: combined panels **7h00m34s**, hood unchanged **9h43m33s**, total **16h44m07s**, saving **1h30m46s**. Actual printed shell centerlines/material, geometry,4walls,30%infill,roof layers,2.8mm bores,Neo SAFE retained; SAFE/bounds/support/pause checks pass and preview inspected. Current source/package: `cad/v2/enclosure/round5-calibrated-28-20261022/shell-time-optimized/`. Incoming `Round5_COMBINED_SHELLS_20261022/`; main G-code names unchanged in X:/3D Printer. Native CAD remains the calibrated release. Remaining accessories ~2h06; full shell day planned tomorrow. No printer started.


## Five-hour print window: individual front panels - 2026-10-22 (Codex)

Left front panel separated and verified at **4h11m13s**, right at **4h15m**. Both retain 2.8 mm bores/Neo SAFE/SD RED→GREY→RED→GREY. New G-code is in X:/3D Printer; combined plate moved to GLAD_OPTIONAL. Start left with the loaded red for today's five-hour window. Source/provenance: `cad/v2/enclosure/round5-calibrated-28-20261022/single-panels-5h/`; details in the calibrated-release agent note. Neither panel marked printed; no printer started.


## Current: 2.8 mm M2 coupon accepted - 2026-10-22 (Codex)

Jim accepted **2.8 mm** from his M2 heat-set coupon; the previous pending-bore entries below are superseded. Applying it in an isolated production derivative at `cad/v2/enclosure/round5-calibrated-28-20261022/`. CAD/slicing checks PASS; released shell SD pause states also PASS. Current Incoming is `Round5_CALIBRATED_M2_28_20261022/`; five G-code files delivered directly to `X:/3D Printer`, with new native/STEP/22STLs and 3MFs in the calibrated package. The insert-bore blocker is cleared. Stronger white inset v2 replaces plate 04 and needs reprinting; silk remains. Tablets/red shields/crest completed. LED window stays open. No LCD test required. See agents/codex-round5-calibrated-28-20261022.md.


## Stronger white shield emblems (plate 04B) - 2026-10-22 (Claude)

Jim: both printed Round 5 white shield insets failed; need stronger, same fit in the printed red shields. `cad/v2/enclosure/round5-print-20261022/emblem-v2/`: 1.8 mm thick (was 1.0), recess-filling base (0.05/side) plus a wider top layer on the red surface (bolts 1.75, feathers 2.25), printed lying on the back with snug supports. Zero overlap with field/panel; boss rides 0.8 higher, M2 x 6 unchanged. Plate 04B 58 m / 4.2 g, SAFE guard passed; copied to Incoming Round5_SD_20261022/PRINT_FIRST and X: package, old 04 G-code renamed .superseded (SHA256SUMS in the package now out of date for that file).

## Independent check of the Round 5 print release - 2026-10-22 (Claude)

Read-only review of `cad/v2/enclosure/round5-print-20261022/` before the event prints. Round 5 baseline-v28 files are byte-identical to the final v2.8 shell. Fuzzy-Boolean containment: R5 Rear_Hood, Front_Right and Lens_Plate contain the v2.8 parts exactly (0 mm3 missing); Front_Left Boolean fails in OCC but equals the mirrored R5 Front_Right within 28 mm3; panel additions are only the 1521 mm3 shield seats on the front faces. Badges (tablets, letters, aquila, shields) clear every robot/head reference (nearest 8.7 mm). Removal sweeps re-run with shells + badges as one body: hood back 150 mm, right panel 120 mm, left panel 20 mm leg with 3 mm slack: unchanged. Hood/panel SD G-code: extrusions within 220 x 220, PLA 200/60, SAFE start, 6 M0 each. Gate unchanged: M2 bore (CFG insert_bore 3.6 in round5-20261021/build_round5.py) awaits the D3 L3 coupon result. Work files: ~/scratch_claude/r5check/.

## 2026-10-22 — Round5 SD print preparation; hardware fit still pending

Jim confirmed SD card, EnderNeo SAFE and his separate silk settings. New production derivative/plates: `cad/v2/enclosure/round5-print-20261022/`. Read `docs/ai/agents/codex-round5-print-20261022.md` and generated `SD_PACKAGE/START_HERE.md`. Full presets retained; all22parts included, SAFE/bed/support checks pass. Reinforced ONLY the new crest clamp, with51pose yoke-clearance check; old v2.8 and styling native unchanged. Roughly25h printing (shells18h13m), excluding colour-stop waiting and assembly.

**Latest calibration choice:** shared coupon note identifies nominal M2 D3 L3 listing data; Jim selected the four-hole mini. This package uses that geometry with full SAFE settings (10m33) and offers a separate optional sideways four-hole test (9m52). No physical winner. Fit-seat01 is also held until the bore is updated. The3.6mm candidates are not approved for nominalD3 stock.

**Still required:** inserts arrive today; Jim will measure OD/length. Bore3.6/depth4/assumed3mm inserts are provisional. Generic coupon and actual inset/clamp retention need physical results; original shell fit over current wiring was not confirmed. SD LCD diagnostic/tablet colour test also pending. Shells/clamps in generated package have `.pending` suffix until hardware sizing is settled. No printer job queued/started. Windows delivery: `X:/Projects/Gladiator/print-release-round5-20261022/package/`; cad-lab Incoming also has `Round5_SD_20261022/`.


## M2 D3 L3 coupon — 2026-10-22 (Codex)

**Current revision:** Jim requested a smaller first pass. Use cad/coupons/m2-d3-l3-mini-20261022/ (four upright holes 2.8/2.9/3.0/3.1 mm). Incoming coupon updated to mini. Geometry and warning-free slice verified; physical winner pending. The larger version below is retained as history.

Insert-specific coupon delivered at cad/coupons/m2-d3-l3-20261022/; new 3MF in Incoming. Listing nominal M2 x OD3 x L3. Tests 2.60–3.30 by 0.10, 3.60 deep, upright and sideways. CAD/mesh/plate and warning-free Orca slice verified. Physical winners pending; do not apply bore changes yet. Existing M2-A and project parts preserved. See agents/codex-m2-d3-l3-coupon-20261022.md.


## Round 5 styling CAD review — 2026-10-21 (Codex)

Jim requested Round 5 styling while keeping v2.8 and its fit/structural geometry untouched. New model and complete review package: cad/v2/enclosure/round5-20261021/. Additive exterior receivers, M2-retained curved scuta/tablets/aquila, sculpted eagle relief, existing vent locations preserved, removable head clamps with captive contact shoes. Independent native/STEP/STL, material-preservation, interface, interference and service-path checks pass; source hashes unchanged. Physical follow-up: existing M2-A bore calibration/insert dimensions and loaded head movement/accessory weight. No print or existing CAD changed. Details: agents/codex-round5-styling-20261021.md.


## Camera service v2 review — 2026-10-21 (Codex)

Jim requested a cover/wiring redesign. Isolated native assembled/exploded models, STEP, review STLs, sources and validation: cad/head/camera-service-v2-20261021/. Two M3 nut-retained cover screws, open lay-in side channels with closing skirts, tie passages and wire-edge chamfers. Carrier hole pattern retained; camera moves 1.5 mm sideways for a 2.275 mm ToF-frame gap. Construction and independent saved-file checks passed. Desktop launcher: Gladiator Camera v2 - Review. Await Jim's CAD review; actual harness bend room, skirt fit and M3 stock need physical confirmation. Full bundle-to-mast routing not modeled. Existing CAD/plates/queue unchanged; no print started. Details: agents/codex-camera-service-v2-20261021.md.


## Shell v2.8: taller hood, speaker back, deeper heatsink notches - 2026-10-21 (Claude)

Jim: 55 mm inside from the deck underside; speaker over the dead space behind; heatsinks were cut off by the panel edge. Hood roof raised 3.9 (outer Z111.9) to Y57 then stepped down (raising the panels traps them under the neck arm, checked); speaker at X64 Y2; apertures also swept 15 mm straight down under the fins (shoulder edge Z90 -> ~76). Zero collisions, sweeps unchanged. Plates H 8 h 42 m, P 7 h 51 m in Incoming. Script backups v26/v27/v28 in ~/scratch_claude/.

## Speaker ears corrected - 2026-10-21 (Claude)

Jim: speaker ears take M2, are 2.8 thick and centred between the front and rear faces. Hood roof pads and the shell-off rail bracket posts adjusted; hood re-verified (zero collisions, sweeps unchanged). Plates H (8 h 10 m) and SPK (21 m) in Incoming.

## Shell v2.7: switch in the hood, rail-foot saddle, speaker under the roof - 2026-10-20 (Claude)

Jim: the rail foot should steady the rear of the shell (bolt optional); switch mounts in the shell; speaker up top. v2.6 recess withdrawn. Hood: flat rear (no pod), switch cradle as v2.5, saddle over the right rail foot shelf (0.3 clear), speaker cradle + grille under the roof at X64 Y38 (ears along Y, leads outboard). Shell-off speaker bracket on the left rail's rear hood inserts (`cad/v2/speaker-mount/v1-20261020/`).
Zero collisions; sweeps re-run. Plates H (8 h 04 m, 140 g) and SPK (27 m) in Incoming. ASSUMED speaker ears 2.5 thick, flush with the cone, M2. Not printed.

## Shell v2.6 finalised to the assembled v2 - 2026-10-20 (Claude)

Jim has v2 assembled (rails, deck v4.1, new wiring, switch on the rail shelf, INA upright adapter) and confirmed the hard-point faces. Hood: INA pod removed (flat rear); switch stays on the rail shelf with the shell on, so the hood cradle/shelf/window are gone and the rear wall has a bottom-open framed recess around the rail-mounted holder; old INA refs replaced by the adapter + board; deck +-2 mm X checked (hood 1.6, panels 5.6).
Zero collisions, sweeps unchanged. Plate H rebuilt (6 h 52 m, 127 g) via scripts/build_v2_savings_plates.py and copied to Incoming with P. Not printed. Open: loose wiring inside the hood volume (not modelled).

## INA226 upright adapter - 2026-10-19 (Claude)

Jim: mount the INA upright at the rear of the batteries/tray, underside toward the tray, header pins LEFT seen from the rear; adapter on the printed tray now, integrate into the tray later.
Built `cad/v2/ina-mount/v3-20261019/` (v2 hook unchanged + 2 mm upright plate bearing on the tray wall and battery end, board on 4 mm stand-offs, M2 x 2) and plate IM (26 m, 5 g, printed lip-down, no supports).
Checked on solids against tray v5, battery, deck, rails as installed, deck v4, switch holder, hood: no collisions. Not printed. Next: fuse into the tray once the adapter is proven.

## Holder: looser pocket, one screw - 2026-10-16 (Claude)

Jim: the pocket narrows around the switch body (too tight); the case is held by screws, so cut to one fastener. Holder now pocket 7.6 x 13.5, one M3 slot at the first shelf insert, 14.5 x 20.0 x 17.9; hood shelf one insert (Y-18.0) with guides; shell rebuilt, zero collisions. Plate SW 18 m. Deck v4.1 confirmed a perfect fit. Unverified: holder with the wired switch, rail-shelf twist with one screw, hood standoff lengths.

## Deck v4.1 CONFIRMED a perfect fit - 2026-10-16 (Claude)

Jim printed deck v4.1 and fitted it on the installed rails: perfect fit. The measured rail layout (symmetric about the mast, splay 1 mm per side over 89 mm, slot centres in `cad/v2/upper-deck/v4-20261016/README.md`) is now VERIFIED; the shell is built around it. Still unverified on hardware: hood standoff lengths (0.2 mm short of the modelled rail face) and the switch holder with the wired switch.

## Holder cradle in the hood - 2026-10-16 (Claude)

Jim: shape the holder to fit the shell attachment point. Hood shelf now has two side guides (15.0 apart, 0.25 each side of the 14.5 mm holder), window 15.4 wide on the same centre line, holder front flush with the outer skin (box_y_front -30.0, inserts Y-18.0 / -9.0). Holder unchanged (its floor slots still serve the printed rail shelf). Shell rebuilt, zero collisions, sweeps unchanged. Not printed.

## Deck v4.1 + holder without inside rounding - 2026-10-16 (Claude)

Jim tried printed deck v3 on the mast (rear left peg centred): all pegs sit outside their slots, left pegs increasingly toward the mast end, right rear peg outside by about 2 mm (he first said inward, then corrected), right front about twice. Deck v4.1: slot centres between the symmetric-rail model and Jim's offsets, 6.0 mm slots, all Y slots 12.6, tie-down slot 6.8 x 5.4 at X11.8 / 68.0. Still unknown: rails' Y position along the mast.
Holder v3: inside corner rounding removed on Jim's request (exterior R1.0 only), 6 walls + 100 % infill kept. D and SW and both ALL plates re-delivered to Incoming.

## Switch holder v3 - 2026-10-16 (Claude)

Jim: the switch is already wired; keep essentially the holder he has, slightly stronger, with a better mount point for covered/uncovered use, screws from the shell interior, NO rail reprint (the printed right rail has the shelf with two inserts). Built `cad/v2/switch-enclosure/v3-20261016/` (rear-open holder, front wall with knob slot, two M2 side screws, two M3 slots to the shelf inserts) + plate SW (23 m). Hood shelf moved to box_y_front -28.6 (inserts Y-16.6 / -7.6) with a 16.0 wide window; shell rebuilt and re-verified, zero collisions.
Deck: Jim printed deck v3 (wrong spacing) with the new rails, so nothing lined up; v4 not printed. OPEN: the rails' Y position relative to the mast is unmeasured (asked Jim to use v3 on the mast as a gauge: per peg offset to its slot).

## Shell on the measured rails; switch box on hold - 2026-10-16 (Claude)

Shell v2.5 rebuilt on the installed rails (see its README): no collisions, sweeps unchanged. Deck v4 is the deck reference.
Switch: Jim's switch is already wired, so the v1 box (front insert, pins through a window) cannot take it; a drop-in v2 draft exists (`cad/v2/switch-enclosure/v2-20261016/`) but Jim then asked for essentially the holder he already has, with dedicated mount points on the rails and the shell, mounted from the shell interior, and NO rail reprint.
Open: which existing holder (v1b? something else) and how it is mounted today; the printed right rail may already carry the 2 insert shelf (X61..77 in CAD, inserts X71, Y-10 and -1) which would be the rail mount point. No switch plate is queued; the v1 SW plate was removed from Incoming.

## Deck v4 on the measured rails - 2026-10-16 (Claude)

Jim measured the installed rails: pegs 58 mm (rear) and 60 mm (front) over their outer faces, tie-down holes 52 mm apart over inner faces, rails 15 mm from the mast tube each side, peg-to-peg 96.7 mm along the left rail. Rails splay about 1 mm per side over 89 mm; the CAD frame width was wrong.
Deck v4 (`cad/v2/upper-deck/v4-20261016/`): per-row slot centres, 5.0 mm slots, one locating slot (left middle), tie-down slot 5.6 x 4.4 at X11.2 / 67.8; checked against the rails placed at the measured layout. Outline NOT widened (3 mm per side hits the driver wedges); waiting for Jim's body width.
OPEN: the shell (hood standoffs, hard points) still assumes the CAD rail positions and must be rebuilt on the measured rails; the rear rail position is a symmetric assumption; plates D and ALL carry deck v4.

## Rails installed 46.5 mm apart - 2026-10-16 (Claude)

Jim installed the arch rails: inner faces 46.5 mm apart (CAD 43.0), no room to move sideways, printed deck v3 did not fit. Deck rebuilt with 7.7 mm wide peg slots (X12.25 / X66.75) and a 7.1 x 4.4 tie-down slot; verified at all three splits of the 3.5 mm; plates D and ALL (both layouts) regrafted and copied to Incoming. Rework of the printed deck by drilling and filing is in the deck README.
OPEN: the split between the rails is unknown (asked Jim to measure outer faces or inner face to mast tube); the shell hood standoffs and hard points assume rails at X6..18 / 61..73 and may be about 1.75 mm short per side; why the CAD frame width is off by 3.5 mm.

## Switch box 3 mm outboard + deck tie-down slot - 2026-10-15 later (Claude)

Jim: keep the power board as is; move the switch box instead of the INA. Right rail shelf X61..77, inserts X71, box centre X71 on rail and hood shelves (distance to the INA cassette 2.0 -> 3.9 mm on the rail shelf, hood 11.3 mm); shell v2.4 rebuilt and re-verified (sweeps unchanged).
Deck tie-down: Y83.5 kept (the only reachable spot: the S3 covers Y3..77 on the left, the breadboard Y15..61 on the right, driver bases start at Y89); slot now 6.0 x 4.4 at X13 / X66 so it serves the new insert (X14 / 65) and a drilled old-rail hole (X12 / 67). Checks are in the deck README.
Plates rebuilt (R 2 h 51 m, D 2 h 45 m, ALL mine 5 h 36 m). Jim's reorganised ALL plate was regrafted with the new geometry into Incoming (his layout and settings, supports on, 1.0 mm rail gap). OPEN: his profile says 250 x 250 and the layout reaches X231 / Y235: confirm the real print area.

## v2 folder move + first-print plates - 2026-10-15 (Claude)

Jim: all changes from the enclosure/rails chat go into a sub folder `v2`; the first print is PLA, not PETG. Moved `cad/{rails,upper-deck,switch-enclosure,antenna-pylon}` and `cad/enclosure/v2-20261013` into `cad/v2/` (script paths updated;
older entries in this file and DECISIONS.md still say `cad/rails/...` etc: read them as `cad/v2/...`). Codex's `cad/enclosure/concept-20261013/` was NOT moved (not from this chat; the scripts read it from there).
New `cad/v2/print-plates/`: OrcaSlicer plates R (both arch rails, 2 h 48 m, 36.5 g, enforcers under the 6 pegs/pads/shelf overhangs) and D (deck v3 top-up, 4 mm brim, 2 h 45 m, 42.7 g), EnderNeo / Generic PLA First Print / 0.20 Standard,
`scripts/build_v2_orca_plates.py`, `scripts/verify_v2_orca_plates.py`. Not opened in the Orca GUI, not printed, not queued. Windows mirror: C:\PlatformIO\Gladiator2.

## Deck v3 built + enclosure v2.3 - 2026-10-15 (Claude)

`cad/upper-deck/v3-20261015/` (README there): derived from the master UpperDeck by boolean edits (master untouched): six old rail-screw holes filled; six through slots for rail pegs (3.6 x 8.6 locating at Y68.35,
3.6 x 12.6 slotted at Y23.85 and Y112.85, X14 / X65); slotted retention holes 3.6 x 7.2 at (14|65, 83.5) for ONE M3 x 12 per rail into the rail insert; two O10 wire holes at (23, 44) and (56, 44) (my guess); 0.8 mm underside
chamfers on every new hole (the deck prints top-up on the glass). Mast bore/collar, the mast-front slot, the four driver bosses and the antenna bosses are unchanged, so the printed driver mounts and the mast are re-used.
Rails now carry the pegs (3.0 x 8.1 x 3.7) and one retention insert pad at Y83.5. Enclosure v2.3: boards and fins shifted 5 mm out along their 45 degree normals (real standoffs are 20 mm, CAD wedge model says 15),
shoulders 4 mm wider (X-41 / X120), apertures cut as the board's swept path (30 mm back along the pull), bed-side chamfers on roof holes / status window / mast notch, switch enclosure floor and bezel.
Sweeps: hood back 150 mm, right panel 120 mm, left panel 20 mm of 45 degree pull then outboard, 3 mm slack (was 4). All drafts, nothing printed.
Open: wire-hole positions; measure the real standoff and driver position; deck stiffness; the roof recess under the front-panel tabs prints as a 1.3 mm depression on the bed face and needs a thin support.

## Arch rails v4.1 - direct inserts, gussets, distributed hard points - 2026-10-15 (Claude)

Jim: rails thick enough that heat-set inserts go straight in (also the one from above) but no more; every attachment strong with fans under overhangs (save space, not plastic); hard points varied.
`cad/rails/v4-20261015/` now: band 8.5 wide, radial 7.0 at the legs growing to 8.5 over the top (8.5 = 7.5 insert + 1.0 floor); no bosses; three mount pads per rail filled down to the arch (no pad overhangs air);
lateral fans at both leg bases; two fans under the right-rail switch shelf; hard points Y22 (Z40, under the deck socket), Y35.5 (Z46), Y59 (Z45) per rail for the hood. Left rail 18.3 cm3 (master rail 28.6).
Strength estimate (arch_fe.py): 3.6 MPa worst case (4 g sideways), 0.33 mm. Enclosure v2.2: six tapered fan bosses (hood, M3 x 25), roof screw bosses have fan cones, switch shelf has fans.
**Tried and dropped:** a front-panel hard point at the front pad: its boss sits under the deck and the driver wedge, and the right panel's 45 degree pull-out stopped after 7 mm. The front panels hang from the hood roof tabs.
Sweeps: hood back 150 mm, right panel 120 mm, left panel two-leg path with 4 mm slack (unchanged). Still not built: deck v3.

## Arch rails v4 draft + switch enclosure + enclosure v2.2 - 2026-10-15 (Claude)

Supersedes the v3 portal rails (kept in cad/rails/v3-20261014). `cad/rails/v4-20261015/` (README there): elliptical arch rails, band 8 x 6 mm, inner face X18 so they print flat with no supports, about half the
plastic of the master rails, foot screws unchanged and open above their foot blocks, three peg-socket pads per rail (one tight, two slotted), shell hard points (Y30 Z38.3, Y56 Z44.9) in hardpoints.json,
switch shelf on the right rail. Rough 3D frame estimate (arch_fe.py): 4.8 MPa worst case at 4 g sideways against a 20 MPa allowable, 0.5 mm sideways. `cad/switch-enclosure/v1-20261015/`: open-rear switch box +
bezel, two M3 x 25 through the top into inserts, same part on the rail shelf (shell off) or a shelf inside the hood (shell on). Enclosure v2.2 reads the hard points from the rails and has a 15.1 x 18.5 bezel window.
Drafts, not printed. **Not built: deck v3** (pegs 3.0 x 8.1 x 7 on the arch centreline X14/X65 at Y24/68.5/113, optional slotted hole at Y90, wire holes). Open: nuts under the aluminium (assumed), retention,
switch pin pitch and rating, INA cassette position if the rail mount is used. Re-run verify_enclosure_v2.py after any rail or neck change.

## Rails v3 draft + enclosure v2.1 - 2026-10-14 (Claude)

`cad/rails/v3-20261014/` (README there): inverted-T 9 mm runners with no floor, foot screws kept at the master positions with open access shafts, three plain peg sockets per rail
(one locating, two slotted along Y) for a drop-in upper deck, one optional retention insert per rail, two horizontal M3 hard points per rail outer face (Y36, Y52, Z49), two O6 wire
ports per rail, and a switch arm built into the RIGHT rail (flush with the rail face, knob tip Y-32.3). Enclosure v2.1 (`cad/enclosure/v2-20261013/`): hood bolted to the hard points by four
M3 x 20 through 12 mm standoffs; skids, edge ribs and the exterior switch housing removed; 9 x 13 knob window in the hood rear wall. Drafts, not printed.
**Not built yet: deck v3** (pegs 3.0 x 8.1 x 11 at Y22/68/114, slotted retention holes, wire holes). Until it exists the sockets stay empty. Open: foot-screw hardware under the aluminium,
rail width, switch pin pitch and rating, stiffness of the 9 mm runner. Re-run verify_enclosure_v2.py after any rail or neck change.

## Enclosure v2 built - 2026-10-13 (Claude)

`cad/enclosure/v2-20261013/` (the README there is the detail; concept-20261013 is untouched). Four parts: rear hood (INA pod, SMA boss, status
lens window), front left/right (heatsink bays; the power switch now lives in an exterior housing with a screwed bezel on the front-right face, Jim 2026-10-14, replacing the cutout), lens plate with a light-pipe tube. The hood rests on two rear skids on the
aluminium deck plus stop ribs and ledges under the upper-deck edge; the front panels hang from the hood by 4 vertical M3 into heat-set inserts (roof tabs).
Verified: single valid solids, zero overlap, the hood slides back 150 mm, the right panel has one straight 45 degree pull, the left panel has a two-leg path
with 4 mm slack against the head neck arm. STLs are in the folder in print orientation; **not queued, not printed, not sliced**.
Open: (1) status LED position is ASSUMED (hood X21, Y14; `led_x`/`led_y`), only the small lens plate needs reprinting if wrong; (2) S3 USB end assumed to be
the rear; (3) SMA hole O7.0 (the pylon's modelled value) and, per Jim 2026-10-14, NO pocket around the nut or flange (2.0 mm flat land + spokes from r11; replacement
pylon at cad/antenna-pylon/v3-20261014/); the pigtail needs about 35 mm more reach for the shell mount; (4) rear pod depth 16 against a plugged
Dupont housing, unmeasured; (5) left panel slack is only 4 mm; (6) thermals, slicer pass, wall slivers (the erosion probe failed) and wiring loops are not checked.
Switch: pin window assumes the pins fit 5 x 10 mm (no pitch measurement); rating unknown; use an inline connector. Ask Jim before queuing prints.

## Orientation supersedes earlier directional descriptions — 2026-10-09 (Codex)

Jim chose **mast = FRONT**. Read ../ORIENTATION.md first: +Y forward, low X
LEFT, high X RIGHT. The switch v1b still occupies the high-X rail, now RIGHT
and frontward; the October5 handedness instructions below are historical.
No rewiring, mirrored parts, new aluminum features, or changed print plates.
The head viewing master faces +Y at legacy pan180, within the existing checked
range but at its endpoint. A centered front-facing head scan needs a separate
indexing/travel/harness review; do not silently change its servo limits.
After the frame update, physically confirm forward and turn directions with
tracks clear before normal driving; software/OTA checks do not prove motor motion.

Verified this session: S3 OTA accepted mast-front image SHA256
7f42a21a58e819d8cfc3875456e0e31e68d33fc4dc8d9d3d8e126f4cb78cfeff,
1524640 bytes. Boot3, app0, marked valid; SAFE/disarmed with0/0 outputs.
Runtime pin map LEFT EN2/PWM42,41; RIGHT EN16,11/PWM17,12; both inverted.
UART telemetry stayed live, frame-error counter unchanged at1. Exhaustive
host checks passed80802 track/trim cases and2025 IMU rebases. Chassis native
reload preserved162 original shapes. IMU/ToF/radar remain offline; actual
motor motion and measured IMU orientation have not been physically confirmed.


## Head print plates for OrcaSlicer — 2026-10-06 (Claude)

Jim asked for the head plates combined and the supports painted. Built `cad/head/orca-plates/`
(`scripts/build_head_orca_plates.py`): three OrcaSlicer projects with Jim's EnderNeo / Generic PLA /
0.20 Standard (4 walls, 30%) settings and painted supports. **A** pedestal, retainer, clamp cap, rotor,
pulley, carriage (4 h 35 m, 52.8 g); **B** display frame, carrier, receiver, yoke, ToF and radar frames
(6 h 20 m, 64.7 g); **C** Neck_Main with 8 mm brim (2 h 08 m, 26.8 g). Times are from headless Orca slices.
- Supports: pedestal and display frame use manual enforcers (top-plate underside clear of r 14.7 around the
  belt flange; four corner tabs). Neck_Main is auto with blockers in both bores, the tube-top lip and the
  two clamp-bolt ears. Nothing else is supported. `support-map-A/B/C.png` show where the slicer put them.
- Geometry untouched: all 13 parts match the released plates (volume, size, orientation).
- Placed in `~/3D-Printer/Incoming/Gladiator/` with `START_HERE_head-ORCA-plates.txt`. **Not printed; Jim starts.**
  The older v04 PLATE1-4 / v05 PLATE5 3MFs stay there, unpainted and superseded.
- Not done: opening the projects in the Orca GUI (command-line slice only). The receiver's three bridged
  roofs and the pedestal's 22 mm bridged roof at z 2.0 are unsupported as released.
- Jim measured the horn arm thickness: 2.0 (see `measurements/mast-head.md`).
- Also `cad/head/master/Gladiator_Head_Master.FCStd`: head-only viewing file, regenerate with
  `xvfb-run -a freecad scripts/build_head_master.py`.

## Power switch holder v1b — 2026-10-05 (Claude)

**v1b replaces v1 (wrong hand).** Jim: v1 "is shaped to fit the right leg, not the left". Cause: **the master's handedness.** The front is
at Y 0 and Z is up, so **low X is the robot's RIGHT**. `SideRailLeft` and the tray's "Base, left" are physically on the right, and the
robot's left rail is `SideRailRight` (X 61-73). v1 was built against `SideRailLeft`. v1b is the same part mirrored about X 39.5,
with every check rerun against `SideRailRight`, the tray, and "Base, right". All pass, with the same clearances.
When Jim says left or right, map it to the master this way. The object names are not renamed.

Jim wants the slide power switch held on the **left rail** in the rear leg space, carried by the raceway floor. **Knob to the rear,
pins forward** (Jim rejected knob-inboard and pins-toward-rail), up = ON. Built `cad/power-switch/v1b/`
(`scripts/build_power_switch_holder_v1b.py`, all checks pass). Switch measurements in `measurements/components.md`.
- Pocket in the gap between the rail and the tray leg on that side, beside the rail's rear wall; the knob top is flush with the deck's rear edge (Y 140).
- C-clip tongues on the raceway floor edge, plus a flange behind the rail's rear face. The tray leg (0.89 away) traps it. Fit it with the tray out.
- The tray lift path was swept and is clear. Nothing on top of the rail, so the upper deck is unaffected.
- Knob width 4.0, measured (window 5.0). Not printed; the STL is in `~/3D-Printer/Incoming/Gladiator/`. Jim starts prints.
- Jim: in tray v2 the tray leg should hold the switch instead.

## Power tray v5 + INA226 cassette v2 — 2026-10-03 (Claude)

Jim printed v4 and the v1 cassette and found: the click bumps and 0.25-clearance pegs were far too tight (nothing came out and the thin
1.0 front wall tore off the tray), the tray walls were far too weak, and the cassette's pressure fit would not work (it needs a lip over the
INSIDE of the wall). Rebuilt as new versions; v4 and v1 are kept as the record of what was printed.
- **Tray v5** (`cad/power-board/v5-tray/`, `scripts/build_power_tray_v5.py`, 52 checks): no bumps or grooves anywhere (plain wells, same 0.25
  clearance Jim said fitted well before the click); front and rear walls 2.4, floor 2.4 (grown downward, board height unchanged), 2 x 2 root
  gussets, 2.5 corner blocks, post-to-wall webs. Side walls stay 1.0 (0.1 inside the rails). v4 bases still fit; v5 bases are the same without grooves.
  **Arms are exactly the v3 arm** (checked to 0.00 mm3). Jim: the v4 V-scoop was an unwanted arm redesign; he only asked for ceiling clearance
  and feet into a base. Do not reshape the arms again without asking.
  Then Jim asked (via a multiple-choice question) for the long arm beside the mast to be shorter, same width: top Z 40 -> 34, 45 degree
  ramp into the taper; taper/flare/post proven identical to v3.
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

**Results 2026-10-03 (Jim):** R3a "Screen is a good fit"; R3b sideways nut block "fits 1" (1-notch, 6.0, already modelled). Not yet reported: R3c, window alignment / M2 corner pilots, circlip, horn screw, horn height (still holds Neck_Main). Logged in `measurements/mast-head.md` and `DECISIONS.md`.
**Later 2026-10-03:** circlip fits well. R3c (GH44 recess printed down) fits and keys one way but is about 1 mm too shallow (Jim, eyeball). Suspect roof sag over the bridge; unconfirmed. GH44_Tilt_Receiver in Plate 3 shares that recess and orientation: do not print it as released. Fix chosen by Jim: **register cut through the plate** (`build_head_v04.py`, receiver; 0 collisions rerun). The regenerated PLATE3 is in the printer folder, not printed. The R3d confirming coupon was built then deleted at Jim's request (no plastic on it); the through-window is unproven until PLATE3 prints. Plate 2 3mf also regenerated but unchanged in content, left unstaged.

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

## Completed independent mast-head review — 2026-10-05 (Codex)

Reviewed corrected candidate: `cad/head/review-20261005/README.md`; downloadable archive and native CAD/STEP/STLs are in the same tree. Confirmed and fixed the horn-height update removing the tilt screw seat, plus the 0.1 mm diaphragm left by the fused support arm after restoring the seat. The candidate has BOTH fixes. See `docs/ai/agents/codex-head-review-20261005.md` for the exact cuts.

Validation: 117,950 part/pose comparisons, zero detected collisions; no modeled ToF obstruction; clear axial cable probe; 24 valid assembly solids and 11 solid/manifold STL exports. Native and STEP reopen, matching volume, and exact comparison to captured source passed. Only GH44_Tilt_Receiver changes geometry. Master unchanged. Belt-at-carriage-end checks now regenerate the belt envelope; tilt sampled every 5 degrees. No print initiated or queue changed by this review.

IMPORTANT integration follow-up: the current `scripts/build_head_v04.py` observed at review completion has adopted the roof fix but not the final screw-shank recut after fusion. That leaves a 0.1 mm diaphragm. Apply BOTH fixes and rebuild Plate 3 before calling its receiver equivalent to the reviewed candidate. Keep concurrent v04 work intact. Sensor mounts, flex harness/strain relief/stops, actual horn screw fit, and inner-race spacer availability remain open. No additional coupon was made.

### Current head continuation — 2026-10-05 (Codex)

The earlier IMPORTANT v04 integration follow-up is **resolved**: the final shank recut
is in canonical source/native/STL and rebuilt Plate3. The saved assembly exactly matches
the reviewed candidate; native/STEP and all four mechanical plates independently pass.
Measured sensor mounts are now in isolated scripts/build_head_v05.py and
cad/head/v05-sensor-mounts/. Full sweeps and delivery packaging are in progress.
See the latest section of docs/ai/agents/codex-head-review-20261005.md and
measurements/mast-head.md. Preserve other agents' work and all review evidence.

### Head continuation completed — 2026-10-05 (Codex)

The in-progress v05 state above is now **complete and validated**. Current prototype:
cad/head/v05-sensor-mounts/README.md; native/STEP,13 STL and3-part Plate5 are delivered.
Corrected canonical v04 Plates1–4 are included; receiver shank/roof blocker closed.
Measured radar hole pitch15x23. Final rear stand-offs14 ToF/22 radar, nominal screws
4 M3x16/4 M3x25. Radar was advanced10 for full modeled downward-field clearance.
145,817 comparisons covered with documented exact-geometry reuse; all final gates and
native/STEP/plate/preview verification pass. Archive:
cad/head/integration-20261005/Gladiator_MastHead_v05_20261005.zip.

Next work depends on actual assembly: connector leads/flex harness,strain relief/stops,
horn screw fit,belt fit,9 mm inner-race spacer availability,screen alignment/screws and
loaded stiffness. Optical/antenna planes/radar RF performance are unmeasured. No new
coupon or print initiated. Preserve backups and concurrent agents' work.


## Enclosure concept - 2026-10-13 (Codex)

User requested an outer body to conceal wiring and finish Gladiator, retaining exposed masthead/heatsinks and allowing exterior antenna relocation. Isolated review model: cad/enclosure/concept-20261013/README.md. Three angular panels, roof Z108, main width97, shoulders153, Y-32..148. Includes current chassis geometry, current oriented v05 head, tray v5, INA cassette v2, switch v1b. Existing CAD sources untouched. Valid native and STEP shell reopen, three single solids, zero detected static volume intersections against selected modeled hardware. Not a print release; no manufacturing meshes or print job.

Next: user style feedback and whether wire loops can be rerouted. Actual harness/connector clearance, panel fasteners/registers/removal sweeps, dynamic tracks/head, SMA mounting-land thickness/pigtail reach, ventilation/temperature and print orientation remain open. Source hashes and explicit limits in validation.json. Do not silently treat the proposed dimensions as measurements. Files also copied to Storage/Projects/Gladiator/enclosure-concept-20261013.
