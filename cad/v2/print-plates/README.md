# v2 print plates for OrcaSlicer, 2026-10-15 (PLA)

Two OrcaSlicer project 3MFs for the first print of the v2 frame parts. Built by `scripts/build_v2_orca_plates.py` (`freecadcmd`), checked by `scripts/verify_v2_orca_plates.py`
(headless Orca 2.4.2 slice; support maps `support-map-R.png`, `support-map-D.png`). Settings: EnderNeo / Generic PLA @System - First Print / 0.20mm Standard @ First Print
(4 walls, 30% crosshatch, 0.2 mm layers, 0.3 first layer), supports `normal(manual)`.
Jim chose PLA for this first print (2026-10-15), so the earlier PETG notes (glass sticking, E = 2000 MPa) do not apply to the first set.

| Plate | Parts | Footprint | Estimate |
|---|---|---|---|
| R | `Arch_Rail_Left_v4` (56.2 x 133 x 12), `Arch_Rail_Right_v4` (56.2 x 157 x 16) | 124 x 157 | 2 h 51 m, 37.3 g |
| D | `Upper_Deck_v3` (85 x 140 x 14), 4 mm brim | 85 x 140 | 2 h 45 m, 42.7 g |

| (withdrawn) SW | `Switch_Housing_v1` (14.5 x 24 x 17.9, floor down, open rear to the side), `Switch_Bezel_v1` (14.5 x 17.9 x 1.2, flat) | 39 x 24 | 23 m, 4.3 g |

Plate **ALL** puts both rails and the deck on one bed. The repo copy is my layout (207 x 157, 3 mm deck brim, 5 mm gaps, extrusions X 4..216, 5 h 36 m, 79.8 g). Jim re-laid it out in Orca and I regrafted his positions and settings (EnderNeo SAFE, FIrst Layer Comp, supports on, normal manual, 1.0 mm top Z gap on the rails): 6 h 1 m, 78.8 g. At his positions the extrusions reach X 231 and Y 235, and his profile says 250 x 250: confirm the real print area.

## Orientation and supports
* Rails print on their flat inner face (the STLs are exported that way). Enforcers sit under every overhang of 10 mm2 or more that has no material below it: the 6 deck-seat pegs (2.5 mm gap, 32 mm2 each),
  the retention-insert pad (27 mm2), the hard-point pads (11 mm2) and, on the right rail, the switch-shelf overhangs (26 + 26 + 20 mm2). Left rail 6 supports, right rail 9. Bores are not supported.
* Deck prints top-up. Every new hole has a 0.8 mm chamfer on the underside, so the first layers on the glass are 45 degree flares, not overhangs. Supports: none.

## Checked
Slice read-back: support extrusions land only at the enforcer places (`support-map-R.png`); the deck has none. Both fit the 220 x 220 bed.
The 3MF was NOT opened in the Orca GUI; look at the preview before sending.

## Not checked
* No fit coupon was printed. The insert bores and the 4.2 mm slots follow the project's PLA calibration only.
* The arch strength estimate (`../rails/v4-20261015/arch_fe.py`) used PETG E = 2000 MPa. Max stress was 3.6 MPa; PLA is stiffer and more brittle, still an order of magnitude of margin in-layer, but a drop or crash onto a rail edge is what would break it.
  PLA also creeps if left under screw load in a hot car.
* Real 20 mm driver standoff positions, the deck wire holes (placement is my guess) and the shell have not been verified on the hardware.

## Rebuilt 2026-10-15 (later)
Rails: switch shelf 3 mm outboard (right rail 16 mm tall in print orientation). Deck: tie-down slot now 6.0 x 4.4 at (13|66, 83.5), usable on new and old rails. Both rails plates carry a 1.0 mm support top Z gap (object-level, so it applies to every rail support, not only the pegs).
The slice shows the top interface ending about 1.0 mm under the peg roofs but a thin plain stack still reaching close to the roof: check the preview under the pegs.

