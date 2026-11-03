# Camera case v4 - plug clip test coupon (2026-11-01)

Jim: "im not sure about these retention clips, lets get a coupon ready to test". STL only, staged in
~/3D-Printer/Incoming/Gladiator_CameraClipCoupon_20261101/ (START_HERE.txt there has the test steps).

| Part | What |
|---|---|
| 01 / 02 / 03 clips | v4 clip with pocket 2.56 / 2.66 / 2.76 mm (wall thickness unchanged), 1 / 2 / 3 notches on the top edge. 02 is identical to the v4 clip (checked). |
| 04 tray coupon | v4 tray cut to floor 1.2 mm + 19.66 mm to the board seats + 0.6 mm lip; keeps the 5 backstop pads, 4 corner seats and the open wire exits; lugs, inserts and snap bumps removed. 5878 mm3 (tray 10906). |

Checks (coupon_checks.json): board, plugs, wires and clips clear of 04; clip to pads 0.4 mm; 4 seat faces at the
board back plane; STLs watertight, on z = 0. Not printed. Clip outer wall 0.67 mm (0.37 mm over 0.35 mm at the pocket
ends) - check it survives slicing.

Rebuild from the repo root (about 3 min; rebuilds v4 into /tmp, v4 files untouched):

    QT_QPA_PLATFORM=offscreen freecadcmd -c "exec(open(\"cad/head/camera-service-v4-20261031/clip-coupon-20261101/build_clip_coupon.py\").read())"
    (cd cad/head/camera-service-v4-20261031/clip-coupon-20261101 && xvfb-run -a freecad coupon_views.py && python3 coupon_sheet.py)
