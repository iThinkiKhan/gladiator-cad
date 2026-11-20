# Manual tilt pulse range — 2026-10-22

Jim requested removal of the 500 microsecond commissioning window while manually
establishing installed tilt travel. The tester now always requests 500–2500 us,
with no window-size controls, shifting or restart at the old 1250/1750 boundaries.
S3 PulseTest removes only the width test; GPIO, parser envelope, timing and
other controller behavior are otherwise unchanged. Saved partial centers/endpoints
and full applied calibration retain their existing storage semantics.

User-confirmed observations: tilt is GPIO13; 1500 us is neutral. Lower pulse values
point the camera down and lift the display. C6 NVS revision 2 was read back as
{tiltPin: "13", tiltNeutral: "1500", panPin: "10"}. No endpoints were guessed.

Canonical tester, shared MastPolicy, generated gateway assets and gateway version
2.3.2 are updated in C:/PlatformIO/Gladiator. The installed S3 release remains the
existing October14 final-integration/firmware source, whose main application,
orientation, power handling and drivers differ from the independent older
canonical root S3 application. That existing release was patched in place for
this build; it was not replaced with the older canonical S3 application.
Both copies of MastPolicy are identical. Original changed source files are
backed up under diagnostics/manual-tilt-20261022; candidate hashes are recorded
there. No credentials or compiled images were published.

Validation: S3 and C6 target builds pass. The production mast policy passes
363,909 angle cases plus full-envelope starts, both target extremes, out-of-range
rejection and existing timing/expiry checks. Native C6 and local bridge Chrome
suites pass, including 500/2000/2500 us simulated targets, removed shift control,
partial robot saves/readback, reconnect, separate-client saves and phone layout.
All 10 bridge HTTP tests pass. No live servo pulse or nonzero drive command was sent.

Installation completed over USB-UART COM13 (CH340K), then C6 OTA. The S3 chip
identity dc:b4:d9:13:4f:94 matched the connected board. A private backup covers
0x8000 through all overwritten application bytes (partition table, NVS and OTA
metadata included). Only app0 at 0x10000 was written; esptool verified the image
hash. NVS, bootloader, partition table and OTA metadata were not written.
S3 reboot telemetry reports testRangeMinUs500 and testRangeMaxUs2500.
Gateway2.3.2 then installed to ota_0, with changed C6 boot/slot and unchanged S3
boot across the C6 update. All three hosted hardware-test assets match source.
Saved setup revision2 is unchanged: GPIO13 tilt neutral1500, pan GPIO10.
Mast/test outputs are off and tracks are disarmed. No live pulse or nonzero drive
command was sent. Full receipt and backup hashes: diagnostics/manual-tilt-20261022.
The native S3 USB interface was bound to Android ADB on this PC; the user moved
the cable to USB-UART, avoiding any Windows driver change. Earlier web-OTA reset
and ArduinoOTA transfer failures remain historical limitations, not repaired OTA.
