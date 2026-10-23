# Project Decisions

Record accepted design decisions here when they are useful across sessions or
agents.

Use dated entries and include the reason or evidence behind the decision.

Do not record brainstorming or unaccepted proposals as decisions.

## 2026-10-15 - deck v3, one insert per rail, real 20 mm driver standoffs

Jim (chat): one heat-set insert on each rail for the deck; build the new deck; re-use the printed motor (driver) mounts and the mast; the driver mounts carry 20 mm standoffs (the CAD wedge model, build_drv_v5.py, uses
STANDOFF = 15, provisional); chamfer any hole that prints on the glass bed. Applied: cad/upper-deck/v3-20261015 (derived from the master deck; peg slots, slotted retention holes at (14|65, 83.5), wire holes, bed-side chamfers),
pegs moved onto the rails (the deck prints top-up), enclosure v2.3 with boards and fins shifted 5 mm along their normals, shoulders widened 4 mm, apertures cut as the swept path, chamfers on bed-side holes in the shell and switch enclosure.
Not decided: wire-hole positions (my placement), real standoff measurement, deck stiffness.

## 2026-10-15 - arch rails and switch enclosure

Jim (chat): nuts secure the rail feet; PETG will be used once a design is final; the portal rails still look like bridge towers, so use a geometric, strong, slim design (he suggested an arch with
mount points); the power switch must not sit in a 'hallway': a separate enclosure with an open rear for wiring that bolts securely to a mount point on the rails or on the body.
Applied as DRAFTS: cad/rails/v4-20261015 (elliptical arch, 8 x 6 mm band, peg-socket deck seat, shell hard points, right-rail switch shelf), cad/switch-enclosure/v1-20261015, enclosure v2.2.
Not decided: deck v3, retention (gravity or one slotted screw per rail), arch proportions, switch pin pitch and rating.

## 2026-10-14 - frame architecture: deck seats in the rails, shell is optional, switch on the frame

Jim (chat, with photos X:/Projects/Gladiator/V1 Complete): the foot screws all align but are hard to reach; the six upper-deck screws almost never line up at once, so the
upper deck should SIT IN the rails like the power board tray sat in its feet; the body is an optional add-on on hard points; charging may remove battery changes;
the power switch must be usable and mounted with or without the shell. The deck, board, mast and head already lift off the rails as one unit.
Applied as a DRAFT: cad/rails/v3-20261014/ (rails with peg sockets, hard points, wire ports, switch arm) and enclosure v2.1 (hood bolted to the rail hard points).
Not decided: deck v3 (pegs, wire holes), retention (gravity only or one slotted screw per rail), rail width, switch pin pitch and rating.

## 2026-10-14 - power switch on the body exterior (SUPERSEDED by the entry above: the switch is now frame-mounted)

Jim (chat): the switch holder is too insecure to operate through a cutout; mount the switch on the exterior of the body instead. Applied in enclosure v2: housing and removable bezel
on the front face of the front-right panel (cad/enclosure/v2-20261013/). Open: switch current rating, pin pitch, inline connector on the leads, ON-up marking.

## 2026-10-14 - antenna mounts: nothing recessed around the nut or flange

Jim (chat): the previous antenna design (master `AntennaPost`: O11 x 4 mm round pocket on the connector side) recesses the connector too much and is too difficult
to turn and tighten; the improvement applies to every antenna mount. Applied to enclosure v2 (rear wall mount) and to a replacement pylon, cad/antenna-pylon/v3-20261014/.
Rule: 2.0 mm land (SMA clamp limit about 2.2), flat on both faces, open flat zone of radius 11 mm around the axis, stiffness from ribs/spokes that start outside the zone.
Not validated on a printed part yet.

## 2026-10-13 - enclosure v2 direction

Jim (chat): the primary aim is to hide the wiring; the heatsinks stay exposed as a styled, efficient feature; let the INA226
poke out and work it into the look (wires will be routed); the S3 status light needs a light pipe or window; fix the antenna mount;
the open top shown in his photo is the working space the body must enclose; build v2. Evidence: the chat, and the concept review in
cad/enclosure/v2-20261013/README.md. Not decided: LED position, final panel attachment hardware after a trial fit, material.

## 2026-10-09 — mast end is FRONT

Jim: "we have been using the mast as REAR, and I want it to be FRONT"; update
notes, CAD, and firmware. Keep CAD coordinates and physical wiring fixed.
Current frame +Y forward, +X right, +Z up, rear-left origin; logical tracks
swap and both reverse polarity. Known chassis yaw rebase is180 degrees, not
a new IMU calibration. Mapping and mechanical limitations: ../ORIENTATION.md.
This decision does not approve new deck machining, mirrored print parts, or
a centered head-travel redesign. Earlier dated directional labels are historical.

