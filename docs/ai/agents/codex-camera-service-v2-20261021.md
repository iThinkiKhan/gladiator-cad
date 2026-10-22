# Camera service v2 — 2026-10-21
Jim requested a redesign because the fitted camera cover falls off and Duponts are difficult to thread.
Source on cad-lab: scripts/build_esp32_cam_case_v4.py and cad/head/esp32-cam-case-v4/ (untracked prior work, preserved).
New isolated review folder: cad/head/camera-service-v2-20261021/.
Two printed parts; 2 x M3x12 and side-loaded M3 nuts replace four plastic-threaded M2 cover screws.
Both side slots open to the cover seam; cover skirts close after pre-wired board insertion; exit height 4.5.
Two rear-lug tie passages; chamfers on floor/skirt wire-contact edges.
Camera/cradle shifts head-local +X by 1.5 mm for 2.275 clearance to the ToF frame. Original three carrier mounting holes remain; screwdriver scallops preserve access.
Current robot-facing view is legacy pan180. Existing travel and robot orientation are unchanged.
Checks: 16 connectors/wire lay-in paths, board insertion/cover removal, board/case/driver/SD/field clearance, 231 sampled pan/tilt poses and 51 fine tilt poses.
Independent saved-file checks: native reload, STEP equality, watertight STL/solid reconstruction, mesh volume, installed wire paths versus head context, fasteners and 1071 hardware-motion poses.
Review draft: actual connector dimensions/bend radius, skirt fit and M3 hardware remain unverified. Wires stop just outside the case openings; full route to mast not modeled. Board retention still depends on cover corner posts.
No existing CAD, print plates, printer queue, servo or firmware changes. No print started. No Git commit or push.
Desktop launcher: Gladiator-Camera-v2.desktop. Local mirror: X:/Projects/Gladiator/camera-mount-v2-20261021/.
