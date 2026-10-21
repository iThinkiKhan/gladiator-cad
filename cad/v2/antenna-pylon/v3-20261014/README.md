# Antenna pylon v3 - 2026-10-14 (Claude)

**Review part. Not printed, not fitted. The master's `AntennaPost` is not modified.** Built by `build_pylon_v3.py` (`freecadcmd`).

Why: Jim found the old pylon too hard to turn and tighten. The master's `AntennaPost` is a 6 mm plate with a round O11 x 4 mm pocket on the inside
(connector flange) and a 2.0 mm web on the outside, O7.0 hole. The round pocket neither holds the flange nor leaves room to hold it by hand.

Rule used here (and in the enclosure v2 rear mount): **no pocket on either face.** 2.0 mm plate (the SMA clamp limit is about 2.2), flat on both sides,
an open flat zone of radius 11 mm around the axis (nut 8 AF / 9.2 corners, flange, fingers, pliers, spanner), stiffness from two edge ribs and two lower diagonal spokes that
start outside that zone.

| | old (master) | v3 |
| --- | --- | --- |
| Plate | 6 mm with O11 x 4 pocket | 2.0 mm, flat both faces |
| Footprint | X56..80, Y2..13 | X54..82 (2 mm wider each side so the ribs clear the zone), Y2..13, same Z64.5..92.5 |
| Hole | O7.0 at (68, 84.5) | same |
| Deck bosses | (60,10), (76,10), O3.6 | same |
| Volume | 4333 mm3 | 3373 mm3 |

Checked: single valid solid; zero overlap with every chassis reference (it rests on the deck bosses and sits flush with the deck edge at X82); no material within 11 mm of the axis on the inside
face at the probed points. STL `Gladiator_AntennaPylon_v3.stl` is solid and manifold, 28 x 28 x 11 mm, outside face down, ribs up (no supports expected; the horizontal bolt holes are 3.6 mm).
Not checked: the real flange shape, the tail/cable route over the breadboard, loaded stiffness of a 2.0 mm plate with the whip on it. If it flexes, thicken the spokes first; do not add a pocket back.
