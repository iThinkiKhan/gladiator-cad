# Gladiator Link v2

## Ownership

The ESP32-S3 is Gladiator's authoritative brain. It samples and retains native
sensor information, validates input, selects control ownership, applies motor
limits/trim, enforces arming/deadman/watchdogs and battery protection, and owns
future autonomous decisions. C6 is a capability the S3 uses: a communications
and interface coprocessor, with no motor, sensor-bus, or autonomy policy.

`shared/RobotProtocol.h` defines framing; `shared/GladiatorLink.h` defines typed
messages, health/hysteresis and the S3 session gate. The S3 `RobotLink` worker
handles protocol/transport work on core 0 and queues bounded requests. Only the
existing S3 control loop validates and applies them. The C6 validates HTTP
syntax/authentication and relays requests; HTTP 202 means **queued**, never
"the robot accepted motion". S3 results and telemetry are authoritative.

## Transport policy

| Condition | Behavior |
| --- | --- |
| Normal | Preferred 460800-baud UART, 8N1; independent probes every 250 ms |
| Single missed packet | No transport change |
| One UART direction lost | Echoes stop proving a round trip; also treated as failure |
| No recent valid echo for 2500 ms | S3 opens AP+STA recovery and attempts the known C6 field network |
| Valid Wi-Fi link available | S3 selects Wi-Fi; identical robot messages/semantics |
| UART returns | Five seconds of continuous round-trip health before preferring UART |
| Recovery gap over 750 ms | Restart UART stability timer |
| UART stable again | Close auxiliary Wi-Fi link and turn off S3 Wi-Fi when no recovery client owns/uses it |
| Neither path available | S3 recovery AP and existing direct BLE remain available |
| Battery radio shutdown | Radio recovery stays inhibited until the existing battery policy permits it |

S3 advertises its selected transport. C6 follows that selection, while measuring
its own UART and Wi-Fi health. Both UART directions keep probing during Wi-Fi
fallback. Separate frame decoders, sequence windows, and health records prevent
one transport's traffic from keeping the other falsely alive. S3 boot IDs and
session epochs invalidate old control; C6 clears cached robot data on S3 reboot.

The C6 field AP (`Gladiator-Gateway`, password from `shared/secrets.h`, `192.168.8.1`) intentionally
stays on in AP+STA mode, including during ordinary homelab service. Thus loss
detection never has to wait for AP startup, and a phone and the S3 can use it
simultaneously. Existing station reconnection runs every ten seconds. S3's
separate `Gladiator-Setup` AP uses `192.168.4.1`; it remains usable even if C6
association fails. S3 retries station association every ten seconds and its
TCP link every three seconds. Its boot AP stays available for at least fifteen
seconds. An existing recovery AP client prevents automatic shutdown.

S3 BLE retains the existing phone protocol/service, in idle advertising state
when unused. BLE is not torn down/recreated during transport changes. USB also
remains independent. There is no C6 BLE service or 802.15.4 stack in this release;
they are explicit extension points rather than advertised working interfaces.

## Wi-Fi channel

The C6 listens only on its field-AP address, TCP port 8765. `WifiLink.h` is a
nonblocking bounded stream adapter, shared by Arduino S3 and IDF C6. Each endpoint
sends a fresh 16-byte nonce. The per-connection HMAC-SHA256 key is derived from
the configured pairing key over `C6 nonce || S3 nonce`. Each following record is:

`frame_length:u16 LE | directional_counter:u32 LE | COBS frame | HMAC:32 bytes`

The MAC covers `direction:u8 || length || counter || frame`; direction is zero
for S3-to-C6 and one for C6-to-S3. Counters begin at one. Nonces, direction and
counters prevent cross-connection replay, reflection and duplicate records.
CRC still detects framing corruption on either transport. WPA2 provides radio
privacy. `GLADIATOR_LINK_KEY` must match in both firmware builds; its checked-in
default is a development pairing key, not a device-unique production credential.
Provision a robot-specific build value before use on shared/untrusted networks.
The HTTP maintenance key is independent and is never used as a pairing key.

Handshake deadline: 2 s. Pending-output deadline: 500 ms. Buffers are fixed and
queue pressure drops optional traffic instead of blocking motor execution. S3
uses PSRAM for its large framing/authentication buffers, with checked allocation
and independent recovery if its link task cannot start. MAC/library failures
close the socket. The C6 rejects extra clients while the current link is active;
an unresponsive connection ages out. No transport retries old drive commands.

## Control and expiry

Control payload: `epoch:u32, client:u32, sequence:u32, observedS3Ms:u32,
operation:u8, deadman:u8, overdrive:u8, power:u8, left:i8, right:i8` (LE).
Operations are 0=disarm, 1=explicit neutral arm, 2=drive/keepalive. Arm requires
zero outputs and deadman released. Operation 2 cannot arm an expired session.

