# Gladiator development state â€” November 9, 2026

**November 19, 2026** — Initial angular profile applied and verified on S3 from C6 revision 14. Camera-forward zero is pan 850 µs and tilt 1500 µs. Enforced limits are 9° left / 7° right and 1.5° down / 2° up. Both outputs were off. Physical camera aiming verification is pending. [Current mast setup](V2_MAST_CONTROL_SCHEMA.md).

**November 20, 2026 — Jim's status (supersedes older notes below):**
- C6 connectivity: intermittent. Jim's theory is antenna issues.
- C6 cold boot does not answer USB. Jim is working on this himself. In this morning's test, a cold-booted C6 received the USB commands (`receivedCommands` 3) but sent nothing back (0 bytes on all three). After a ROM reset back into the normal app, it replied normally. Evidence: diagnostics/connection-recovery-20261120.
- IMU orientation loss: Jim believes it was an I2C issue, which has since been resolved.
- Radar: never installed. Its OFFLINE status is expected, not a fault.
- Mast calibration revision 14 was re-verified on C6 and S3 after reboots on November 20.

The October 24 event is complete. Standard development is active; event launchers and Halloween display instructions are historical.

## Current state

- Canonical source: C:/PlatformIO/Gladiator. Preserve credentials, display orientation, camera flip/mirror and saved servo measurements.
- CAM recovered through its CH340 USB motherboard on COM9. Initial serial output showed download mode; a normal reset booted the intact Halloween image and its recovery Wi-Fi. This does not establish why it previously showed only a backlight on robot power.
- CAM masthead-1.3.6 is installed and confirmed in app1; app0 retains 1.3.5. Screen fault RESOLVED: purple DC was on IO12 instead of IO2. Jim corrected it and physically confirmed face/status. Normal hardware SPI mode 0, initialization 1MHz, drawing 4MHz, rotation 3; color test and DC probe OFF. Wiring: docs/MASTHEAD_DISPLAY_WIRING.md. Private pre-change 4MB backup: diagnostics/cam-usb-20261109.
- Mounted CAM video verified on robot power/network: 252 JPEG frames/20.078s (12.55fps), same boot, cameraError=0, no status HTTP failures. The slower bench-recovery-network result is historical. Stream and spotlight are off after testing; long-term harness reliability/endurance remain unverified.
- Board indication follows Jim's requested pattern: two short flashes once after local boot checks pass, then no healthy heartbeat. Blocking faults repeat every five seconds: 3 camera, 4 station Wi-Fi, 5 stale/missing gateway/controller data, 6 HTTP/network/main-loop fault. Initial network grace is 30 seconds; startup stalled beyond 10 seconds is a service fault. Both LEDs stay quiet during normal operation. Manual spotlight retains priority; status pulses are suppressed during video. White pulses are still 60 ms at duty 6/255; OTA retains its existing light-off behavior. A stopped/unpowered CPU cannot signal.
- CAM is currently role-verified at http://192.168.8.2/, with camera ready and fresh gateway data. C6 saved camera address is 192.168.8.2; verify role after future DHCP changes. Final video check: 141 complete JPEGs in 10s (14.1fps), same CAM boot, stream closed afterward. Evidence: diagnostics/screen-recovery-20261109/io2-corrected/verified.json.
- Installed and confirmed C6 gateway-2.4.15 in ota_1; the earlier 2.4.13 deployment is historical. See saved-position mast update below. UART task priority6 and separate RX diagnostics are included. Both the main page and development Overview now show live camera readiness, idle/streaming, address and Wi-Fi signal, with fault/stale/gateway-loss states and five-second polling. Development also shows firmware, frame/error counters and native camera diagnostics. This includes the previously built spotlight proxy/UI. Live browser checks matched hosted source and showed Ready / idle with no browser errors or command writes. S3 boot continuity and saved mast setup were verified unchanged; tracks remained disarmed and mast/test outputs off.
- Mounted check November9: initial 66s stable UART, outputs OFF, fresh 64-cell laser grids, healthy power/LiDAR and initially healthy IMU. Later IMU fused orientation dropped out; automatic recovery reached count7 and restored all ten reports/valid pose, but treat IMU as intermittent. Four earlier I2C recoveries, no additional bus recoveries between native snapshots. Radar remains OFFLINE, compass heading unqualified, mast angular calibration unapplied, endpoints revision8 unchanged. Final power about 15.84V/3.29W.


- V2 mast contract locked by Jim: docs/V2_MAST_CONTROL_SCHEMA.md and docs/v2-mast-control.json. Pan GPIO10 right500/neutral1500/left2000 us, lower=right with mast as front. Tilt GPIO13 down1150/neutral1450/up1450 us. Pan pulse limits are selected software limits, not physical stops; mast is mechanically free through360 degrees, but wires require bounded accumulated travel. Excessive belt slip and rotor/ring/pedestal retention remain blockers; Jim is reprinting rotor/ring. Pulse anchors were saved and verified in C6 commissioning record revision 12; no S3 angular profile or motion command was sent.


- C6 gateway-2.4.13 was prepared during the baseline monitor and subsequently installed during USB-powered link isolation. Separate UART/Wi-Fi diagnostics and main-loop/USB/OTA status were added. Loaded60s test accepted4927 UART frames/~1.43MB with0 new frame/detail/drop errors; S3 continuity and V2 record12 preserved. Evidence: diagnostics/c6-link-isolation-20261109/REPORT.md. This is a short USB bench result, not full field-power acceptance.


