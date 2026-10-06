# Head print plates for OrcaSlicer (combined, supports painted), 2026-10-06

Three ready-to-open OrcaSlicer projects for the head, built from the released plates
(v04 Plates 1-4, v05 Plate 5). They carry Jim's EnderNeo printer, Generic PLA @System -
First Print filament and 0.20mm Standard @ First Print process (4 walls, 30% crosshatch infill,
0.2 mm layers) plus the support painting below. Every part keeps its released print
orientation. Nothing here changes any part's geometry.

| Project | Parts | Estimate (Orca CLI slice) |
|---|---|---|
| ORCA-A PanStack | pedestal, retainer, clamp cap, rotor, drive pulley, servo carriage | 4 h 35 m, 52.8 g |
| ORCA-B TiltAndSensors | display frame, GH44 carrier, GH44 receiver, tilt yoke, ToF frame, radar frame | 6 h 20 m, 64.7 g |
| ORCA-C Neck_Main | Neck_Main with 8 mm brim | 2 h 08 m, 26.8 g |

Total about 13 h, 144 g. The estimates come from slicing each project headlessly with
OrcaSlicer 2.4.2 and the settings embedded in it, so the real print will differ a little.
Nothing has been printed.

## Support painting

Process default is `normal(manual)`: supports appear only where a painted enforcer says so.

* **Pan_Raised_Pedestal** (A): one enforcer, the exact plan view of the top-plate underside, from
  the bed to the roof. It is cut away inside r 14.7 of the axis, so nothing touches the belt
  flange or channel. Supports may stand on the base flange.
* **Rear_Display_Frame** (B): four enforcers, one under each corner tab (tabs at z 58.2).
* **Neck_Main** (C): this object is `normal(auto)` with blockers, so the arm frame, the collar
  wing and the arm-end bosses get supports while four things stay clear: the mast-bore
  ceiling (z 16.0), the stepped ledge (z 15.5), the 0.8 mm lip at the top of the tube (z 41.5)
  and the two clamp-bolt ears (so no support goes into a bolt hole).
* Everything else prints with no supports: retainer, rotor, drive pulley, carriage, clamp cap,
  yoke, GH44 receiver, carrier, ToF frame, radar frame.

The enforcers and blockers are ordinary parts of the Orca project (see the object list). They
can be moved, resized or deleted there.

## Checks done

Each project was sliced and the G-code read back: support extrusions land only in the places
above (`support-map-A/B/C.png`, support seen from above over the part outlines). Layer height
0.2, 4 walls, 30% infill, supports on, no brim except Neck_Main. All three fit the 220 x 220 bed
(A 158 x 108, B 189 x 145 with 15 mm side margins, C 78 x 86 plus its 8 mm brim).

## Not checked

* The projects were not opened in the Orca GUI, only sliced from the command line. Open each
  one and look at the preview before sending.
* Left unsupported, as released: the three internal roofs in the GH44 receiver (about 12 mm
  wide, 3.8 mm up; a 1 mm sag happened on the R3c coupon) and the 22 mm bridged roof inside
  the pedestal at z 2.0. If either sags, add an enforcer.
* Neck_Main touches the bed over 142 mm2 and is 43 mm tall. Watch its first layers.

## Rebuild

    freecadcmd scripts/build_head_orca_plates.py
    python3 scripts/verify_head_orca_plates.py

Settings template: `template/` (a project Orca saved with the EnderNeo profile). The script
overrides it with the flattened EnderNeo / Generic PLA / 0.20 Standard presets from
~/.var/app/com.orcaslicer.OrcaSlicer, then turns supports on. `build-summary.json` lists every
setting that was changed relative to the template.
