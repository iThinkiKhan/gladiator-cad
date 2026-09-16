# Upper structure design log

Running record of decisions for the second-floor electronics deck and its supporting rails.
Started 2026-09-15. Component dimensions live in `measurements/components.md`; chassis/deck
geometry in `measurements/chassis.md`.

## Intended architecture

- Two structural rails running front-to-back along the sides, carrying a second-floor
  electronics deck above the battery.
- Rails double as protected wire raceways where practical.
- Upper deck spans essentially the full 140 front-to-rear length.
- Upper deck is removable while the rails stay mounted to the aluminum lower deck.
- Reinforced opening / support point in the upper deck for the sensor tower mast.
- No extra rear T-support unless the geometry demands it — the two rails plus the upper deck
  should form the structural box on their own.
- Battery and wiring stay serviceable. Deck area on both levels should be useful space.

Goal is a body that supports development and organization, replacing the current pile of parts
and wiring sitting on and around the battery.

## Decisions locked

| Decision | Choice | Rationale |
| --- | --- | --- |
| Process / material | FDM printed, PETG | Heat tolerance near motor drivers and battery |
| Upper deck fastening | Heat-set brass inserts in the rails | Deck opens repeatedly; self-tapped plastic threads strip |
| Component split | Power hardware low, logic up top | Keeps heat, noise and thick cable away from the S3 and IMU |
| Deck removal | Lifts off loaded, boards attached | Deck acts as a removable tray |
| Rail-to-deck mounting | **Via the outermost slits at both ends, not the holes** | Slots give fore-aft adjustment when setting the rails |
| **Aluminum lower deck** | **Existing physical part — do not add features to it** | It is already fabricated. The CAD is a faithful reverse-model. New features would mean hand-machining a finished plate |
| Lateral adjustment | Crosswise slots in the **printed rail feet**, not the aluminum | Some play, but not much. Keeps all tolerance absorption in the cheap-to-reprint part |
| Slot fastening | Plain M3 screw, nut and washer under the deck | A screw through a slot has nothing to self-tap into |
| Upper deck width | **100**, wider than the 79 lower deck | Two 9.5 buses on the edges leave an 81 channel; S3 (42) + breadboard (35.5) = 77.5 fit side by side. At 95 they would not |
| Motor drivers | One per side, **canted diagonally outward** | Fins (which hang below the board) aim down-and-out into moving air; flared "exhaust header" look; avoids a 49.5-tall vertical board punching through the upper deck |
| Power distribution board | Hung from the **underside of the upper deck**, over the battery | Will not fit the rear zone — the mast bisects it; hanging it means it lifts away with the deck and exposes the cells |
| Power rails | Fore-aft only; **placement unresolved** | At 84 long they exceed the 79 deck width, so they cannot run crosswise |

## Mast

The mast **penetrates the upper deck**, and the upper deck acts as its structural support. It
carries a **swappable sensor head**. Servo placement undecided.

**The lower deck 14 opening at (39.5, 113) is the anchor point.** The upper deck is a secondary
bearing, not the primary support.

That ordering matters structurally. The cantilever moment from the sensor head is reacted by the
aluminum lower deck, and the upper deck only has to restrain the mast laterally — a much smaller
load. So the upper deck opening needs a modest collar or bushing rather than a heavy reinforced
boss with ribs, which is what keeps the second-floor area around the mast usable rather than
sacrificed to structure. The two bearings sit roughly 38 apart vertically, which stiffens the mast
considerably against deflection compared with anchoring at one deck alone.

**Open:** mast OD is still unmeasured, along with whether the 14 hole takes the mast tube directly
or a stepped spigot at its base.

## Consequences of those choices

- A PETG boss hosting an M3 heat-set insert needs roughly a 4.2 bore with >= 2 wall around it, so
  the rail must be about 9 wide minimum wherever the upper deck bolts down.
- Two different joints, two fastener types: rails bolt **down** to aluminum with M2 screws
  self-tapping into the existing 1.6 pilots; the upper deck bolts **up** into heat-set inserts in
  the printed rails. Only the second joint is opened repeatedly.
- Because the deck lifts off loaded, the rail-to-deck wiring interface is a real design item.
  Leading approach: wires run up inside a rail and break at a connector near the top, so the deck
  disconnects at two points rather than twenty.

## Rail mounting geometry

Rails anchor through the outermost slits. Relevant existing slot geometry:

| Slot | X extent | Y extent |
| --- | --- | --- |
| Front left | 8.5 .. 12.5 | 7.5 .. 40.5 |
| Front right | 66.5 .. 70.5 | 7.5 .. 40.5 |
| Rear outer left | 11.5 .. 15.5 | 99.5 .. 132.5 |
| Rear outer right | 63.5 .. 67.5 | 99.5 .. 132.5 |

