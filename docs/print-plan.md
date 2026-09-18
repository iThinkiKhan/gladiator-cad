# Print plan — body and mast (prepared 2026-09-17 for 2026-09-18)

Nine STLs are in `/home/buralien/Desktop/3D-Printer-Incoming/`, named `Gladiator_P<plate>_...`.
Every one was exported at 0.01 mm deflection and passed: single closed solid, manifold, no
self-intersections, sitting on Z=0, fits the bed, volume matches CAD to 0.5%, and **the intended
face is verifiably the one on the bed**.

The head is deliberately excluded — its interface is not frozen.

## The one thing that has to happen in order

**Plates 3 and 4 are gated on the insert-bore result.** The rails and the upper deck carry all
16 heat-set insert bores between them, about 130 g of filament, and every one of them is
currently 4.4 mm on an unverified assumption. Measure first, then slice those two plates.

Nothing else is gated on it: plate 2 has no insert bores in it at all, so it can run while the
coupon is being measured.

> If you still have the **all-in-one v2 coupon printed on 2026-09-17**, measuring that gives you
> the same insert-bore answer *plus* the spigot-peg, clearance-hole and slot answers, and you can
> skip printing plate 1 entirely. Coupon A is there in case that print is gone or you want a
> fresh one in the filament you are about to use.

If the winning bore is not 4.4, it is one spreadsheet parameter (`rail_insert_dia`) feeding all
16 bores — tell me the number and re-exporting both plates takes a couple of minutes.

## The plates

| Plate | Parts | Footprint | Tallest | Solid | Support | Status |
| --- | --- | --- | ---: | ---: | ---: | --- |
| **1** | Coupon A | 62 x 17 | 10 | 5.2 cm3 | 0 | **the gate** |
| **2** | Mast base, antenna post, power shield | 138 x 28 | 73 | 22.2 cm3 | 1180 mm2 | ready, not gated |
| **3** | Side rail L + R | 102 x 133 | 12 | 54.6 cm3 | 640 mm2 | **after the coupon** |
| **4** | Upper deck | 85 x 140 | 14 | 50.3 cm3 | 0 | **after the coupon** |
| **5** | Mast tube | 20 x 20 | 114 | 22.2 cm3 | 65 mm2 | optional — read below |
| **6** | Driver mounts L + R | 123 x 52 | 72 | 63.6 cm3 | 1876 mm2 | blocked — read below |

"Solid" is the true material volume; Orca's own estimate after infill is the number to trust.
For scale, 100% solid in PLA would be about 6.5 g for plate 1 and 68 g for plate 3.

## Orientation, plate by plate

Each file is already rotated and dropped onto Z=0. **Do not re-orient them in Orca** — just drop
them on the plate.

**Plate 2 — mast base, antenna post, power shield**

- **Mast base**, upside down, spigot pointing **up**. This keeps the Ø13.8 spigot and the Ø20.4
  mast socket coaxial with the build direction so they stay round, and it puts the deck-mating
  face upward where nothing scars it. The cost is that only the Ø26/Ø20.4 collar ring touches
  the bed — 204 mm2. **Brim.** The collar itself acts as a pillar holding the plate up, so the
  878 mm2 of support is only the plate's outer area and it lands on the non-critical top face.
- **Antenna post**, on its front face — the flat the SMA nut tightens against. The best print in
  the whole set: 639 mm2 on the bed, 21 mm2 of support, and the Ø6.5 SMA bore prints vertically
  so it stays round for the bulkhead.
- **Power shield**, on its side, 73 tall on a 47 x 24 footprint. **Brim.** Flat-down would need
  9x the support.

One caution on this plate: above 25 mm only the power shield is still printing, so the layers get
very short. Turn on a minimum layer time / "slow down for short layers" or it will not cool.
If you would rather not risk it, the power shield is fine on its own plate.

**Plate 3 — side rails.** Each rail lies on its **outboard** face, so the wire raceway opens
upward and needs no support. 320 mm2 each, 12 mm tall.

The known trade-off (unchanged): laid this way the three M3 insert bores lie *in* the layer plane
rather than across it, and a heat-set insert expanding sideways can wedge layers apart. There is
6 mm of material around each bore and PETG bonds well between layers. If an insert does split a
rail, reprint that one standing up.

**Plate 4 — upper deck.** Flat, bosses and mast collar up, **zero support**. The face on the bed
is the face that mates with the rail tops, which is the flattest surface a printer produces.
85 x 140 is the largest footprint in the set and still fits fine.

**Plate 5 — mast tube.** Prints vertically, which is the only sane orientation for a Ø20/Ø12
tube — but that puts the layer lines perpendicular to the bending load a sensor head applies,
which is the weakest possible arrangement. A mast that fails will fail at a layer line.

The design already treats the mast as a removable, standardised part, and its only features
(wire window, cross-pin hole, index flat) are easy to drill and file. **A bought Ø20/Ø12
aluminium or carbon tube is the better long-term answer.** Print this one if you want the
assembly complete for fit-checking; don't treat it as final.

**Plate 6 — driver mounts. Do not print these yet.** They carry 2.7 mm self-tap pilot holes on a
39.5 x 39.5 pattern that has never been checked against a real BTS7960 board. They are also the
most expensive plate in the set (64 cm3, 1876 mm2 of support, 72 mm tall). Offer up an actual
driver board to the hole pattern first — if the pattern is wrong, this is the plate you least
want to have printed twice.

## Fixed while preparing this

The file previously sitting in the incoming folder as
`Gladiator_SideRail_L_print-on-outboard-face.stl` **was laid on its inboard face**, not its
outboard face — raceway opening downward, 1448 mm2 of support instead of 320. The old exporter
chose between the two candidate rotations by testing whether the result was 12 mm tall; both
rotations pass that test, and it took the first one. The bounding box was identical either way,
so nothing downstream could have caught it.

That file is now renamed `SUPERSEDED_DO-NOT-SLICE_wrong-face-down_SideRail_L.stl`. It can be
deleted, it is only still there because deleting things is your call.

The exporter now names the direction that must end up facing the bed and computes the rotation
from it, then **asserts the resulting bed-contact area matches the intended face** — the outboard
face is 3350 mm2 and the inboard face 2089, so that check cannot pass on the wrong one.

## Checked and found fine

- **The mast base is solid through the middle** — 11.5 mm of plastic on the bore axis. That is
  correct, not a missing wire path: the wires enter through the tube's side window at Z 24–36,
  which sits in the open air between the aluminium deck and the upper deck.
- Every round feature survived the export. The coupon's four bores measure 3.9997 / 4.1997 /
  4.3997 / 4.5997 against nominals of 4.0 / 4.2 / 4.4 / 4.6 — 0.0003 mm undersize, versus the
  0.200 mm a default-deflection export would have produced.

## Material

PLA for this batch is sensible for fit-checking, with the usual caveats: heat-set inserts run
around 200 C in PLA rather than 240–250, and PLA softens near 60 C, which is exactly why the
rails and deck specify PETG — they sit near the drivers and the battery. **Re-run the coupon when
you switch to PETG**; PETG shrinks more, so the winning bore may well be one size up.
