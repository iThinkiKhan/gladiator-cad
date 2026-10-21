"""Power switch holder v3 (2026-10-16, Claude): the holder Jim already has (v1b idea: pocket, knob window, FRONT side open for the pins and leads, so a switch that is ALREADY WIRED slides in),
a little stronger, with a real mounting point for covered (hood shelf) or uncovered (right rail shelf) use.

Run: freecadcmd build_switch_holder_v3.py

Jim 2026-10-16: the switch is already wired and cannot be unwired; he wants essentially the holder he has, slightly stronger, with a better mount point for covered or uncovered operation, mounted from the
interior of the shell, and NO reprint of the rails (the printed right rail already has the shelf with two inserts).
What it is: a closed rectangular tube, 14.5 x 17.9, with a 2.0 mm front wall carrying the knob slot; the switch body is pushed in from the OPEN REAR knob-first, so the soldered leads trail out of the open rear.
It is held by two M2 screws through the side walls (they press the metal body, removable) and the leads leave through the open 9 mm shroud.
Mounting: two M3 screws go DOWN from the top (heads inside the shell, nothing visible outside) through two slots 5.0 (X) x 3.6 (Y), 9 mm apart, into the two heat-set inserts of the shelf. The slots take +-0.7 mm of
position error in X (the rail's real shelf position is only known to about that).
Frame as v1: x' lateral (centred), y' 0 = pocket front, the front wall is y' -2.0..0, rear open at y' L, z' 0 = floor underside.
"""
import FreeCAD as A, Part, MeshPart, math, json, os, traceback
from pathlib import Path

V = A.Vector
R = Path('/home/buralien/projects/gladiator-cad')
O = R / 'cad/v2/switch-enclosure/v3-20261016'
O.mkdir(parents=True, exist_ok=True)

P = dict(W=14.5, floor=2.7, top=1.7, L=18.0, body=(6.8, 12.7, 6.37), clear=0.4, front_t=2.0, shroud_w=9.0, screw_y=(12.0,), screw_slot=(5.0, 3.6),
         knob_slot=(4.6, 8.0), chamfer=0.7, m2_pilot=2.2)
p = P
bw, bl, bd = p['body']
cw, ch = bw + 2 * p['clear'], bl + 2 * p['clear']        # pocket 7.6 wide x 13.5 tall (0.15 per side, as v1b)
H = p['floor'] + ch + p['top']                           # 17.9 (the shell window was sized for 17.9)
zc = p['floor'] + ch / 2
pocket_len = bd + 0.3


def plain(s):
    q = Part.Shape()
    q.importBrepFromString(s.exportBrepToString())
    return q


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cut(a, *s):
    a = plain(a)
    for x in s:
        a = plain(a.cut(plain(x)))
    return plain(a.removeSplitter())


def rect_w(cx, cy, w, l, z):
    vs = [V(cx - w / 2, cy - l / 2, z), V(cx + w / 2, cy - l / 2, z), V(cx + w / 2, cy + l / 2, z), V(cx - w / 2, cy + l / 2, z)]
    return Part.makePolygon(vs + [vs[0]])


W2 = p['W'] / 2


def rbox(x0, x1, y0, y1, z0, z1, r):
    """box with its Z-parallel edges rounded (wall joints: no sharp inside corners to start a crack, and the perimeters turn instead of butting)"""
    b_ = box(x0, x1, y0, y1, z0, z1)
    es = [e for e in b_.Edges if abs(e.tangentAt(e.FirstParameter).z) > 0.99]
    return b_.makeFillet(r, es)


body = rbox(-W2, W2, -p['front_t'], p['L'], 0, H, 1.0)                                 # outside vertical corners R1.0
cuts = [box(-cw / 2, cw / 2, 0, pocket_len, p['floor'], p['floor'] + ch),                          # pocket (sharp inside corners)
        box(-p['shroud_w'] / 2, p['shroud_w'] / 2, pocket_len, p['L'] + 1, p['floor'], p['floor'] + ch),   # open rear: pins and soldered leads (9 wide), the body is pushed in through here
        box(-cw / 2, cw / 2, pocket_len - 0.1, p['L'] + 1, p['floor'], p['floor'] + ch)]            # same height, pocket width kept all the way to the rear so the body slides in
