# Codex Notes

Codex-owned durable observations and handoff notes.

2026-10-09 — Firmware GPIO side swap requested by Jim: left driver uses the
USB-to-UART/UART-side group GPIO16/17/11/12; right driver uses the native-USB-side
group GPIO2/42/41 with R_EN/L_EN tied on GPIO2. Updated BoardConfig, motor
enable handling, README wiring table, and SENSOR_CORE documentation.

2026-10-09 — Jim superseded the old frame: mast is now FRONT. The pin-side
swap above describes the former mast-rear names, not current logical tracks.
Current LEFT: native-USB side EN2/RPWM42/LPWM41; current RIGHT: UART side
R_EN16/L_EN11/RPWM17/LPWM12. Both inverted, wiring unchanged. Orientation.h
transforms old trim and derived IMU chassis frame. See ../../ORIENTATION.md.
CAD coordinates unchanged; head viewing pose is legacy pan180, fixed neck
unmoved. Front-facing is at the existing range endpoint; no servo recentering.

OTA verified: image1524640 bytes, SHA256
7f42a21a58e819d8cfc3875456e0e31e68d33fc4dc8d9d3d8e126f4cb78cfeff;
boot3/app0 valid, SAFE/disarmed/outputs0,0, stable UART telemetry. Host tests
passed80802 track/trim and2025 IMU quaternion-frame cases. No physical motor
test; IMU/ToF/radar offline. Deployed S3 coexistence/heartbeat fixes also copied
into the shared firmware source; its secret macros preserved (no credentials
added). Original CAD/user-dirty work backed up on CAD server at
/home/buralien/gladiator-orientation-backup-20261009 before changes.
