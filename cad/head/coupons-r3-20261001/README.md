# Gladiator head coupons, round 3 (2026-10-01)

Three small checks, about 11 g in all, of things the released v0.4 head parts depend on that no
coupon has tested yet. Each answers one question. Plate:
`Gladiator_HeadR3_CouponPlate_3-pieces.3mf`. PLA, no supports, no brim, **do not auto-orient**.
Every dimension is copied from `scripts/build_head_v04.py`.

| Piece | Question | Protects |
| --- | --- | --- |
| **R3a** screen slice (the frame's lip and pocket only) | Does your ST7789 drop into the pocket, show its visible area squarely in the window, and take 4 x M2 screws from behind the board into the corner pilots? | the display frame (15 cm3). The hole-to-edge offset is **assumed** |
| **R3b** sideways nut block | Does an M3 nut press into a 6.0 pocket printed on its **side**? (1 notch = 6.0, 2 notches = 6.2) | the neck collar and the tilt pivot, whose nut pockets print sideways. H5 only tested pockets printed upright |
| **R3c** GH44 register, recess down | Does the key of your plate F blank carrier still drop into the recess, and only one way round, when the recess prints **against the bed**? | the GH44 receiver, which prints face down |

## How to test

- **R3a:** the small **notch in one long edge marks the PIN edge.** Lay the board face down into the
  pocket from the back, pins toward the notch. Look through the front: is the whole lit area in the
  window? Then 4 x M2 screws from behind the board into the corners. Report: fits / tight / where it is off.
- **R3b:** press an M3 nut into each side pocket by thumb. Report which one takes it and holds.
- **R3c:** drop the plate F blank carrier's key in. It should seat flat. Turned 180 degrees, it should not.

## Checks that need no print, using coupons you already have

1. **Circlip:** snap a circlip into the groove on the winning **2-notch H3b post**, over a bearing.
2. **Horn screw:** in **H6a**, does the horn screw's shank pass the 3.4 centre hole while its head
   sits on the plate?
3. **Horn height (the neck waits on this):** push the cross horn fully onto a servo spline and measure
   from the **underside of an ear** to the **top of the horn arms**. The model uses 13.25.
