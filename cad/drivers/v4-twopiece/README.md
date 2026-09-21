# Driver mount v4 — two pieces

Built 2026-09-20. Candidate; master untouched. Supersedes v2 and v3.

## Why two pieces

The board's high bosses land at X 14.54, Y 95 and 134.5. The deck screws are at
X 14.5, Y 95 and 135. **They want the same place.** In one piece you must choose
between supporting the boss and reaching the screw — v3 chose the screw and the
high bosses came out with **zero** material around them, which is what Jim spotted.

Split, there is no conflict. The base goes down first with open sky above it;
the wedge then bolts on and can be solid right through that region.

## Assembly order

1. Heat-set insert into each deck boss (the deck's own Ø4.6 pocket, as printed)
2. Base plate down, 2 × M3 from above
3. Wedge onto the base, 4 × M3 horizontally from inboard into inserts in the wedge
4. Board onto four M3 male-female standoffs, GPIO face inboard

## Measured

| | v1 | v3 | v4 |
| --- | ---: | ---: | ---: |
| Boss support, high pair | n/a | **0.0 mm³** | **277** |
| Boss support, low pair | n/a | 129 | **410** |
| Pieces | 1 | 1 | 2 |
| Volume | 33.4 cm³ | 20.4 | 11.8 + 25.2 = **37.0** |
| Deck bearing | 591 mm² | 1411 | 803 |
| Fins vs track | 3.4 proud | 6.6 inside | **6.6 inside** |

Every build stage a single valid solid, both pieces. Zero overlap between base
and wedge. Zero clashes against eleven robot solids. Both deck screws open, all
four standoff axes clear.

Volume went **up** against v3 — that is the cost of actually supporting the
bosses and of the joint flange. Two simpler pieces, each printable flat.

## Still open

1. Zero running clearance on the 376 mm³ deck cut.
2. `STANDOFF` 15 mm is a placeholder until the plugged GPIO connector is measured.
3. No print orientation.
4. No load check. The joint is 4 × M3 in single shear plus the flange bearing.
5. Fins reach Z 115.3 — not checked against the mast head's swept field.

Rebuild: `scripts/build_drv_v4.py`.
