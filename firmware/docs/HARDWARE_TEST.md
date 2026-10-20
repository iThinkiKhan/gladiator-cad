# V2 phone hardware tester

Gateway 2.2.3 serves the guided tester directly at
http://192.168.8.1/hardware-test/ on Gladiator-Gateway Wi-Fi.
The root driving page links to it. A PC or Internet connection is unnecessary.

Tap Connect to robot, identify GPIO10/13 one at a time, record measured positions,
and save calibrated limits through the S3 before deliberate enablement.
The first pulse is left blank because the physical servo position is unknown.
See ../tools/hardware-test/README.md for the installed commissioning process.

Hosting adds only static GET routes to the existing gateway architecture.
Controls use the existing S3-authoritative mast/commissioning APIs, safety checks,
limits and leases. No new drive/ARM controls, automatic enable, hardware gate,
network provisioning change or camera/display firmware update is introduced.
Camera, sensor and mechanical faults remain visible and require their own diagnosis.

The local PC variant remains available for development. The C6 build regenerates
compressed assets from the same source files using the PlatformIO pre-build hook.
Compiled firmware, private configuration, backups and runtime logs stay local.

Development recording works while slewing or after Stop, expiry or link loss.
Recorded values are retained as a partial draft on the phone, not gated behind
motion-session checks. Full measured calibration is applied to S3 separately.
Repeated start/save acknowledgment checkboxes are removed; deliberate enable,
S3 commissioning checks and calibrated motion limits remain.

## Robot memory and pulse testing — gateway 2.2.4

Individual centers/endpoints and edited limits now commit to C6 NVS through
GET/POST /api/mast/setup, with revision checks, partial-field merge and flash
readback. Other devices load the robot record on Connect. Complete applied aiming
calibration remains persisted/enforced by S3 and its current limits are displayed.
Use Save current entries to migrate an earlier phone-only draft.

Testing now provides 5–100 µs steps, direct target entry, a slider and 500 µs
windows that can be stopped/repositioned around the current S3 command. S3 ramps
subsequent moves at 100 µs/s. No automatic enablement or motion on reconnect.

Tilt is confirmed on GPIO13 with regulated 5 V/common ground. No GPIO/PWM resource
conflict was found in the deployed S3 source. Physical pegging remains unresolved;
target and commanded pulse are shown independently to support waveform/wiring/servo
diagnosis. No live movement was commanded by the agent.
