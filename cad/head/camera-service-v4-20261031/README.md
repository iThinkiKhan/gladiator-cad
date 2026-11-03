# Gladiator camera case v4 (camera service v4) - CAD draft, 2026-10-31

v3 (cover on M2 heat-set inserts) plus a window for the flash LED and clips that keep the Dupont plugs on the
header pins. Not printed, not sliced. The v3 folder is unchanged.

## What changed from v3

| | v3 (Oct 30) | v4 |
|---|---|---|
| Flash LED (GPIO4, the 5 x 5 mm white LED at the far corner) | behind the solid cover | 6.3 x 6.6 window in the cover, 0.4 bed chamfer |
| Light tube | - | 0.8 mm walls from the cover down to 0.33 mm above the LED, so light does not fill the case; notched where the camera flex meets its connector |
| Beam | - | hard cut-off about 42 deg half-angle; centre-weighted (full LED visible only within about 5 deg, about 40% at the edge of the camera picture, which is about 32 deg) |
| Dupont plugs | 16 loose single plugs | 2 printed plug clips (same part, print 2): each holds a row of 8 plugs as one block, with a rear comb (1.74 mm lane per wire, open on the outer side and the back) |
| Plug backstop | 3 mm open space behind the plugs | 5 floor pads 0.4 mm behind the clips (clear of the carrier screws, M3 driver holes and display screws) |
| Mass | tray 10872, cover 4511 mm3 | tray 10906, cover 4505 mm3; clip 469 mm3 each (about 1.2 g for both) |

Outside shape, inserts, snap bumps, wire channels, skirts and SD slot are the same as v3.

## Assembly (plugs)

1. Push the 8 plugs of a row onto the header pins as now.
2. Hold the clip behind the plugs, comb toward the plugs, and drop each wire sideways into its lane (lanes open
   toward the nearest long wall).
3. Slide the clip forward over the plugs until the comb touches the plug ends.
4. Bend each wire out toward the wall and lay it into the side channel as in v2/v3.
5. Push the board into the tray past the snap bumps. The floor pads now sit 0.4 mm behind the clips; with the cover
   on, the plugs cannot back off the pins.

Clip prints comb face down (pockets open upward), 4.1 x 22.0 x 13.0 mm. Rows with fewer than 8 wires are fine.

## Checks (all pass)

- `validation.json`: all v3 checks, plus
  - LED: top fully visible through the window with the board shifted 0.4 mm any way; tube 0.33 mm or more from the
    board; beam (42 deg) clear of the case, cover screws, carrier, ToF frame and display frame.
  - Clips: no contact with the board, plugs, modelled wires, tray or cover with 0.4 mm board play; slide-in path
    clear; 0.4 mm to the pads; pads clear of plugs and wire paths; carrier/display driver access unchanged.
- `check_in_head_v2.json`: v4 in the current balanced head: no contact at home or over tilt -38..34 / pan -20..180;
  first contact at 36 deg camera-down, the same as v2 and v3.

## Not verified

- The LED is identified from the board STEP (5.06 x 5.4 x 1.64 part at the far corner). Check it on the real board:
  it should sit in the window in `front_led_window.png`.
- The LED cannot be turned on yet: the camera firmware holds GPIO4 low. It needs a firmware change (PWM on GPIO4 with
  a brightness cap; the bare LED gets hot at full power).
- Plug stack height (header plastic 2.66 + plug 14.0) is the v2 assumption. If the real plugs sit higher, the clip
  touches the pads before the board seats: file the pads. If lower, the gap is bigger than 0.4.
- Wire lanes assume wire up to about 1.6 mm outside diameter. Thicker silicone wire may need the teeth trimmed.
- Clip pockets are 2.66 wide for 2.54 plugs; FDM usually prints them about 0.1 under, so the fit should be snug.
- Insert stock size and snap-bump grip, as for v3.
- The v2 mast print set (v2_tail.py) still points at the v2 STLs.

## Files

- `Gladiator_Camera_Service_v4_REVIEW.FCStd` (groups: PrintedParts incl. Plug_Clip_A/B, BoardAndWiring incl.
  Flash_LED_GPIO4 and a hidden LED_beam_42deg, Fasteners, HeadContext, Sections incl. LED and plug-row cuts).
- `Gladiator_Camera_Service_v4_EXPLODED.FCStd`, `Gladiator_Camera_Service_v4.step` (tray + cover),
  `Gladiator_Camera_Service_v4_with_clips.step`.
- `stl/Camera_Service_v4_Tray.stl`, `stl/Camera_Service_v4_Lid.stl`, `stl/Camera_Service_v4_Plug_Clip_print2.stl`.
- `review_sheet.png`, `front_led_window.png`, `cover_inside.png`, `plugs_rear.png`, `open_tray_clips.png`,
  `open_tray.png`, `section_plugs.png`, `section_led.png`, `assembled.png`, `exploded.png`.

Rebuild on cad-lab from the repo root:

    xvfb-run -a freecad cad/head/camera-service-v4-20261031/build_camera_service_v4.py
    python3 cad/head/camera-service-v4-20261031/check_in_head_v2.py
    python3 cad/head/camera-service-v4-20261031/review_sheet.py
