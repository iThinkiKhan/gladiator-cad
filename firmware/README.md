# Gladiator

**2026-10-09: mast is FRONT.** Logical LEFT is the native-USB-side driver;
RIGHT is the USB-to-UART-side driver. Wiring is unchanged; both track polarities
are reversed in software. See [orientation](docs/ORIENTATION.md). Do not invert
the phone/C6 controls a second time. `/api/status` reports `MAST_FRONT` and pins.

**Next milestone: [Interface v1](docs/INTERFACE_V1.md).** Field controls on the
phone, one C6 development interface, independent S3 recovery service. S3 remains
the authoritative controller. Implementation is built and host-tested; paired
firmware installation and physical acceptance remain.

Sensor Core v1 firmware for an ESP32-S3 tracked robot using two BTS7960 motor
drivers. BLE and field-web drive control remain available. A dedicated
sensor task provides modular INA226, BNO085, SEN0628 8x8 ToF and SEN0610 C4001
drivers, native measurements, derived values, timestamps, independent sampling
rates, and sensor health. The INA226 and BNO085 are connected. The SEN0628 driver
was bench tested on 2026-09-09 against the real sensor using the CYD rig in
`src/bench/`, at a steady 15 Hz with no bus or protocol errors, but the sensor is
not yet installed on the chassis. The SEN0610 still requires a physical bench test.

A Seeed XIAO ESP32C6 runs the separate `gateway/` communications coprocessor:
external-antenna Wi-Fi, one phone field interface, a tabbed development site,
saved network settings, and authenticated C6 OTA. **The S3 is the authoritative
brain** for motors, safety, sensors, ownership and future autonomy. Gladiator
Link v2 carries typed, rate-controlled messages over preferred UART
(S3 TX4/RX5 ↔ C6 RX17/TX16) or authenticated Wi-Fi, with sustained-loss failover,
stable UART recovery, and optional Wi-Fi bandwidth leases. Native sensor detail
and retained logs are requested explicitly. See [Gladiator Link architecture
and validation guide](docs/GLADIATOR_LINK.md) and [gateway setup](docs/NETWORK_GATEWAY.md).

The paired v2 firmware must be built and installed on both boards. This change
has host/browser validation; physical cable-loss, radio coexistence and motor
watchdog timing still require the bench procedure in the architecture guide.

See [Sensor Core architecture, wiring and bench guide](docs/SENSOR_CORE.md).
C6 `/dev` contains the development tools; S3 `/service` contains recovery and
firmware maintenance. S3 `/api/sensors` exposes the complete snapshot. Send `sensors` over USB serial for the same JSON.

The PlatformIO target is configured for the installed N16R8 module: 16 MB flash,
8 MB octal PSRAM, and Espressif's 16 MB dual-OTA partition table.

## Pin map

| Track | Signal | ESP32-S3 GPIO |
| --- | --- | ---: |
| Left | R_EN + L_EN (tied) | 2 |
| Left | RPWM | 42 |
| Left | LPWM | 41 |
| Right | R_EN | 16 |
| Right | RPWM | 17 |
| Right | L_EN | 11 |
| Right | LPWM | 12 |

R_IS and L_IS are unused. The S3 ground, both BTS7960 logic grounds, and battery
ground must be common. Motor power comes from VBATT at the drivers, not USB.

## First test

1. Put the chassis on blocks so both tracks are clear of the floor.
2. Build and upload the `gladiator_s3` PlatformIO environment on COM25.
3. Open the phone app, choose **Drive**, connect to **Gladiator**, then arm.
4. Select 25% and briefly hold each direction.
5. Forward must now move toward the mast. Both drivers are software-inverted
   relative to the historical powered test, with logical tracks exchanged.
   Confirm forward, reverse, and both turns with tracks clear before driving.

## INA power monitor wiring

Do not use GPIO19/GPIO20 for I2C while this S3 is programmed through native
USB: those pins carry USB D-/D+. The installed INA226 uses SDA=GPIO8 and
SCL=GPIO9.

The module was identified as an INA226 with an R002 (0.002 ohm) shunt. Firmware
auto-detects its address from 0x40 through 0x4F (0x4A/B reserved for the IMU), reads bus and shunt voltage
directly, and calculates current using the installed shunt value. Serial and
the phone Drive tab report live voltage, current and power plus minimum voltage
and peak absolute current since boot.

## Status light

The onboard WS2812 (GPIO48) is the only status channel that works with no
cable, no phone and no Wi-Fi client. If the light stays dark, the board is a
revision that wires it to GPIO38: change `STATUS_LED_PIN` in `src/BoardConfig.h`.

At boot the controller announces why it last restarted, then switches to live
status. Highest priority wins:

