"""Tidy the printer incoming folder: three live plates at the top, everything else
filed under _archive/. Nothing is deleted - every move is reversible.
"""
import os
import shutil

INC = '/home/buralien/Desktop/3D-Printer-Incoming'

KEEP = {
    'Gladiator_PlateB_MAST-AND-FITTINGS.3mf',
    'Gladiator_PlateD_DRIVER-MOUNTS.3mf',
    'Gladiator_PlateF_ALL-COUPONS.3mf',
}

MOVES = {
    'done': [
        ('Gladiator_PlateA_BODY_rails-and-upper-deck.3mf', 'printed 2026-09-18'),
        ('Gladiator_P1_CouponA_InsertBores_flat.stl', 'insert bore answered: 4.6'),
        ('Gladiator_CouponC_SelfTapPilots_flat.stl', 'obsolete - nuts and washers chosen instead'),
    ],
    'superseded': [
        ('Gladiator_PlateE_ALL-COUPONS.3mf', 'replaced by plate F'),
        ('Gladiator_PlateD_DRIVER-MOUNTS_BLOCKED.3mf', 'old name, no longer blocked'),
        ('Gladiator_HeadCoupon_BeltMesh_60deg.stl', 'replaced by the 3-up belt coupon on plate F'),
    ],
    'not-queued': [
        ('Gladiator_PlateC_MAST-TUBE.3mf', 'buy a 20/12 aluminium or carbon tube instead'),
    ],
    'single-parts': [
        ('GH44_Blank_Carrier.stl', 'on plate F'),
        ('GH44_Receiver_Fit_Coupon.stl', 'on plate F'),
        ('Gladiator_HeadCoupon_BeltMesh_3up.stl', 'on plate F'),
        ('Gladiator_CouponD_SmaBore_counterbore-DOWN.stl', 'on plate F'),
        ('Gladiator_P2_AntennaPost_print-on-front-face.stl', 'on plate B'),
        ('Gladiator_P2_MastBase_print-spigot-UP.stl', 'on plate B'),
        ('Gladiator_P2_PowerShield_print-on-side.stl', 'on plate B'),
        ('Gladiator_P3_SideRail_L_print-on-outboard-face.stl', 'on plate A, printed'),
        ('Gladiator_P3_SideRail_R_print-on-outboard-face.stl', 'on plate A, printed'),
        ('Gladiator_P4_UpperDeck_print-flat-bosses-up.stl', 'on plate A, printed'),
        ('Gladiator_P5_MastTube_print-vertical.stl', 'on plate C'),
        ('Gladiator_P6_DriverMount_L_print-inverted.stl', 'on plate D'),
        ('Gladiator_P6_DriverMount_R_print-inverted.stl', 'on plate D'),
    ],
}

log = []
for sub, entries in MOVES.items():
    d = os.path.join(INC, '_archive', sub)
    if not os.path.isdir(d):
        os.makedirs(d)
    for fn, why in entries:
        src = os.path.join(INC, fn)
        if os.path.exists(src):
            shutil.move(src, os.path.join(d, fn))
            log.append('  _archive/%-14s %-52s %s' % (sub + '/', fn, why))
        else:
            log.append('  (absent)       %-52s %s' % (fn, why))

leftover = [f for f in sorted(os.listdir(INC))
            if os.path.isfile(os.path.join(INC, f)) and f not in KEEP and f != 'README.txt']

readme = """GLADIATOR - PRINT QUEUE
=======================

Three plates are live. Open one in Orca, check the notes, slice.
Everything else is filed under _archive/ - nothing has been deleted.

  Gladiator_PlateB_MAST-AND-FITTINGS.3mf
      Mast base, power shield, antenna post.
      BRIM on the mast base and the power shield - both sit on under 260 mm2.
      Minimum layer time ON: above 25 mm only the power shield is still printing.
      The antenna's SMA bore is the one dimension still guessed - coupon D on
      plate F settles it, so plate F is worth running first.

  Gladiator_PlateD_DRIVER-MOUNTS.3mf
      Both driver mounts. Board interface measured and closed 2026-09-20.
      Arms are relieved 2.0 deep for the header tails; the board bears on a pad
      at each screw.
      HARDWARE: M3 x 18-20, with a NUT AND WASHER behind the frame. These are
      3.6 clearance holes, not self-tapping pilots. The space behind each hole is
      clear, so a nut and driver both fit.
      CAUTION: the arms sit 0.24 mm from the heatsink and this is PLA, which
      softens near 60 C. Treat as a fit prototype, not something to drive hard.

  Gladiator_PlateF_ALL-COUPONS.3mf
      Every coupon still worth printing - 13 of them, 200 x 115 of bed.
      Plate F = plate E, minus coupon C (obsolete once nuts were chosen), plus
      coupon D (the SMA bore, which postdated plate E).

ARCHIVE
-------
  _archive/done/          printed, or the question is answered
  _archive/superseded/    replaced by something newer
  _archive/not-queued/    deliberately not printing (the mast tube - buy one)
  _archive/single-parts/  individual STLs for every part now carried on a plate;
                          pull one out to reprint a single part

Regenerate any of this from the repo:
  scripts/build_plates.py       plates A-D
  scripts/build_plate_f.py      plate F
  scripts/build_coupon_plate.py plate E (the head workstream's coupon geometry)
"""

with open(os.path.join(INC, 'README.txt'), 'w') as f:
    f.write(readme)

print('moved:')
for line in log:
    print(line)
print()
print('left at the top level:')
for f in sorted(os.listdir(INC)):
    p = os.path.join(INC, f)
    if os.path.isfile(p):
        print('  %-48s %8.0f kB' % (f, os.path.getsize(p) / 1024.0))
    else:
        print('  %s/' % f)
if leftover:
    print()
    print('NOT filed (unrecognised - left alone):')
    for f in leftover:
        print('  %s' % f)
