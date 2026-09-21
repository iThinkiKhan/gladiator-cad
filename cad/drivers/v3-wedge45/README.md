# Driver mount v3 — 45° wedge, standoffs, uses the deck bosses as printed

Built 2026-09-20. Design candidate; master untouched (hash pair in
`validation.json`). Supersedes the v2 candidate.

## Fastening — Option A, settled from the deck solid

The deck's Ø4.6 feature is a **blind pocket opening upward**, 7.5 mm deep, with
2.5 mm of slab beneath. That is an insert pocket, so:

**Heat-set insert into the deck boss from above; M3 screw comes DOWN through the
mount.** No modification to the printed deck.

The mount provides what v1 never had: a Ø3.6 clearance hole from the foot top to
the boss top at Z 58, a Ø9.8 pocket clearing the Ø9.0 boss, and a column above
each screw that a driver can actually reach.

| Driver shaft | v1 | v3 |
| --- | ---: | ---: |
| Ø7, worst 4 mm band | 100% blocked | 55% blocked, Z 78–86 |
| Ø4 hex key, over 64 mm | 513 mm³ (64%) | **41 mm³ (5%)** |

**Use a hex-socket M3 and a hex key.** A fat screwdriver will rub the plate edge.

## Measured against v1 and v2

| | v1 | v2 | v3 |
| --- | ---: | ---: | ---: |
| Cant | 60° | 60° | **45°** |
| Volume | 33.4 cm³ | 22.4 | **20.4** |
| Deck bearing | 591 mm² | 776 | **1411** |
| Fins vs track line | 3.4 proud | 4.2 inside | **6.6 inside** |
| Insert wall | 0.75 mm | 2.0 | **2.0** |
| Screw hole to the insert | absent | absent | **present, both** |
| Boss pockets clear | yes | **no, fouled** | **yes** |
| Deck material cut for fit | — | 804 mm³ | **112 mm³** |

45° is deliberate: every overhanging face lands at the printable limit.

Built in six stages with a solid check after each — foot, ribs, plate, bosses,
clearance cuts, bores — because the previous attempt fused everything at once and
produced 11 disjoint solids. **Every stage was a single valid solid.**

Checks: zero clashes against upper deck, both rails, chassis deck, battery box,
mast, mast base, power shield, antenna post, S3, breadboard and the opposite
mount. All four standoff axes clear. Fins reach X −43.41 against a track line at
X −50.

## Still open

1. **Zero running clearance** on the 112 mm³ deck cut. Still has to become a real
   gap before printing.
2. **`STANDOFF` 15 mm is a placeholder** until the plugged GPIO connector is
   measured. Changing it moves the bosses, not the board.
3. **No print orientation.** The wedge is a 45° triangle so it has an obvious
   flat face, but that has not been worked through.
4. **No stress result.** Bearing area and insert wall are much better than v1;
   that is not the same as a load check. The outboard end of each rib is a
   triangular cantilever 18.8 mm long, deepest at the root.
5. Fins now reach Z 115.3. Not checked against the mast head's swept field.

Rebuild: `scripts/build_drv_v3.py`.
