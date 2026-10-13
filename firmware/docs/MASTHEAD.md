# Gladiator masthead firmware

Implemented October 13, 2026. **Both boards are flashed and the camera/C6 bench checks pass.** CAM USB writes verified on COM8; C6 OTA verified, including a second reboot under video load. After reseating the OV2640 ribbon, live QVGA video delivered 1,343 JPEG frames at 14.92 fps over 90 seconds. The camera recovered after a C6 reboot without resetting. The TFT is not connected yet, and the C6 has no live S3 telemetry, so physical display and sensor-driven expression tests remain outstanding. See [bench results](masthead/bench-20261013.md). Both target builds and host tests pass.

The CAM target is `firmware/cam/`; C6 integration is in the existing `firmware/gateway/` and `firmware/shared/` trees. This change adds three display endpoints and a masthead panel. S3 source, motor control, UART framing, transport failover, sensor ownership, and the S3/C6 pairing architecture are unchanged.

## Architecture and operation

```text
S3 motors/safety/sensors -- existing typed UART or Wi-Fi link --> C6 gateway
                                                                  |
                             /api/visual JSON, polled by CAM       | Wi-Fi
                                                                  v
                       ESP32-CAM: OV2640 + local ST7789 expressions
                                  |
                        HTTP :81/stream JPEG --> operator browser
```

The CAM is a Wi-Fi station on the C6's existing WPA2 access point or the same trusted LAN. It polls the C6 at approximately 5 Hz, renders eyes at a target of 15 Hz, and produces QVGA (320×240) JPEG video capped at approximately 15 fps. These are limits/targets, not measured performance. Two latest-frame camera buffers and the graphics buffer use PSRAM. No microSD driver or full display images over the network.

Camera streaming uses its own HTTP task and port; CAM status remains on port 80. Polling runs in a separate task from display rendering. A lost gateway connection produces animated gray idle eyes within 1.5 seconds of the last accepted response. Wi-Fi reconnect attempts occur every 10 seconds. Camera initialization failure is logged and leaves the display running; correct the wiring/power and reboot to retry initialization. A failed stream closes its socket; the operator starts video again after reconnection.

The C6 translates **S3-reported** presentation states and fresh sensor data:

| Priority | Condition | Expression |
|---|---|---|
| 1 | Controller telemetry absent or at least 500 ms old; unknown S3 state | Offline |
| 2 | S3 battery LOCKOUT/CRITICAL, or valid range below 500 mm | Alert |
| 3 | S3 DRIVE | Active |
| 4 | Valid presence sensor reports present | Greeting |
| 5 | S3 ARMED | Scanning |
| 6 | S3 SAFE | Ready |

Range/presence samples must have health OK and age below 1000 ms, including transport age. Battery voltage must have health OK and age below 500 ms. Unavailable measurements are JSON null, never a fabricated zero-distance detection. The threshold is a display effect, not an obstacle avoidance rule. Scanning eyes indicate the ARMED presentation state or a requested animation; they do not assert that a sensor scan is occurring.

Authorized display commands last 1–60 seconds and then return to automatic mode. Offline and automatic alerts take priority over temporary expressions. No display endpoint queues commands to the S3 or acquires a motor session. The separate LiDAR remains on the S3.

## Wiring: camera preserved, microSD unused

**Confirm the exact display module before applying power.** Eight signal labels identify an SPI connection, but do not establish VCC/backlight voltage, current limiting, or resolution. The default here assumes a 170×320 ST7789, rotated to landscape. Confirm against the actual seller/manufacturer documentation; change the three display defines in `cam/src/LocalConfig.h` if needed. A 1.9-inch size alone is insufficient evidence.

| Display label | Connection | Notes |
|---|---|---|
| SCL | ESP32-CAM GPIO14 | SPI clock, not I²C |
| SDA | ESP32-CAM GPIO13 | SPI MOSI, not I²C |
| DC | ESP32-CAM GPIO2 | Strap pin: display must not force it high during UART download |
| CS | ESP32-CAM GPIO15 | Display chip select; strap pin, keep external loading light |
| RES | Pull up to **3.3 V**, typically 10 kΩ | Software reset; no GPIO reset connection |
| BLK | Fixed backlight supply/driver per module documentation | Never assume this is a 5 V-tolerant input or a current-limited LED |
| VCC | Module's documented supply | Prefer 3.3 V only when the module supports it; no 5 V logic |
| GND | Common ground | CAM, screen, and regulator |

