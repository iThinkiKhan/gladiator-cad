"""Apply the 2026-09-18 coupon results to the master, and bind the fit-critical
radii to the Parameters spreadsheet so they are actually parametric.

Two separate things are being fixed here:

1. **The values.** The coupon says round features print about 0.25 undersize on this
   printer, while flat walls run slightly OVER (plate 88.00 -> 88.25). Every fit that
   was tested wants one step up: insert bore 4.4 -> 4.6, M3 clearance 3.4 -> 3.6,
   M2 clearance 2.4 -> 2.6, mast spigot 13.8 -> 14.0. The rail foot slot is NOT
   changed - it has flat walls, it measured right, and Jim confirmed the fit.

2. **The binding.** These radii were plain numbers in the sketches with no expression
   attached, even though the spreadsheet had aliases for several of them. Changing
   rail_insert_dia did nothing. They are bound here so the documented behaviour is
   the real behaviour.
"""
import datetime
import os
import shutil
import sys
import FreeCAD as App

_p=print
def print(*a,**k):
    _p(*a,**k)
    sys.stdout.flush()

REPO = '/home/buralien/projects/gladiator-cad'
MASTER = REPO + '/cad/master/Gladiator_Master.FCStd'
DRAFTS = REPO + '/cad/master/drafts'

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
if not os.path.isdir(DRAFTS):
    os.makedirs(DRAFTS)
backup = os.path.join(DRAFTS, 'Gladiator_Master.%s.pre-calibration.FCStd' % stamp)
shutil.copy2(MASTER, backup)
print('backup -> %s' % backup)

import traceback
doc = App.openDocument(MASTER)
sp = doc.getObject('Parameters')

def guard(label, fn):
    try:
        return fn()
    except BaseException as e:
        print('*** %s FAILED: %s: %s' % (label, type(e).__name__, e))
        traceback.print_exc()
        sys.stdout.flush()
        raise

# ---- 2. bind the sketch radii ---------------------------------------------
# feature -> (expected current radius, spreadsheet alias)
BIND = [
    ('RailInsertCuts',      2.20, 'rail_insert_dia'),
    ('DrvInsertCut',        2.20, 'rail_insert_dia'),
    ('S3InsertCut',         2.20, 'rail_insert_dia'),
    ('AntInsertCut',        2.20, 'rail_insert_dia'),
    ('UpperDeckScrewCuts',  1.70, 'deck2_screw_dia'),
    ('AntFixHoleCut',       1.70, 'deck2_screw_dia'),
    ('DrvDeckHoleCut',      1.70, 'deck2_screw_dia'),
    ('MastPinCut',          1.70, 'mast_pin_dia'),
    ('MastTubePinCut',      1.70, 'mast_pin_dia'),
    ('MastPlateScrewCuts',  1.20, 'm2_screw_dia'),
    ('ShieldScrewCut',      1.20, 'm2_screw_dia'),
    ('AntSmaCut',           3.25, 'ant_sma_dia'),
    ('MastSpigotPad',       6.90, 'mast_spigot_dia'),
]

print()
print('binding radii to the spreadsheet:')
bound = 0
for fname, expect_r, alias in BIND:
    o = doc.getObject(fname)
    if o is None:
        raise SystemExit('%s not found' % fname)
    prof = getattr(o, 'Profile', None)
    sk = prof[0] if isinstance(prof, (list, tuple)) and prof else prof
    if sk is None or not hasattr(sk, 'Constraints'):
        raise SystemExit('%s has no sketch' % fname)
    hits = 0
    for i, c in enumerate(sk.Constraints):
        if c.Type not in ('Radius', 'Diameter'):
            continue
        val = c.Value
        want = expect_r if c.Type == 'Radius' else expect_r * 2
        if abs(val - want) > 1e-6:
            continue                      # not one of ours (fillet, etc.) - leave it
        expr = 'Parameters.%s / 2' % alias if c.Type == 'Radius' else 'Parameters.%s' % alias
        sk.setExpression('Constraints[%d]' % i, expr)
        hits += 1
    if hits == 0:
        raise SystemExit('%s: found no radius constraint at %.2f - aborting' % (fname, expect_r))
    bound += hits
    print('  %-22s %d constraint(s) -> %s' % (fname, hits, alias))

print('  %d constraints bound in total' % bound)

doc.recompute()

