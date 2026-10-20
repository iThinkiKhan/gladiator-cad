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

2026-10-14 — operator integration and control corrections. Jim uses installed SG90s on GPIO10/13 and explicitly removed the proposed GPIO6 hardware gate. S3 stores measured calibration in NVS, leaves PWM off at boot and supports deliberate field enable, bounded pan/tilt, speed/Center/Scan/OFF, installed pulse tests and 1.5 pan gearing. Manual aim can coexist with driving; commissioning requires disarmed tracks. Field keys and client front/rear inversion removed; live drive power changes and S3 PWM ceiling added.
Installed C6 2.2.1 and CAM 1.1.4 OTA verified; latest phone APK installed in place. S3 operator release recovered through authorized USB with full backup/NVS preserved. S3 OTA remains intermittent: one valid changed-slot boot, later byte-identical valid images rejected by native verifier. No validation bypass; experimental hash backend removed. Last voltage 10.06 V triggered existing battery/radio lockout; restore deck power AND power-cycle before further OTA/ARM tests.
No physical mast or track motion was commanded. Servo axis identity/calibration and cable clearance remain operator acceptance. SEN0628/radar OFFLINE; verify 5 V I²C translation to SDA8/SCL9. Current guide: ../../firmware/docs/FINAL_INTEGRATION.md. Deployment/limitations: ../../firmware/docs/control-fix-20261014.md.

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
