# Stronger white shield emblems (v2) - 2026-10-22 (Claude)

Jim: both printed white shield insets came out poorly; they must be inherently stronger and still fit the red shields already printed.
Built by `build_emblem_v2.py` from the Round 5 print CAD (read-only). Same red field, same silk boss, same M2 x 6 screw.

* Base layer fills the red field recess to 0.05 mm per side (was 0.15); a wider top layer sits on the red surface: bolts 1.75 mm (were 1.15), feathers 2.25 (1.65), ring 2.7..5.4, rim 0.5 mm wider inward.
* 1.8 mm thick (was 1.0): about 6x the bending stiffness; 1052 mm3 against 490. It stands 1.4 mm proud of the red (was 0.6). The old emblem lies entirely inside the new one.
* Checked on solids: zero overlap with the red field and the panel; the silk boss rides 0.8 mm higher (0.1 mm3 contact at its curved edge); the M2 x 6 still reaches the insert.
* **Print lying on its back, visible face up**, snug normal supports under the curved back, 3 mm brim, 0.12 mm layers (Jim white PLA First Print / EnderNeo SAFE from plate 04). 58 m, 4.2 g for both. SAFE start guard passed.
  Files: `R5_04B_White_Shield_Emblems_v2_STRONGER.3mf`, `R5_04B_EMBLEMS_V2.gcode` (SD). Replaces plate 04.
