# Upper deck v3 - DRAFT, 2026-10-15 (Claude)

**Draft for review. Not printed, not fitted. The master UpperDeck is not modified.** Derived from the master deck solid by `build_deck_v3.py` (`freecadcmd`, run after `build_rails_v4.py`).
Jim (2026-10-15): the deck sits in the rails like the power board sat in its feet; ONE heat-set insert per rail holds it down; re-use the printed driver mounts (20 mm standoffs) and the mast;
chamfer any hole that prints on the glass bed.

## What changed against the printed deck
| | printed deck | v3 |
| --- | --- | --- |
| Rail screws | six M3 holes (X12/67, Y16/68/120) that almost never line up together | **filled in**: nothing to line up |
| Seat | flat on the rail tops | **six plain through slots** on the rail centre lines (X14 left, X65 right): 4.2 x 8.6 locating slot at Y68.35, 4.2 x 12.6 slotted at Y23.85 and Y112.85. The rail pegs are 3.0 x 8.1 x 3.7 (peg top at Z58.2, below the deck top, so nothing pokes up under the S3 or the driver bases). Clearance 0.6 mm each side across (the two rails are located only by their foot screws in 4 mm aluminium slots, so their spacing can drift a few tenths: 4.2 not 3.6 absorbs it; see the rails README for the spacing gauge), 0.25 mm at the locating slot ends, 2.25 mm at the slotted ends |
| Hold-down | six screws | **one M3 x 12 per rail** into the rail's insert, through a **slotted hole 4.4 x 7.2 at (14, 83.5) and (65, 83.5)**: the slot absorbs misalignment, the pegs do the locating. Position chosen clear of the S3 (so the head is reachable) and 2+ mm from the driver boss. Use a washer |
| Wires | one slot at the mast front | the mast-front slot is kept, plus **two O10 wire holes at (23, 44) and (56, 44)** (my placement; they are parametric, say where you really want them) |

Unchanged: outline, the mast bore with its Z68.5 bearing collar (the mast is re-used), the four **driver-mount bosses** ((14.5,95) (14.5,135) (64.5,95) (64.5,135), D4.6 insert pockets), the S3 bosses and the antenna-pylon bosses (60,10) (76,10).
The printed driver mounts therefore bolt on exactly as now.

## Glass-bed chamfers
The deck prints **top up, underside (Z54.5) flat on the glass**. Every NEW hole (six peg slots, two retention slots, two wire holes) has a 0.8 mm x 45 degree chamfer on the underside; the old deck already carries 0.4 / 0.8 mm entry chamfers on its through holes.
Rails print on their inner face; none of their holes opens on that face. For the shell: the hood and the front panels print roof-down, so the roof screw holes (3.6) and the status window have chamfers on the roof face (0.7 and 0.6 mm), the mast notch has a 0.7 mm lead-in,
the switch enclosure's floor holes and the bezel's slot and screw holes are chamfered on the face that goes on the glass. The roof recess under the front-panel tabs prints as a 1.3 mm deep depression on the bed face and needs a thin support.
Printing aids, not tested on your printer.

## Checked
Single valid solid, volume 47.9 cm3 (old 49.5), STL solid and manifold, 85 x 140 x 14 mm. 15 probes in the solid: slots, retention slots and wire holes open; the old rail holes filled; plate solid beside the slots; the underside chamfer open;
mast bore open; a driver boss solid with its insert pocket open. Zero overlap with both arch rails, which touch it only where they seat (pegs in the slots).

## Open
* Wire-hole positions are a guess. The S3 and the breadboard will sit over them (leads rise under the boards).
* The retention screw needs M3 x 12 and a washer; confirm the head does not foul the breadboard region (it is at Y83.5, behind the S3 and breadboard).
* A flat 4 mm plate with six slots: I did not model its stiffness; it carries the same loads as before and sits on three pads per rail instead of the rail tops.

Files: Gladiator_UpperDeck_v3.FCStd, .step, .stl, validation.json, deck_v3_sections.png, build_deck_v3.py.

