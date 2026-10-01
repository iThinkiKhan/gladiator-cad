# Claude Notes

Claude-owned durable observations and handoff notes.

## Master file conventions worth knowing (2026-09-27)

- Many parts that sit on the upper deck are **not** spreadsheet-driven in Z: `AntennaPost`,
  `DriverMountLeft`, `DriverBoardLeft`, `WireSlotTool`, `DrvFootReliefTool` and the `DrvV5_*`
  group. Since 2026-09-27 their `Placement.Base.z` is bound to
  `rail_top_z - upper_drawn_rail_top` (48), so they follow the rails. Same idea for the imported
  head candidate and `MastIndexFlatTool`, via `mast_top_z - head_drawn_mast_top` (120).
- Rail sketches `RailGroove`, `RailFootWells`, `RailTabs`, `RailMountSlots` and the haunch
  vertices of `RailOuterProfile` carry hard-coded geometry. `scripts/apply_first_build_fixes.py`
  rewrites them; changing `rail_soffit_z` etc. alone will not move them.
- Order matters when lifting the deck: move `WireSlotTool` **before** the first recompute, or
  `WireSlotEase` (edge-indexed chamfer) loses its edge links in between.
- The front-foot screw is driven through the open inboard side of the well; the Ø6 shafts from
  the rail top are blocked by the 2 mm raceway floor.

## Print hand-off location (2026-09-30)

`~/Desktop/3D-Printer-Incoming` is a symlink to `~/3D-Printer/Incoming`, and it now holds one
subfolder per project (e.g. `Petey/`). Gladiator files go in `~/3D-Printer/Incoming/Gladiator/`.
Jim cleared the old plates out of the incoming folder and out of `cad/print-ready/` (those
deletions are his, uncommitted; leave them). OctoPrint prints come off the SD card.

## Uncommitted work found in the master (2026-09-27)

`Gladiator_Master.FCStd` had been modified on 2026-09-21 15:49 and never committed: extra head
carrier envelopes (e.g. `GH44_Camera_Carrier`, `ESP32_CAM_Envelope`) in `HeadCandidate_v01`.
It was preserved and went into the 2026-09-27 build-2 commit along with the rail/mast changes.
