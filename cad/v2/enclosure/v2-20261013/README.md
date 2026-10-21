# Gladiator enclosure v2.3 - 2026-10-15 (Claude)

**v2.3 (2026-10-15): driver boards and heatsinks moved to the real 20 mm standoff positions (the CAD wedge model was built with 15 mm), shoulders widened 4 mm, new deck v3, bed-side chamfers. v2.2 (2026-10-15): the shell is an OPTIONAL add-on bolted to hard points on the arch rails (`../../rails/v4-20261015/`); the power switch is a separate open-rear enclosure that bolts to a rail shelf or to a shelf inside the hood.**

**Status: review model with print-orientation STLs. NOT queued, NOT printed, not slicer-tested. Jim starts prints.**
Built from the concept in `../concept-20261013/` (Codex), which is untouched. Current frame: +Y front (mast), +X right, +Z up,
origin rear-left of the aluminium deck ([ORIENTATION](../../../docs/ORIENTATION.md)).

Goal (Jim): hide the wiring and the working space with a stylish body; keep the heatsinks exposed as a styled, efficient feature;
let the INA226 pokes out into the look; give the S3 status light a window; sort the antenna; make it printable and removable.

## What changed from the concept

| Concept problem (found in review) | v2 |
| --- | --- |
| Front panels were threaded onto the driver boards: no straight removal path for the left panel with the head on | Panels still frame the heatsinks (4 mm around the fins, 2 mm around the PCB) but the seam moved to Y78 and the lap is **roof tabs only**; flank seam is a plain 0.6 butt. Right panel: one straight 45 degree pull. Left: two-leg path, 4 mm slack (see below) |
| No way to attach it | **Optional add-on, held at six spread-out hard points on the arch rails** (v2.2): three per side on the hood, at Y22 (Z40), Y35.5 (Z46) and Y59 (Z45) on the rail pads/arch. Every point is a tapered boss, wide at the wall like a fan, to 0.2 mm short of the arch face; M3 x 25 screws go in from the outside into heat-set inserts set straight into the arch. Positions come from `../../rails/v4-20261015/hardpoints.json`. Nothing else touches the frame. The front panels hang from the hood by 4 vertical M3 through the roof tabs and are located by the heatsink apertures (a direct front-panel point was tried and dropped: it blocks their 45 degree pull-out). |
| INA226 header pins 8.6 mm from the rear wall | **Rear pod**: 36 mm wide x 16 mm deep step, Z14..48, 45 degree top. Header tips (Y-21) now have about 24 mm to the pod's inner wall (Y-45.6) |
| Status LED hidden under the roof | **Lens window** in the roof over the S3 plus a separate **lens plate with a light-pipe tube** (see assumption A1) |
| Antenna: 2.4 mm wall vs ~2.2 mm SMA clamp limit; the old pylon sank the connector in an O11 x 4 mm pocket, too hard to hold and tighten (Jim, 2026-10-14) | **No pocket on either face.** Flat 2.0 mm land (a 0.4 mm O22 spot-face inside), O7.0 hole, nut and antenna on the flat outside face, four diagonal spoke ribs that start 11 mm from the axis so there is straight-in access at 0/90/180/270 degrees. Section: `sma_mount_v2.png` |
| Power switch reached through a 19 x 23 mm cutout, held by a clip holder that wobbled (Jim) | **A separate switch enclosure with an open rear** (`../../switch-enclosure/v1-20261015/`) bolts to a shelf inside the hood (shell on) or to the right rail's shelf (shell off): same part, same two inserts. The hood rear wall has a 15.1 x 18.5 window for the recessed bezel; the knob stands out 2.3 mm. No hallway |
| 3 tiny rear slots (72 mm2) | 3 louvers 42 x 2.4 mm (about 300 mm2) on the rear face |
| Plain box-ish rear and front | 6 mm rear and 5 mm front edge chamfers; uniform 2.4 mm walls (normal to the surface) |

## Parts (print orientation STLs in this folder)

