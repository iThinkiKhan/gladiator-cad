# Four-hole M2 D3 L3 coupon — current revision

Jim requested a smaller first-pass coupon, 2026-10-22. This replaces the 16-hole test as the current print choice.

Open M2_D3_L3_Mini_EnderNeo_PLA.3mf. Four labeled upright blind holes: 2.8, 2.9, 3.0, 3.1 mm CAD diameters, each 3.6 mm deep with a 0.15 mm entry chamfer. Envelope 40 x 13 x 6 mm; 7 mm bosses, 2.4 mm floor. Clipped corner marks the 2.8 end.

Print flat base down at 100% scale. Existing EnderNeo PLA profile, 0.20 mm layers, four walls, 25% infill, no supports or brim. Native/STEP reopen, four bore/floor checks, manifold STL and warning-free Orca slicing verified. No print started.

Check delivered inserts against the listing's nominal M2 thread, 3 mm knurled OD, 3 mm length. Try 3.0 first; go smaller if loose or larger if installation needs excessive pressure. Install flush using the supplier's PLA guidance and consistent temperature/dwell. Cool completely. Reject bulging, cracks, tilt, spinning or pullout. Keep the test screw tip clear of the blind floor. Record the winning CAD label in results.csv; confirm with a fresh insert before applying it widely. This small coupon tests the vertical print orientation; sideways holes need confirmation if used later. A physical fit result is still pending.

build_coupon.py is the editable source; dimensions on the saved FreeCAD solid are descriptive metadata. Existing project geometry is preserved.

Slicer estimates:
; filament used [g] = 1.78
; total filament used [g] = 1.78
; estimated printing time (normal mode) = 9m 51s
