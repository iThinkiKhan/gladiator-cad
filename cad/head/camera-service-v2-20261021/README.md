# Gladiator camera service case v2 — review draft, 2026-10-21

This is a new serviceability revision of the installed ESP32-CAM case. The earlier generator calls its design "case v4"; "service v2" is the redesign requested in the October 21 chat. It does not replace any existing source, head assembly, or print plate.

## What changes

- Two diagonal M3 cover screws engage side-loaded metal nuts instead of four M2 screws engaging plastic.
- Both side wire channels open all the way to the front cover seam. Plug the Duponts onto the board outside the tray, lower the wired board onto its pads, and lay each row's wires into its side channel.
- Deep cover skirts close the channels, leaving a 4.5 mm high wire opening at the backplate. End clearance around each skirt is 0.3 mm. These are fit allowances pending a physical print.
- Two 3.6 x 2.4 mm tie passages run through the rear portions of the cover lugs for bundle strain relief.
- Carrier screw holes, lens aperture and microSD access follow the original case. The cradle and camera move 1.5 mm toward head-local +X to give 2.275 mm between the case and ToF frame.
- Wire-contact edges have 0.6 mm floor chamfers and 0.4 mm skirt chamfers. Local screwdriver reliefs preserve access to the carrier fasteners after the sideways shift.

## Files to review

- Gladiator_Camera_Service_v2_REVIEW.FCStd: assembled native CAD with head context, named parts, fasteners, and optional connector/wire references.
- Gladiator_Camera_Service_v2_EXPLODED.FCStd: cover moved forward 40 mm, head context hidden.
- Gladiator_Camera_Service_v2.step: two printed parts in their assembled robot pose.
- stl/: individual print-oriented meshes. These are review exports, not an accepted print release.
- validation.json: geometric and assembly checks.
- source-v4.py: preserved upstream generator including board measurements and the supplied board STEP mapping.
- build_camera_service_v2.py and generated-build.py: reproducible construction and validation.

The native view faces the camera toward robot +Y using the current head-master pan180 viewing pose. Measurements and checks are calculated in the original head construction frame, then transformed for viewing. No travel range is changed.

## Hardware and assembly

Keep the original three M2x6 carrier screws. Cover hardware is provisionally two M3x12 screws and two standard M3 nuts. The 6.0 mm across-flats nut pocket and 3.6 mm M3 clearance follow this printer's recorded fit results; 2.8 mm nut-pocket depth is an allowance. Screw-head reference is diameter 6 x 3 mm. Confirm stock screw and nut dimensions before printing.

The ToF-side wires leave into the new gap beside the case; the reference wires stop just outside that opening. Their complete route to the carrier cable slot and the fixed mast is not modeled. Route both bundles clear of the ToF frame and retain a service loop.

1. Fit the two nuts from the outer top/bottom ends of the diagonal lugs.
2. Install the tray on the existing carrier and install the display using the inherited access holes.
3. With power off, plug the camera's Duponts on while the board is accessible outside the tray.
4. Lower the board onto the existing corner pads, putting the two wire rows into their open side channels.
5. Route the wires toward the rear 4.5 mm openings, close the cover skirts into the channels, and fit the two M3 screws.
6. Tie the sleeved wire bundles at the lug passages without crushing individual conductors. Leave a movement loop between moving and fixed head structures.

## Limits of the CAD checks

Board height measurements are Jim's October 13 caliper values, inherited from the original generator: PCB 0.8; SD holder top 4.4; camera flange top 6.75; lens tip 9.4; lens diameter 7; module plus PCB 6.2 mm. Board footprint and component placement otherwise follow the original assumptions and supplied STEP.

Dupont housings remain assumed 2.6 x 2.6 x 14 mm; wire probes are 1.4 mm thick. The original 3 mm connector-to-floor space is retained. The new case removes threading but does not establish the real wire bend radius or improve that 3 mm allowance. Inspect the actual harness in the native model and trial fit before printing a final version.

The lid still provides final PCB retention through four corner posts with the inherited 0.3 mm gap. Support the board when servicing the open case.

Motion checks are sampled rigid-body checks, not continuous guarantees or cable-flex validation. The validated legacy pan interval is -20..180 degrees (current robot-front-relative -200..0); tilt checks cover -25..25. Check actual fitted harness movement separately. No servo, printer, wiring, firmware, or existing CAD is changed by this review.

## Rebuild and verify on cad-lab

Run from /home/buralien/projects/gladiator-cad:

    xvfb-run -a freecad cad/head/camera-service-v2-20261021/build_camera_service_v2.py
    xvfb-run -a freecad cad/head/camera-service-v2-20261021/run_verify_gui.py

The saved-file verifier uses FreeCAD's GUI runtime to restore the PartDesign feature objects. The provided STEP contains just the two printed parts. Both native review files also contain optional component references.

