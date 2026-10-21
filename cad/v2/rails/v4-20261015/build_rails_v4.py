"""Arch rails v4 (2026-10-15, Claude). The master SideRailLeft/Right are NOT modified.

Run: freecadcmd build_rails_v4.py

Jim, 2026-10-15: the v3 rails still look like bridge towers; wants a geometric design that keeps strength without taking up so much space,
suggested an arch with mount points. Nuts secure the rail feet (screw from above, nut below). PETG will be used. Same deck-in-the-rails idea
as v3 (plain peg sockets), same shell hard points, foot screws at their current positions.
Frame: +Y front (mast), +X right, +Z up, origin rear-left of the aluminium deck. Left rail built here, right = mirror about X = 39.5 + a switch shelf.

Arch: elliptical head on two short vertical legs, band 8 wide (X10..18, inner face X18 so the part prints flat on its inner face, no supports under it),
6 thick radially. Legs stand clear of the foot screws; the screw heads are in open air above the foot blocks.
"""
import FreeCAD as A, Part, MeshPart, math, json, os, shutil, traceback
from pathlib import Path

V = A.Vector
R = Path('/home/buralien/projects/gladiator-cad')
O = R / 'cad/v2/rails/v4-20261015'
O.mkdir(parents=True, exist_ok=True)
W = Path('/tmp/railsv4')
W.mkdir(exist_ok=True)
shutil.copy(R / 'cad/enclosure/concept-20261013/Gladiator_Enclosure_Concept.FCStd', W / 'c.FCStd')

P = dict(
    # Jim 2026-10-15: thick enough that heat-set inserts go straight into the arch (7.5 deep + 1.0 floor = 8.5), no bosses, but no more.
    band_x=(9.5, 18.0), t_leg=7.0, t_apex=8.5,       # band 8.5 wide (X); radial thickness 7.0 at the legs (battery + screw-head limit) growing to 8.5 at the top
    yc=68.35, zc=24.0, a_c=51.15, b_c=21.5,          # centreline ellipse: leg centres Y17.2 (inner edge 20.7, clear of the battery) and Y119.5 (outer edge 123.0, clear of the front screw head)
    z_foot=6.0,
    foot_x=(6.0, 18.0), foot_rear_y=(2.0, 20.8), foot_front_y=(117.0, 135.0), foot_z=(2.0, 6.0),
    foot_screws=[(10.5, 10.0), (13.5, 127.0)], foot_hole_d=3.6,
    pegs=True,                       # False = flat pads, for use with the OLD printed deck (drill it; see README)
    peg_x=14.0, peg_w=3.0, peg_l=8.1, peg_h=3.7, sockets=[(23.85, 12.6), (68.35, 8.6), (112.85, 12.6)], pad_x=(9.5, 18.0), pad_extra=4.4,   # pegs on the rails (3.0 x 8.1 x 3.7, tray style); deck slots 3.6 x 8.6 (locating) or 12.6 (slotted)
    retention=[(14.0, 83.5)], insert_d=4.6, insert_depth=7.5,
    
    # right-rail switch shelf: the switch enclosure sits on it (see build_switch_box.py)
    shelf=dict(x=(61.0, 77.0), y=(-22.0, 6.5), z=(2.0, 12.0), insert_y=(-10.0, -1.0), insert_x=71.0),   # 2026-10-15: 3 mm further outboard than the first draft so the box clears the INA cassette (X60.4) by 3.4 mm
)
N = 60
p = P


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


def zcl(y):
    """centreline height of the arch at Y"""
    d = (y - p['yc']) / p['a_c']
    return p['zc'] + p['b_c'] * math.sqrt(max(0.0, 1 - d * d))


def arch_profile():
    yc, zc, zf = p['yc'], p['zc'], p['z_foot']
    ao, bo = p['a_c'] + p['t_leg'] / 2, p['b_c'] + p['t_apex'] / 2
    ai, bi = p['a_c'] - p['t_leg'] / 2, p['b_c'] - p['t_apex'] / 2
    pts = [(yc - ao, zf), (yc - ao, zc)]
    for k in range(1, N):
        th = math.pi - math.pi * k / N
        pts.append((yc + ao * math.cos(th), zc + bo * math.sin(th)))
    pts += [(yc + ao, zc), (yc + ao, zf), (yc + ai, zf), (yc + ai, zc)]
    for k in range(1, N):
        th = math.pi * k / N
        pts.append((yc + ai * math.cos(th), zc + bi * math.sin(th)))
    pts += [(yc - ai, zc), (yc - ai, zf)]
    return pts


