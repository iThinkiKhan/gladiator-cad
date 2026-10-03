# Power board tray v5 — 2026-10-03

Built by `scripts/build_power_tray_v5.py`. It reads the master and v3/v4 without changing them, checks everything against
solids, and refuses to export if any check fails (52 checks pass). Results are in `validation.json`; `tray-v5.png` shows the
sections. **Nothing here has been printed.** v4 (what Jim printed) is kept as the record in `../v4-tray/`.

## What Jim found with v4, and what v5 does

| Jim, after printing v4 | v5 |
| --- | --- |
| The removable mounts were far too tight; once the click engaged nothing would come out, and the strong legs tore the thin front wall off the tray before a foot moved. "Just let them slide into wells." | **No bumps, no grooves, anywhere.** The pegs slide into plain wells with the same 0.25 clearance that already fitted well before the click. Nothing holds the tray except its own weight and the collar. |
| The walls are far too weak. "We don't need this tiny thin tray anymore." | Front and rear walls 1.0 -> **2.4** (grown outward, so the board and its end gaps do not move). Floor 1.6 -> **2.4**, grown downward (floor top, posts and board height are unchanged). 2 x 2 root gussets along the inside of all four walls, four 2.5 corner blocks (the front corners are where it tore), and a web from each board post to the side wall. |

| The v4 'lighter arms' pass turned the arm into a V. Jim only wanted more ceiling clearance and feet that go into a base, not an arm redesign. | **The arms are exactly the v3 arm again**: the V scoop is gone and nothing else about the arm changed. A check proves the taper, web and flare match v3 to 0.00 mm3 from the v3 floor up (below that, the taper's two 1 mm side strips reach down to the lower floor). Mast tube gap 0.40 and rim contact 50 mm2, both as v3. |
| Then: the long arm beside the mast is too thick; make it shorter (lower top), same width. | The long arm's top comes down evenly from Z 40 to **Z 34** (20 tall -> 14), width 4.1 unchanged. A 45 degree ramp (Y 104-110) joins it to the full-height taper so it prints without support. The root block, taper, flare and post are proven identical to v3 (0.00 mm3), and the arm was only lowered (nothing added). `WEB_TOP` in the script if you want a different height. |

What differs from v3 around the arms, all from Jim's requests: the rear posts end in pegs that drop into the bases, the post above the peg is 0.6 wider inboard (so the M3 head clears the base wall), a 0.7 fillet at the peg root, and the root block reaches the lower, thicker floor.

The side walls stay 1.0. The tub is only 0.1 inside the rails and has to lift out past them, so they cannot grow outward; they are tied
into the floor, the corner blocks and the post webs instead.

Tray 15.62 -> 19.44 cm3 (about 24 g solid PLA). Floor underside is now 23.9 (1.9 over the modelled cells, was 2.7). Under the board
601 of 10800 mm3 is plastic (posts, webs, gussets); the whole middle is free for solder tails (4.5 tall).

## Bases

The v4 bases already printed still fit the v5 pegs. They have a groove in each well wall that does nothing now; it only costs a little
wall. The v5 bases (queued) are the same part without the grooves. Reprint them only if the grooves bother you.

## Print notes (not started; Jim starts it)

- Tray: as exported, rear face down, as before. 42.8 x 33.8 x 113.2, 270 mm2 on the bed, so use a brim of 8 mm or more.
- **The front wall prints as a bridge across the open tub** (it is the top of the print). It is now 2.4 thick, but the first layers
  still bridge about 36 mm. If your slicer will, add supports under the front wall. Use 4 or more perimeters or a solid wall; the walls
  are thick enough to be solid.
- Fit coupon (the real left base plus a plain peg) is in the same folder if you want to try the slide-in fit before the tray.

## Files

`PowerBoardTray_v5.FCStd/.step`, `stl/` (tray, BaseLeft, BaseRight, FitCoupon, installed reference), also in `~/3D-Printer/Incoming/Gladiator/`.
The INA226 cassette that hangs on the front wall is `../ina-cassette-v2/`.
