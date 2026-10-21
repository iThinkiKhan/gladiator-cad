# Power switch holder v3 - DRAFT, 2026-10-16 (Claude)

**Draft. Not printed.** Built by `build_switch_holder_v3.py`. Replaces the v1 box (switch had to go in from the front through a pin window, impossible for a switch that is already wired) and the v2 drop-in draft (on hold).
Jim: keep essentially the holder he has (the v1b idea: pocket, knob window, open on the pin side so a wired switch slides in), a little stronger, a better mount point for covered or uncovered use, screws from inside the shell, and no reprinted rails.

* **Shape:** a closed rectangular holder 14.5 x 26 x 17.9. 2.0 mm front wall with a 4.6 x 8.0 knob slot (the knob stands 2.85 mm proud). Pocket 7.1 x 13.0 (0.15 per side over the 6.8 x 12.7 body). **The rear is open** (9 mm wide shroud): the wired switch is pushed in from the rear knob-first and the soldered leads trail out.
* **Retention:** two M2 pilot holes through the side walls (D2.2, mid-pocket): M2 x 8 screws press on the metal body, removable. (A dot of glue would also do.)
* **Stronger than v1:** front wall 2.0 (was a 1.2 bezel), no counterbore in the top wall (v1 left 0.9 mm under the screw head), top 1.9, floor 3.0, side walls 3.7 at the pocket.
* **Wall joints (Jim: they tend to separate, not the walls):** every OUTSIDE vertical corner is rounded R1.0 so the perimeters turn the corners instead of butting; the inside corners are sharp (Jim: exterior rounding is enough, and inside radii would cut into the switch body corners). The plate sets this one part to **6 walls and 100 % infill** (object-level), so it is all perimeters and solid fill, with no sparse infill to leave joints unsupported. Worth printing it slower and hotter than normal if your joints still split; I have not changed temperature or speed.
* **Mount, same part both ways:** two M3 x 25 + 7 mm washer go DOWN from the top (heads inside the shell, nothing outside) through two slots 5.0 (X) x 3.6 (Y), 9 mm apart (Y12 and Y21 from the pocket front), into heat-set inserts in the shelf.
  The slots give 1.0 mm of play each side in X, so a shelf position known to half a mm is enough. The screw passes beside the leads in the shroud (3 mm each side).
  * **Uncovered:** the printed right rail's shelf, which already has the two inserts (CAD insert X71, Y-10 and Y-1; with the rail as installed X72.6). **No rail reprint.** Holder floor at Z12, front face Y-24.
  * **Covered:** a shelf inside the hood (inserts at X71, Y-18.0 and Y-9.0, floor Z30.5) with a CRADLE: two guides 15.0 mm apart (0.25 each side of the 14.5 mm holder), 7 mm tall, along the holder's sides, so it drops in one way and sits exactly. The hood rear wall has a 15.4 x 18.5 window cut on the same centre line, and the holder's 2.0 front wall is FLUSH with the outer skin (Y-32.0); the knob stands 2.85 mm proud of it. The floor slots only matter on the rail shelf; in the hood the guides locate it.
* **Checked (solids):** switch body, knob, pins, leads envelope and the rear slide-in path: zero overlap with the holder. On the real right rail shelf: no overlaps, 5.4 mm from the INA cassette, 5.0 mm above the track approximation. On the hood shelf: no overlaps, 11.3 mm from the INA cassette.
* **Print:** floor down as exported, no supports (7.1 and 9.0 mm bridges), floor-slot chamfers on the bed side. 24 m, 4.6 g (plate SW).

## Open
* The switch pin pitch and current rating are still unmeasured; the leads need an inline connector if the holder moves between mounts.
* ON-up is not marked.
* Whether the real printed shelf sits at the insert position I computed (X72.6) is a calculation from the rail's measured placement, not a measurement: the slots cover +-1.0 mm.

## Revision 2026-10-16 (Jim: the pocket around the switch body is too tight; one screw is enough)
* **Looser pocket:** 7.6 wide x 13.5 tall (0.4 mm per side over the 6.8 x 12.7 body; was 0.15). It narrowed exactly where the switch body sits, and PLA flats print oversize, so a switch with its leads was hard to get in. The two M2 side screws hold the switch (they pinch it from both sides, centred), so the pocket no longer has to grip it.
* **One screw:** a single M3 x 25 + washer through one 5.0 x 3.6 slot at 12 mm behind the pocket front, into the FIRST shelf insert (rail shelf: the insert at Y-10; hood shelf: Y-18.0). The housing is now **14.5 x 20.0 x 17.9** (was 26 long); floor 2.7, top 1.7, front wall 2.0, side walls 3.45.
  Screw length: top 1.7 + cavity 13.5 + floor 2.7 + insert 7.5 = 25.4.
* **Hood:** the shelf has one insert, the cradle guides (15.0 apart) stop the holder turning, window and flush face unchanged. **Rail shelf (uncovered):** one screw on a flat shelf can let the holder twist if the leads are tugged; the clamp friction resists it. If it wobbles, say so and I will add two small skirts that straddle the shelf.
* **Checked (solids):** switch body, knob, pins, leads envelope and rear slide-in path: zero overlap. Rail shelf: no overlaps, 9.8 mm from the INA cassette, 5.0 mm above the track. Hood shelf: no overlaps, 12.6 mm from the INA cassette. Shell rebuilt: zero collisions, sweeps unchanged (hood back 150 mm, right panel 120 mm, left panel 3 mm slack).
* **Print:** plate SW, 18 minutes, 3.5 g, 6 walls + 100 % infill, floor down, no supports.
* The soldered leads still pass the screw column, 1.8 mm behind the pin tips, with 3 mm each side in the 9 mm shroud.
