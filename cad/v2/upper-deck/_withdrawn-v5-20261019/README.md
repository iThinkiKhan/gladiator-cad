**WITHDRAWN 2026-10-19: Jim wants the deck left as it is (v4). The base takes the screw depth and the insert relief instead (cad/drivers/v5-interlock, v5d).**

Upper deck v5 (2026-10-19): deeper deck-screw pockets for the driver mounts.

Derived from the saved v4 deck solid; everything else is identical to v4.

The v5d driver base sinks the deck-screw head 3.3 mm into the foot, so the screw
tip now reaches 3.3 mm lower than before.  An M3 x 10 from the recess floor
(foot underside = boss top Z64.5, + 0.7 mm floor = Z65.2) ends at Z55.2, but the v4 pocket
floor is at Z57.0.  A D3.6 relief hole is added under the D4.6 insert pocket,
down to Z55.0 (0.5 mm skin over the Z54.5 underside).  The insert pocket itself
(D4.6, 7.5 deep, insert 7.05 long) is unchanged, so inserts set exactly as before.
For an already printed v4 deck: drill a 3 mm hole through the insert bore to 9.5 mm below the boss top.

Validation: validation.json

## Print orientation and sag (2026-10-19)
The deck prints top-up, so the insert pockets open upward and their floors sit on solid plastic: no bridge, no sag. The new D3.6 relief under each insert pocket is below the pocket floor ring and only gets wider upward, so it is not an overhang either. Bores that DO sag when printed: any pocket that is horizontal or opens toward the bed (the hood shelf pocket, now 0.6 mm deeper; the rails' retention and switch-shelf inserts, which print horizontal on their inner face; the driver wedges' joint and standoff pockets).
