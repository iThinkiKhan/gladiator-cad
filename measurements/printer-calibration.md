# Printer calibration log

**This is the authoritative record of how the printer actually prints.** Anything in the CAD that
depends on a real-world fit should be checked against this file before it is committed to.

| | |
| --- | --- |
| Machine | Ender-3 Neo, 220 x 220 x 250, 0.4 nozzle (the `EnderNeo` Orca profile, OctoPrint at 192.168.0.30) |
| Material | **PLA**, and PLA until a deliberate, calculated move to PETG (Jim, 2026-09-18) |
| Slicer | OrcaSlicer 2.4.2 |

## Round 1 — fit coupon v2, measured 2026-09-18

First real-world test on this printer. Source geometry: `cad/coupons/Gladiator_FitCoupon_v2.FCStd`,
exported at 0.01 mm deflection, so the STL is true to the CAD within 0.0003 mm and contributes
nothing to the errors below.

### Flat outside walls — slightly OVER

| Feature | Nominal | Measured | Error |
| --- | ---: | ---: | ---: |
| Plate length | 88.00 | 88.25 | **+0.25** |
| Plate width | 62.00 | 62.10 | **+0.10** |

### Round features — consistently UNDER, inside and outside alike

| Feature | Kind | Nominal | Measured | Error |
| --- | --- | ---: | ---: | ---: |
| Insert boss OD | outside | 9.00 | 8.75 | -0.25 |
| Insert boss OD | outside | 9.00 | 8.75 | -0.25 |
| Spigot peg, largest | outside | 14.00 | 13.8 | -0.20 |
| Spigot peg, middle | outside | 13.80 | 13.5 | -0.30 |
| Spigot peg, smallest | outside | 13.60 | 13.3 | -0.30 |
| Insert bore, largest | inside | 4.60 | 4.4 | -0.20 |
| Insert bore, next down | inside | 4.40 | 4.0 | -0.40 |

### Fit results

| Test | Result |
| --- | --- |
| Heat-set insert | **4.6 bore wins.** Pulled in totally flush, and could not be pulled back out with a screw threaded in. |
| M3 clearance hole | **3.6 wins.** 3.2 and 3.4 would not pass a screw. |
| M2 clearance hole | **2.6 wins.** 2.2 and 2.4 would not pass. |
| All clearance holes | Even the winners need the screw **turned** to get through the very bottom — first layer only. |
| Rail foot slot (3.4 wide) | **Good as-is.** Takes an M3 comfortably, would take an M2 with a washer. No change wanted. |
| Spigot peg in the real deck hole | **14.0 wins.** Turns easily, little to no jiggle in the aluminium Ø14. |

## The diagnosis

**It is not a scale error and it is not a flow problem. Round features specifically print small.**

Flat walls run slightly *over* (+0.10 to +0.25), which is the ordinary result of the bead squashing
outward past the toolpath. Every curved feature runs about 0.25 *under*, and — this is the
diagnostic part — **it does not matter whether the curve is convex or concave.** Outside circles
and holes are both small by roughly the same amount.

That rules out the two obvious suspects. A scale error would have put the 88.00 plate at about
85.6; it measured 88.25. Under-extrusion would have made the holes come out *larger*, not smaller.

**The rail slot is the clincher.** It is 3.4 wide, the same nominal as the M3 round holes that
would not pass a screw — and it takes an M3 comfortably. Same size, same plate, same layer. The
only difference is that the slot has flat walls and the hole has curved ones.

What that points to is the toolpath under-shooting on curves: slicer arc approximation plus
corner-cutting from acceleration and junction deviation. On a convex circle that lands the bead
inside the intended contour and the peg comes out small; on a hole it lands the bead further into
the opening and the hole comes out small too. One mechanism, both signs.

Worth trying, in rough order: lower outer-wall acceleration and jerk/junction deviation, tighten
Orca's arc-fitting tolerance, and check belt tension. This is a tuning problem, not a fact of life
— 0.25 mm is large for a curve error.

**Separately, the first layer pinches every hole.** Screws pass the winning sizes but need turning
at the very bottom. That is elephant's foot, and it is a different fix: first-layer z-offset or
squish, or Orca's elephant-foot compensation. Worth doing regardless, because it affects every
part's bed face.

## What was changed in the CAD, 2026-09-18

The tested values were applied to the master. These are **calibration-compensated numbers for this
printer as it prints today**, not changes of design intent — if the curve error is tuned out, they
should be revisited together.

