# Masthead v2 power bus spot study - 2026-10-30 (Claude)

Jim wants a 5V + GND bus at the top of the mast so fewer wires go up the tube. Near term: a breadboard like the
one on the deck (46.3 x 35.5 x 9.3, 21.5 tall with Duponts), or a cut-down breadboard power rail (9.5 wide, 9.3 tall).
Later: a perfboard with JST connectors. STUDY ONLY: v2 generator, CAD and print files are unchanged.

Findings (bb_spots.py, bb_rail.py; tilt -90..90 every 2, pan -20..180 every 10):
- The yoke floor (Z 200.5..206, X 12.5..72.5, Y 92..127) has no room: columns stand on it, and a rail on it
  with Duponts limits tilt to 20 up / 12 down (middle) or 24 up (rear strip).
- Beside the head on the -X side (opposite the camera case), outside the head X range, nothing touches in
  any tilt or pan pose. The shelf touches the head only past 48-52 deg camera-down (v2 limit is 34).
  - Cut rail 34 mm: shelf from the yoke floor edge X 12.5 out to X -17 (30 mm).
  - Full breadboard: shelf out to X -43.5 (56 mm).
- A +X shelf passes under the camera case and limits camera-down to 28-32. A rear shelf works but sticks out 40+.

Picture: power_bus_spots.png (picture.py, from export_spots.py meshes).

## Recessed spots and distro-board idea - 2026-10-30 later

Jim re-measured the rail: 82 long, 9.3 wide, 9.2 deep; plan 2 rows x 3 groups of 5 (about 46-49 mm, not measured).
recess_spots.py (Codex balanced model, tilt -38..34 every 2 at pan -20..180 every 20), envelope 48 x 9.5 x 9.3 + leads to 21.5:
- S1 screen-frame side window (side opposite the camera, 50 x 24 opening): clear in every pose. It IS the screwdriver
  path to the tilt horn screw (first hit along the tilt axis is the horn at X 20.2), so leave a hole on the axis or make it removable.
- S2 brim on top of the screen bezel: clear in every pose (adds about 21 mm of height with leads plugged in).
- S3 pocket on the neck collar: hits the pan rotor; the 20 mm tube itself has no room for a pocket.
Picture: power_bus_recess.png.

Jim is leaning to a custom through-hole distro PCB instead (trunk soldered to it): 5V, GND, SDA, SCL (+ tilt and
maybe pan servo signals). The ST7789 is driven by the ESP32-CAM, so no SPI goes down the mast. Open: ToF breakout
voltage, radar return, servo signals on the trunk vs a PCA9685 on the board. S1 also suits a small PCB.
