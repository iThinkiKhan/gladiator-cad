> EVENT COMPLETE — October 31, 2026. Historical event record. Standard development has resumed: [current development state](DEVELOPMENT_CURRENT.md). Event-day instructions below are retired.

> OCTOBER 24 EVENT: Jim selected fixed mast, camera and expressions; no motor/servo movement. Current runbook: X:/Projects/Gladiator/EVENT_TODAY.md. New camera service-v2 print delivered X:/3D Printer/GLAD_CAMERA_SERVICE_V2.gcode, 1h58m42, physical fit/repair acceptance pending. Canonical display-only launcher: tools/booth/run_fixed_display.py. Current power median 3.21W; one-minute health and short live display checks pass. See docs/ai/agents/codex-event-fixed-20261024.md.

# Gladiator + Petey booth — October 24, 2026

Updated October 22 after the final sequencer and controller checks. Tablet excluded by Jim.

## Start here on Opal

- Sequence editor: **http://172.23.44.190/booth/** (also `http://gladiator-gateway.lan/booth/`).
- Manual drive, expressions and camera: **http://172.23.44.190/**.
- Mast identification/calibration: **http://172.23.44.190/hardware-test/**.
- Diagnostics/network/firmware: **http://172.23.44.190/dev**.

These pages live on C6 and work without the PC or Internet. Use one staff controller. Keep its page visible and device awake during playback. Nothing starts when opening, reloading or reconnecting. The saved customer tablet setup is unchanged.

## Program a repeating show

1. Start with Display example, Movement example, or Tracks + mast example. Edit the cards in seconds, signed track percentages and mast head degrees. Add, duplicate, remove and reorder steps. Advanced JSON is optional; Preview applies those edits to the cards.
2. Choose Once, Repeat a set number (up to 100), or Repeat until STOP, with a 1–60 second pause between cycles. Preview shows the cycle length and track time.
3. Save on this device stores steps and repeat preferences in this browser. Export/Import carries the steps; choose playback settings on the destination. The supplied routine JSON files are examples, not accepted physical choreography.
4. For movement, deliberately check supervision after rehearsal. Mast also requires its separate checkbox and a complete measured calibration applied to S3. Missing calibration blocks a combined sequence before either arm request.
5. During each pause, tracks are zero and the mast holds its last target. STOP ALL, Escape, leaving/hiding the page, lost ownership, stale data, a rejected request, controller restart or a delayed control loop ends playback. There is no automatic restart after a fault. STOP asks for disarm and mast OFF; check the S3 state. Hardware watchdogs/leases remain the fallback. Servo OFF releases holding torque.

A Tracks + mast cue submits both targets concurrently from one fresh S3 snapshot. It does not measure pose or guarantee simultaneous physical arrival. Enabling mast moves to its measured neutral. An aim dwell gives it time to move under its saved speed profile.

Per cycle: maximum 40 steps / 90 seconds; at most 5 seconds of track commands; each track cue at most 1.5 seconds and +/-25%. Begin with tracks raised clear, then tune short pulses on the actual van floor. Timed commands are not distance control, and forward/reverse can drift on every repeat. Establish a small envelope away from the van opening, walls and cables before public use.

## Installed hardware/software state

- C6 **gateway-2.3.9**, SHA-checked OTA, running ota_1; previous ota_0 retained. Its hosted editor matches source. TCP_NODELAY remains enabled for small field replies; full diagnostic streams temporarily coalesce packets. Native sensor detail is decoded with bounded memory, and the crowd path parses only the cached range subtree. Reset reason, heap/largest block and allocation-failure context are now available in status.
- S3 **Mast operator v6 / radio dwell / bounded IMU**, app0, USB-UART COM13, MAC dc:b4:d9:13:4f:94. Application-only writes passed flash hash verification; NVS/OTA metadata were not flashed. Both servo routes start detached and tracks start disarmed. Installed MAST_FRONT mapping, PWM cap, trim behavior and mast safeguards were retained. Canonical flight recorder, link diagnostics and fast power monitoring were retained. The production build also preserves the version-checked 500 ms SH2 missing-reply timeout.
- **Current source is C:/PlatformIO/Gladiator for both S3 and C6.** Mast support and the SH2 build hook were merged from the previous installed integration tree without modifying it. Older notes requiring separate S3 source are superseded by this audited merge; do not replace current sources with the old tree.
- **Tilt pulse calibration is saved** in C6 nonvolatile storage and was preserved. The separate complete pan-and-tilt aiming profile is not applied on S3. C6 saved setup revision 4 contains: pan GPIO10; tilt GPIO13, low1150 / neutral1500 / high1800 microseconds. These records must not be overwritten. Remaining pan measurements/bounds, physical behavior and the complete profile still need acceptance. No servo was enabled or physically moved during this booth-sequencer session.
- Tracks stayed physically disconnected. Three forward/reverse command cycles completed with disarm confirmed afterward. Actual travel/direction and combined physical choreography remain to be rehearsed.
- LiDAR is healthy at about 15 Hz after Jim swapped SDA/SCL. The real 64-zone crowd grid still refreshes about 1 Hz via native detail, in sensor order. It is a stylized range view, not a calibrated map. Jim previously confirmed its response on Petey Explore.
- Opal reserves C6 **172.23.44.190**, Petey **172.23.44.123**, on SOIT-Field. Its 2.4 GHz width is 20 MHz, channel Auto, maximum TX power; 5 GHz unchanged. C6 external antenna is already selected. RSSI remains weak around -81 to -86 dBm: place its antenna clear of metal and recheck at the venue. Do not choose a fixed channel without checking venue conditions.

