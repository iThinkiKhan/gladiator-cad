# Gladiator operator integration — 2026-10-14

Open **http://192.168.8.1/** on Gladiator-Gateway Wi-Fi. The field page combines live video, mast aiming, driving and display expressions. Field operation needs no maintenance key. Firmware/network maintenance and persistent camera-address setup retain their existing key.

## Operator controls

- Start video explicitly. The existing ESP32-CAM feed remains `http://192.168.8.2:81/stream`, with one viewer at a time. Video stays visible while scrolling the phone controls. Stop the native phone viewer before starting the browser viewer.
- Enable mast only after saving measured calibration. Check the clear-area confirmation and press **Enable at neutral**. This deliberately starts PWM at the saved neutral pulses; a displaced SG90 may move immediately. It does not measure or discover the current pose.
- Hold the pan/tilt arrows to aim; release to hold. Adjust speed from 1–30 head degrees/second. **Center** moves smoothly to calibrated zero. **Scan** sweeps the saved pan limits with tilt at zero. **Hold / stop scan** arrests the current trajectory. **Mast OFF** removes both PWM signals. Drive **DISARM** also requests Mast OFF.
- Mast aiming and driving may operate together. Calibration and single-output pulse tests require disarmed, stationary tracks. Both remain under S3 power/safety authority.
- Drive power may change while armed or moving. Normal modes retain smooth ramping; lowering power caps actual PWM immediately. The S3 ceiling applies after trim and ramp. Overdrive remains an explicit selection. Mast is the fixed FRONT for phone, website and S3; the obsolete front/rear client inversion is removed.
- Camera image settings expose QQVGA/QVGA/VGA/SVGA resolution, brightness −2…2, automatic/manual exposure 0…1200, vertical flip and horizontal mirror. They are read back from OV2640 and reset on camera reboot. These controls do not change TFT orientation. The C6 camera proxy runs separately so an offline camera cannot block drive HTTP requests.

## Existing servo wiring and PWM

GPIO10 and GPIO13 remain connected as installed. Test each to identify the axes, then select their roles in the saved profile; swapping wires is unnecessary. Pan10/tilt13 are provisional defaults. The S3 validates that the profile uses this pair exactly once each.

| Resource | Assignment |
| --- | --- |
| Mast GPIO10/13 | LEDC channels 4/5, dedicated low-speed timer 2, 14 bits |
| LEFT drivetrain | EN2, PWM42/41, channels 0/1, timer 0 |
| RIGHT drivetrain | EN16/11, PWM17/12, channels 2/3, timer 1 |
| Existing shared I²C | SDA8 / SCL9, 400 kHz, SensorManager worker |
| C6 UART | TX4 / RX5 |
| Bench power / status | GPIO7 / GPIO48 |

GPIO10/13 are output-capable and unused by the audited drivetrain, I²C, UART, native USB and PSRAM configuration. GPIO6 is no longer assigned to a mast gate. No external hardware watchdog/interlock is required by this firmware. Servo supply remains regulated separately with common ground; PWM OFF does not switch off that supply or guarantee holding torque.

## Installed commissioning from the field page

1. Disarm drive. Open **Installed servo testing & saved calibration**. Test one GPIO at a time while observing the installed mast and cables. Verify the labelled SG90 units behave as positional servos; the label alone does not establish usable pulse span, frequency or clearance.
2. Choose the first pulse deliberately and a small low/high pulse window. The form leaves pulse values blank rather than assuming current position. Validation accepts 500–2500 µs and 50–100 Hz as parser ceilings, not a declaration of safe SG90 specifications. A test window cannot exceed 500 µs. Begin much smaller where clearance requires it. Press **Start single output test**; the first pulse may move the unknown pose.
3. Use **Move to test pulse** for observed adjustments. Subsequent pulses slew at 100 µs/s. The test stops after 10 seconds without a new target, unsafe power, track arming or a control-loop gap over 100 ms. Press **Outputs OFF** before starting the other pin or changing the test window.
4. Identify pan/tilt GPIOs and establish a repeatable physical forward/neutral pose. Record measured low, neutral and high pulse values, corresponding negative/positive servo SHAFT angles relative to neutral, and whether increasing pulses moves the head negatively. A neutral at an endpoint supports one-sided limits; do not claim clearance on both sides unless tested.
5. Pan uses the installed **60T driving / 40T driven = 1.5** ratio: head angle = shaft angle ×1.5. Thus ±45° head motion requires ±30° shaft travel. Enter measured shaft angles and desired HEAD limits separately; the S3 performs conversion for every move, jog and scan. Tilt ratio is 1. A reversed axis exchanges pulse directions without changing the ratio.
6. Start with narrow observed clearance, such as ±5° head pan and ±3° tilt, or a smaller one-sided range. Expand only while checking cables, supports, pulleys and hard stops. Firmware ceilings are ±45° head pan and ±20° head tilt; saved limits can only be narrower. No modulo rotation or accumulated turns can wind cables beyond the saved range.
7. Check the installed-verification box and **Save calibration (outputs off)**. Wait for the S3 action to report calibration saved. A gateway HTTP 202 means queued, not accepted by S3. Calibration is saved in S3 NVS and loaded after resets; current position and enabled state are never restored. **Load saved values into form** lets you revise calibration without USB.
8. Close commissioning and deliberately enable at neutral. Test directional buttons, Center, Scan, Hold and OFF under observation. If the axis direction is wrong, switch OFF, correct its reversed flag and save. A reconnect, reload or another browser tab cannot acquire an existing mast session automatically.

