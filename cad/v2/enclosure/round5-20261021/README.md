# Gladiator Round 5 — separate styling model

Derived from the saved **enclosure v2.8, 21 October 2026**, in a new directory. The original native model, generator, exports and validation files are preserved byte for byte. `baseline-v28/` contains a frozen rebuild source. This folder is a CAD review package; it does not replace a print plate.

Open **Gladiator_Round5.FCStd** for the coloured assembly. `Gladiator_Round5_PrintParts.step` contains the printed parts in assembled coordinates; `stl/` contains individual print-oriented meshes. `build_round5.py` rebuilds the geometry on cad-lab; `verify_round5.py` checks the saved files independently. Read `independent-verification.json` for the completed checks.

## Round 5 implementation

- Grey enclosure with a red 12 mm roof cap and red belt at robot Z50–56. Native colour-region objects partition the exact shell volume for display. The hidden named shell objects and the manufacturing STLs remain single solids; colour regions are not additional print parts. Manual filament changes create the cap and belt.
- Two red **R28 curved scuta**, each 27.3 × 41.6, with separate pre-curved white winged thunderbolts and silk bosses. Each remains attached to its own removable panel. The white pattern has approximately 0.15 mm side relief and a 0.4 mm seating recess; it is made curved in CAD and does not depend on hot-water bending.
- Two white **GLADIATOR** tablets with raised red lettering and ansae. Each tablet has a locating pocket and two M2 screws. The single combined tablet mesh permits one face-up colour change at 1.5 mm.
- A sculpted rear **aquila clutching a fulmen**. Curved flight-feather outlines have tapered relief tops; the breast and head have rounded surfaces, with breast feather grooves, a recessed eye, hooked beak, talons, and four forked lightning strokes. A central M2 fastener and two hidden locating pegs retain it without large wing fasteners. The bolt strokes are 1.2 mm; eye diameter 0.7 mm and shallow grooves are optional fine detail rather than load-bearing features.
- Four rear lorica lips adapted around the **existing** vent slots. Slot position, width, height and airflow opening are preserved. The guide's uniform lame spacing was adjusted to accomplish this.
- Red galea crest, silk holder trim, and silk rear neck guard. New removable black clamps attach to the real receiver/carrier and display top edges; there is no fictional yoke top bar. Broad captive shoes spread clamp-screw force against the existing frame. All of these accessories move with the tilt group.

## Inset retention and preservation of fits

The original shell walls are not recessed or drilled. Locating seats and insert bosses are **added outside** them. The shields and tablets sit in real shallow exterior pockets; screws provide retention and clamping independently of their slip clearance. The aquila seats on broad support lands, with two concealed anti-rotation pegs and one screw. Shield boss screws capture the white emblems as well as the red fields.

This intentionally increases exterior projection compared with the guide's shallow pockets: tablet face 6.3 mm from the original skin; shield red spine 6.25 mm, white detail another 0.6 mm, with the boss above that; aquila backing 4.8 mm from the skin. Those offsets provide screw engagement while preserving all original wall material and interior space.

Original rail hard points, standoffs, roof tabs, seam screws, panel split, mast clearance, driver/heatsink apertures, speaker mount/grille, status window/light pipe, SMA land, switch cradle, and deck geometry remain unchanged. The main CAD bodies, mast and head are copied as read-only context. The separately reviewed camera service case is an extra clearance reference; this styling revision does not replace that case or alter its mounting.

The removal verifier authenticates the frozen v2.8 sweep evidence and replays the added material, badges and hardware at 1 mm increments against the old and new obstacles. It also checks the original moving solids against new obstacles. This reuses exact unchanged geometry rather than treating appearance partitions as physical panels. The hood's speaker and switch move with the hood.

## New hardware — provisional stock dimensions

| Hardware | Count | Use |
| --- | ---: | --- |
| M2 heat-set inserts | 13 | Seven body badge mounts; six head accessory mounts |
| M2 × 4 | 6 | Four tablet screws; two neck-guard screws |
| M2 × 5 | 3 | Crest clamp and two neck clamps, acting on captive shoes |
| M2 × 6 | 4 | Two shield bosses; aquila centre; crest to holder |

The new insert bore is parameterized at **3.6 mm**, depth **4.0 mm**, assuming a **3.0 mm long insert**. These are design allowances, not accepted calibration results. The existing M2-A coupon covers upright and sideways bores; use its result and actual insert length to update the two parameters before a production print. Existing structural screw and insert geometry is not changed by this revision. Reference screw heads are 3.8 mm diameter × 1.6 mm tall; confirm actual hardware.

Install inserts before attaching the badges. Fit the locating pieces without forcing them, then snug the screws. Clamp screws work as jack screws against their broad captive shoes; their heads deliberately stand off the clamp. The crest and neck guard can be removed without drilling or cutting the existing head.

## Printing and practical limits

Shells keep their original roof-down orientation and baseline support requirements. New exterior receivers may need local supports; inspect these in the slicer. Curved red fields and white emblems are exported standing on their lower edge, with their curvature in the layer plane; use a brim for the thin white pieces. Tablets and aquila print with their backs down. Tablets change from white to red at print Z1.5 mm; raised letter height is 0.6 mm. Print the eagle with a fine layer profile (for example 0.12–0.16 mm) to retain the shallow feather and eye detail, then inspect the preview at actual size. This package does not claim a slicer-verified setting.

Crest is exported on its broad side. Clamp shoes are small flat pads; use a brim and keep their contact faces clean. Regular PLA carries clamp and receiver loads; silk is used for decorative covers and faces, not spring clips or load-bearing tongues.

Added head weight and servo inertia are real even though the existing head structure and travel limits are unchanged. Weigh the printed accessories and check the loaded tilt movement before use. Wiring flexibility, real material fit, thermal behaviour, and physical vibration retention are not established by CAD. No printer job or queue was changed.

## Completed saved-file checks

- 22 valid single-solid printed parts; all individual meshes solid and manifold; STEP reopens with 22 solids and matching geometry under documented spatial checks.
- Original shell material retained; 58 context shapes match the baseline; nine original enclosure files hash-match.
- No detected new-part, existing-component or screw interference, including the camera service v2 case as context.
- Hood 150 mm rearward, right panel 120 mm at 45 degrees, left panel 20 mm at 45 degrees then 90 mm outward at 15 degrees: additions clear at 1 mm samples against authenticated original sweep evidence. The hood-owned switch and speaker also move with the hood in this check.
- Head additions clear eleven relative tilt poses; original pan range retained; fixed structure and sensor fields remain clear under the stated geometric bounds.
- Existing vents/SMA access and all seven new body insert bores checked clear.

See `independent-verification.json` for values, thresholds and the distinction between CAD verification and physical confirmation.
