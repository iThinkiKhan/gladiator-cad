"""For every model island that starts above the bed, check something is printed directly under it on the layer below."""
import re, sys, collections
import numpy as np
g = sys.argv[1]
lay = collections.defaultdict(list); x = y = z = 0.; role = ''; w = .4
for l in open(g, errors='ignore'):
    if l.startswith(';TYPE:'): role = l[6:].strip(); continue
    if l.startswith(';WIDTH:'): w = float(l[7:]); continue
    if not l.startswith('G1 '): continue
    v = {a: float(b) for a, b in re.findall(r'([XYZE])([-\d.]+)', l.split(';')[0])}
    nx, ny, z = v.get('X', x), v.get('Y', y), v.get('Z', z)
    if v.get('E', 0) > 0 and (nx != x or ny != y) and role not in ('Custom',):
        n = max(1, int(((nx - x) ** 2 + (ny - y) ** 2) ** .5 / .5))
        for i in range(n + 1): lay[round(z, 2)].append((x + (nx - x) * i / n, y + (ny - y) * i / n, role))
    x, y = nx, ny
zs = sorted(lay); G = 1.0
occ = {}
for zz in zs:
    occ[zz] = set((int(p[0] // G), int(p[1] // G)) for p in lay[zz])
worst = []
for i in range(1, len(zs)):
    below = set().union(*[occ[q] for q in zs[:i] if zs[i] - .65 < q < zs[i] - .01])
    cells = set((int(p[0] // G), int(p[1] // G)) for p in lay[zs[i]] if not p[2].startswith('Support') and 'Bridge' not in p[2] and p[2] != 'Overhang wall')
    nb = lambda c: any((c[0] + a, c[1] + b) in below for a in (-1, 0, 1) for b in (-1, 0, 1))
    unsup = [c for c in cells if not nb(c)]
    if unsup: worst.append((len(unsup), zs[i], unsup[:3]))
worst.sort(reverse=True)
print(g.split('/')[-1], '| layers', len(zs), '| layers with model cells (1 mm grid) having nothing printed within 1 mm below:', len(worst))
for n, zz, ex in worst[:8]: print('   Z%.2f: %d cells, e.g. %s' % (zz, n, ex))
