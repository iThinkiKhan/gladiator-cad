# V2 installed-hardware development page — 2026-10-20

Jim reports Gladiator assembled in V2 configuration, with the same electronics and
SG90 servos on GPIO10/13. Neither axis has been physically tested or identified.

Added a standalone local hardware tester in firmware/tools/hardware-test in the
GitHub repository; the canonical local source is C:/PlatformIO/Gladiator/tools/hardware-test.
Run Start-HardwareTest.cmd or Python serve.py, then open http://127.0.0.1:8765/.
It bridges only the existing integrated C6 APIs; no firmware flash is required.

The guided UI covers one-GPIO pulse tests, small steps, recording centers/endpoints,
measured shaft/head limits with pan ratio 1.5, S3 profile save/readback, explicit
enable, aim/hold/center/bounded scan, camera picture settings and stream, face tests,
and sensor health. Raw test windows are explicit and limited by the S3; normal
movement remains subject to S3 calibration, safety, session and lease rules.
Track controls are DISARM only. Boot/reconnect never auto-enable.

Nine local HTTP bridge tests and simulated Chrome desktop/phone workflows passed.
No real movement, camera setting, calibration save, firmware update or power change
was commanded. Installed mechanical/electrical behavior and actual network/firmware
compatibility still require operator testing. Older OTA and sensor acceptance notes
remain historical unresolved items; this page does not claim those are resolved.

Canonical local firmware has independent earlier work; only this new standalone
tool and its documentation are being added to the existing GitHub integration branch.
No older canonical firmware is copied over the published October14 firmware.
Runtime state, screenshots, credentials, binaries and flash backups remain local.
