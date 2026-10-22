# Gladiator head v0.4 — corrected mechanical head, 2026-10-05

The current native CAD, STEP, STL and Plates 2–4 include the reviewed tilt screw fix.
The 1.2 mm retaining roof remains intact and the final screw passage is cut after the
support arm is fused. Plate 3 is the corrected receiver version.

Jim's 16.5 mm horn-height measurement is to the raised center hub. The calibrated
post20.05, M2 pilots2.35, horn pocket0.15 and nut pockets6.0AF remain in use.
Circlip seating is confirmed. Neck_Main is on Plate4; the old horn-height hold is closed.

The master and inherited v03 source are unchanged. 117,950 sampled part/pose comparisons
pass, with zero detected collision, zero modeled ToF obstruction and a clear11.9 mm axial
cable probe. All24 assembly solids and11 print meshes pass. Native/STEP reopens pass;
every Plate1–4 triangle matches its canonical STL within export precision.

The v04 sensor carrier and square ToF reference are historical placeholders. Use
**../v05-sensor-mounts/** for the measured42 x27.5 ToF and22 x30 radar mounting system.
v05 preserves all v04 mechanical parts except its widened sensor carrier; Plate5 adds
the carrier and two removable sensor frames.

Print orientations and support requirements:

| Plate | Parts | Supports |
|---|---|---|
|1|Raised pedestal, retainer, clamp cap|Pedestal top plate only; keep belt channel clear|
|2|Rotor, drive pulley, servo carriage|None|
|3|Tilt yoke, corrected receiver, rear display frame|Display tabs only|
|4|Neck_Main|C arm, pad and riser; brim recommended|

PLA,0.2 mm layers,4 walls,30–40% infill; verify slicer preview. Plate containers are
geometry only and do not include printer profiles. Do not auto-orient.

Assemble yoke-to-pedestal bolts before fitting tilt servo and receiver. Fit the receiver
horn screw along the tilt axis from the left. Pan60 degrees gives access to the pan-drive
service screws. Bearing/spacer/screw/belt fit must still be checked in actual assembly.
The modeled9 mm inner-race spacer is reference hardware, not confirmed stock.
Complete flex harness, strain relief and mechanical stops remain unfinished.

Files: native FCStd and STEP at real robot position; stl/; plates/; validation.json,
artifact-verification.json and build-summary.txt. The original README is preserved in
cad/head/integration-20261005/before/20261005T160338Z/.