| Parameter | Was | Now | Basis |
| --- | ---: | ---: | --- |
| `rail_insert_dia` | 4.4 | **4.6** | insert test, all 16 bores |
| `deck2_screw_dia` | 3.4 | **3.6** | M3 clearance test, 14 holes |
| `mast_pin_dia` | 3.4 | **3.6** | M3 clearance test |
| `m2_screw_dia` | *(none)* | **2.6** | M2 clearance test, 4 holes. New parameter — there wasn't one. |
| `mast_spigot_dia` | 13.8 | **14.0** | peg fit in the real aluminium hole |
| `ant_sma_dia` | 6.5 | **6.75** | **ESTIMATED, NOT TESTED** — see below |
| `rail_slot_width` | 3.4 | **3.4** | unchanged, confirmed good by test |

Design intent behind those numbers, for whoever tunes the printer later: the insert bore is meant
to be a physical 4.4, the M3 clearance a physical 3.4, the M2 a physical 2.4, and the spigot a
physical 13.8. Every compensated value is intent + 0.2 rounded to the coupon's step.

### Holes were NOT opened up for the first-layer snag

The screws pass the winning sizes and snag only at the very bottom. That is elephant's foot, not a
diameter problem, so opening the holes further would have made every mounting hole sloppy to fix a
lip that only exists on one layer (Jim's call, 2026-09-18).

Instead the bed-facing entrance gets a **0.35 mm 45 degree relief** (`hole_entry_chamfer`, a new
parameter). It removes the lip without touching the working diameter, and doubles as a lead-in.

Checked against each part's real print orientation rather than assumed — **only two parts have any
bore entering at the bed:**

| Part | Relieved | Why the others are not |
| --- | --- | --- |
| Upper deck | 6 x M3 clearance (3.6) and the 20.4 mast bore, at the Z=48 bed face | — |
| Mast base | the 20.4 mast socket, at the Z=20 collar top, which is its bed face | — |
| Side rails | nothing | prints on its outboard face, so the insert bores run horizontal |
| Driver mounts | nothing | vertical holes, but they sit up in the air when inverted |
| Power shield, antenna post, mast tube | nothing | those holes all run horizontal in their print orientation |

**The two 20.4 mast bores were not part of the original brief.** They are included because the mast
tube has to slide into both and an elephant-foot lip sits exactly where it enters. On a fit feature
that is worse than on a screw hole, and the chamfer costs nothing.

### The one value that is a guess

`ant_sma_dia` at 6.75 targets a physical 6.5 against an SMA thread of 6.35. Nothing on the coupon
tested a hole that size, so it is an extrapolation from the 0.25 curve error. It is also the
easiest one to correct by hand: if the connector will not pass, run a 6.5 mm drill through it.

### A latent bug fixed at the same time

The fit-critical radii were **plain numbers in the sketches with no expression attached**, even
though the spreadsheet already had aliases for several of them. Changing `rail_insert_dia` would
have done nothing at all, despite the design document saying it fed all 16 bores.

**31 constraints across 13 features are now bound to the spreadsheet**, so the documented behaviour
is the real behaviour. Insert bores, M3 and M2 clearance holes, the mast pin, the SMA bore and the
mast spigot all now follow their parameter.

## Still outstanding from this coupon

- The 4.00 and 4.20 bores were not measured (the fit answer arrived before they mattered).
- The two bore readings that were taken disagree: nominals 0.2 apart, readings 0.4 apart
  (4.60 -> 4.4, but 4.40 -> 4.0). Caliper inside-jaws in a 7.5 mm deep blind bore is an awkward
  measurement; pin gauges would be better if the number is ever needed precisely. The *fit* result
  is unaffected — that came from an actual insert, not a caliper.

## Standing note on PLA

Building in PLA is a deliberate choice (Jim, 2026-09-18) and every number here is a PLA number.

- **PETG will not inherit this calibration.** PETG shrinks more; holes come out tighter still. When
  the move happens, re-run coupon A in PETG before committing real parts — and note that the
  compensated values above would need re-deriving, not just carrying over.
- **PLA softens near 60 C.** The rails and upper deck sit near the motor drivers and the battery,
  which is why the design originally specified PETG. Accepted as a known trade-off for the
  prototype; not a reason to stop, but a reason not to treat these as final parts.
- **Heat-set inserts run cooler in PLA** — around 200 C rather than 240-250. Let the insert sink
  under its own weight rather than pushing, or it will bulge the boss.
