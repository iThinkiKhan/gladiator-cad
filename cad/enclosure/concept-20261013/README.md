# Gladiator enclosure concept - 2026-10-13

Review model, not a print release. Source CAD is on cad-lab. Existing robot geometry was read only; the new shell lives in its own directory.

## Design

Three angular body panels conceal the inter-deck wiring and upper electronics. A rear hood ends at Y85.7; front-left and front-right panels start at Y86.3 and separate about X39.5. The front panels surround the mast through a 26 mm opening. Proposed rear exterior antenna location lets the original antenna pylon be removed. Current mast-front frame: +Y front, +X right, +Z up; aluminum deck X0..79, Y0..140.

The split is intended to permit service without removing the head. Panel removal trajectories have not yet been validated. Mounting tabs, registers, fasteners and wire retainers are not modeled.

| Proposed shell dimension | Value (mm) |
| --- | ---: |
| Main electronics body width | 97 |
| Widest front shoulders | 153 |
| Total length | 180 (Y -32..148) |
| Bottom / roof elevation | Z14 / Z108 |
| Body height | 94 |
| Nominal wall inset | 2.4 |
| Panel seam | 0.6 |
| Heatsink aperture offset | 4 |
| PCB aperture offset | 2 |

These are design choices, not measurements. The loft produces varying thickness at sloped transitions; 2.4 is not a guarantee of uniform normal wall thickness. The design reaches outside the aluminum deck only above the approximate track tops. Track width179 and track top near Z7 come from project measurements; no accurate moving track model exists here.

The rear extension covers the separate INA226 cassette, whose pins reach Y-21. The inner rear wall at Y-29.6 leaves 8.6 mm past those modeled pins. That is a packaging budget, not verified connector bend clearance. Roof underside is Z105.6, compared with the S3 reference top Z92.8; the 12.8 mm budget excludes unmodeled wiring. The assembled photo contains taller wire loops, so this concept assumes a tidier harness or later roof changes.

## Sources and validation

- Current chassis native master: source geometry copied from saved shapes. Structural body BREP shapes are read directly from the native archive when the runtime omits PartDesign objects; source models are never recomputed or saved.
- Current v05 head viewing master, already oriented mast-front. Historical embedded v01 head excluded.
- Current master v5 driver bodies and envelopes, including the 6.5 mm rail/deck height change. The standalone driver file is older in Z and was not substituted.
- Separate power tray v5, INA cassette v2 and switch holder v1b included.
- Old antenna pylon and legacy power shield excluded as replaced components.
- All three panels are single valid solids. Static intersection checks against the copied structure, electronics reference solids, tray, cassette, switch and current head pose find no volume overlap above 0.01 mm3. The exclusion openings intentionally clear the driver board edges as well as heatsinks.
- Native and shell STEP reopen checks, source hashes and limitations are in validation.json.
- Tracks, wheels and exterior antenna are simplified illustrative geometry. Heatsinks are the source CAD's solid envelopes, not individual fins. Colors are presentation choices.

## Before fabrication

1. Confirm the angular shape and the actual wire routing. Measure the tallest retained connector/wire loop relative to the upper deck top (Z58.5). Current roof underside is47.1 mm above that surface.
2. Design removable panel attachments to printed structure or reusable deck fasteners. Keep the existing aluminum unchanged. Captive screws are the preferred next design direction; screw access and battery service sequence need checking.
3. Sweep panel removal and head motion; check moving-track clearance against the physical machine. The roof is6 mm below the lowest current fixed-neck reference, but that alone is not a motion-sweep test.
4. Check SMA thread/panel thickness and pigtail reach. Current rear wall is2.4 mm with a trial7 mm cutout. The project documentation quotes about2.2 mm maximum connector panel thickness, so a local thin mounting land or separate insert must be designed before printing. The antenna shown is only a placement proposal; its actual size and RF performance are not validated.
5. Finalize ventilation and wire strain relief; check temperature in the closed body. Preserve current PLA calibration unless the user chooses a material change.
6. Add panel location lips and fasteners, check printable orientation/supports, then export manufacturing meshes. No STLs, sliced plates or print jobs were issued from this concept.

## Files

- Gladiator_Enclosure_Concept.FCStd - editable native review assembly.
- Gladiator_Enclosure_Shell_CONCEPT.step - three shell sections only.
- Gladiator_Enclosure_Assembly_CONCEPT.step - shell and source references; illustrative tracks and antenna excluded.
- body.png - head hidden to show the shell.
- assembled.png - shell with current head pose.
- clearance.png - transparent panels showing packaging.
- build_concept.py - reproducible FreeCAD GUI construction script; run with xvfb-run -a freecad on cad-lab. Uses absolute repository paths.
- validation.json - checks and source provenance.
