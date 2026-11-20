# V2 mast control schema

The live S3 now uses the initial **angular profile from C6 revision 14**, bounded to 9° left / 7° right and 1.5° down / 2° up. The table below documents the revision 13 pulse profile retained as the commissioning baseline.

| Rev 14 axis | Low µs | Neutral µs | High µs | Shaft limits | Head limits |
| --- | --- | --- | --- | --- | --- |
| Pan (GPIO10, reversed, 1.5 ratio) | 650 | 850 | 1050 | −6.3° / +5.1° | −9° right / +7° left |
| Tilt (GPIO13) | 1300 | 1500 | 1550 | −1.8° / +2.4° | −1.5° down / +2° up |

Applied 2026-11-19 21:49 UTC; re-read from C6 and S3 on 2026-11-20 after a C6 reboot (still revision 14, calibrated, outputs off). Speed 2°/s, 50 Hz. Physical camera aiming is still to be verified. Full values: `angularProfileRevision14` in `v2-mast-control.json`.

Jim selected these installed-mast pulse points on November 19, 2026. C6 setup revision 13 and the S3 saved-position profile were verified with both servo outputs off. The matching machine-readable record is `v2-mast-control.json`. The November 9 readback preserves the previous points.

| Axis | GPIO | Lower pulse | Neutral | Higher pulse |
| --- | --- | --- | --- | --- |
| Pan | 10 | 500 µs right | 850 µs camera forward | 1500 µs left |
| Tilt | 13 | 950 µs down | 1500 µs camera level | 2000 µs up |

PWM is 50 Hz. Use the camera as the direction reference. The screen faces the opposite direction. Jim reported much better belt engagement with the new rotor and no visible harness tension during his manual checks. The camera lifts only slightly above level, so measure the usable upward angle and verify that the mechanism moves freely under load before using it as an angular limit.

The S3 enforces a bounded pulse range on each axis. Pan has no mechanical stop. Continuous rotation and modulo wrapping stay disabled. Check the physical cable position before deliberate arming after a reset or manual repositioning. These servos have no verified head-position feedback or absolute cable-turn reference.

Degree-based aiming needs a repeatable camera-forward and level datum, signed shaft angles and corresponding head angles at measured pulse points, and usable limits inside verified mechanical and harness clearances. Verify the installed pulley ratio used by the firmware. The chassis IMU measures the chassis. Pulse positions are available for manual aiming, while degree targets and scan require an applied angular profile.

Jim operates the physical tests. Assistant-issued motor or servo movement requires his explicit permission. Opening a page, saving positions or restarting leaves outputs off. The S3 remains the authority for motion and output safety.
