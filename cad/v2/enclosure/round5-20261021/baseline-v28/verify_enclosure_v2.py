"""Gladiator enclosure v2 verification (2026-10-13, Claude).

Run:  freecadcmd verify_enclosure_v2.py
Reads Gladiator_Enclosure_v2.FCStd (written by build_enclosure_v2.py) and writes removal-sweeps.json.

What it proves (rigid-body, straight-line translations only; no flex, no rotation, no printed tolerance):
  * rear hood: how far it slides straight back with the front panels on / off
  * front panels: free travel along the 45 degree outboard-and-up pull, 1 mm resolution, head ON
  * left panel: the two-leg path (45 degree pull, then a 15 degree outward slide) and its margin
  * roof-screw access: free height above each screw head
"""
import FreeCAD as A, Part, math, json, time, traceback, os
from pathlib import Path

V = A.Vector
O = Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/v2-20261013')


def plain(s):
    q = Part.Shape()
    q.importBrepFromString(s.exportBrepToString())
    return q


def P(*a):
    print(*a, flush=True)


OUT = {}
try:
    d = A.openDocument(str(O / 'Gladiator_Enclosure_v2.FCStd'))
    sh = {o.Name: plain(o.Shape) for o in d.Objects if not o.Shape.isNull()}
    PAN = ('Rear_Hood', 'Front_Left', 'Front_Right')
    base = [n for n in sh if n.startswith(('Ref_', 'Head_', 'Track_Approx', 'Wheel_Approx'))]

    def obst(exclude):
        return [(n, sh[n]) for n in base + [p for p in PAN if p not in exclude]]

    def hit(shape, dv, t, obs, thr=0.3):
        m = plain(shape)
        m.translate(dv * t)
        mb = m.BoundBox
        for n, o in obs:
            if not mb.intersect(o.BoundBox):
                continue
            try:
                v = m.common(o).Volume
            except Exception:
                v = 1.0 if m.distToShape(o)[0] < 0.01 else 0.0
            if v > thr:
                return n
        return None

    def free_travel(name, dv, obs, maxd, step):
        dv = V(dv.x, dv.y, dv.z)
        dv.normalize()
        free = 0
        for t in range(step, maxd + 1, step):
            h = hit(sh[name], dv, t, obs)
            if h:
                return free, h
            free = t
        return free, None

    t0 = time.time()
    # hood, rearward
    f, b = free_travel('Rear_Hood', V(0, -1, 0), obst(('Rear_Hood', 'Front_Left', 'Front_Right')), 150, 2)
    OUT['hood_back_front_panels_off'] = dict(free_mm=f, blocked_by=b, tested_to_mm=150)
    f, b = free_travel('Rear_Hood', V(0, -1, 0), obst(('Rear_Hood',)), 150, 2)
    OUT['hood_back_front_panels_on'] = dict(free_mm=f, blocked_by=b, tested_to_mm=150)
    P('hood', OUT['hood_back_front_panels_off'], OUT['hood_back_front_panels_on'])

    # right panel, 45 degrees outboard-up, head on
    f, b = free_travel('Front_Right', V(1, 0, 1), obst(('Front_Right',)), 120, 1)
    OUT['front_right_45deg_pull'] = dict(free_mm=f, blocked_by=b, tested_to_mm=120)
    P('right', OUT['front_right_45deg_pull'])

    # left panel
    obs = obst(('Front_Left',))
    nv = V(-1, 0, 1)
    nv.normalize()
    f, b = free_travel('Front_Left', nv, obs, 45, 1)
    OUT['front_left_leg1_45deg_pull'] = dict(free_mm=f, blocked_by=b)
    ex = V(-math.cos(math.radians(15)), 0, math.sin(math.radians(15)))
    t_clear = None
    for t in range(10, f + 1):
        shp = plain(sh['Front_Left'])
        shp.translate(nv * t)
        ok = True
        for s_ in range(3, 91, 3):
            if hit(shp, ex, s_, obs):
                ok = False
                break
        if ok:
            t_clear = t
            break
    OUT['front_left_two_leg_path'] = dict(
        leg1='pull outboard-and-up at 45 degrees', leg1_needed_mm=t_clear, leg1_available_mm=f,
        slack_mm=(f - t_clear) if t_clear is not None else None,
        leg2='then slide outboard at 15 degrees elevation (90 mm tested, free)' if t_clear is not None else 'NO PATH FOUND')
    P('left', OUT['front_left_two_leg_path'])

    # coarse direction rings (3 mm steps) for the two front panels: shows the 45 degree pull is the only exit
    ring = {}
    for nm in ('Front_Right', 'Front_Left'):
        best = []
        for el in range(0, 91, 15):
            for az in range(0, 360, 15):
                if el == 90 and az > 0:
                    continue
                e, a = math.radians(el), math.radians(az)
                dv = V(math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e))
                fr, bl = free_travel(nm, dv, obst((nm,)), 60, 3)
                best.append((fr, 'el%d az%d' % (el, az), bl))
        best.sort(key=lambda t: -t[0])
        ring[nm] = [dict(free_mm=f_, direction=d_, blocked_by=b_) for f_, d_, b_ in best[:4]]
        P(nm, 'best straight pulls (60 mm cap):', ring[nm])
    OUT['front_straight_pull_ring_60mm_cap'] = ring

    # roof-screw access
    acc = []
    heads = [(n, sh[n]) for n in sh if n.startswith('Head_')]
    for (x, y) in ((22, 72), (33, 72), (50, 72), (66, 72)):
        col = Part.makeCylinder(5, 160, V(x, y, 109))
        zmin = None
        for n, o in heads:
            if not col.BoundBox.intersect(o.BoundBox):
                continue
            try:
                c = col.common(o)
            except Exception:
                continue
            if c.Volume > 0.05:
                z = c.BoundBox.ZMin
                zmin = z if zmin is None else min(zmin, z)
        acc.append(dict(screw_xy=[x, y], free_height_above_roof_mm=None if zmin is None else round(zmin - 108, 1)))
    OUT['roof_screw_access_10mm_column'] = acc
    P('access', acc)
    OUT['runtime_s'] = round(time.time() - t0, 1)
    OUT['limits'] = ('Rigid straight-line sweeps against the modelled references (head in its modelled pose, simplified '
                     'tracks). No printed tolerance, no wiring, no flex, no rotation. Free = no volume overlap above 0.3 mm3.')
    (O / 'removal-sweeps.json').write_text(json.dumps(OUT, indent=2))
except BaseException:
    traceback.print_exc()
os._exit(0)
