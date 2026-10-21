"""Side rails v3 (2026-10-14, Claude). The master's SideRailLeft/Right are NOT modified.

Run: freecadcmd build_rails_v3.py

Jim's brief (2026-10-14): skinnier rails, no floor between legs and runner, easy access to the foot screws (which DO align),
the upper deck sits IN the rails like the power board tray sat in its feet (the six deck screws almost never lined up),
natural hard points for the optional shell, holes to pass wires from the rails through the deck, and a power switch that works with
or without the shell. Frame: +Y front (mast), +X right, +Z up, origin rear-left of the aluminium deck.

Left rail = built here; right rail = mirror about X = 39.5 plus the switch arm.
ASSUMED (not measured): see README.md.
"""
import FreeCAD as A, Part, MeshPart, math, json, os, shutil, traceback
from pathlib import Path

V = A.Vector
R = Path('/home/buralien/projects/gladiator-cad')
O = R / 'cad/v2/rails/v3-20261014'
O.mkdir(parents=True, exist_ok=True)
W = Path('/tmp/railsv3')
W.mkdir(exist_ok=True)
shutil.copy(R / 'cad/enclosure/concept-20261013/Gladiator_Enclosure_Concept.FCStd', W / 'v2.FCStd')   # Codex concept: untouched source of the chassis references

P = dict(
    y0=2.0, y1=135.0,
    outer_x=6.0, runner_w=9.0,                    # runner X6..15 (the old rail was X6..18)
    slab_z=(43.5, 54.5), web_x=(8.5, 12.5), web_z=(37.0, 43.5),   # inverted T, no floor, soffit Z37.0 (was 36.5)
    rear_leg=dict(x=(6.0, 16.0), y=(2.0, 15.0)), front_leg=dict(x=(6.0, 18.0), y=(119.0, 135.0)),
    foot_z=(2.0, 6.0),
    foot_screws=[(10.5, 10.0), (13.5, 127.0)],     # as in the master rails; Jim: they align
    shaft_d=6.4, foot_hole_d=3.6,                  # open vertical access straight down to the foot, nothing in the way
    # deck seats in plain peg sockets, tray-style (0.25 clearance on a 3.0 x 8.1 peg): one locating socket, two slotted along Y
    peg_x=10.5, peg_w=3.6, sockets=[(22.0, 12.6), (68.0, 8.6), (114.0, 12.6)], socket_z0=42.5,
    # optional retention screw per rail (deck gets a slotted hole): vertical insert D4.6 x 7.5
    retention=[(10.5, 85.0)], insert_d=4.6, insert_depth=7.5,
    # hard points for the optional shell: horizontal inserts in the outer face
    hardpoints=[(36.0, 49.0), (52.0, 49.0)],
    wire_ports=[(10.5, 44.0), (10.5, 92.0)], port_d=6.0,
    # switch arm (right rail only). Switch: 6.8 x 12.7 x 6.37, knob 5.0 proud x 4.0, envelope 6.0 (measurements/components.md)
    arm_cx=66.0, arm_w=14.0, arm_cz=40.0, arm_h=16.8, arm_y=(-27.3, 3.0), sw_body=(6.8, 12.7, 6.37), sw_clear=0.3,
    bezel_t=1.2, bezel_screw_dx=5.3,
)


def plain(s):
    q = Part.Shape()
    q.importBrepFromString(s.exportBrepToString())
    return q


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def fuse(*s):
    r = plain(s[0])
    for x in s[1:]:
        r = plain(r.fuse(plain(x)))
    return plain(r.removeSplitter())


def cut(a, *s):
    a = plain(a)
    for x in s:
        a = plain(a.cut(plain(x)))
    return plain(a.removeSplitter())


p = P
y0, y1 = p['y0'], p['y1']
zs0, zs1 = p['slab_z']
zf0, zf1 = p['foot_z']
rl, fl = p['rear_leg'], p['front_leg']

# ----------------------------------------------------------------- left rail
solid = [box(p['outer_x'], p['outer_x'] + p['runner_w'], y0, y1, zs0, zs1),                       # runner slab
         box(p['web_x'][0], p['web_x'][1], y0, y1, p['web_z'][0], zs0),                           # web
         box(rl['x'][0], rl['x'][1], rl['y'][0], rl['y'][1], zf0, zs0),                           # rear leg
         box(fl['x'][0], fl['x'][1], fl['y'][0], fl['y'][1], zf0, zs0),                           # front leg
         box(fl['x'][0], fl['x'][1], fl['y'][0], fl['y'][1], zs0, zs1),                           # front slab wing (covers the O6.4 shaft)
         box(6.0, 18.0, rl['y'][0], rl['y'][1], zf0, zf1),                                        # rear foot
         box(6.0, 18.0, fl['y'][0], fl['y'][1], zf0, zf1)]                                        # front foot
