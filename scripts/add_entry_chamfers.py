"""Add a 45 degree entrance relief to the bores that start on the build plate.

Jim's call, 2026-09-18: the winning clearance holes pass a screw but snag at the very
bottom, which is elephant's foot, not a diameter problem. So the holes stay at 3.6/2.6
and the bed-facing entrance gets a small chamfer to remove the lip.

Checked against each part's actual print orientation rather than assumed: only two
parts have any bore entering at the bed.

  UpperDeck  - 6 x M3 clearance (3.6) and the 20.4 mast bore, all at the Z=48 bed face
  MastBase   - the 20.4 mast socket, at the Z=20 collar top, which is its bed face

The rails' insert bores, both driver mounts' deck holes and every M2 hole print either
horizontal or up in the air, so they are untouched.

The two 20.4 bores were not in Jim's brief. They are included because the mast tube has
to slide into both and an elephant-foot lip sits exactly where it enters; the chamfer
doubles as an assembly lead-in.
"""
import datetime
import os
import shutil
import sys

import FreeCAD as App

_p = print


def print(*a, **k):
    _p(*a, **k)
    sys.stdout.flush()


REPO = '/home/buralien/projects/gladiator-cad'
MASTER = REPO + '/cad/master/Gladiator_Master.FCStd'
DRAFTS = REPO + '/cad/master/drafts'

CHAMFER = 0.35          # mid of Jim's 0.3-0.4
TOL = 1e-4

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
if not os.path.isdir(DRAFTS):
    os.makedirs(DRAFTS)
backup = os.path.join(DRAFTS, 'Gladiator_Master.%s.pre-chamfer.FCStd' % stamp)
shutil.copy2(MASTER, backup)
print('backup -> %s' % backup)

doc = App.openDocument(MASTER)
sp = doc.getObject('Parameters')

# parameter row, so the size is editable like everything else
rowof = {}
for r in range(1, 250):
    try:
        a = sp.get('A%d' % r)
    except Exception:
        continue
    rowof[str(a)] = r
if 'hole_entry_chamfer' not in rowof:
    r = max(rowof.values()) + 1
    sp.set('A%d' % r, 'hole_entry_chamfer')
    sp.set('B%d' % r, '%g mm' % CHAMFER)
    sp.setAlias('B%d' % r, 'hole_entry_chamfer')
    print('  new parameter hole_entry_chamfer = %.2f mm (row %d)' % (CHAMFER, r))
doc.recompute()

# body -> (bed-face Z in the part's own coords, the bore diameters to relieve)
JOBS = [
    ('UpperDeck', 48.0, (3.6, 20.4)),
    ('MastBase', 20.0, (20.4,)),
]

print()
for body_name, bed_z, dias in JOBS:
    body = doc.getObject(body_name)
    tip = body.Tip
    shape = tip.Shape
    picks = []
    for i, e in enumerate(shape.Edges):
        if len(e.Vertexes) != 1:                    # a full circle closes on one vertex
            continue
        try:
            c = e.Curve
        except Exception:
            continue
        if c.TypeId != 'Part::GeomCircle':
            continue
        d = round(c.Radius * 2, 2)
        if not any(abs(d - t) < 0.01 for t in dias):
            continue
        if abs(e.CenterOfMass.z - bed_z) > 0.01:
            continue
        picks.append(('Edge%d' % (i + 1), d))

    if not picks:
        raise SystemExit('%s: found no bore edges at Z=%.1f - aborting' % (body_name, bed_z))

    ch = doc.addObject('PartDesign::Chamfer', '%sEntryChamfer' % body_name)
    ch.Base = (tip, [n for n, _ in picks])
    ch.Size = CHAMFER
    ch.setExpression('Size', 'Parameters.hole_entry_chamfer')
    body.addObject(ch)
    doc.recompute()

    if ch.isError() if hasattr(ch, 'isError') else False:
        raise SystemExit('%s chamfer errored' % body_name)
    counts = {}
    for _, d in picks:
        counts[d] = counts.get(d, 0) + 1
    print('  %-12s chamfered %s at Z=%.1f  ->  %s'
          % (body_name, ', '.join('%dx dia %.2f' % (c, d) for d, c in sorted(counts.items())),
             bed_z, ch.Name))

doc.recompute()

# ---- verify ---------------------------------------------------------------
print()
print('verifying:')
PARTS = ['SideRailLeft', 'SideRailRight', 'UpperDeck', 'MastBase', 'MastTube',
         'PowerShield', 'AntennaPost', 'DriverMountLeft', 'DriverMountRight']
ok = True
for n in PARTS:
    s = doc.getObject(n).Shape
    good = s.isValid() and len(s.Solids) == 1 and s.Volume > 0
    ok = ok and good
    print('   %-18s valid=%-5s solids=%d vol=%9.1f' % (n, s.isValid(), len(s.Solids), s.Volume))

# the straight part of each bore must survive at full size
print()
for n, dias, cnt in (('UpperDeck', 3.6, 6), ('UpperDeck', 4.6, 10), ('UpperDeck', 20.4, 1),
                     ('MastBase', 20.4, 1), ('MastBase', 14.0, 1), ('MastBase', 2.6, 2)):
    s = doc.getObject(n).Shape
    got = sum(1 for f in s.Faces if f.Surface.TypeId == 'Part::GeomCylinder'
              and abs(f.Surface.Radius * 2 - dias) < 0.005)
    mark = 'ok' if got == cnt else '*** MISMATCH'
    if got != cnt:
        ok = False
    print('   %-12s dia %6.2f straight bore still present: expected %2d found %2d  %s'
          % (n, dias, cnt, got, mark))

# and there must now be cones at the bed faces
print()
for n, bed_z in (('UpperDeck', 48.0), ('MastBase', 20.0)):
    s = doc.getObject(n).Shape
    cones = [f for f in s.Faces if f.Surface.TypeId == 'Part::GeomCone']
    near = [f for f in cones if abs(f.BoundBox.ZMin - bed_z) < 0.5 or abs(f.BoundBox.ZMax - bed_z) < 0.5]
    print('   %-12s conical relief faces at the bed face: %d' % (n, len(near)))
    if not near:
        ok = False

if not ok:
    raise SystemExit('VERIFICATION FAILED - not saving')

doc.save()
print()
print('saved. previous state: %s' % backup)
