# Coupon M2-A: M2 heat-set insert bores (2026-10-21, Claude)

Jim 2026-10-21: M2 heat-set inserts in every print from now on. This coupon finds the bore for them on this printer, as coupon A did for M3 (4.6 won).
Built by `build_coupon_m2_inserts.py`. Plate: `cad/v2/print-plates/Gladiator_COUPON-M2_Insert_Bores_upright-and-sideways.3mf` (48 min, 11 g, plate down, no supports).

* **Front row, upright** (bore axis vertical, in 7 mm bosses): how a boss that prints standing up takes an insert.
* **Back wall, sideways** (bore axis horizontal, from the back face): how a bore that prints lying down takes one; its top is a bridge, exactly as in the INA bosses and the switch holder side screws.
* **Bores, LEFT to RIGHT in both rows: 2.8, 3.0, 3.2, 3.4, 3.6, 3.8 mm** nominal. The clipped corner is at the 2.8 end (front left). All 6.0 mm deep, so 3, 4 or 5 mm long inserts fit.
* Expect round holes to print about 0.25 small (measurements/printer-calibration.md), so a 3.6 nominal comes out near 3.35.

## How to read it
Set an insert in each bore at about 200 C (PLA), letting it sink under its own weight. The winner is the smallest bore where the insert goes in flush without bulging the boss
or the wall, and does not pull out with a screw threaded in. Check the sideways row separately: the bridged top of a horizontal bore usually sags, so it may want a bigger bore.
Record the winners (upright and sideways) in measurements/printer-calibration.md; every part with M2 inserts then gets that bore and a depth of insert length + 0.5 to 1 mm.

## Unknown
The insert's outside diameter and length (send the listing or caliper one): they set the depth and confirm the range covers it.
