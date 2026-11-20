> EVENT COMPLETE — October 31, 2026. Historical event record. Standard development has resumed: [current development state](DEVELOPMENT_CURRENT.md). Event-day instructions below are retired.

# Gladiator event operator — October 23, 2026

**Installed: gateway-2.4.3.** The operator page and USB diagnostics are installed on C6. S3 firmware is unchanged. Firmware readback passed; the current calibration/boot storage and the other firmware slot were preserved. No track, servo-enable, raw-test or calibration-write command was sent during this work.

## Open the controls

On Opal: http://172.23.44.190/booth/

Direct fallback: join Gladiator-Gateway and open http://192.168.8.1/booth/ .

Power Opal before the robot for normal booth use. While a direct client is connected, C6 pauses automatic searches for a missing Opal network so its shared radio can serve that client. To return to Opal, connect the staff device to Opal; when direct clients leave, C6 resumes its saved-network search within about 10 seconds. Credentials are retained.

After explicit approval, this PC's all-user Gladiator-Gateway profile was replaced using its existing key with WPA2PSK/AES settings. The stored XML and active CCMP connection were verified. Windows still lists GCMP as an alternate in its profile summary; no global Wi-Fi policy was changed. Other Wi-Fi profiles and Opal settings were untouched. The subsequent 60-second direct fallback check passed with zero request errors; earlier failed runs remain recorded. Opal then became visible and C6 rejoined at its saved address without a reset. This installation is not an event-length battery or network rehearsal.

## What is saved now

C6 record revision 4 contains tilt GPIO13 and **1150 / 1500 / 1800 microseconds** for low / neutral / high, plus pan GPIO10. Pan pulse endpoints are not yet saved. S3 does not yet have a complete applied aiming profile.

The page shows stored pulse measurements separately from a complete applied profile. Shaft angles, usable head limits, PWM frequency and speed must be entered from calibration before applying an aiming profile; none are guessed. New saved entries are read from the robot rather than from this handoff snapshot.

1. After working power is restored, finish pan measurements and the remaining angle/limit fields through **Finish or review measurements**. Stop the raw test when finished.
2. Review the complete profile on the booth page, confirm its travel/direction/clearance, then choose **Apply saved calibration**. The software stores and verifies S3 readback with outputs OFF.
3. Once applied, S3 reloads its profile on startup. Reapplying at every boot is unnecessary. Opening or reconnecting the page does not enable motion.
4. **Camera & manual aiming** opens the operator view. Its separate Enable action moves to saved neutral; rehearse only when the physical setup is ready.

## Build the repeating routine

Use step cards for waits, expressions, tracks, mast targets or **Tracks + mast**. Add, duplicate and reorder cards; Preview checks the routine. Named poses save commanded angles without moving the head. Add a pose as a mast card; changing it to Tracks + mast keeps its angles so you can add a short track pulse.

Choose Once, a repeat count, or Repeat until STOP, with a pause between cycles. Save stores the routine and repeat preferences in this browser. Export/Import carries the steps to another device or between Opal and direct-Wi-Fi addresses; select repeat preferences there. Poses are also browser-local and tied to the physical calibration.

Keep the staff page visible and device awake. Motion requires deliberate supervision and, for mast steps, an applied matching calibration. STOP ALL or Escape ends playback. Leaving the page, stale telemetry, changed ownership, rejected commands or a controller restart also stops it; reconnect never resumes it. During pauses, tracks are zero and the head holds its last target.

Bounds remain 40 steps and 90 seconds per cycle, at most 5 seconds of track commands per cycle, each track pulse at most 1.5 seconds and 25 percent. Coordinated cues start both targets together; they do not measure distance or guarantee synchronized physical arrival. Rehearse the actual van-floor path before repeating it.

## Field troubleshooting

**USB health check.cmd** works on this PC with the connected C6 and its existing WinUSB driver. It reads status, saved measurements and field outputs without changing control lines, resetting the board, asking for credentials or sending motion commands. Its local report is C:/PlatformIO/Gladiator/diagnostics/field-usb-latest.json . The summary includes the saved Wi-Fi network, current LAN IP and connection reason, without passwords.

**Opal LAN health check.cmd** in the shared kit runs the following one-minute read-only test on this PC. Join SOIT-Field-5G first. It prints PASS/FAIL and saves diagnostics/field-lan-latest.json.

Read-only LAN check, from the canonical project:

`python tools/booth/check_gateway_readonly.py --host 172.23.44.190 --seconds 60 --out diagnostics/field-lan-latest.json`

That check reads status/field/crowd/full diagnostics. Crowd reads renew only a short sensor-detail lease. It does not arm, enable, stop another operator, write settings or run a routine.

Firmware maintenance is separate from normal operation. The installer shortcuts are version/hash guarded; they refuse an already-updated or unexpected baseline. USB recovery scripts are tied to this device, backup and specific source version. Do not rerun a firmware write after an interrupted verification; inspect its receipt first. Complete flash backups and credential-bearing binaries/ELFs stay in the canonical local diagnostics folder, not this share.

## Verified and still pending

Automated checks cover sequencing, saved settings, revision races, STOP/preflight, UI, maintenance installation and bounded JSON streaming. The streaming decoder round-trips real captured S3 data, rejects truncated/malformed inputs and failed sinks, and processes an 18 KB JSON result with allocations above 4 KB prohibited. Large native diagnostics now retain bounded wire snapshots and stream through a 512-byte buffer.

Live USB checks confirm the installed version, unchanged saved record, unchanged S3 boot and all outputs OFF with USB-power battery lockout. The subsequent Opal test passed for 180 seconds: 180 samples, zero HTTP errors, 36 full diagnostic replies and 179 fresh grids after the first warm-up sample. Median crowd GET time was 36.3 ms (PC to C6 HTTP, not end-to-end display latency). Both boot IDs were unchanged, outputs stayed OFF and no allocation failure occurred. One additional link frame error was counted; detail errors and dropped frames did not increase. All four served operator assets matched source after gzip decoding. A separate 60-second direct fallback check also passed. Receipts, including earlier failed runs, remain under diagnostics/operator-20261023/.

C6 signal was about -77 dBm during the check. Place its antenna clear of the van metal and recheck in position. The roughly 1 Hz grid publication still contributes visible LiDAR delay even when HTTP requests take tens of milliseconds.

**Still pending:** working battery power; completed pan and angular calibration; applying and physically rehearsing the full profile; track/mast choreography on the van floor; real camera power/frames; an event-length Opal/battery rehearsal. The tablet is unchanged. Camera controls are prepared, but no real camera stream was commissioned in this session.
