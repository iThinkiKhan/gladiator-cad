# Head preprint review — 2026-09-22

Source reviewed: CAD server `cad/head/v03-belt/` and `scripts/build_head_v03.py`, plus the current fit notes in `measurements/mast-head.md`, `docs/print-plan.md`, and the local v0.1 head README. This is a review of the current candidate, not a manufacturing release.

## Stop: pan ratio is reversed

The modeled SG90 drive pulley has 40 teeth and the driven head pulley has 60. Belt motion requires `head_angle = servo_angle * 40/60`, not `servo_angle * 60/40` as the generator, manifest, and validation assume. Therefore:

- The requested -20° to +180° head travel (200° total) requires 300° of servo travel.
- A 0° to 180° face switch requires 270° of servo travel.
- The recorded measured 160° servo sweep would produce at most 106.7° of head travel with these pulleys, before end margins.

The generator's `RATIO`, `SERVO_TRAVEL`, and `posed(... servo ...)` calculations have the wrong physical ratio. Its servo-pose collision results and conclusion that the SG90 can turn the two-face head are therefore invalid. Correct the tooth counts/actuator and regenerate a new candidate before printing the neck, pedestal, or full moving head. Swapping to a 60T drive and 40T driven pulley would give the intended 1.5 output ratio mathematically, but its servo attachment, packaging, torque, and collision envelope need a new design and check.

## Stop: the fixed center distance does not match the belt calculation

For the modeled 60T/40T pulleys and a 180 mm pitch-length belt, the generator reports a 39.745 mm shaft spacing. The open-belt pitch-line equation gives about 39.486 mm. At 39.745 mm, the path length is about 180.512 mm. In `centre_distance()`, the code solves `C = b - k/(2*C)` although its own stated approximation gives `C = b - k/C`. There is no designed tension adjustment or measured stretch allowance, so this spacing must be corrected and physically checked with the delivered belt before a fixed-position neck is printed.

## Fit results already recorded

- Bearing seat/post coupon #2 was preferred. Plate F identifies its modeled dimensions as 32.35 mm seat and 20.20 mm post. The v0.3 head still has 32.10/19.95 mm. Elephant foot prevented full insertion on the coupon; address that at the first layer or by local cleanup, while preserving the successful mating diameters.
- The GH44 locating register fits. The male-side M3 holes do not pass a screw; the female through-holes do. The female nut pockets did not accept nuts, with print error still possible. The current full head has not incorporated those results.
- Jim physically fitted the delivered belt to the 3-up mesh coupon on 2026-09-22 and selected the arc with **two scallop/notch marks**. This is the middle profile: groove radius 0.65 mm, nominal groove depth 0.75 mm. This validates that printed tooth profile against his belt; it does not validate the pulley ratio, fixed center distance, tension, or horn attachment.
- The latest tongue-and-groove coupon fits perfectly with no geometry change requested, superseding the earlier suggestion to lower the tongue 0.20 mm. The screen mounting gauge and final active-window fit are not recorded as passing in the notes reviewed here.

## Print sequence

The #2 belt groove is selected. Jim confirms he has belts, bearings, and circlips, **but no pulley**. Both pulleys can therefore be redesigned as printed candidates; neither tooth count is locked by purchased hardware. A 60T drive / 40T head pair gives the intended 1.5 head-to-servo travel mathematically. At the same 225° servo position, the 60T drive flange would reach about 8.5 mm past the robot's left edge. The 40T driven groove root radius is about 11.73 mm while the inherited pedestal waist radius is 12 mm, so merely swapping tooth counts would partly fill the printed grooves. Jim has single-arm and cross SG90 horns; the recorded shaft-center-to-long-tip distance is **17 mm**. The v0.3 CAD instead represents the pan horn as a 9 mm radius round disk. A cross horn under a 60T drive pulley is a reasonable adapter candidate, using the supplied spline and center screw plus adjustable radial mounting slots, but actual screw-hole spacing and vertical fit still require a physical coupon. These require new geometry and checks. Next resolve drive geometry, center distance/tension, calibrated fastener holes and bearing dimensions, GH44 retention, screen fit, and a flex harness. Rebuild and verify the full assembly against the current master before releasing main head STLs and print orientations.

**2026-09-22 follow-up:** Jim reports five holes in each cross-horn arm, located somewhat toward the tip. An isolated 60T horn-slot coupon now exists under `cad/head/drive-coupons-20260922/`, with a local copy under `docs/mast-head/drive-coupons-20260922/`. Its slots span 7–14 mm radius, and its tooth profile uses the passing two-notch groove. The CAD is one valid solid, and the STL is a solid 40.09 × 40.09 × 7.4 mm mesh with about 1,145 mm² bed contact. It is for unpowered horn, screw, and belt fit; it does not release the full drive.
