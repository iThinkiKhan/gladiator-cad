# Gladiator modular mast/head — preliminary direction

Reviewed 2026-09-16. Concept review only; no production geometry or interface dimensions are frozen.

**Update:** a generated v0.1 CAD candidate and proposed GH44 carrier interface now exist in `cad/head/v01/` on the CAD server. See that folder's README and validation.json for the actual implemented geometry, fit prototypes and remaining manufacturing details. The earlier direction below is design context, not a manufacturing specification.

## Evidence and review limits

- Inspected the live, already modified `Gladiator_Master` document in FreeCAD 1.0.0 on the remote CAD workstation. Its tree contains Parameters, Chassis deck, battery references, Side rail right, Mast base, Mast tube, Upper deck, S3 + expander reference, Breadboard + C6 + BNO reference, Power board shield, Antenna post, and Driver mount right.
- Subsequently completed a separate headless inspection over SSH of `/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd`, plus the CAD repository's measurement files and upper-structure design log. Repository was clean at inspection, HEAD `cdf813c` (open driver frames). The saved master is the numerical audit source; the live GUI had an unsaved-change marker and could differ. Never saved or modified the live document or saved master.
- Read the live parameter sheet: deck length 140 mm, width 79 mm, thickness 2 mm; center-hole diameter 14 mm, center X 39.5 mm, center Y 113 mm. These are CAD values, not new caliper measurements. The center-hole diameter must not be mistaken for the mast bore.
- Jim is using the local PC; continue CAD access through SSH as `buralien@192.168.0.21`, without taking over the desktop.
- Local project is the PlatformIO firmware workspace; `git status` reports that it is not a Git repository. No native CAD source was found in this workspace or local Documents/Desktop searches.
- Jim explicitly rejected all previous fit-kit dimensions except the smallest servo gauge, which fitted perfectly. Its source specifies a **22.8 × 12.0 mm rectangular opening through a 4 mm plate**. Preserve that tested opening for the current SG90 body, not an inferred complete servo model. Do not reuse old tower collars or other coupon dimensions. Jim has SG90 servos with standard gears and predominantly M2/M3 screws, nuts and bolts.
- Firmware review: ESP32-S3 owns motors/safety/sensors; XIAO ESP32-C6 is the communications coprocessor. Two BTS7960 drivers drive the tracks. INA226 and BNO085 share I2C with planned head sensors. GPIO8/9 run I2C at 400 kHz; GPIO4/5 serve the C6 UART, and GPIO19/20 are native USB. No servo pin allocation is present in BoardConfig.h. The ToF has been bench tested; the radar still needs its physical bench test according to the repo.

## Existing CAD — verified dimensions and implications

Coordinates use front-left origin; X right, Y rearward, Z upward. Front-facing sensors look toward negative Y.

| Item | Saved model | Consequence |
| --- | --- | --- |
| Mast | 20 OD / 12 ID; Z 6–120; center (39.5,113) | 4 mm nominal wall, 114 mm tube, 68 mm above deck top. SG90 cannot fit inside the bore. Top height is documented as a placeholder. |
| Lower socket | 20.4 ID, 26 OD; collar to Z 20 | 0.2 mm nominal radial clearance; removable tube retained by transverse M3/3.4 mm hole at Z 13. |
| Base | 13.8 spigot in existing 14 mm aluminum opening; bottom Z -5 | Only 1 mm documented margin above motor. No new lower protrusions or aluminum machining. Two existing M2 pilots at (19,111)/(60,111) resist rotation and share fastening with power shield. |
| Upper deck | 79 × 140; main slab Z 48–52 | Loaded tray lifts off for battery service. |
| Deck mast support | 20.4 bore, 28 OD; Z 38–52 | 14 mm bearing length. Socket/deck support centers about 32 mm apart. A head wider than the bore must detach before the deck slides up over the mast, or mast must be removed first. |
| Intended wire entry | Rear 10 × 12 window at Z 24–36 | Entry should connect below deck into 12 mm bore; actual pocket defect described below. Base beneath bore is solid, and retention pin crosses lower bore: route through side entry above pin. |
| S3/expander envelope | X 1–43, Y 15–89, Z 58–86.3 | Governs forward/downward ToF sightlines and wiring clearance. |
| Breadboard/C6/BNO envelope | X 43.5–79, Y 15–61.3, Z 52–73.5 | Almost no lateral spare deck width; keep neck packaging at mast top. |
| Driver supports | Y 90–139.5, up to Z 94 | Rear-side moving-envelope obstacles. Installed boards/heatsinks/cables are not fully represented by these support solids. |
| Antenna post | X 65–75, Y 3–13, Z 52–78 | Actual whip/pigtail envelope still needed. |