## 2026-10-03 — round-3 coupons: screen pocket and sideways nut pocket

Evidence is in `measurements/mast-head.md`, "Round-3 coupon results".

- **Display frame pocket (R3a): Jim, "Screen is a good fit".** Keep the 62.5 x 29 board with 0.3 pocket clearance.
  Window alignment and the M2 corner pilots were not explicitly reported.
- **Sideways M3 nut pockets (R3b): the 1-notch 6.0 AF pocket.** Jim, "the sideways nut block fits 1".
  Matches the NUT_AF = 6.0 already in `build_head_v04.py`; no change.
- **GH44 receiver register: cut through the plate, not a recess.** R3c printed the 1.6 deep recess about 1 mm shallow
  facing the bed (Jim, eyeball; cause unconfirmed, roof sag suspected). Jim chose the through-window from four options.
  Carrier key and outline unchanged. Jim declined a confirming coupon ("we dont need to spend plastic on that"), so the
  through-window is unproven until PLATE3 prints; the check is the same drop-in of the blank carrier key.

## 2026-10-01 — head v0.4 design inputs settled by the round-2 coupons

Evidence is in `measurements/mast-head.md`, "Round-2 coupon results" and "follow-up answers".

- **Neck collar key: the 1-notch version, 0.10 clearance to the mast flat.** Jim: "Just go with
  one." Re-tested by feel after he first reported the opposite, and it matches the printed solids.
- **M3 captive-nut pockets: 6.0 across flats modelled.** H5, "perfectly".
- **Pulley spacing: a tension slot about 2.5 mm long centred near 39.7.** The belt was tightest
  about midway up a 37.5-42.0 slot (an eyeball position).
- **Drive: 60T on the servo, 40T on the head**, and the 2-notch groove, from the 09-22 work.
- **Pan servo drawn from the real numbers**: spline top 32, case boss top 28.5, ear underside 17.5,
  body 22.7. The old 13.2 and 8.3 are not used.
- **Settled later the same day by the final coupon plate (Jim):** spindle post **20.05** (H3b, "two
  notch post wins"); M2 thread-forming pilot **2.35** (H4b, "right in the middle between 1 and 2");
  horn pocket clearance **0.15**, the snug one (H6, "one notch horn pocket").

## 2026-09-30 — the printed v2 mast tube is the mast

Jim: "the taller v2 tube. We are not buying a tube, drop that." The v2 tube (top Z 130, from
`cad/build2-20260927/`) is on the robot. The earlier suggestion to buy a Ø20/Ø12 aluminium or
carbon tube is withdrawn from `docs/print-plan.md` and `docs/GLADIATOR_DESIGN.md`. The head
designs to this tube. Its index flat was checked against both the master and the printed STL:
0.9 deep, 8.0 wide, on the rear, running 15 down from the top.

## 2026-10-21 — Round 5 styling, original structural CAD preserved

Jim selected curved scuta and a lightning-bolt aquila from the styling guide, requested firmly mounted insets and a more detailed eagle, and authorized adaptations needed to make the CAD work. The implementation must remain a separate version and preserve the original CAD and existing structural/fit interfaces. Review implementation: cad/v2/enclosure/round5-20261021/. New insert calibration and physical accessory testing are not accepted results.

## 2026-10-22 — SD card and Jim's SAFE/material presets

Jim confirmed these prints will run from SD card and explicitly requested his EnderNeo SAFE settings and the separate silk filament settings. Use full inherited presets, preserving the SAFE start-code checker; apply necessary layer/support/orientation changes per plate. The incoming M2 inserts have not been measured yet; no bore or retention result is accepted by this decision.


## 2026-10-22 - Round 5 calibrated M2 bores and print status

Jim accepted the coupon 2.8 mm M2 heat-set bore and requested all affected CAD/prints updated. Decorative tablets and red shields/crest are printed; silk remains, and the white insets need reprinting using the stronger v2 (plate 04B). Keep Neo SAFE and separate silk profiles, SD/LCD colour pauses. LED window remains open; cover is optional. No additional LCD diagnostic is required by Jim. Production derivative: cad/v2/enclosure/round5-calibrated-28-20261022/. Earlier structural geometry and insert sizes remain preserved.


## 2026-10-22 - Keep both front panels together; preserve structure

Jim: print both front panels at once, save time without compromising structure, with all day tomorrow available for shells. Single-panel variant is optional. Implemented only a panel support-layout change; all model geometry and structural extrusion settings retained. Current combined shell package is in the calibrated derivative shell-time-optimized/.
