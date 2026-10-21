# INA226 mount v3 (adapter) - DRAFT, 2026-10-19 (Claude)

**Draft. Not printed.** Built by `build_ina_mount_v3.py`. Replaces the v2 cassette (the cantilevered shelf), which Jim found weak.
Jim (2026-10-19): mount the INA at the rear of the batteries and the power-board tray, board flat against them (underside toward the tray), header pins facing LEFT
when you look at the robot from the rear with the mast forward. Later it becomes part of the power-board tray; for now an adapter on the printed tray (no reprint of the tray, rails or deck).

## What it is
* **Hook (unchanged from the v2 cassette, so it fits the printed v5 tray):** a 1.6 mm lip over the top of the tray's rear wall (wall top Z33.4) and two 8 mm toes down the
  inside of the wall between the corner blocks. Every gap to the tray 0.3 mm. It drops on from above and lifts straight off; with the tray in, it cannot move more than 0.3 mm
  in any direction (checked: 0.5 mm forward, back, left, right or down is stopped by the tray or the battery holder).
* **Upright backplate**, 2 mm, X21..58, from the lip down to Z2.5 (0.5 mm above the aluminium). It bears on the battery holder's end face (0.3 gap) and, through a spacer block above
  the cells, on the tray wall (0.3 gap). So the board load goes into the tray wall and the battery holder, not into a cantilever.
* **Board:** 26 x 22 INA226 stands upright on the plate's rear face, underside toward the tray, **component side facing the rear, header pins to the LEFT (X26..32), terminals on the
  RIGHT with the leads leaving to the right**, toward the switch on the right rail shelf. Board X32..58, Z8.5..30.5, PCB at Y13.1..14.7.
  Four 4 mm stand-offs: two M2 bosses in the header-edge corners (holes 2.0 from the edges, same as v2, which you already screw into) and two pads under the middle;
  the 3 mm terminal pin tails clear the plate by 1 mm. Screws: **2 x M2 x 5 or x 6 self-tapping** (1.6 pilots, 3.6 deep).
* 5.5 g. Print **upside down, the top of the lip on the bed** (as exported): no supports, the stand-offs have 45 degree undersides. Plate IM: 26 minutes, 5 g.

## Checked (solids)
* Adapter, board, terminals (with their tails), header pins and an 8 mm Dupont housing on the pins: **no collision** with the tray v5, battery holder and cells, aluminium deck,
  both rails AS INSTALLED (measured layout), deck v4, mast tube and base, the switch holder on the rail shelf, or the rear hood.
* Gaps: tray, battery holder 0.3 (the hook fit); deck 0.5; rails 4.9 from the adapter, 4.8 from the board (right rail); the board is 6.3 from the battery holder.
* Screwdriver access from the rear to both M2 screws and the terminal screws: clear with the shell off. With the hood on, the hood covers them (as everything else).
* The leads leaving the terminals to the right reach the right rail's rear foot/shelf after about 5 mm, so they turn there (rear, to the switch, or up).

## Fitting
1. Take off the old cassette.
2. Screw the INA to the adapter (component side out, header to the left as seen from the rear).
3. Drop the adapter onto the tray's rear wall from above: lip over the wall, toes inside, plate down behind the batteries.

## Next (Jim: make it part of the power-board assembly)
Once this fits, the same plate and stand-offs can be fused onto the tray's rear wall for the next tray print (same board position, no hook). Not built until the adapter is proven.

## Inferred, not measured
M2 hole positions (2.0 from the header edge and the sides) and the 3 mm pin tails, as for v2; header pins 7 mm; terminal height 11.8.
