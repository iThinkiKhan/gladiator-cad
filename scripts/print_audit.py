import math
import FreeCAD as App
import Part

DOC = '/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd'
doc = App.openDocument(DOC)

# Only the parts WE print. Right-hand parts are mirrors of the left, same print behaviour.
PRINTED = ['SideRailLeft', 'UpperDeck', 'MastBase', 'MastTube', 'PowerShield',
           'AntennaPost', 'DriverMountLeft']

ORIENTS = [
    ('+Z  (as modelled)', App.Vector(0, 0, 1)),
    ('-Z  (upside down)', App.Vector(0, 0, -1)),
    ('+X  (on -X face)', App.Vector(1, 0, 0)),
    ('-X  (on +X face)', App.Vector(-1, 0, 0)),
    ('+Y  (on -Y face)', App.Vector(0, 1, 0)),
    ('-Y  (on +Y face)', App.Vector(0, -1, 0)),
]

OVERHANG_LIMIT = 45.0    # degrees from vertical; beyond this needs support
GRID = 4


def sample_normals(shape):
    """Area-weighted normal samples across every face."""
    out = []
    for f in shape.Faces:
        try:
            u0, u1, v0, v1 = f.ParameterRange
        except Exception:
            continue
        area = f.Area
        if area <= 0:
            continue
        norms = []
        for i in range(GRID):
            for j in range(GRID):
                u = u0 + (u1 - u0) * (i + 0.5) / GRID
                v = v0 + (v1 - v0) * (j + 0.5) / GRID
                try:
                    n = f.normalAt(u, v)
                except Exception:
                    continue
                if f.Orientation == 'Reversed':
                    n = App.Vector(-n.x, -n.y, -n.z)
                norms.append(n)
        if not norms:
            continue
        w = area / len(norms)
        for n in norms:
            out.append((n, w))
    return out


def overhang_area(samples, up):
    bad = 0.0
    for n, w in samples:
        c = n.dot(up)
        if c < 0:
            ang = math.degrees(math.asin(min(1.0, -c)))   # 90 = flat horizontal underside
            if ang > OVERHANG_LIMIT:
                bad += w
    return bad


def footprint(shape, up):
    bb = shape.BoundBox
    dims = {'x': bb.XLength, 'y': bb.YLength, 'z': bb.ZLength}
    axis = 'x' if abs(up.x) > 0.5 else ('y' if abs(up.y) > 0.5 else 'z')
    height = dims.pop(axis)
    a, b = list(dims.values())
    return a, b, height


def min_wall(shape):
    """Smallest solid thickness between opposing parallel planar faces."""
    planars = []
    for f in shape.Faces:
        if f.Surface.TypeId != 'Part::GeomPlane':
            continue
        n = App.Vector(f.Surface.Axis)
        if f.Orientation == 'Reversed':
            n = App.Vector(-n.x, -n.y, -n.z)
        n.normalize()
        planars.append((f, n))
    best = None
    for i in range(len(planars)):
        fi, ni = planars[i]
        ci = fi.CenterOfMass
        for j in range(i + 1, len(planars)):
            fj, nj = planars[j]
            if ni.dot(nj) > -0.999:
                continue
            d = abs((fj.CenterOfMass - ci).dot(ni))
            if d < 0.05 or d > 30.0:
                continue
            probe = ci + ni.multiply(d * 0.5) if False else App.Vector(
                ci.x + ni.x * d * 0.5, ci.y + ni.y * d * 0.5, ci.z + ni.z * d * 0.5)
            try:
                if not shape.isInside(probe, 1e-6, True):
                    continue
            except Exception:
                continue
            if best is None or d < best[0]:
                best = (d, probe)
    return best


def holes(shape):
    seen = {}
    for f in shape.Faces:
        if f.Surface.TypeId != 'Part::GeomCylinder':
            continue
        r = round(f.Surface.Radius, 2)
        ax = f.Surface.Axis
        if abs(ax.z) > 0.9:
            d = 'Z (vertical)'
        elif abs(ax.x) > 0.9:
            d = 'X (horizontal)'
        elif abs(ax.y) > 0.9:
            d = 'Y (horizontal)'
        else:
            d = 'angled'
        seen.setdefault((r, d), 0)
        seen[(r, d)] += 1
    return seen


for name in PRINTED:
    o = doc.getObject(name)
    s = o.Shape
    bb = s.BoundBox
    print('=' * 78)
    print('%s   vol %.1f mm3   bbox %.1f x %.1f x %.1f'
          % (name, s.Volume, bb.XLength, bb.YLength, bb.ZLength))
    print('  solids=%d shells=%d valid=%s faces=%d'
          % (len(s.Solids), len(s.Shells), s.isValid(), len(s.Faces)))

    samples = sample_normals(s)
    total = sum(w for _, w in samples)
    print('  --- print orientation (support-needing area, >%.0f deg overhang) ---' % OVERHANG_LIMIT)
    rows = []
    for label, up in ORIENTS:
        bad = overhang_area(samples, up)
        a, b, h = footprint(s, up)
        rows.append((bad, label, a, b, h))
    rows.sort()
    for bad, label, a, b, h in rows:
        flag = '  <-- best' if (bad, label, a, b, h) == rows[0] else ''
        print('    %-20s support area %8.1f mm2 (%4.1f%%)  bed %.0fx%.0f  h=%.0f%s'
              % (label, bad, 100.0 * bad / total if total else 0, a, b, h, flag))

    mw = min_wall(s)
    if mw:
        print('  min wall between parallel faces: %.2f mm  at %s'
              % (mw[0], (round(mw[1].x, 1), round(mw[1].y, 1), round(mw[1].z, 1))))
    else:
        print('  min wall: none detected')

    hs = holes(s)
    if hs:
        print('  holes / round features:')
        for (r, d), n in sorted(hs.items()):
            print('    dia %5.2f  axis %-14s  x%d' % (r * 2, d, n))
    print()
