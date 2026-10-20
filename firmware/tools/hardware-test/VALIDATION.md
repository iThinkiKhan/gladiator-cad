# Verification — 2026-10-20

Added standalone hardware bench files only. Existing firmware and CAD were not edited or flashed.

- 9 Python API bridge tests passed using local fake HTTP servers.
- Chrome/Playwright simulated-gateway checks passed: no startup or Connect writes; blank first pulse rejected; explicit GPIO test; pulse stepping constrained to window; neutral recording; pan 1.5 ratio span validation; calibration save/readback with outputs off; explicit enable, jog/release-to-hold and scan; focus OFF; connection recovery without auto-enable; drivetrain DISARM; camera read/apply and temporary face; explicit video start/stop; 390px phone layout without horizontal overflow.
- Desktop and phone screenshots reviewed for layout.
- All robot and camera requests in browser tests were intercepted. No real servo, drivetrain, camera or power changes were commanded.

Not verified: installed firmware compatibility, physical pin-to-axis mapping, SG90 electrical/mechanical behavior, actual pulley routing, endpoint measurements, real network latency, camera stream reachability or sensor accuracy. These require the operator's installed hardware test.

## Usability revision — 2026-10-20

Replaced the long form with four focused views, guided A/B/C servo testing,
automatic small pulse windows, one-click position recording, explicit stop/switch
workflow, status hints, collapsible measurements and a shared video/aim view.
Simulated Chrome checks passed again, including both GPIOs, automatic window creation,
endpoint capture, switching with first pulse cleared, save/readback, ratio limits,
motion/stop/recovery, camera controls, sensor summary cards and phone layouts.
No live hardware commands or firmware changes were made in this revision.

## C6 hosting and OTA — 2026-10-20

User explicitly requested the page on the C6 for phone use without a PC and
approved OTA. Gateway 2.2.2 builds successfully (RAM 39.7%, flash 61.5%).
Simulated native C6 and optional PC bridge browser suites both pass.
The native page uses existing same-origin gateway APIs; no PC proxy is involved.

OTA succeeded over the existing LAN maintenance route. C6 boot ID changed and
active slot changed ota_0 -> ota_1. S3 boot ID remained unchanged. Gateway stayed
online beyond its automatic boot-confirmation interval. All three served gzip
assets decompress to the exact source used for the build; root field page links
to hardware setup. Both AP192.168.8.1 and LAN192.168.0.230 respond as 2.2.2.
Actual C6-hosted page rendered in the browser and connected to live S3 telemetry.
Tracks remained disarmed; mast/test output remained off; calibration is blank.
S3 and CAM firmware, NVS and private network configuration were preserved.

Image SHA256: 44348dd2e93af8eaa5c590e1998bc884bf9573417a4c08b5b43fd0d89c2c9376

No servo or nonzero drivetrain movement was commanded. Previously observed
camera sensor initialization failure and offline ranging sensors are not fixed
by hosting the page; physical diagnosis and commissioning remain operator work.

## Center recording fix — gateway 2.2.3, 2026-10-20

Reproduced the failure: S3 retained a valid test GPIO/pulse after Stop, but the
page disabled recording because the local motion session was inactive.
Removed active-session, freshness and target-settled gates from draft capture.
Retained S3 command values per GPIO and partially completed setup fields locally.
Draft restoration never restores enablement or motion. Partial import/export is
supported. Removed repeated test/save acknowledgement checkboxes and duplicated
frontend commissioning preconditions; S3 still enforces actual movement rules.
Full setup save stops mast output automatically and reports S3 rejection/timeout.

Simulated native checks pass recording during slew, after Stop and offline,
reload persistence with zero replay, automatic stop-before-save ordering, and
explicit S3 rejection without overwriting the saved profile. Existing aiming,
limits, startup, recovery, camera and mobile layout checks pass in both modes.

Gateway 2.2.3 build and OTA succeeded. Slot changed ota_1 -> ota_0 and the C6
boot changed. S3 boot remained unchanged; mast/test off and tracks disarmed.
All three served assets match source. Existing S3 and CAM firmware unchanged.
Image SHA256: 7d978d940337a2cd9c8212a2b9903c05175efa77607d994c1d2cd32c659fd7b4


## Robot-side calibration and usable pulse tests — gateway 2.2.4

Individual centers/endpoints and setup field edits now commit to C6 NVS through
GET/POST /api/mast/setup (schema/revision/partial fields). One atomic NVS record
stores the data and revision. Each capture waits for commit/readback; unchanged
values skip writes. Other devices load robot entries on Connect. Stale revisions
return 409 and clients retry only their changed fields, preserving unrelated edits.
An earlier phone draft is preserved separately for explicit one-click migration.
Complete applied calibration continues to persist in S3 NVS and every controller
can read the S3-enforced limits. Partial records do not enable outputs.

Pulse testing offers 5/10/25/50/100 µs steps, direct target entry, a slider and
automatic 500 µs windows. Stop & shift window prepares the next window without
restarting motion. Existing S3 100 µs/s slew, bounds and deliberate Start remain.
Only S3-reported commands are captured; no unconfirmed target is labeled position.

Validation: 10 local bridge tests pass. Native C6 and PC simulated Chrome suites
pass, including partial robot saves before angle measurements, fresh-device load,
revision conflict merge, migration without motion, coarse/direct targets, pulse
bounds, applied-profile readback/rejection, pulley limits, aim/hold/scan/OFF,
focus/link recovery, camera/face controls and desktop/phone layouts.
Visual inspection found and corrected a range-label encoding error before the
final deployed image. JavaScript syntax and final UTF-8 labels checked.

Live C6 API checks rejected invalid GPIO11, pulse9999 and an unknown enable field
(400), plus a stale revision (409). Saved only the operator-confirmed tiltPin13,
then verified commit/readback, unchanged-save revision stability, and identical
NVS record after a subsequent OTA/reboot. No center, endpoint or shaft angle was
guessed. Robot NVS remains a partial assignment record; S3 is not calibrated.

Final 2.2.4 OTA verified changed boot/slot, S3 boot continuity, fresh safe/disarmed
telemetry and all three served assets exactly matching source. AP-hosted page
rendered and connected to live telemetry with Saved on robot revision1. Only C6
updated; S3/CAM, their calibration and private settings remain. No live servo or
nonzero drivetrain movement was commanded. Battery ~15.82 V.
Final image SHA256: 5946213cec00a2a29ef14f03989968b1a5dab77467551352b7c716cc1dea1560
Final image bytes: 1216928. RAM39.7%, flash61.9%.

Tilt remains a physical acceptance issue: operator confirms GPIO13, 5 V and common
ground. Deployed S3 source audit finds no GPIO13 or PWM allocation conflict and
uses the same duty conversion for either test pin. No connector waveform or shaft
response was measured. The operator was asked to compare the separate target and
S3-commanded readout during a brief supervised test. No claim that pegging is fixed.
