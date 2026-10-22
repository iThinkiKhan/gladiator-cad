# ESP32-CAM case v4 - replaces the SEN0610 presence-sensor frame (2026-10-13)

Two printed parts hold an AI-Thinker ESP32-CAM beside the SEN0628 8x8 ToF on the GH44 dual carrier.
Only the lens (front) and the microSD slot (top end) are open. The only other opening is a small wire exit.
**Not printed and not fitted yet.** v4 supersedes v1-v3 (all unprinted). v2 used Jim's caliper heights, v3 added the independent review, v4 uses all 16 pins with wire slots in both side walls and a shallower rear.

| Part | Print orientation | Notes |
| --- | --- | --- |
| `ESP32_CAM_Case_v4_Tray.stl` | floor (carrier face) down, opens up | 31.95 x 53.85 x 29.9 mm, no supports. Bridges: SD window (17 mm), wire exit (9 mm) |
| `ESP32_CAM_Case_v4_Lid.stl` | outer face down, lip/posts up | 31.95 x 53.84 x 8.2 mm, no supports |

PLA, 0.2 mm, 4 walls, 30% infill (same as the head plates). Tray about 13.4 cm3, lid 3.2 cm3.
**Plate:** `Gladiator_Head_ORCA-D_ESP32-CAM-Case_v4_Tray-and-Lid.3mf` (OrcaSlicer, EnderNeo / Generic PLA First Print /
0.20 Standard, no supports, no brim). Headless slice: **1 h 40 m, 18.9 g, 149 layers**; 76 x 54 mm on the bed.
Only overhang walls in the G-code: lid counterbore ceilings (z 1.5), the four wire-slot roofs (z 6.5, 9.7 mm each), SD window roof (z 28.7-29.5, 17 mm).
Open it in Orca and look at the preview before sending (the project was sliced from the command line only).

## Jim's caliper values used (all from the bare back of the PCB, 2026-10-13)

PCB 0.8. SD holder top 4.4. Camera square top 6.75 (it rests on the SD holder). Lens tip 9.4, lens a 7 mm circle.
ESP32 module + PCB thickest 6.2. The STEP's PCB, SD holder, camera and module heights were replaced with these;
all other STEP parts (header pins, small parts) are as supplied. Camera square footprint and lens position come from the STEP.

## Layout (head frame: +X right, +Z up, sensors face -Y)

* The tray takes the old radar frame's place: board centre x = 26.5. It bolts to the carrier through the **same three
  M2 holes** the radar frame used, at (37.5, +-8) and (24.5, 12), with 3 x M2x6 from the carrier rear. Tray floor is 3 mm,
  the same engagement as the radar frame. Remove the radar frame and the SEN0610.
* **Board orientation:** portrait, **SD end up**. The lens is on the board centre line, 8.9 mm above the tilt axis.
  The card slides in from the top: 17 x 5.2 mm window in the top wall, with the outer wall thinned to 1.0 mm around it (finger recess)
  so an ejected card can be grabbed.
* **Lens:** the lid inner face is 7.3 mm above the PCB back (0.55 mm over the camera square), the lid face 9.3 mm. The 7 mm lens
  comes through a 9 mm hole and ends 0.1 mm proud of the lid face (the hole allows 1 mm of placement slop each side).
* **Rear zone / wires (all 16 pins):** 19.7 mm between the PCB back and the tray floor holds the header pins (9 mm, straight) plus a
  Dupont female housing on every pin (modelled 14 mm long) and a 3 mm bend. Each wire turns sideways at the connector end and leaves
  through a slot in the **left or right long wall**: each wall has two slots (pins 1-4 and 5-8, 9.7 mm wide, 3.4 mm tall, sitting on the floor),
  split by a 0.8 mm strut so the roofs print without supports. Left-row wires go toward the ToF side and the carrier cable slot; right-row wires leave the other side.
  You will need to route the right-hand bundle around the tray (over the top or bottom end) to the cable slot; tie or tape both bundles to the carrier face.
* **Retention:** four 45-degree pads under the PCB corners (the only places clear of components on the back of the
  board), four lid posts on the front corners (0.3 mm gap to the 0.8 mm PCB), and a lid lip. The lid is held by 4 x M2x8 into the tray's four ears.
* **Clear of the ToF:** left wall is 0.78 mm from the ToF frame. The lens ends 3.5 mm ahead of the ToF front
  reservation plane (the case is about 32 mm deep), so the ToF never sits in the camera's view.

