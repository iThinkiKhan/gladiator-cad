# Arch rails v4 - DRAFT, 2026-10-15 (Claude)

**Draft for review. Not printed, not fitted. The master SideRailLeft/Right are not modified.** Built by `build_rails_v4.py` (`freecadcmd`); strength estimate `arch_fe.py`.
Frame: +Y front (mast), +X right, +Z up. Replaces the v3 portal rails (`../v3-20261014/`, kept as the record).

Jim's brief (2026-10-15): the rails looked like bridge towers; wants a geometric design that keeps its strength without taking up so much space (an arch with mount points).
Nuts secure the rail feet (screw from above, nut below). PETG once the design is final. Thick enough that heat-set inserts go DIRECTLY in (including the one from above), but no more.
Every attachment must be strong, with fans under overhangs; the goal is to save space more than plastic. Hard points must be varied: the shell must not hang from one spot.

## What it is
* **An elliptical arch on two short legs.** Band **8.5 mm wide** (X9.5..18; the inner face is X18 so the part prints flat on that face with no supports), radial thickness **7.0 at the legs growing to 8.5 over the top**.
  7.0 at the legs is the most the battery (Y21) and the screw heads allow; 8.5 = 7.5 insert depth + 1.0 floor. Centreline ellipse over Y17.2..Y119.5, apex extrados Z49.75.
* **Foot screws:** same positions as the master rails, (10.5, 10) and (13.5, 127). The legs stand clear of them, so each screw head is in **open air above its foot block**.
  Foot blocks 12 wide, 4 thick. **Lateral fans** (a 3.5 x 10 mm triangle up each leg face) stiffen both leg bases sideways, where the strength estimate is worst.
* **Three mount pads per rail**, each filled down to the arch so no pad overhangs air (a fan under the overhang, made by filling the pad box and subtracting the space under the arch):
  rear Y14..41, middle Y56..80.7, front Y98..122 (the front one is deck seat only). Each carries a **peg for the deck** (3.0 x 8.1 x 3.7, tray style, 0.7 mm lead-in chamfer) that stands up through a through slot in the deck. The pegs live on the rails, not the deck, because the deck prints top-up and the glass bed forbids pegs under it.
  **One vertical insert per rail at Y83.5** (Jim: one heat-set per rail for the deck), in its own pad; the deck gets a matching slotted hole.
* **Hard points for the shell, spread along the rail, inserts straight into the pad / arch face (no bosses):**

| Point | Y | Z | Holds | Notes |
| --- | ---: | ---: | --- | --- |
| rear pad, low | 22 | 40 | hood | tucked under the deck socket (socket floor Z46.5): 4 mm of pad above it, floor 1.0 |
| rear pad | 35.5 | 46 | hood | in the pad block, floor 1.0, walls 3+ mm |
| middle | 59 | 45 | hood | in the 8.4 mm arch, floor 1.0, walls 1.9 |

  Three per rail, six in all, 37 mm apart end to end and at three different heights (Z40, 46, 45), so the hood is held at separated points on each side instead of hanging from one spot.
  **Tried and dropped:** a front-panel point at the front pad (Y100.5). Its boss sits under the deck and the driver wedge, so the panel could not rise along its forced 45 degree pull (right panel stopped after 7 mm).
  The front panels stay tied to the hood by their four roof tabs, and are located by the heatsink apertures.
* **Switch shelf (right rail only):** 12 x 28.5 x 10 block behind the rear foot (X61..73, Y-22..6.5, Z2..12) with two M3 inserts at (68, -10) and (68, -1), and two **fans** (triangular webs) down to the foot block either side of the screw head.
* **Wires:** no ports needed; the arch is open, so leads pass beside it and up through deck holes wherever wanted.
* **Volume:** left rail **18.3 cm3 vs 28.6 cm3** for the master rail (right rail 21.3 with the shelf): the saving is space, not so much plastic, as asked.

## Strength estimate (arch_fe.py, rough: read the limits)
3D beam frame along the centreline, fixed at both feet, loads at the three pads; PETG E = 2000 MPa; section 8.5 x 7.0 (the thinnest part); unit mass guessed at 0.9 kg; compared against 20 MPa (printed PETG, 4+ walls, loaded along the layers):

