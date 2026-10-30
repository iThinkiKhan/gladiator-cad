# Mast v2 - closed tube wiring review, 2026-10-30

Jim selected internal wiring in a stiff tube, with pull-cord threading, instead of the continuous lay-in slot.
This is an isolated CAD proposal. The previous v2 model, generator, and print files are preserved.

## Proposal

- Keep the 20 mm OD, 12 mm ID, 144 mm tube length (world Z6..150), key flat, base pin at Z13 and head bolt at Z123.
- Remove the long rear slot completely. Retain a short lower inlet on the existing +Y face, nominal 10 x 12 mm throat, with rounded corners and flared edges; maximum opening bounds Z23.2..36.8.
- Add 0.7 mm lead-in chamfers at both bore ends without changing OD seating surfaces.
- Plain closed tube: +4.24 g solid PLA relative to the slotted tube.
- Optional integral bolt guard: +4.86 g total; an elliptical sleeve around the unchanged M3 through-bolt prevents direct wire/screw contact. Minimum guard wall 1.0 mm. This option is shown in the assembled review file; the plain version is also supplied.

## Guard tradeoff

The sleeve divides the bore locally into two crescent-shaped wire passages. Each accepts a nominal 3.2 mm round CAD gauge, with no allowance on that round gauge for printing variation. A 2.84 mm square CAD gauge also clears the saved model along each upper path. These are geometric gauges, NOT measured connector dimensions or a proven bundle capacity. Multiway plugs may not pass. Actual lead count, housing dimensions, insulation and print tolerance need checking before adopting the guard.

The optional guard needs a bridge across the bore during upright printing. This has not been sliced or printed. Both variants remain proposals; no numerical stiffness improvement or strength rating is claimed.

## Wiring/service sequence

1. Before installation, feed a cord from the open top to the lower inlet. With the guard, use one of the two passages alongside it.
2. Pull loose leads or individual terminals through gradually; stagger the joints rather than pulling a thick connector cluster. Avoid pulling on crimp contacts.
3. Pull a second spare cord through with the harness and retain it for later additions.
4. Provide slack and strain relief outside the inlet and at the head. Existing pan/tilt flex loops still require physical checks.
5. For the plain tube, remove the head bolt before feeding wires; wire clearance during bolt reinstallation remains unresolved. The guarded option addresses this locally, at the cost of connector space.

## Files and rebuild

- Gladiator_Closed_Mast_Review.FCStd: existing head/robot with protected tube, plus previous/plain/protected comparisons and a cutaway.
- Closed_Tube.step / Closed_Tube.stl: plain variant at origin.
- Closed_Tube_Bolt_Guard.step / Closed_Tube_Bolt_Guard.stl: protected variant at origin.
- closed_mast_review.png: actual CAD mesh comparison with a schematic bolt section.
- build_closed_tube.py: source; run on cad-lab with system python3 (imports /usr/lib/freecad/lib).
- verify_saved.py, render_review.py, validation.json: independent saved-file checks, rendering and results.

## Verification and limits

Both native variants and re-imported STEP models are valid single solids; exported meshes are closed/manifold. Both fit the saved assembly at its home pose without interference above the 0.05 mm3 check threshold. Saved-file checks verify the restored rear wall, original height, and upper wire gauges. The original v2 CAD hash is unchanged. Head movement geometry and firmware limits were not modified; a fresh full motion/harness check was not performed.

No slicing, printing, physical fit, or stiffness testing. Keep the current print queue unchanged. Confirm the real harness before choosing the optional guard or preparing print files.
