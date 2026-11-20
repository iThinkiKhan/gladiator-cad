# Antenna bulkhead mount v3: clear fixing screws

The saved v2 mount has two 3.4 mm fixing holes at `(60, 10)` and `(76, 10)`.
Those holes pass through the Z58–62 flange, but the gussets and the rear edge
of the upright plate obstruct the screw-head and driver approach above Z62.

`fix_antenna_screw_access.py` opens a 6.4 mm diameter vertical approach over
each hole from Z62 to Z86 with an editable FreeCAD pocket. It leaves the
flange, existing 3.4 mm holes, SMA opening, and all other assembly parts alone.

- `AntennaMount_v3_print-on-front-face.stl` is the corrected print file.
- `Gladiator_Master_antenna_v3_candidate.FCStd` contains the editable pocket
  in an isolated copy of the full assembly.
- `AntennaMount_v3_screw-access.step` is an interchange copy of the mount.
- `validation.json` records the exact clearance and mesh checks.

The original master and `Gladiator_P2_AntennaPost_print-on-front-face.stl`
remain unchanged. Use the **v3** STL for this mount. Check the actual screw-head
diameter before printing; the modeled vertical approach is 6.4 mm wide.
