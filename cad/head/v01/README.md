# Gladiator modular head v0.1

**A CAD review candidate and reusable carrier interface, not a manufacturing release.**

The candidate keeps the fixed 20/12 mm mast and makes the neck, motion unit and sensor carrier separate serviceable assemblies. It includes a fixed adapter using the same carrier interface, so early sensor work does not depend on finished servo hardware. The saved master was not overwritten.

## Files and source of truth

On the CAD server, open `cad/head/v01/Gladiator_Head_v01.FCStd` inside `/home/buralien/projects/gladiator-cad`. The starting master is captured as `source-master.FCStd`; its SHA-256 and source Git commit are in `validation.json`. The candidate was refreshed against source commit `5489d23`, which tapers the upper deck and redistributes the S3/breadboard layout. The user's live document and the master file remain separate from this candidate.

- `Gladiator_Head_v01.FCStd`: robot plus new head; dual carrier visible by default after styling. Other carriers are separate, hidden alternatives.
- `Gladiator_Head_v01.step`: installed head and hardware/envelope references, without the robot. Reference blocks are included deliberately for layout review, not manufacturing.
- `GH44_Carrier_Template.FCStd` and `.step`: reusable common mating base.
- `head-config.json`: dimensional manifest. Only the sweep limits are accepted as independent overrides; other changes require paired geometry changes in the generator.
- `validation.json`: solid validity, sampled interference, nominal ToF field and wiring passage results.
- `fit-prototypes/GH44_Blank_Carrier.stl` and `GH44_Receiver_Fit_Coupon.stl`: first fit pieces, oriented with their primary mating geometry facing up.
- `fit-prototypes/GH44_Fixed_Head_Adapter.stl` and `Neck_Clamp_Cap.stl`: optional unpowered fit prototypes. Orient and support these deliberately in the slicer; automatic flat placement is not a validated print orientation.
- `scripts/build_modular_head.py`: generator in the CAD repository. Geometry is regenerated from source into individual named Part features. This is **not** an editable sketch/constraint history, and editing the dimensional manifest alone does not parameterize every solid.
- `scripts/style_head_candidate.py`: sets visibility, colors and the initial CAD view in an independent offscreen process. It does not touch the user's open FreeCAD document.

## GH44-v0.1 carrier interface

This is a proposed versioned interface. Freeze it only after the fit pair is printed and tested. New sensor modules reuse this geometry; they do not change the mast or copy the SG90 mounting pattern.

| Feature | Proposed dimension |
| --- | --- |
| Common mating plate | 44 × 44 mm |
| Carrier base thickness | 3 mm |
| Receiver face thickness | 4 mm |
| Screw pattern | Four holes on a 32 × 32 mm square |
| Screw clearance | Ø3.4 mm, M3 screws |
| Receiver nut pockets | 5.7 mm across flats, 2.7 mm modeled pocket depth; verify actual nuts and PETG fit |
| Locating register | 26 × 22 mm male, one 5 mm clipped corner |
| Male engagement | 1.4 mm |
| Female profile | 26.4 × 22.4 mm; one corresponding clipped corner |
| Female recess | 1.6 mm effective depth from face |
| Cable window | 18 × 10 mm through both halves and receiver backbone |

The clipped corner prevents a 180° rotated carrier from seating. The register locates the module and takes lateral load; screw preload retains it. Screw clearance holes are not alignment datums. The four screws remain accessible around the current sensor envelopes. Standard M3 washers/head styles and final screw length still require fit checks; do not substitute large heads blindly near the carrier edge.

**Coordinate convention:** robot X is right, Y rearward, Z up. A forward-facing module looks toward negative Y. In the reusable template the mating plane is Y=-52, the carrier datum center is (0,-52,177), and sensor geometry extends toward negative Y. The receiver is behind that plane. Hole offsets are X ±16 and Z ±16 relative to the datum. Preserve those features, the register and the cable window when creating another carrier.

The nominal interface geometry is deliberately the same on all carriers. To use a carrier on the fixed adapter in this assembly, translate the local carrier by (0,+26,-22) relative to its moving-head position. The fixed adapter replaces the entire motion neck and reuses the front clamp cap; it is not installed alongside the moving neck.

## Carriers in this candidate

| Carrier | Sensor-support plate | Current status |
| --- | --- | --- |
| Blank | 44 × 44 common base | Fit prototype and starting template |
| SEN0628 | 38 × 38 adjustment plate | 29 × 29 × 13 clearance block; actual PCB standoffs/retention not yet designed |
| SEN0610 | 34 × 40 adjustment plate | 24 × 32 × 13 clearance block; **13 mm depth is a placeholder** |
| ESP32-CAM | 38 × 50 adjustment plate, shifted up 6 mm | 28.5 × 42 × 15 clearance block; lens/header placement provisional |
| Combined | 70 × 42 adjustment plate | ToF center X=-17, radar center X=+17 relative to carrier datum |

These adjustment slots are generic M2 mounting provisions, **not claimed PCB hole coordinates**. Sensor-specific standoffs or edge clamps must keep solder joints, connectors, optics and antenna areas clear. The reference blocks are not detailed sensor CAD models. Larger future modules may overhang the 44 mm interface, but require a new swept-envelope and payload check.

## Neck and motion arrangement

