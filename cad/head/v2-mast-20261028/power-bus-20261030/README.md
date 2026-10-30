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

## Distro PCB on the yoke floor - Jim's direction, 2026-10-30 evening

Jim: servos stay on their OWN circuit, powered from the power board (no shared 5V wire with the head), leads straight to
the lower deck as now. Trunk = 5V, GND, SDA, SCL only, soldered to a custom through-hole PCB that covers the mast hole
(the yoke wire passage) and is held by a modified yoke floor. The tilt servo lead keeps its current path, passing UNDER
the board through a cut-out. The pan servo lead (now running down the outside of the mast) should enter the mast where
its carriage holder meets the neck, maybe through a cut-out in the carriage so it is hidden.

clearance_map.py / lowenv.npy: worst-case free height above the yoke floor top (Z 206) over tilt -38..34, 2 mm cells
(Codex balanced model). pcb_envelope.py -> pcb_envelope_on_yoke_floor.png. DRAFT envelope, nothing modelled:
- Board about 21 x 25 between the yoke columns: X 40.6..61.9, Y 97..122.5, sitting over the wire passage (X 40.3..46, Y 107..119).
- Connector band Y 109..119 (under the tilt pivot): 30+ mm free at every tilt. Tall parts (headers, bulk cap) go here.
- Y 97..109: about 7-10 mm free, so parts <= 4 mm above the board. Y 119..122.5: about 4-8 mm free, board only.
- Front right (X 50..62, Y < 97): the camera case sweeps to about 2 mm above the floor at 34 deg camera-down. Keep out.
- Keep the driver hole to the pan retainer screw at (52.8, 99.7) r3.5 open (notch or hole in the board).
- 2 x M2 heat-set inserts in the floor (floor is 5.5 thick): draft positions (44, 99.5) and (58.8, 119.8).
- A 2 mm pocket in the floor for the board gains 2 mm everywhere; leave relief for through-hole leads underneath.
- Tilt servo lead: comes down the ear column (X 27.5..39.7) and enters the passage at its -X edge, under the board edge.

Pan servo lead route (proposal, not checked): the SG90 bottom (Z 150.2) sits level with the tube top (Z 150); the neck
arm joining the servo pad to the bearing post is Z 151..158; the collar's closed band is Z 142..150 above its -Y split.
A channel under the pad/carriage to a window through the collar and tube just below the tube top on the servo side
would take the lead inside. The carriage slides 10 mm (C38..48), so leave a slack loop. The SG90 plug (about 7.6 mm
wide) will not pass beside the M3 head bolt at Z 123 (about 4.5 mm each side): thread it with the bolt out, or
re-pin the plug after threading. A window in the closed band weakens the collar: check before adopting.
