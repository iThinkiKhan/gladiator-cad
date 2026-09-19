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
| Hole span across width, outer edge to outer edge | 35.5 | → 30.9 center-to-center |
| Hole span along length, outer edge to outer edge | 59.6 | → 55.0 center-to-center |
| **Hole pattern, center-to-center** | **30.9 x 55.0** | Confirmed 2026-09-15 |

Spans were measured across the outer edges of the holes, so center-to-center = span − hole
diameter: 35.5 − 4.6 = 30.9 across the width, 59.6 − 4.6 = 55.0 along the length. That places
hole centers 5.55 in from each long edge and 9.5 in from each end, leaving 3.25 and 7.2 of
material outboard respectively. Self-consistent with the 42 x 74 outline.

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
| **Overall, fin tip to tallest component** | **41** | Governing stack height |
| Heatsink width | 51 | Matches board width |
| Heatsink protrusion below the PCB underside | ~28 | |
| Components above the PCB | ~13 | Back-solved from 41 overall |

No dupont pins on these boards — the tallest features are the screw terminals.

### Mounting interface — NOT MEASURED (2026-09-18)

**The driver mount's geometry depends on three numbers that appear nowhere in this file.**
They were carried in the design document as statements of fact; tracing them found no
measurement behind any of them. Until they are taken off a real board, the driver mount
is not printable.

| Number the design uses | Value assumed | Status |
| --- | ---: | --- |
| Mounting hole pitch, across the board | 39.5 | **assumed.** The only mention anywhere is one design-doc sentence. |
| Mounting hole pitch, along the board | 39.5 | **assumed**, and assumed equal to the other. The board is 49.5 x 51, so a square hole pattern is a guess, not a given. |
| Heatsink length | 32 | **assumed.** This file records the heatsink's width (51) and its protrusion (~28) but never its length. The mount's arms sit on the (49.5 - 32) / 2 = 8.75 of bare board it supposedly leaves at each end. |
| Board mounting hole diameter | not used | needed anyway, to know what screw the pattern takes |

Take all four with calipers off an actual BTS7960. For the pitches, measure outside-edge
to outside-edge across a diagonal pair and subtract one hole diameter, or inside-to-inside
and add one — and **measure the two directions separately** rather than assuming square.

If the heatsink length is not 32, the arms move even if the hole pattern is right: they
are positioned to land on bare board beyond the heatsink, not merely on the holes.


**Orientation:** the heatsink is on the **underside** of the board — fins project from the face
opposite the components, not from an edge.

**Mounting intent:** one driver per side, **canted diagonally with the heatsink facing outward and
the fins pointing up and away from the tracks.** The component face therefore looks down-and-inward,
putting the screw terminals toward the vehicle interior where they can be wired. Fins pointing up
and out keeps them out of track debris and in clean air — track fouling is not a concern in this
orientation.

Envelope, measured outward/upward from the board's inner edge (board 51 across the cant, fins 28
proud of the board face):

| Cant from horizontal | Outboard reach | Vertical rise |
| ---: | ---: | ---: |
| 30 deg | ~58 | ~50 |
| 45 deg | ~56 | ~56 |
| 60 deg | ~50 | ~58 |

At any of these the driver assemblies reach roughly 50-58 outboard of wherever they anchor. With
tracks reaching 50 outboard (X -50 / 129), anchoring at the deck edge X 0 / 79 lands them right at the track line; anchoring further out makes them the widest point.

Fallback if canting off the rails proves awkward: mounts that rise above and to the sides of the
upper deck, carrying the drivers at the same angle but higher up.

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

- **Tracks extend about 50 outboard of each deck edge**, measured 2026-09-16. Deck is X 0..79, so
  the tracks occupy X -50..0 and X 79..129, and **overall vehicle width is 179**. Consequences:
  the upper deck is now 79, flush with the aluminum, so it has no overhang at all; and a canted driver
  reaching ~50-58 outboard of its anchor becomes the widest point on the vehicle unless it is
  anchored at roughly X 0 / X 79 or further inboard.
- The vehicle is **tracked** (skid-steer), with track runs flanking the deck on both sides. Any
  hardware projecting outboard of the deck edges — notably the motor driver heatsinks — has to
  clear the track runs laterally; vertically they sit low (tops near Z 7) so anything at deck
  height or above is clear of them.
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

- Motor driver: total height standing on its fins, and PCB underside to fin tips (see note above)
- C6 antenna connector position and pigtail length
- ~~Track top height~~ - measured: ~5 above the deck, so tops sit near Z 7 (possibly more in motion).
- ~~Mast OD~~ - decided as a design choice, not measured: 20 OD / 12 bore, 13.8 base spigot.
- Battery: true width (79 vs 80), holder height with cells seated, cable exit and connector
- Vertical clearance needed above the holder to extract an 18650 (cells are 65 long; they may
  need to tip out rather than lift straight up)
- Battery front/rear gaps measured directly (resolves the 43.5 calculated vs ~45.5 estimated conflict in `chassis.md`)
- Motors: whether any part rises above the lower deck (Z > 2)
- Wire counts and gauges for front-to-rear runs, to size the raceway
- Screws on hand (M2 / M2.5 / M3, lengths) and heat-set insert sizes
- Printer bed size
