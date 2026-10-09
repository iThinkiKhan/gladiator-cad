# Gladiator Sensor Core v1

The firmware separates device behavior from data. The sensor worker owns the
I2C bus; motor, BLE, USB, and web code read snapshots. No sensor commands the
motors. Autonomous behavior and new current/voltage cutoffs are outside this
milestone.

## Hardware inventory

| Device | Interface | Address (7-bit) | Status at implementation |
| --- | --- | --- | --- |
| INA226, R002 shunt | I2C GPIO8/9 | Detected automatically in 0x40–0x4F, excluding 0x4A/B | Connected |
| GY-BNO08X / BNO085 | I2C GPIO8/9 | 0x4A or 0x4B | Driver ready; installation and physical bench test pending |
| DFRobot SEN0628 | I2C GPIO8/9 | 0x30–0x33 | Driver bench tested 2026-09-09 on the CYD rig; chassis installation pending |
| DFRobot SEN0610 / C4001 | I2C GPIO8/9 | 0x2A or 0x2B | Driver ready; physical bench test pending |

All addresses above are 7-bit. The example 0x52 address from the planning chat
does not describe this SEN0628 board: its RP2040 presents a different protocol.
The SEN0610 is a 24 GHz radar with I2C/UART interfaces, not a Wi-Fi peripheral.

The established motor pins remain right: 16,17,11,12; left: 2,42,41. Native USB
uses GPIO19/20. These pins and bus settings live in `src/BoardConfig.h`.
Bus speed is 400 kHz; each Wire transaction has a 10 ms timeout. Do not use
0x4A/B for an INA226 in this stack: these addresses are reserved for the IMU.

## Installing the BNO085 next

Disconnect USB and motor/battery power before wiring. Connect the module's
labeled VCC to 3.3 V, GND to common ground, SDA to GPIO8, and SCL to GPIO9,
in parallel with the INA226. Keep I2C pull-ups at 3.3 V.

The chip requires PS0 and PS1 low for I2C mode and BOOTN high for normal
operation. GY-BNO08X board revisions differ: confirm its existing solder
straps/pull resistors by the board markings before changing them. Do not infer
physical header order from another manufacturer's breakout. Firmware probes
both 0x4A and 0x4B. This version uses I2C polling, with no interrupt/reset GPIO
assigned. If the actual chip is BNO086, interrupt wiring/driver changes are
needed; BNO086 does not support I2C polling.

After reconnecting power, allow detection and report setup to complete. USB
`sensors` or the dashboard should show IMU_BODY online, increasing per-report
counts, and a native quaternion. Rotate the module by hand and verify all axes.
Calibration accuracy may initially be low; that is shown as DEGRADED rather
than a communication failure. Keep it away from track motors and magnets while
establishing an orientation baseline. The ESP32/BNO08x I2C combination still
requires a real bench test; clock stretching and board wiring can affect it.

For the DFRobot modules, select I2C on the module and connect D/T (data) to
GPIO8 and C/R (clock) to GPIO9, plus 3.3 V and ground. Confirm each board's
printed pin labels. The firmware probes the documented address options.

## Where information lives

`SensorManager` owns one driver object for each device. Driver `update()` calls
perform only the work due for that device. `RobotSensors` contains plain data:

```cpp
sensors::RobotSensors data;
sensorManager.snapshot(data);

data.power.raw.shuntCounts;          // signed, original INA226 register
data.power.derived.currentAmps;      // counts -> amps, using the R002 shunt
data.power.meta.health;              // communication/freshness
data.imu.reports[0].native;          // full decoded rotation-vector report
data.imu.derived.pitchDeg;           // separate interpretation
data.tofFront.raw.distanceMm[37];    // exactly the device's zone 37
data.presence.raw.result[0];         // retained C4001 result register
```

The native data is never replaced by filtering or derived values. There is no
new software smoothing. INA226 retains the previous 16-sample hardware
averaging, 1.1 ms bus/shunt conversion settings (`0x0527`), and 20 Hz polling.
This preserves the prior behavior; it does not capture every ADC conversion or
every brief current spike. Its bus and shunt registers are sequential reads,
not a simultaneous latched pair. The BLE compatibility view rounds values to
the existing millivolt/milliamp packet format; native registers remain intact.

### BNO085 report selection

| Native report | Requested rate |
| --- | ---: |
| Rotation quaternion + accuracy estimate | 100 Hz |
| Calibrated acceleration | 100 Hz |
| Calibrated angular velocity | 100 Hz |
| Calibrated magnetic field | 25 Hz |
| Linear acceleration | 50 Hz |
| Gravity | 50 Hz |
| Raw accelerometer ADC counts | 100 Hz |
| Raw gyroscope ADC/temperature counts | 100 Hz |
| Raw magnetometer ADC counts | 25 Hz |
| Game rotation quaternion (no magnetometer) | 100 Hz |

