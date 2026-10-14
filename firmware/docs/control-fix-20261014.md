# Operator integration and control corrections — 2026-10-14

The installed field page now combines live video, manual pan/tilt, speed, Center, bounded Scan, Hold/OFF, installed commissioning, saved calibration and OV2640 settings. S3 owns all motion and limits. See [operator and physical commissioning guide](FINAL_INTEGRATION.md).

## Control corrections

- Removed the phone's second orientation inversion and obsolete front/rear toggle. Website, phone and S3 share the fixed mast-front frame: Forward +L/+R, Reverse −L/−R, Left −L/+R, Right +L/−R. Existing S3 motor wiring/polarities and measured trim remain.
- Field drive, mast, commissioning and temporary expressions require no maintenance key. Network provisioning, firmware maintenance and persistent camera-address setup retain their key.
- Power can change while armed or moving in both clients. S3 normal-mode PWM is capped after trim and ramp, scaling tracks together to preserve their ratio. Lowered ceilings apply immediately. Overdrive remains explicit. Stop/reconnect/background/watchdog reset the client to 25%.
- Removed the proposed GPIO6 gate and external-watchdog requirement. GPIO10/13 wiring is used as installed; saved calibration can assign either pin to either axis. Boot loads calibration without starting PWM. Enable at neutral is explicit and may move a displaced positional SG90. Normal aiming can coexist with drive; pulse testing/calibration requires disarmed stationary tracks.
- Operator profiles store measured servo shaft angles separately from head limits. S3 applies pan 60T/40T = 1.5 to every move, jog and scan. No angle wrap or unrestricted scan exists. Default commissioning form limits are narrow; pulse/shaft values are deliberately blank.

## Installed firmware and phone

- **C6 gateway 2.2.1:** OTA accepted, changed slot and new boot verified through the existing LAN route. `192.168.8.1` recovered after disconnect/rejoin of the PC's saved Wi-Fi profile. Key-free ARM/DISARM passed with zero tracks/deadman off before the battery inhibit. No movement was commanded during the live checks.
- **CAM 1.1.4:** OTA installed and confirmed, NVS/private display geometry preserved. Default QVGA feed and TFT-only 180° offset remain. Live image settings readback passed for brightness, exposure, resolution up to SVGA, flip/mirror; original settings were restored. A subsequent stream check observed valid frames.
- **S3 operator release:** USB recovery was authorized after repeated OTA activation failures. A full 16 MB private backup was completed first. Recovery writes only app0 and standard OTA metadata, preserving NVS, bootloader, partition table, filesystem and the other app slot. Final source uses the standard SDK verifier and normal appended SHA256; no validation bypass or forced activation exists.
- **Phone:** latest same-signature release installed in place on the reconnected SM-S938U. ADB reported success and package update time `2026-10-14 15:20:02`. App data was preserved. Live power and unified-console shortcut are included; launching that shortcut stops the native camera viewer before opening the browser console.

## S3 OTA remains an open reliability issue

Native sequential web OTA improves error reporting and preserves the running slot on rejection. Matching DIO runtime/bootloader configuration with OPI PSRAM allowed one OTA app0 → app1 activation, followed by a verified valid new boot. Later attempts rejected valid images with `ESP_ERR_OTA_VALIDATE_FAILED`; USB snapshots of rejected app0/app1 slots matched the uploaded bytes exactly and their image digests were valid. A monitored attempt specifically reported `Image hash failed` from the SDK verifier.

An experimental software hash backend passed host reference vectors but did not establish reliable hardware activation, so it was removed from the release. Its diagnostics are retained privately. Do not disable image hashing, force boot selection or describe OTA as reliably repaired. Further testing must exercise both slot directions and corrupt/incomplete-image rejection on stable power. ArduinoOTA compatibility remains, but its PC return connection was not successfully established in this session.

The last power measurement was **10.06 V**, with the existing configured four-cell battery guard reporting CRITICAL/lockout and radio shedding. Live OTA and ARM tests are paused pending restored deck power and a power cycle. This inhibit is separate from the removed mast hardware gate and live power-selector behavior.

## Verification and remaining acceptance

All three target builds pass. Host checks cover 4,080,501 drive/power combinations, 363,909 mast angle pairs, measured gear conversion, smooth jog/scan, bounded pulse commissioning, replay/expiry/stops, invalid/stale sensors, production gateway handlers and visual priorities. Real Chrome fixtures exercise explicit enable, aim/release, speed, Center, Scan/OFF, saved-profile requests, image controls, recovery, phone layout and existing development tabs. Phone checks cover 4,465 mixer cases, production BLE bytes/checksum/queued stop, live power during a held direction, background disarm and opt-in video; TypeScript and release build pass.

Installed pan/tilt identity, neutral pulses, clearance and calibrated bounds still require the operator's observed tests. No servo pulses or nonzero track commands were sent by the agent. LiDAR and radar still report OFFLINE/no sample; power monitor and IMU communicated before the power inhibit. SEN0628 5 V connector pull-ups require verified I²C translation before S3 GPIO8/9; sensor firmware and real ranging acceptance remain physical work. Event readiness requires those checks and sustained deck-power operation, not only successful compilation.
