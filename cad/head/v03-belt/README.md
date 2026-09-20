# Gladiator head v0.3 — corrected belt pan drive

Built 2026-09-19 from the v0.2 comparison candidate. **The v0.2 file and the saved
robot master are unchanged**, confirmed by the SHA-256 pair recorded in
`validation.json`.

The belt is kept — it is the right idea. What changed is everything that made the
v0.2 belt unbuildable: the ratio, the pulley geometry, the belt length, and where
the servo lives.

## What changed and why

| | v0.2 | v0.3 |
| --- | --- | --- |
| Drive ratio | 1:1, 50T / 50T | **1.5:1 step-up, 60T driven / 40T drive** |
| Servo travel needed | 180 deg, the full SG90 range | **133 deg**, its reliable middle band |
| Belt | 184 mm — not a stock length | **180 mm / 90T 2GT closed loop** |
| Shaft spacing | 42 mm | 39.745 mm, derived from the belt, not chosen |
| Pulley geometry | pitch cylinders and flange envelopes | **cut 2GT grooves**, printable |
| Driven pulley | separate hub, nothing to fasten it | **integral with the pedestal** |
| Servo position | 34–36 mm behind the chassis rear edge | **forward-left at 225 deg, 41 mm inside it** |
| Bearing centres | 11 mm apart | **16 mm apart**, no height change |
| Rotor seat / spindle | 32.20 / 19.90 mm | 32.10 / 19.95 mm |
| Retainer bore | 26 mm — rubs the fixed inner race | **29 mm**, bears on the outer race only |
| Pan travel | 0..180 deg | **-20..180 deg** |
| Hard stops | printed posts at -15 / 195 deg | **removed** — see below |
| FOV check | pan = 0 only | **swept across the whole travel** |
| Servo body in collision checks | rotated with the drive | **fixed**, which is what it actually is |

### The ratio was the real flaw

A 1:1 belt asks the SG90 for a full, repeatable 180 deg with hard stops 5.44 deg
outside it. Usable SG90 travel is typically 160–180 deg and varies unit to unit.
Fall short and the screen never squares up; overshoot and a plastic lug is driven
into a plastic post.

At 1.5:1 the servo swings 133 deg for 200 deg of head travel. Torque at the head
drops to about 118 mN·m, against a pan axis carried on two bearings — far more than
the friction, cable torsion and inertia need. Head resolution becomes roughly
1.5 deg per servo step.

**RATIO, the tooth counts and HEAD_TRAVEL are parameters at the top of the
generator.** Measure the servo, change the numbers, rebuild.

### The servo moved off the back

v0.2 put the pan servo and drive pulley 34–36 mm behind a 140 mm deck, at head
height, on the most collision-prone face of a robot whose sensors point the other
way. Because a belt decouples the servo from the pan axis, it does not have to be
there. It now sits forward-left at 225 deg local, fully over the deck, carried on a
C arm that passes **below** the rotor at Z 114.5–120 and outboard of it.

225 deg rather than straight ahead is deliberate: it holds the arm sweep to
135 deg, which leaves the clamp cap's sector open. Straight ahead would need a
180 deg sweep.

Everything above Z 144 is untouched, so the tilt axis stays at Z 205 and the whole
tilt, carrier and screen assembly is inherited from v0.2 unmodified.

### Why there are no printed hard stops

A post at the travel limit has to sit at a radius the C arm does not reach, and a
printed lug driven into a printed post is a worse failure than a servo reaching its
own internal limit. Travel is held by the servo end stops plus firmware limits. If
a hard stop is wanted later it belongs at the drive pulley, next to the fixed
platform, not around the pan axis.

## Checks

`validation.json` records: 12,197 head part-pair pose tests and 33,948 head-to-robot
tests at 5 deg pan steps across the full -20..180 range with tilt at -25 / 0 / +25,
**zero collisions**; the nominal 60x60 deg ToF frustum swept across the same range
with **zero intersections**; an 11.9 mm test cylinder clear through the 12 mm cable
passage; every active part a single valid solid; and both source hashes unchanged.

These are sampled rigid-solid checks. They do not prove clearance between samples,
nor cable behaviour, servo travel, tooth mesh, print fit, stiffness or strength.

## Buy this

| Item | Spec | Note |
| --- | --- | --- |
| Pan bearings | **2 x 6804 (20 x 32 x 7)** | Buy 4. Load is a non-issue — the design uses about 1% of the rating. Seal drag is under 10% of the servo torque budget, so 2RS or ZZ are both fine; buy on price. |
| Belt | **2GT closed loop, 90 teeth / 180 mm, 6 mm wide** | Buy it, do not print it. A printed TPU belt has no glass cords, so it stretches under tension and that stretch becomes pointing error on an open-loop servo. |
| Drive pulley | **40T 2GT, 6 mm belt width** | Bought. Tooth accuracy matters most on the small pulley. Bolts to the supplied SG90 horn — do not print a spline. |
| Driven pulley | none — printed, integral to the pedestal | Gate on the mesh coupon first. |
| Circlip | Ø20 shaft external | Groove is at Z 144.5, 1.4 mm wide. |

