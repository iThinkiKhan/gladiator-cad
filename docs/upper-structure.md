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
| Rail-to-deck mounting | **Via the existing slits, not the holes** | Slots give fore-aft adjustment when setting the rails |
| Existing 4mm / M2 hole pattern | Repurposed for board mounts | Freed up by moving rail mounting to the slits |
| Lateral adjustment | Add small horizontal (crosswise) slots at the rail feet | Absorbs the 3mm front/rear X offset and print tolerance |
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

## Proposed rail cross-section (for review, not yet modeled)

| Property | Value | Notes |
| --- | --- | --- |
| Overall | 14 wide x 38 tall | Z 2 (deck top) to ~40 (upper deck underside) |
| Left rail X | 5 .. 19 (center 12) | Covers front slot 8.5-12.5 and rear outer slit 11.5-15.5 |
| Right rail X | 60 .. 74 (center 67) | Mirrored |
| Length | ~130, Y 5 .. 135 | Just inside the deck ends |
| Wall thickness | 2.4 | 6 perimeters at 0.4 nozzle, PETG |
| Section | C-channel, opening inboard | Wires hidden from outside, accessible with the deck off |
| Internal raceway | ~11.6 wide x ~33 tall | Generous for the bundle |
| Deck attachment | M3 heat-set inserts in bosses at the rail top | 3-4 per rail |

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
