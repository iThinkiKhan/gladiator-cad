# Power-board cradle v1

Standalone replacement candidate for `PowerShield`. It does not modify the
master assembly.

## What it does

- shields the solder side with a 1.0 mm floor;
- leaves 7.0 mm between that floor and the PCB underside;
- locates a 60 x 40 x 1.6 mm board on four 6 mm OD M2 thread-forming standoffs at the
  confirmed 54.25 x 34.5 mm pattern;
- surrounds the complete PCB perimeter to protect every edge of the solder side;
- supports both long rear rails on the top rim of the mast base without using
  either mast fastener;
- carries its load on two short, exposed M3 bolts in low tabs at the rear ends
  of the long deck slots;
- uses the rear M2 pair as anti-lift/anti-rotation fasteners; and
- does not share either mast-base mounting screw.

## Hardware and assembly

1. Fit the cradle after the mast base and rails are installed.
2. Put short M3 screws and ordinary washers through the exposed 3.6 mm holes in
   the deck-level tabs at `(25.5, 130.5)` and `(53.5, 130.5)`, then through the
   long deck slots. Use washers/nuts below the deck. The support columns are
   offset sideways, so nothing obstructs a driver above either screw.
3. Drive short M2 thread-forming screws upward through the deck's 1.6 mm rear
   pilots at `(19, 128)` and `(60, 128)` into the matching blind foot pilots.
   These are secondary anti-lift/anti-rotation restraints; the M3 bolts carry
   the structural load.
4. Fasten the board from above with four M2 screws into the 1.6 mm blind
   thread-forming pilots. Start gently and do not bottom the screws into the
   shield floor.

## Fit gates before committing to the full print

- The current vertical budget permits **16.2 mm above the PCB top** before the
  upper-deck underside. The recorded total board height is about 16 mm, which
  is consistent with this but close. Check the tallest connector while plugged
  in; if it exceeds 15.2 mm above the PCB, the upper deck must be removed for
  service or the stack height must change.
- The floor is 0.7 mm above the recorded battery envelope and provides 7.0 mm
  for solder/leads below the PCB. Verify no lead exceeds 7.0 mm.
- Confirm the selected M2 screws form cleanly in the deck and foot pilots
  without splitting the edge beside either rail. They are secondary restraints;
  the M3 slot bolts carry the structural load.

## Printing

Use `stl/PowerBoardCradle_v1_print-on-rear-face.stl`. Print with the rear feet
on the bed and add a brim. The installed-coordinate STL is included only for
assembly inspection.

Suggested starting point: PETG, 0.20 mm layers, 4 walls, 5 top/bottom layers,
25-35% gyroid. Enable build-plate-only organic support under the tray's rear
wall and the horizontal PCB posts; the mast-bearing rails themselves are
vertical in this orientation. Preview all four M2 pilots before starting.