The bearings are safe to order now; they are unaffected by the ratio decision. Hold
the belt and pulley order until the servo travel is measured, because a different
ratio changes both.

## Print this, and only this, for now

`stl/Gladiator_HeadCoupon_BeltMesh_3up.stl` — three 60 deg arcs of the driven
ring side by side, 48.4 x 18.1 x 6 mm, 1.79 cm3 total, a few minutes.
**Use a brim**: each piece has only ~100 mm2 of bed contact, less than the mast
base that already needs one.

**One question: which groove width meshes with a real 2GT belt?** Depth is held
at the 2GT nominal 0.75 mm on all three, so width is the only variable. The
scallop count on the inner face identifies each — 1 is narrowest:

| Scallops | Groove radius | Width at OD | Tooth land at OD |
| ---: | ---: | ---: | ---: |
| 1 | 0.60 | 1.162 | 0.812 |
| 2 | 0.65 | 1.285 | 0.689 |
| 3 | 0.70 | 1.396 | 0.577 |

Press a length of belt into each arc. You want the one where the belt seats
fully to the root, does not ride up on the tooth tips, and does not rock
sideways. Note that the tooth land is the thinnest printed feature here — at
0.58 to 0.81 mm it is one to two extrusion widths on a 0.4 mm nozzle, so if a
variant fails, check whether the teeth came out mushy (a slicer resolution
problem) or crisp but the wrong size (a profile problem). Those need different
fixes.

The single-arc `Gladiator_HeadCoupon_BeltMesh_60deg.stl` is the 0.65 variant
alone, kept for reprinting one.

Do not print the pedestal until one of these passes — the pedestal is 20 cm3
and its teeth come from the same code.

The other STLs are exported **in their as-modelled orientation, which is not a
validated print orientation.** They exist so the geometry can be inspected and
sliced for fit checking, not as a print release. A real plate layout comes after the
coupons, the way `docs/print-plan.md` does it for the body.

## Still open

- Servo usable travel — unmeasured, and it sets the ratio.
- Bearing seat 32.10 and spindle 19.95 mm are nominal clearances, not print-verified.
  They need their own coupon once the bearings arrive.
- Belt tension and tensioning method are not designed. Centre distance is fixed.
- The harness. About 14 conductors must pass the 12 mm bore and twist over 200 deg.
  Flat ribbon rather than a round bundle, with a defined free length anchored top and
  bottom.
- Screen active window, mount holes and connector exit remain unmeasured, so the
  bezel opening is still the whole-board rectangle.
- The mast index flat is still the inherited 0.9 mm feature. The deeper blind dimple
  and grub screw proposal would be a change to the real master and **was not made
  here**.
- No load, stiffness, creep or payload rating is claimed.

## Rebuild

`generator/build_head_v03.py`, run with `freecadcmd` on the CAD server. It opens the
v0.2 file read-only and writes only this directory.

## Calibration gap — every fastener hole in v0.3 is at nominal

Found 2026-09-20. The head candidates were built on 2026-09-16 and 09-17.
`measurements/printer-calibration.md` landed on 09-18 and was applied to the
master only. **The head never inherited it.**

On this printer, round features print about 0.25 mm under, and the fit coupon
established that a modelled 3.4 and 2.4 will not pass an M3 or M2 screw at all.
So as it stands:

| Feature in v0.3 | Modelled | Calibrated value | Effect if printed now |
| --- | ---: | ---: | --- |
| Mast clamp bolts | 3.4 | **3.6** | M3 will not pass |
| Pedestal to tilt yoke | 3.4 | **3.6** | M3 will not pass |
| GH44 carrier screws | 3.4 | **3.6** | M3 will not pass |
| Servo ear screws | 2.4 | **2.6** | M2 will not pass |
| Pedestal / retainer M2 | 2.2 | **2.6** | M2 will not pass |
| Bearing seat in the rotor | 32.10 | pending plate E | prints ~31.85, bearing will not enter |
| Spindle post on the neck | 19.95 | pending plate E | prints ~19.70, bearing will be loose |
| Rotor M2 self-tap pilot | 1.6 | pending coupon C | unknown |

Nothing here changes design intent — the intent is still an M3 clearance, an M2
clearance, and a firm bearing seat. These are compensations for how this printer
prints today, exactly as the master's `deck2_screw_dia` and `m2_screw_dia`
already are.

**All of it is applied in the same rebuild as the belt ratio**, so the head is
rebuilt once rather than three times. Until then, treat every STL in `stl/` as
geometry for inspection only.

The GH44 fit coupons in `cad/head/v01/fit-prototypes/` carry the same 3.4 holes.
That does not invalidate the coupon — it tests the register, the indexing and
the seating, none of which depend on the screw holes — but expect the four M3
holes on it to need a drill.
