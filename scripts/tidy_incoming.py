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
            if os.path.isfile(os.path.join(INC, f)) and f not in KEEP]

# No README is written here. Jim deleted the one this script used to drop in the
# incoming folder and asked for it not to come back - the plate notes live in
# docs/print-plan.md, and a second copy in the print folder just goes stale.

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
