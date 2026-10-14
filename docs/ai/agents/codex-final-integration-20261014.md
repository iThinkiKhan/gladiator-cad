# Final integration candidate — 2026-10-14

Baseline: latest GitHub `codex/esp32-cam-masthead-20261013`,
ecc7709e282c08337c89439dd4136f9342beae6a. Main remains
3fb6cc9315b296403a86ee2b214b0a425530e8d1. Camera work is PR1, still draft;
this integration is stacked on it so the diff preserves that working subsystem.
No original workspace, CAD, credentials, installed firmware or hardware changed.

Jim reports assembled S3/C6/CAM/TFT operational and both servos SG-90.
Read [commissioning guide](../../../firmware/docs/FINAL_INTEGRATION.md).

Implemented: TFT-only 180° offset, provisioned-CAM-preserving 1.1.3 source;
C6 2.1.1 field mast relay/default camera address; S3 Mast v1 with GPIO10/13,
LEDC4/5 timer2 at verified frequency/14 bits; GPIO6 external-gate heartbeat.
Every boot requires measured USB calibration. Every powered session requires
physical neutral verification/USB reference. Reference hold allows 10 seconds
to select the field keepalive, then a 750 ms lease. Bounds include one-sided
neutral-at-endpoint profiles and enforce at most ±45° head pan/±20° tilt.
Scanning requires valid LiDAR and stops on invalid/nearby returns or presence.
Control-loop/source freshness is tracked independently of transport health.

Validation performed on production code/isolated fixtures:

- S3, CAM and C6 PlatformIO target builds pass. Final build evidence is local;
  builds use public credential placeholders for S3/C6 and are not deploy-ready.
- Mast policy passes 363,909 angle pairs, reference/startup lock, endpoint
  calibration, smooth steps, bounded scanning, replay, lease/timing faults,
  link/power interlocks, invalid range, stop and unsigned clock wrap.
- Production gateway visual/mast HTTP handlers pass authorization, malformed
  bodies, limits, stale source/transport, override precedence and default camera.
- Production sensor driver tests pass native 64-zone reads, all-invalid values
  (0/19/4000/65535), bad payload bounds, power/presence failures and recovery.
- CRC/COBS protocol and typed Link tests pass; 80,802 track/trim and 2,025 IMU
  orientation cases pass. Existing motor-control JavaScript compares unchanged
  to the baseline. Existing phone hold/release/arm/reconnect/tab-stop tests pass.
- Real-browser mast test passes no startup commands, explicit maintenance,
  signed head angles, calibrated bounds, scanning, stop, failures/reconnect,
  no automatic resume and 390 px layout. Screenshot inspected locally.
- CAM OTA policy/maintenance and existing video/expression browser tests pass.
- UTF-8 source encoding and `git diff --check` verified.

Not physically validated: GPIO/header continuity, external power/signal watchdog
gate, installed SG90 supply/frequency/pulse endpoints/neutral/head clearance,
pan belt indexing, SEN0628 hardware revision/firmware/level-shifter voltages,
startup/reset behavior, stall behavior, combined video/sensor/display soak and
drivetrain movement. No flash/upload or servo motion performed. Those checks
are mandatory before claiming event-ready mast motion. Fixed-mast camera/display
remains the fallback if hardware acceptance is incomplete.

Electrical finding: vendor SEN0628 V1.0 sheet4 exposes VIN-side pull-ups through
its FET translator, so 5 V supply does not guarantee 3.3 V connector logic.
Use an external bidirectional translator between sensor and GPIO8/9 and verify.
No sensor-bus speed/ownership or motor/battery/transport protocol was replaced.
