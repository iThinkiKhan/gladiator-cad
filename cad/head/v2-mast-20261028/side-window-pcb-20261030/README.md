# Masthead v2 - head distro perfboard in the screen-frame side window (DRAFT, 2026-10-30, Claude)

Jim: use his own perfboard (30 x 70, or 20 x 80, cut to length) in "the open window between the two legs" of the
screen holder, on the side away from the camera. This replaces the yoke-floor pocket idea (`../pcb-floor-20261030/`);
the yoke goes back to the Codex balanced yoke (no pocket, full floor). The pan-lead window (neck + tube) is kept.

Open **`Gladiator_Head_v2_Side_PCB_REVIEW.FCStd`** (colored; desktop icon "Gladiator Masthead v2 - side PCB").

## What is modelled

- **Window (measured from the CAD):** between the screen frame's two side rails, 24 tall (Z 235.5..259.5) and about
  50 long (from the camera-carrier plate at Y 90.9 to the screen bezel at Y 140.5). Rails are plain 4.5 x 9.5 bars.
- **Board:** Jim's 30 wide perfboard cut to **55 long**, on the outside face of the rails, centred on the window, so it
  laps 3 mm onto each rail. Solder side against the rails, parts facing out.
- **6 mm hole in the board on the tilt axis**, 21.5 mm from the camera-end edge and 15 mm from the bottom edge: the
  screwdriver to the tilt horn screw goes through it (the window is that path today).
- **Two printed clamp bars** (magenta), 55 x 9.5, 4.6 thick, each with a rebate that grips 3 mm of the board edge.
  M2 x 8 screws through each bar into **4 M2 heat-set inserts in the frame rails** at Y 97 / 141, Z 229.5 / 265.5
  (2.8 bore, 4 deep, 3.5 mm in from the rail's outer edge). Drill them into the printed v06 frame (the bars line the
  holes up), or reprint the frame from `stl/Rear_Display_Frame_v06_with_side_PCB_inserts.stl`.
- The board rides with the head, so the camera, screen and ToF leads to it never flex. The trunk (5V, GND, SDA, SCL)
  crosses the tilt joint to reach it: give it a service loop close to the tilt axis.

## Checks (CAD, validation.json)

- Board, bars and a 20 mm deep parts envelope on the outer face: no overlap with anything at home; clear of the yoke,
  tilt servo and pivot at every tilt -38..34; clear of the fixed side at pan -20..180 with the head at -38, 0 and 34.
- Screwdriver path to the tilt horn screw: clear through the 6 mm hole.
- Insert bores sit in solid rail; frame stays one valid solid; bar STLs closed and manifold, print outer face down, no support.
- Mass estimate: board 4.8 g, bars 4.3 g, parts and leads ~6 g, centred 6 mm behind the tilt axis (screen side), so it
  slightly offsets the camera-heavy head.

## Not verified

- Nothing printed. The 3 mm lap on each rail and the bar rebate fit are untested; the window size comes from the CAD
  of the v06 frame, not a caliper.
- Trunk route and service loop across the tilt joint not modelled.
- Hole positions in the cut perfboard are Jim's to set; only the 6 mm access hole position matters.

## Print / hardware (this option)

- `stl/Side_PCB_Clamp_Bar_Top.stl`, `stl/Side_PCB_Clamp_Bar_Bottom.stl` (new, any colour).
- 4 x M2 heat-set inserts + 4 x M2 x 8 screws.
- Neck and tube with the pan-lead window: `../pcb-floor-20261030/stl/Gladiator_Head_v2_Neck_Main_PanLead.stl`,
  `../pcb-floor-20261030/stl/Gladiator_Head_v2_Mast_Tube_v2_PanLead.stl`.
- Yoke: the v2 yoke (`../stl/Gladiator_Head_v2_Tilt_Yoke.stl`), NOT the pocketed one in `../pcb-floor-20261030/stl/`.

## Files

`build_side_pcb.py` (freecadcmd) -> `Gladiator_Head_v2_Side_PCB.FCStd`, `stl/`, `validation.json`.
`style_side_pcb.py` (xvfb-run -a freecad) -> `Gladiator_Head_v2_Side_PCB_REVIEW.FCStd`.
`render_side_pcb.py` (freecadcmd, then python3 ... draw) -> `side_pcb_review.png`.
