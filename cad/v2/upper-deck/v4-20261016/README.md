# Upper deck v4 - DRAFT, 2026-10-16 (Claude)

**Draft for review. Not printed, not fitted.** Built by `build_deck_v4.py` (`freecadcmd`), derived from the master deck as v3 was. Replaces v3 (`../v3-20261015/`, kept as record: its slots assumed the CAD rail spacing, which is wrong).

## Why
Jim installed the arch rails and measured the real body (2026-10-16): peg outer faces **58 mm apart at the rear, 60 mm at the front** (CAD 54); the two tie-down heat-set holes **52 mm apart over their inner faces** (about 56.6 between centres, CAD 51);
rails **15 mm from the mast tube on each side** (so symmetric about the mast, inner faces about 50 mm apart there); **96.7 mm** from the rear of the rear peg to the front of the front peg on the left rail (CAD 97.1).
So the rails splay about 1 mm per side over the 89 mm between the end pegs, and the CAD frame width was wrong, which is why no deck has lined up since the first print.

## What changed against v3 (everything is placed from the measurements, mast at X39.5)
| | v3 | v4 |
| --- | --- | --- |
| Peg slot centres X, left / right | 14 / 65 (all rows) | rear (Y23.85) **12.0 / 67.0**, middle (Y68.35) **11.5 / 67.5**, front (Y112.85) **11.0 / 68.0** |
| Peg slot width (X) | 4.2, later 7.7 wide | **5.0** (1.0 mm each side; covers about 0.5 mm of tape error) |
| Peg slot length (Y) | 8.6 locating at the middle, 12.6 others, both rails | **left middle 8.9 locating (0.4 each end); every other slot 12.6**. One locating slot only, so rails that differ by a fraction of a mm in Y cannot bind the deck |
| Tie-down slot | 6.0 / 7.1 x 4.4 | **5.6 (X) x 4.4 (Y)** at X11.2 / X67.8, Y83.5; the real inserts sit at X11.33 / 67.67 (1.17 mm margin each side) |
| Outline | 85 x 140 | **unchanged** (see below) |
Everything else is as v3: mast bore and Z68.5 collar, mast-front slot, four driver bosses ((14.5,95) (14.5,135) (64.5,95) (64.5,135)), S3 and antenna bosses, wire holes (23,44) (56,44), 0.8 mm underside chamfers on every new hole, old rail-screw holes filled.

## Checked (solids)
Valid single solid, STL solid and manifold, 85 x 140 x 14. 21 probes pass (slots open, plate beside them solid, chamfers, fills, bore, boss). **Zero overlap with both rails placed at the measured layout** (left rail shifted 2.0 mm out and rotated 0.64 degrees, right the mirror, splay about the rear pegs).
Tie-down screw M3 through each slot: zero overlap with the deck; a 9 mm column above each head is clear of every reference up to Z129 on the left (the pan servo: 70 mm of driver room) and clear to the top on the right; a 9 mm fender washer bears on 61 % of its area.
The deck stays on the mast for X; the pegs have 1.0 mm play each side.

## Outline widening: not done, and why
Jim asked for the whole deck to match the body width. I tried 3 mm per side: it runs into the driver wedges (204 mm3 on each side, between Y89 and Y140), and the original edge is not a plain full-thickness edge. Nothing needs it functionally (the nearest slot edge is 14 mm from the deck edge).
`widen` is a parameter in the script. I need the real body width before choosing a number; the rear half (Y0..88) is clear of the wedges if a step is acceptable.

## Open
* **Shell not rebuilt.** The hood standoffs and rail hard points assume rails at X6..18 / 61..73; the real rails are 2 to 3 mm further out per side and splayed. The shell sweeps and clearances are void until it is rebuilt on the measured rails.
* The rail splay is a symmetric assumption (15 mm from the mast on both sides at the mast); the rear was only measured as an overall spacing.
* Wire-hole positions are still my guess.

## v4.1 (2026-10-16, later): slot centres and tolerance after Jim tried the printed v3 on the mast
Jim put the printed v3 deck over the mast on the installed rails (rear left peg centred in its slot as the reference): every peg sits OUTSIDE its slot, left pegs increasingly so toward the mast end (about 1 mm at the rear, more in the middle, most at the front),
and the right rear peg is also outside its slot (about 2 mm; he first said inward, then corrected that), with the right front peg about twice the rear offset. That agrees in direction with the tape measurements (rails 55 mm apart over peg centres at the rear, 57 at the front, v3 slots 51).
The model (symmetric about the mast) and Jim's rough offsets differ by up to about 1 mm, so v4.1 puts each slot centre between the two and makes the slots wide enough for both:
| | slot centre X (left / right) | peg X from the model | peg X from Jim's offsets (rough) |
| --- | --- | --- | --- |
| rear (Y23.85) | 12.5 / 67.0 | 12.0 / 67.0 | about 13 / 67 |
| middle (Y68.35) | 11.75 / 67.75 | 11.5 / 67.5 | about 12 / 68 |
| front (Y112.85) | 11.0 / 68.5 | 11.0 / 68.0 | about 11 / 69 |
* Peg slots **6.0 wide** (1.5 mm of play each side), **all six 12.6 long** (no locating slot: the Y position of the rails along the mast has not been measured, so nothing in Y is tight; the mast and the tie-down screws locate the deck).
* Tie-down slot **6.8 (X) x 5.4 (Y)** at X11.8 / X68.0, Y83.5: covers the insert from X10.5 to 13.1 (left) and X66.6 to 69.2 (right), margin 1.4 to 1.6 mm each side in X; Y play 1.2 each side. Still serves a hole drilled in an old rail (X12 / X67).
* Checked on solids: valid single solid, 46.9 cm3, STL solid and manifold, zero overlap with both rails at the model's measured layout, the tie-down screw clear of the deck, 70 mm of screwdriver room on the left and clear on the right, 42 % of a 9 mm fender washer bearing on the plate. 21 probes pass.
* **Still open: the rails' Y position along the mast** (nothing in Y is tight, but if the real offset is more than about 2 mm the slots still miss). A front-to-back offset per peg from the printed v3 would settle it.

## What locates the deck (2026-10-16, Jim: Y is about centred on the printed v3; the tie-down screws matter more)
* **The mast locates the deck.** The mast bore is R10.2 on a R10.0 tube: 0.2 mm of clearance, so the deck cannot move in X or Y once it is over the mast. Everything on the rails therefore has to be placed relative to the MAST, which is how the slot centres were derived (rails 15 mm from the tube each side, symmetric, splayed toward the mast end).
* **Jims Y check:** with the printed v3 on the mast, every peg sat roughly centred along its slot length, so the rails Y position along the mast matches the CAD to about a mm. v3 had a tight (8.6 mm) slot in the middle with no front-back play, which fitted only because of that.
* **So the slots are deliberately loose and the tie-down screws are the hold-down:** pegs 6.0 x 12.6 (1.5 mm each side in X, 2.25 in Y) only stop the deck turning more than about 1 degree about the mast and keep it on the pads; the tie-down slots 6.8 x 5.4 take the rail position error that the mast bore cannot, and the one M3 per rail pulls the deck onto the pads. A tight tie-down hole would fight the mast bore, so I did NOT make them tight.
* The skew is built in: the slot centres move outboard toward the mast end on both rails (left 12.5 to 11.0, right 67.0 to 68.5).

## Fit confirmed 2026-10-16
Jim printed v4.1 and fitted it on the installed rails: perfect fit.
