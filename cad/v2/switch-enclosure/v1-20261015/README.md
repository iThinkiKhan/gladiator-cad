# Power switch enclosure v1 - DRAFT, 2026-10-15 (Claude)

**Draft. Not printed. Built by `build_switch_box.py`.** Jim: no 'hallway'; a separate enclosure with an open rear for wiring that bolts to a mount point on the rails OR on the body.

* **Housing** 14.5 wide x 24 long x 17.9 tall: pocket for the switch body (7.1 x 13.0 x 6.67), a 1.4 mm rear lip with a 5.4 x 11 pin window, and a **wiring shroud that is open at the rear**.
* **Bezel** (separate, 1.2 mm): clamps the body edges, knob slot 4.6 x 8.0, two M2 screws in the side walls (D2.35 pilots). The knob stands 3.65 mm proud of the bezel.
* **Mounting:** two M3 x 25 go down through the top wall (counterbored), through the wiring cavity and the floor, into two heat-set inserts 9 mm apart in a shelf. Same part, same two inserts, either mount:
  * **Rail mount (shell off):** the shelf on the right arch rail (`../../rails/v4-20261015/`), enclosure floor at Z12, front face at Y-22, knob toward the back; box centre X71 (shelf X61..77).
  * **Body mount (shell on):** a shelf inside the hood (`../../enclosure/v2-20261013/`), floor at Z30.5, front face at Y-29.4. The hood rear wall has a 15.1 x 18.5 window; the bezel sits 1.4 mm inside the outer face and the knob stands out 2.3 mm.
* **Checked:** fits the real switch dimensions with zero overlap (body, knob, pins); on the rail shelf, zero overlap with every chassis reference; on the hood shelf, zero overlap with the hood and the references, 0.3 mm to the window edge.
* **Assumed or open:** pin pitch (window assumes 5.4 x 11); the switch current rating (unknown); leads need an inline connector so the enclosure can move between mounts; ON-up is not marked yet; the box is now centred at X71 on both mounts (moved 3 mm outboard 2026-10-15) so it is 3.9 mm from the INA cassette on the rail shelf and 11.3 mm on the hood shelf.
* Print: housing floor down, open rear up (no supports in the cavity expected); the bezel flat.

**SUPERSEDED 2026-10-16 by `../v3-20261016/`**: the front-insert design cannot take a switch that is already wired.
