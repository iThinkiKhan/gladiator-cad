# V2 phone hardware tester

Gateway 2.2.2 serves the guided tester directly at
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
