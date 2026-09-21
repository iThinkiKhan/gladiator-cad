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

Jim dropped a real driver into the mount and found the **GPIO face ends up
pointing outboard**. He wants it facing the vehicle interior. He is right, and
the mount as built cannot give him that — this is a real geometry change, not an
assembly choice.

**First reading of this was wrong** and is corrected here. It claimed the board
only needed turning 180 degrees in its own plane. That is false: an in-plane
rotation cannot change which *face* points outboard, and the face is the whole
problem.

#### What the frame was actually built for

Measured off `DriverMountLeft` in the PCB's own frame (u = 0..49.5 fore-aft,
v = 0..51 along the cant, w = 0 at the PCB plane, +w outboard):

| Test | Clash |
| --- | ---: |
| 2 mm strip over both arms, v 10.75..42.25 | **0.0 mm3** |
| Heatsink block 28 mm inboard through the window | 434.6 mm3 frame, **111 mm3 into the UpperDeck** |
| Heatsink 28 mm outboard | **0.0 mm3**, clear past 45 mm |
| Component block 13 mm inboard, inside the window | 26.7 mm3, effectively clear |

The relief pockets returning **exactly zero** against a 2 mm strip is the
evidence. They were cut to clear a 2 mm feature in that precise band, and the
only thing 2 mm proud in that band is the **solder tails flanking the heatsink**
on the back of the board. So the frame assumes the heatsink goes INBOARD through
the window, which puts the component and GPIO face outboard.

#### That contradicts the documented intent, and the intent is right

The "Mounting intent" paragraph above says the heatsink faces **outward** with
fins up in clean air, and the component face looks down-and-inward putting the
terminals toward the interior. The built frame does the opposite. Two
independent reasons the documented intent wins:

1. **Wiring.** With the component face inboard, the v=0 board edge sits at
   X -8.39, Z 90.0 — 8.4 mm outboard of the deck edge and level with the top of
   the S3 envelope (Z 86.3). A very short run. Outboard-facing, every wire has to
   come back over the heatsink.
2. **Heat.** Inboard the fins are buried against the upper deck in dead air, and
   they already clip it by 111 mm3 at full depth. Outboard they are in clean
   moving air, which is what the intent paragraph asked for.

#### The flip is feasible

Verified against the solid, not assumed:

- Heatsink outboard: clear of the frame and of every robot solid out past 45 mm.
- Components 13 mm inboard, inside the u 9..41 window: 26.7 mm3, effectively
  clear, and clear of the chassis deck, upper deck, rails, mast, power shield,
  antenna post, S3 and breadboard.
- The window stays clear to about 22 mm inboard before frame material appears
  and 28 mm before the upper deck does, so 13 mm of components has real margin.
- The four screw holes are a rectangle, so they re-register under a face-over
  flip exactly as they do under an in-plane rotation.

#### What has to change in CAD

The arms and screw pattern stay. The **relief pockets have to be re-cut for
whatever is on the component face near the short edges**, because after the flip
it is the component side, not the solder side, that sits over the arms. Their
current position and 2 mm depth were sized for tails and carry no information
about the component side.

That cannot be designed until the board is measured, and it is the same edit
that will rebuild `DrvHoleSketch` for the real hole pitch. One edit to the
master, once the numbers are in.

#### Needed from the board, which is now in hand

1. **Hole pitch, both directions.** Two readings. 39.5 x 39.5 is still an assumption.
2. **On the COMPONENT face:** what stands within 9 mm of each short edge, and how
   tall. This sets the new relief pockets and is the item that actually gates the
   change.
3. **Tallest component overall**, to confirm 13 mm.
4. **Which edge the GPIO header runs along, which the screw terminals**, and how
   far in from the holes.
5. **Heatsink footprint** — length along u and width along v, plus how proud it
   stands. Still never measured, and it decides whether the u 9..41 window is
   even the right size once it is on the outboard side.
6. **Screw access** with the board seated — which side a driver and nut can reach.

Do not update the hole pattern by editing `drv_hole_pitch`; it drives nothing.
`DrvHoleSketch` carries literal coordinates and must be rebuilt in a script with
the resulting solid verified.

