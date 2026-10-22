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
- **Screws clamp, they do not carry.** Four M3 run horizontally, the lower pair
  normal to the vertical seat and the upper pair 22° off it (see below; about
  93% of their tension still clamps the seat), so they put the joint faces into
  compression. Shear is the tongue's job.
- **Heads recessed.** Ø6.0 × 3.5 counterbore in the base wall's inboard face; an
  M3 socket head is about 3 mm, so nothing stands proud. Raising the wall top
  to Z82 leaves **3.0 mm above the upper counterbore** instead of 1.0 mm.
- **Inserts in the wedge, with room.** The flange is 9 mm thick and there is
  **15.0 mm of material behind each bore** against the 7.05 mm insert.
- **High bosses are complete cylinders.** Each Ø9 boss has an Ø4.6 × 8.2 mm
  blind insert pocket and 2.8 mm of solid backing. A flat 9 mm-wide web ties it
  to the flange. The upper boss columns pass into the base wall, so the wall
  has **vertical slots** around them: the column's 0.4 mm clearance swept
  straight up to the wall top. (A pocket that followed the 45° column, as first
  built on 2026-09-22, trapped it — lowering the wedge collided by up to
  2.7 mm³ between 1 and 5 mm of travel, and the parts could not be assembled.)
- **Serviceable with the mast fitted** (2026-09-23). Battery changes do not
  need the mount off (Jim, 2026-09-23), but it is still worth being able to
  remove it without disturbing anything else. The two upper joint
  screws sit at Y105 / Y124.5, between the boss slots and the mast tube's
  shadow, so they are **splayed 22° in plan** away from the mast. Straight in
  they had 8.0 / 11.5 mm of driver room before the mast; splayed, 34.5 mm (to
  the opposite mount), matching the lower pair's 37 mm. Their counterbores keep
  3.5 mm depth on axis; the thinnest wall under a splayed counterbore is
  **1.63 mm**, and the web to the boss slots is 2.14 mm. Print the new base and
  wedge together; the upper screw holes differ from every earlier v5 part.

## v5c base: cup relief (2026-09-24)

The printed 2026-09-23 wedges would not seat. The two upper heat-set cups (the
high boss columns) hit the base: the joint stayed open by roughly a millimetre.
The slot had 0.4 mm nominal clearance, but the wall behind each cup's closed end
rose parallel to its 45 deg face with only 0.25-0.3 mm to spare, and print error
closed that.

The cups locate nothing; the tongue and groove does. Jim, 2026-09-24: the wall
behind the cups is not structural, drop it. So the **base only** changes, and
the printed wedges are reused as they are:

- The slot is now the cup's own 45 deg bore, Ø(9 + 2 x 1.7), continued down its
  axis and out through the inboard face, with everything above it removed. The
  wall no longer rises behind the cup.
- The floor stops at Z73, keeping the full 2.0 mm wall over the lower joint
  screw's counterbore directly beneath each cup (Jim: don't thin it). The
  cup's lowest edge is 0.4 mm outboard of that counterbore, so this sets the
  down clearance at 1.5 mm. That screw's head seats on the counterbore floor,
  which is untouched.
- Past each cup's outer edge, the wall end drops to Z73 as well. This removes
  the thin fin that stood at each end of the wall.
- Toward the splayed upper joint screws the side clearance stays 0.6 mm; the
  web to those counterbores is 1.66 mm (v5 already had 1.63 mm there).
- Seated cup clearance: **1.5 mm down, 2.1 mm along the axis, open inboard,
  3.3 mm toward the base end, 0.65 mm toward the upper screw** (printed v5:
  0.3 / 0.25 / 0.3 / 0.45 / 0.45).
- The relief is cut after the wedge is final, so the wedge cannot grow into it.
  The build compares the rebuilt wedge with the printed one and refuses to save
  unless they match (difference 0.0 mm3).
- Base 16.59 -> 16.11 cm3. Deck bearing, seat, tongue, deck screws, joint screw
  counterbores and the coupon section are unchanged. Drop-on, lift-out, base
  removal and screw access all still pass.

Reprint `Gladiator_PlateJ_DRIVER-V5c-BASES-ONLY_deck-face-down.3mf` (both
bases, no supports).

## Measured

| | v3 | v4 | v5 |
| --- | ---: | ---: | ---: |
| Boss support, high pair | 0.0 mm³ | 277 | **282** |
| Boss support, low pair | 129 | 410 | **410** |
| Seat contact | n/a | none | **536 mm²** after lead-in + locator reliefs |
| Interlock | none | none | **4 mm, full 51.5 mm length** |
| Screw heads | n/a | proud | **recessed 3.5 mm** |
| Wall above upper counterbore | n/a | 1 mm | **3.0 mm** |
| Seat roof above groove | n/a | 0.4 mm | **2.7 mm** |
| Material behind insert | n/a | 4 mm flange | **15.0 mm** |
| Deck bearing | 1411 mm² | 803 | **954** |
| Volume | 20.4 cm³ | 37.0 | **40.3** |

Both pieces single valid solids at every build stage, zero overlap between them,
zero clashes against eleven robot solids, both deck screws open, all four
standoff axes clear, fins 6.6 mm inside the track line.

## Assembly

