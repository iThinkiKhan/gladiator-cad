# Interface v1

The next Gladiator milestone consolidates presentation and development tools.
S3 remains Gladiator: it owns motors, sensors, safety, battery policy, control
ownership, session validation and transport selection. C6 relays requests and
displays S3 reports. No change to the established S3/C6 ownership model.

## Surfaces

| Surface | Purpose | Contents |
| --- | --- | --- |
| C6 `/` | Phone field interface | Hold-to-run drive, ARM/DISARM, power level including Overdrive, battery voltage/state, telemetry freshness, transport, heading/range/presence, warnings |
| C6 `/dev` | Single development interface | Overview, Controller, Power, IMU, Range, Presence, Communications, System, Logs, Firmware |
| S3 `/service` | Independent recovery and maintenance | S3 state, DISARM, boot/power evidence, retained logs, firmware upload, native fault-evidence links |
| S3 `/field` | Deliberate fallback during C6 failure | The same field page, using direct S3 session validation |

S3 `/` redirects to `/service`. Its old drive dashboard is removed. Existing
S3 HTTP APIs, USB recovery, OTA and BLE protocol remain available; this milestone
does not remove maintenance compatibility or change authentication.

Field diagnostics is closed by default. Native data and the development link
are inside it. C6 access keys stay in page memory. Connection quality is shown
as availability and telemetry age in milliseconds; this is not a measurement of
the phone's RF signal strength. C6 station RSSI, when available, belongs to the
network diagnostics and describes its upstream station connection.

This repository contains the shared browser field interface and firmware BLE
protocol, but no separate native phone app source. Interface v1's browser changes
do not imply a separately installed phone application has been updated.

## Development tools

- **Overview:** authoritative controller state, transport, power and sensor health.
- **Controller:** explicitly opened field controls, including independent signed
  track commands under Diagnostics. All commands use the existing typed control
  endpoint. Switching tabs or hiding the page ends the local test session and
  requests disarm; the existing S3 watchdog handles interrupted requests. Recovery
  never automatically arms. The maintenance key is shared with the embedded
  controls only through checked same-origin parent/frame messages.
- **Power, IMU, Range, Presence:** readable S3 measurements and validity, explicit
  diagnostic capture, collapsed native/configuration/timestamp snapshots. Range
  includes all 64 native distances in device order, labeled with snapshot age.
- **Communications:** link diagnostics, ping/state request, bounded WIFI bandwidth
  lease, native radio information and existing saved network settings.
- **System:** S3 firmware/reset information and separate collapsed S3/C6 details.
- **Logs:** requested S3 retained logs, text filter, periodic sensor-line filter,
  and separately labeled browser-observed communications events.
- **Firmware:** inventory, existing authenticated C6 upload and S3 recovery route.

Diagnostic capture has a 30-second lease; streaming explicitly renews it while
visible. Stopping the stream requests a zero lease. Native sensor configuration
is inspectable; arbitrary sensor writes/calibration commands are not added to
Link v2 by this presentation milestone.

## Authoritative data and vocabulary

`shared/InterfaceVocabulary.h` defines controller `UNKNOWN`, `SAFE`, `ARMED`,
`DRIVE`; battery `UNKNOWN`, `OK`, `WARN`, `LOCKOUT`, `CRITICAL`, `BENCH`; sensor
`UNKNOWN`, `INITIALIZING`, `OK`, `DEGRADED`, `STALE`, `ERROR`, `OFFLINE`, `DISABLED`.
S3 computes controller state from its armed flag and actual motor outputs.
The C6 decoder maps the S3 state code to a label without recomputing it.
Visible transport names are `UART`, `WIFI`, `NONE`; existing lower-case raw link
API strings are retained for compatibility. UI `UNAVAILABLE` describes loss of
access to telemetry and does not replace the S3 sensor health enum.

Battery warnings use the S3 battery classification and lockout flags, never a
browser voltage threshold. Heading validity is reported by S3: rotation-vector
sample present and no older than 300 ms, healthy IMU, valid derived orientation,
and native accuracy at least 2. Relative game-vector yaw is retained in native
details and is never presented as a compass heading.

Field `/api/field` adds `sensors`, `transport`, `telemetryAgeMs` and controller
`battery`. C6 copies decoded S3 sensor topics; it advances receipt/sample ages
as before. A disconnected controller, expired sample age, invalid derived value
or non-OK health suppresses live measurements. Display age budgets are 500 ms for power/IMU and 1000 ms for range/presence,
whose compact topics arrive every 500 ms. These hide expired measurements
without changing reported S3 health. Historical native snapshots stay
labeled with their age. No battery percentage is fabricated from voltage.

The Link v2 CONTROLLER payload appends two bytes: Interface v1 state and battery
codes. ORIENTATION appends one byte for S3 heading validity. No control, session,
transport or safety fields change. The new C6 accepts legacy telemetry but shows
state/battery UNKNOWN and unavailable heading when those bytes are absent; it
does not infer missing state and the field ARM control stays disabled. Partial
controller extensions and extra bytes are rejected.

**Install the paired builds, C6 first.** The old C6 decoder rejects extended S3
payloads. Frame protocol version remains 2; these payload extensions require the
paired Interface v1 images for full operation.

## Validation and hardware acceptance

Host validation:

```powershell
./tools/test_protocol.ps1
./tools/test_sensors.ps1
./tools/test_interface_codec.ps1
# Set GLADIATOR_NODE_MODULES to the directory containing Playwright.
node tools/test_link_ui.cjs
node tools/test_interface_v1.cjs
pio run -e gladiator_s3
pio run -d gateway -e gladiator_c6
```

Browser tests intercept every request on a simulated host and never contact
hardware. Codec tests compile the production C6 telemetry decoder against cJSON.
Screenshots and build logs are retained under `diagnostics/interface-v1-*`.

After installing both images, complete the existing Link cable-loss/radio and
motor-watchdog bench procedure with the chassis supported. Verify live state and
battery agreement between S3 service and C6, explicit arming, hold/release,
Overdrive, independent tracks, tab/background disarm, UART/WIFI failover without
motion replay, native capture/expiry, and independent S3 OTA recovery. Hardware
flashing and physical acceptance have not been performed by this implementation.