| Light | Meaning |
| --- | --- |
| Two short green flashes | Ordinary start; live status follows |
| N red blinks, repeated 3x | Abnormal reset: 2 brownout, 3 panic, 4 task WDT, 5 interrupt WDT, 6 other WDT, 7 unknown |
| Amber solid | Driving; outputs are live |
| Amber 2 Hz | Armed and idle; it can move without warning |
| Red 1 Hz | Maintenance AP is not running |
| Magenta double-blink | I2C bus down, or the power monitor went offline |
| Blue solid | Phone connected over BLE |
| Cyan solid | A Wi-Fi station is associated |
| Green breathe | Healthy: AP up, safe, nobody connected |

A red blink code that repeats forever instead of giving way to live status is a
reset loop, and the code says why. A host opening the USB serial port resets
the S3 on purpose (raw reason 0x15/0x16); that is suppressed and never reported
as a fault. `/api/status` and the `sensors` snapshot both carry `led`, `apUp`,
`apStations`, `resetReason`, `resetRaw`, `resetBlinkCode` and `bootCount`.

`bootCount` lives in RTC memory: it survives a reset but not a power cycle. A
count above 1 on a battery that never left the chassis means the controller
restarted itself rather than being restarted by someone.

The light is capped to `STATUS_LED_MAX` (40/255) so it is not a meaningful load
on the battery it reports about, and the RMT write is issued only when the
colour actually changes.

## Wireless maintenance and OTA

The controller creates a WPA2 recovery access point at boot and during C6 link
failure. After stable UART recovery, its Wi-Fi shuts down when no service client
is connected. Existing BLE remains idle/available; battery-critical radio
shedding takes precedence over communications recovery.

- Network: `Gladiator-Setup`
- Wi-Fi password: `GLADIATOR_MAINTENANCE_AP_PASSWORD` in `shared/secrets.h` (gitignored; copy `shared/secrets.example.h`)
- Recovery field interface: `http://192.168.4.1/field` (S3 root opens service)
- Recovery service and S3 OTA: `http://192.168.4.1/service`
- Normal C6 phone interface: `http://192.168.8.1` (Gladiator-Gateway)
- C6 development website: `http://192.168.8.1/dev`

The field page provides the shared hold-to-run drive controls and five power
levels. C6 `/dev` adds controller testing, four sensor views, communications,
system, logs and firmware tools. S3 `/service` is recovery-only, with disarm,
fault evidence, retained logs and S3 firmware upload. Direct fallback driving is
an explicit recovery link to `/field`. Legacy S3 command APIs remain compatible.
BLE and web control retain their established ownership and deadman behavior.
Upload `.pio/build/gladiator_s3/firmware.bin` for S3 firmware maintenance.
Both browser and PlatformIO OTA updates immediately coast and disarm the motors.

For direct PlatformIO OTA, connect the computer to `Gladiator-Setup`, then run:

```powershell
pio run -e gladiator_ota -t upload
```

The OTA password is `GLADIATOR_OTA_PASSWORD` in `shared/secrets.h`; put the same value in `platformio_local.ini` (gitignored; copy `platformio_local.ini.example`). USB upload remains the default
environment and recovery path.

The build regenerates the application image without an appended SHA-256 trailer
to avoid an activation fault in this ESP32-S3 Arduino toolchain. The ESP image
checksum remains enabled, and authenticated PlatformIO OTA also verifies the
complete source MD5 before activation.

Normal 25/50/75/100 modes use a soft-start ramp. Overdrive immediately applies
100% PWM duty, which passes the available VBATT through the BTS7960; after the
normal 100% ramp completes, its steady-state electrical output is also full
duty.

Straight-line drive is trimmed in both directions, measured on 2026-09-08 with
the BNO085 game rotation vector rather than estimated by eye. Commanding unequal
tracks bypasses the trim, so the raw asymmetry could be swept directly:

| Direction | Measured veer | Balance point | Constant | Result at 50% |
| --- | --- | ---: | ---: | --- |
| Forward | `0.580*d + 13.08` deg/s | `d = -22.5` | 22% | 39/61, +1.1 deg/s residual |
| Reverse | `0.645*d - 9.30` deg/s | `d = +14.4` | 14% | -43/-57, -0.3 deg/s residual |

`d` is left minus right. The signs differ only because both tracks invert in
reverse; in magnitudes the same track is held back either way. Untrimmed the
chassis veered about 13 deg/s forward and 8 deg/s in reverse.

The trim applies only when both tracks are commanded equal and non-zero in
normal modes; turning and Overdrive are untrimmed. Above roughly 78% the
opposite track saturates and the correction stops growing. The constants were
measured at one power level on carpet, so they assume the asymmetry scales with
commanded power. A 22% imbalance is large enough to be worth investigating
mechanically rather than only compensating for in firmware.

The outputs coast and disable on button release, DISARM, BLE disconnect, invalid
command, or 350 ms without a fresh command frame.