kw, kh = p['knob_slot']
cuts.append(box(-kw / 2, kw / 2, -p['front_t'] - 1, 0.5, zc - kh / 2, zc + kh / 2))                # knob slot through the front wall
sw_, sl_ = p['screw_slot']
for sy in p['screw_y']:
    cuts.append(box(-sw_ / 2, sw_ / 2, sy - sl_ / 2, sy + sl_ / 2, -1, H + 1))                     # M3 slot, top to floor (heads inside the shell)
    cuts.append(Part.makeLoft([rect_w(0, sy, sw_ + 2 * p['chamfer'], sl_ + 2 * p['chamfer'], 0.0), rect_w(0, sy, sw_, sl_, p['chamfer'])], True, True))   # chamfer on the floor underside (glass bed)
for sg in (1, -1):                                                                                  # two M2 pilot holes through the side walls: the screw tips press on the metal switch body
    cuts.append(Part.makeCylinder(p['m2_pilot'] / 2, W2 - cw / 2 + 0.5, V(sg * (cw / 2 - 0.4), 3.2, zc), V(sg, 0, 0)))
holder = cut(body, *cuts)
PARTS = {'Switch_Holder_v3': holder}

chk = dict(status='v3 DRAFT - not printed', parameters=P, height_mm=H, knob_centre_above_floor_underside_mm=round(zc, 2), parts={})
bb = holder.BoundBox
chk['parts']['Switch_Holder_v3'] = dict(valid=holder.isValid(), solids=len(holder.Solids), volume_mm3=round(holder.Volume, 1),
                                        size_mm=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)])


def vol(a, b):
    try:
        return round(a.common(b).Volume, 3)
    except Exception:
        return None


sw_body = box(-bw / 2, bw / 2, 0.15, 0.15 + bd, zc - bl / 2, zc + bl / 2)
sw_knob = box(-2.0, 2.0, 0.15 - 5.0, 0.15, zc - 3.0, zc + 3.0)
sw_pins = box(-2.5, 2.5, 0.15 + bd, 0.15 + bd + 3.7, zc - 5.0, zc + 5.0)
sw_leads = box(-3.0, 3.0, 0.15 + bd + 3.7, p['L'] + 20, zc - 5.5, zc + 5.5)
slide_path = box(-bw / 2, bw / 2, 0.15, p['L'] + 30, zc - bl / 2, zc + bl / 2)               # the body pushed in from the rear along -Y
chk['fit'] = dict(body_vs_holder=vol(sw_body, holder), knob_vs_holder=vol(sw_knob, holder), pins_vs_holder=vol(sw_pins, holder), leads_vs_holder=vol(sw_leads, holder),
                  slide_in_from_rear_path_vs_holder=vol(slide_path, holder), knob_tip_beyond_front_wall_mm=round(5.0 - p['front_t'] - 0.15, 2),
                  m2_pilots_reach_body_clearance_mm=round(cw / 2 - bw / 2, 2),   # an M2 x 8 reaches it with 3.35 mm of wall to thread into
                  screw_slot_x_play_each_side_mm=round((sw_ - 3.0) / 2, 2))
chk['mounting'] = dict(screws='ONE M3 x 25 (head + washer inside the shell/above the shelf) down through the 5.0 x 3.6 slot into the first shelf insert',
                       length_check='top 1.7 + cavity 13.5 + floor 2.7 + insert 7.5 = 25.4: use M3 x 25 and a 7 mm washer; the screw passes beside the leads in the 9 mm shroud (3 mm each side)')

