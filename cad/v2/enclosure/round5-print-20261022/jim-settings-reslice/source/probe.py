import re, sys
g = sys.argv[1]; X0, X1, Y0, Y1, Z0, Z1 = map(float, sys.argv[2:8])
x = y = z = 0.; role = ''; hits = {}
for l in open(g, errors='ignore'):
    if l.startswith(';TYPE:'): role = l[6:].strip(); continue
    if not l.startswith('G1 '): continue
    v = {a: float(b) for a, b in re.findall(r'([XYZE])([-\d.]+)', l.split(';')[0])}
    nx, ny, z = v.get('X', x), v.get('Y', y), v.get('Z', z)
    if v.get('E', 0) > 0 and Z0 <= z <= Z1:
        mx, my = (x + nx) / 2, (y + ny) / 2
        if X0 <= mx <= X1 and Y0 <= my <= Y1: hits.setdefault((round(z, 2), role), 0); hits[(round(z, 2), role)] += 1
    x, y = nx, ny
for k in sorted(hits): print('  Z%.2f %-22s %d' % (k[0], k[1], hits[k]))
