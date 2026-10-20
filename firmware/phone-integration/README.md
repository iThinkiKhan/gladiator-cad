# Native phone camera integration

The Gladiator Drive screen lives in the Spectre Android companion app. Its
source is maintained locally in `C:/PlatformIO/Spectre/companion_app`; it is not
in this firmware repository. This patch contains only the camera additions and
the directly related background-drive safety change, not the companion app's
private configuration or unrelated source. No APK/credentials are published.

Apply at the Spectre project root with:

```sh
git apply --check --unidiff-zero gladiator-phone-camera.patch
git apply --unidiff-zero gladiator-phone-camera.patch
```

On this machine the tested changes were already applied to the original app
source and the same-signature release APK installed in place on the connected
phone. The old APK and changed source originals are backed up privately; no
settings/data were cleared.

The Drive screen has a pinned camera viewer above the scrolling controls. Join
`Gladiator-Gateway` Wi-Fi, then press **Start video**. The viewer opens the existing
`http://192.168.8.2:81/stream` directly; motor control remains BLE. It binds only
that video socket to the C6 Wi-Fi interface, preserving other Spectre routing.
Only one camera viewer is supported: stop any browser stream before starting
the phone viewer. Stop/retry is explicit; failed/stale video is cleared and
never displayed as live. Leaving Drive, backgrounding, or native teardown closes
the stream. Returning does not restart video. Backgrounding also clears held
drive buttons/disarms, and background heartbeats are suppressed.

The native bounded MJPEG reader runs off the UI thread, rejects malformed,
oversized or truncated frames, and holds only the latest decoded frame.
Android HTTP access is allowed only for this camera address in addition to
the existing home-map exception. No new dependency, camera credential, motor
command or mast enable path was added to the viewer.

Apply the subsequent [control fix](gladiator-phone-control-fix.patch) after the
camera patch. It removes the obsolete front/rear switch and second inversion:
mast is FRONT in both phone and S3. Forward sends positive L/R, Reverse negative
L/R, Left negative L/positive R, Right positive L/negative R. Power changes remain available while armed or moving. It resets to 25% on stop/reconnect/background/watchdog, and
clears the S3's release latch with a disarmed frame after watchdog expiry.
Normal encoded track commands cannot exceed the selected percentage; Overdrive
requires the explicit 100% Overdrive selection. Motor telemetry shows S3-reported
outputs and selected power. The S3 enforces the same PWM ceiling after straight-line trim and ramp; selected duty is not a measurement of vehicle speed.

Validation: Android release build/lint and TypeScript pass; 4,465 fixed-frame
drive checks and production BLE-frame/checksum/queued-stop checks pass; 14
production multipart-reader checks pass;
production component tests cover explicit Start, background Stop, no restart,
pinned placement and drive disarm/no heartbeat/no resume. Physical phone video
and coexistence/long-run acceptance should be checked on the robot Wi-Fi.

The camera card now offers **Camera aim, scan & field controls**, opening the unified field console. It first stops the native stream so the browser can become the single viewer. Backgrounding the native Drive screen disarms BLE as before. The field console then provides web drive, live video, aiming, saved calibration and camera image settings. Phone installation status is recorded in the deployment report; latest APK may require reconnecting the phone for in-place installation.