## Assembly order (matters: the display and carrier screws are under the case)

1. Carrier on the tilt receiver with its 4 x M3 (unchanged).
2. Tray onto the carrier: 3 x M2x6 **from the carrier rear**, before the display frame (same as the radar frame).
3. Display frame: 4 x M2 from the front. The right-hand pair goes through the tray floor (5.4 mm holes).
   The two M3 carrier heads at x=16 sit in 6.8 mm pockets, so those stay serviceable with the lid and board off.
4. Thread the free (male) ends of the jumper wires from inside the tray out through the slots: the left-row wires through the left wall,
   the right-row wires through the right wall. Push each female end onto its pin, then lower the board in, lens side first, SD end up, and seat it on the four pads.
5. Lid on (lens through the hole), 4 x M2x8 into the ears. Screw heads stand about 1.4 mm proud.

## Before you seal it

* All 16 pins are wired out, so you can still flash through the jumpers (GPIO0 to GND for boot mode, U0T/U0R for serial); the board does not need to come out of the case.
* The white flash LED is under the lid (no window); keep it off in firmware.
* No vents: the ESP32-CAM runs warm streaming video. Add vent slots in the lid if it gets hot in testing.
* The board has no mounting holes; it is held by the pads and posts, with about 0.4 mm slop in each direction.

## Independent review (2026-10-13) and what it changed

Re-checked by different methods from the build script: exact mesh booleans on the exported STLs (no case/carrier/ToF/lid-tray overlap),
200k-point board-surface containment (0 points inside the case, 0.3 mm to the lid), a print-overhang analysis of the print-oriented STLs,
and landmark checks (card tip x 22.0-33.0 / z 20.8 inside the 17.7-34.7 window; lens centre on the hole). New probes in the CAD script:
M2 screw shanks clear the carrier holes, the jumper path from the notch to the cable slot clears the ToF frame, the SD card sweeps out
through the window, and a 1-degree tilt sweep. FOV assumptions checked against specs: SEN0628 is 60 deg (checked with 90), stock OV2640
is about 52-68 deg (checked with 80); even a 120-160 deg lens never sees the ToF because the lens is 3.5 mm ahead of it.
Found and fixed: a probe of mine that tested the wrong thing (shank vs tray instead of vs carrier). Improvement: SD finger recess.
Not changed on purpose: no strain relief for the jumpers (tie or tape them to the carrier face), no vents.
v4: depth is dominated by pin + connector length (about 16.7 mm behind the PCB); shorter Dupont housings shrink the case 1 for 1.

## Checks passed (validation.json)

No overlap of the case with the board, carrier, ToF frame, ToF envelope, display frame or receiver. PCB sits on the pads
with 0.3 mm to the lid posts; the lens is 1.0 mm from the hole edge. All 16 header-pin Dupont housings clear the tray and
the 5.4 mm-deep module, with 3.0 mm behind them and 1.0 mm to the wall, and a 1.4 mm wire probe from each connector out through its slot clears the tray (0.17 mm from the strut). Driver paths to the display screws and carrier M3
screws are clear. A 90-degree ToF pyramid and an 80-degree camera cone are clear of the case and frames. 451 pan/tilt poses
(pan -200..200 in 10s, tilt -25..25 in 5s) clear. At +25 degrees tilt the tray's lower mating edge would hit the yoke base
plate, so it carries a 45-degree bevel below z -19.5.

## Still to verify on the real parts

* Lens centre is 11.4 mm from the SD end (STEP). The 9 mm hole absorbs about 1 mm of error each way; check once the tray is printed.
* Camera square footprint 15.5 x 8.5 mm (STEP). Only its height (6.75) was measured.
* Dupont housing length 14 mm and wire bend 5 mm. If yours are shorter, or you solder the wires, the case can be
  shorter by roughly 8 mm. Header pins are assumed soldered in (9 mm behind the PCB, from the STEP).
* Lens height tolerance: the lens sits 0.1 mm proud; a 0.3 mm shorter lens ends 0.2 mm below the lid face, still fine.

Source: `scripts/build_esp32_cam_case_v4.py`; reference model `reference/esp32-cam/ESP3-CAM.STEP` (supplied by Jim).
Hardware layout from `cad/head/v05-sensor-mounts/`.