Keep GPIO4 off and unconnected to the screen: on the AI-Thinker board it drives the white flash LED. GPIO12 remains unused because its boot strap can select an incompatible flash supply. GPIO16/17 are not spare PSRAM-compatible display pins. GPIO0 remains the camera clock during normal running and is grounded **only during flashing**. Camera ribbon stays on its original board. Leave the microSD slot empty.

Regulated 5 V from the deck supplies the **CAM board's 5 V pin**, not its 3.3 V pin. Use short local power/ground wiring and a regulator with adequate transient current capacity for camera, Wi-Fi, and the screen. Do not assume the CAM's onboard 3.3 V regulator has spare capacity for an unknown backlight; use a separate suitable local 3.3 V regulator if necessary. All SPI logic is 3.3 V. Boot failures, brownout messages, and corrupt frames require power/wiring investigation, not disabling brownout protection.

RES pulled high allows the library's software reset at startup and avoids the GPIO4 LED conflict. This is a design choice that needs a cold-boot test on the actual panel. If the module requires a hardware reset circuit, add a suitable power-on reset circuit to RES; do not consume a camera/PSRAM pin or connect RES to GPIO12 without reviewing the straps.

## Configure, build, and first flash

1. Copy `cam/src/LocalConfig.example.h` to `cam/src/LocalConfig.h`. Set SSID/password to the existing C6 AP credentials obtained through the existing USB provisioning workflow. Set `VISUAL_GATEWAY_URL` to `http://192.168.8.1`. For LAN operation, use the common LAN SSID and the C6's reserved LAN IPv4 address. Do not use a network with wireless client isolation.
2. Confirm panel dimensions/rotation in that header. Keep the OV2640 pin map intact. For C6, copy `shared/secrets.example.h` to the ignored `shared/secrets.h` and set the existing robot field password. Set the CAM Wi-Fi password to the same field AP credential in ignored `cam/src/LocalConfig.h`. Preserve any existing S3/C6 pairing-key override identically on those two boards. The CAM does not use the robot-link pairing protocol. A fresh public checkout contains placeholders; do not overwrite a deployed board with an unconfigured build.
3. Build using PlatformIO:

   ```powershell
   pio run -d cam
   pio run -d gateway
   ```

4. First flash the CAM with a USB-UART adapter using **3.3 V UART logic**, TX to CAM U0R/GPIO3, RX to U0T/GPIO1, common ground, and suitable regulated 5 V board power. Disconnect screen DC/GPIO2 during flashing if its loading prevents download mode; first bring-up with all screen signal leads disconnected is simplest. Do not power the assembly simultaneously from conflicting supplies.
5. Ground GPIO0, reset/power-cycle into the UART loader, then run `pio run -d cam -t upload --upload-port COMxx`, replacing COMxx with the adapter's actual port. Remove the GPIO0-ground jumper and reset to run. GPIO0 is required for the camera clock. Read logs at 115200 baud using `pio device monitor -p COMxx -b 115200`.
6. Upload the integrated C6 through its established `/dev` OTA workflow using the newly built `gateway/.pio/build/gladiator_c6/firmware.bin`. Keep the robot disarmed during maintenance. An S3 update is not needed. The C6's existing NVS station settings/admin key and OTA partition layout are preserved.
7. Read the CAM IP from serial, open `http://CAM_IP/api/status`, and reserve its DHCP address on the selected network. Open the C6 field interface, expand **Camera setup**, enter that private IPv4 address, and save using the existing maintenance key. Camera address is persisted in the C6's separate `visual` NVS namespace.
8. Press **Start video**. The image connects directly to `http://CAM_IP:81/stream`; C6 never proxies the JPEG stream. One viewer at a time. The C6 field page must be served over HTTP, as in the existing firmware; an HTTPS reverse proxy needs a matching camera proxy to avoid mixed-content restrictions. Video stops when the page is hidden or the image errors.

