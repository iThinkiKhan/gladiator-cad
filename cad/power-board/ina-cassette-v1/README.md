# INA226 cassette v1 — 2026-10-01

Built by `scripts/build_ina_cassette_v1.py`. It reads the master and the v4 tray without changing them, checks
everything against solids, and refuses to export if any check fails. Results are in `validation.json`;
`ina-cassette-v1.png` shows the layout. **Nothing here has been printed.**

## What it is

A flat shelf for the INA226, in front of the battery box. It is a separate part that hangs on the front wall of
the power board tray v4 and slides off forward, so it can change without touching the tray. The tray is not modified.

- **Board layout (Jim):** front to back, header edge facing the front with its 4 pins poking out (7 mm), screw
  terminals at the rear. The board sits on two M2 posts at the header-edge corners (4 tall) and two small pads. A **10 mm** gap
  between the terminal edge and the plate leaves room for the terminal wires to leave and turn (about 3 straight, then a 5 mm bend; the side lips
  are low, so wires can leave sideways or up).
- **Hold:** a plate in front of the tray's front wall, a lip over the wall top (0.1 clear) and a tongue under the
  tray floor (0.1 clear). Two small bumps on the tongue press the floor by 0.2 mm, so it holds by friction and
  clicks as it goes on. No screws. It cannot lift off; it slides off forward.
- **Sideways:** two wings on the shelf sit 0.6 from the rails' front posts (X 18 and 61) and locate it sideways
  whenever the tray is in the robot. The tray's side walls are only 0.1 inside the rails, so nothing else can.
- **Lifts out with the tray:** checked over 40 mm of straight lift, and over 20 mm of slide-on travel, with the mast
  tube fitted.

## Fitting

1. Hold the cassette in front of the tray (tray out of the robot is easiest), tongue level with the underside of
   the tray floor and lip level with the top of the front wall.
2. Slide it straight back until the plate meets the wall. The bumps click.
3. Screw the INA226 to the two posts with M2 screws (self-tapping into a 1.6 pilot), terminals toward the rear.
4. To remove: pull it straight forward.

## Check before printing

1. **The two hole positions are inferred, not calipered.** Jim: the holes touch the corner of the board with about 1 mm
   of board around them. Read as a corner arc of r 2 concentric with the d2 hole, so the hole centres are 2.0 from the
   header edge and 2.0 from each side edge (18.0 apart). If the real offsets differ by more than about 0.3, tell me
   the two readings.
2. **Pin tails: Jim measured about 3 mm** between the bottom of the screw terminal and the bottom of the board, read here as the pin
   tails below the PCB (it replaces the derived 2.2). The posts leave 1.0 under them. If the 3 meant something else, tell me.
3. **Nothing is assumed under the PCB** apart from the terminal and header tails. The two pads sit 13 from the header
   edge, near the side edges, away from the terminal tails. Check the underside before the first fit.
4. **Overhang.** The board hangs 12.2 beyond the front edge of the deck; the pin tips reach 19.2 beyond it. A Dupont
   housing on the pins adds about 8 to 14 more.
5. The terminal block depth (8.5) is an envelope, not a measurement.
6. Fit is tight by design (0.1 gaps). If it is too tight or too loose on the printed tray, the gaps and bump height
   are `GAP_Z` and `BUMP_H` in the script.

## Files

`INA226_Cassette_v1.FCStd/.step`, `stl/Gladiator_INA226_Cassette_v1_print-upright.stl` (also in
`~/3D-Printer/Incoming/Gladiator/`), `stl/INA226_Cassette_v1_installed.stl`. About 4.8 g. Prints upright, no support:
42.0 x 46.2 x 11.5, 1515 mm2 on the bed, one 2 mm lip overhang (84 mm2).

## Print notes (not started; Jim to start it)

- Print it as exported: shelf and tongue undersides on the bed, plate and lip standing. No supports, no brim needed. Do not scale it.
- The fit that matters is 0.1 mm on the plate, lip and tongue, and the 0.3 bumps. It can only be tried on the **printed tray**, so the
  cassette and tray should be printed together, or the tray first. Hold the cassette level and slide it on from the front.
- If it will not slide on, the first thing to try is lightly sanding the tongue top (the bumps), not scaling the part.
- The shelf is a 37 mm cantilever. Keep it away from the bed edge when moving it; the first layers are the whole fit.
