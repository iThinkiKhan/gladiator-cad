# Codex Notes

Codex-owned durable observations and handoff notes.

2026-10-09 — Firmware GPIO side swap requested by Jim: left driver uses the
USB-to-UART/UART-side group GPIO16/17/11/12; right driver uses the native-USB-side
group GPIO2/42/41 with R_EN/L_EN tied on GPIO2. Updated BoardConfig, motor
enable handling, README wiring table, and SENSOR_CORE documentation.