- Field monitor stopped for Jim's power-off after21.0min/609samples (planned30min, not completed). No C6/S3/CAM resets or HTTP failures; tracks never armed; Jim manually tested servos, assistant sent no motion commands. IMU had4 observed pose-loss windows and recovered; link added28frame/103detail errors under detailed polling, isolated further in a load comparison. During that historical baseline, candidate2.4.13 was not installed and C6 was2.4.12; see the later2.4.13 isolation result below. Camera remained ready but idle during this window, so no continuous-video endurance claim. Screen testing next. Full report: diagnostics/field-monitor-20261109/REPORT.md.


- Jim accepted the new bus and masthead distribution board as successful and in use. Current investigation used USB backfeed to power S3 electronics (~4.17V) with battery lockout and all motor/servo outputs off; no movement commands or power-protection override were sent.


- C6 initial USB isolation retained UART wires to an unpowered S3; rising legacy aggregate errors did not prove C6 hardware fault. Once backfeed powered S3, old2.4.12 accepted2255frames/~40s with0 new errors. After2.4.13 update, loaded link also passed. Direct USB-console replies are still unverified; HTTP diagnostics/OTA work and new main-loop telemetry is healthy.


- Battery-powered repeat on C6 2.4.13 completed60.266s/60samples: UART4959frames/1439758bytes,0new UART/frame/detail/drop errors, all core telemetry fresh, IMU pose valid60/60, no C6/S3 resets, all track/servo outputsOFF, V2 record12 unchanged; battery15.826–15.887V. Initial attempt stopped after39saved samples on a power-validity guard; readback recovered~15.90V with no proven voltage collapse, one intact-guard retry completed. Retain this separate sensor-validity transient. No movement/firmware/calibration commands. Evidence: diagnostics/battery-link-test-20261109/REPORT.md.

- 2026-11-19: CAM masthead-1.4.0 (screen style upgrade) INSTALLED by authenticated OTA after Jim approved it. It runs from app0, and app1 keeps 1.3.6 for rollback. New eyes/HUD and a changed-tile push: 11.5 fps measured, against about 5 before. Display wiring and SPI settings are unchanged. The CAM address is now 192.168.8.3 (role verified); this PC took .2. Verify the role before reusing a DHCP address. The look on the physical panel is still to be eyeballed by Jim. See diagnostics/face-style-20261119/REPORT.md.

## Remaining development checks

Flash visibility and quiet healthy behavior are physically confirmed. The mounted screen now works after correcting DC from IO12 to IO2; face/status are physically confirmed, camera works, and no tests remain active. Investigate the separate C6 panic restart with a recorded 2,656-byte allocation failure, intermittent IMU orientation loss, and longer video/harness endurance. See diagnostics/screen-recovery-20261109/io2-corrected/REPORT.md.

Jim selected Gladiator-Gateway for direct development. CAM station connection and C6 saved address are now verified at 192.168.8.2 (latest cold boot; verify device role). Camera DHCP assignment changed after the C6 reboot; identity was checked and the saved address corrected. A fixed DHCP reservation is not established, so recheck the address if the camera becomes unreachable after network restarts. Verify device role before using a DHCP address; 192.168.8.2 has belonged to both CAM and S3 on different boots. Confirm mounted video performance and physical display/battery presentation together; this camera-status check did not start video or enable the spotlight.

Keep servos and tracks off during camera work. Do not replace the incomplete angular profile with guessed angles. Mast calibration, physical camera/harness reliability and autonomy remain separate engineering work.

Receipts: diagnostics/camera-status-20261109 (C6 2.4.11/2.4.12 installations, saved camera addresses, main/development live read-only browser verification and screenshots), diagnostics/cam-boot-indicator-20261109 (current 1.3.2 build/install/reset/light/video checks), diagnostics/cam-usb-20261109 (backup, source-before, build, installed, video-check and images), diagnostics/status-20261108 (main-board samples), diagnostics/spotlight-20261031 (previous spotlight source work).



- Separate gateway fault discovered: C6 boot1604705851 resetReasonCode4(PANIC), previous failed allocation2656 bytes, while S3/CAM boots remained continuous. Root cause unproven; clean UART counters do not qualify gateway as field-ready. No C6 reset/update sent in screen work.

- Main-page saved-position mast control is installed: C6 gateway-2.4.15 and S3 Mast operator v15. C6 revision12 was copied to S3 without changing it: pan GPIO10 right500/neutral1500/left2000 us; tilt GPIO13 down1150/neutral1450/up1450 us. No angular measurements were invented and calibrated remains false; positionsReady=true enables normal manual operation. Main page: area-clear checkbox -> Arm mast at saved neutral -> hold arrows / Center / Disarm mast. Scan and angle targets remain unavailable in this mode. Opening/reconnecting does not arm. Live browser confirmed the arm path, exact saved profile and all outputs OFF; assistant sent zero movement commands. Physical operation after arming remains for Jim. Details: docs/MAST_SAVED_POSITIONS.md; evidence: diagnostics/mast-positions-20261109.
