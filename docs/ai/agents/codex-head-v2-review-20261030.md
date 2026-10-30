# Masthead v2 design review - 2026-10-30 (Codex)

User direction: retain the original slotted mast tube for now. Closed-tube work is a retained alternative only. This review changes no CAD geometry, firmware, or print files.

Sources: cad/head/v2-mast-20261028/README.md, make_v2.py, v2_tail.py, validation.json, scripts/build_head_v2_mast.py, and the saved Gladiator_Head_v2_Mast.FCStd. Frame per docs/ORIENTATION.md. Findings below distinguish verified CAD facts from suggested changes.

## Verified findings and proposed improvements

1. **Tensioner screw reach:** lug thickness 7 mm and initial pad gap 0.5 mm, increasing to 10.5 mm at C48. Required under-head reach is 7.5 mm at C38, 13.5 at C44, and 17.5 at C48. The specified M3x16 cannot bear on the pad at the final 1.5 mm of carriage travel (maximum theoretical C46.5). Consider M3x20 or a recessed/thinner lug, then model screw, head and nut throughout travel; these hardware solids are absent from the saved assembly. A longer screw requires an envelope check at the retracted end.

2. **Tilt balance:** existing CAD estimates put ~104.9 g of tilting parts 21.6 mm toward the camera from the tilt pivot, unchanged by the whole-head 26 mm rearward relocation. Estimated level holding moment remains 0.227 kg cm. Recommend moving payload mass toward the pivot using a revised or adjustable receiver/carrier interface, rather than adding counterweight or extending the screen. Any adjustment needs renewed collision, optical and wire checks. These masses are estimates, not scale readings.

3. **Cable choke at yoke:** despite the 12 mm mast bore, the floor opening is a partial circular cut, starting 0.8 mm to one side of a radius-6.5 bore. In the saved yoke a 5.7 mm round vertical gauge at world X43.15,Y113 clears its floor; 5.8 mm overlaps by 0.335 mm3. This is nominal CAD clearance with no print allowance, not a confirmed connector fit or whole-harness capacity. Enlarge/reshape the yoke passage if feasible and add rounded exits, defined fixed/moving strain relief, and separate controlled pan/tilt loops. The collar bolt crossing the bore also remains a wiring consideration with the slotted tube.

4. **Pan indexing:** source HEAD_TRAVEL is -20..180 deg in the legacy frame. As documented in ORIENTATION.md, robot-forward is pan180, an endpoint. Recommend a separately checked mechanical indexing change to put useful scanning travel on both sides of forward; do not simply expand software limits. Present collision and harness checks do not approve a new interval.

5. **Purposeful tilt stops and yoke roots:** current saved sweeps are clear at 38 deg up and 34 down, with first sampled contact at 40 up (receiver/yoke) and 36 down (camera tray/yoke). Consider dedicated stop features carrying load into the receiver/yoke rather than letting the camera case become the stop. Narrower columns gained tilt clearance but make fillets/gussets at their roots worth investigating outside the swept volume. No strength analysis or physical stiffness finding is claimed.

Priority: correct screw reach as a small mechanical fix; improve payload balance and wire routing before freezing the next head print. Pan indexing is a useful functional improvement that deserves its own full motion/harness review.
