# Gladiator chassis measurements

Units: mm. Declared orientation: front is the edge before the 4S battery case. Origin is the front-left deck corner viewed from above. X increases right; Y increases rearward; Z increases upward.

| Feature | Value | Model interpretation |
| --- | ---: | --- |
| Deck front-to-back | 140 | Y = 0 to 140 |
| Deck side-to-side | 79 | X = 0 to 79 |
| Deck thickness | 2 | Z = 0 to 2 |
| Tower opening interior diameter | 14 | Center X = 39.5, center Y = 113 |
| Rear edge to tower opening rear edge | 20 | 140 - 20 - 7 = 113 center Y |
| Tower opening side margins | about 32 each | Centered based on 79 mm deck width |
| Battery case front gap | 21 | Footprint begins at Y = 21 |
| Battery case length | 75.5 | Footprint ends at Y = 96.5 |
| Battery case width | 79-80 | Modeled as 79 mm, full deck width |
| Battery case rear gap | about 45.5 estimated | Calculation from other measurements is 43.5 mm; remeasure later |
| Four rear slit widths | about 4 | Modeled as rectangular 4 mm cut-throughs |
| Rear slit rear termination | 7.5 from rear | Rear Y = 132.5 |
| Long (inner) rear slit front termination | about halfway down battery case | Modeled Y = 58.75, approximate |
| Short (outer) rear slit length | about 33 | Front Y = 99.5 |
| Inner rear slit to tower opening | 5 | Measured nearest-edge gap |
| Outer rear slit offset | 12 toward each side | Modeled center-to-center from inner slit |

Current modeled rear slit X extents: long (inner) left 23.5-27.5, long (inner) right 51.5-55.5, short (outer) left 11.5-15.5, short (outer) right 63.5-67.5. Slot end profiles and exact front endpoints still need another measurement; the model currently uses square ends.

## Front slots (added 2026-09-15)

Two new slots near the front, independent of the rear slits above: 4 mm wide, near edge 8.5 mm from each side, terminating 7.5 mm from the front edge and running rearward from there.

| Feature | Value | Model interpretation |
| --- | ---: | --- |
| Front slot side gap | 8.5 from deck side edge | Left slot X = 8.5-12.5, right slot X = 66.5-70.5 |
| Front slot edge gap | 7.5 from front edge | Slot near end Y = 7.5 |
| Front slot length | 33 (matches rear short slot length) | Slot far end Y = 40.5 |

Modeled front slot extents: left X 8.5-12.5, Y 7.5-40.5; right X 66.5-70.5, Y 7.5-40.5.

## Front mounting holes (added 2026-09-15)

Two 4 mm holes near the front edge, X-positioned 3 mm inside each front slot's inner edge; each is paired with an M2 self-tap pilot hole 1 mm (edge-to-edge) further from the front edge, directly below it.

| Feature | Value | Model interpretation |
| --- | ---: | --- |
| Mount hole diameter | 4 | Through-hole |
| Front hole edge gap | 12 from front edge | Hole center Y = 12 |
| Front hole slit inset | 3 inside front slot's inner edge | Left center X = 15.5, right center X = 63.5 |
| Pilot hole diameter | 1.6 | M2 self-tap pilot, not a free-pass clearance hole (aluminum deck) |
| Pilot hole edge-to-edge gap | 1 from the 4mm hole | Left/right pilot center Y = 15.8 |

Modeled front hole centers: 4mm holes (15.5, 12) and (63.5, 12); paired M2 pilot holes (15.5, 15.8) and (63.5, 15.8).

## Rear pilot holes (added 2026-09-15)

Four M2 self-tap pilot holes (1.6 mm) in the gap between each side's rear inner (long) and rear outer (short) slit, biased 0.5 mm toward the outer slit from the gap midpoint.

| Feature | Value | Model interpretation |
| --- | ---: | --- |
| Rear pilot edge gap | 12 from rear edge | First hole Y = 128 |
| Rear pilot spacing | 17 between the pair | Second hole Y = 111 |
| Rear pilot outside bias | 0.5 toward outer slit | Offsets X from the inner/outer slit gap midpoint |

Modeled rear pilot hole centers: left (19.0, 128) and (19.0, 111); right (60.0, 128) and (60.0, 111).

All of the above are driven by named cells in the `Parameters` spreadsheet inside `Gladiator_Master.FCStd` (`mount_hole_diameter`, `pilot_hole_diameter`, `front_slit_side_gap`, `front_slit_edge_gap`, `front_slit_length`, `front_hole_edge_gap`, `front_hole_slit_inset`, `pilot_hole_offset`, `rear_pilot_edge_gap`, `rear_pilot_spacing`, `rear_pilot_outside_bias`). `outer_slit_center_spacing` still drives the rear outer slits, unchanged from the original model.
