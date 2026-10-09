# Gladiator communications coprocessor

The XIAO ESP32-C6 extends the S3 with external-antenna Wi-Fi and web/API
processing. The S3 remains authoritative for motors, safety, sensor acquisition,
robot state and future autonomy. See [Gladiator Link v2](GLADIATOR_LINK.md) for
the protocol, control validation, transport policy and physical validation plan.

## Wiring and normal transport

| Signal | S3 | C6 |
| --- | --- | --- |
| S3 → C6 | GPIO4 TX | GPIO17 RX (XIAO D7) |
| C6 → S3 | GPIO5 RX | GPIO16 TX (XIAO D6) |
| Reference | GND | GND |

UART remains 460800 baud, 8N1, 3.3 V logic. Boards retain their separate power
feeds. S3 I²C remains GPIO8 SDA / GPIO9 SCL at 400 kHz. C6 GPIO3 LOW enables
the RF switch and GPIO14 HIGH selects the installed external antenna.

The interface is **Gladiator Link**, not UART. Typed frames also run over an
authenticated Wi-Fi stream on the C6 field AP. Five seconds of stable UART
round-trip health are required to prefer it; 2.5 seconds without recent probe
echoes trigger fallback. Loss of a remote driving session always requires a
fresh arm action. Telemetry and requested detail never move motor policy to C6.

## Pages and network

- Normal phone field interface: `http://192.168.8.1/`.
- C6 development site: `http://192.168.8.1/dev`.
- C6 field AP: `Gladiator-Gateway`, password `GLADIATOR_FIELD_PASSWORD` (`shared/secrets.h`).
- Homelab: same pages at the DHCP address reported by C6 `/api/status` or USB
  `status`; hostname `gladiator-gateway` (no mDNS service).
- Independent S3 recovery: `Gladiator-Setup`, password `GLADIATOR_MAINTENANCE_AP_PASSWORD` (`shared/secrets.h`), phone
  interface `http://192.168.4.1/field`, service/OTA `http://192.168.4.1/service`.

C6 keeps its field AP in AP+STA mode while connecting to saved homelab Wi-Fi.
Settings survive OTA; station reconnection occurs every ten seconds. The C6 AP
is simultaneously available to phones and S3 fallback. S3 opens its own recovery
AP if needed and powers Wi-Fi down after UART stability when no recovery client
needs it. Existing S3 BLE remains available, subject to battery radio shutdown.

C6 POST endpoints require its random per-device 32-character maintenance key.
Read it physically using USB `credentials` or `gateway_manage.py usb-key`.
Network responses never expose credentials. Pages keep entered keys in memory.
The shared Wi-Fi Link pairing key is a separate compile-time setting; replace
the development default identically in both builds for a specific robot.

## Build, provision, update

S3 remains Arduino 2.x; C6 uses ESP-IDF 6.0.1. Both use PlatformIO espressif32
7.0.1. The S3 and C6 images are different and must not be interchanged. Link v2
requires a matched firmware pair; direct S3 recovery remains available during
the update sequence.

```powershell
pio run -e gladiator_s3
pio run -d gateway -e gladiator_c6
# Installation: use the attached board's confirmed port.
pio run -e gladiator_s3 -t upload --upload-port COM25
pio run -d gateway -t upload --upload-port COM30
python tools/gateway_manage.py usb-key --port COM30
./tools/connect_gateway_ap.ps1
python tools/gateway_manage.py provision --profile "Nothing But Net"
python tools/gateway_manage.py status --url http://GATEWAY_IP
python tools/gateway_manage.py ota --url http://GATEWAY_IP
```

Use the PlatformIO Python environment for pyserial helpers. Provisioning reads
the selected saved Windows profile into memory without printing its password.
The helper's maintenance key file remains
`diagnostics/gateway-private/credentials.json`, excluded by `.gitignore`.

C6 OTA accepts `gateway/.pio/build/gladiator_c6/firmware.bin`, checks project
identity and the complete image, writes the inactive 1.875 MiB slot, then reboots
only C6. It confirms boot after fifteen seconds if the link task and HTTP server
are alive; an absent S3 does not fail boot validation. Rollback stays enabled.
S3 OTA remains a separate USB or recovery-service operation and coasts/disarms
outputs. Its upload progress feeds the existing task watchdog.

## External API

| Method/path | Purpose |
| --- | --- |
| GET `/api/field` | Current S3 controller/session state for field control |
| GET `/api/status` | C6 radio, heap, firmware, OTA slot and link diagnostics |
| GET `/api/robot` | Schema 2: compact topics, requested native/system/log snapshots and ages |
| POST `/api/control` | Relay typed command; S3 validates and reports acceptance |
| POST `/api/subscribe` | `{intervalMs:1000,leaseMs:30000}`; bounded native diagnostics stream |
| POST `/api/link` | `{leaseMs:60000}`; ask S3 for auxiliary Wi-Fi bandwidth |
| POST `/api/ping` | Diagnostic ping and one native snapshot request |
| POST `/api/config` | Save `ssid` and `password`, reconnect station |
| POST `/api/ota` | Raw C6 firmware, `application/octet-stream` |

All POST requests require `X-Gladiator-Key`. Telemetry is readable without a
key. These existing local HTTP services do not provide TLS; do not expose them
directly to the Internet. Put remote access behind an authenticated TLS service.

Compact topics have independent source timestamps and C6 receipt ages. Native
snapshots preserve full INA, BNO085, ToF and radar information on request. Cached
native data and logs are historical; inspect receipt age before consuming them.
No LLM, remote autonomy service, C6 BLE service or 802.15.4 protocol is configured.

## Validation

```powershell
./tools/test_protocol.ps1
./tools/test_sensors.ps1
# After installing the matched pair, with the robot disarmed:
python tools/bench_gateway.py --url http://GATEWAY_IP --seconds 30 --ping --details
python tools/test_gateway_http.py --url http://GATEWAY_IP
```

The live bench never commands movement. HTTP tests reject invalid credentials
and a header-sized wrong-project image without changing the OTA slot. Follow the
[physical failover and ownership procedure](GLADIATOR_LINK.md#verification-and-remaining-bench-work)
before accepting motor-control or radio-recovery timing on hardware.

Earlier v1 evidence under `diagnostics/` records C6 USB/OTA/provisioning tests and
the original gateway installation. It is preserved as historical evidence and
does not validate this v2 transport or control path. This integration was built
and tested on the host/browser; paired firmware installation and physical
failover, coexistence, heap and motor-deadline checks remain pending.

Interface consolidation and the paired firmware rollout are documented in
[Interface v1](INTERFACE_V1.md). S3 root now opens recovery service.