## Tie-down screws: checked 2026-10-15 (later)
Jim: confirm the tie-down screws catch the rails, and make the holes usable on new or old rails.
* **Position.** Y83.5 is the only place on the left that a screwdriver reaches: the S3 board covers Y3..77 (Z64.5 and up), the breadboard covers Y15..61 on the right, and the driver bases start at Y89. The old rail screw positions (Y16, 68, 120) are under the S3 or the driver mounts, so they cannot be reused on this deck.
* **One slot, two rails.** The slot is **6.0 (X) x 4.4 (Y)**, centred X13 (left) / X66 (right): it takes the new rail's insert at X14 / X65 and a hole drilled in the OLD rail at X12 / X67, both at Y83.5. I probed the old rail: solid there from Z47 to the top, with 3.7 mm of rail on each side of a Ø4.6 bore at X12, so a heat-set insert fits. Drill it Ø4.6, 7.5 deep.
* **Checks (solids).** M3 shank through the slot at X12, X14 (left) and X65, X67 (right): zero overlap with the deck. A 9 mm column over the screw head is clear of every reference (S3, breadboard, driver bases, mast, head) up to Z129 on the left (the pan servo) and clear to the top on the right: 70 mm of screwdriver room on the left.
  Zero overlap with both arch rails; the shell hood, front panels and removal sweeps are unchanged by this.
* **Washer.** About 40 % of a 7 mm washer bears on solid plate because the slot is wide: use a fender (9 mm OD) washer, or a plain one, and do not over-tighten PLA.
* **On old rails** the deck sits on their flat tops and is held by only these two screws, one per rail: it cannot slide more than the slot play (about 1 mm in X, 0.7 mm in Y), and nothing else locates it. The peg slots stay open (no pegs on old rails).

## Rails 3.5 mm further apart than designed (Jim, 2026-10-16)
Jim installed the arch rails: inner faces are **46.5 mm** apart (CAD 43.0), and the rails cannot move sideways. The first v3 deck (peg slots 4.2 wide, 0.6 each side) did not fit.
How the 3.5 mm splits between the two rails is not known, so the slots now cover every split: left peg X 10.5..14.0, right peg X 65.0..68.5.
* **Peg slots 7.7 (X) wide** (was 4.2), centred X12.25 (left) and X66.75 (right); Y lengths unchanged (8.6 locating at Y68.35, 12.6 at Y23.85 and Y112.85).
  Each peg now has 2.35 mm of play each side when the split is even, and still 0.6 mm when one rail did not move at all.
* **Tie-down slot 7.1 (X) x 4.4 (Y)** at X12.25 / X66.75: covers the insert at X10.5..14 (left) / 65..68.5 (right), and an old-rail hole at X12 / X67.
* Checked on solids at all three splits (left rail out 0 / 1.75 / 3.5 mm, right rail out 3.5 / 1.75 / 0): zero overlap of either rail with the deck and of the tie-down screw with the deck. Volume 46.7 cm3.
* The deck now sits on the pads with only loose X location from the pegs: the mast sets X, the tie-down screws clamp it. Washer: the slot is wide, so use a 9-10 mm fender washer (a 7 mm washer bears on only about a quarter to two fifths of its area).
* **Saving the printed (narrow) deck:** open the slots with a drill and file: peg slots to X8.4..16.1 (left) and X62.9..70.6 (right) over their existing Y lengths, tie-down slots to X8.7..15.8 (left) and 63.2..70.3 (right), width 4.4.
* **Open:** the shell's hood standoffs and any piece that touches the rail outer faces assumed rails at X6..18 / 61..73. If the rails really sit about 1.75 mm further out each side, the standoffs are about 1.75 mm short. Measure each rail's outer face (or inner face to the mast tube: CAD 11.5 mm each side) so I can correct it.


**SUPERSEDED 2026-10-16 by `../v4-20261016/`** (slots rebuilt on the measured rail positions). Kept as the record of what was first printed.
