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