1. Heat-set into each deck boss (deck's own Ø4.6 pocket, as printed)
2. Base down, 2 × M3 from above
3. Heat-sets into the wedge flange, 4 off
4. Wedge lowered straight down onto the base so the groove engages the tongue
5. 4 × M3 from inboard, counterbored: lower pair horizontal, upper pair angled
   22° away from the mast (the counterbores set the angle)
6. Board onto four M3 male-female standoffs, GPIO inboard

## Removal — nothing else comes off

1. Unplug the driver board's wiring
2. Remove the 4 joint screws from inboard; the mast stays in place
3. Lift the wedge, board and heatsink as one unit straight up about 6 mm to
   clear the tongue, then out along the board's normal (up and outboard)
4. Remove the 2 deck screws from above; lift the base straight off

`build_drv_v5.py` checks each step against the robot as modelled, including the
mast tube, the head candidate above it and the mirrored right-hand mount:
wedge drop-on clear at every 0.5 mm, driver room at every joint screw, the
wedge unit's lift-out path, deck-screw access from above (60 mm clear) and the
base's lift-out. The build refuses to save if any of them fails.

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

## v5e base: countersink only (2026-10-19)

**This replaces v5d.** v5d buried a 3.0 mm socket head in the 4.0 mm foot and left a 0.7 mm clamp floor (0.5 mm in the
first versions). That was wrong: the printed bases had no usable clamping face. Jim's instruction: the ONLY change from the
original (v5c) base is a countersink for flat-head screws, so the screw sits flush and clamps the base to the deck through
the heat-set insert; the back wall makes room for the cone; supports go in the boss pockets so their ceilings do not sag.
The wedge (printed), the deck (v4, printed) and every other base feature are unchanged, except the little extra spacing
Jim asked to keep from v5d (below). v5d's head recess and insert relief are gone.

Fault being fixed: the deck screws sit on the foot top (Z62), the wedge's bearing face, so a head standing proud held the
wedge off (70 mm3 of overlap per socket-head screw on the v5c base).

- **90 degree countersink at each deck screw**, seat sized for the worst case M3 flat head (DIN 7991 / ISO 10642, dk 6.72,
  k 1.86, shank 3.0). Seat top diameter 7.3 at Z62, down to the D3.8 hole at Z60.24. The head finishes **0.3 mm
  below the foot top** (a smaller dk 6.0 head sinks to about 0.7).
- **Clamp seat under the head: 2.24 mm thick at the hole edge, resting on the boss top** (it was 0.7 mm), and the bearing
  area is 35.8 mm2 (it was 12.4 mm2 flat). The base is clamped through the cone onto the boss ring and the insert.
- **Extra spacing (kept from v5d, Jim):** deck-screw hole D3.6 -> D3.8 (the cone centres the head); tongue straight sides and
  locator peg shaved 0.05 mm per side (peg top 0.05 too), so the guide clearances go 0.20 -> 0.25 mm. The R0.8 root fillets
  keep 0.20. Bearing faces (seat, wall, foot underside) are untouched.
- **Back wall carved out for the screw head (Jim):** the countersink continues up through the wall root as a vertical
  cylinder of the seat's top diameter (7.3 mm, centred on the screw), 2.5 mm above the foot top (Z62 to 64.5). It reaches
  X18.16, i.e. 1.16 mm into the wall face (X17), and leaves a 1.7 mm web under the lower joint screw hole (Z66.2). The head,
  its driver and any head that ends up proud have a clean circular opening, and no lip hangs over the cone. The wedge flange
  stays at X<=17 so it does not touch the notch. Cost: about 13 mm2 of the wall face's bearing area per screw, the wall root
  band -8 %, the whole base 95 mm3 against v5c (16.11 -> 16.02 cm3), cones, wall carve and spacing together.
- Checks (printed wedge, saved base): head vs base 0, head vs wedge 0, wedge drops on at 0..5 mm lift with zero overlap,
  hex/Phillips access column open, base vs the v4 deck (+6.5 Z of this frame) 0.

**Screws (flat head, length measured from the top of the head).**
| Length | Tip Z | Engaged in the 7.05 mm insert | Deck pocket |
|---|---|---|---|
| M3 x 8 | 53.7 | 4.3 mm | clear |
| **M3 x 10** | 51.7 | **6.3 mm** | clear |
| M3 x 12 | 49.7 | 8.3 mm | hits the pocket floor (11 mm3) |
Use M3 x 10 (M3 x 8 also works). Heat-set inserts must end flush with the boss top.

**Printing: supports in the boss pockets.** The base prints deck-face-down, so the D9.8 pocket over each deck boss opens
toward the bed and its ceiling (Z58, 6.0 above the bed) is a bridge. Plate L carries a support enforcer in each of the four
pockets (R4.7, up to 0.3 above the ceiling); slice check: support only inside the pockets, layers 0.3 to 5.9 mm, nothing
else on the plate. Pull the supports out through the pocket mouth after printing. The rest of the profile is the baseline
D profile (4 walls, 30 % crosshatch, 0.20 mm). 2 h 06 m, 27.5 g for both bases.

`scripts/build_drv_v5e_countersink.py` (base) and `scripts/build_plate_v5e.py` (plate L) derive from the saved v5c base
because `build_drv_v5.py` can no longer reproduce the printed wedge (master drift). `build_drv_v5d_headrelief.py` is
superseded. Previous outputs: `~/backups/drv-v5c-20261019/`.

Print `Gladiator_PlateL_DRIVER-V5e-BASES-ONLY_countersunk-M3_pocket-supports_deck-face-down.3mf`.