- The neck seats on the existing mast top at Z=120 and clamps its outside. The 12 mm nominal cable bore remains open through the spindle. Two accessible M3 clamp bolts pass outside the bore.
- A shallow rear index flat is added to the candidate mast over Z=105..120, with the neck key leaving approximately 0.2 mm clearance at the flat. This is a proposed common mast-interface feature, independent of sensor choice.
- The saved mast's reversed wire-window defect is corrected in the candidate. The lower anchor, retaining pin and aluminum deck are retained.
- Two **20 × 32 × 7 mm bearings** support pan, with an inner spacer and a nominal 20 mm shaft circlip. The SG90 supplies torque through an offset parallelogram link instead of supporting the entire head on its output shaft.
- Pan servo offset is 42 mm rearward; both cranks are 12 mm radius, with a 42 mm link. Equal crank radii give a 1:1 parallelogram on the intended assembly branch. Operate around the perpendicular neutral position; do not cross a linkage dead center.
- The pan rotor has a rear stop lug and fixed stop posts beyond the proposed ±40° operating range. Exact contact angle and all stop hardware need a physical check.
- Tilt axis is 26 mm forward of the mast center at Z=177. The servo mounts internally, and the opposite side uses a 4 OD / 3 ID sleeve and an M3 pivot. Use a smooth bearing surface rather than running a threaded section in the sleeve.
- Proposed operating envelope is **pan ±40°, tilt ±25°**. These are CAD review limits, not installed firmware limits. Tilt stops and final horn coupling still require completion before powered operation.

## Hardware and unresolved manufacturing details

Confirmed inventory remains SG90 servos and M2/M3 hardware. **The bearings, circlip, spacer and tilt sleeve are new proposed hardware; no purchase was made.**

The servo mounts use Jim's 22.8 × 12.0 fit opening, 27.2 mm ear-hole spacing, 2.5 mm ear thickness, 17 mm base-to-ear height and 13.2 mm ear-to-horn height. Ear holes are Ø2.5 on the real servo; use M2 screws and appropriate washers rather than forcing M3 through them. Shaft cross-width centering is still assumed at 6 mm. Upper servo shape and horn thickness are approximate clearance models.

Pan horn adapter has radial adjustment slots. Tilt horn attachment currently has provisional holes. Neither is a claim that the exact supplied horn pattern is known. Keep the supplied servo horn and central spline connection; do not print replacement splines. Link joints need suitable smooth pivots, washers and retention. The bearing outer-retainer ring currently uses M2 pilot bores; the thread/insert method has not been released.

Bearing and circlip dimensions are based on manufacturer references, but printed PETG shaft strength, bearing fit, axial retention, wear and creep are untested. Metal-shaft circlip load ratings do not apply to this printed spindle. Do not assume both bearings can be rigidly preloaded by nominal printed dimensions; set spacer/shim fit from the real hardware without binding.

## Wiring and sensing

The neck and carrier retain open passages. A hidden neutral-route guide exits the mast toward the front/right, passes around the internal tilt servo and enters the carrier from behind. It is a route guide, **not** a designed flex harness: plug dimensions, strain relief, bend radius, slack at both motion limits and service disconnects remain to be selected. Keep wiring clear of the rear pan link.

Develop regulated servo power separately from the sensor supply, with a common signal reference. Preserve 3.3 V I2C logic for the current S3 bus. Reserve a separate future camera/data connection; the standard mechanical interface does not imply every future sensor uses the same four-wire bus. Module swaps are power-off service operations. Keep the body IMU fixed. Moving-head measurements will need pose/settling metadata when servo firmware is implemented.

A nominal 60° × 60° ToF frustum was checked against nearby modeled structure at the sampled poses, using an **assumed optical center on the front of the ToF clearance envelope**. This does not validate the exact lens position, aperture, a protective window, optical crosstalk, radar behavior while moving, or unmodeled cables/driver boards/antenna whip. The radar is represented by an open-face envelope; no RF cover is specified.

## Validation and next fit work

The generator checks each manufactured/reference part is a single valid solid, checks independent moving-part interference and current robot geometry at sampled poses, verifies normal carrier mating and rejection of reversed mating, checks cable-port clearance solids, and records master-file hashes before and after. The results are in `validation.json`; they are finite CAD checks, not continuous collision proof, load tests or physical acceptance.

First print only the GH44 blank and receiver fit coupon using the intended PETG process. Check full seating, sensible register clearance, anti-rotation indexing, screw/nut access and cable-window alignment. Then fit the clamp and fixed adapter unpowered. Only after horn hardware, bearings, sensor retention and flex harness are resolved should the complete moving assembly be printed and powered. Weigh the populated carrier and establish a payload/center-of-mass limit from torque, cable drag and vibration tests; no rated payload is claimed yet.

## Manufacturer references

- [DFRobot SEN0628](https://wiki.dfrobot.com/sen0628/)
- [DFRobot SEN0610](https://wiki.dfrobot.com/sen0610/)
- [TowerPro SG90 analog](https://towerpro.com.tw/product/sg90-analog/)
- [SKF bearing catalog: 20 × 32 × 7](https://cdn.skfmediahub.skf.com/api/public/094cc500316fc14e/pdf_preview_medium/094cc500316fc14e_pdf_preview_medium.pdf)
- [Rotor Clip DSH-20](https://www.rotorclip.com/product/dsh-20/)
