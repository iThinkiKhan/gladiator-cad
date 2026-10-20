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
