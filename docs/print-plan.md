# Print plan — body and mast

Prepared 2026-09-17; rebuilt 2026-09-18 as actual arranged plates after the first coupon results.

## Live queue (2026-09-21)

### Driver v5 print prep (2026-09-21)

The old Plate D/G driver parts are the superseded one-piece mount. Do not print
those for the current design. The v5 tongue-and-groove mount has its own queue:

1. `Gladiator_DriverV5_INTERLOCK-FIT-COUPON.3mf` — run first; no supports.
   The exact 4.00 mm tongue / 4.40 x 4.20 mm groove reproduces the model's
   untested 0.20 mm clearance.
2. `Gladiator_PlateI_DRIVER-V5-INTERLOCK.3mf` — left/right bases and wedges.
   Use PLA, 0.20 mm layers, 4 walls, 30% infill, 5 mm brim, and automatic
   normal supports from the build plate only. Do not auto-orient.

The bases print deck-face-down. OrcaSlicer 2.4.2 selected a full end face for
the wedges; this leaves the standoff pockets accessible and supports the
horizontal bosses. Plate I is the current driver-mount plate.

The printer's incoming folder now holds the **v5 fit coupon and Plate I**. The
older body/mast/coupon plates remain in the printer library; Plate D/G's driver
geometry is superseded. Nothing was deleted by this v5 print-prep pass.

| Plate | State |
| --- | --- |
| **I** v5 driver bases + wedges | live — print only after the v5 interlock coupon fits |
| Driver v5 interlock coupon | live — print first |
| B mast base, power shield, antenna post | library |
| D/G old driver mounts | superseded by v5 Plate I |
| F all remaining coupons | library |
| A body (rails + upper deck) | printed 2026-09-18 |
| C mast tube | not queued — buy a 20/12 tube instead |
| E coupons | superseded by F |

**Plate F = plate E, minus coupon C, plus coupon D.** Coupon C tested self-tapping
pilots and became obsolete when Jim settled on nuts and washers; coupon D was
committed two minutes after plate E was built, so plate E never carried it. The head
coupons are lifted out of plate E unchanged, so they stay byte-identical to what
`build_coupon_plate.py` produced — `build_plate_f.py` only re-packs the bed.

**Run F before B.** Coupon D settles the antenna's SMA bore, which is the last
guessed dimension on plate B.

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

## Plate D — driver mounts

**Unblocked 2026-09-20.** The board interface is measured and closed, and both gates below are
resolved. Recorded here for the reasoning trail.

**Hardware it needs: M3 x 18-20, with a nut and washer behind the frame.** The holes are 3.6
clearance, not self-tapping pilots — Jim has no self-tappers, and a heat-set insert would leave
only 1.21 of wall against the heatsink where the coupon's working boss had 2.2. A nut loads that
wall in compression instead. The space behind each hole is clear: a Ø12 x 10 probe finds 0.0 mm3.

**Still true, and worth knowing:** the arms sit 0.24 mm from the heatsink, in PLA, which softens
near 60 C. A fit prototype, not something to drive hard on.

It remains the most expensive plate in the set — 61 cm3, 72 mm tall, 1943 mm2 of support.

**1. Three numbers that were never measured.** The hole pitch in both directions and the heatsink
length are assumptions, not measurements; see the "Mounting interface — NOT MEASURED" block in
`measurements/components.md` for exactly what to put calipers on. Calipers only, no printing.

**2. The self-tap pilot size.** *(The pin-clearance problem is solved — the arms now carry a
2.0 deep relief across A 8.0..39.5, leaving a bearing pad at each screw. See the calibration and
components notes. This item is what remains.)* `Gladiator_CouponC_SelfTapPilots_flat.stl` — 48 x 8.5 x 6 mm,
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

## Plate E — all remaining coupons

`Gladiator_PlateE_ALL-COUPONS.3mf`, built 2026-09-20. 13 pieces, 24.5 cm3,
about 30 g. Everything left that gates a real part, on one bed.

**Turn on a brim.** Several pieces have small footprints — each belt arc has
about 100 mm2, less than the mast base that already calls for one.

**Do not let Orca auto-orient.** Every piece is already on its correct face.

