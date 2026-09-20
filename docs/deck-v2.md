# Upper deck v2 — design spec

Started 2026-09-20. **Not yet cut.** Two things block the geometry; the power board mount is
specified here and can be cut as soon as one of them clears.

## Why v2 exists

1. **The S3 boss pattern on the printed deck is wrong** and cannot be rescued by re-drilling —
   see `measurements/components.md`. That alone forces a reprint.
2. The power distribution board has never had a mount.

Since the deck is being reprinted anyway, the power board mount is free to fold in. That is the
whole argument for doing it here rather than bolting legs to the aluminium deck.

## The envelope, measured on the solids

| | |
| --- | ---: |
| Deck underside | Z 48.00 |
| Battery top | Z 21.50 |
| **Headroom** | **26.50** |
| Clear span across X between the rails (at Z 34.8) | **9.75 .. 69.50 = 59.75** |
| Battery footprint | X 0..79, Y 21.0..96.5 |

**The board can only go one way round.** At 60 x 40 it needs 60 along Y and 40 across X. Turning
it to put 60 across X fails by a quarter of a millimetre — the clear span is 59.75. So it spans the
battery lengthwise, which is exactly why it has to lift away with the deck.

## Why not legs to the aluminium deck

`PowerShield` already implements that, and it is geometrically sound — checked against the battery,
both rails, the mast base and tube, and both decks: **zero clash with anything**.

The objection is not fit, it is the battery. The cells come out vertically, and the shield sits
directly over them at Z 6..30 spanning Y 39..112. Anything fixed above the battery has to come off
before a cell can be swapped, which is the constraint `measurements/components.md` recorded in the
first place. Hanging the board from the deck keeps that access.

## The mount: through-holes only, no underside features

**The deck gets four M2 clearance holes and nothing else.** The board hangs below on spacers; the
deck itself stays single-sided.

That matters more than it sounds. The deck prints with **zero support** precisely because every
feature is on the top face, and the face on the bed is the one that mates with the rail tops — the
flattest surface a printer makes. Putting standoffs on the underside would cost both: support
scarring on the mating face, and roughly 10000 mm2 of support. Through-holes cost neither.

It also makes the spacer height tunable without touching the deck, which matters because the stack
is tight (below), and it allows bought M2 standoffs instead of printed ones.

### Hole positions

Board centred across the clear span and along the battery:

| | |
| --- | ---: |
| Board occupies | X 19.63 .. 59.63, Y 28.75 .. 88.75 |
| Hole pattern (c-t-c, confirmed) | 34.5 across X, 54.25 along Y |
| **Hole centres** | **X 22.38 and 56.88, Y 31.63 and 85.88** |
| Hole diameter | 2.6, the calibrated M2 clearance |

Clear of the six rail-fixing holes at X 12 / 67, and clear of the mast collar.

## Two problems that need deciding

### 1. The stack is tight

Board envelope is leads + PCB + components. Against 26.50 of headroom:

| If "~16 tallest point" means | Stack | Slack |
| --- | ---: | ---: |
| 16 above the PCB (so 6 + 1.6 + 16) | 23.60 | **2.90** |
| 16 including the PCB (so 6 + 16) | 22.00 | **4.50** |

That slack has to cover clearance at the deck, clearance to the battery, **and** the growth room
Jim asked for on the 6 mm lead protrusion. At the pessimistic reading there is not much left.

**Needed:** is the ~16 measured from the PCB surface or from its underside? One caliper reading.

### 2. The screws land under the top-side boards

The S3 occupies X -0.5..41.5 and the breadboard X 44..79.5, so *any* hole in the X 22..57 band sits
under one of them. There is no gap between those two boards to exploit — it is 2.5 wide.

M2 heads are about 3.5 across and 1.5 tall, and the S3 stands on 6 mm bosses, so they physically
fit underneath. But it fixes the assembly order: **power board and its four screws go in before the
S3 and the breadboard.**

Alternative if that is unacceptable: a printed spacer that snaps into the deck hole from below, so
no top-side access is ever needed. More design, no assembly-order constraint.

## Still blocking the cut

- **S3 hole diameter and board outline** — the contradiction in `components.md`. Without it the
  bosses cannot be placed, and that is v2's main purpose.
- **Which edge the power board's wires exit** — decides whether the board needs rotating 180 in Y,
  and whether the spacers need to clear a connector.
