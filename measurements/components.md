# Gladiator component measurements

Units: mm. Caliper-measured 2026-09-15.

**These supersede everything implied by the printed coupons in `cad/TestPrint01/` and
`reference/test-batch-01/`.** Those coupons were confirmed inaccurate and must not be used as a
dimensional source for anything.

## S3 + expander deck (logic, upper deck)

| Feature | Value | Notes |
| --- | ---: | --- |
| Board length | 74 | |
| Board width | 42 | |
| Height, S3 mounted | 17.5 | |
| Height, tallest dupont pins | 28.3 | Governs upper-deck headroom |
| Mounting holes | 4.6 dia | One in each corner |
| Hole spacing across width | 35.5 | **Ambiguous — see note** |
| Hole spacing along length | 59.6 | **Ambiguous — see note** |

Hole spacings were reported as measured "from nearest edges of the circles." Taken literally
(the gap between facing edges), the width figure is geometrically impossible: 35.5 + 4.6 = 40.1
center-to-center on a 42-wide board puts hole centers 0.95 from the edge, so a 4.6 hole would
run off the board. Read instead as outer-edge-to-outer-edge, center-to-center becomes 30.9
(width) and 55.0 (length), placing centers 5.55 in from the long edges and 9.5 in from the
ends — plausible. **Unconfirmed. Do not cut a mounting pattern from these numbers yet.**

## Breadboard with C6 + BNO (logic, upper deck)

| Feature | Value | Notes |
| --- | ---: | --- |
| Breadboard length | 46.3 | |
| Breadboard width | 35.5 | |
| Breadboard height | 9.3 | Board alone |
| Height, tallest dupont pins | 21.5 | Including the board |
| BNO board length | 26 | |
| BNO board width | 15 | |
| BNO overhang past breadboard edge | 9.5 | Only 5.5 of its width sits on the breadboard |

The C6 carries an external antenna — antenna position and pigtail length not yet measured, and
it needs to sit clear of the aluminum deck to radiate.

## INA226 (power, lower deck)

| Feature | Value | Notes |
| --- | ---: | --- |
| Board length | 26 | |
| Overall length incl. dupont pins | ~40 | Pins extend past the board end |
| Board width | 22 | |
| Height, tallest point | 11.8 | |

## Motor driver x2 (power, lower deck)

| Feature | Value | Notes |
| --- | ---: | --- |
| Board length | 49.5 | |
| Board width | 51 | |
| Height incl. heatsink | 41.2 | |
| Height excl. heatsink | 18.7 | |
| Heatsink height | 32 | |
| Heatsink width | 51 | Matches board width |
| Heatsink protrusion past board bottom edge | ~28 | |

Intent: mount so the **heatsinks sit outside the body envelope** — exposed to airflow while the
bot moves, and to reclaim interior volume. Heatsink orientation relative to the board is not yet
pinned down precisely enough to model (see open questions).

## Power distribution board (power)

| Feature | Value | Notes |
| --- | ---: | --- |
| Board length | 60 | |
| Board width | 40 | |
| Height, tallest point | ~16 | |

## Breadboard power rails x2 (buses)

| Feature | Value | Notes |
| --- | ---: | --- |
| Length | 84 | |
| Width | 9.5 | |
| Depth | 9.3 | |

## Chassis observations (from reference photo, 2026-09-15)

- The vehicle is **tracked** (skid-steer), with track runs flanking the deck on both sides. Any
  hardware projecting outboard of the deck edges — notably the motor driver heatsinks — has to
  clear the track runs. Deck-edge-to-track clearance and track top height relative to the deck
  are **not yet measured** and gate that idea.
- The "battery case" is an **open 4-cell 18650 holder**, not a sealed box. Cells sit in open
  channels on spring contacts and are extracted **vertically**. The 79 x 75.5 footprint is
  consistent with four cells side by side across the width (~19 each) with their 65 length
  running fore-aft.
- Consequence: nothing may be permanently fixed over the battery unless it lifts away with the
  upper deck. This supports hanging the power distribution board from the deck underside —
  removing the deck exposes the cells for swapping.
- Because it is skid-steer, yaw scrubbing and vibration are significant. The BNO wants to sit near
  the center of rotation (roughly mid-chassis, X ~39.5, Y ~70) and ideally isolated from the
  deck's resonance rather than out at an extremity.
- The C6's external antenna is a long whip on an SMA pigtail. It needs a mounting point clear of
  the aluminum deck and of the motor drivers.

## Fit consequences against the existing chassis

Lower deck is 79 x 140 x 2. The battery box (79 x 75.5 x 19.5, Z 2..21.5) occupies the full deck
width at Y 21..96.5, leaving two exposed zones: **front Y 0..21 (21 deep)** and **rear Y
96.5..140 (43.5 deep)**. The tower bore sits in the rear zone at (39.5, 113), spanning X
32.5..46.5 and Y 106..120.

- **Motor drivers cannot lie flat anywhere.** Their 49.5 x 51 footprint exceeds the 43.5-deep
  rear zone in both orientations, and two side by side would need 102 of the 79 available width.
  Vertical or outboard mounting is mandatory, not merely preferred.
- **The power distribution board cannot sit in the rear zone.** At 60 x 40 it only fits that zone
  rotated (60 across X, 40 along Y) — but centered that way it spans X 9.5..69.5 and Y
  96.5..136.5, and the mast passes straight through it. The clear areas either side of the mast
  are only 32.5 wide, short of the 60 needed. It also cannot go in the 21-deep front zone.
  Candidate: hang it from the **underside of the upper deck** over the battery, so it lifts away
  with the deck and preserves battery access.
- **Power rails only fit fore-aft.** At 84 long they exceed the 79 deck width, so they cannot run
  crosswise. Candidate: recess them into the top of the side rails, where the wiring already runs.
- **Inter-deck height budget.** If the power distro (16 tall) hangs beneath the upper deck over
  the 21.5-high battery, the deck underside lands around Z 40, i.e. a rail roughly 38 tall above
  the lower deck. That is the current leading constraint on overall height.

## Still to measure

- S3 hole spacing, confirmed center-to-center (or edge-of-board to hole-center)
- Motor driver heatsink orientation relative to the board
- C6 antenna connector position and pigtail length
- Mast OD, height above lower deck, and whether it passes through the upper deck
- **Track clearance:** deck side edge to inner face of each track run, and track top height
  relative to the deck top (Z = 2). Gates whether heatsinks can hang outboard.
- Battery: true width (79 vs 80), holder height with cells seated, cable exit and connector
- Vertical clearance needed above the holder to extract an 18650 (cells are 65 long; they may
  need to tip out rather than lift straight up)
- Battery front/rear gaps measured directly (resolves the 43.5 calculated vs ~45.5 estimated conflict in `chassis.md`)
- Motors: whether any part rises above the lower deck (Z > 2)
- Wire counts and gauges for front-to-rear runs, to size the raceway
- Screws on hand (M2 / M2.5 / M3, lengths) and heat-set insert sizes
- Printer bed size