| Pieces | Question it answers | Marking |
| --- | --- | --- |
| 3 x belt mesh arc | Which 2GT groove width grips a real belt? | scallops on the inner face, 1 = narrowest (r 0.60 / 0.65 / 0.70) |
| 3 x bearing seat ring | Which modelled bore gives a real 32.00 bearing OD a firm seat? | notches on the rim, 1 = smallest (32.20 / 32.35 / 32.50) |
| 3 x spindle post | Which modelled post slides into a real 20.00 bearing bore without slop? | notches on the wall, 1 = smallest (20.05 / 20.20 / 20.35) |
| 1 x screen mount gauge | Is the ST7789 hole pattern really 26.00 x 58.25 centres? | — |
| 1 x coupon C | Which self-tap pilot holds an M3 without splitting? | clipped corner marks the smallest |
| GH44 blank carrier + receiver | Does the carrier interface seat, index and reject a reversed fit? | — |

### The brackets are calibration-compensated, not nominal

Round features on this printer come out about **0.25 mm under**, convex and
concave alike — see `measurements/printer-calibration.md`. So the bearing
brackets are deliberately modelled oversize:

| Piece | Modelled | Expected printed | Target |
| --- | ---: | ---: | --- |
| Seat, 1 notch | 32.20 | ~31.95 | too tight |
| Seat, 2 notches | 32.35 | ~32.10 | **the prediction** |
| Seat, 3 notches | 32.50 | ~32.25 | too loose |
| Post, 1 notch | 20.05 | ~19.80 | too loose |
| Post, 2 notches | 20.20 | ~19.95 | **the prediction** |
| Post, 3 notches | 20.35 | ~20.10 | will not enter |

If 2 notches wins on both, the curve error is still 0.25 and the numbers go
straight into v0.3. If a different one wins, that is new calibration data and
`printer-calibration.md` gets updated first.

The seat wants the bearing to press in and stay without rocking. The post wants
the bearing to slide on by hand and not wobble. Do not force either — a bearing
hammered into an undersized printed pocket will hold until the PLA creeps.

### Screen mount gauge

Hole centres are **26.00 wide x 58.25 long**, derived from Jim's two clean
inside-to-inside readings (24 and 56.25) plus the confirmed M2 hole diameter.
Holes are 2.6, the calibrated M2 clearance — 2.2 and 2.4 would not pass a screw
on this printer.

This settles the disagreement in the raw readings physically instead of by
argument: lay the board on the gauge and see whether four M2 screws drop
through. If they do, the pattern is confirmed and the display frame can be cut.
If they do not, measure the offset and that is the correction.

It predicts outside-to-outside of 28.00 and 60.25, with 0.500 and 1.125 mm of
board outboard of the holes. Jim's readings of 29 and "maybe 61.5" disagree, but
the 29 was annotated as the board edge and the 61.5 was hedged; the 1.125
prediction lines up with his 1.3 reading.

### What each result unblocks

| Result | Unblocks |
| --- | ---: |
| GH44 pair | Tilt yoke, tilt receiver, dual carrier, clamp cap, the fixed head — 39 cm3 |
| Bearing seat + post | Pan rotor, retainer — 14.5 cm3 |
| Belt mesh | The pedestal — 20 cm3. Needs a real 2GT belt to test against. |
| Screen gauge | The display frame — 10.8 cm3, still also needs the active window measured |
| ~~Coupon C~~ | **Dropped from plate F 2026-09-20 — read the note below.** |

**Coupon C is off plate F, and that leaves one thing hanging.** It was carrying two jobs. The
first, the driver mount pilots, is moot: Jim has no self-tapping screws, so those became 3.6
clearance holes for nuts and washers and there is no thread to form.

The second job does not go away. **The pan rotor's M2 self-tap pilots assume self-tapping screws
that do not exist in this build.** No coupon settles that — coupon C tested M3 at 2.7 / 2.9 / 3.1
and was only ever a proxy for the M2 case. It is a design question: the pan rotor needs M2
clearance holes with nuts, or M2 heat-set inserts, or machine screws formed into plastic and
accepted as consumable. The driver mounts took the nut route because the space behind them was
clear; whether the pan rotor has that room is for the head workstream to check.

Printing coupon C now would answer a question nobody has, so it stays off the plate — flagged
here rather than quietly dropped.