Note the **3mm lateral offset** between the front and rear outer slots (front centers X 10.5 /
68.5, rear outer centers X 13.5 / 65.5). A rail at constant X cannot sit centered in both, which
is what the added crosswise adjustment slots are meant to absorb. Size and placement of those
slots are not yet decided.

## Upper deck area problem

Recessing the power rails into the rail tops was considered and **rejected**: the upper deck sits
on top of the rails and spans the full width, so it would cover them. The buses need to be
reachable while the bot is running, so they have to live on an exposed surface.

That pushes them onto the upper deck, which is then tight. At 79 x 140 the deck must hold:

| Item | Footprint | Area |
| --- | --- | ---: |
| S3 + expander | 42 x 74 | 3108 |
| Breadboard (C6 + BNO) | 46.3 x 35.5 | 1644 |
| Power rails x2 | 84 x 9.5 each | 1596 |
| | **total** | **6348 of 11060** |

57% raw coverage sounds workable, but it does not lay out cleanly. Two buses along the side edges
leave a 60-wide central channel; the S3 (42) and breadboard (35.5) fit that channel individually
but not side by side (77.5), so they must sit fore-and-aft — 74 + 46.3 = 120.3 end to end. With
the mast at Y 113 eating the rear, only ~103 of length is clear ahead of it. Doesn't fit. Nor can
the breadboard be relegated downstairs: the rear zone is 43.5 deep (breadboard is 46.3 long, and
rotating it into the zone collides with the mast), and the front zone is only 21 deep.

Levers, roughly in order of preference:

1. **Make the upper deck wider than the lower deck.** Nothing constrains it to 79 — it sits above
   the tracks, which are free space. Going to ~95-100 wide buys 2000-3000 mm2, gives the buses
   their own edge lanes, and provides outer edges to hang the canted driver mounts from (the
   stated fallback). Also shelters the tracks.
2. Stack the breadboard above the S3 on standoffs.
3. Relocate the buses vertically onto the inner faces of the rails, reachable from above through a
   gap between the deck edge and the rail.

## Consequence of mounting through slots rather than holes

Self-tapping into the aluminum only works at the 1.6 pilot holes. A screw passing through a
**slot** has nothing to bite, so rail mounting needs a nut, T-nut or backing bar on the
**underside** of the lower deck. Under-deck clearance beneath the slots is therefore a new
requirement and is not yet measured — the track units and motors live down there.

## Side rails — BUILT

Modeled in `Gladiator_Master.FCStd` as `SideRailLeft` (PartDesign body) and `SideRailRight`
(mirrored about the deck centerline). Fully parametric off the `Parameters` spreadsheet.

**They are arches, not straight beams.** The battery holder fills the full deck width (X 0..79)
from Y 21..96.5 up to Z 21.5, so a constant-section rail sitting on the deck would pass straight
through it. The rails instead land on the exposed deck ahead of and behind the battery and span
over it.

**Faceted arch, not a portal.** The first version had legs sized by filling the footprint rather
than by load — a 37-long solid slab at the rear. Each rail carries roughly 2.5 N, which against a
12 x 8 PETG section is about 0.02 MPa versus PETG's ~50 MPa yield: over-built by three orders of
magnitude. Stiffness and printability set the minimum, not strength. The legs are now slender
haunches and the material between them is gone.

| Property | Value |
| --- | --- |
| Left rail X | 6 .. 18 (12 wide) |
| Right rail X | 61 .. 73 (mirrored) |
| Length | Y 2 .. 135 |
| Top face | Z 40, flat full length — carries the upper deck |
| Front foot | Y 2 .. 13, underside Z 2 |
| Front haunch | 4 chords, Y 13 -> 20, rising Z 2 -> 24 |
| Soffit | Y 20 .. 112, flat at Z 24 (2.5 clear over battery top Z 21.5) |
| Rear post | 4 chords, Y 112 -> 119, falling Z 24 -> 2 — 7 of run, matching the front |
| Rear foot | Y 119 .. 135, underside Z 2 |
| Beam depth over battery | 16 |
| Section | **Solid member with a raceway worked into it**, not a hollow shell |
| Raceway groove | Z 26..33 (7 tall) x 8.5 deep = 59.5 mm2, open on the inboard face, full length |
| Top slab | Z 33..40 (7 solid, full 12 width) — hosts the heat-set inserts |
| Bottom flange over arch | Z 24..26 |
| Outboard web | X 6..9.5 (3.5 solid) |
| Volume | 20508 mm3 each |