| Part | File | Print size (mm) | Notes |
| --- | --- | --- | --- |
| Rear hood | `Gladiator_Enclosure_v2_Rear_Hood.stl` | 115.7 x 126.0 x 94 | roof down. Supports needed for the standoffs and SMA spokes; the 4 insert pockets face up |
| Front left | `..._Front_Left.stl` | 76.2 x 83.0 x 94.0 | roof down |
| Front right | `..._Front_Right.stl` | 76.2 x 83.0 x 94.0 | roof down |
| Lens plate | `..._Lens_Plate.stl` | 33.6 x 19.6 x 12.7 | face down, tube up. **Print in natural/translucent filament** |

All fit the 220 x 220 x 250 Ender-3 Neo bed. STL meshes are solid and manifold. Solid volume 170.8 cm3 (about 210 g at PLA density if
fully solid; the 2.4 mm walls are mostly perimeters). Do not trust a print time from me: slice it.

Hardware: 6 x M3 x 25 (hood to the rail hard points; 6 matching heat-set inserts go in the rails), 4 x M3 heat-set insert (D4.6 pocket, 7.5 deep, the calibrated bore) and 4 x M3 x 12 screws with washers for the roof tabs, 1 x SMA bulkhead
(the one on the pylon, with its nut), glue for the lens plate, optional 5 mm clear rod for the light pipe.

## Verified (build_enclosure_v2.py, verify_enclosure_v2.py -> validation.json, removal-sweeps.json)

* All four parts are single valid solids. **Zero volume overlap** with every chassis, tray, INA, switch and head reference. Skirt is 7.0 mm above the
  modelled track tops.
