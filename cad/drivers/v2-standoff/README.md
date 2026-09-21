# Driver mount v2 — board on standoffs, GPIO face inboard

Built 2026-09-20. **A design candidate, not a print release**, and the master is
untouched — confirmed by the SHA-256 pair in `validation.json`.

The board no longer bolts flat against the mount. It floats on four M3
male-female standoffs, so the mount's only job is to present four boss tops at
the right points in space and get that load into the deck.

## Why this is the better joint

The number from the foot work: a screw pulled to 0.4 N·m develops about **667 N**
of preload, and preload is what threatens PLA — not the terrain.

With a male-female standoff the joint you actually torque is the board screw,
and it lands in the standoff's own metal thread. The PLA only ever sees the male
stud, done up hand-tight into a heat-set insert. **The preload never reaches the
plastic.** Bolting the board straight to the mount, inserts or not, does not have
that property.

## What changed, measured

| | v1 | v2 |
| --- | ---: | ---: |
| Board face | bolts flat to the mount | floats on standoffs |
| GPIO / component face | outboard | **inboard** |
| Heatsink | inboard, through the window, clipping the upper deck | **outboard, free air** |
| Fin tip vs the track line | **3.4 mm proud** | **4.2 mm inside** |
| Material around each insert | 0.75 mm | **2.0 mm** |
| Bearing on the deck | 342 mm² | **776 mm²** |
| Volume | 33.4 cm³ | **22.4 cm³** |
| Relief pockets | 2 mm, for the solder tails | gone — the standoff gives that clearance |

Sampled checks: single valid solid; **zero clashes** against upper deck, both
rails, chassis deck, battery box, mast, mast base, power shield, antenna post,
S3 and breadboard; all four standoff axes clear between boss top and board.

## The structure

Moving the board 12 mm inboard and standing it off 15 mm retreats the boss plane
a long way inboard, and that is what makes the mount compact:

| Boss | Global position | Supported by |
| --- | --- | --- |
| inboard-high pair | X 12.12, Z 71.52 | short rise off the foot, directly beneath |
| outboard-low pair | X −7.63, Z 37.31 | skirt hanging just outboard of the deck edge |

The old mount had to reach out to X −37. This one does not leave X −11.5. The
foot also grows outboard from X 6 to X 0, the real deck slab edge, which is where
most of the extra bearing comes from.

## Parameters

`STANDOFF_LEN` is free — stacking standoffs makes any length available, and
changing it moves the **bosses**, not the board. `BOARD_OFFSET` is what is fixed,
because it is set by track clearance.

`BOSS_OD` 9.0 and `BOSS_BORE` 4.6 are the deck's own proven geometry — the joint
where the insert coupon showed an insert could not be pulled back out.

## Not done yet — do not print this

1. **Zero running clearance.** The deck and rail clearance cuts were taken at the
   obstacle's exact surface. `makeOffsetShape` was tried and produced a shape
   that did not fully contain the original, which left an 804 mm³ interference —
   worse than no offset — so it was backed out. A real clearance has to be added
   before this is a part.
2. **`STANDOFF_LEN` 15 is a placeholder.** The gap has to swallow the *plugged*
   GPIO connector and its wire bend, and that has not been measured.
3. **No rib or gusset design.** The spine is a plate with a rectangular window.
   The load path is better than v1 by bearing area and insert wall, but nothing
   here is a stress result.
4. **No print orientation.** Exported as-modelled.
5. The heatsink model is 32 wide across the cant and dead centre (both measured)
   and 28 proud (from `components.md`). Its fore-aft extent is still unmeasured,
   though with the fins outboard it no longer affects fit.
6. Track top height is still unmeasured. Jim's call to proceed without it.

## Relationship to the master

This does not touch `DriverMountLeft` / `DriverMountRight`. Those are live in the
master and `Gladiator_PlateG_MASTBASE-AND-DRIVERS.3mf` is queued with them. This
is a separate candidate so it can be reviewed and merged deliberately rather than
colliding with work in progress.

Rebuild: `scripts/build_drv_v2.py`, run with `freecadcmd` on the CAD server.