## Switch enclosure plate SW (2026-10-15)
Housing and bezel on one small plate, no supports: the pocket (7.1 wide) and the wiring shroud (9.0 wide) roofs are bridged, the floor holes carry chamfers on the bed side. 23 m, 4.3 g. Print it alone and test-fit the real switch first: the pin pitch (5.4 x 11 window) is assumed and the current rating is unknown.

## 2026-10-16: deck rebuilt for the installed rail spacing
Jim measured 46.5 mm between the installed rails' inner faces (CAD 43.0). Deck v3 now has 7.7 mm wide peg slots and a 7.1 mm tie-down slot (see the deck README). D: 2 h 44 m, 42.1 g. The rails and the switch plate are unchanged. ALL (both layouts) regrafted with the new deck.

## 2026-10-16 (later): deck v4
D and ALL carry deck v4 (`../upper-deck/v4-20261016/`): slots at the measured rail positions, 5.0 mm wide, one locating slot. D: 2 h 45 m, 42.6 g. The outline is unchanged (85 x 140), so the layouts are unchanged. The older D file (Upper_Deck_v3, wide slots) is superseded.

## 2026-10-16: switch plate withdrawn
The switch enclosure plate was removed: Jim's switch is already wired and the box is being redesigned (see `../switch-enclosure/v2-20261016/README.md`).

## 2026-10-16 (later): switch holder plate SW
Holder v3 (see `../switch-enclosure/v3-20261016/README.md`), one part, floor down, no supports, 23 m, 4.4 g. Replaces the withdrawn box plate.

## 2026-10-16 (later): deck v4.1 and holder with sharp inside corners
Deck v4.1 (6.0 mm slots at centres between the model and Jim's offsets, all slots slotted in Y): D 2 h 45 m, 42.3 g, ALL regrafted. Holder: inside rounding dropped, outside corners R1.0, 6 walls + 100 % infill: SW 24 m, 4.6 g.

## 2026-10-16 (later): holder with a looser pocket and one screw
SW: 14.5 x 20.0 x 17.9, 18 m, 3.5 g.

## 2026-10-19: time/material savings plates (Jim's choice)
Built by `scripts/build_v2_savings_plates.py` from the D plate's Orca profile, then sliced headless (Orca 2.4.2) to read the numbers back. Copies are in `~/3D-Printer/Incoming/Gladiator/`. The Orca GUI preview was not opened; look at it first.

| Plate | Parts | Profile change | Slice |
|---|---|---|---|
| D2 | `Upper_Deck_v4` (unchanged deck) | 3 walls, 3 top / 3 bottom, 15 % gyroid; 0.20 mm kept for the peg slots; 4 mm brim as D | 2 h 23 m, 34.8 g (D v4: 2 h 45 m, 42.3 g) |
| H | `Rear_Hood` (shelf insert pocket 0.6 deeper) | 0.28 mm layers, tree supports (auto) | 8 h 08 m, 141.9 g |
| P | `Front_Left` + `Front_Right` on one bed | same as H | 7 h 51 m, 121.4 g |

Shell total 15 h 59 m / 263.3 g against 18 h 07 m / 289.2 g at 0.20 mm with normal auto supports (the same slicer, same parts). Deck saves 22 min and 7.5 g. The driver bases are plate L (countersunk, with supports in the boss pockets; see `../../drivers/v5-interlock/README.md`, v5e); the rails are already printed. Not changed: the lens plate (natural/translucent filament, separate print).
What 0.28 costs: visible layer lines on the styled shell, and the 4 roof-boss insert pockets and shelf pocket come out in 0.28 steps. Tree supports alone cut ~8 g per part but add ~1 h; they pay off only with 0.28. Infill density barely matters on these (2.4 mm walls, 4 mm deck).

Deck v5 (deeper screw relief) was withdrawn the same day: the deck stays as printed; the driver base takes a countersink for flat-head screws instead (`../../drivers/v5-interlock/README.md`, v5e). Plate D2 therefore uses deck v4.

## 2026-10-19: INA226 adapter plate IM
`../ina-mount/v3-20261019/`: one part, printed upside down (lip on the bed), no supports, 26 m, 5.0 g.
