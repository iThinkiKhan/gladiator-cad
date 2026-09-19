# Print plan — body and mast

Prepared 2026-09-17; rebuilt 2026-09-18 as actual arranged plates after the first coupon results.

## The plates

Four 3MF files in `/home/buralien/Desktop/3D-Printer-Incoming/`. **Each one is a complete build
plate with the parts already laid out** — open it in Orca, check the settings noted below, slice.
No arranging, no re-orienting. Every part is already rotated onto its correct face and sitting on
the bed.

| File | Contains | Group size | Tallest | Solid | Status |
| --- | --- | --- | ---: | ---: | --- |
| `Gladiator_PlateA_BODY_rails-and-upper-deck.3mf` | Upper deck + both side rails | 193 x 140 | 14 | 105 cm3 | **ready** |
| `Gladiator_PlateB_MAST-AND-FITTINGS.3mf` | Mast base, power shield, antenna post | 134 x 28 | 73 | 22 cm3 | **ready** |
| `Gladiator_PlateC_MAST-TUBE.3mf` | Mast tube alone | 20 x 20 | 114 | 22 cm3 | ready, but read the note |
| `Gladiator_PlateD_DRIVER-MOUNTS_BLOCKED.3mf` | Both driver mounts | 121 x 52 | 72 | 64 cm3 | **do not print yet** |

Bed is 220 x 220, and every plate is centred on it with 8 mm between parts and at least 10 mm of
edge margin. Checked pair by pair for overlap, not assumed.

The individual per-part STLs are still in the same folder (`Gladiator_P*.stl`) for reprinting one
part or building a different combination. The plates above are the normal path.

## Plate A — the body

**This is the one that gets you a chassis.** Both rails and the upper deck fit together with room
to spare, and it is the lowest-risk plate in the set: everything is under 15 mm tall, the deck has
11126 mm2 of bed contact and each rail 3350 mm2, and total support is 647 mm2 across all three.

- Upper deck: flat, bosses and mast collar up, **zero support**. The face on the bed is the one
  that mates with the rail tops.
- Both rails: **outboard face down**, so the wire raceway opens upward and needs no support.

Known trade-off, unchanged: laid this way the rails' insert bores lie *in* the layer plane, and a
heat-set insert expanding sideways can wedge layers apart. There is 6 mm of material around each
bore. If one splits, reprint that rail standing up.

## Plate B — mast base, power shield, antenna post

**Turn on a brim** — the mast base sits on a thin Ø26/Ø20.4 ring (181 mm2) and the power shield is
73 mm tall on a 47 x 24 footprint (252 mm2). Both want the extra grip.

**Turn on a minimum layer time / slow-down-for-short-layers.** Above 25 mm only the power shield is
still printing, and its layers are small enough to cook without it.

- Mast base: upside down, spigot pointing up, so the Ø14.0 spigot and Ø20.4 socket stay coaxial
  with the build direction and print round, and the deck-mating face ends up on top where nothing
  scars it.
- Antenna post: on its front face — the flat the SMA nut tightens against. The best print in the
  set, 21 mm2 of support.
- Power shield: on its side. Flat-down would need nine times the support.

## Plate C — mast tube

Vertical is the only sane orientation for a Ø20/Ø12 tube, but it puts the layer lines perpendicular
to exactly the bending load a sensor head applies. A mast that fails will fail at a layer line.

**A bought Ø20/Ø12 aluminium or carbon tube is the better answer.** The design already treats the
mast as a removable, standardised part and its only features (wire window, cross-pin hole, index
flat) are easy to drill and file. Print this if you want the assembly complete for fit-checking;
do not treat it as final. Needs a brim.

## Plate D — driver mounts. Not yet.

The most expensive plate in the set — 64 cm3, 72 mm tall, 1875 mm2 of support — and the one
whose interface is least verified. Two separate things gate it.

**1. Three numbers that were never measured.** The hole pitch in both directions and the heatsink
length are assumptions, not measurements; see the "Mounting interface — NOT MEASURED" block in
`measurements/components.md` for exactly what to put calipers on. Calipers only, no printing.

**2. The self-tap pilot size.** `Gladiator_CouponC_SelfTapPilots_flat.stl` — 48 x 8.5 x 6 mm,
about 2.7 g, prints flat with no support. It reproduces the real arm: 8.5 wide, the hole offset so
the thin wall is 2.15, 12 mm of axial depth, and the holes canted 30 degrees from the bed to match
how the layers will actually run across the screw in the printed part. A flat bar with vertical
holes would be the easy case and would flatter the result.

Three pilots, 2.7 / 2.9 / 3.1 nominal, which on this printer land near 2.45 / 2.65 / 2.85. An M3
self-tapper in PLA generally wants 2.5-2.6, so the current 2.7 design value is probably one step
small. The clipped corner marks the smallest.

Drive an M3 self-tapper into each and look for the one that forms a thread and holds without
splitting the 2.15 wall or stripping.

**A caution on updating the pattern afterwards.** `drv_hole_pitch` exists in the spreadsheet but
drives nothing — the four hole centres are literal coordinates in `DrvHoleSketch`. An attempt to
bind them was backed out: the expression evaluates and moves the sketch, but the change does not
propagate to the body's solid reliably in headless FreeCAD, and a half-working binding is worse
than an obvious literal. When the measurements arrive the pattern gets updated by rebuilding that
sketch in a script, with the resulting solid verified — not by editing a cell.

## Settings that apply to all of them

- **PLA**, per the current build decision. Heat-set inserts want about 200 C in PLA, not the
  240-250 used for PETG, and should sink under their own weight rather than being pushed.
- **First-layer squish / elephant-foot compensation is worth setting properly.** The bores that
  start on the bed now carry a 0.35 mm entrance relief so a lip cannot pinch them, but that relief
  is insurance, not a substitute — the lip affects the bed face of every part.
- Every part is already oriented. **Do not let Orca auto-orient them.**

## If Orca re-centres the plate on import

The positions are written into the 3MF, and the relative arrangement is what matters. If Orca
shifts the group as a whole, the layout is still correct; one press of Arrange gives an equivalent
result.

## What was verified before these files were written

Each part: single closed solid, manifold, no self-intersections, sitting on Z=0, mesh volume
matching CAD to within 0.5%, and **the intended face verifiably the one on the bed** — that last
check exists because an earlier export silently laid a rail on its inboard face while naming the
file for the outboard one.

Each plate: every pair of footprints tested for overlap, every part tested against the bed
envelope, and each 3MF re-opened afterwards to confirm the container, the millimetre unit, the
object count and that every triangle index is in range.

Mesh tessellation is 0.01 mm throughout. At FreeCAD's 0.1 default every round feature comes out
about 0.2 mm undersize, which is a whole step of the coupon's bore sizes; at 0.01 the exported
holes measure within 0.0003 mm.

## Current part sizes

These are calibration-compensated for this printer — see `measurements/printer-calibration.md`.

| | Value |
| --- | ---: |
| Insert bores (16) | 4.6 |
| M3 clearance (14) | 3.6 |
| M2 clearance (4) | 2.6 |
| Mast spigot | 14.0 |
| SMA bore | 6.75 — **estimated, untested** |
| Rail foot slot | 3.4, confirmed by test |
| Bed-face entrance relief | 0.35 at 45 degrees |

The SMA bore is the one number nothing tested. If the connector will not pass, run a 6.5 mm drill
through it; nothing else on that part depends on it.