x0b, x1b = p['band_x']
vs = [V(x0b, y, z) for y, z in arch_profile()]
arch = Part.Face(Part.makePolygon(vs + [vs[0]])).extrude(V(x1b - x0b, 0, 0))

parts = [arch,
         box(*p['foot_x'], *p['foot_rear_y'], *p['foot_z']),
         box(*p['foot_x'], *p['foot_front_y'], *p['foot_z'])]
holes = []
for (fx, fy) in p['foot_screws']:
    holes.append(Part.makeCylinder(p['foot_hole_d'] / 2, 10, V(fx, fy, p['foot_z'][0] - 2)))


def prism_yz(pts, x0, x1):
    vs_ = [V(x0, y, z) for y, z in pts]
    return Part.Face(Part.makePolygon(vs_ + [vs_[0]])).extrude(V(x1 - x0, 0, 0))


def prism_xz(pts, y0, y1):
    vs_ = [V(x, y0, z) for x, z in pts]
    return Part.Face(Part.makePolygon(vs_ + [vs_[0]])).extrude(V(0, y1 - y0, 0))


# the void under the arch: pads and gussets may fill the space ABOVE the extrados (the 'fan' under an overhang) but never intrude under the arch
yc_, zc_, zf_ = p['yc'], p['zc'], p['z_foot']
ai_ = p['a_c'] - p['t_leg'] / 2
bi_ = p['b_c'] - p['t_apex'] / 2
vpts = [(yc_ - ai_, zf_), (yc_ - ai_, zc_)]
for k in range(1, N):
    th = math.pi - math.pi * k / N
    vpts.append((yc_ + ai_ * math.cos(th), zc_ + bi_ * math.sin(th)))
vpts += [(yc_ + ai_, zc_), (yc_ + ai_, zf_)]
void = prism_yz(vpts, 0.0, 40.0)

# mount pads: deck-seat socket + shell hard points, each filled down to the arch so no pad overhangs air
# (A hard point for the front panels at the front pad was tried and dropped: its boss sits under the deck and the driver wedge, so the panel cannot rise along its forced 45 degree pull.)
PADS = [dict(y=(14.0, 41.0), socket=p['sockets'][0], hp=[(22.0, 40.0), (35.5, 46.0)]),   # rear: hood, one point under the deck socket (floor Z46.5) and one beside it
        dict(y=(56.0, 80.7), socket=p['sockets'][1], hp=[(59.0, 45.0)]),                 # middle: hood
        dict(y=(98.0, 122.0), socket=p['sockets'][2], hp=[])]                            # front: deck seat only
hp = []
for pd in PADS:
    parts.append(cut(box(p['pad_x'][0], p['pad_x'][1], pd['y'][0], pd['y'][1], 20.0, 54.5), void))
    sy, sl = pd['socket']
    for (hy, hz) in pd['hp']:
        holes.append(Part.makeCylinder(p['insert_d'] / 2, p['insert_depth'] + 1, V(x0b - 1, hy, hz), V(1, 0, 0)))     # straight into the pad / arch face
        hp.append(dict(y=hy, z=hz, owner='hood' if hy < 78.6 else 'front', face_x_left=x0b, face_x_right=79.0 - x0b))
# deck-seat pegs: the deck prints top-up, so the pegs live on the rails and the deck gets through slots (3.6 wide, bed-side opening chamfered)
def peg(cx, cy, w, l, h, ch=0.7):
    def rect(z, hw, hl):
        vs_ = [V(cx - hw, cy - hl, z), V(cx + hw, cy - hl, z), V(cx + hw, cy + hl, z), V(cx - hw, cy + hl, z)]
        return Part.makePolygon(vs_ + [vs_[0]])
    body_ = Part.makeLoft([rect(54.0, w / 2, l / 2), rect(54.5 + h - ch, w / 2, l / 2)], True, True)
    tip_ = Part.makeLoft([rect(54.5 + h - ch, w / 2, l / 2), rect(54.5 + h, w / 2 - ch, l / 2 - ch)], True, True)
    return fuse(body_, tip_)