| Case (per rail) | max stress | apex movement |
| --- | ---: | ---: |
| static weight | 0.2 MPa | 0.01 mm down |
| 4 g shock down | 0.9 MPa | 0.05 mm |
| 4 g along Y plus weight | 2.7 MPa | 0.08 mm |
| 4 g sideways plus weight | 3.6 MPa | 0.33 mm sideways |

About 5x margin at 4 g. **Limits:** mass is a guess, feet assumed rigid, the fans and pad fill are not modelled (they only help), no stress concentrations, no print tested. Print on the inner face in PETG, 4+ walls; flex the first one by hand before printing both.

## Checked
Left and right are single valid solids; STL meshes solid and manifold; zero overlap with every chassis reference; touching the decks only where meant. Every hard-point bore probed in the solid: open, 1.0 floor, solid walls;
the void under the arch stays empty; pad overhangs are filled; the fans clear the screw heads.

## Open
1. Deck v3 is built (`../../upper-deck/v3-20261015/`): six through slots for these pegs, two slotted retention holes, wire holes.
2. Retention: one M3 x 12 per rail into the insert at (14 or 65, 83.5), decided.
3. Whether the nuts are under the aluminium or in the foot; I assumed under, screw from above.
4. Arch proportions are my choice (apex 49.75, legs to Z24). A flatter or taller arch, or a truss, are easy variants.

Files: Gladiator_ArchRails_v4.FCStd/.step, Gladiator_Arch_Rail_Left_v4.stl, Gladiator_Arch_Rail_Right_v4.stl, validation.json, hardpoints.json, arch_fe.json, arch_rails_v4_sections.png, build_rails_v4.py, arch_fe.py.

## Using the OLD printed deck with these rails (Jim 2026-10-15: a cheap adapter, or drilling, is fine)
The old deck is a flat 4 mm plate with six M3 holes that match nothing on the new rails, and the rails' pegs (3.7 high) would stand up into its solid plate (243 mm3 of overlap per rail).
* **Rails:** set `pegs=False` in `build_rails_v4.py` (or slice the pegs off) to get flat pads; the deck then seats flush with zero overlap.
* **Two drilled holes in the old deck, one per rail:** at (14, 83.5) and (65, 83.5), M3 x 12 with a washer into the rail insert. I checked both spots on the old deck: plain solid plate, 3 mm of material all round, nothing on top, clear of the S3 and the driver base.
  Locate them kinematically so rail spacing error cannot jam it: **left = round 3.6 mm hole, right = a slot 3.6 wide x 6 long running ACROSS the deck (two overlapping drill holes 2.4 mm apart in X).** The left hole fixes position, the right one fixes yaw.
* **Optional printed bits (cheap):** a 43.0 x 12 x 20 mm **rail-spacing gauge** (the rail inner faces are flat planes at X18 and X61, so a 43.0 mm block between them sets the spacing while you tighten the foot screws), and
  two 14 x 10 x 1.6 mm **slot washers** to give the screw head a clean bearing over the drilled slot. Neither is modelled yet.
* **Not recommended:** a printed peg adapter under the old deck. It would lift the whole deck, mast and head by its thickness, and the pegs would still need sockets in the rails.

## Update 2026-10-15 (later): switch shelf 3 mm outboard
Jim agreed to move the switch box rather than the INA cassette. The right rail's shelf is now X61..77 (was 61..73) with its two inserts at X71 (was 68); the outer fan runs to X77.
The box (X63.75..78.25) is 3.9 mm from the INA cassette (it was 2.0 mm by distance, 0.35 mm sideways), and it still clears the track approximation (starts at X79) and sits above it (track top Z7, shelf Z2..12 only to X77, box floor Z12).
The right rail STL is now 16 mm tall in print orientation (was 12): the shelf is the extra layers. Same part works on the hood shelf (also X71). Everything else on both rails is unchanged.

## Deck tie-down screw (2026-10-15, later)
One M3 x 12 + washer per rail into the insert at (X14 left / X65 right, Y83.5): unchanged. The deck slot over it is now 6.0 (X) x 4.4 (Y) at X13 / X66, so the same slot also lands on an insert drilled in an OLD rail at (X12 / X67, Y83.5). See the deck README for the checks.
