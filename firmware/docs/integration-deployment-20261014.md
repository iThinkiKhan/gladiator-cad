# Final integration deployment — 2026-10-14

User-authorized changes are published in stacked
[draft PR2](https://github.com/iThinkiKhan/gladiator-cad/pull/2), based on the
existing working camera branch. CAD and unrelated work were preserved. All
three ESP boards were updated over Wi-Fi OTA; no wired board flash or NVS erase
was performed. No servo or drivetrain movement was commanded.

## Verified installed state

| Component | Result |
| --- | --- |
| S3 | Interface v1 / Link v2 / Mast v1; new software-reset boot, app1, image marked valid; mast-front motor pins/inversion preserved |
| C6 | gateway-2.1.1; new boot in ota_0, surviving confirmation window; fresh UART S3 telemetry, zero frame/JSON errors at verification |
| CAM | masthead-1.1.3; app0, explicitly confirmed, camera ready, buffered display active; TFT-only 180° offset compiled with the original private 170×320 geometry/base rotation |
| Camera stream | Eight live MJPEG frames received at `192.168.8.2:81/stream` after C6 reboot; visual state returned to ready/SAFE |
| Mast | OFF, uncalibrated, unreferenced, session0, reason "boot: position unknown"; no automatic startup/reconnect movement |
| Power / IMU | Both reporting healthy, fresh samples; robot SAFE/disarmed, track commands zero, battery OK |
| LiDAR / presence | OFFLINE, no samples; derived range invalid and visual nearest/presence null; no false obstacle alert |
| Native Android phone | Updated in place via the connected phone's ADB install, release APK signed identically to previous installation; source originals and old APK preserved privately; data/settings not cleared |

Existing CAM authenticated upload/confirmation, S3 maintenance web update and
C6 authenticated SHA-checked OTA endpoint were used. The S3 ArduinoOTA reverse
TCP connection failed, so the existing web uploader was used without changing
firewall settings. An initial C6 connection reset left the old image running;
the subsequent paced upload returned success and the new boot was verified.
Private AP/OTA/pairing credentials were retained, not replaced with examples.

The native phone viewer was built/installed, but actual video on the phone was
not physically verified before it disconnected. Join `Gladiator-Gateway` Wi-Fi,
open Gladiator Drive and press **Start video**; stop browser video first because
the camera supports one viewer. Leaving Drive/backgrounding stops video and
disarms held drive controls. Returning does not automatically restart either.
Source-only patch and validation instructions: [phone integration](../phone-integration/README.md).

## Remaining event acceptance

- Confirm the rotated panel visually and run a combined video/display/telemetry
  soak for at least 30 minutes. A brief successful stream is not a soak test.
- Verify the SEN0628 bus-mode/address, regulated power, common ground and external
  5 V-to-3.3 V bidirectional I²C translator, then demonstrate 64 valid zones,
  measured targets, unplug/recovery and all-invalid behavior. Current OFFLINE
  telemetry means hardware ranging and sensor-driven scanning are not accepted.
- Verify the normally-off external servo power AND signal watchdog gate on GPIO6.
  GPIO10/13 physical pan/tilt assignment is still unknown. Identify them only with
  mechanically disengaged outputs and follow the measured neutral/limit process
  in [commissioning](FINAL_INTEGRATION.md). Never reference an unknown assembly.
- Verify startup/reset/stall/link-loss/cutoff behavior and initial restricted
  poses before enabling any assembled mast movement. The reported S3 historical
  maximum loop time includes a 418 ms gap during deployment/maintenance;
  sustained timing under the actual event workload is not yet accepted. Mast
  policy removes its session if a control-loop gap exceeds 100 ms.

Until these physical checks pass, use a fixed-mast camera/display demonstration.
Firmware limits, SG90 labels and commanded-angle estimates do not establish
mechanical position or clearance.

Build, host policy/protocol/sensor and browser checks passed. Phone TypeScript,
Android release/lint, 23 existing drive cases, 14 production MJPEG-parser cases
and explicit-start/background-stop/no-resume component checks passed. Configured
binaries, credentials, camera frames and complete phone app source are not
published. Detailed network receipts and hashes remain in local ignored
`firmware/build-output/` and the private handoff directory.
