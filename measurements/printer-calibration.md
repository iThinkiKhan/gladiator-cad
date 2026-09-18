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

### Outside features

| Feature | Nominal | Measured | Error |
| --- | ---: | ---: | ---: |
| Insert boss OD (largest-bore boss) | 9.00 | 8.75 | **-0.25** |
| Insert boss OD (next boss down) | 9.00 | 8.75 | **-0.25** |
| Spigot peg, largest | 14.00 | 13.8 | **-0.20** |
| Spigot peg, middle | 13.80 | 13.5 | **-0.30** |
| Spigot peg, smallest | 13.60 | 13.3 | **-0.30** |

### Inside features

| Feature | Nominal | Measured | Error |
| --- | ---: | ---: | ---: |
| Insert bore, largest | 4.60 | 4.4 | -0.20 |
| Insert bore, next down | 4.40 | 4.0 | -0.40 |

## What this says

**Outside features come out about 0.25 mm UNDERSIZE, consistently.** Five independent
measurements, all between -0.20 and -0.30, mean -0.26.

That is backwards from the normal case. A typical printer runs outside features *over* nominal,
because the extruded bead squashes outward past the toolpath. Getting them under means the machine
is laying down less material than the slicer believes.

**A constant offset fits the data better than a scale error.** Against a constant -0.26:
predicted 8.74 / 13.74 / 13.54 / 13.34 versus measured 8.75 / 13.8 / 13.5 / 13.3. Against a
0.978 scale factor the 14.00 peg should have measured 13.69, and it measured 13.8. So this reads
as a contour/flow offset, not steps-per-mm.

**The one measurement that would settle it is missing:** the plate outline, nominal 88.00 x 62.00.
A scale error puts that at about 85.6; a constant offset puts it at about 87.75. Those are 2 mm
apart and impossible to confuse. Worth taking before changing anything.

**Under-extrusion is ruled out** as the sole cause: under-extrusion makes holes come out *larger*,
and the holes here are smaller.

### One reading to re-check

The two bore measurements disagree with each other. Their nominals are 0.2 apart; the readings are
0.4 apart:

- 4.60 nominal -> 4.4 measured (-0.20)
- 4.40 nominal -> 4.0 measured (-0.40)

One of those is probably a measurement artefact. Caliper inside-jaws in a 7.5 mm deep blind bore
is an awkward measurement at the best of times. **Pin gauges or clean drill shanks would be far
more trustworthy here than calipers.** Until then, treat the hole error as "somewhere between 0.2
and 0.4 under" rather than a single known number.

## Where this bites the current design

Every one of these follows from the numbers above, not from a new opinion about the parts.

| Part | Feature | Nominal | Will print about | Consequence |
| --- | --- | ---: | ---: | --- |
| Antenna post | SMA bulkhead bore | 6.50 | 6.10 - 6.30 | **Will not pass the connector.** SMA thread major diameter is 6.35. |
| Mast base | Spigot into the deck's 14.0 hole | 13.80 | 13.55 | **0.45 of slop** on the mast's primary structural bearing, against 0.20 intended. |
| Rails, upper deck | M3 insert bores | 4.40 | 4.00 - 4.20 | Effectively one to two sizes down from intent. Resolved by the insert test, not by calipers. |
| Mast base, upper deck | Mast socket / collar bore | 20.40 | 20.20 | Fine. Tube prints ~19.75, so clearance lands at ~0.45 against 0.40 intended. |
| Rails, deck | M3 / M2 clearance holes | 3.40 / 2.40 | 3.20 / 2.20 | Fine, screws still pass. |
| Power shield | M2 holes | 2.40 | 2.20 | Fine. |

### A useful coincidence

The **4.6 boss physically measures 4.4** — which is exactly what the design wanted the 4.4 bore to
be. Likewise the **14.0 peg physically measures 13.8**, exactly the mast base's intended spigot.
So if the insert test crowns the 4.6 boss, and the 14.0 peg is the one that fits the real aluminium
hole, the correct response is to move the *nominals* up one step and let the printer's offset land
them on target.

## Recommendation: fix the printer before changing the CAD

A 0.25 mm outside-feature error on a new machine is a calibration problem, not a design input.
Compensating for it in the model would bake today's miscalibration into the geometry permanently,
and then correcting the printer later would break every part at once.

Check, roughly in this order: flow rate / extrusion multiplier, E-steps, the filament diameter
setting in the profile, and any horizontal expansion or X-Y size compensation carrying a negative
value in the `EnderNeo` profile.

The exception is anything that must fit hardware that cannot be adjusted — the aluminium deck's
14.0 hole and the SMA connector's 6.35 thread. Those two are worth a nominal change regardless,
because they have to work with the printer as it is on the day.

## Still outstanding from this coupon

- Plate outline **88.00 x 62.00** and thickness **4.00** — the decisive scale-vs-offset measurement.
- The 4.00 and 4.20 bores (only the two largest were measured).
- M3 clearance holes 3.20 / 3.40 / 3.60 and M2 2.20 / 2.40 / 2.60.
- The rail foot slot: does an M3 screw pass and slide the full 3.0 of travel.
- **The heat-set insert test.** This is the one that gates the rails and the upper deck, and no
  caliper reading substitutes for it — the question is which boss takes an insert square and flush
  without splitting, not what the bore measures.

## Standing note on PLA

Building in PLA is a deliberate choice (Jim, 2026-09-18) and these numbers are PLA numbers. Two
things that follow, recorded so they are not rediscovered later:

- **PETG will not inherit this calibration.** PETG shrinks more; holes come out tighter still. When
  the move happens, re-run coupon A in PETG before committing real parts.
- **PLA softens near 60 C.** The rails and upper deck sit near the motor drivers and the battery,
  which is why the design originally specified PETG. Accepted as a known trade-off for the
  prototype; it is not a reason to stop, but it is a reason not to treat these as final parts.
