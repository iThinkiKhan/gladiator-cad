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

At any of these the driver assemblies reach roughly 50-58 outboard of wherever they anchor, which
may well make them the widest point on the vehicle. Track outer extent is still needed to confirm.

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
  the upper deck's 10.5 overhang each side is nowhere near the track edge; and a canted driver
  reaching ~50-58 outboard of its anchor becomes the widest point on the vehicle unless it is
  anchored at roughly X 0 / X 79 or further inboard.
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

- Motor driver: total height standing on its fins, and PCB underside to fin tips (see note above)
- C6 antenna connector position and pigtail length
- Mast OD, height above lower deck, and whether it passes through the upper deck
- Track **top height** relative to the deck top (Z = 2) — the outboard extent is now known (below)
  but the height is not.
- Battery: true width (79 vs 80), holder height with cells seated, cable exit and connector
- Vertical clearance needed above the holder to extract an 18650 (cells are 65 long; they may
  need to tip out rather than lift straight up)
- Battery front/rear gaps measured directly (resolves the 43.5 calculated vs ~45.5 estimated conflict in `chassis.md`)
- Motors: whether any part rises above the lower deck (Z > 2)
- Wire counts and gauges for front-to-rear runs, to size the raceway
- Screws on hand (M2 / M2.5 / M3, lengths) and heat-set insert sizes
- Printer bed size

### Board orientation — Jim's test fit, 2026-09-20

Jim dropped a real driver into the mount and found the **GPIO header ends up on
the outboard edge**, where the wires would have to climb back over the heatsink
to reach the S3. He wants it on the interior edge. He is right, and the mount
already allows it.

**Measured off `DriverMountLeft`, in the PCB's own frame** (u = 0..49.5
fore-aft, v = 0..51 along the cant, w = 0 at the PCB plane, +w outboard toward
the fins):

| Board edge | Where it actually sits | Wire run to the S3 |
| --- | --- | --- |
| **v = 0** | X -8.39, Z 90.0 — inboard and HIGH, 8.4 mm outboard of the deck edge | short, straight over the deck edge into the S3 envelope (tops out at Z 86.3) |
| **v = 51** | X -33.89, Z 45.83 — outboard and LOW, out over the track | has to climb back over the full heatsink |

So the cant runs inboard-high to outboard-low, and the fins point outboard-up.
The GPIO belongs at v = 0.

**The fix needs no change to the mount.** The four PCB screw holes are a
rectangle — 39.5 x 39.5 as currently modelled — and any four-corner rectangle is
centrally symmetric, so a **180 degree rotation of the board in its own plane
always re-registers on the same holes**, whatever the real pitch turns out to
be. Verified against the sketch: the pattern maps exactly onto itself.

An in-plane rotation also keeps the same face outboard, so the heatsink stays in
free air. Turning the board around moves the GPIO from v = 51 to v = 0 and does
nothing else.

**The frame is symmetric too**, so the flip costs nothing:

| Feature | Extent | Symmetric under the flip? |
| --- | --- | --- |
| Fore arm | u 0..8.5 | yes, maps to the aft arm |
| Aft arm | u 41..49.5 | yes |
| Open window | u 8.5..41, full v | yes |
| Relief pocket in each arm | v 10.75..42.25, 2 mm deep | **nearly** — centre is 26.5 against a board centre of 25.5, so it is biased 1 mm outboard |

That 1 mm bias is the only thing that weakly favours the current orientation. It
should be re-centred on v = 25.5 so neither orientation is preferred. Folded into
the same edit as the hole-pattern update rather than done on its own, since the
master gets touched once.

### Manoeuvrability — what actually constrains getting the board in

The board approaches from outboard-up and moves inboard-down along -w, straight
onto the frame face. Checked against ChassisDeck, UpperDeck, both side rails,
MastTube, MastBase, PowerShield, AntennaPost, S3Board, Breadboard and the
opposite driver mount: **the seated board is clear of all of them**, and so is
the approach.

The real constraint is the frame itself. Measured clearance inboard of the PCB
face:

| Region | Clearance |
| --- | ---: |
| u 9..40.5, all v — the open window | **13 mm**, clear through |
| u 0..9 and 41..49.5, v 13..38 — the relief | **2 mm** |
| u 0..9 and 41..49.5, v 0..13 and 38..51 — solid arm | **0 mm** |

So **anything on the component face standing more than 2 mm proud must lie
within u 9..40.5** — a 31.5 mm window in the 49.5 mm length. That is symmetric,
so the flip does not change it.

The screw holes sit at v 5.75 and 45.25, inside the solid strips, which is
correct — the board needs to seat flat where it is bolted.

### Still not measured, and this is the moment

Plate D has been blocked since 2026-09-18 on numbers that were assumed. Jim now
has a board in his hands, so:

- **Hole pitch, both directions.** 39.5 x 39.5 is an assumption. Two readings.
- **Where the GPIO header and the screw terminals sit** relative to the holes,
  and which edge each runs along.
- **What projects more than 2 mm from the component face within 9 mm of either
  short edge** — that is exactly what the relief pockets have to clear, and
  nobody has checked what is actually there.
- **Heatsink length along u**, still never measured.
- **Screw access.** The PCB bolts to the frame's outboard face, so check which
  side the screw head and nut can actually be reached from with the board in
  place.

Do not update the hole pattern by editing `drv_hole_pitch` — it drives nothing.
`DrvHoleSketch` carries literal coordinates and has to be rebuilt in a script
with the resulting solid verified.
