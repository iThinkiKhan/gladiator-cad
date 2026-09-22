# Driver mount v5 — interlocked two-piece

Built 2026-09-20. Candidate; master untouched. Supersedes v2, v3, v4.

## The joint

v4's joint was 4 × M3 in single shear with proud heads — the weak point, and the
thing Jim called out. v5 moves the load into the plastic:

- **Full-length tongue and groove.** A 4 mm rib runs the whole Y length of the
  base's foot top (X 2..6); the wedge's seat plate carries the matching groove.
  It engages by lowering the wedge on, and it takes the outboard shear.
- **Guided entry and relieved root.** The tongue has 0.6 mm top chamfers and
  its two roots blend into the foot with R0.8 fillets. Matching R1.0 reliefs in
  the groove preserve 0.2 mm clearance while narrowing the mouth to X 1..7;
  that leaves a 1.0 mm edge web instead of the original 0.2 mm feather edge.
- **Full-length L seat.** The wedge beds on the foot top (Z 62) over 536 mm²
  after the entry and locator reliefs, and against the wall's outboard face
  (X 17). Two faces, both full length.
- **Structural roof over the groove.** The seat is 7.0 mm thick, leaving
  **2.7 mm of solid material above the groove** instead of the original 0.4 mm.
- **Fore/aft locator.** One 4 x 4 x 2 mm peg and matching pocket register the
  joint along Y with 0.2 mm clearance per side.
- **Screws clamp, they do not carry.** Four M3 run horizontally, normal to the
  vertical seat, so they put the joint faces into compression. Shear is the
  tongue's job.
- **Heads recessed.** Ø6.0 × 3.5 counterbore in the base wall's inboard face; an
  M3 socket head is about 3 mm, so nothing stands proud. Raising the wall top
  to Z82 leaves **3.0 mm above the upper counterbore** instead of 1.0 mm.
- **Inserts in the wedge, with room.** The flange is 9 mm thick and there is
  **15.0 mm of material behind each bore** against the 7.05 mm insert.
- **High bosses have conventional solid supports.** Each high standoff boss
  keeps its Ø9 insertion face, steps into a compact Ø12 × 3 mm collar, and sits
  on a full 9 mm-wide triangular pedestal tied directly into the rib and seat.
  The Ø4.6 × 8 mm insert pocket remains blind with solid material behind it;
  there are no longer any clipped cone or petal-like fragments.

## Measured

| | v3 | v4 | v5 |
| --- | ---: | ---: | ---: |
| Boss support, high pair | 0.0 mm³ | 277 | **318** |
| Boss support, low pair | 129 | 410 | **410** |
| Seat contact | n/a | none | **536 mm²** after lead-in + locator reliefs |
| Interlock | none | none | **4 mm, full 51.5 mm length** |
| Screw heads | n/a | proud | **recessed 3.5 mm** |
| Wall above upper counterbore | n/a | 1 mm | **3.0 mm** |
| Seat roof above groove | n/a | 0.4 mm | **2.7 mm** |
| Material behind insert | n/a | 4 mm flange | **15.0 mm** |
| Deck bearing | 1411 mm² | 803 | **954** |
| Volume | 20.4 cm³ | 37.0 | **41.7** |

Both pieces single valid solids at every build stage, zero overlap between them,
zero clashes against eleven robot solids, both deck screws open, all four
standoff axes clear, fins 6.6 mm inside the track line.

## Assembly

1. Heat-set into each deck boss (deck's own Ø4.6 pocket, as printed)
2. Base down, 2 × M3 from above
3. Heat-sets into the wedge flange, 4 off
4. Wedge lowered onto the base so the groove engages the tongue
5. 4 × M3 horizontally from inboard, counterbored
6. Board onto four M3 male-female standoffs, GPIO inboard

## Print package

Run `scripts/build_drv_v5_plate.py`. It writes:

- `Gladiator_DriverV5_INTERLOCK-FIT-COUPON.3mf` — print this first. It now uses
  full 51.5 mm sections cut from the real joint, including the lead-ins, root
  fillets and fore/aft locator. The base section prints in the production base
  orientation; the wedge section stands on its production end face. This tests
  layer direction and accumulated length error as well as nominal clearance.
- `Gladiator_PlateI_DRIVER-V5-INTERLOCK.3mf` — both left/right bases and wedges,
  already oriented and arranged for the Ender-3 Neo.

Plate I uses the existing calibrated PLA profile: 0.20 mm layers, 4 walls,
30% infill, a 5 mm brim, and automatic normal supports from the build plate.
The bases sit on their deck faces. The wedges sit on a full end face, the
orientation selected by OrcaSlicer 2.4.2 after comparing the candidate faces.
Do not auto-orient the finished plate.

`orca-v5-process.json` records those Plate I overrides. The fit coupon should
use the normal PLA process with supports off. Give the tall wedge section a brim.

## Still open

1. Zero running clearance on the deck cut, and **the revised tongue/groove pair
   is modelled at 0.2 mm clearance which has not been print-tested with its new
   lead-ins, fillets, locator or full length.** Print the representative coupon.
2. `STANDOFF` 15 mm remains provisional until the plugged connector is measured.
   Once measured, use the shortest standoff that clears the connector and wire
   bend; every millimetre removed reduces leverage at the boss.
3. ~~No print orientation.~~ Closed by the Plate I package above. The wedge
   needs support for its horizontal bosses in the selected end-face orientation.
4. **The load split is designed, not proved.** The tongue is intended to take
   shear and the screws to clamp; nothing here calculates how much each actually
   carries.
5. Fins reach Z 115.3, unchecked against the mast head's swept field.

Rebuild: `scripts/build_drv_v5.py`.
