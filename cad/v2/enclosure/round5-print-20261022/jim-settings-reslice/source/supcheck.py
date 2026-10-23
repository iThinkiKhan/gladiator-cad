"""Support-vs-fastener-path check (Codex's hole list and transform, re-implemented). Usage: supcheck.py 07|08 file.gcode"""
import json, math, re, sys
import numpy as np
from pathlib import Path
N = Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-calibrated-28-20261022')
key, g = sys.argv[1], sys.argv[2]
segs = []; x = y = z = 0.; role = ''
for l in open(g, errors='ignore'):
    if l.startswith(';TYPE:'): role = l[6:].strip(); continue
    if not (l.startswith('G1 ') or l.startswith('G0 ')): continue
    v = {a: float(b) for a, b in re.findall(r'([XYZE])([-\d.]+)', l.split(';')[0])}
    nx, ny, nz = v.get('X', x), v.get('Y', y), v.get('Z', z)
    if v.get('E', 0) > 0 and (nx != x or ny != y) and role.startswith('Support'): segs.append([x, y, nx, ny, nz])
    x, y, z = nx, ny, nz
a = np.array(segs)
if key == '07':
    B = json.load(open(N / 'mount-checked-release/build-summary.json')); ENV = json.load(open(N / 'mount-checked-release/native-mount-envelopes.json'))
    holes = {'Rear_Hood': [(f'Tablet_{s}_{yy}', (xx, yy, 70), 0, 1.4, 4) for s, xx in [('L', -11.8), ('R', 90.8)] for yy in [-6, 48]] +
             [('Aquila', (26, -34.8, 68.5), 1, 1.4, 4), ('Speaker_rear', (64, -16.25, 101.9), 2, 1.4, 4), ('Speaker_front', (64, 20.25, 101.9), 2, 1.4, 4)]}
    sl = math.atan(1 / 89)
    for yy, zz in [(22, 40), (35.5, 46), (59, 45)]:
        left = 7.5 - sl * (yy - 23.85) - .2; right = 71.5 + sl * (yy - 23.85) + .2
        holes['Rear_Hood'] += [(f'Rail_L_{yy}', ((-9 + left) / 2, yy, zz), 0, 1.8, left + 9), (f'Rail_R_{yy}', ((88 + right) / 2, yy, zz), 0, 1.8, 88 - right)]
    for xx in [22, 33, 50, 66]:
        holes['Rear_Hood'] += [(f'Roof_insert_{xx}', (xx, 72, (95.6 + 103.1) / 2), 2, 2.3, 103.1 - 95.6), (f'Roof_clearance_{xx}', (xx, 72, (103.1 + 106.7) / 2), 2, 1.8, 106.7 - 103.1)]
    holes['Rear_Hood'] += [('SMA', (68, -31, 84.5), 1, 3.5, 2)]
else:
    B = json.load(open(N / 'print/build-summary.json')); ENV = json.load(open(N / 'print/native-mount-envelopes.json'))
    holes = {'Front_Left': [('Scutum_L', (16, 150.8, 79), 1, 1.4, 4)], 'Front_Right': [('Scutum_R', (63, 150.8, 79), 1, 1.4, 4)]}
rep = {}
for p in B['plates'][key]['parts']:
    name = p['name']
    if name not in holes: continue
    b = ENV[name]['bounds']; c = p['at_mm']; mid = np.array([(b[0] + b[3]) / 2, (b[1] + b[4]) / 2])
    def w(px, py, pz): return np.column_stack([px - c[0] + mid[0], mid[1] - (py - c[1]), b[5] - pz])
    p0 = w(a[:, 0], a[:, 1], a[:, 4]); p1 = w(a[:, 2], a[:, 3], a[:, 4])
    for nm, cen, axis, rad, depth in holes[name]:
        d0 = p0 - np.array(cen); dr = p1 - p0; ax0 = d0[:, axis]; ad = dr[:, axis]; half = depth / 2 + .2
        lo = np.zeros(len(a)); up = np.ones(len(a)); mv = np.abs(ad) > 1e-10
        ta = np.zeros(len(a)); tb = np.zeros(len(a)); ta[mv] = (-half - ax0[mv]) / ad[mv]; tb[mv] = (half - ax0[mv]) / ad[mv]
        lo[mv] = np.maximum(0, np.minimum(ta[mv], tb[mv])); up[mv] = np.minimum(1, np.maximum(ta[mv], tb[mv]))
        ok = (lo <= up) & (mv | (np.abs(ax0) <= half))
        r0 = np.delete(d0, axis, axis=1); rd = np.delete(dr, axis, axis=1); den = np.sum(rd * rd, axis=1)
        t = np.zeros(len(a)); nz = den > 1e-15; t[nz] = -np.sum(r0[nz] * rd[nz], axis=1) / den[nz]; t = np.maximum(lo, np.minimum(up, t))
        dist = np.sqrt(np.sum((r0 + t[:, None] * rd) ** 2, axis=1))
        hits = ok & (dist < rad + .2)
        rep[nm] = (int(hits.sum()), round(float(dist[ok].min()), 2) if ok.any() else None)
print(Path(g).name, 'support segments', len(a), '| paths', len(rep), '| paths hit:', {k: v for k, v in rep.items() if v[0]} or 'NONE')
print('   nearest support to each path (mm from axis):', {k: v[1] for k, v in rep.items()})
if key == '07' and len(sys.argv) > 3:
    p = [q for q in B['plates']['07']['parts'] if q['name'] == 'Rear_Hood'][0]
    b = ENV['Rear_Hood']['bounds']; c = p['at_mm']; mid = np.array([(b[0] + b[3]) / 2, (b[1] + b[4]) / 2])
    cen = np.array([68, -31, 84.5])
    gx = cen[0] - mid[0] + c[0]; gy = c[1] + mid[1] - cen[1]; gz = b[5] - cen[2]
    print('SMA hole on the plate: X %.1f Y %.1f, print height %.1f mm (axis along plate Y, 7 mm dia, 2 mm wall)' % (gx, gy, gz))
    near = a[(np.abs((a[:, 0] + a[:, 2]) / 2 - gx) < 5) & (np.abs((a[:, 1] + a[:, 3]) / 2 - gy) < 6)]
    zs = sorted(set(np.round(near[:, 4], 2)))
    print('support segments within 5 mm of it:', len(near), '| Z from %.2f to %.2f' % (min(zs), max(zs)) if zs else '')
    inside = near[(np.abs(near[:, 4] - gz) < 3.6)]
    print('of those at the hole height band (+-3.5 mm):', len(inside), 'Y range %.1f..%.1f' % (inside[:, [1, 3]].min(), inside[:, [1, 3]].max()) if len(inside) else '')
