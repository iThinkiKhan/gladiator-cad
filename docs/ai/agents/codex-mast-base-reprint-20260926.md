# Mast base reprint — 2026-09-26

Jim requested a 1.5 mm shorter center peg and a chamfer on the mast hole, then asked for the part in the CAD lab's 3D-Printer/Incoming folder.

The current master already had a 0.35 mm upper mast socket chamfer and a 5.0 mm locating spigot below the deck. A copied editable FreeCAD assembly was saved at `cad/mast-base/reprint-20260926/Gladiator_Master_MastBase_short-spigot.FCStd` with 3.5 mm spigot protrusion and a 0.8 mm by 45 degree socket entry. The 14.0 mm spigot diameter and 20.4 mm straight mast bore remain unchanged. The original master and live session were left alone.

The revised mesh was exported spigot up at 0.01 mm linear deflection to `cad/mast-base/reprint-20260926/Gladiator_MastBase_spigot-3p5_chamfer-0p8_UP.stl` and copied byte-for-byte to `~/3D-Printer/Incoming`. FreeCAD confirmed one valid solid; the STL is manifold and solid, bounds 47 × 28 × 23.5 mm, 8,690 facets, and mesh volume agrees with CAD within 0.01%. Use a brim for the thin socket rim contacting the bed and support under the outer plate.

Rebuild script: `scripts/build_mast_base_reprint.py`.
