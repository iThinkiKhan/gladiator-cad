# 60T SG90 cross-horn fit coupon

This is a **small unpowered fit piece** for the next pan-drive candidate. It is not a replacement for the v0.3 head or a released moving mechanism.

## Print

Open `Drive60_HornSlot_Fit_Coupon_print-flat.stl`. The part is already flat, 40.09 mm across the flanges and 7.4 mm tall. Print with its axis vertical, no supports, using the same PLA, 0.4 mm nozzle, and tooth-detail settings that made Jim's two-notch belt coupon fit. The bed-facing area is about 1,145 mm². A brim is optional if adhesion needs it.

The model has 60 teeth, a 6 mm belt channel, and the accepted 0.65 mm groove radius / 0.75 mm groove depth. It has four radial 2.6 mm wide M2 clearance slots whose centerlines run from 7 to 14 mm radius. Jim reports five holes on each arm of the available cross horn, and a 17 mm center-to-long-tip distance. The horn-hole locations themselves are not modeled as fixed coordinates.

## Unpowered check

1. Seat the actual cross horn flat under the pulley, with the original servo-spline horn and center screw retained.
2. Check that at least one hole in each of two opposite arms lies within its radial slot. Check whether an M2 screw passes the selected horn holes and whether its head and any nut clear the servo case.
3. Confirm a screwdriver and the original horn-retaining screw can pass through the 5.5 mm center access hole.
4. Fit the delivered GT2 belt around the whole pulley. Confirm tooth seating and that the flanges do not pinch the 6 mm belt.

Record the actual arm-hole choice, screw/nut arrangement, and any interference. A fit here supports the horn interface only. The driven pulley, corrected ratio, exact belt center distance, tension adjustment, and installed collision/sweep checks remain separate gates.

## Evidence

`validation.json` records dimensions and solid/mesh checks. The saved FreeCAD and STEP files are included for inspection. `preview-section.png` shows a horizontal cut through the tooth channel and mounting slots. Source: `scripts/build_head_drive_coupon.py` on the CAD server; local copy in `tools/cad_head_work/`.
