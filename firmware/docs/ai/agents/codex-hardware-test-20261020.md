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