## Verification and limits

- Runner: **28 unit checks**. Browser: **8 checks**, including editing, repeat preferences/no autostart, uncalibrated combined blocking, STOP/Escape and phone layout.
- S3 orientation/trim, mast policy/hardware, drive-power, protocol/link/Wi-Fi and sensor checks pass. Power tests exercise actual acquisition windows, short reads, current peaks and voltage sag retention. SH2 regression reproduces the original missing-reply hang and verifies bounded replies, explicit deadlines, clock wrap and recovery.
- Production crowd-grid and bounded detail/JSON-stream tests pass, including a real native snapshot round trip, every truncated prefix, escaping, invalid data and chunk failures. Both final firmware builds pass.
- Recovered S3 crash shows LoadProhibited in Wi-Fi `scan_parse_beacon`, matching the documented rapid scan/teardown failure. The missing dwell/debounce policy is now retained. Initial merged S3 passed three finite recovery-radio cycles; the final v6 passed another two. S3 also stayed up during final C6 OTA. Intentional radio transitions briefly made telemetry stale, and can stop playback; that is not permission to relax its timing checks.
- Earlier C6 diagnostics stress exposed restarts. After bounded decode/range caching and bulk TCP coalescing, the final build passed **35 combined feed/diagnostic checks over about 61 seconds**: no resets, all grids fresh, no added frame/detail errors or drops, outputs OFF. This is a short regression check, not an event-length reliability guarantee.
- Final crowd GET timing: **20/20 successful**, median **40.55 ms**, range **20.39–98.93 ms**. Earlier TCP comparison reduced status median68.48 to28.49 ms and crowd94.34 to42.27 ms. These are PC/LAN HTTP timings; they do not measure camera or end-to-end LiDAR lag.
- Final repeat/STOP and missing-calibration checks pass on the installed gateway. Motion protocol was checked with motors disconnected; physical mast choreography is not commissioned.

## Petey and camera

Petey's installed event image is `3a899d6b5121244acf755f201fbb945c500604ea1a7a6dcd4124371abc0c9c9f`; normal host491/0, event35/0. Tap Explore on badge home for the real grid and stylized eyes, then Camera for video, with LiDAR one tap away. Existing settings/SD were retained and private event services remain closed. Petey was not reachable during the latest Gladiator checks; no new live Petey confirmation is claimed.

The camera viewer is implemented, but **zero real camera frames have been commissioned**. ESP32-CAM is still unreachable at saved192.168.8.2; Jim will check power when practical, and its programmer is inaccessible. Once powered/reachable, join CAM itself to SOIT-Field with its existing authenticated maintenance setup, reserve its Opal IP, then save that private IP in C6 camera setup. Petey streams directly from CAM port81 `/stream`; close other viewers because CAM supports one viewer. Source uses QVGA/latest-frame capture. Petey drops queued frames, has a separate decoder, limits decode rate and hides frozen frames; live FPS/latency/reconnect/memory still need measurement on the real feed.

Petey polls crowd every200 ms in Explore/Camera with station sleep disabled there, restored on exit. Faster polls cannot remove the 1 Hz grid source interval. Its SD worker stack was increased to32 KiB after measured64-byte headroom; the final short capture had8256 bytes free and no reset. The earlier Petey panic cause remains unconfirmed. No full camera-load or event-length endurance test was performed. A temporary PC stream/firewall attempt received zero frames; no firewall rule or test server remains.

