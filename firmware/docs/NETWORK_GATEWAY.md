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
- Masthead camera on the field AP: `192.168.8.2`. The direct video endpoint is
  `http://192.168.8.2:81/stream`. Gateway 2.4.19 leases addresses from
  `192.168.8.10` through `192.168.8.109`, leaving the camera's fixed address
  available regardless of client join order.
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

## C6 USB console after a cold start

On November 20, gateway 2.4.15 consistently processed USB console commands after a true USB power cycle but returned zero bytes on the same Windows WinUSB interface. The receive counter was verified over the AP. Resetting the host's USB receive pipe did not help. Espressif ROM chip identification responded through the same cable and driver.

A normal USB-triggered C6 core reset while the cable stays connected restored USB replies. The Windows client may need to rejoin Gladiator-Gateway after the C6 restarts. The separate S3 stayed up and saved mast revision 14 and the outputs-off state were verified. A USB power cycle reproduced the fault. The reset is a recovery procedure for the current firmware. No flash writes were needed. Exact cold-start initialization cause remains unconfirmed.

Evidence: `diagnostics/connection-recovery-20261120/usb-cold-warm-summary.json`.

### Gateway 2.4.17 fix

The installed C6 application flushes the transmit FIFO before it starts the buffered USB driver and again before the first command reply. Each console reply also drains the standard-output buffer. Two real USB power cycles reported power-on reset and returned all three read-only console replies with zero recovery resets. Revision 14 read back on each cold boot. OTA preserved 2.4.15 in the rollback slot. All eight deployed operator-page assets matched their previous content.

Evidence: `diagnostics/connection-recovery-20261120/usb-cold-fix-verified.json`. The pinned release and its exact source are in the adjacent `c6-usb-candidate` directory.

### Fixed field camera address

Masthead 1.4.2 uses `192.168.8.2/24` when its saved network is
`Gladiator-Gateway` and its gateway URL is `http://192.168.8.1`. It uses DHCP
for other saved networks. The gateway's saved camera address is `192.168.8.2`
on the direct AP. Petey gets it from `/api/visual`, and the Android native
camera viewer already uses the same fixed endpoint.

When migrating an older installation, update the gateway before the camera.
If the old camera fails to rejoin after the gateway update, a full robot
power cycle lets it take a temporary address from the new DHCP pool. Verify
its `masthead-camera` role before sending the camera update to that address.
The camera returns at `192.168.8.2` after the new firmware starts.

November 20 installation evidence is in
`diagnostics/visual-calibration-20261120/`. The gateway build used the 2.4.17
release's operator-page assets and applied the addressing change to that base.

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