for (sy, sl) in (p['sockets'] if p['pegs'] else []):
    parts.append(peg(p['peg_x'], sy, p['peg_w'], p['peg_l'], p['peg_h']))
for (rx, ry) in p['retention']:
    parts.append(cut(box(p['pad_x'][0], p['pad_x'][1], ry - 4, ry + 4, 20.0, 54.5), void))
    holes.append(Part.makeCylinder(p['insert_d'] / 2, p['insert_depth'] + 1, V(rx, ry, 54.5 - p['insert_depth'])))
# lateral fans at both leg bases (outer side, where there is room): triangle X6..9.5 rising 10 mm up the leg face
for (ly0, ly1) in ((yc_ - (p['a_c'] + p['t_leg'] / 2), yc_ - ai_), (yc_ + ai_, yc_ + (p['a_c'] + p['t_leg'] / 2))):
    parts.append(prism_xz([(6.0, 6.0), (x0b, 6.0), (x0b, 16.0)], ly0, ly1))
left = cut(fuse(*parts), *holes)

# right rail: mirror + switch shelf with fans
right = plain(left.mirror(V(39.5, 0, 0), V(1, 0, 0)))
sh = p['shelf']
shelf = box(sh['x'][0], sh['x'][1], sh['y'][0], sh['y'][1], sh['z'][0], sh['z'][1])
gus = [prism_yz([(sh['y'][1], 6.0), (sh['y'][1], sh['z'][1]), (sh['y'][1] + 6.7, 6.0)], 61.0, 65.2),         # fans from the shelf back down to the foot block,
       prism_yz([(sh['y'][1], 6.0), (sh['y'][1], sh['z'][1]), (sh['y'][1] + 6.7, 6.0)], 71.3, 77.0)]         # either side of the foot-screw head
right = fuse(right, shelf, *gus)
right = cut(right, *[Part.makeCylinder(p['insert_d'] / 2, p['insert_depth'] + 1, V(sh['insert_x'], iy, sh['z'][1] - p['insert_depth'])) for iy in sh['insert_y']])
PARTS = {'Arch_Rail_Left_v4': left, 'Arch_Rail_Right_v4': right}

# ------------------------------------------------------------------ checks vs the chassis references
d = A.openDocument(str(W / 'c.FCStd'))
skip = ('Ref_UpperDeck', 'Ref_SideRail', 'Ref_PowerBoardTray', 'Ref_Base', 'Ref_INA226', 'Ref_BoardReference', 'Ref_PowerSwitchHolder', 'Ref_Switch', 'Head_',
        'Rear_Hood', 'Front_', 'Lens_', 'Track_Approx', 'Wheel_Approx', 'Antenna')
refs = {o.Name: plain(o.Shape) for o in d.Objects if o.Name.startswith('Ref_') and not o.Name.startswith(skip)}
chk = dict(status='v4 ARCH DRAFT - not printed, not fitted', parameters=P, parts={}, collisions=[], nearest={}, hardpoints=hp)
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
chk['old_rail_volume_mm3'] = round(d.getObject('Ref_SideRailLeft').Shape.Volume, 1)
# arch geometry facts: normal thickness along the band
yc, zc = p['yc'], p['zc']
ao, bo = p['a_c'] + p['t_leg'] / 2, p['b_c'] + p['t_apex'] / 2
ai, bi_ = p['a_c'] - p['t_leg'] / 2, p['b_c'] - p['t_apex'] / 2


def normal_thickness(y):
    d = (y - yc) / ao
    if abs(d) >= 1:
        return None
    th = math.acos(d)
    ox, oz = yc + ao * math.cos(th), zc + bo * math.sin(th)
    return min(math.hypot(ox - (yc + ai * math.cos(u * math.pi / 720)), oz - (zc + bi_ * math.sin(u * math.pi / 720))) for u in range(0, 721))