## Remaining field acceptance

Power the robot down and charge it now: the final handoff reading was13.85 V. Charge before the next rehearsal. Finish remaining mast physical work and measured calibration, preserving the saved tilt values. Reconnect tracks only when ready to rehearse actual directions/travel; tune short cues on the van floor and export the accepted routine. Then check the mounted Petey display, brightness/sound, real camera if available, router cold boot/rejoin, and event-length power/runtime. A brief radio test is not a physical Opal power-cycle test. LiDAR level-translation/electrical verification remains unrecorded.

Credentials and flash/ELF recovery copies stay local under `C:/PlatformIO/Gladiator/diagnostics/booth-20261022/` and the Petey project's private evidence folder. See `validation.json` for hashes and current checks; the canonical `tools/booth/README.md` describes the reusable test tools. No movement sequence is left running.


## October23 saved-settings software update

A tested gateway-2.4.0 operator update is prepared but not installed. It adds saved/applied calibration status, apply/readback without motion, reusable commanded poses and direct entry to manual aiming. See the sibling event-operator-20261023 release folder or canonical docs/SAVED_SETTINGS_OPERATOR_2026-10-23.md. The last installed gateway remains2.3.9 until live deployment is verified. Current pan work and saved measurements were not changed by this preparation.


October23 current install: C6 gateway-2.4.3 is installed and USB/readback verified, with saved tilt revision4 intact and S3 v6 unchanged. Saved-profile controls, poses, repeats and read-only USB field checks are ready. Pan/full angular calibration, physical motion, actual camera frames and continuous Opal testing remain pending. See C:/PlatformIO/Gladiator/docs/SAVED_SETTINGS_OPERATOR_2026-10-23.md and NAS event-operator-20261023/README.md.


October23 network follow-up: Opal rejoin verified; 180-second read-only LAN check passed with zero HTTP errors and median crowd GET36.3ms. Both controller boots and saved tilt record4 unchanged; outputs off. All-user PC fallback profile replacement explicitly approved and applied (stored WPA2PSK/AES, activeCCMP). Operator kit now includes Opal LAN health check.cmd. Camera, working battery/full pan calibration, physical and event-length rehearsal remain pending.


## October 23 evening: boot-loop fix, eye fix, field troubleshoot page (installed)

**Installed now:** S3 **Mast operator v13 / I2C bus recovery** (app0, COM13, SHA in `diagnostics/i2c-bus-recovery-20261023/s3-installed.json`); C6 **gateway-2.4.9** (ota_0; 2.4.8 kept in ota_1). Saved mast setup revision 8 unchanged; tracks disarmed, mast off; no motion commands sent.

**Boot loop (S3 restarting every ~7 s, `SENSOR WATCHDOG stage=1`):** a read that times out part-way leaves a sensor holding SDA low (GPIO8 read LOW even in the ROM bootloader). The ESP-IDF 4.4 I2C driver then never returns, the task watchdog reboots, and because a software reset does not power the sensors down, the next boot hangs the same way. v13 (`src/sensors/I2CBus.h`, `SensorManager.cpp`):
- clears the bus (9-18 SCL clocks + STOP) at boot and whenever SDA/SCL is low before a transaction; never calls the driver on a stuck bus;
- after 3 sensor-watchdog resets in a row it stays up without the sensor watchdog (drive/link/display keep working, sensors report OFFLINE, battery unmonitored) instead of looping; a minute of normal running clears the streak;
- counters in S3 native detail `bus.stuck / recoveries / hangResets / watchdog` (`diagnostics/i2c-bus-recovery-20261023/read_bus.py`), UART lines `I2C bus stuck (...)`.
- Host test `tests/i2c_bus_recovery_test.cpp` (mid-byte clear, boot clear, permanent SDA/SCL faults refused without driver calls). Live: survived a cold boot on a fresh pack, 0 stuck events so far. The mid-transaction hang path and the 3-hang breaker were not reproduced live.

**Eyes flashing:** installed 2.4.7 raised ALERT whenever the LiDAR saw anything under 500 mm, even parked. 2.4.8+ alerts on proximity only when ARMED/DRIVE; battery LOCKOUT/CRITICAL always alerts. `/api/visual` now reports `alertReason` (BATTERY / PROXIMITY / EXPRESSION). Test `tests/visual_state_test.cpp`; the old rule fails it. Live: SAFE at 408-418 mm shows `ready`. ARMED proximity alert not checked live.

