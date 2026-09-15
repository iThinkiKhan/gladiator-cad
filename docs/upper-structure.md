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
| Power rails | Recessed into the top of each side rail | At 84 long they exceed the 79 deck width, so they can only run fore-aft; the side rails are already the wiring path |

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