#### Correction to the frame description, 2026-09-20 (probe: `scripts/drv_axis_check.py`)

Both earlier descriptions of this frame were wrong, including the one in
`measurements/components.md` dated 2026-09-19. Swept in global coordinates:

The frame does **not** touch the board in two strips. It touches it at **four
corner pads**, and the four screw holes land exactly in them:

| Region (u = 49.5 / global Y, v = 51 / cant) | State |
| --- | --- |
| u 0..9 and 41..49.5, **crossed with** v 0..11 and 42..51 | four solid pads, board seats here, screws here |
| u 0..9 and 41..49.5, v 11..42 | 2 mm recess — the solder-tail relief |
| **u 9..41, all v** | clear through, no material |

So the clear opening is bounded **in u**, the 49.5 / global Y axis, and it is
**32 mm wide**. Confirmed independently by the frame's own faces normal to Y, at
Y 89, 101, 128.5 and 140.5 — structure at the fore and aft ends of the board,
with nothing between.

`measurements/components.md` computes the arm fit as `(51 - 32) / 2 = 9.5`
strips along the **51** axis, and concludes 0.24 mm clearance per side. That
calculation is against the wrong axis. The heatsink figure that was measured —
**32 across the 51 axis** — is not the dimension this window constrains.

**The dimension that constrains it is the heatsink's extent along the 49.5 /
global Y axis, and that has never been measured.** If it exceeds 32 mm the
heatsink does not pass, and no amount of clearance on the other axis helps.

#### Which makes the flip more attractive, not less

With the board flipped to heatsink-outboard, the heatsink passes through
**nothing** — it stands in free air, verified clear of the frame and every robot
solid out past 45 mm. The unmeasured Y extent stops mattering for fit entirely,
and only the 13 mm component stack has to clear the window.

So the flip Jim wants:

1. puts the GPIO face inboard, 8.4 mm from the deck edge at S3 height
2. puts the fins in clean air, as the mounting intent always specified
3. **removes an unmeasured dimension from the critical path**
4. costs a re-cut of the four corner pads' relief, sized to the component side

#### Consequence for the print queue

`Gladiator_PlateG_MASTBASE-AND-DRIVERS.3mf` is in the printer queue and contains
both driver mounts. They are built heatsink-inboard. If the flip is accepted,
that geometry changes and the plate should be pulled before it is sliced —
64 cm3 and the tallest parts in the set.

### How the driver mount fastens to the deck — settled 2026-09-20

Probed the deck solid with a D3.0 column down the boss axis at (14.5, 95),
1 mm at a time (`scripts/drv_deck_boss_probe.py`):

| Z band | Deck material | State |
| --- | ---: | --- |
| 48..50.5 | solid | **2.5 mm floor** |
| 50.5..58 | none | open pocket |

So the D4.6 feature in each deck boss is a **blind pocket opening upward at the
boss top**, 7.5 mm deep, closed underneath by 2.5 mm of deck slab. D4.6 is this
printer's calibrated heat-set bore and 7.5 mm suits the 7.05 mm insert.

**That is an insert pocket in the DECK, not a clearance hole.** As printed, it
wants the insert in the deck boss and the screw coming DOWN from the mount.

Jim's recollection was the opposite — insert in the foot, screw up through the
deck — and that is why it never worked: nothing was ever cut to make it work. It
also explains why v1's column above the boss is 95 percent solid. That is not a
defect, it is the clearance hole that was never added, because the intended
direction was never settled.

**The deck is already printed, so this is now a fork, not a preference.**

| | Works with the deck as printed | What the mount needs |
| --- | --- | --- |
| **A. Screw down** | yes, no modification | a D3.6 clearance hole from the mount's top face to Z 58, and driver access above it |
| **B. Screw up** | needs the 2.5 mm pocket floor drilled through | a heat-set insert in the foot above Z 58; the existing D4.6 then serves as clearance |

B is a two-minute drill on a part that lifts off anyway, and it puts the insert
in a part being designed fresh rather than relying on a pocket that is already
committed. A costs nothing but needs real driver access designed, which v1 never
had either.

Either way the mount needs a feature at those two points that neither v1 nor the
v2 candidate has.
