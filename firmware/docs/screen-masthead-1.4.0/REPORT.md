# Masthead screen style upgrade: masthead-1.4.0 (INSTALLED 2026-11-19)

2026-11-19. Jim asked for maximum "cool factor" on the masthead screen. He was calibrating the mast at the time and said to ask before flashing, so **nothing was installed and no commands were sent to the robot**. The CAM is still running masthead-1.3.6.

## What changed (cam/ only)
- `cam/src/FaceRender.h` (new): all screen artwork.
  - Angular visor eyes with a two-ring glow, fixed scanlines, a glint that sweeps across, iris/pupil/highlight, blinks (with an occasional double blink) and READY saccades.
  - Eyes morph smoothly between modes and the colour cross-fades. A 240 ms glitch plays on a mode change.
  - Per-mode looks:
    - READY: cyan, glances around.
    - SCANNING: blue, with a sweep beam and the pupils locked to it.
    - ENGAGED (S3 DRIVE): orange, angry slant, brow blades, flicker.
    - ALERT: red, wide eyes, shaking pupils, flashing hazard triangles.
    - HELLO: green arcs with sparkles.
    - OFFLINE: dim bars, "STANDBY".
  - Pupils widen and the eyes narrow as the real front LiDAR range closes.
  - Header: italic GLADIATOR wordmark, accent stripes, a mode pill (CHECK amber / FAULT red when there is a problem), and a sweeping underline.
  - Footer: battery icon with a voltage bar coloured by the S3 battery state, front range with proximity segments, Wi-Fi bars plus dBm, and the operator message or gateway line.
  - Status dashboard: icon, title, action, six health tiles and the mast/link line. It has the same content and the same 12 s rotation rules as before (`opstatus::select` / `dashboard` unchanged).
  - Boot splash, about 2.7 s: the wordmark is revealed by a scan line, then real CAMERA / WI-FI / GATEWAY states, then a wipe into the face. Face and dashboard changes also use the wipe.
- `cam/src/FrameCanvas.h` (new): a full-screen 320x170 frame in PSRAM, and a changed-tile push (32x10 tiles) against a mirror of the glass.
  - Removes the old 500 ms header/footer flicker.
  - Roughly doubles the frame rate at the same 4 MHz SPI clock.
- `cam/src/main.cpp`:
  - `render()` now builds a `face::Scene` from the same data as before.
  - A full repaint is forced after any display reinit or test pattern / DC probe.
  - The text-only fallback is kept for when the PSRAM buffers can't be allocated or the panel is not 320x170.
- `cam/src/Config.h`: version `masthead-1.4.0`.
- Unchanged: display wiring, SPI mode/clocks (1 MHz init, 4 MHz draw), rotation, camera, OTA, indicator, Wi-Fi, all HTTP APIs.

## Data honesty
Every number on screen comes from data that was already there: S3 state/battery/volts, LiDAR nearestMm, diagnostics, CAM RSSI and camera state.
- The battery bar runs from S3 lockout (13.2 V) to a full 4S pack (16.8 V). It is a voltage bar, not a percentage.
- Nothing is synthesised, and the renderer sends no commands.

## Verification
- Build: `pio run -e gladiator_cam` SUCCESS. Flash 1,002,901 / 1,966,080 (51.0%), RAM 16.6%. Log: `build.log`.
- Candidate: `masthead-1.4.0.bin`, SHA-256 `58e6210df26d27eee4154934643a2e627b1c6577d94b337c11267174ffb53847`.
- PC preview (`tools/screen_preview/`) runs the real renderer and the real tile push against a fake panel.
  - The panel matched the frame on every one of 543 frames across 9 scenarios.
  - Simulated rates at 4 MHz: 11–15 fps in normal views, about 8.7 fps in ALERT (full-eye pulses), and a 222 ms worst frame (the first full paint).
  - The old firmware pushed a full 78 KB canvas every frame (about 156 ms, roughly 5–6 fps).
  - GIFs and the contact sheet are in `preview/`.

## Installed (2026-11-19, after Jim said "Yes, install it")
- DHCP changed: the CAM is now at **192.168.8.3** (role verified as masthead-camera), and this PC holds 192.168.8.2. The C6 /api/visual cameraIp already reported 192.168.8.3.
- Authenticated application-only OTA with `install/install.py`. The SHA-256 matched, the CAM rebooted, 1.4.0 reported, and the image was confirmed.
  - Now running from **app0**. **app1 still holds 1.3.6** for rollback.
  - NVS, Wi-Fi and camera orientation were untouched. No motion commands were sent.
- After boot:
  - displayBuffered true; free PSRAM went from 3,921,995 to 3,782,459 bytes (−139.5 KB = two 320x170 frames minus the old 320x122 canvas);
  - free heap about 151 KB;
  - display 320x170 at 4 MHz, 1 initialisation, no test pattern.
- 30 s monitor (`install/stability.json`): same bootId throughout, 0 gateway poll errors, steady heap, indicator "ready". **Measured 11.5 frames/s** on hardware in READY (1.3.6 managed about 5).
- Still not checked: how the artwork looks on the physical panel (Jim to eyeball), CPU time per frame, and longer endurance with video streaming at the same time.

## Not verified
- Not run on the real CAM or panel. Colours and brightness on the real IPS panel are untested.
- ESP32 render CPU time is assumed (12 ms), not measured.
- PSRAM allocation of the two 108,800-byte frames has not been seen on hardware (about 3.9 MB was free on 1.3.6).
- The mode-change glitch effect lasts 240 ms. Don't mistake it for the old DC wiring fault: a real fault shows static or a blank panel that persists.

## Install (when Jim says go)
Authenticated CAM OTA, as for 1.3.6 (`diagnostics/screen-recovery-20261109/dc-probe/install.py` pattern). 1.3.6 stays in the other slot for rollback.
