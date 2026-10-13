# Masthead firmware handoff

## 2026-10-13 — ESP32-CAM masthead firmware (Codex)

Jim requested a self-contained OV2640 camera/ST7789 visual subsystem through the existing S3 → C6 → Wi-Fi architecture, then authorized flashing/testing and publication for other agents.

- Entry point: [masthead firmware guide](../../../firmware/docs/MASTHEAD.md); [measured bench results](../../../firmware/docs/masthead/bench-20261013.md).
- Source: `firmware/cam/`, `firmware/gateway/src/VisualApplication.h`, `firmware/shared/VisualState.h`, and the masthead additions in `firmware/shared/FieldPage.h`.
- CAM OTA 1.1.2 installed/confirmed over Wi-Fi; wrong/corrupt images and interrupted transfers rejected safely; deliberate unconfirmed boot rolled back. Recovery AP works without C6 or camera. Keep the private CAM key; see firmware/docs/MASTHEAD.md. USB supplied power during tests; jumper-only power untested. OV2640 currently reports 0x105 again; resolve before sealing.
- Camera/C6 flashed; 90-second QVGA test achieved 14.92 fps. Ribbon reseating resolved initial OV2640 detection failure. Gateway reboot/reconnect passed; no camera reset was observed.
- TFT is NOT connected. Default 170×320 geometry and reset pull-up need actual module confirmation. Candidate SPI wiring is clock14/data13/DC2/CS15, RES pulled to 3.3 V; GPIO4 flash LED stays off; microSD unused.
- C6 has no live S3 telemetry in this bench. Offline state is intentional; the display API cannot override stale robot state or automatic alerts.
- Next: wire/validate screen, connect S3, test authoritative sensor effects, then run the 30-minute event soak. Preserve mast-front orientation, motor safety, existing secrets, and other agents' CAD work.
- GitHub contains source/config examples and aggregate results only. Private credentials, deployed binaries, and camera photos remain local. A fresh checkout must be configured before flashing.
