"""Set the printer queue: exactly the live plates at the top, everything else filed.

Why this exists in this form. `export_prints.py` and `build_plates.py` used to write
straight into the printer's incoming folder, so every re-export dumped all nine part
STLs and all five plates back on top of a curated queue - three times in one session.
Those scripts now write only to `cad/print-ready/`, and the queue is set here,
deliberately, by naming what is live.

Nothing is deleted. Everything not live is moved under `_archive/`.
"""
import os
import shutil
import sys

REPO = '/home/buralien/projects/gladiator-cad'
SRC = os.path.join(REPO, 'cad/print-ready')
INC = '/home/buralien/Desktop/3D-Printer-Incoming'

# What is actually queued right now, and why. Edit this list; it is the whole point.
LIVE = [
    ('Gladiator_PlateH_DECK-AND-GH44.3mf',
     'the fast one - upper deck v2 and the corrected GH44 receiver, both flat and low'),
    ('Gladiator_PlateG_MASTBASE-AND-DRIVERS.3mf',
     'mast base + both driver mounts, REBUILT with the flat-footed mounts'),
]

BUCKETS = {
    'done': ['PlateA', 'PlateC', 'PlateF', 'CouponA', 'P1_Coupon'],
    'superseded_plates': ['PlateD', 'PlateE'],
    'superseded': ['PlateD', 'PlateE', 'CouponC', 'BeltMesh_60deg'],
    'blocked': ['PlateB'],
}


def bucket_for(fn):
    for b, keys in BUCKETS.items():
        for k in keys:
            if k in fn:
                return b
    return 'single-parts'


def main():
    live_names = set(n for n, _ in LIVE)
    for b in list(BUCKETS) + ['single-parts']:
        d = os.path.join(INC, '_archive', b)
        if not os.path.isdir(d):
            os.makedirs(d)

    # 1. file away anything at the top level that is not live
    moved = 0
    for fn in sorted(os.listdir(INC)):
        p = os.path.join(INC, fn)
        if not os.path.isfile(p) or fn in live_names:
            continue
        dest = os.path.join(INC, '_archive', bucket_for(fn), fn)
        shutil.move(p, dest)
        print('  filed    %-52s -> _archive/%s' % (fn, bucket_for(fn)))
        moved += 1

    # 2. make sure every live file is present and current
    for fn, why in LIVE:
        src = os.path.join(SRC, fn)
        dst = os.path.join(INC, fn)
        if not os.path.exists(src):
            print('  *** MISSING from cad/print-ready: %s' % fn)
            continue
        if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
            shutil.copy2(src, dst)
            print('  queued   %-52s %s' % (fn, why))
        else:
            print('  current  %-52s %s' % (fn, why))

    print()
    print('queue:')
    for fn in sorted(os.listdir(INC)):
        p = os.path.join(INC, fn)
        if os.path.isfile(p):
            print('   %-52s %7.0f kB' % (fn, os.path.getsize(p) / 1024.0))
        else:
            print('   %s/' % fn)
    print()
    print('%d file(s) filed away' % moved)


main()