body = fuse(*solid)
holes = []
for (fx, fy) in p['foot_screws']:
    holes.append(Part.makeCylinder(p['shaft_d'] / 2, 60, V(fx, fy, zf1)))                         # open access shaft from the top
    holes.append(Part.makeCylinder(p['foot_hole_d'] / 2, 10, V(fx, fy, zf0 - 2)))                 # foot hole
for (sy, sl) in p['sockets']:
    holes.append(box(p['peg_x'] - p['peg_w'] / 2, p['peg_x'] + p['peg_w'] / 2, sy - sl / 2, sy + sl / 2, p['socket_z0'], zs1 + 1))
for (rx, ry) in p['retention']:
    holes.append(Part.makeCylinder(p['insert_d'] / 2, p['insert_depth'], V(rx, ry, zs1 - p['insert_depth'])))
    holes[-1] = Part.makeCylinder(p['insert_d'] / 2, p['insert_depth'] + 1, V(rx, ry, zs1 - p['insert_depth']))
for (hy, hz) in p['hardpoints']:
    holes.append(Part.makeCylinder(p['insert_d'] / 2, p['insert_depth'] + 1, V(p['outer_x'] - 1, hy, hz), V(1, 0, 0)))
for (px, py) in p['wire_ports']:
    holes.append(Part.makeCylinder(p['port_d'] / 2, 40, V(px, py, p['web_z'][0] - 2)))
left = cut(body, *holes)

# ----------------------------------------------------------------- right rail = mirror + switch arm
right = plain(left.mirror(V(39.5, 0, 0), V(1, 0, 0)))
cx, cz = p['arm_cx'], p['arm_cz']
bw, bl, bd = p['sw_body']
cl = p['sw_clear']
ay0, ay1 = p['arm_y']
arm = box(cx - p['arm_w'] / 2, cx + p['arm_w'] / 2, ay0, ay1, cz - p['arm_h'] / 2, cz + p['arm_h'] / 2)
right = fuse(right, arm)
pocket_len = bd + cl
bulk0 = ay0 + pocket_len                      # body rear face rests here
bulk1 = bulk0 + 2.0
cav = box(cx - (bw + cl) / 2, cx + (bw + cl) / 2, ay0 - 1, 2.0, cz - (bl + cl) / 2, cz + (bl + cl) / 2)
bulkhead = box(cx - (bw + cl) / 2 - 0.5, cx + (bw + cl) / 2 + 0.5, bulk0, bulk1, cz - (bl + cl) / 2 - 0.5, cz + (bl + cl) / 2 + 0.5)
pinwin = box(cx - 2.7, cx + 2.7, bulk0 - 0.5, bulk1 + 0.5, cz - 5.5, cz + 5.5)
exitwin = box(cx - 3.5, cx + 3.5, -9.0, -1.0, cz - p['arm_h'] / 2 - 1, cz - 6.0)
pilots = [Part.makeCylinder(2.35 / 2, 6.0, V(cx + sg * p['bezel_screw_dx'], ay0, cz), V(0, 1, 0)) for sg in (1, -1)]
right = cut(right, cav)
right = fuse(right, bulkhead)
right = cut(right, pinwin, exitwin, *pilots)
# bezel (separate part): clamps the switch body, knob slot 4.6 x 8.0
bezel = box(cx - p['arm_w'] / 2, cx + p['arm_w'] / 2, ay0 - p['bezel_t'], ay0, cz - p['arm_h'] / 2, cz + p['arm_h'] / 2)
bezel = cut(bezel, box(cx - 2.3, cx + 2.3, ay0 - 3, ay0 + 1, cz - 4.0, cz + 4.0),
            *[Part.makeCylinder(2.6 / 2, 5, V(cx + sg * p['bezel_screw_dx'], ay0 - 3, cz), V(0, 1, 0)) for sg in (1, -1)])
knob_tip_y = ay0 - p['bezel_t'] - (5.0 - 1.2)

PARTS = {'SideRail_Left_v3': left, 'SideRail_Right_v3': right, 'Switch_Bezel_v3': bezel}

# ----------------------------------------------------------------- checks against the current chassis references
d = A.openDocument(str(W / 'v2.FCStd'))
skip = ('Ref_SideRail', 'Ref_PowerBoardTray', 'Ref_Base', 'Ref_INA226', 'Ref_BoardReference', 'Ref_PowerSwitchHolder', 'Ref_Switch', 'Head_',
        'Rear_Hood', 'Front_', 'Lens_', 'Switch_Bezel', 'Track_Approx', 'Wheel_Approx')
