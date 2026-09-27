# Build 2 parts — 2026-09-27

Fixes from Jim's first physical build. The parts were generated from the master by
`scripts/apply_first_build_fixes.py`, which checks everything against solids and refuses to
save if any check fails. `validation.json` has every mesh's bounds, bed area and volume, plus
the overlap tables before and after. `rail-v2-vs-first-build.png` compares the old and new rails.

| File | What | Print |
| --- | --- | --- |
| `Gladiator_Coupon_RailFrontFoot_R_v2_deck-face-down.stl` | Bottom 10 mm of the new right front foot, ~1.5 g | **Print first.** Screw it through the real right-front slit (M3 from inside the well). If it passes and the head sits flat, print the rails. |
| `Gladiator_SideRail_L_v2-tall_print-on-outboard-face.stl` | Left rail, 6.5 taller, front slot 3.5 back | Outboard face down, raceway up. 52.5 x 133 x 12, ~35 g solid |
| `Gladiator_SideRail_R_v2-tall_print-on-outboard-face.stl` | Right rail (mirror) | Same |
| `Gladiator_MastTube_v2-Z130_print-vertical.stl` | Mast tube, 124 long (was 114) | Vertical, brim |
| `Gladiator_MastBase_v2-holes-42p5_print-spigot-UP.stl` | Mast base, M2 holes 42.5 apart, 3.5 spigot, 0.8 socket chamfer | Upside down, spigot up; brim, support under the outer plate |

Not reprinted: the upper deck. It is the same part, lifted 6.5 by the taller rails.

Changes:

- Battery-to-soffit clearance 8.5 → **15.0**. Rail top Z 48 → 54.5.
- The front foot screw moves from Y 10 to Y 13.5. The foot is lengthened to Y 18.5 (2.5 clear of
  the battery holder's front face). Lateral play is unchanged, at 3 mm.
- A 1.3 mm head relief in the front well. v1's head fouled the outboard skin over the slit.
- Mast top Z 120 → 130.
- Mast base M2 holes 41 → 42.5 apart (±0.75). This is a fit observation, not a caliper reading.
  The deck model was left alone; see `measurements/chassis.md`.

The copies in `~/3D-Printer/Incoming` are byte-identical. The superseded 2026-09-26 mast base
STL was moved to `Incoming/_archive/superseded-20260927/`, so it can't be printed by mistake.
