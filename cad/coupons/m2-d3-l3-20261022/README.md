# M2 x D3 x L3 heat-set fit coupon — 2026-10-22

Open **M2_D3_L3_Coupon_EnderNeo_PLA.3mf** in OrcaSlicer, or import the STL at 100% scale, flat base down. The supplied project uses the existing EnderNeo PLA profile, 220 x 220 mm bed, 0.20 mm layers, four walls, four top/bottom layers, 25% infill, no supports and no brim. Review the sliced paths before printing. No printer job is started by this package.

## Hardware basis

Jim's supplied listing screenshot says **M2 x D3 x L3 (100 pcs)**: nominal M2 internal thread, 3 mm outside diameter, 3 mm insert length. These are listing dimensions, not caliper measurements. Check the knurled maximum OD and length of several delivered inserts before testing. Other listing fields (including 2 mm item diameter and 2.2 mm compatible groove) conflict or describe different features; they are not the pilot bore specification.

The old M2-A coupon had 2.8–3.8 mm bores in 0.2 mm steps and 6 mm depth because the insert dimensions were unknown. This separate version narrows the step to 0.1 mm and uses the supplied 3 mm length. Existing coupons and project parts remain preserved.

## Read the coupon

- Envelope: **80 x 25 x 9.9 mm**, including raised labels.
- **Upright bosses:** holes open from above, vertical during printing.
- **Back wall:** holes enter from the outer rear face, horizontal during printing. The matching size is marked on top of the wall, directly above each hole. When looking directly at the rear face, the order appears reversed; use the labels.
- Both sets have **2.60, 2.70, 2.80, 2.90, 3.00, 3.10, 3.20, 3.30 mm CAD bore diameters**. Labels show one decimal. The clipped front corner identifies the 2.60 end.
- All bores are **3.60 mm blind depth**, with a **0.15 mm radial x 0.15 mm axial 45-degree entry chamfer**. Cylindrical land: 3.45 mm. A flush 3 mm insert has 0.60 mm nominal space below it for displaced plastic.
- Upright bosses: 7 mm OD, 6 mm total height, 2.40 mm floor. Horizontal wall: 6 mm thick, 2.40 mm material behind each blind bore. Smallest radial upright wall is 1.85 mm; horizontal roof above the straight largest bore is 2.35 mm.

The printer log records undersize printed circles, but the actual error for these small bores and this orientation must be determined here. No extra diameter correction is applied to the printed labels. Avoid adding new slicer hole compensation during this test unless it will also be used on the project parts; record any changes.

## Test and choose the fit

1. Use the same filament, profile, orientation, layer height and wall settings planned for the real part. The existing project baseline is PLA. Re-test for another material or a changed profile.
2. Let the coupon cool and remove it from the bed. Leave the bore walls as printed; drilling or reaming would test a different process.
3. Try a cold insert at 3.00 mm first. A hole that lets the whole insert drop in freely is too loose for this test. Move smaller or larger as needed; there is no need to consume all 16 inserts. Keep unused neighboring holes cool while testing.
4. Support the coupon on a firm surface with the test hole pointing upward during installation, including the sideways holes after rotating the cooled coupon. Keep the iron aligned with the bore. Use the insert supplier's temperature guidance for PLA; the existing project log used about 200 C as a starting point. Log the actual setting and use consistent dwell and light pressure. If excessive force is needed, stop and try the next larger bore.
5. Seat the insert flush, then remove the iron and allow it to cool completely without moving it. Reject holes that bulge, crack, separate layers, or leave the insert tilted. Do not continue forcing an undersized hole.
6. Fit an M2 screw with roughly 2 mm of engagement into the insert, keeping its tip clear of the blind floor. Check for spinning and pullout under the intended service load, using a consistent method. A hand check does not establish a rated joint strength. Record the observations in **results.csv**.
7. Choose the **smallest bore that installs cleanly and remains secure after cooling**, separately for vertical and horizontal print orientations. Reprint the coupon to confirm the candidate and adjacent size with fresh inserts before changing repeated project features. If no size passes, extend the range rather than forcing a winner.

## Carrying the result into projects

Record the winning **CAD diameter**, insert batch dimensions, material, slicer hole compensation, installation temperature, and print orientation in the printer-calibration log. A good vertical result does not establish the horizontal bore size. Preserve the tested 3.60 mm blind depth and entry geometry where the actual part permits it; check screw engagement, wall/floor thickness, tool access and loads on each part. A narrower boss or thinner wall needs its own confirmation. Longer screws may need a deeper relief beyond the insert.

The native FreeCAD file contains the coupon solid and dimension metadata. **build_coupon.py** is the editable geometric source; rebuild after changing values. Metadata fields on the saved solid are descriptive and do not regenerate its shape by themselves. STEP is included for reuse in other CAD tools.

## Validation

See validation.json, saved-file-verification.json and plate-validation.json. Checks cover one valid CAD solid, native/STEP reopen, all 16 unobstructed bores with closed blind ends, solid manifold STL, and 3MF mesh agreement with the STL. Physical installation, repeatability and joint strength remain to be measured.

OrcaSlicer 2.4.2 validation slice succeeded without warnings. Slicer statistics:

```
; filament used [mm] = 3079.43
; filament used [cm3] = 7.41
; filament used [g] = 9.18
; total filament used [g] = 9.18
; total filament cost = 0.18
; estimated printing time (normal mode) = 43m 43s
```
