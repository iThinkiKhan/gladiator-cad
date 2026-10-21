**SUPERSEDED 2026-10-15 by the arch rails in ../v4-20261015/ (Jim: the portal rails still looked like bridge towers). Kept as the record.**

# Side rails v3 - DRAFT, 2026-10-14 (Claude)

**Draft for review. Not printed, not fitted. The master SideRailLeft/Right are not modified.** Built by `build_rails_v3.py` (`freecadcmd`); frame +Y front (mast), +X right, +Z up.
Photos used: X:\Projects\Gladiator\V1 Complete (2026-10-14).

Jim's brief: skinnier rails, no floor between legs and runner, easy access to the foot screws (they DO align), the upper deck sits in the rails like the tray sat in its feet
(the six deck screws almost never lined up), optional shell on natural hard points, holes to pass wires from the rails through the deck, and a power switch that works with or without the shell.

| | old rail (master) | v3 |
| --- | --- | --- |
| Runner | 12 wide, U with a 2 mm floor, soffit Z36.5 | **inverted T, 9 wide** (X6..15 left): 11 tall slab Z43.5..54.5 plus a 4 wide web to Z37.0. **No floor.** 16% less plastic (left rail 23.9 vs 28.6 cm3) |
| Foot screws | at (10.5,10) and (13.5,127) behind a 2 mm floor | **same positions** (they align); O6.4 access shaft straight down from the top to the foot, nothing in the way. Reach it with the upper unit lifted off |
| Deck attachment | 3 M3 inserts per rail (they do not line up together) | **three plain peg sockets per rail**, tray style: 3.6 wide, one tight locating socket (Y68, 8.6 long) and two slotted along Y (Y22 and Y114, 12.6 long) so a scale error cannot over-constrain it. Sockets are 12 deep. The deck needs matching pegs (3.0 x 8.1, 11 long) |
| Retention | six screws | **one optional vertical M3 insert per rail** (Y85); the deck gets a slotted hole there, so nothing has to line up. Gravity alone holds it otherwise (the tray was the same) |
| Shell hard points | none | **two horizontal M3 inserts per rail** in the outer face (Y36 and Y52, Z49), 7.5 deep |
| Wires | end windows | **two O6 vertical ports per rail** (Y44, Y92) through slab and web, open below, for leads going up to a deck-mounted board. The deck needs matching holes |
| Switch | clip holder on the rail | **arm built into the RIGHT rail**: 14 x 16.8 tube from the rear leg to Y-27.3, switch pocket 7.1 x 13.0 at the end, a bulkhead with a pin window, leads exit through a bottom window, and a removable bezel (2 x M2) clamps the body. Knob tip at Y-32.3, so it comes through the shell rear wall window |

## Checked
* Left, right and bezel are single valid solids; STL meshes solid and manifold. Zero overlap with every chassis reference (deck, battery, mast base, drivers, S3, breadboard); they touch the deck only where meant.
* Every feature probed in the solid (foot shafts open, sockets, insert bores, ports, arm pocket, bulkhead, pin window, exit window), left and mirrored right.

## ASSUMED or open (please answer before printing)
1. What sits under the aluminium at the foot screws (nut or thread) is unknown to me; I kept the positions.
2. Runner 9 mm wide is my pick for "skinnier"; the old rail was 12. The inboard face is now X15 (was 18).
3. Deck v3 is NOT built: it needs pegs, slotted retention holes and wire holes. Until then the sockets stay empty and the old deck cannot sit in them.
4. Switch: pin pitch unknown (pin window is 5.4 x 11); current rating unknown; use an inline connector so the rail can come off. Mounted on the right rail rear, knob facing the back.
5. A 9 mm T runner over a 92 mm unsupported span is thinner than before; I have not run a stiffness estimate. Print in PETG with 4 or more walls.
6. The old power tray bases and the tray are ignored in the clearance checks (the board moves to the upper deck).

Files: Gladiator_Rails_v3.FCStd and .step, Gladiator_SideRail_Left_v3.stl, Gladiator_SideRail_Right_v3.stl, Gladiator_Switch_Bezel_v3.stl, validation.json, rails_v3_sections.png, build_rails_v3.py.
