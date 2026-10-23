# Gladiator - current calibrated print files, 22 October 2026

M2 heat-set coupon accepted: **2.8 mm**. The insert-bore blocker is cleared.

Already printed: tablets, red shields/crest and coupon. Reprint the stronger white insets; silk is still outstanding. The LED window stays open.

| File | Load | Estimated print time |
| --- | --- | --- |
| GLAD_01_WHITE_EMBLEMS_V2.gcode | WHITE | 58m 19s |
| GLAD_02_SILK_DETAILS.gcode | SILK | 35m 36s |
| GLAD_03_BLACK_CLAMPS_M2_28.gcode | BLACK | 31m 53s |
| GLAD_04_HOOD_SD_M2_28.gcode | RED -> GREY -> RED -> GREY | 9h 43m |
| GLAD_05_PANELS_SD_M2_28.gcode | RED -> GREY -> RED -> GREY | 8h 31m |
| GLAD_OPTIONAL_FIT_SEATS_M2_28.gcode | Regular PLA | 57m 20s |

White v2 is the stronger revision, lying face-up with snug supports. The red shields you printed are unchanged. Silk uses your separate silk profile. Black clamps are newly released with 2.8 mm bores. Fit seats are optional; no extra coupon or LCD test is required.

The two shell jobs are prepared for whenever you choose to print them. Each starts RED, then pauses for GREY, RED, GREY. At each change: first click acknowledges you and reheats; at the second stop swap and hand-purge to the requested colour, wipe, reengage the idler, then click. Keep the head and bed still. There are two clicks per change.

| Shell | Load at stop | Actual colour boundary | Approximate elapsed slicer time |
| --- | --- | --- | --- |
| GLAD_04_HOOD_SD_M2_28 | GREY | 12.01 mm | 2h 56m |
| GLAD_04_HOOD_SD_M2_28 | RED | 55.97 mm | 7h 04m |
| GLAD_04_HOOD_SD_M2_28 | GREY | 61.85 mm | 7h 25m |
| GLAD_05_PANELS_SD_M2_28 | GREY | 12.01 mm | 2h 14m |
| GLAD_05_PANELS_SD_M2_28 | RED | 52.05 mm | 4h 53m |
| GLAD_05_PANELS_SD_M2_28 | GREY | 57.93 mm | 5h 33m |

Times exclude warm-up, waiting at pauses, manual purging and assembly.

All files use EnderNeo SAFE with your inherited machine/filament presets, 60 C bed, original G28/M420 S1/left purge start and separate silk profile. Production bores are 2.8 mm, depth 4.0 mm retained; earlier structural insert sizes and screw clearances are unchanged. Original models and stronger-v2 source files remain hash-unchanged. All thirteen production bores checked in the saved native, 22 valid STEP solids, no support paths through the insert cavities, actual extrusion bounds inside 220 x 220 mm. Released shell pause states replayed and restored correctly. These are CAD/toolpath checks; actual assembly and clamp retention are not newly claimed as tested.

Windows destination: X:/3D Printer. CAD and 3MF projects are included. Source scripts target cad-lab paths. No printer job has been started.
