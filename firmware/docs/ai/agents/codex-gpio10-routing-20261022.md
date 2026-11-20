# GPIO10 routing audit - 2026-10-22

User verified wiring: pan GPIO10, tilt GPIO13, one control page. Later explicitly authorized bounded servo tests, reversing excursions to avoid twisting cords. Preserve tilt records 1150/1500/1800.

No swapped pin constants or shared motor PWM channels found. HTTP jog-test previously omitted a GPIO and targeted whichever raw test was active. New UI heartbeat/manual jog and shared FieldPage specify pin; C6 rejects missing/invalid pin; S3 rejects mismatches without changing target or renewing the lease. USB mast-jog still explicitly controls the current USB test.

Hardware begin/start/stop explicitly detach both matrix routes. Previous pinMode(INPUT_PULLDOWN) disabled output but retained matrix routing. No proof yet this caused observed powered tilt. Telemetry now includes output-enable and matrix signal for each pin, PWM frequency, pin-required capability, raw stop reason and max tick. Signal77 is pan/channel4, signal78 tilt/channel5, 256 disconnected. Register data is not a measured waveform or position feedback.

Read-only probes observed HTTP timeouts, one PC Wi-Fi disconnect, and stable gateway bootId across successful samples. Rejoined Gladiator-Gateway. No proven NVS crash. Gateway power saving was already off, camera requests already asynchronous. UI now explicitly labels HTTP timeouts, without retrying commands.

Both firmware builds pass. Host policy covers wrong-pin rejection both ways and 363909 angle cases. Production Hardware mock tests cover alternating GPIO10/13, matrix detachment and partial attachment failure. Native and PC bridge browser suites pass, including delayed timeout recovery and both GPIOs. All 10 bridge HTTP tests pass.

Candidates S3 Mast operator v4 and C6 gateway-2.3.4. Check diagnostics/gpio10-routing-20261022 receipts for install status. Initial 460800 USB read backup failed corrupt data before any write; lower-speed backup/install pending at note creation. No live motion yet.

S3 source is this existing installed-release firmware tree, not the independently edited older canonical root S3 driver/trim sources. C6 and hardware tester remain canonical C:/PlatformIO/Gladiator. Shared MastPolicy/FieldPage updated in both. Preserve this source separation.

## Installation follow-up: sensor-task watchdog

After the first GPIO-routing image flashed and hash-verified, UART captured repeated task_wdt resets at about 7 seconds, naming `sensors (CPU 0)`. Both CPUs were in idle at the panic; backtrace decoded against the flashed ELF. C6 peerBootId changed repeatedly, so S3 never returned stable fresh mast telemetry. No actuator commands had been sent.

Adafruit BNO08x 1.2.5 SH2 `opProcess` treats timeout_us==0 as unlimited. Product ID/calibration/save operations have zero defaults. New scripts/bounded_sh2.py applies a version-checked 500ms fallback to those waits, preserving explicit timeouts, at build time into the build directory. It does not modify the dependency cache. PlatformIO middleware redirects only this dependency's sh2.c. S3 platformio.ini enables the middleware.

Regression tests/sh2_timeout_test.c and tests/run_sh2_timeout_test.py compile the production SH2 source with a simulated nonreplying transport. Original source demonstrably hangs (process killed after test timeout); patched source passes missing product/calibration/save reply timeouts, timely completion, explicit deadlines, uint32 clock wrap and subsequent-command recovery. Full S3 build passes, patched object is compiled and archived in the Adafruit library.

Second S3 application flash, still at offset0x10000/230400 baud, passed identity and hash checks, reusing the verified original pre-update backup. New image and receipt supersede the routing-only candidate. Stable boot verification pending at this note update. This captured watchdog is real, but physical pan recovery and exact source of previously observed tilt movement remain to be verified.

## Installed and live software acceptance

Final S3 image includes GPIO binding/detachment and bounded SH2 waits, flashed over USB-UART COM13 at230400, device MAC and image hash verified. Original pre-update flash backup retained; NVS/OTA metadata not written. S3 peerBootId1453605948 stayed stable through reboot verification, C6 update, live test and post-test checks; no watchdog text in subsequent passive UART capture. Sensor power health recovered and mast safe/fresh true.

C6 gateway-2.3.4 installed OTA on ota_0, boot/slot and validation checked; S3 did not reboot during C6 update; all three served assets exactly match source. Saved setup revision4 unchanged: tilt GPIO13 low1150 / neutral1500 / high1800, panPin10. Full S3 aiming profile remains unapplied because pan measurements/angles are not yet complete; user describes tilt physically calibrated. Do not overwrite those measured tilt records.

User-authorized live pan sequence: first1500, target1525, return1500, target1475, return1500, explicit stop. All S3 pulse targets reached; GPIO10 output enabled, matrix77/channel4, timer50Hz. GPIO13 output disabled and matrix256 disconnected throughout. Both outputs disabled/disconnected after stop; last commanded pulse1500. No full rotations commanded. Missing-pin jog rejected HTTP400; wrong-pin jog rejected by S3 with no target/output change (rejected counter1 is this deliberate test). Max raw service interval7ms. This is software/register acceptance, not an oscilloscope measurement or confirmed physical movement.

Eight post-test reads over about16seconds all fresh/safe, HTTP62-94ms, same S3 boot. No timeout or reset during live motion test. Physical operator observation requested after the sequence; pending at this note update. If no visible pan movement, first confirm the small excursion was observable and consider a larger bounded reversing excursion. Do not recheck wiring as the primary assumption: Jim explicitly verified it and requested software investigation.

Receipts: installed.json, usb-flashed.json, s3-post-update.json, pan-live-test.json, post-test-health.json. Regression logs native-tests.log / bridge-tests.log; SH2 before/after regression output captured by tool and source tests reproducible. Builds and policy/hardware/SH2/browser/HTTP regressions pass. No further production changes after these checks.
