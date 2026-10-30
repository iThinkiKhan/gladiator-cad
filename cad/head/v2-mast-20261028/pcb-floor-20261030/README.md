# Masthead v2 - head distro PCB on the yoke floor + pan servo lead into the mast (DRAFT, 2026-10-30, Claude)

Jim: "I want a pocket for the board to sit in, with a channel under it for the servo wire."
Base: Codex balanced derivative (`../balance-tensioner-20261030/Gladiator_Head_v2_Balanced.FCStd`, SHA256 in validation.json).
Changes `Tilt_Yoke` (PCB floor), `Neck_Main` and `Mast_Tube_v2` (pan lead window). Open **`Gladiator_Head_v2_PCB_Floor_REVIEW.FCStd`** (colored) in FreeCAD.

The board outline is a PLACEHOLDER until the PCB is designed; change `OUTLINE`/`INSERTS` in `build_pcb_floor.py` and rebuild.

## What is modelled

- **Pocket:** board seat 1.0 deep in the yoke floor frame (floor top Z 204.5), 0.3 wall clearance. A 1.6 mm board sits
  with its top 0.6 above the floor.
- **Lead relief:** a 1.5 mm well under the board (1.8 mm ledge round the edge) for trimmed through-hole leads and solder.
  Where the floor frame is already open, the pedestal top plate is 3.0 below the board.
- **3 x M2 heat-set inserts** (A front-left, B and C on the right bar), 2.8 bore through the 3.0 mm left under the seat.
  The pedestal top plate below is the backstop: fit the inserts before bolting the yoke down. M2 x 4 screws.
- **Tilt servo lead channel:** 4 x 3 mm, from the open floor in front of the ear column, under the board edge, into
  the wire passage over the pan bore. The lead comes down the front face of the ear column (blue in the file).
- **Board outline (placeholder), about 23 x 29.5:** stepped front (the camera case sweeps low at the front right), notched
  round the M3 yoke bolt head and the screwdriver hole to the pan retainer screw.
- The trunk (5V, GND, SDA, SCL) comes up the wire passage under the board and is soldered to it.

## Checks (CAD, validation.json)

- New yoke: one valid solid; print STL `stl/Gladiator_Head_v2_Tilt_Yoke_PCB.stl` closed and manifold, floor on the bed,
  no support, 14.9 g solid PLA (was 15.6).
- Board, inserts, lead and yoke bolt head: no overlap with anything at home.
- Tilt -38..34 every 2 deg: board and lead never touched by the head. Pan -20..180: nothing touches the fixed side.
- Tallest parts allowed on the board (clears every tilt pose; yellow zones in the file): front-left 8 mm,
  front-right 10 mm, connector band (Y 109.5..118.5, under the tilt pivot) 30 mm, rear strip 6 mm.

## Not verified / watch

- The floor cross bar between the two yoke columns loses about 57% of its material (pocket + relief). The columns stay
  bolted to the solid pedestal top plate right at their feet, and the front bar is untouched, so it should hold, but it
  is not strength-checked. The screwed-down PCB stiffens it again.
- Not printed. Insert fit in a 3 mm through-bore (insert length 3.0 nominal) is untested.
- The real PCB outline, connector positions, trunk solder pads and lead lengths do not exist yet.

## Pan servo lead into the mast (Jim: "Yes, pan window")

The SG90 lead leaves the servo end that faces the mast, low down (Jim's v1 photo). It now drops off that end, runs in an
8.4 mm slot under the neck flange (open underneath, hidden below the servo), through a tunnel in the collar wall
(Z 145..148.6) and an 8.4 x 5.2 notch in the top of the mast tube, then down the bore with the trunk.
- Sized for the 3-pin Dupont plug pushed through flat (7.6 x 2.5): `plug_path_hits` empty.
- A 5.6 mm groove in the neck housing wall gives the lead room at the tightest tensioner setting (C38, servo end only
  1 mm from the wall). Lead envelope clear at C38, C44 and C48.
- The tube notch is on the servo side, away from the key flat, so it always lines up with the tunnel.
- Removed: 610 mm3 from the neck, 185 mm3 from the tube. Neck and tube still single valid solids; STLs closed.
- New print files: `stl/Gladiator_Head_v2_Neck_Main_PanLead.stl` (collar on the bed, supports as before) and
  `stl/Gladiator_Head_v2_Mast_Tube_v2_PanLead.stl` (upright, no support).
- Pictures: `pan_lead_review.png` (true CAD sections, `section_pan_lead.py`).

Watch: the plug still cannot pass the M3 head bolt lower in the tube (about 4.5 mm each side): feed the lead with the
bolt out, or re-pin the plug after threading. The 1.4 mm roof over the slot under the flange is thin; not strength-checked.
The pan lead stays separate from the PCB, as Jim wants (servos on their own circuit to the lower deck).

## Files

`build_pcb_floor.py` (freecadcmd) -> `Gladiator_Head_v2_PCB_Floor.FCStd`, `stl/`, `validation.json`.
`style_pcb_floor.py` (xvfb-run -a freecad) -> `Gladiator_Head_v2_PCB_Floor_REVIEW.FCStd`.
`render_pcb_floor.py` (freecadcmd, then python3 ... draw) -> `pcb_floor_review.png`.
`section_pan_lead.py` (freecadcmd, then python3 ... draw) -> `pan_lead_review.png`.
