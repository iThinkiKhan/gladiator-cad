# Gladiator field sequencer

The C6 hosts `/booth/` and serves these assets locally. Open `http://172.23.44.190/booth/` on Opal with one staff controller. The tablet is outside this release.

Use the step cards to edit expressions, waits, tracks, mast angles, or a coordinated **Tracks + mast** cue. Duplicate, remove and reorder steps; Preview applies advanced JSON edits. Choose Once, a count, or Until STOP; the cycle pause is 1â€“60 seconds. Save retains the steps and playback preferences in this browser. Export/Import transfers the step array; choose repeat options again on the destination. Reload never starts playback.

Movement requires deliberate supervision. Mast movement additionally requires a saved, applied S3 calibration and the mast checkbox. All mast bounds are checked before acquiring either actuator. Enabling mast moves to measured neutral. Coordinated targets are submitted concurrently from one fresh controller snapshot; physical arrival is not synchronized or measured. During a pause the tracks are zero and the mast holds its target. STOP ALL, Escape, leaving/hiding the page, stale data, a delayed control loop, changed ownership, rejected commands or a controller restart end the show. Keep the page visible and the device awake; no reconnect/resume/autostart exists.

Per-cycle limits: 40 steps, 90 seconds total, 5 seconds of track commands; each track cue is at most 1.5 seconds and +/-25 percent. Repeats are a supervised lease-controlled session, not distance control. Reversing does not guarantee return to the start. Rehearse with tracks raised clear, then in a small safe envelope on the actual van floor. Servo OFF releases holding torque.

## Checks

- `node tools/booth/test.cjs`: runner safety and sequencing unit checks.
- `node tools/booth/test_ui.cjs`: isolated browser checks and desktop/phone renderings; uses the bundled Playwright runtime.
- `python tools/booth/measure_latency.py --host 172.23.44.190 --path /api/crowd --samples 20`: read-only LAN timing.
- `node tools/booth/test_live.cjs 172.23.44.190 RECEIPT.json`: real display-repeat and uncalibrated-mast preflight checks. Add `--disconnected-tracks` ONLY after physically disconnecting motors; it deliberately arms and sends three short forward/reverse command cycles. No mast movement test is included.
- `python tools/booth/exercise_recovery.py --host 172.23.44.190`: finite recovery Wi-Fi leases with motion required OFF; checks both controller boot IDs, live grid, diagnostic JSON and radio dwell. Intentional radio transitions can briefly make telemetry stale; motion pages must still stop on that condition.

Firmware builds embed the current assets automatically. Deployment is a separate maintenance operation; do not re-upload just because a verification times out. Receipts, original-source copies and credential-bearing recovery images remain in local `diagnostics/booth-20261022/`, not on the NAS.

## Saved-settings operator update â€” October23

Prepared gateway-2.4.0 adds saved/applied calibration status, revision-safe Apply with S3 readback, calibration backup and reusable commanded poses. The manual-aim link loads the existing operator view without enabling outputs. New measurements block an outdated profile from being used by a mast routine; STOP also cancels its preflight. Profiles already applied reload on the S3 at boot. No S3 firmware change is needed. See docs/SAVED_SETTINGS_OPERATOR_2026-10-23.md for installation status and use.

Additional checks: `node tools/booth/test_settings.cjs` and `node tools/booth/test_settings_ui.cjs`. `python tools/booth/deploy_c6.py --check-only` verifies the candidate's version, embedded assets and hash without contacting a robot. Actual installation requires stopped outputs and a verified baseline; the tool reads/computes the latest saved setup before upload and compares it afterward.


Installed gateway-2.4.3 adds bounded native-diagnostics streaming and pauses missing-Opal scans during a direct AP session. Saved settings/sequence assets retain their verified behavior. Read-only USB check: `python tools/booth/check_c6_usb.py --out diagnostics/field-usb-latest.json`; bounded LAN check: `python tools/booth/check_gateway_readonly.py --host 172.23.44.190 --seconds 60 --out diagnostics/field-lan-latest.json`. A subsequent 180-second read-only Opal check passed with zero HTTP errors and median crowd GET36.3ms; physical motion and event-length verification remain pending. USB summaries include Wi-Fi status/IP; Check-Opal-LAN.cmd provides a one-click read-only check. See the current operator guide for measured limits and installation receipts.