All 13 audited top-level solid objects have valid saved shapes. Seven targeted existing mast/neighbor solid-intersection checks report zero volume; this is not a complete robot collision or strength certification. Evidence: `mast-head/cad-audit-20260916.txt` in the firmware workspace.

**Confirmed wire-window defect:** `MastWindowCut` has Reversed=False, Length=20 and points toward +Y from Y=126, away from the tube (rear outer surface Y=123). Its volume is exactly unchanged from `MastTubePad` (22921.060 mm³). Solid probes across the rear wall at Z 25,30,35 remain occupied. An isolated in-memory trial of Reversed=True and Length=12 opens the rear wall into the bore, preserves the front wall, and leaves one valid solid. Final tube volume in that trial is 22324.660 mm³. No correction has been saved into the master. Apply this before producing a mast intended to route wires; recheck the complete entry width and real plugged harness in the eventual fit model.

**Sightline implication:** a ToF optical origin at the mast center Y=113 needs about Z=143 or higher for its nominal lower 30° ray to clear the S3 envelope's front/top corner (Y=15,Z=86.3), before adding margin. This is an inferred center-section envelope calculation, not a full FOV test. A forward offset reduces required height. Downward tilt increases deck intrusion substantially. Keep the head compact but do not arbitrarily shorten the mast or bury the optical face at its top plane.

## Recommended architecture

Fixed chassis and mast → removable neck/motion unit → standardized moving mounting face → interchangeable sensor carrier.

Use two deliberately separate interfaces:

1. **Mast-to-neck structural interface.** A removable external split collar around the existing 20 mm mast, seated on its top rim while preserving the 12 mm cable opening. Add a defined anti-rotation index to the final common mast interface, such as a shallow external key/flat; do not rely solely on friction for repeated alignment. Accessible M3 nuts/bolts retain the neck. Confirm overlap length and local mast strength before dimensioning the collar. Avoid a transverse screw across the upper cable bore. Detach the neck and its connector to retain upper-deck service access. The motion unit can then be replaced or upgraded independently of the mast.
2. **Motion-unit-to-carrier interface.** A common flat datum, shallow locating register with an asymmetric key, and a compact four-screw pattern around a cable opening. Use M3 screws and captured nuts in the reusable receiver as the initial direction, matching available hardware. Locating geometry carries lateral load; screws provide clamp load. Do not ask screw clearance holes to provide repeatable sensor orientation. Keep tool access available with sensors installed. Final footprint, hole spacing, engagement, and tolerances remain open; M2 sensor screws depend on actual sensor mounting holes.

Every new sensor carrier reproduces the same mating face. Its front, sensor standoffs, openings, and enclosure can differ. Publish the interface in a small drawing and reusable FreeCAD template once fit is validated. Define not only holes but also forward/up axes, origin, screw lengths, cable connector access, allowed swept envelope, payload mass, center-of-mass limits, and electrical expectations. This is a bounded module family, not unlimited compatibility with any future payload.

First carriers: SEN0628-only, SEN0610-only, and a combined carrier using replaceable individual sensor inserts. Include a blank carrier template. A fixed neck adapter should accept the same carrier interface for early tests and for sensors better kept stationary.

## Motion and packaging

- Provisionally use limited-angle pan and tilt. Do not select continuous rotation with a wire bundle through the mast.
- Keep the pan actuator fixed in the removable neck above/around the mast; support the rotating stage with a separate radial/thrust load path sized to the payload. Avoid supporting the entire head as a long cantilever on the servo output shaft.
- Use a short tilt cradle with support on both sides. One side can drive through the horn; the other uses an idler pivot. Put the combined head center of mass close to the tilt axis. Tilt actuator moves with pan, but the mast remains stationary.
- Treat the existing SG90s as a lightweight prototype motion unit, not a guarantee that every future combination can be carried. Use their supplied horns rather than printing servo splines. TowerPro's analog SG90 rating is a stall specification, not a continuous payload allowance, and actual supplied units must be characterized. Account for gravity, acceleration, cable torque, friction and vibration before defining payload limits. The common mast/carrier interfaces should survive a future stronger neck.
- A hollow pan pivot or offset servo drive can preserve the central cable path; actual bore and servo packaging determine which is worthwhile. Do not shrink the wire path merely to force a servo inside the existing mast.
- Reserve a protected flex loop for each axis, strain relief on both fixed and moving ends, rounded cable exits, and a service opening. The harness must accommodate travel without winding tight, rubbing gear teeth, or pulling connectors. Hardware stops protect the harness; software limits stop short of them. Initial travel targets should be chosen only after a swept-envelope check with plugged-in cables.
- Separate regulated servo power from sensor supply distribution; share the required signal reference. Size regulator and wiring from selected servo stall current. Do not put raw battery voltage or servo loads on the sensor power connector.
- Keep the body IMU fixed to the chassis. A moving ToF is no longer simply `tofFront`: later firmware must attach head pose/settling state and carrier orientation to samples. Commanded servo angle is not measured pose. Radar behavior during head/robot motion must be tested; initially characterize presence while stationary and settled.

