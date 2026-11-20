# Manual test continuity — 2026-10-22

Installed gateway2.3.3 via authenticated C6 OTA. New boot/ota_1 and unchanged S3
boot verified. All three hosted hardware-test assets match source. S3, CAM,
pairing, normal aiming profiles and motion rates were not reflashed or changed.

Jim reported losing control after moving in one direction or recording center.
Live S3 telemetry showed healthy power/UART, no initial rejections and explicit
"Outputs stopped". A browser regression reproduced visible-page blur sending OFF.
Manual tests now survive visible focus changes and transient stale/failed status
reads; commands wait for fresh telemetry. Hiding/leaving still requests OFF and
S3 leases still expire without keepalives. Reconnect preserves an existing manual
test and offers explicit Resume for its GPIO, adopting reported state without a
new starting pulse. Ended/rejected tests clear local state without an extra OFF
and permit another Start. Calibrated aiming retains its existing background/link
behavior. This change is limited to the manual-test workflow.

Native C6 and local-bridge Chrome suites pass. New coverage includes visible blur,
a stale sample, a brief HTTP failure, reconnect/resume without a first-pulse or
OFF request, reversing from1150 to1800 while saving endpoints, preserving center,
and restarting after the S3 ends a test. The initial blur regression failed before
the fix and passed afterward. Existing calibration, storage, layout, control and
camera cases remain covered. C6 target build passes.

Robot C6 NVS revision4 verified after reboot:
- tilt GPIO13, lower1150 us, neutral1500 us, upper1800 us;
- pan GPIO10 assignment only; no pan center/endpoints guessed.
These are partial setup records. The S3 still reports calibrated=false; a full
normal aiming profile has not been applied. Raw commissioning remains500–2500 us.

Jim reports that tilt reaches1800 and holds, although lifting appears labored.
The existing100 us/s ramp is unchanged:1500 to1800 takes about3 seconds in software.
This does not establish servo torque margin or regulator voltage under load.
No live pulse or nonzero track command was sent by the agent.

Runtime evidence, image hash, source backups, before-fix reproduction and test logs:
C:/PlatformIO/Gladiator/diagnostics/test-continuity-20261022.
