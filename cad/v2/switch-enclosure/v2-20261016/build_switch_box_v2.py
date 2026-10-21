"""Power switch enclosure v2 (2026-10-16, Claude): DROP-IN for a switch that is ALREADY WIRED.

Run: freecadcmd build_switch_box_v2.py

Jim 2026-10-16: the switch is already wired up and cannot be unwired, so v1 (switch pushed in from the front, pins through a rear window) cannot be used.
v2: housing open at the top and the rear. The wired switch drops in from above, knob through the front wall, soldered leads leave through the open rear.
A lid screws down over it (the same two M3 screws that bolt the box to the shelf go through the lid and the floor). No bezel any more: the knob slot is in the front wall.

Local frame as v1: x' lateral (centred), y' from the pocket front (0) to the open REAR (L), z' from the floor underside (0) up.
The front wall occupies y' -1.2..0 (where the v1 bezel was), so every placement and the hood window are unchanged.
"""
import FreeCAD as A, Part, MeshPart, math, json, os, traceback
from pathlib import Path

V = A.Vector
R = Path('/home/buralien/projects/gladiator-cad')
O = R / 'cad/v2/switch-enclosure/v2-20261016'
O.mkdir(parents=True, exist_ok=True)

P = dict(W=14.5, floor=3.0, lid=1.9, L=24.0, body=(6.8, 12.7, 6.37), clear=0.3, rib=0.65, front_t=1.2, shroud_w=9.0, screw_y=(12.0, 21.0), screw_d=3.6, cb_d=6.4, cb_depth=1.0,
         knob_slot=(4.6, 8.0), chamfer=0.7)
p = P
bw, bl, bd = p['body']
cw, ch = bw + p['clear'], bl + p['clear']         # pocket 7.1 wide x 13.0 tall
H = p['floor'] + ch + p['lid']                    # 17.9
zw = p['floor'] + ch                              # wall top = lid underside, 16.0
pocket_len = bd + p['clear']                      # 6.67
zc = p['floor'] + ch / 2                          # pocket centre height


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


def fuse(*s):
    r = plain(s[0])
    for x in s[1:]:
        r = plain(r.fuse(plain(x)))
    return plain(r.removeSplitter())


def xz_rect(y, w, h):
    vs_ = [V(-w / 2, y, zc - h / 2), V(w / 2, y, zc - h / 2), V(w / 2, y, zc + h / 2), V(-w / 2, y, zc + h / 2)]
    return Part.makePolygon(vs_ + [vs_[0]])


# ------------------------------------------------------------------ housing: floor, side walls, front wall; open top, open rear
W2 = p['W'] / 2
body = box(-W2, W2, -p['front_t'], p['L'], 0, zw)
lip_end = pocket_len + 1.4
cuts = [box(-cw / 2, cw / 2, 0, pocket_len, p['floor'], zw + 1),                                     # pocket for the switch body, open top
        box(-(cw / 2 - p['rib']), cw / 2 - p['rib'], pocket_len - 0.2, lip_end, p['floor'], zw + 1),   # passage for the pins / leads past the two side ribs (the ribs stop the body sliding back)
        box(-p['shroud_w'] / 2, p['shroud_w'] / 2, lip_end - 0.2, p['L'] + 1, p['floor'], zw + 1)]     # wiring shroud, open top and rear
kw, kh = p['knob_slot']
cuts.append(box(-kw / 2, kw / 2, -p['front_t'] - 1, 0.5, zc - kh / 2, zc + kh / 2))                      # knob slot through the front wall
for sy in p['screw_y']:
    cuts.append(Part.makeCylinder(p['screw_d'] / 2, p['floor'] + 2, V(0, sy, -1)))                        # M3 down through the floor into the shelf insert
    cuts.append(Part.makeCone(p['screw_d'] / 2 + p['chamfer'], p['screw_d'] / 2, p['chamfer'], V(0, sy, 0), V(0, 0, 1)))   # chamfer on the floor underside (prints on the glass)
housing = cut(body, *cuts)

# ------------------------------------------------------------------ lid
lid = box(-W2, W2, -p['front_t'], p['L'], zw, H)
lcuts = []
for sy in p['screw_y']:
    lcuts.append(Part.makeCylinder(p['screw_d'] / 2, p['lid'] + 2, V(0, sy, zw - 1)))
    lcuts.append(Part.makeCylinder(p['cb_d'] / 2, p['cb_depth'] + 1, V(0, sy, H - p['cb_depth'])))
lid = cut(lid, *lcuts)
PARTS = {'Switch_Housing_v2': housing, 'Switch_Lid_v2': lid}

chk = dict(status='v2 DRAFT - not printed', parameters=P, height_mm=H, knob_centre_above_floor_underside_mm=round(zc, 2), parts={})
for n, s in PARTS.items():
    bb = s.BoundBox
    chk['parts'][n] = dict(valid=s.isValid(), solids=len(s.Solids), volume_mm3=round(s.Volume, 1), size_mm=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)])