## Sensor faces and wiring

DFRobot documents the SEN0628 with a 60° horizontal × 60° vertical ranging angle, I2C/UART/USB, PH2.0-4P interface, and 3.3–5 V supply. Keep both optical paths exposed and avoid a recessed tunnel. For initial clearance layout, expand the opening outward from the optical envelope by at least d × tan(30°) per side for recess depth d, plus manufacturing/alignment margin; this is a layout estimate, not optical validation. Provide USB/service access. Do not assume a generic clear cover is optically acceptable.

DFRobot documents SEN0610 as a 22 × 30 mm, 24 GHz radar board with a 100 × 80° beam and 3.3/5 V supply. Keep metal hardware, other boards, servo bodies, and cable bundles out of its forward sensing region. An eventual PETG cover needs comparison testing with the actual filament, thickness, and spacing; do not assume arbitrary plastic is RF-transparent. Verify which board axes correspond to the two beam angles.

Use an accessible polarized sensor connector and short carrier pigtail initially. Specify pin order explicitly; connectors that fit are not necessarily electrically compatible. Preserve 3.3 V I2C logic at the controller. Reserve physical space for a separate future camera/data cable rather than promising camera support over four-wire I2C. Swap modules with power off. Check bus rise time/errors with the actual mast harness and servo motion because it shares the installed power monitor and IMU bus.

## PETG design approach

Use short load paths, filleted transitions, ribbed cradle arms, generous fastener bearing surfaces, and metal hardware at repeatedly serviced joints. Avoid thin snap tabs, sharp arm roots, printed precision bearings, and prolonged high clamp stress in unsupported plastic. Arrange part splits so major bending loads are carried along printed layers where practical. Make new hardware fit coupons for the actual PETG process; the only accepted old gauge result is the smallest servo opening. A small receiver/carrier fit coupon should precede the full head print.

## Hardware update from Jim, 2026-09-16

User-supplied published dimensions below are layout inputs, not independently verified hole coordinates or full plugged-in envelopes. Check original drawings before committing sensor-specific geometry.

| Device | Supplied nominal size | Provisional clearance envelope | Open details |
| --- | --- | --- | --- |
| SEN0628 | 27.5 × 27.5; maximum stack 11.5 | 29 × 29 × 13 | Ø3.1 holes; drawing references 22/15/5.5 and R3.5 must be mapped to actual drawing, not interpreted as a guessed hole pattern. Plug/access clearance separate. |
| SEN0610 | 22 × 30 | 24 × 32 in XY | Physical height/front-back protrusions, hole coordinates, and plugged connector envelope unknown. |
| AI-Thinker ESP32-CAM | 27 × 40.5 × 4.5 ±0.2, excluding protrusions | 28.5 × 42 × approximately 15 | Future carrier envelope; actual lens/header heights and installed camera orientation must be checked. Supplied DIP pitch 2.54 and approximately 22.86 row-reference span are not a mounting-hole pattern. |

SG90 caliper measurements: ears 2.5 thick, ear holes Ø2.5, overall ear-tip span 32.5, tab length 5; long horn approximately 36 end-to-end, shorter/wider part approximately 18 end-to-end. Jim reports horn extends at most 5 beyond the tab. That overhang is orientation-specific, not sufficient to define its entire rotation envelope; do not infer symmetric 18 mm radius without checking shaft location. Preserve tested body opening 22.8 × 12.0.

The mast harness has not been designed. Design the harness alongside the neck, preserving the mast's 12 mm bore and using accessible disconnects. Do not request dimensions for nonexistent harness parts. Carrier envelopes permit a concept layout now; precise horn/ear geometry gates a detailed servo cradle.

