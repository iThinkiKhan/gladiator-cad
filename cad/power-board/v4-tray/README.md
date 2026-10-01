# Power board tray v4 + snap-in base — 2026-10-01

Built by `scripts/build_power_tray_v4.py`. It reads the master without changing it, checks everything
against solids, and refuses to export if any check fails. Results are in `validation.json`;
`tray-v4-snap-base.png` shows the joint. **Nothing here has been printed.**

## What it is

- **Two bases** (left, right). Each is bolted once at the same rear slits the v3 tabs used, now with an **M3** bolt (Jim: it fits the slit better)
  ((25.5, 130.5) and (53.5, 130.5), tab Z 2.2-5.2, hole 3.4). Each carries a socket, set 0.6 further inboard than first drawn so a d6 M3 head clears the socket wall.
- **The tray** is v3 with the rear tabs gone. Its two rear posts end in **pegs 1 mm smaller**
  (3.0 x 8.1, were 4 x 9.1) that drop into the sockets, 11 mm deep. The arms still rest on the mast
  collar rim, so the pegs never bottom out (1.0 clear).
- **Retention:** 0.25 clearance each side, plus a small ridge (0.5 proud) on each peg face that clicks into a
  groove in the socket wall at Z 11.7. About 0.25 mm of interference per side while it rides the wall.
  No printed latch arms.

## Fitting the bases and swapping batteries

1. Upper deck off. Put both bases on the deck over the rear slits with the M3 bolts **loose** (nut under the deck).
2. Lower the tray so the arms sit on the mast collar and the pegs go into the sockets. It clicks.
3. Tighten the two M3 bolts. A 5 mm wide driver path is clear above each bolt with the tray seated.
   This is the **only** time the bolts are touched.
4. **Battery change:** lift the tray straight up (the click lets go after about 2 mm), set it aside with the board
   still wired (leave slack), swap cells, drop it back. No tools.

## Changes from v3, and why

| Jim, 2026-10-01 | v4 |
| --- | --- |
| Easier battery change: base the tray snaps into | Two bolt-once bases, plug-in pegs, click bump |
| "Get height back": tray can come 1.8 closer to the cells | Floor Z 26.5 -> **24.7**. Jim: installed cells are "negligibly over the rim", so the real gap to the cells is about 2.7 (modelled 0.5 over the holder). The master BatteryCells (4 over) is stale |
| Board closer to the floor | Four board screw posts 7 -> **4.5** tall (pilot depth 4.0) |
| Net | Board sits **4.3 lower**; connector room under the upper deck 17.8 -> **22.1** |

Board holes, board position, the open board ends and the arm geometry are unchanged. The root is slightly deeper
(15.3 vs 13.5 at Y 96) because the floor went down.

## Strengthening pass (Jim, 2026-10-01): lighter arms, stronger tabs

Jim: the arms look overbuilt, and the tabs look prone to breaking. Reading "tabs" as the base tab and its socket walls, plus the
peg root. The arms and the base now trade plastic.

| Part | Change | Why |
| --- | --- | --- |
| Arms | Top scooped from Z 40 down to Z 29 between Y 104.5 and Y 123 (a V: 40 degree front ramp, so no support). Arm is 9 deep at the lowest, 45.7 mm2 at Y 115 (was 82). The root, flare and posts stay full depth. | Between the two collar contacts the arm sees about 0.4 MPa for a 60 g tray. Tray 16.56 -> 15.62 cm3. |
| Base walls | Inboard wall 1.6 -> 2.4, rear wall 1.6 -> 2.0. The bolt-side wall stays 1.2 (the M3 head needs the room). | Cantilever walls, 12 mm tall, printed with the layers across them. |
| Base tab | Runs 2 past the inboard wall and 0.7 past the rear wall, with an r1.8 root fillet inboard and r0.6 rear. | The walls rose straight off a sharp tab edge. |
| Bolt-side wall | A rib on the outside from Z 9 to 17.2, Y 130 to 136, 0.8 thick (wall 2.0 there). It starts above the M3 head and keeps 0.05 clear of the d5 driver path. | The bump groove cut that wall to 0.65. That notch was the weakest point, not the root. |
| Peg root | r0.7 fillet where the peg meets the full-size post, on the two edges that are not flush. | A 3.0 peg into a 4.6 post is a sharp step. |

Bases are 1.04 -> 1.38 cm3 each. The front wall stays 1.2 (the mast base flange is right behind it at Y 127), and the peg is still
3.0 x 8.1 (42 mm2 for the pair against the old post's 56), as you asked.

## Things to check before printing

1. **Cell height.** Jim: installed cells are negligibly over the rim, so the floor has about 2.7 of room. If you want more height back, the floor could drop about 1.7 further and still keep 1.0. Not done: it is your call.
2. **Board underside.** The posts are now 4.5 tall. The assembled board's longest solder tail or lead must be under
   about 4.5 or it touches the floor, which sits 1 above the cell tops.
3. **Bed contact is only 270 mm2** (v3: 364) for a part 111.8 tall. Use a brim of 8 mm or more.
4. **Print the fit coupon first** (`Gladiator_PowerTray_v4_FitCoupon_base-and-peg.stl`: the real left base plus the
   peg, printed the way the tray prints). It answers one question: does the peg go in, click, and hold, and does the
   socket wall survive repeated swaps.

## Files

`PowerBoardTray_v4.FCStd/.step`, `stl/` (tray, BaseLeft, BaseRight, FitCoupon, installed reference).
The four print STLs are also in `~/3D-Printer/Incoming/Gladiator/`. The v3 tray is superseded; do not print it.

## Not in this build

The INA226 cassette in front of the battery box. Photos received 2026-10-01 but the caliper was not read. It needs mounting holes, board thickness, terminal and header
positions. The recorded size is 26 x 22, 11.8 tall, about 40 with the dupont pins.