The S3 requires a current epoch, nonzero client ID, monotonic sequence, a recently
observed S3 timestamp (at most 300 ms old), valid ranges/flags, and ownership.
Active movement cannot be stolen by another source. The existing 350 ms command
watchdog, deadman release, motor ramp/trim, and battery guard still apply.
Link command queues hold six entries, have a 150 ms age limit, and are tagged
with transport generation. Transport selection or C6 boot changes revoke the
remote session. Deadline expiry and disarm advance the epoch. Delayed arm frames
from an old epoch cannot revive it. Control results carry client/sequence/epoch
and a result code: accepted, expired, ownership conflict, invalid, replay,
stale timestamp, or offline.

Only fresh user interaction can arm again. The shared phone page stops sending
when state becomes stale, ownership changes, it loses focus, or an epoch changes.
It never queues retries or automatically arms after reconnection. The existing
legacy web/BLE timeout paths also require release before rearming. Recovery
field control goes directly to the same S3 session validator. C6 firmware OTA
does not transfer ownership or pause S3 expiry.

## Typed telemetry and details

Wire version is 2. Header is version:u8, type:u8, sequence:u32, boot:u32,
payload_length:u16. CRC32 IEEE covers header+payload, then the whole frame is
COBS encoded with a zero delimiter. Maximum payload is 10,000 bytes. Little
endian integers and explicitly encoded IEEE floats avoid compiler struct/ABI
dependencies. v1 full JSON telemetry is no longer accepted. Both boards must
be updated together; a mixed pair leaves S3 recovery and existing direct control
available, but does not negotiate an unsafe partially compatible link.

| Message | Type | Default rate / purpose |
| --- | ---: | --- |
| HELLO / HEARTBEAT | 1 / 2 | 4 Hz; role, probes, echoed boot/probe, selected transport, epoch, bandwidth lease |
| PING / PONG | 4 / 5 | Empty diagnostic request/reply |
| GET_STATE | 6 | One requested native snapshot |
| CONTROLLER | 16 | 10 Hz; S3 time, epoch/client, arm/deadman/owner, actual outputs, watchdog, timing, boot count |
| POWER | 17 | 5 Hz; voltage/current/power/extrema and sample metadata |
| ORIENTATION | 18 | 10 Hz; ordinary and game rotation validity/angles, sample metadata |
| RANGE | 19 | 2 Hz; nearest range, usable-zone count, sample metadata |
| PRESENCE | 20 | 2 Hz; presence/target validity, range/speed, sample metadata |
| DETAIL | 21 | Requested full native snapshot, chunked |
| SUBSCRIBE | 22 | interval:u32 (100–10000 ms), lease:u32 (0–60000 ms); zero lease stops renewal |
| CONTROL / CONTROL_RESULT | 32 / 33 | S3-validated input and result |
| WIFI_LEASE | 40 | duration:u32, at most 60 s; zero cancels |
| SYSTEM | 41 | Requested binary system tree, at most once per 2 s |
| LOG | 42 | Requested retained S3 log (up to 12,000 bytes), at most once per 5 s |

Routine S3 telemetry is approximately 1.8 KB/s including framing, before control
replies, instead of multiple complete JSON sensor documents per second. Each
sensor keeps sampling independently on the S3; link rates do not alter drivers.
Metadata includes health, online/sample flags, source update time, sample/error
counts and measured source rate. C6 advances each topic's displayed age
independently, including when only that topic stops. HTTP JSON is generated on
the C6, with source timestamps kept separate from C6 receipt ages.

Full detail uses an extensible typed binary tree (null, false, true, LE float64,
length-prefixed UTF-8, arrays and maps). It preserves the existing sensor schema,
all native BNO reports/calibration/product information, INA raw registers, the
64-zone ToF grid, radar registers, validity and timestamps. It is a sampled
snapshot stream, not lossless capture of every native sensor event. No native
information is removed from the S3. New high-rate individual report types can
be added without changing control messages.

DETAIL and LOG fragments carry transfer ID, total size and byte offset (three
u32 values), followed by at most 384 bytes. Receivers publish only complete,
ordered transfers and retain their receipt ages. Fragments cannot monopolize
UART; controller/probe traffic is scheduled first. UART detail is capped at
1 Hz, Wi-Fi detail at 10 Hz, and leases expire within 60 seconds. A disconnect
or transport change may discard an incomplete transfer; the next snapshot
replaces it. Cached native snapshots/logs are explicitly historical until
refreshed; their embedded ages describe capture time, not the current moment.

A Wi-Fi bandwidth lease can be requested even while UART is healthy. S3 brings
up its station link, keeps control/summary traffic on UART, and routes requested
native detail/logs over Wi-Fi. This exercises a second channel without changing
robot semantics or moving safety policy. Expiry returns Wi-Fi to idle/off when
no recovery client needs it. A lease does not renew itself except through an
explicit external subscription action.

