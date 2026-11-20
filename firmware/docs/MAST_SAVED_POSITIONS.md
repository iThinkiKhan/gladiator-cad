# Main-page mast controls from saved positions

The main page can arm the mast using recorded pulse positions without a servo-test
session or an angular calibration. This implements Jim's November 9 request.

Revision 13, verified November 19: pan GPIO10 right 500, neutral 850, left
1500 microseconds. Tilt GPIO13 down 950, neutral 1500, up 2000 microseconds.
PWM is 50 Hz. Directions follow the camera. The screen faces the opposite way.

Check the area-clear acknowledgement, then select **Arm mast at saved neutral**.
Arming deliberately commands the two recorded neutral pulses. Hold an arrow to
aim and release to hold. Center returns to recorded neutral; **Disarm mast**
detaches PWM. Loading a page, saving positions and rebooting never enable outputs.

Saved-position coordinates are signed percentages of each neutral-to-end span,
not degrees. Each direction uses its own recorded pulse span. The default
speed is 5% of a saved span per second, adjustable to 30%. S3 enforces the recorded
pulse limits, ownership, sequence validation, 750 ms operator lease, power/link
checks and loop-timing stops. There is no continuous rotation or modulo wrapping.
Scan and nonzero angle targets are rejected in this mode. No measured angle,
physical feedback, cable envelope or mechanical readiness is inferred.

C6 builds a `positions` configuration from its flash record after a revision
check; browser-supplied pulse values are not used. S3 validates and saves that
profile, with outputs off. `positionsReady` and `controlMode: saved-positions`
identify the mode; `calibrated` remains false. Normal arm uses operation 8;
angular operation 7 cannot arm a saved-position profile. Main-page arm checks
the commissioning revision again, rejecting stale positions. Existing angular
calibration and commissioning paths remain separate.

Evidence and deployment records: `diagnostics/mast-positions-20261109/`.

Revision 13 readback: `diagnostics/mast-commissioning-20261119/saved-position-profile.json`.
