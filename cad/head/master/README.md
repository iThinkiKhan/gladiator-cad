# Gladiator head master

**Current robot frame, 2026-10-09: mast is FRONT (+Y), +X right, +Z up.**
See ../../../docs/ORIENTATION.md. This native viewing file now shows the ToF/radar
face toward +Y at legacy pan180/tilt0. The fixed keyed neck stays put; moving
parts use the existing checked pose. Released print geometry/plates unchanged.
The old -20..180 pan range is -200..0 relative to new forward: forward is an
endpoint, **not a centered home**. No servo motion or new travel limits implied.
`orientation.json` records the frame/pose; robot-front preview looks from +Y.

`Gladiator_Head_Master.FCStd` is the mast head on its own, for looking at in FreeCAD.
It is a viewing file: every solid is a copy of the matching solid in the current head
prototype (`../v05-sensor-mounts/`), posed mast-front in real robot coordinates, so it lines up with
`../../master/Gladiator_Master.FCStd`. Nothing here is modelled by hand and nothing in the
chassis master or the v05 files was touched.

Do not edit it by hand. Change the head generators (`scripts/build_head_v04.py`,
`scripts/build_head_v05.py`) and re-run:

    cd ~/projects/gladiator-cad
    xvfb-run -a freecad scripts/build_head_master.py

The script copies the 26 head solids plus the mast tube, saves the FCStd with colours,
writes the STEP and four preview PNGs, and checks every copied volume against the source.
`build-check.json` has the per-part result.

## Tree

| Group | What | Colour |
|---|---|---|
| FixedNeck | Neck_Main, clamp cap, pan servo carriage (printed) | grey |
| Pan | rotor, retainer, raised pedestal, drive pulley (printed) | orange |
| Tilt | yoke, GH44 receiver, dual carrier, ToF frame, radar frame, display frame (printed) | green |
| Hardware | bearings, spacer, circlip, both SG90s and horns, belt, pivot bolt, ST7789 | see-through |
| Hardware, keep-out volumes | Dual_ToF_Envelope (blue), Dual_Radar_Envelope (red) | see-through |
| Mast_Context | the mast tube, Z 6 to 130, so the head sits on something | faint |

Tip: tick or untick a whole group in the tree to hide it. Hide Hardware to see only the
printed parts.

## Status of what it shows

Prototype v05: v04 mechanics (60T on the servo, 40T on the head, sliding servo carriage,
horn plate, tilt yoke, through-cut GH44 receiver) plus measured sensor mounts for the
42 x 27.5 ToF board and the 22 x 30 radar. Checked in CAD only (about 145,800 pose
comparisons, no collisions). Not assembled or printed as a whole: harness, strain relief,
mechanical stops, belt fit and horn screw fit are open. See `../v05-sensor-mounts/README.md`.