# placements: hood shelf (covered) at X71 (hood geometry), right rail shelf (uncovered) at the REAL printed-rail insert position
SPL = math.atan(1.0 / 89.0)
rail_ins_x = 71.0 + 2.0 + SPL * (-10.0 - 23.85)      # right rail moved 2.0 mm out and turned about its rear peg (CAD insert X71)
PL = {'hood_shelf': dict(x=71.0, y_front=-29.4, z_floor=30.5), 'rail_shelf_real': dict(x=round(rail_ins_x, 2), y_front=-22.0, z_floor=12.0)}
chk['placements'] = PL
checks = {}
try:
    rd = A.openDocument(str(R / 'cad/v2/rails/v4-20261015/Gladiator_ArchRails_v4.FCStd'))
    rr = plain(rd.getObject('Arch_Rail_Right_v4').Shape)
    rr.translate(V(2.0, 0, 0))
    rr.rotate(V(67.0, 23.85, 0), V(0, 0, 1), -math.degrees(SPL))
    cd = A.openDocument(str(R / 'cad/enclosure/concept-20261013/Gladiator_Enclosure_Concept.FCStd'))
    refs = {o.Name: plain(o.Shape) for o in cd.Objects if o.Name.startswith(('Ref_', 'Track_Approx', 'Wheel_Approx')) and not o.Name.startswith(('Ref_SideRail', 'Ref_PowerBoardTray', 'Ref_Base', 'Ref_BoardReference', 'Ref_PowerSwitchHolder', 'Ref_Switch'))}
    refs['Rail_Right_real'] = rr
    ina = {k: v for k, v in refs.items() if 'INA226' in k}
    for pl_name, pl in PL.items():
        c = plain(holder)
        c.translate(V(pl['x'], pl['y_front'], pl['z_floor']))
        res = {}
        for nm, rs in refs.items():
            if c.BoundBox.intersect(rs.BoundBox):
                v_ = vol(c, rs)
                if v_ is None or v_ > 0.01:
                    res[nm] = v_
        checks[pl_name + '_overlaps'] = res or 'none'
        checks[pl_name + '_nearest_INA_mm'] = round(min(c.distToShape(rs)[0] for rs in ina.values()), 2)
        if pl_name.startswith('rail'):
            checks['rail_shelf_slot_x_range_vs_shelf_insert'] = dict(insert_x=round(rail_ins_x, 2), slot_x_range=[round(pl['x'] - sw_ / 2, 2), round(pl['x'] + sw_ / 2, 2)])
            checks['rail_shelf_holder_gap_to_track_mm'] = round(min(c.distToShape(refs[k])[0] for k in refs if k.startswith(('Track', 'Wheel'))), 2)
except Exception:
    traceback.print_exc()
chk['placement_checks'] = checks

doc = A.newDocument('Gladiator_SwitchHolder_v3')
for n, s in PARTS.items():
    o = doc.addObject('Part::Feature', n)
    o.Shape = s
doc.recompute()
doc.saveAs(str(O / 'Gladiator_SwitchHolder_v3.FCStd'))
Part.export([doc.getObject(n) for n in PARTS], str(O / 'Gladiator_SwitchHolder_v3.step'))
c = plain(holder)
c.translate(V(-c.BoundBox.XMin, -c.BoundBox.YMin, -c.BoundBox.ZMin))
m = MeshPart.meshFromShape(Shape=c, LinearDeflection=0.02, AngularDeflection=math.radians(8))
m.write(str(O / 'Gladiator_SwitchHolder_v3.stl'))
chk['stl'] = dict(is_solid=m.isSolid(), non_manifold=m.hasNonManifolds(), size_mm=[round(c.BoundBox.XLength, 1), round(c.BoundBox.YLength, 1), round(c.BoundBox.ZLength, 1)],
                  print='floor down as exported, open rear toward +Y; no supports (the pocket roof is a 7.1 bridge, the shroud roof a 9.0 bridge)')
(O / 'validation.json').write_text(json.dumps(chk, indent=1, default=str))
print(json.dumps(chk, indent=1, default=str)[:3500], flush=True)
os._exit(0)