refs = {o.Name: plain(o.Shape) for o in d.Objects if o.Name.startswith('Ref_') and not o.Name.startswith(skip)}
chk = dict(status='v3 DRAFT - not printed, not fitted; assumptions in README.md', parameters={k: v for k, v in P.items()}, parts={}, collisions=[], nearest={},
           knob_tip_y=round(knob_tip_y, 2), references_used=sorted(refs))
for name, s in PARTS.items():
    bb = s.BoundBox
    chk['parts'][name] = dict(valid=s.isValid(), solids=len(s.Solids), volume_mm3=round(s.Volume, 1),
                              bbox=[round(v, 1) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)])
    rows = []
    for rn, rs in refs.items():
        if not s.BoundBox.intersect(rs.BoundBox) and s.distToShape(rs)[0] > 30:
            continue
        try:
            v = s.common(rs).Volume
        except Exception:
            v = 0.0
        if v > 0.01:
            chk['collisions'].append(dict(part=name, ref=rn, volume_mm3=round(v, 3)))
        else:
            rows.append((round(s.distToShape(rs)[0], 2), rn))
    rows.sort()
    chk['nearest'][name] = rows[:6]
# original rails for a volume comparison
orig = d.getObject('Ref_SideRailLeft').Shape
chk['old_rail_volume_mm3'] = round(orig.Volume, 1)

# STLs and native/step
doc = A.newDocument('Gladiator_Rails_v3')
for n, s in PARTS.items():
    o = doc.addObject('Part::Feature', n)
    o.Shape = s
doc.recompute()
doc.saveAs(str(O / 'Gladiator_Rails_v3.FCStd'))
Part.export([doc.getObject(n) for n in PARTS], str(O / 'Gladiator_Rails_v3.step'))
stl = {}
for n, s in PARTS.items():
    c = plain(s)
    c.translate(V(-c.BoundBox.XMin, -c.BoundBox.YMin, -c.BoundBox.ZMin))
    m = MeshPart.meshFromShape(Shape=c, LinearDeflection=0.03, AngularDeflection=math.radians(10))
    m.write(str(O / ('Gladiator_%s.stl' % n)))
    bb = c.BoundBox
    stl[n] = dict(is_solid=m.isSolid(), non_manifold=m.hasNonManifolds(), size_mm=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)])
chk['stl'] = stl
(O / 'validation.json').write_text(json.dumps(chk, indent=1, default=str))
print(json.dumps({k: chk[k] for k in ('parts', 'collisions', 'nearest', 'old_rail_volume_mm3', 'stl', 'knob_tip_y')}, indent=1, default=str), flush=True)

# ----------------------------------------------------------------- section images
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(16, 11))

    def sl(ax, shape, nrm, val, ix, iz, color):
        for w in shape.slice(nrm, val):
            pts = w.discretize(150)
            ax.plot([getattr(q, ix) for q in pts], [getattr(q, iz) for q in pts], color=color, lw=1.4)
    sl(axs[0][0], left, V(1, 0, 0), 10.5, 'y', 'z', '#c0392b')
    axs[0][0].set_title('LEFT rail, side section X=10.5: foot shafts, 3 peg sockets, retention insert, wire ports', fontsize=9)
    sl(axs[0][1], left, V(0, 1, 0), 68.0, 'x', 'z', '#c0392b')
    sl(axs[0][1], left, V(0, 1, 0), 36.0, 'x', 'z', '#e57373')
    axs[0][1].set_title('LEFT rail cross sections: Y=68 (socket) and Y=36 (hard-point insert)', fontsize=9)
    sl(axs[1][0], right, V(1, 0, 0), 68.5, 'y', 'z', '#1565c0')
    axs[1][0].set_title('RIGHT rail with switch arm, side section X=68.5', fontsize=9)
    sl(axs[1][1], right, V(0, 0, 1), 40.0, 'x', 'y', '#1565c0')
    sl(axs[1][1], left, V(0, 0, 1), 49.0, 'x', 'y', '#c0392b')
    sl(axs[1][1], right, V(0, 0, 1), 49.0, 'x', 'y', '#1565c0')
    axs[1][1].set_title('Plan sections: Z=49 both rails (hard points), Z=40 right arm', fontsize=9)
    for ax in axs.flat:
        ax.set_aspect('equal'); ax.grid(alpha=.3)
    fig.savefig(str(O / 'rails_v3_sections.png'), dpi=65, bbox_inches='tight')
except Exception:
    traceback.print_exc()
os._exit(0)