## Interfaces

[Interface v1](INTERFACE_V1.md) is the next milestone. C6 `/` is the phone field
interface; `/dev` is the single development site with Overview, Controller,
Power, IMU, Range, Presence, Communications, System, Logs and Firmware tabs.
Native detail is collapsed and explicitly requested. Controller embeds the same
field controls and includes independent track tests. S3 `/` redirects to
recovery-only `/service`; deliberate fallback field access is at S3 `/field`.
S3 publishes controller state, battery classification and heading validity; C6
never reconstructs robot state from motor values. See the milestone document
for the paired Link v2 telemetry extensions and installation order.

C6 GET `/api/field` returns current controller state for field driving. GET
`/api/robot` schema 2 returns gateway diagnostics, compact robot topics, requested
`native` and `system` documents, retained `logs`, and receipt ages. GET
`/api/status` reports C6 state. POST `/api/control`, `/api/subscribe`, `/api/link`,
`/api/ping`, `/api/config` and `/api/ota` require `X-Gladiator-Key`. Key storage,
network provisioning, and C6 OTA identity checks retain the existing behavior.
S3 recovery HTTP retains its WPA2-local access model; it uses the same strict
control fields/session semantics without the C6 maintenance header.

The C6 link worker blocks for one RTOS tick on every pass. This target uses a
100 Hz tick, so millisecond delays shorter than 10 ms must not be converted with
`pdMS_TO_TICKS`: they truncate to zero and can starve the CPU 0 idle task. The
C6 status response reports the tick rate, link delay, and task priority.

The S3 recognizes USB bench operation when the native USB host is present and
the INA226 sees the installed controller's 3.8-5.5 V USB-fed logic rail. A
higher-voltage regulated bench supply can overlap the normal 4S voltage range,
so the bench harness grounds active-low GPIO7 to identify that case; its internal
pull-up selects normal LiPo policy when the signal is absent. After 500 ms of a
stable signal the S3 skips only LiPo voltage lockout and radio shedding. Removing
the signal or USB source restores the normal timed thresholds. Watchdog, arming,
deadman, control ownership, and session expiry are unchanged. Voltage in the 4S
operating range is deliberately never used to guess the source.

## Verification and remaining bench work

Automated checks:

```powershell
./tools/test_protocol.ps1
./tools/test_sensors.ps1
pio run -e gladiator_s3
pio run -d gateway -e gladiator_c6
# Set GLADIATOR_NODE_MODULES to a node_modules directory containing Playwright.
node tools/test_link_ui.cjs
```

Host tests exercise framing corruption/noise, typed control, one-way UART loss,
stability hysteresis, replay/boots/clock wrap, ownership, expiry and no automatic
rearming. Wi-Fi adapter tests use real HMAC-SHA256 with a fragmented socket shim:
known vector, queued frames, tamper, replay within/across connections,
backpressure and deadline closure. Browser tests simulate API responses and
exercise hold/release, explicit arm, timeout/recovery without resumption, disarm,
tabs, missing native data, and console errors. None of those tests energizes
hardware or establishes actual RF timing.

Before deployment acceptance, with tracks clear of the floor:

1. Install both v2 images by the existing USB procedure. Check boot, free/minimum
   heap, stack health, link counters and stable UART; compare INA and all native
   sensor reports against S3 `/api/sensors`.
2. Confirm field control only after explicit arm; verify deadman release and
   network loss coast within the S3 350 ms deadline. Test ownership against BLE
   and recovery web control and verify battery lockout still rejects arming.
3. Remove either UART direction separately, then both. Verify a short interruption
   does not switch; sustained loss opens the S3 recovery AP and selects C6 Wi-Fi.
   Phone access to the C6 AP and telemetry must coexist. No driving may resume
   until a new arm action. Repeat with C6 reboot/OTA and partial frames.
4. Remove C6 power/network too. Verify independent S3 AP/BLE and safe control
   expiry. Restore C6 and confirm old commands cannot move the robot.
5. Restore UART intermittently, then continuously. Require five seconds stable
   before returning; verify S3 Wi-Fi turns off only when its service AP has no
   client. Confirm no oscillation, stale source ages, or resumed session.
6. Request a 60 s bandwidth lease on healthy UART. Verify control remains UART,
   details use Wi-Fi, sampling stays unchanged, and expiry powers Wi-Fi down.
   Repeat under congestion and with lost detail fragments; monitor dropped frames,
   heap minima, loop timing, thermal/radio coexistence and physical watchdog timing.

These physical checks remain pending. The code is prepared and built; no firmware
was flashed or robot motion commanded as part of the host/browser validation.