**Field troubleshooting:** **http://172.23.44.190/help** (venue router) or **http://192.168.8.1/help** (robot's Gladiator-Gateway Wi-Fi, no router needed). Live checklist (brain/restarts, battery, power monitor, IMU, LiDAR, radar, mast, link, eyes + reason, router RSSI, gateway, camera) with fixes, plus steps for boot loop, eyes alert, sensors offline, lost connection, camera, won't drive. Read-only; linked as **Troubleshoot** on the drive page.

**Notes from tonight:**
- A second 4S pack went from 14.4 V to 9.6 V (2.4 V/cell) under ~0.3 A; it was disconnected. Check that pack before charging it.
- S3 Wi-Fi OTA (`/update`) returned `ESP_ERR_OTA_VALIDATE_FAILED` for v12 and the current image was retained. Update the S3 over the UART cable (`diagnostics/i2c-bus-recovery-20261023/install_s3_uart.py`; v11 fallback image `diagnostics/lidar-fast-20261023/s3-v11-recovery.bin`).
- The Windows PC kept dropping the Gladiator-Gateway Wi-Fi (no internet); reconnect with `netsh wlan connect name=Gladiator-Gateway`. Phones may prompt to "stay connected".
- Codex's half-applied /help edits (duplicate include/handler/routes, garbled link) were cleaned up before building.

## October 23 night: camera to Petey and LiDAR latency (installed)

- S3 **Mast operator v14 / I2C bus recovery / 15 Hz range grid** (COM13, app0; receipt `diagnostics/stream-latency-20261023/s3-v14-installed.json`, v13 kept as fallback). Only change: the compact grid is sent once per LiDAR sample (`shared/RangeGrid.h` PERIOD_MS 200 -> 67). The gateway now receives **13.8 grids/s** (was 5), median age **70 ms**, crowd GET ~33 ms. Gateway unchanged (2.4.9).
- Petey: Camera page no longer bounces back to LiDAR; camera now **14.9 fps** with 0 dropped frames (was ~8), decode 60 ms (was 81); LiDAR grid on Petey ~195 ms old (was ~300). Details and rollback in Petey `docs/EVENT_2026-10-24.md`.
- Camera stream to a PC: 14.9 fps, 5.3 KB frames, steady 67 ms spacing. Camera quality 14/20/25 changed decode time only slightly; left at 14.
- 2-minute check with Petey streaming: no S3/gateway restarts, all sensors OK, gateway RSSI -49 dBm.
- PC: use **SOIT-Field-5G** (keeps the PC off the 2.4 GHz channel the robot, camera and Petey share).
- Not measured: glass-to-glass camera latency; event-length run with camera streaming.
- Camera picture was upside down: now rotated 180 deg (vflip + hmirror). Camera **masthead-1.2.1** saves flip/mirror in its NVS when changed (drive page "Camera image settings") and restores them at boot; verified across an OTA reboot (`diagnostics/stream-latency-20261023/cam-1.2.1-installed.json`). Jim confirmed the picture is correct on Petey. Camera source is still only in Codex's folder: `C:\Users\jimsc\.codex\visualizations\2026\10\14\01a13b42-...\final-integration\firmware\cam` (1.2.0 rebuilt byte-identical before the change).

## October 23: battery use from the flight recorder (`diagnostics/power-20261023/`)

- Electronics-only load is steady **~3.2-3.3 W (0.20-0.21 A at 15.5 V)**; current rises only as pack voltage falls (regulators draw constant power). No leak is visible on the monitored side of the INA226; anything wired before the shunt would not be seen.
- Second ("fresh") pack started at 15.86 V (3.96 V/cell, partly charged), ran ~125 min, delivered **~450 mAh**, stayed flat to ~15.2 V for ~110 min, then fell off the knee to 12.3 V. Jim switched off at very low voltage.
- First pack started at 14.84 V (3.7 V/cell, nearly empty) and collapsed to 5.6 V after ~136 mAh (2.4 V/cell seen): over-discharged; inspect and check per-cell voltages before trusting it.
- Idle runtime estimate for a fully charged pack: about 0.8 x capacity / 0.21 A (e.g. 1500 mAh ~5.7 h, 2200 mAh ~8 h); driving adds more. Charge both packs to 16.8 V on a balance charger and compare cells.

