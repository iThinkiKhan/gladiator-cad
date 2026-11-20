# Verified masthead display wiring

Physically verified November 9, 2026: ST7789 1.9-inch 170x320 screen, mounted in landscape at 320x170, rotation 3.

**Purple DC on GPIO12 caused static/blank output. Moving it to GPIO2 restored the face and status screens.** GPIO numbers refer to printed IO labels, not header positions.

| Screen signal | Wire | CAM connection |
| --- | --- | --- |
| DC | Purple | **IO2 / GPIO2 — not IO12** |
| SDA / MOSI | Green | IO13 / GPIO13 |
| CS | Blue | IO15 / GPIO15 |
| SCL / SCLK | White | IO14 / GPIO14 |
| RES | Existing lead | CAM 3V3 |
| VCC | Existing lead | Shared masthead 5V header |
| BLK | Existing lead | 5V |
| GND | Existing lead | Common GND |

The CAM and laser matrix also use the shared 5V header, as Jim reported. The screen breakout's exact manufacturer and voltage ratings remain unidentified; this records working wiring rather than certifying its voltage ratings. RES is a logic reset input: never move it to 5V. CAM 3V3 measured about 3.3V.

CAM masthead-1.3.6 is installed and confirmed in app1; app0 retains 1.3.5. Normal settings are hardware SPI mode 0, 1MHz initialization and 4MHz drawing. Temporary authenticated display diagnostics expire within 120 seconds; all tests are OFF in normal operation. No SD card is required, and the firmware does not initialize SD.

GPIO2 configuration and input readback agree HIGH between writes. Earlier 0V readings were on GPIO12 and do not establish GPIO2 damage.

Evidence: diagnostics/screen-recovery-20261109/io2-corrected/REPORT.md and verified.json. OTA receipt: diagnostics/screen-recovery-20261109/dc-probe/installed.json. Final video check: 141 JPEGs in 10 seconds (14.1fps), then stream closed. This assistant sent no actuator commands.
