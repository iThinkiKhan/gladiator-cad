# Shared Project State

This file contains concise project state useful across AI assistants.

## Sources of truth

Use the repository's engineering documentation and measurements for detailed
technical facts, including:

- ../GLADIATOR_DESIGN.md
- ../components.md
- ../deck-v2.md
- ../upper-structure.md
- ../print-plan.md
- ../../measurements/chassis.md
- ../../measurements/components.md
- ../../measurements/mast-head.md
- ../../measurements/printer-calibration.md

Do not copy large sections of those files here. This is a map and current-state
summary, not a second documentation tree.

## Current shared state

2026-10-14 — Jim reports assembled S3/C6/CAM/TFT working; both servos SG-90.
Final integration deployed via Wi-Fi OTA: S3 Mast v1, C6 2.1.1, CAM 1.1.3.
Same-signature native phone app updated in place with explicit camera viewer.
Remaining physical acceptance: ../../firmware/docs/FINAL_INTEGRATION.md;
verified deployment: ../../firmware/docs/integration-deployment-20261014.md.
Mast is OFF/unreferenced; physical GPIO10/13 axis assignment is unverified.
LiDAR reports OFFLINE/no sample; power/IMU and S3/C6 link are healthy.
SEN0628 powered from 5 V needs external I²C translation; mast requires verified
normally-off power/signal gate and measured calibration before outputs enable.

2026-10-13 — CAM OTA 1.1.2 installed and confirmed over Wi-Fi, rollback/interruption/corruption checks passed, recovery AP usable without gateway/sensor. USB power only; jumper supply untested. OV2640 currently reports 0x105 again: resolve before sealing. Details: ../../firmware/docs/masthead/cam-ota-20261013.md. Private CAM key remains local.

2026-10-13 — ESP32-CAM/C6 visual subsystem flashed and camera-tested: 14.92 fps QVGA over 90 seconds, gateway reboot recovery passed. TFT is not connected; S3 telemetry absent at the bench. Source/setup: ../../firmware/docs/MASTHEAD.md; next steps: agents/codex-masthead-20261013.md. Credentials and configured binaries are excluded from GitHub.

2026-10-09 — **Mast is FRONT**, per Jim. Current frame +Y forward, +X right,
+Z up; origin rear-left. Low X LEFT, high X RIGHT. No geometry or wiring move.
See ../ORIENTATION.md before interpreting older front/rear or left/right notes.
Firmware swaps logical tracks and reverses both polarities; native CAD carries
the same frame. Head master faces +Y at legacy pan180 (a travel endpoint, not
a centered servo home). Historical aliases and print plates stay unchanged.

No cross-agent state has been formally summarized here yet.

Agents should add concise, verified current state as work proceeds.