Each stream keeps its own full `sh2_SensorValue_t`, host receipt time, sensor
timestamp, accuracy/status bits, sequence, delay, count, and missed-report
counter. The SH2 callback handles every event in a received packet. The usual
library last-event getter would retain only the last report delivered during
one service call. Euler angles are derived from a normalized *copy* of the
quaternion; the native quaternion is unchanged. That copy also has the measured
mount tilt removed, so published angles are chassis-frame (see below). Yaw is
not a calibrated robot compass bearing. Rates are requests, not claims about
uninstalled hardware; the API exposes actual counters for measurement.

### BNO085 calibration

Neither the Adafruit wrapper nor the SH2 default enables dynamic gyroscope or
magnetometer calibration, so those accuracy bytes stay at 0 no matter how much
the chassis moves. The driver calls `sh2_setCalConfig(ACCEL|GYRO|MAG)` on every
start and after a device reset, then reads the mask back; `imu.calibration`
reports what is actually in effect rather than what was asked for. Once any of
the gyroscope, rotation-vector or game-rotation-vector streams reaches accuracy
2, `sh2_saveDcdNow()` persists the calibration into the chip so a power cycle no
longer discards it. It saves only on an improvement, and only while reports are
arriving: that SH2 call busy-waits with no timeout and must never be issued to a
device that has stopped answering.

Two orientation streams are published side by side. `imu.derived` comes from the
magnetometer-backed rotation vector. `imu.gameDerived` comes from the game
rotation vector, which fuses only gyroscope and accelerometer: absolute roll and
pitch, relative yaw that drifts slowly, and no compass bearing. On a chassis
whose magnetometer sits beside two BTS7960 drivers and the track motors, the
magnetometer may never calibrate, so `gameDerived` is the usable heading source
and health is judged on it. Both remain native and neither replaces the other.

### IMU mounting

The module is not bolted level. Averaging roll and pitch over exactly three full
chassis rotations isolates the body-fixed component, because a whole number of
turns cancels any planar floor slope; the residual sweep gives the slope itself.
Measured 2026-09-08: mount tilt **roll -10.65°, pitch +4.96°**, on a floor
sloping about 3.0°.

`IMU_MOUNT_ROLL_DEG` / `IMU_MOUNT_PITCH_DEG` in `BoardConfig.h` hold those
values, and both derived blocks are published in chassis frame as
`q_chassis = q_sensor ⊗ conj(q_mount)`. The tilt is fixed in the body frame, so
it composes on the right: verified against a live quaternion, that leaves yaw
unchanged to 0.034° while left-multiplication rotates heading by ~0.45° and
either reversed order doubles the tilt instead of cancelling it. `imu.mounting`
reports the offsets and that they are applied. The native quaternions are not
touched, so raw sensor-frame angles remain recoverable from them.

There is no yaw correction. Gravity provides no heading reference, so a yaw
mounting offset is not observable by this method and is left at zero.

Every blocking SH2 operation — `enableReport`, `setCalConfig`, `saveDcdNow` —
runs through `opProcess`, which busy-waits on `shtp_service()` with `timeout_us`
left at 0, meaning no timeout at all. An unresponsive device can therefore hang
the sensor task indefinitely. The task watchdog subscription in `SensorManager`
is what bounds that to a reboot instead of a silent freeze.

### SEN0628 data

The module's documented RP2040 protocol exposes 64 unsigned distances in
device order. It does not expose ST's per-zone quality, signal, or multiple
target fields. The API explicitly reports those capabilities as false instead
of inventing values. All returned distances, including invalid/sentinel values,
are retained. `usableZones` and `nearestMm` are optional derived range checks
over 20 mm to just below 4000 mm, not native quality indicators.

The span is half-open because 4000 is a sentinel, not a measurement. The bench
run on 2026-09-09 pointed the sensor across a desk: about fifteen zones returned
1560–1950 mm with tens of mm of frame-to-frame jitter, and every remaining zone
returned exactly 4000, never 3990 or 4010. Counting it as usable reported 64/64
zones in a scene where most of the array saw nothing, which would let obstacle
logic read empty air as a confirmed 4 m of clearance. Zones that genuinely sit
at the range limit are therefore also dropped; that is the safe direction, since
the sensor gives no way to tell them apart from a zone with no return.

Startup sends the 8x8 mode packet, waits for its response, and allows the
vendor's five-second settling interval without sleeping in the driver. The
response parser bounds and validates payload length before copying 64 values.
The poll period is 67 ms. It does not invent frame timestamps or frame IDs that
the interface does not supply, and repeated identical depths may be legitimate.

### C4001 data

Polling is 5 Hz. The driver preserves status, firmware version, all seven
result registers and eleven configuration registers. It starts acquisition if
stopped but does not change mode, range, sensitivity, or saved settings.
Presence mode and distance/speed mode share registers; the API exposes separate
validity flags, so a target count is never misrepresented as a presence bit.
There is no added hold-last-target filtering. A fresh read is communication
health; the module's own running/initialization bits describe measurement
availability.

## Timing and health

The Arduino control loop runs on core 1. A dedicated task on core 0 owns Wire
and the sensor drivers. Sensor snapshots use a short, nonblocking mutex copy;
there is no mutex held during I2C, report parsing, or JSON serialization.
The worker yields one RTOS tick between passes. Driver modules contain no
`delay()` calls or wait-for-data loops.

