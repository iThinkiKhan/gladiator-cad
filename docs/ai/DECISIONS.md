# Project Decisions

Record accepted design decisions here when they are useful across sessions or
agents.

Use dated entries and include the reason or evidence behind the decision.

Do not record brainstorming or unaccepted proposals as decisions.

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
