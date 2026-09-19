# Gladiator v0.2: rear screen and 180-degree pan

Separate CAD comparison candidate, 2026-09-17. **The original v0.1 file and the saved robot master are unchanged.** This is a geometry review, not a print-ready mechanism.

## Open and compare

- `Gladiator_Head_v02_Screen180.FCStd`: second native FreeCAD file, including the robot context and both head poses. Opens with sensors forward.
- `reference/Gladiator_Head_v01.FCStd`: unchanged copy of the exact first CAD candidate used as the starting point. The pre-existing local v0.1 copy is also left untouched.
- `head-v01-v02-comparison.png`: original, new sensors-forward pose, and new screen-forward pose rendered at the same scale and camera angle from actual CAD solids.
- `Gladiator_Head_v02_Screen180.step`: head-only export with sensors forward.
- `Gladiator_Head_v02_Screen180_Presented.step`: head-only export after the 180-degree turn. Reference hardware and the screen board envelope are included, as in the first candidate.

In FreeCAD, switch poses by hiding **POSE 1 - sensors forward (0 deg)** and showing **POSE 2 - screen forward (180 deg)** in the tree. Select a group and press Space to toggle visibility. Show only one pose at a time; the two groups represent the same physical assembly. The robot context stays visible. Existing unused carrier variants remain hidden in their original groups.

## Kept from the first design

The fixed mast and mast interface, split collar geometry, bearing seats and retainer screw pattern, GH44 mating interface, sensor envelopes, and original tilt assembly geometry are retained. The four new display-frame holes in the dual carrier do not alter its GH44 mating features. Unchanged source parts are reused directly from the v0.1 document, rather than redrawn from estimated dimensions.

## Changes for comparison

| Item | Second candidate |
| --- | --- |
| Screen | Jim's confirmed whole ST7789 board: 62 x 29 x 3.2 mm, landscape |
| Rear frame | 76 x 44 mm outside; removable frame with four side rails |
| Frame attachment | Four proposed M2 clearance holes, diameter 2.4 mm, at X +/-32 and Z +/-18 relative to the carrier center |
| Board opening | Provisional 62.6 x 29.6 mm whole-board clearance; not a measured active-screen bezel cutout |
| Tilt position | Original assembly raised 28 mm; tilt axis now Z=205 in the original model coordinates |
| Pan drive | Replaces the parallelogram with equal timing-pulley and belt envelopes; retains the original SG90 platform and shaft spacing |
| Pan operation | Sensors forward at 0 degrees, screen forward at 180 degrees, return by reversing |
| Stops | Revised fixed posts and rotor lug; nominal contact about -5.44 and 185.44 degrees |

The extra height clears the fixed servo, horn and drive while retaining most of the original tilt geometry. The original +/-40-degree scan about sensor-forward is **not** retained by this 0..180-degree operating proposal. It would require additional actuator travel or a different ratio.

The pulley concept uses a specified 2 mm pitch and 50 teeth on each pulley, 42 mm between shafts, giving a theoretical pitch-loop length of 184 mm. These are design inputs, not identified commercial parts. Pulleys show pitch cylinders and flange envelopes, not printable tooth geometry. A 1:1 ratio requires an actuator with verified usable 180-degree travel; Jim's SG90 range and loaded performance have not yet been established. Hub, horn attachment, belt tensioning and final hardware selection remain open.

The dark rectangle is the measured **whole board**, not a claim about active-screen size, pixels or mounting holes. Board retention, the active window position, connectors and cable clearance need the actual module details before manufacturing. The thin frame rails and extra height also need payload/deflection evaluation; no load rating is claimed.

## Checks completed

`validation.json` records 23 active single valid solids, 5,265 head part/pose comparisons and 10,488 head-to-robot comparisons. Pan was sampled every 10 degrees from 0 through 180, with tilt at -25, 0 and +25 degrees where relevant. No sampled rigid-solid collisions were found. A separate sampled belt-to-nonpulley check also found no intersections.

The nominal forward ToF field was checked at the travel pose for three tilt angles, with no modeled intersections. The 11.9 mm test cylinder through the nominal 12 mm mast/neck passage remains clear. The stops clear 0 and 180 degrees and intersect the lug in the intended overtravel samples at -6 and 186 degrees. The saved native file was reopened, both pose volumes checked, and group visibility toggles verified. Both STEP exports were read back, checked for valid geometry and 23 solids, and their total volumes compared within a 0.001% numerical tolerance. Original source and master SHA-256 hashes are preserved in the report.

These checks do not prove clearance between samples, actual sensor fields, wiring flexibility, servo travel, torque, print fit or strength. Presentation is a parked mode: the proposed firmware should stop before turning and restore fresh forward sensor readings before movement resumes. Firmware was not changed.

## Rebuild

The native candidate also exists on the CAD server under `/home/buralien/projects/gladiator-cad/cad/head/v02-screen-180/`. Source scripts are copied in `generator/`. Run the builder, then the styling/verifier, using the CAD server's system Python and FreeCAD modules. Run the styling script in a private `xvfb-run -a` display. The generator writes only the second candidate directory; it opens the first file as input and never saves over it. The local preview renderer uses Python, NumPy, Pillow and the Windows Segoe UI fonts.

No STL manufacturing release is supplied for this candidate.