The SG90 has no external position feedback. Telemetry reports commanded estimates. Firmware cannot detect slipping belts, back-driving, a servo's own power-up behavior or an incorrect physical calibration. Software outputs are detached on startup/reset and after lease/safety failures; a powered head may still need support when PWM stops.

## Startup, stopping and sensor behavior

The S3 boots with servo pins as pulled-down inputs. Loading calibration never attaches PWM. After deliberate enable, the owning field page renews a 750 ms lease. Browser background/blur, link generation changes, unsafe power or a loop gap over 100 ms stop PWM; returning requires another deliberate enable. No automatic scan or motion replay occurs.

Operator scan remains bounded even when LiDAR is unavailable. Unknown/invalid readings do not become obstacles. Fresh valid range under 500 mm or fresh valid radar presence stops the sweep at its commanded pose. Autonomous attention motion is reserved for later work; the existing sensor-driven display priorities remain active: valid nearby returns alert, valid presence can greet, S3 scanning selects scanning eyes, and stale/unsafe controller state overrides operator expressions. LiDAR alone does not classify people.

TFT output is rotated by `(existing base rotation + 2) % 4`, preserving private panel dimensions and rendering. Camera orientation remains at its established default unless deliberately changed using the new image controls.

## SEN0628: 5 V power is not 3.3 V I²C

The vendor specifies 3.3–5 V supply. Its
[V1.0 schematic, sheet 4](https://dfimg.dfrobot.com/wiki/21121/SEN0628_rp2040-8-8-matrix_schematics_v1.0.pdf)
shows a 2N7002 dual-FET level shifter and connector-side 10 kΩ pull-ups to **VIN**.
With the sensor powered from deck-one 5 V, the Gravity connector can therefore
idle near 5 V. Its internal RP2040 runs near 3.3 V; that does **not** make the
external connector safe for the S3.

- Sensor VCC to regulated deck-one 5 V; sensor GND to common ground.
- Sensor SDA/SCL to the **5 V side** of a bidirectional I²C level translator
  rated for the existing 400 kHz bus. Translator low-side reference/pull-ups to
  S3 3.3 V; low-side SDA to GPIO8 and SCL to GPIO9. Keep existing 3.3 V devices
  on that low side. Never connect 5 V pull-ups directly to S3 pins.
- Before connecting GPIO8/9, measure both signal sides powered and idle;
  verify the S3 side stays near 3.3 V and has suitable rise times on the assembled
  bus. Inspect total parallel pull-ups rather than blindly adding more. If the
  installed board revision differs, inspect its circuit and measure it too.
- Confirm I²C mode/address selectors. The driver discovers 0x30–0x33 and requests
  8×8 mode. Keep the vendor startup settle delay (5 seconds), bounded reads and
  retries. No additional Wire owner or blocking ranging loop was added.
- Remove the protective film. The vendor's
  [firmware 1.3 guidance](https://wiki.dfrobot.com/sen0628/docs/21564) describes
  invalid-value fixes; record the installed module firmware and, if older,
  update it using the vendor procedure with S3 I²C disconnected and safe power.
  Sensor firmware was not changed in this session.

The existing SensorManager, typed RANGE telemetry and native 8×8 grid remain.
On the C6 `/dev`, select Range and request inspection to see all 64 native zones;
the normal field page shows the valid nearest distance. Bad transport/status,
short payloads, values below 20 mm, 4000/no-return, or larger invalid values cannot
produce valid detections. All-invalid frames are healthy communications with
`valid:false`, zero usable zones and zero derived nearest distance. Native
values remain available for diagnosis. A failure clears derived distance;
stale data loses detection validity. Visual alerts require healthy data younger
than 500 ms. Empty/invalid data means **unknown**, not a guaranteed clear path.
The sensor is a demonstration behavior input, not a certified collision sensor.


## Firmware updates and event acceptance

Build S3, C6 and CAM with their existing private configuration. Do not publish compiled images, keys, full-flash backups or companion-app data. OTA is the intended primary update method; USB remains available for recovery. The S3 native web OTA path retains normal appended SHA256 image validation and reports exact native errors. Rejected or interrupted updates retain the running slot. Firmware upload stops drive/mast before writing.

See [deployment and control corrections](control-fix-20261014.md) for actual installation/verification status. Rejoin Gladiator-Gateway Wi-Fi after its AP restarts if a client retains a stale association. Its configured home-LAN address provides a second maintenance route.

Before the event, perform supervised physical acceptance: verify all four drive directions at 25%, measured PWM ceiling, installed axis/pulse/ratio mapping, cable clearance throughout saved travel, stops/background/reconnect/reset, video during driving/aiming, and all 64 LiDAR zones with invalid samples showing UNKNOWN. Run a sustained session on deck power. No physical mast or track motion was commanded by the agent, and LiDAR currently has no valid live samples.
