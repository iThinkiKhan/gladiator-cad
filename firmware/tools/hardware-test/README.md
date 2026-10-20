# Gladiator V2 hardware bench

## Use from your phone — no PC required

With gateway firmware **2.2.2**, connect the phone to **Gladiator-Gateway** and open
**http://192.168.8.1/hardware-test/**. A Hardware setup & servo tests link is also
available on the existing driving page. Tap Connect to robot in the tester.
The page and assets are served by the C6 and use its existing APIs directly.
No local Python service, PC, Internet access or external script/CDN is needed.
Opening the page and connecting do not enable servo or track motion.

## Optional PC-hosted version

Run **Start-HardwareTest.cmd** in this folder, then open **http://127.0.0.1:8765/**.
The launcher uses PlatformIO Python (or Python 3); it installs no packages.
Connect the PC to Gladiator's network, enter the gateway address and click Connect.
This mode retains the restricted local API bridge. Keep its terminal open while
using the tester; Ctrl+C stops that service.

## Simplified interface

The page has four views: **Test servos**, **Save setup**, **Camera & aim**, and **System**.
Starting pulse automatically fills a small test window; range/frequency edits are under
Test range & frequency. Use the large +/− buttons and one-click center/endpoint recording.
Stop & test other servo turns outputs off, switches GPIO, and clears the first pulse.
Stop & review setup opens the calibration form. Recorded pulses and measured shaft
angles have their own expandable sections. Camera and aiming controls share one view;
raw sensor data and logs live under System. STOP ALL stays visible while scrolling.

## First installed mast test

1. Keep the mast visible and tracks disarmed. Use one controller page at a time.
2. Choose GPIO10 or GPIO13. Choose a first pulse deliberately; neutral is blank
   because the mechanism has never been referenced. 500–2500 µs and 50–100 Hz are
   existing firmware parser bounds, **not verified SG90 specifications**.
3. Set a small window (±50 µs helper), confirm supervision and start that GPIO.
   The first pulse can move immediately. Use 5/10/25 µs steps. The S3 limits the
   test window to 500 µs and slews subsequent changes.
4. Identify the axis and choose a useful neutral. Record with the matching
   “This is pan/tilt · save center” button. This records GPIO and commanded pulse,
   not a measured position. Stop output before changing GPIO/window or saving.
5. Record only pulse endpoints actually reached without binding. Enter measured
   servo **shaft** angles relative to neutral, pulse endpoints and smaller allowed
   head travel. Initial limits: ±5° pan and ±3° tilt. Pan head/shaft ratio is
   **60/40 = 1.5**, applied by the S3; do not apply it twice. Verify belt routing
   and direction. A zero shaft angle and corresponding neutral pulse support a
   neutral at one mechanical endpoint. Mark reverse if increasing pulses move negative.
6. Verify positional servo behavior and clearance, then Save calibration to S3.
   Wait for matching S3 profile readback. Export a draft as a backup. Loading or
   importing only edits fields; it never enables movement.
7. Confirm “Enable at saved neutral” and enable. This initial positioning may move
   both servos. Hold arrows to jog, release to hold, or use center/bounded scan.
   Apply speed updates the S3 rate. Disable after testing.

Raw GPIO testing deliberately bypasses the saved angular profile to establish it;
its explicit pulse window and S3 test lease still apply. The full parser range is
not a measured mechanical range.

## Stops and recovery

- **STOP ALL** requests mast/test OFF and drivetrain DISARM. It never arms
  or drives tracks. Check live S3 status; an unreachable gateway cannot confirm a stop.
- **Stop & hold** stops calibrated movement while retaining servo output.
  **Servos off** releases output; an unsupported mast may sag.
- Normal mast lease is 750 ms; raw test lease is 10 seconds. The default keepalive
  renews only this page's deliberately started, confirmed test while active.
- Focus loss/tab hiding sends OFF for a session owned here. Browser close, PC
  failure or lost Wi-Fi may prevent delivery; the S3 lease is the fallback.
- Startup, reconnect, stale telemetry, reset and session loss never auto-enable.
  No external hardware interlock is required by this tester.
- Existing S3 power checks, commissioning checks, PWM ownership, limits and motion
  authority remain in effect.

## Camera, face and sensors

Start video explicitly. The browser uses the existing ESP32-CAM stream advertised
by the gateway and needs a route to that camera (normally 192.168.8.2:81).
Use one video viewer at a time. Read settings before changing resolution,
brightness, exposure, flip or mirror. Settings reset on camera reboot.
Face selection is temporary for 30 seconds and subject to existing visual authority.

Sensor data comes from /api/field with health metadata. Missing values remain
unknown. The tester does not infer obstacles or add autonomous reactions.
Use the field controls link for driving.

## Phone access (optional)

Run: python serve.py --listen 0.0.0.0 --port 8765

Open http://PC-LAN-ADDRESS:8765/ on a phone on the same trusted LAN. Windows may
ask about firewall access. This development bridge has no login; do not expose
it outside the trusted robot network. Default launch binds only to this PC.
Browser tabs share a bridge connection; use one operator. The phone also needs
a route to the camera address for direct video.

## Compatibility and scope

Requires existing /api/mast, /api/mast/config, /api/field, /api/visual, /api/camera
and /api/control APIs. Missing or stale mast APIs leave motion unavailable.
Inspect installed firmware before an update. Hosting the page on the robot requires the C6 update. It does not require an S3
or camera update, and does not alter saved S3 calibration or drivetrain settings.

S3 stores calibration only after a successful save; the page confirms readback.
Exports are explicit local downloads. Frames, credentials and enablement are not saved.

## Verification

Run: python -B -m unittest discover -s tests -p test_server.py -v

Browser checks require Playwright and Chrome. Set GLADIATOR_NODE_MODULES to the
folder containing Playwright (or install Playwright normally), start serve.py on
port8765, then run:
node tests/test_ui.cjs

Tests use a simulated gateway, never hardware, and check startup/Connect writes,
pulse bounds, save readback, aiming, release/hold, focus stop, link recovery,
DISARM and phone layout. Installed clearance and behavior still require your tests.

On Windows, browser checks use installed Chrome by default. Elsewhere they use
Playwright Chromium. Set GLADIATOR_CHROME to an explicit browser executable if needed.
Test screenshots are written next to the tests and excluded from Git.

## Build the C6-hosted page

From firmware/gateway run: pio run -e gladiator_c6

The pre-build script embeds deterministic gzip copies of index.html, app.js and
styles.css in flash. HardwareTestAssets.h is generated and ignored by Git; edit
the original assets in tools/hardware-test. Four GET routes serve the page (with
or without trailing slash), script and stylesheet. Existing control APIs and
maintenance authorization remain unchanged.

For simulated direct-mode checks set GLADIATOR_NATIVE=1 and run tests/test_ui.cjs.
The default test mode checks the PC bridge. Neither mode contacts the robot.