Latest SG90 measurements: hole centers about **27.2**, distinct from **32.5** ear-tip span; body bottom to ear underside **17**; ear underside to installed horn underside about **13.2**. Shaft-to-short-body-side is **8.3**. Jim clarified the other **17** is **shaft center to a long horn tip**, not a body-side offset. Cross-width shaft position remains unmeasured; check other horn tips against approximately 36 overall length before final swept clearance. Full measurement record is `docs/mast-head/hardware-dimensions.md` locally and `measurements/mast-head.md` on the CAD server. Horn attachment pattern remains needed for the final coupling.

SEN0610 front/rear component heights and plugged lead space are needed before a close-fitting carrier/cover, but do not block the initial system envelope. SEN0628 hole coordinates should first be resolved from its original drawing rather than asking Jim to remeasure published geometry.

## Exact measurements needed

Record mm and identify the measurement orientation. No need to measure everything before the CAD audit is resumed.

### First: hardware and existing assembly

- SG90 body cross-section is already fit-tested at a 22.8 × 12.0 opening; no need to repeat that coupon. Still measure body bottom-to-ear seating plane, mounting-ear overall span/thickness, ear hole-center spacing and diameter, shaft center from one body end and side, and ear seating plane-to-horn underside with the horn installed. Measure usable horn radius and screw-hole spacing, and note lead exit. Confirm how many servos are available. Do not assume a 4 mm-deep gauge fit proves an entire pocket's taper/cable clearance.
- Available M2/M3 screw lengths, nut across-flats/thickness, and any bearings. CAD history documents 5.0 OD × 7.05 long M3 inserts; confirm they remain available only if we choose to use them. Initial neck/carrier uses captured nuts.
- Current printed mast: OD in two directions near its top, minimum clear ID, top-to-upper-deck distance, and any existing top holes/key/slot. These validate CAD-to-print fit, especially if parts have already been printed.
- Largest connector that must pass through the mast: width × thickness × length; actual bundle width/thickness with intended cables. Include camera cable only if already selected. Note any plug that can be installed after threading.

### Each sensor, facing its sensing face

Use PCB left and bottom edges as X/Y datums with the connector orientation noted. Record PCB width/height/thickness, maximum component projection front and rear, number and diameter of mounting holes, and each hole center's X/Y from the datums. For equal holes, center spacing can be measured as outside-to-outside minus one hole diameter; do not try to grip imaginary centers with calipers.

Record sensing-window/antenna position and extent, connector housing projection beyond the PCB, and the plugged cable's natural exit envelope without forcing a tight bend. For SEN0628, include USB plug access and optical window height above the PCB. For SEN0610, identify the antenna face and switch access. A kitchen-scale mass reading is helpful if available; do not estimate servo size from board dimensions alone.

## Next design gate

Numeric saved-CAD audit is complete and prior kit exclusion is resolved. Next obtain the missing sensor/servo dimensions, correct the mast window in an isolated candidate, then make an assembly envelope with fixed mast, moving neck, cable loops, carrier, and sensor visibility volumes. Compare single/combined carriers at all motion extremes with upper deck, antenna, electronics, and tool access. Only then freeze interface dimensions, choose bearings/servo transmission, and produce detailed printable geometry.

Validate with: interface coupon; unpowered fit/service and full-travel cable checks; then supported/secured powered motion and simultaneous sensor communications; finally controlled vibration/drive trials and repeatable removal/reinstallation checks. Check fastener loosening, PETG creep, sensor clipping, radar self-motion behavior, and brownouts.

## Sources

- Live FreeCAD assembly and parameter sheet, inspected 2026-09-16 (limited inspection described above).
- Local README.md, docs/SENSOR_CORE.md, src/BoardConfig.h, src/sensors/SensorData.h, src/sensors/SensorManager.cpp.
- CAD repository measurements/chassis.md, measurements/components.md, docs/upper-structure.md and saved master at HEAD cdf813c. Its design log contains superseded stages; current solids and latest decisions govern.
- Historical `gladiator_batch1_v04_cadquery.py` in Downloads/gladiator_batch1_v04_bundle.zip: only the smallest servo aperture is accepted, per Jim's explicit confirmation.
- https://wiki.dfrobot.com/sen0628/ (manufacturer specifications accessed 2026-09-16).
- https://wiki.dfrobot.com/sen0610/ (manufacturer specifications accessed 2026-09-16).
- https://towerpro.com.tw/product/sg90-analog/ (manufacturer reference; do not assume it certifies Jim's particular servos).