chk['arch'] = dict(normal_thickness_mm={str(y): round(normal_thickness(y), 2) for y in (24, 30, 36, 40, 48, 56, 68, 76, 90, 100)},
                   insert_floor_mm=round(p['band_x'][1] - p['band_x'][0] - p['insert_depth'], 2),
                   apex_extrados_z=round(zc + bo, 2), leg_bands_y=[round(yc - ao, 2), round(yc - ai, 2), round(yc + ai, 2), round(yc + ao, 2)])

doc = A.newDocument('Gladiator_ArchRails_v4')
for n, s in PARTS.items():
    o = doc.addObject('Part::Feature', n)
    o.Shape = s
doc.recompute()
doc.saveAs(str(O / 'Gladiator_ArchRails_v4.FCStd'))
Part.export([doc.getObject(n) for n in PARTS], str(O / 'Gladiator_ArchRails_v4.step'))
stl = {}
for n, s in PARTS.items():
    c = plain(s)
    c.rotate(V(0, 0, 0), V(0, 1, 0), 90 if n.endswith('Left_v4') else -90)       # lie on the inner face
    c.translate(V(-c.BoundBox.XMin, -c.BoundBox.YMin, -c.BoundBox.ZMin))
    m = MeshPart.meshFromShape(Shape=c, LinearDeflection=0.02, AngularDeflection=math.radians(8))
    m.write(str(O / ('Gladiator_%s.stl' % n)))
    bb = c.BoundBox
    stl[n] = dict(is_solid=m.isSolid(), non_manifold=m.hasNonManifolds(), size_mm=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)])
chk['stl'] = stl
(O / 'validation.json').write_text(json.dumps(chk, indent=1, default=str))
(O / 'hardpoints.json').write_text(json.dumps(dict(hardpoints=hp, shelf=sh), indent=1))
print(json.dumps({k: chk[k] for k in ('parts', 'collisions', 'nearest', 'old_rail_volume_mm3', 'stl', 'arch', 'hardpoints')}, indent=1, default=str), flush=True)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(17, 10))

    def sl(ax, shape, nrm, val, ix, iz, color):
        for w in shape.slice(nrm, val):
            pts = w.discretize(200)
            ax.plot([getattr(q, ix) for q in pts], [getattr(q, iz) for q in pts], color=color, lw=1.4)
    sl(axs[0][0], left, V(1, 0, 0), 14.0, 'y', 'z', '#c0392b')
    # battery and deck for context
    for nm, col in (('Ref_BatteryBox', '#7f8c8d'), ('Ref_ChassisDeck', '#34495e'), ('Ref_MastBase', '#16a085')):
        sl(axs[0][0], refs[nm], V(1, 0, 0), 20.0 if nm != 'Ref_MastBase' else 30.0, 'y', 'z', col)
    axs[0][0].set_title('LEFT arch, side section X=14 (red) with battery, decks and mast base for context', fontsize=9)
    sl(axs[0][1], right, V(1, 0, 0), 65.0, 'y', 'z', '#1565c0')
    sl(axs[0][1], right, V(1, 0, 0), 67.0, 'y', 'z', '#90caf9')
    axs[0][1].set_title('RIGHT arch with switch shelf (X=65 dark, X=67 light)', fontsize=9)
    sl(axs[1][0], left, V(0, 1, 0), 68.5, 'x', 'z', '#c0392b')
    sl(axs[1][0], left, V(0, 1, 0), 30.0, 'x', 'z', '#e57373')
    sl(axs[1][0], left, V(0, 1, 0), 56.0, 'x', 'z', '#ef9a9a')
    axs[1][0].set_title('LEFT cross sections: Y=68.5 (locating socket), Y=30 and Y=56 (hard-point bosses)', fontsize=9)
    sl(axs[1][1], left, V(0, 0, 1), 10.0, 'x', 'y', '#c0392b')
    sl(axs[1][1], right, V(0, 0, 1), 8.0, 'x', 'y', '#1565c0')
    axs[1][1].set_title('Plan sections: feet (Z=10 left, Z=8 right with shelf)', fontsize=9)
    for ax in axs.flat:
        ax.set_aspect('equal'); ax.grid(alpha=.3)
    fig.savefig(str(O / 'arch_rails_v4_sections.png'), dpi=65, bbox_inches='tight')
except Exception:
    traceback.print_exc()
os._exit(0)
