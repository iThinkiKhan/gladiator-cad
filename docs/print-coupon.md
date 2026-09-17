# Fit + calibration coupon v1

`cad/coupons/Gladiator_FitCoupon_v1.stl` — 80 x 52 x 11 mm, ~25 g, prints flat with **no support**.

One print answers the questions that would otherwise be answered by scrapping a rail or a deck.
There are 16 heat-set insert bores across the rails and the upper deck, worth about 133 g of
filament between them, and all of them ride on one unverified number.

## What is on it

Features are identified by the row of **small round pips** next to each one — count them.

| Pips | Feature | Nominal | What it tells you |
| ---: | --- | ---: | --- |
| 1 | Insert boss | bore **4.0** | Heat-set insert fit. Bosses are 9 dia x 6 tall on 4 of plate, bored 7.5 deep leaving a 2.5 floor — **identical to the real deck bosses**, which are the tightest case in the design. |
| 2 | Insert boss | bore **4.2** | |
| 3 | Insert boss | bore **4.4** | This is what every part currently uses. |
| 4 | Insert boss | bore **4.6** | |
| 1 | Spigot peg | **13.6** dia | Try these in the **real aluminium deck's 14.0 tower hole**. The mast base's spigot is 13.8 and drops through with only **1 mm to the motor** underneath — worth knowing before printing MastBase. |
| 2 | Spigot peg | **13.8** dia | Current design value. |
| 3 | Spigot peg | **14.0** dia | |

Unpipped features, left to right, smallest first:

- **M3 clearance holes** — 3.2 / 3.4 / 3.6 through the full 4 mm (the deck's thickness). Design uses 3.4.
- **M2 clearance holes** — 2.2 / 2.4 / 2.6. Design uses 2.4.
- **Rail foot slot** — 3.4 wide with 3.0 of travel, exactly as built into the rail feet. Check that an
  M3 screw passes *and* that an M3 nut sits under it, and that it actually slides.

## Using it as printer calibration

The plate's own outline is the reference — **80.00 x 52.00 x 4.00** is a longer, more sensitive
baseline than a 20 mm test cube.

Measure both of these, because **they will not match**, and the difference is the useful part:

1. **An outside feature** — the plate's 80.00 and 52.00, and the peg diameters (13.60 / 13.80 / 14.00).
   Outside features usually print **oversize** by roughly 0.05–0.2 mm.
2. **An inside feature** — the clearance holes (3.20 / 3.40 / 3.60) and the bores.
   Holes usually print **undersize** by a similar amount.

Knowing both numbers separately is what lets you pick a nominal for every other part on the robot,
rather than guessing. If, say, your holes come out 0.15 small and your pegs 0.1 large, then the
4.4 bore is really behaving like a 4.25 and the 13.8 peg like a 13.9.

Measure the plate near its **top face**, not at the bed. The first layer squashes out (elephant's
foot) and will read a few tenths over regardless of how well the printer is calibrated.

## Reading the results

- **Insert bores** — heat an insert into each. The right one pulls in square, sits flush or a hair
  proud, and does not split the boss or push a bulge out the side. Too tight splits it; too loose
  spins under torque. Note the winning number.
- **Pegs** — the right one enters the aluminium hole with light finger pressure and no rock. If 13.8
  is tight, that is your printer running oversize on outside features and it applies to every other
  outside dimension too.
- **Slot** — if a nut will not sit, the slot needs widening before the rails are printed, not after.

If the winning bore is not 4.4, tell me the number and I will change it in one place — it is a
single spreadsheet parameter (`rail_insert_dia`) feeding all 16 bores.

## PLA now, PETG later

Printing the first batch in PLA is sensible for fit checking, with three caveats.

- **Heat-set inserts run cooler in PLA** — roughly 200 C on the iron versus 240–250 for PETG. PLA is
  less forgiving: let the insert sink under its own weight rather than pushing, or it will bulge the
  boss.
- **Reprint this coupon when you switch to PETG.** PETG shrinks more than PLA, so holes tend to come
  out tighter and the winning bore may well be a size up. It is 25 g to re-check and it protects the
  real parts again.
- **PLA softens around 60 C.** Fine for fit-checking and for driving gently, but the rails and deck
  sit near the motor drivers and the battery, which is exactly why the design specifies PETG. Do not
  treat PLA structural parts as final.

## After this, print in this order

1. **One side rail** — easiest print in the set (on its outboard face, 12 mm tall, ~159 mm2 of
   support) and it bolts straight to the real aluminium deck, so it tests the insert bores and the
   slot alignment against hardware that cannot be adjusted.
2. **Mast base** — small, and it proves the spigot and the 1 mm motor clearance.
3. Second rail, then the **upper deck** (now prints flat with zero support).
4. Antenna mount, power shield.

Not yet: the **mast tube** (buy a 20/12 aluminium or carbon tube instead — printed vertically its
layer lines run perpendicular to the bending load), the **driver mounts** (check the 2.7 self-tap
holes against a real board first), and anything under **`HeadCandidate_v01`** (that interface is not
frozen).