The deployed CAM was configured for the existing C6 access point. Credentials, configured firmware binaries, and captured images are deliberately excluded from GitHub. Build from source with your local secrets and use the matching PlatformIO target so the bootloader and partition offsets match the board.

## Display API

`GET /api/visual` on the C6 is a small read-only snapshot. Schema 1 contains `fresh`, `mode`, `state`, `battery`, optional `volts`, `nearestMm`, `present`, `message`, `override`, `cameraIp`, and `streamUrl`. CAM response bodies are bounded to 1536 bytes; body collection has a 300 ms deadline. This read-only HTTP telemetry relies on the trusted WPA2/LAN network. Existing robot-control transport authentication is unchanged.

`POST /api/visual` requires the existing `X-Gladiator-Key` maintenance header. Example bodies:

```json
{"mode":"scanning","leaseMs":30000,"message":"Looking around"}
```

```json
{"mode":"greeting","leaseMs":30000,"message":"Hello!"}
```

```json
{"mode":"auto"}
```

Modes: ready, scanning, active, alert, greeting, offline, or auto. Messages are up to 48 printable ASCII characters. A temporary expression requires fresh, known S3 state; it cannot conceal an automatic alert.

`POST /api/visual/config` also requires the maintenance header. Body `{"cameraIp":"192.168.8.2"}` stores the camera address; `{"cameraIp":""}` disables the video link. Only literal private IPv4 addresses are accepted.

On the CAM, `GET /api/status` reports camera readiness, stream/frame/error counters, RSSI, heap/PSRAM, buffered-display availability, and current effective mode. The CAM root page can start/stop video independently. CAM configuration currently uses the local build header and serial upload; OTA camera updates and mDNS are future additions.

## Verification and bench acceptance

The two target builds pass. Host tests execute the production display policy and C6 handlers with HTTP/NVS/time doubles, plus the field page's actual JavaScript in a DOM mock. They cover stale controller/sensors, priority, lease expiry, unsigned clock wraparound, unauthorized display commands, malformed inputs, private-IP validation, opt-in video, visibility/error handling, URL changes, and separation from motor commands. These do not prove physical SPI alignment, radio latency, heap endurance, or C6 control timing under load.

Run `tests/run_host.ps1` on Windows with PlatformIO's `toolchain-gccmingw32` and Node on PATH, or `sh tests/run_host.sh` on Linux with GCC. Build the gateway first so its managed cJSON dependency is available. The existing motion JavaScript was compared against the base revision and remained unchanged. Only the new masthead UI and its separate API requests were added.

Before the event:

- Verify camera alone, then display alone, then simultaneous video and animation. Confirm PSRAM detected, image orientation, colors, panel offsets, and repeated cold boots with the screen connected.
- Run video plus a scanning expression for at least 30 minutes. Inspect heap/PSRAM and error counters at start/end; measured throughput/latency must be acceptable to the operator.
- With S3 SAFE, request scanning then greeting while streaming. Confirm return to automatic at expiry. Use actual valid LiDAR/radar data to test automatic alert/greeting; their unavailable state must not generate detection effects.
- Interrupt C6 Wi-Fi, restart the gateway, and reconnect. Confirm eyes go offline and recover; stream can be started again. UART/S3 motor authority must remain independent.
- Confirm existing field control telemetry remains responsive with a CAM polling and a browser streaming. Check C6 frame-error/drop counters. Perform any physical track test using the established tracks-clear procedure.

## Hardware and library references

- [AI-Thinker ESP32-CAM schematic](https://docs.ai-thinker.com/_media/esp32/docs/esp32_cam_sch.pdf): camera, flash LED, and PSRAM wiring.
- [Espressif boot-mode selection](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html): GPIO0/2/12/15 constraints.
- [Espressif camera driver](https://github.com/espressif/esp32-camera): JPEG, PSRAM, and framebuffer behavior.
- [Pinned Adafruit ST7789 implementation](https://github.com/adafruit/Adafruit-ST7735-Library/blob/1.11.0/Adafruit_ST7789.cpp): software reset and centered panel offsets.
- [Waveshare 1.9-inch module](https://www.waveshare.com/wiki/1.9inch_LCD_Module): an example of a 170×320 ST7789 panel, **not confirmation of the installed module**.
