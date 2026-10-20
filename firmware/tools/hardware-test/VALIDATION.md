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