The Adafruit library performs bounded blocking startup/reset/report
configuration internally. Those operations run only in the sensor task. They
can temporarily interrupt *other sensor sampling*, but cannot block the motor
control loop. Snapshot consumers independently age metadata, so old data is
marked stale even when the worker is busy. `workerMaxUs` includes startup and
reinitialization, while `controller.loopMaxUs` measures completed control-loop
work excluding its normal final 2 ms yield. Neither metric alone is a hardware
watchdog timing certification.

Health states distinguish initialization, OK, degraded measurement quality,
stale data, errors, and offline devices. Error counters are cumulative;
consecutive errors reset on successful reads. Missing devices are retried every
five seconds. Three failed I2C sampling attempts mark a device offline. Old
measurements remain available with their original timestamps; missing first
measurements are JSON null rather than fictional zero readings.

All time comparisons use unsigned subtraction for millisecond-counter rollover.
Host receipt timestamps use the ESP32 64-bit microsecond clock. The device's
own SH2 timestamp is also preserved and should not be assumed to share the
same origin. Snapshot data is latest-per-stream, not an unlimited recording of
every sample; the web page and USB capture are downsampled views. Continuous
full-rate logging is a separate future feature.

## Bench tools and endpoints

- `GET /api/sensors`: complete native/derived/metadata snapshot and controller state.
- `GET /api/status`: existing phone/web-compatible summary, now including `inaValid`.
- USB at 115200: send `sensors` or `status` followed by newline for JSON. These
  commands cannot arm or move. Large USB snapshots are refused while armed.
- Web console: `sensors` returns the same complete JSON.
- Dashboard: health table, ages, rates, native power counts, Euler angles,
  expandable complete JSON. Display refresh is 2 Hz.

Run the capture with the PlatformIO Python environment (which has pyserial):

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\python.exe" tools\bench_sensors.py --seconds 30
```

After installing a sensor, add `--require imu`, `--require tofFront`, or
`--require presence`. The script records JSONL and checks new samples, native
power scaling, timestamps, task status, and disarmed zero motor commands. It
does not prove the physical motor-enable pin voltages or exercise powered motion.

### CYD bench rig

`src/bench/` runs the shipping drivers on a CYD (ESP32-2432S028R) so a sensor can
be exercised before it is committed to the chassis. It is a separate PlatformIO
environment, and `gladiator_s3` excludes `src/bench/` from its image, so the two
never share a `setup`/`loop`.

Wire the sensor to the CYD CN1 header: GND, GPIO27 = SDA, GPIO22 = SCL, 3V3 to
3V3. Then:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -e cyd_bench -t upload -t monitor
```

The panel shows an I2C scan at boot, then five views of the live 64 zones: HEAT
(8x8 grid in cm with an auto-ranged legend), PLAN (top-down 60 degree fan of the
nearest return per column, rings at 1–4 m), CLOUD (three-quarter point cloud),
TREND (nearest return over 300 frames, with dropouts marked) and DIAG (address,
health, rate, bus and protocol error counts, last response bytes, free heap).
Tap the screen for the next view and hold for about 0.7 s to freeze. Over serial,
`n`/`p` and `0`–`4` select a view, `f` freezes, `s` rescans and `g` toggles the
grid dump. The full mm grid is printed once a second either way.

The rig is what found the 4000 mm sentinel described above. Note that the bench
views exclude the sentinel through their own `zoneValid()` rather than trusting
`ToFData::derived`, so the two agree only while the driver keeps the half-open
span.

Host C++ tests compile the actual power, matrix and presence drivers against a
fake I2C bus. They cover full precision, negative current, extrema, short reads,
recovery, malformed payloads, mode-dependent radar interpretation and rollover.
Run `tools/test_sensors.ps1`; it accepts a C++ compiler path and uses the local
Zig compiler if present. No test tools are included in the firmware image.

## Choices to revisit together

Rates and report selection live in `BNO085Sensor.cpp`; bus and INA settings
live in `BoardConfig.h`. The data structures live in `SensorData.h`. These are
deliberately small, visible decisions. Later we can add mounting transforms,
calibration objects, filtered copies, report queues, richer ToF hardware, or
motor safety policies without changing or discarding native readings.

## Primary references

- [TI INA226 datasheet](https://www.ti.com/lit/ds/symlink/ina226.pdf)
- [CEVA BNO08X datasheet](https://www.ceva-ip.com/wp-content/uploads/BNO080_085-Datasheet.pdf)
- [Adafruit BNO08x implementation](https://github.com/adafruit/Adafruit_BNO08x)
- [DFRobot SEN0628 documentation](https://wiki.dfrobot.com/sen0628/)
- [DFRobot MatrixLidar protocol implementation](https://github.com/DFRobot/DFRobot_MatrixLidar)
- [DFRobot SEN0610 documentation](https://wiki.dfrobot.com/sen0610/)
- [DFRobot C4001 register implementation](https://github.com/DFRobot/DFRobot_C4001)