# ---- 1. spreadsheet values -------------------------------------------------
NEW = {
    'rail_insert_dia': (4.4, 4.6, 'heat-set insert bore; 4.6 took the insert flush and would not pull out'),
    'deck2_screw_dia': (3.4, 3.6, 'M3 clearance; 3.4 would not pass, 3.6 did'),
    'mast_pin_dia':    (3.4, 3.6, 'M3 cross-pin, same clearance finding'),
    'mast_spigot_dia': (13.8, 14.0, '14.0 peg fitted the real deck hole with little to no jiggle'),
    'ant_sma_dia':     (6.5, 6.75, 'ESTIMATED, not tested: targets 6.5 physical against a 6.35 thread'),
}
rowof = {}
for r in range(1, 200):
    try:
        a = sp.get('A%d' % r)
    except Exception:
        continue
    rowof[str(a)] = r

for alias, (old, new, why) in NEW.items():
    r = rowof.get(alias)
    if r is None:
        raise SystemExit('alias %s not found in column A' % alias)
    cur = sp.get(alias)
    curv = cur.Value if hasattr(cur, 'Value') else float(cur)
    if abs(curv - old) > 1e-6:
        raise SystemExit('%s is %.3f, expected %.3f - aborting' % (alias, curv, old))
    sp.set('B%d' % r, '%g mm' % new)
    print('  %-18s %.2f -> %.2f   (%s)' % (alias, old, new, why))

# new alias for the M2 clearance holes, which had no spreadsheet entry at all
if 'm2_screw_dia' not in rowof:
    r = max(rowof.values()) + 1
    sp.set('A%d' % r, 'm2_screw_dia')
    sp.set('B%d' % r, '2.6 mm')
    sp.setAlias('B%d' % r, 'm2_screw_dia')
    print('  %-18s NEW row %d = 2.6   (M2 clearance; 2.4 would not pass, 2.6 did)' % ('m2_screw_dia', r))
doc.recompute()

# ---- 3. verify -------------------------------------------------------------
print()
print('verifying:')
PARTS = ['SideRailLeft', 'SideRailRight', 'UpperDeck', 'MastBase', 'MastTube',
         'PowerShield', 'AntennaPost', 'DriverMountLeft', 'DriverMountRight']
ok = True
for n in PARTS:
    s = doc.getObject(n).Shape
    good = s.isValid() and len(s.Solids) == 1
    dias = {}
    for f in s.Faces:
        if f.Surface.TypeId == 'Part::GeomCylinder':
            d = round(f.Surface.Radius * 2, 2)
            dias[d] = dias.get(d, 0) + 1
    print('  %-18s valid=%s solids=%d  %s' % (n, s.isValid(), len(s.Solids),
          ' '.join('%.2fx%d' % (d, c) for d, c in sorted(dias.items()))))
    ok = ok and good

EXPECT = [
    ('SideRailLeft', 4.6, 3), ('SideRailRight', 4.6, 3), ('UpperDeck', 4.6, 10),
    ('UpperDeck', 3.6, 6), ('MastBase', 2.6, 2), ('MastBase', 3.6, 2),
    ('MastBase', 14.0, 1), ('MastTube', 3.6, 2), ('PowerShield', 2.6, 2),
    ('AntennaPost', 3.6, 2), ('AntennaPost', 6.75, 1),
    ('DriverMountLeft', 3.6, 2), ('DriverMountRight', 3.6, 2),
]
print()
for n, d, cnt in EXPECT:
    s = doc.getObject(n).Shape
    got = sum(1 for f in s.Faces if f.Surface.TypeId == 'Part::GeomCylinder'
              and abs(f.Surface.Radius * 2 - d) < 0.005)
    mark = 'ok' if got == cnt else '*** MISMATCH'
    if got != cnt:
        ok = False
    print('  %-18s dia %6.2f  expected %2d  found %2d  %s' % (n, d, cnt, got, mark))

# the rail slot must be untouched
rs = sp.get('rail_slot_width')
rsv = rs.Value if hasattr(rs, 'Value') else float(rs)
print()
print('  rail_slot_width still %.2f (must stay 3.40 - Jim confirmed the fit)' % rsv)
if abs(rsv - 3.4) > 1e-6:
    ok = False

if not ok:
    raise SystemExit('VERIFICATION FAILED - not saving')

doc.save()
print()
print('saved. backup of the previous state is at:')
print('  %s' % backup)
