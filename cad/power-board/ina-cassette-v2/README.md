# INA226 cassette v2 — 2026-10-03

Built by `scripts/build_ina_cassette_v2.py`. It reads the master and the v5 tray without changing them, checks everything against
solids, and refuses to export if any check fails (28 checks pass). `ina-cassette-v2.png` shows it. **Nothing here has been printed.**
v1 (what Jim printed) is kept in `../ina-cassette-v1/`.

## What changed from v1

Jim, after printing v1: "the cassette needs a lip on its top connection to go over the inside of the power board, its not going to work
with just a pressure fit", and the tight mounts tore the front wall off the tray.

- **A real hook.** A plate outside the front wall, a lip over the wall top, and two toes down the **inside** of the wall (between the
  tray's new corner blocks). It **drops on from above and lifts straight off**. It hangs by its own weight.
- **No tongue under the floor, no friction bumps, no pressure fit.** Every gap to the tray is 0.3. Checked: the cassette touches nothing
  while dropping on from 40 mm above, and it cannot move more than the 0.3 gap in any direction (the toes meet the inside of the wall
  or a corner block, the plate meets the outside, the lip meets the top).
- The two corner blocks in the tray locate it sideways; the wings still sit between the rails' front posts as well.

## Layout (unchanged)

Board front to back, header edge facing the front with its pins poking out 7, terminals at the rear, flat shelf. 10 mm of wire gap
behind the terminals. M2 posts (4 tall, for the 3 mm pin tails) at the header-edge corners.

**The tray's front wall is thicker (2.4), so the board now hangs 14.0 past the deck's front edge and the pin tips reach 21.0**
(v1: 12.2 and 19.2). Say so if you want the wire gap trimmed to pull it back.

## Print notes (not started; Jim starts it)

- Print as exported (upright, shelf and plate bottoms on the bed). 41.8 x 43.0 x 12.1, about 4.6 g, 1181 mm2 on the bed.
- **It needs supports, from the build plate only**: under the lip (it overhangs 4.6 past the plate) and under the two toes (which hang
  4.7 below the lip). Nothing else overhangs.
- No fit is tight, so print it as is, no sanding. If it will not go on, the toes or lip are the likely cause; tell me the gap you see.

## Still inferred

The two M2 hole positions (2.0 from the header edge and each side edge) are from Jim's description, not calipered. Pin tails 3.0 are
Jim's "about 3 between the bottom of the screw terminal and the bottom of the board", read as below the PCB.
