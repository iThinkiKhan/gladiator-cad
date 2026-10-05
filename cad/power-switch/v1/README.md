# Power switch holder v1 — 2026-10-05

Built by `scripts/build_power_switch_holder_v1.py`. It reads the master and the v5 tray and changes neither. It checks
everything against solids and refuses to export if any check fails; all pass (`validation.json`). `switch-holder-v1.png`
shows it in place. **Not printed.**

## What Jim asked for

- A small holder for the slide power switch on the **left rail**, using the rear leg space and the raceway floor ("the floor
  of the wire runner can support it").
- **Knob faces the rear, pins point forward.** Not toward the tray legs, not toward the rail. Slide is vertical; **up is ON**.
- Keep the rear clear for wires. Do not get in the way of lifting the power tray out or bolting on the upper deck.

## What it is

- A pocket for the switch in the gap between the rail and the tray's left leg, right beside the rail's sealed rear wall.
  Switch body Y 128.6-135.0, X 19.35-26.15, Z 23.7-36.4. **The knob top is at Y 140.0, flush with the lower deck's rear edge**,
  5 mm proud of the rail's rear face.
- Rear plate with a 5.0 x 6.8 knob window and an engraved up arrow (ON) above it. Front fully open, so the pins and
  4 mm ahead of them are clear for the solder joints and wires.
- **Holding it:** two 1.5 tongues (0.1 gap each side) grip the raceway floor's inboard edge (Z 36.5-38.5) with 5 mm of overlap.
  A flange wraps 3.7 mm behind the rail's rear face, so it can't slide forward, and the tongues stop it sliding back. With the
  tray in, the tray leg is 0.89 away, which can't let it back off 5 mm of tongue, so it can't fall off. No clicks or bumps.
- The switch pushes into the pocket from the front, pins last. The pocket is 0.15 per side over Jim's numbers, and flat walls
  print about 0.1-0.25 over on this printer, so it should be snug. If it's loose, a dot of hot glue.

## Fitting

1. Lift the tray out.
2. Push the switch into the holder (knob through the window, arrow up).
3. Slide the holder outboard onto the raceway floor edge, tongues above and below the floor, until the flange sits behind the rail's rear face.
4. Put the tray back. The tray lift path was swept 60 mm up: it clears the holder and the switch.

## Clearances (from the solids)

Rail 0.10, tray leg 0.89, left base 5.2, upper deck 14.4. Nothing else in the master touches it.

## Print

`stl/Gladiator_PowerSwitchHolder_v1_LEFT-rail_print-on-inboard-face_no-supports.stl`, also in `~/3D-Printer/Incoming/Gladiator/`.
Lay it on the **inboard face** (as exported). 17.8 x 7.7 x 14.3, 118 mm2 on the bed, about 0.7 g. No supports: the only
overhang is the 7.1 bridge over the pocket, and a 45 degree gusset carries the upper tongue. A brim helps on a part this small.

## Not measured

- **Knob width** is assumed to be no more than 4.4 (the window is 5.0). Jim gave the knob's height (5.0) and travel envelope (6.0) but not its width.
- Pin layout is assumed to be one row down the middle. That only matters for the clearance check, because the pin face is fully open.