# fit test with the real switch dimensions, dropped in from above
sw_body = box(-bw / 2, bw / 2, 0.15, 0.15 + bd, zc - bl / 2, zc + bl / 2)
sw_knob = box(-2.0, 2.0, 0.15 - 5.0, 0.15, zc - 3.0, zc + 3.0)
sw_pins = box(-2.5, 2.5, 0.15 + bd, 0.15 + bd + 3.7, zc - 5.0, zc + 5.0)
sw_leads = box(-3.0, 3.0, 0.15 + bd + 3.7, p['L'] + 20, zc - 5.5, zc + 5.5)      # soldered leads and sleeves trailing out of the open rear (generous 6 x 11 envelope)


def vol(a, b):
    try:
        return round(a.common(b).Volume, 3)
    except Exception:
        return None


chk['fit'] = dict(body_vs_housing=vol(sw_body, housing), body_vs_lid=vol(sw_body, lid), knob_vs_housing=vol(sw_knob, housing), knob_vs_lid=vol(sw_knob, lid),
                  pins_vs_housing=vol(sw_pins, housing), pins_vs_lid=vol(sw_pins, lid), leads_vs_housing=vol(sw_leads, housing), leads_vs_lid=vol(sw_leads, lid),
                  body_rear_gap_to_ribs_mm=round(pocket_len - (0.15 + bd), 2), knob_tip_beyond_front_wall_mm=round(5.0 - p['front_t'] - 0.15, 2),
                  drop_in_path_clear=bool(vol(box(-bw / 2, bw / 2, 0.15, 0.15 + bd, zc - bl / 2, zc + bl / 2 + 30), housing) == 0.0),
                  note='the body is dropped straight down between the front wall and the two side ribs; the lid then closes the top')
chk['mounting'] = dict(screws='two M3 x 25 through the lid (counterbored) and the floor into two heat-set inserts 9 mm apart in the shelf', screw_y_prime=p['screw_y'])

# placements: the same two shelves as v1
PL = {'rail_shelf': dict(x=71.0, y_front=-22.0, z_floor=12.0), 'hood_shelf': dict(x=71.0, y_front=-29.4, z_floor=30.5)}
chk['placements'] = PL
checks = {}
try:
    rd = A.openDocument(str(R / 'cad/v2/rails/v4-20261015/Gladiator_ArchRails_v4.FCStd'))
    rr = plain(rd.getObject('Arch_Rail_Right_v4').Shape)
    cd = A.openDocument(str(R / 'cad/enclosure/concept-20261013/Gladiator_Enclosure_Concept.FCStd'))
    refs = {o.Name: plain(o.Shape) for o in cd.Objects if o.Name.startswith('Ref_') and not o.Name.startswith(('Ref_SideRail', 'Ref_PowerBoardTray', 'Ref_Base', 'Ref_BoardReference', 'Ref_PowerSwitchHolder', 'Ref_Switch'))}
    refs['Rail_Right_v4'] = rr
    ina = {k: v for k, v in refs.items() if 'INA226' in k}
    for pl_name, pl in PL.items():
        res = {}
        for lab, shp in (('housing', housing), ('lid', lid)):
            c = plain(shp)
            c.translate(V(pl['x'], pl['y_front'], pl['z_floor']))
            for nm, rs in refs.items():
                if c.BoundBox.intersect(rs.BoundBox):
                    v_ = vol(c, rs)
                    if v_ is None or v_ > 0.01:
                        res[lab + ' vs ' + nm] = v_
            checks[pl_name + '_nearest_INA_mm'] = round(min(c.distToShape(rs)[0] for rs in ina.values()), 2)
        checks[pl_name + '_overlaps'] = res or 'none'
except Exception:
    traceback.print_exc()
chk['placement_checks'] = checks

doc = A.newDocument('Gladiator_SwitchEnclosure_v2')
for n, s in PARTS.items():
    o = doc.addObject('Part::Feature', n)
    o.Shape = s
doc.recompute()
doc.saveAs(str(O / 'Gladiator_SwitchEnclosure_v2.FCStd'))
Part.export([doc.getObject(n) for n in PARTS], str(O / 'Gladiator_SwitchEnclosure_v2.step'))
stl = {}
for n, s in PARTS.items():
    c = plain(s)
    c.translate(V(-c.BoundBox.XMin, -c.BoundBox.YMin, -c.BoundBox.ZMin))
    m = MeshPart.meshFromShape(Shape=c, LinearDeflection=0.02, AngularDeflection=math.radians(8))
    m.write(str(O / ('Gladiator_%s.stl' % n)))
    bb = c.BoundBox
    stl[n] = dict(is_solid=m.isSolid(), non_manifold=m.hasNonManifolds(), size_mm=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)])
chk['stl'] = stl
(O / 'validation.json').write_text(json.dumps(chk, indent=1, default=str))
print(json.dumps(chk, indent=1, default=str)[:4000], flush=True)
os._exit(0)
