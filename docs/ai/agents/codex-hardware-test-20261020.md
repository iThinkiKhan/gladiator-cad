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

## Follow-up: hosted on C6 and OTA deployed

Jim explicitly requested phone access without this PC and OTA deployment.
Gateway 2.2.2 now serves /hardware-test/ plus its gzip assets and adds a shortcut
on the existing driving page. Native mode uses the original gateway control APIs;
S3 retains all motion/commissioning authority. PC-hosted mode is still available.

Canonical gateway source was reconciled against the exact published October14
baseline using Git blob hashes; prior canonical files were backed up locally.
Only C6 firmware was built/flashed; existing S3 source, CAM, secrets and NVS were
not replaced. Gateway version/slot change, three served assets, AP/LAN access,
S3 boot continuity and motion-off state were verified. See the tester VALIDATION.md
and firmware/docs/HARDWARE_TEST.md. Runtime OTA evidence and binary stay private.
The camera sensor was not initializing before this update; LiDAR/presence were
offline. Those hardware/firmware acceptance items are still separate pending work.

## Development workflow correction — gateway 2.2.3

Jim reported Save center blocked and asked to remove development friction.
The old UI incorrectly required an active owned/settled test even for local draft
recording. Recording now uses retained command data after Stop/link loss, without
movement-side guards. Partial drafts survive reload locally and remain distinct
from applied S3 calibration. Repeated test/save acknowledgements and duplicate
frontend commissioning gates removed. Complete setup save automatically stops
mast tests, then lets S3 decide and displays its rejection/confirmation.

Native and PC simulated regressions passed. C6 2.2.3 OTA boot/slot and exact assets
verified; S3 boot stayed unchanged and outputs stayed off. No pulse test, center
assignment or physical movement was commanded by the agent on live hardware.
