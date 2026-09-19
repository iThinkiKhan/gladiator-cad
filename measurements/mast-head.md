# Mast-head hardware dimensions

Recorded from Jim's measurements and supplied specification table, 2026-09-16. All dimensions in mm unless stated. CAD-server copy: `measurements/mast-head.md`. Keep raw measurements distinct from design allowances and inferred geometry.

## SG90 servos — physical measurements

| Feature | Value | Interpretation/status |
| --- | ---: | --- |
| Tested servo-body gauge opening | 22.8 × 12.0 | Smallest opening fitted perfectly; recovered from original gauge source. Opening is through a 4 mm plate, not a complete body measurement. |
| Ear-tip to ear-tip overall span | 32.5 | Overall length, **not** mounting-hole spacing. |
| Mounting-hole center spacing | about 27.2 | New measurement; use as provisional hole pitch. |
| Ear thickness | 2.5 | Measured. |
| Ear-hole diameter | 2.5 | Measured; not a nominal M3 clearance hole. |
| Individual tab length | 5 | User description; do not infer body length from overall span minus two tabs without checking tab overlap. |
| Body bottom to ear underside | 17 | Ear underside is mounting seating plane. |
| Ear underside to installed horn underside | about 13.2 | Installed horn clearance datum. |
| Shaft center to short body side | 8.3 | User-reported body-end offset. Cross-width shaft offset remains unmeasured. |
| Shaft center to long horn tip | 17 | Jim clarified this is a horn radius, **not a body-side offset**. Other tips/full sweep still need checking against the approximately 36 overall horn length. |
| Long horn end-to-end | about 36 | Does not establish symmetry about shaft. |
| Shorter/wider horn portion end-to-end | about 18 | User-described horn geometry. |
| Horn extension beyond tab | at most 5 | Orientation-specific observation; not full swept radius. |

Derived vertical distance: body bottom to installed horn underside is approximately **30.2** (17 + 13.2), assuming both measurements use the same ear underside datum and horn installation. This is not total servo height.

Hardware available: SG90 servos with standard gears; predominantly M2/M3 screws, nuts and bolts. Servo count, screw lengths and horn fixing pattern remain unrecorded. Do not force an M3 screw through the measured Ø2.5 ear hole.

Only the smallest servo gauge is accepted from the previous experimental print batch. All other historical coupon dimensions/results are excluded by Jim's instruction.

## Sensors — user-supplied published dimensions

These are supplied reference values, not new physical measurements or independently checked manufacturer drawings. Verify original drawings before fixing mounting geometry. Clearance envelopes are planning allowances, not guaranteed plugged-in envelopes.

| Device | Board/body size | Mounting/geometry supplied | Height/protrusion supplied | Provisional CAD envelope |
| --- | --- | --- | --- | --- |
| DFRobot SEN0628 8×8 Matrix LiDAR | 27.5 × 27.5 | Ø3.1 holes; drawing references 22 / 15 / 5.5; R3.5 corner lobes | Maximum stack 11.5 | 29 × 29 × 13 |
| DFRobot SEN0610 C4001 | 22 × 30 | Hole coordinates not established | Component/connector height unknown | 24 × 32 XY; Z pending measurement |
| AI-Thinker ESP32-CAM | 27 × 40.5 × 4.5 ±0.2 | DIP-16, 2.54 pitch; approximately 22.86 between header-row references | Board/module body 4.5–4.58 excluding lens/headers | 28.5 × 42 × approximately 15 with OV2640; must check actual protrusions |

SEN0628 reference spacings are not yet assigned to coordinates. ESP32-CAM header references are not mounting holes. C4001 front/rear height, connector clearance and mounting points still need measurement for a tight carrier. Sensor mass and the selected installed configurations remain unknown.

## Current mast and deck — saved CAD audit

Source: saved `cad/master/Gladiator_Master.FCStd` at CAD repository HEAD `cdf813c`, audited 2026-09-16. Live GUI may contain unsaved differences. These are model dimensions, not new caliper readings.

| Feature | Value |
| --- | --- |
| Lower deck | 79 wide × 140 long × 2 thick |
| Mast center | X 39.5, Y 113; origin front-left, X right, Y rearward, Z up |
| Lower deck mast opening | Ø14 |
| Mast locating spigot | Ø13.8, bottom Z -5 |
| Documented motor clearance below spigot | 1 |
| Mast OD / bore | 20 / 12 |
| Mast bottom / top | Z 6 / 120; tube length 114 |
| Mast height above deck top | 68 |
| Lower socket ID / collar OD | 20.4 / 26; collar top Z 20 |
| Mast retention cross-hole | Ø3.4 at Z 13 |
| Upper deck slab | 79 × 140; Z 48–52; thickness 4 |
| Upper deck mast collar | Ø28 outside, Ø20.4 bore; Z 38–52; length 14 |
| Intended rear wire window | 10 wide × 12 high; Z 24–36 |
| S3/expander envelope | X 1–43, Y 15–89, Z 58–86.3 |
| Breadboard/C6/BNO envelope | X 43.5–79, Y 15–61.3, Z 52–73.5 |
| Driver support extent | Y 90–139.5; top Z 94 |
| Antenna post extent | X 65–75, Y 3–13, Z 52–78 |

The saved wire-window pocket does not actually open the tube. An unsaved trial with Reversed=True and Length=12 opens the rear wall into the bore. See `docs/mast-head/cad-audit-20260916.txt` on the CAD server. No master geometry was changed by that audit.

## Harness

Not yet designed. Preserve the 12 mm mast bore; develop conductors, accessible disconnects and flex loops alongside the neck. There are no actual bundle/connector dimensions to report yet. Reserve separate provision for future camera/data wiring rather than assuming a four-wire sensor connection covers it.