* Minimum gaps: standoff ends 0.2 mm off the rail faces (intended), hood to upper-deck edge 1.5, lens tube to S3 envelope 1.2, panel to driver PCB 2.0, to mast 3.0, to fins 4.0. The switch enclosure on the hood shelf was checked against the hood and the references (zero overlap).
* **Hood**: slides straight back 150 mm (the full distance tested) with the front panels on or off.
* **Front right**: one straight pull outboard and up at 45 degrees, 120 mm free, head on.
* **Front left**: no straight pull exists (the head neck's servo arm blocks any straight path at 23 mm). Two-leg path: pull 20 mm out and up at 45 degrees, then slide
  outboard at 15 degrees elevation; the neck arm leaves **3 mm of slack** on the first leg (v2.3). Workable, fiddly, and the one thing I would still improve.
* Roof screw access: free height above the head of each screw is 31 mm (X22), 53 mm (X33), open (X50, X66).
* A 1 mm resolution check caught a roof-tab collision that a 3 mm sweep missed (fixed). The sweeps are rigid straight-line translations only.

## Assembly and removal

1. Hood: slide it on from behind with the six tapered bosses running along the arch faces until its front butts the front panels' seam (Y78); fit 6 x M3 x 25 from the outside.
2. Front panels: lower each over its heatsink, tabs onto the hood roof recess, fit 4 x M3 (22/33 left, 50/66 right at Y72).
3. Removal: unscrew the 4 roof screws and the 6 hood flank screws. Right panel straight out/up at 45 degrees. Left panel out 20 mm at 45 degrees, then outboard. Then slide the hood back.
   The upper unit (deck, board, mast, head) lifts off the rails afterwards, as it does today. The switch enclosure unbolts from the hood shelf (two M3 from the top) and moves to the rail shelf.

## Assumptions and things I could NOT verify (read before printing)

* **A1 - status LED position is a guess.** The default light pipe is at hood X21, Y14 (S3 USB end, assumed rear). The window is 30 x 16 mm and the lens plate
  can be reprinted with the tube moved (`led_x`, `led_y` in `build_enclosure_v2.py`). The tube stops at Z94 (above the S3 *envelope*, which includes the tallest Dupont pins);
  a 5 mm clear rod in its 5.2 mm bore carries the light down to the LED. A printed tube alone will be dim at 40/255.
* **A2 - SMA hole is O7.0**, the value modelled for the pylon on the robot (the docs quote 6.5; the master CAD has 7.0). The pigtail must reach about 35 mm further back than it does now. Which way the connector flange wants to be held is unknown to me (round, hex or D-flat): both faces are flat and open so you can hold it with pliers while tightening the nut.
  The pigtail must reach about 35 mm further back than it does now.
* **A3 - the rear pod depth (16 mm)** gives about 26 mm from the header tips. I have not measured a plugged Dupont housing.
* **A5 - the switch enclosure** (see its README): pin pitch, rating and an inline connector are open. The shelf inside the hood is printed in the hood (cantilevered 25 mm from the rear wall, supports needed).
* **A4 - the four insert pockets** (D4.6, 7.5 deep, the project's calibrated bore) are installed from below with the hood off.
* The old antenna pylon can stay or go; v2 does not touch it.
* Not checked: thermal behaviour, a slicer pass, wall slivers (my erosion probe failed to run), the real tolerance stack of 1 mm-class gaps, wiring and connector loops (none modelled),
  RF performance of an antenna beside a printed shell. The hood screws are not tested for shake or load.
* PLA softens in a hot car or in sun. Dark PLA in direct sun at an event may need PETG (your call; the calibration is for PLA).

## Files

| File | What |
| --- | --- |
| `Gladiator_Enclosure_v2.FCStd` | editable native review assembly (panels, lens plate, reference solids copied from the concept) |
| `Gladiator_Enclosure_v2_Panels.step` | the four printed parts |
| `*.stl` | print-orientation meshes |
| `build_enclosure_v2.py` | `freecadcmd` generator; all dimensions are parameters at the top |
| `verify_enclosure_v2.py` | removal sweeps and screw access |
| `render_enclosure_v2.py`, `sections_enclosure_v2.py` | images (`xvfb-run -a freecad` for the first) |
| `validation.json`, `removal-sweeps.json` | evidence and limits |
| `render_*.png`, `sections_v2.png`, `sma_mount_v2.png` | views |

See also `../../antenna-pylon/v3-20261014/`: a replacement pylon built with the same no-pocket rule, for the case where you keep the antenna on the deck.

## v2.3 notes (2026-10-15)
* **20 mm standoffs.** `build_drv_v5.py` carries `STANDOFF = 15` (provisional); Jim says the printed mounts have 20 mm. The shell script therefore shifts each board and heatsink 5 mm outward along its 45 degree normal (X -3.5 / Z +3.5 left, X +3.5 / Z +3.5 right); the wedge and base do not move.
  Boards and fins still clear the head by 16.6 mm or more. The apertures follow the boards, and the shoulders are 4 mm wider (X -41 / X120) so the shifted board corners keep wall.
* **Deck v3** (`../../upper-deck/v3-20261015/`) replaces the deck reference; the hood and panels are checked against it.
* **Bed-side chamfers** on every through hole that prints on the glass (roof screw holes, status window, mast notch, switch enclosure floor and bezel); see the deck README.
* **Apertures are the boards' swept path (v2.3).** With the boards 5 mm further out they pierce the roof edge, and a plain offset hole stopped both front panels after 2 mm. The cut is now the board and heatsink outlines
  swept 30 mm back along the 45 degree pull (3 mm steps), so no roof or flank material lies in the path. Re-run `verify_enclosure_v2.py` after ANY change to the driver positions.
* Sweeps with everything of v2.3: hood back 150 mm; right panel one straight 45 degree pull, 120 mm free; left panel 20 mm of 45 degree pull then outboard, 3 mm slack against the head neck arm.

## v2.4 note (2026-10-15, later)
The switch box moved 3 mm outboard (box_x 71, was 68) to clear the INA cassette; the hood shelf, bezel window and insert pockets follow. Rebuilt and re-verified: no collisions, hood back 150 mm, right panel 120 mm, left panel 20 mm of 45 degree pull with 3 mm slack, as before.
The hood is 0.2 mm from the arch rails at its standoff contacts (intended).

## v2.5 (2026-10-16): rebuilt on the MEASURED rails
Jim installed the rails and measured them (pegs 58 mm apart at the rear and 60 at the front over their outer faces, 15 mm from the mast tube each side). `build_enclosure_v2.py` now places the arch rails as installed (left rail 2.0 mm out and turned 0.64 degrees about the rear peg, right the mirror)
and reads the face position of each rail at each hard point, so every hood standoff ends 0.2 mm short of the real rail face (they are about 2 mm shorter than before: the rails moved TOWARD the hood walls). Deck v4 replaces v3 as the deck reference.
Re-verified on solids: zero collisions; hood 0.15 mm from each rail at the standoff tips (intended); sweeps as before: hood back 150 mm, right panel one 45 degree pull of 120 mm, left panel 20 mm of 45 degree pull then outboard, 3 mm slack.
Not changed: the hood shelf for the power switch (box X71, floor Z30.5); the switch itself is being re-decided (see the switch-enclosure README).

**Holder window (2026-10-16, later):** the hood switch shelf now takes holder v3: shelf inserts at Y-16.6 and Y-7.6 (box front at Y-28.6), window 16.0 wide, same hood height. Rebuilt and re-verified: zero collisions, sweeps unchanged.

**Holder cradle (2026-10-16, later):** hood switch shelf widened to X61.5..80.5 with two 2 mm guides 15.0 apart (7 mm tall, Y-30..-8) around the holder; window 15.4 wide; holder front flush with the outer skin (box front Y-30.0, inserts Y-18.0 / -9.0). Rebuilt and re-verified: zero collisions, hood back 150 mm, right panel 120 mm, left panel 20 mm of 45 degree pull with 3 mm slack. Probes: guides solid at X62.5 / 79.5, window open, outer face open at Y-32.05.

**One-screw holder (2026-10-16, later):** the hood switch shelf has ONE insert (Y-18.0), the shelf ends at Y-12 and the guides at Y-11. Rebuilt and re-verified, zero collisions.

**Shelf insert pocket deeper (2026-10-19, Jim: inserts tended to sit high).** The hood prints roof-down, so the shelf's insert pocket opens toward the bed and its closed end is a 4.6 mm bridge. Bridge sag shortens such a pocket and leaves the insert proud (the same cause suspected for the head's R3c recess). The pocket is now 8.1 deep (was 7.5; floor 1.9 mm of the 10 mm shelf) for the 7.05 mm insert. The four roof-boss pockets print opening upward and are unchanged. Rebuilt and re-verified: zero collisions, sweeps unchanged (hood back 150, right panel 120, left panel 20 + 3 slack). Previous files: `~/backups/enclosure-v2-20261019/`. Slicer: bridge speed/flow for the hood is worth a look in the preview over that pocket.

## v2.6 (2026-10-20): finalised to the assembled v2 (Jim: rails, deck v4.1, new wiring, switch on the rail, INA upright)
* **INA bulge removed.** The rear pod existed only for the old INA's header pins; the INA now stands upright inside the body on its adapter (`../../ina-mount/v3-20261019/`). The rear wall is flat.
  The old INA cassette references are out of the clearance model; the adapter and the board envelope are in.
* **Switch stays on the right rail's shelf with the shell on** (the leads have some slack, not enough to move it into the hood). The hood cradle, shelf, guides, window and insert are removed.
  The rear wall is opened around the holder (X64.6..80.6, bottom open from the skirt at Z14 up to Z30.5) with a 1.6 mm frame (two side walls and a ceiling) running in from the skin
  to 0.6 mm short of the holder's face, so the inside stays hidden. The knob tip sits 5.2 mm inside the outer skin; the holder is 0.85 mm from the hood at its nearest.
* **Deck position tolerance.** Jim measures the deck overhang at 12 mm (right rear) and 8 mm (left) from the rail faces, against about 10.5 each side in the model. With the deck moved
  2 mm either way the hood keeps 1.6 mm and the front panels 5.6 mm, no overlap.
* Rebuilt and re-verified: zero collisions; hood 0.15 mm from each rail at the standoff tips (hard-point faces confirmed by Jim); sweeps unchanged (hood back 150 mm, right panel 120 mm,
  left panel 20 mm of 45 degree pull then outboard, 3 mm slack). Hood 94.3 cm3; plate H (0.28 mm, tree supports) 6 h 52 m, 127 g (was 8 h 7 m, 142 g). Front panels unchanged.
* Not checked: the loose wiring itself (the photos show long jumper loops at the rear and over the deck; they have to sit inside the hood volume when it slides on from the rear).

## v2.7 (2026-10-20, later): switch back in the shell, rail foot used by the shell, speaker under the roof
Jim: the rail foot is there to steady the rear of the shell (bolting optional); the switch mounts in the shell; add a speaker mount up top (rear/top, omnidirectional, leads to the top deck).
v2.6's rail-mounted switch recess is withdrawn (backup of that script: ~/scratch_claude/build_enclosure_v2.v26.py).
* **Flat rear (no INA pod)** and the INA adapter in the clearance model, as v2.6.
* **Switch in the hood**: cradle, window, one insert at Y-18.0 and the flush holder face, as v2.5 (holder v3, one M3 from inside). With the shell off the same holder bolts to the rail foot.
  The leads need about 20 mm more reach than on the foot (or an inline connector).
* **Rail-foot saddle**: a cap with cheeks hangs from the switch shelf over the right rail's foot shelf (0.3 mm clear over the top and both sides): the rear right corner of the hood cannot drop more than
  0.35 mm or shift sideways more than 0.35 mm. It slides on with the hood (2 mm lead-in at its front) and off again (hood back 150 mm checked). No bolt: the foot's front insert is under the deck edge
  and the rear one sits under the switch holder, so a screw there could only be reached through a hole in the roof; say if you want that.
* **Speaker cradle under the roof**, over the breadboard right of centre (centre X64, Y38): the cone faces up, 3.5 mm under the roof, behind a grille of 31 x d2.4 holes (chamfered on the roof face);
  two 7 mm ear pads with M2 pilots (36.5 apart along Y) and two end fences locate it, the outboard fence is notched for the leads, which drop beside the hood wall to the deck.
  ASSUMED: ears 2.5 thick and flush with the cone face. Clear of everything static; 2.95 mm from the S3 board (which stands beside it), 7.1 mm above the breadboard.
* Deck +-2 mm X: hood 1.6 mm, panels 5.6 mm, no overlap. Zero collisions. Hood 101.8 cm3, now 99 mm tall (the saddle). Plate H (0.28 mm, tree supports) 8 h 04 m, 140 g.

**Speaker ears (2026-10-21, Jim):** M2, 2.8 thick, CENTRED between the front and rear faces (6.1..8.9 behind the cone face), not flush. The roof pads now reach down 9.6 mm to the ear plane (cone still 3.5 under the roof). Rebuilt and re-verified: zero collisions, sweeps unchanged. Plate H 8 h 10 m, 141 g.

## v2.8 (2026-10-21): taller hood, speaker moved back, heatsink notches deeper
* **Hood roof raised to 55 mm inside** (Jim: measured from the deck underside, deck included): outer roof Z111.9 (was 108), from the rear wall to Y57, then a 45 degree step down to the old roof by Y60.9.
  The front panels, the roof lap and the seam screws keep their height: raised front panels hit the head neck arm (Z114) within 3 mm of their 45 degree lift-off (checked, both panels trapped), so only the hood goes up.
  Under the head (Y>57) the inside height stays 51.1 mm. Status window, lens plate and speaker grille follow the raised roof.
* **Speaker moved back** over the empty space behind the breadboard: centre X64, Y2 (cone 3.5 under the roof, Z106). 2.95 mm from the S3, 11 mm above the breadboard.
* **Heatsink notches:** seen from the side the shoulder top (Z90) hid the lowest 8 mm of each heatsink. The aperture now also runs 15 mm straight down under the fin outline (+4 mm), so the
  shoulder edge drops to about Z76 under each heatsink (fins bottom Z82). Panels 36.6 -> 35.2 cm3, still single solids.
* Zero collisions; hood back 150 mm, right panel 120 mm, left panel 20 mm of 45 degree pull with 3 mm slack. Plates: H 8 h 42 m, 148 g; P 7 h 51 m, 119 g.