**Posts at both ends, not a diagonal.** v3 ran the rear haunch as a 24-long rake from Y 97 down to
Y 121, which meant the deck load was carried by that diagonal — the triangle was doing the work
rather than a post. The rear now drops in 7 of run, matching the front, and the soffit instead
runs flat all the way to Y 112. Side effect: the rear zone gains usable volume, because the old
rake cut down through exactly where the power hardware lives.

**Raceway capacity.** Wire counts are large and will keep changing as the build iterates, so the
groove is deepened to 8.5 (59.5 mm2 per rail, ~119 mm2 across both). At roughly 2.3 mm2 per
22 AWG wire including packing slop that is about 50 wires total. It cannot grow vertically — the
7 top slab is needed for the inserts and the beam is only 16 deep — so any further capacity comes
from depth, at the cost of the outboard web (now 3.5).

**Why solid rather than a shell.** v2 was a 2.4 thin-walled box section — structurally fine but it
read as a wall with a hole in it, and worse, a 2.4 top wall cannot host an M3 heat-set insert
(they need ~5.7 of depth). Making the member solid and cutting only a channel into it gives both
the bridge-arch look and a 7 top slab with somewhere for the inserts to actually live.

**The arch is asymmetric by necessity.** The battery sits 21 from the front deck edge but 43.5
from the rear, and the soffit has to be at Z 24 before it reaches the battery. The front haunch
therefore climbs 22 in 7 of run and is near-vertical whatever shape is drawn; the rear has three
times the room and gets the long sweep. Forcing symmetry would only waste the rear space.

The raceway is offset perpendicular to each haunch rather than vertically, so wall thickness
stays at 2.4 around the curve instead of thinning on the shallow rear chords.

**Mounting:** slots at both ends, per decision — no reliance on the 4mm locating hole. Each leg
has a crosswise adjustment slot giving 4 total lateral play (M3 clearance, 3.4 wide):

| Foot | Foot slot | Screw nominal | Lands in deck slot |
| --- | --- | --- | --- |
| Front | X 7.3..13.7, Y 8.3..11.7 | X 10.5, Y 10 | Front slot X 8.5..12.5, Y 7.5..40.5 |
| Rear | X 10.3..16.7, Y 125.3..128.7 | X 13.5, Y 127 | Rear outer slit X 11.5..15.5, Y 99.5..132.5 |

Travel is 3 total (±1.5) at each foot — "some play, but not much". The rail X range 6..18 is
centred on the midpoint of the two screw positions so both slots keep equal edge margin.

The 3 lateral offset between the front and rear deck slots is absorbed by the feet, so the rail
itself runs dead straight. Fastening is a plain M3 screw with a nut and washer under the deck.

**Wire retention.** Five tabs sit inside the raceway at Y 25, 45, 65, 85 and 105, each 4 long and
2 thick at the groove opening, alternating bottom (Z 26..30) and top (Z 29..33). They leave a 3
gap to press wire through and then hold it captive behind them; alternating sides makes the run a
shallow labyrinth so nothing works its way back out. Printed with the rail on its side the groove
opens upward, so the tabs need no support.

**Heat-set inserts.** Three M3 bores per rail (4.2 dia, 6 deep from the top face) at Y 16, 68 and
120, on the rail centreline X 12 — 3.9 of material either side. They sit in the 7 top slab with 1
to spare above the raceway ceiling. Positions dodge the driver shafts at Y 10 and 127.

**Foot wells.** At each foot the inboard face is opened out to 9 deep, from the floor at Z 6 up to
the raceway, so a driver can reach the mounting screw. Front well Y 2..15, rear Y 119..135.

**Driver access:** a 6 dia shaft through the top slab directly above each mounting screw. The
raceway is continuous, so a driver drops straight down through the hole to the screw head. The
upper deck covers these in normal use — they're only needed with the deck off, which is exactly
when rails get adjusted.

Verified: zero clash against the battery, the lower deck, or each other.

Insert positions (Y 16, 68, 120) are provisional — the upper deck's hole pattern must be drilled
to match them, or they get moved when the deck is laid out. Three per rail gives six fixings
across a 140 deck.

## Open questions blocking modeling

1. **Track geometry.** Deck side edge to inner face of each track run, the track's outer extent,
   and its top height relative to the deck top (Z = 2). The canted drivers flare outboard over the
   tracks, so this decides the cant angle and how far out the boards can reach before the fins
   foul the track.
2. **Motor driver height reconciliation** — the reported 41.2 / 18.7 / 32 / 28 figures don't close
   (see `measurements/components.md`).
3. **Mast OD** and whether it penetrates the upper deck.

## Deferred

- Whether the rails taper to follow the 3mm front/rear slot offset, or run straight with offset
  feet. Decide once the crosswise adjustment slots are sized.
- Rail-to-deck wiring connector location.
- Antenna mounting point, clear of the aluminum deck and the drivers.
