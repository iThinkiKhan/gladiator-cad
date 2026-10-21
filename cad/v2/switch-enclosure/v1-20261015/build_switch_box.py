"""Power switch enclosure v1 (2026-10-15, Claude).

Run: freecadcmd build_switch_box.py

Jim, 2026-10-15: no 'hallway'; a separate enclosure with an OPEN REAR for wiring that bolts securely to a mount point on the rails OR on the body.
Switch (measurements/components.md): body 6.8 wide x 12.7 along the slide axis (mounted vertically, up = ON) x 6.37 deep, knob 5.0 proud x 4.0 wide,
knob envelope 6.0, pins 3.7. ASSUMED: pin pitch (window 5.4 x 11), current rating unknown.

Local frame: x' lateral (centred), y' from the FRONT face (0, knob side) to the open REAR (L), z' from the floor underside (0) up.
Mounted frame: knob toward -Y, so world Y = Y_front + y'. Two M3 screws go down through the top wall at y'=12 and y'=21, through the wiring
cavity and the floor, into heat-set inserts in the shelf (rail shelf, or the shelf inside the hood). Same part, same two inserts, either mount.
"""
import FreeCAD as A, Part, MeshPart, math, json, os, shutil, traceback
from pathlib import Path

V = A.Vector
R = Path('/home/buralien/projects/gladiator-cad')
O = R / 'cad/v2/switch-enclosure/v1-20261015'
O.mkdir(parents=True, exist_ok=True)

P = dict(W=14.5, floor=3.0, top=1.9, L=24.0, body=(6.8, 12.7, 6.37), clear=0.3, lip=1.4, pin_window=(5.4, 11.0),
         shroud_w=9.0, screw_y=(12.0, 21.0), screw_d=3.6, cb_d=6.4, cb_depth=1.0, bezel_t=1.2, bezel_screw_dx=5.4, pilot_d=2.35, pilot_depth=6.0,
         knob_slot=(4.6, 8.0))
p = P
bw, bl, bd = p['body']
cw, ch = bw + p['clear'], bl + p['clear']         # pocket 7.1 x 13.0
H = p['floor'] + ch + p['top']                    # 17.9
pocket_len = bd + p['clear']                      # 6.67


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


zc = p['floor'] + ch / 2                           # pocket centre height
body = box(-p['W'] / 2, p['W'] / 2, 0, p['L'], 0, H)
pocket = box(-cw / 2, cw / 2, -1, pocket_len, p['floor'], p['floor'] + ch)
lip_end = pocket_len + p['lip']
shroud = box(-p['shroud_w'] / 2, p['shroud_w'] / 2, lip_end, p['L'] + 1, p['floor'], p['floor'] + ch)
pinwin = box(-p['pin_window'][0] / 2, p['pin_window'][0] / 2, pocket_len - 0.5, lip_end + 0.5, zc - p['pin_window'][1] / 2, zc + p['pin_window'][1] / 2)
cuts = [pocket, shroud, pinwin]
for sy in p['screw_y']:
    cuts.append(Part.makeCylinder(p['screw_d'] / 2, H + 2, V(0, sy, -1)))                                            # through top and floor
    cuts.append(Part.makeCylinder(p['cb_d'] / 2, p['cb_depth'] + 1, V(0, sy, H - p['cb_depth'])))
    cuts.append(Part.makeCone(p['screw_d'] / 2 + 0.7, p['screw_d'] / 2, 0.7, V(0, sy, 0), V(0, 0, 1)))      # chamfer on the floor underside (prints on the glass bed)
for sg in (1, -1):
    cuts.append(Part.makeCylinder(p['pilot_d'] / 2, p['pilot_depth'], V(sg * p['bezel_screw_dx'], 0, zc), V(0, 1, 0)))
housing = cut(body, *cuts)
bezel = box(-p['W'] / 2, p['W'] / 2, -p['bezel_t'], 0, 0, H)
def xz_rect(y, w, h):
    vs_ = [V(-w / 2, y, zc - h / 2), V(w / 2, y, zc - h / 2), V(w / 2, y, zc + h / 2), V(-w / 2, y, zc + h / 2)]
    return Part.makePolygon(vs_ + [vs_[0]])


kw, kh = p['knob_slot']
c_ = 0.6
bezel = cut(bezel, box(-kw / 2, kw / 2, -3, 1, zc - kh / 2, zc + kh / 2),
            Part.makeLoft([xz_rect(-p['bezel_t'], kw + 2 * c_, kh + 2 * c_), xz_rect(-p['bezel_t'] + c_, kw, kh)], True, True),    # slot chamfer on the front face (the bed side when printed)
            *[Part.makeCylinder(2.6 / 2, 5, V(sg * p['bezel_screw_dx'], -3, zc), V(0, 1, 0)) for sg in (1, -1)],
            *[Part.makeCone(2.6 / 2 + c_, 2.6 / 2, c_, V(sg * p['bezel_screw_dx'], -p['bezel_t'], zc), V(0, 1, 0)) for sg in (1, -1)])
PARTS = {'Switch_Enclosure_v1': housing, 'Switch_Bezel_v1': bezel}

chk = dict(status='v1 DRAFT - not printed', parameters=P, height_mm=H, knob_centre_above_floor_underside_mm=round(zc, 2), parts={})
for n, s in PARTS.items():
    bb = s.BoundBox
    chk['parts'][n] = dict(valid=s.isValid(), solids=len(s.Solids), volume_mm3=round(s.Volume, 1),
                           size_mm=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)])

# fit test with the real switch dimensions
sw_body = box(-bw / 2, bw / 2, 0.15, 0.15 + bd, zc - bl / 2, zc + bl / 2)
sw_knob = box(-2.0, 2.0, 0.15 - 5.0, 0.15, zc - 3.0, zc + 3.0)
sw_pins = box(-2.5, 2.5, 0.15 + bd, 0.15 + bd + 3.7, zc - 5.0, zc + 5.0)


def vol(a, b):
    try:
        return round(a.common(b).Volume, 3)
    except Exception:
        return None


chk['fit'] = dict(body_vs_housing=vol(sw_body, housing), body_vs_bezel=vol(sw_body, bezel), knob_vs_bezel=vol(sw_knob, bezel), knob_vs_housing=vol(sw_knob, housing),
                  pins_vs_housing=vol(sw_pins, housing), body_rear_gap_to_lip_mm=round(pocket_len - (0.15 + bd), 2),
                  knob_tip_beyond_bezel_mm=round(5.0 - p['bezel_t'] - 0.15, 2))

# placements: rail shelf (right rail) and hood shelf
PL = {'rail_shelf': dict(x=71.0, y_front=-22.0, z_floor=12.0), 'hood_shelf': dict(x=71.0, y_front=-29.4, z_floor=30.5)}
chk['placements'] = PL
chk['screw_insert_positions'] = {k: [round(v['y_front'] + sy, 2) for sy in p['screw_y']] for k, v in PL.items()}
chk['screw_length_mm'] = 'M3 x 25: head counterbore 1.0 + top 1.9 + cavity %.1f + floor 3.0 + 7.5 insert = about %.1f' % (ch, p['top'] - p['cb_depth'] + ch + p['floor'] + 7.5)


def place(shape, pl):
    c = plain(shape)
    c.translate(V(pl['x'], pl['y_front'], pl['z_floor']))
    return c


checks = {}
try:
    rd = A.openDocument(str(R / 'cad/v2/rails/v4-20261015/Gladiator_ArchRails_v4.FCStd'))
    rr = plain(rd.getObject('Arch_Rail_Right_v4').Shape)
    cd = A.openDocument(str(R / 'cad/enclosure/concept-20261013/Gladiator_Enclosure_Concept.FCStd'))
    refs = {o.Name: plain(o.Shape) for o in cd.Objects if o.Name.startswith('Ref_') and not o.Name.startswith(
        ('Ref_SideRail', 'Ref_PowerBoardTray', 'Ref_Base', 'Ref_INA226', 'Ref_BoardReference', 'Ref_PowerSwitchHolder', 'Ref_Switch'))}
    refs['Rail_Right_v4'] = rr
    hb = place(housing, PL['rail_shelf'])
    zb = place(bezel, PL['rail_shelf'])
    res = {}
    for nm, rs in refs.items():
        for lab, sh in (('housing', hb), ('bezel', zb)):
            if sh.BoundBox.intersect(rs.BoundBox):
                v = vol(sh, rs)
                if v is None or v > 0.01:
                    res[lab + ' vs ' + nm] = v
    checks['rail_shelf_overlaps'] = res or 'none'
    checks['rail_shelf_gap_to_nearest_mm'] = sorted([(round(hb.distToShape(rs)[0], 2), nm) for nm, rs in refs.items() if hb.distToShape(rs)[0] < 15])[:4]
except Exception:
    traceback.print_exc()
chk['rail_shelf_checks'] = checks

doc = A.newDocument('Gladiator_SwitchEnclosure_v1')
for n, s in PARTS.items():
    o = doc.addObject('Part::Feature', n)
    o.Shape = s
doc.recompute()
doc.saveAs(str(O / 'Gladiator_SwitchEnclosure_v1.FCStd'))
Part.export([doc.getObject(n) for n in PARTS], str(O / 'Gladiator_SwitchEnclosure_v1.step'))
stl = {}
for n, s in PARTS.items():
    c = plain(s)
    if n.startswith('Switch_Bezel'):
        c.rotate(V(0, 0, 0), V(1, 0, 0), 90)       # lie flat
    c.translate(V(-c.BoundBox.XMin, -c.BoundBox.YMin, -c.BoundBox.ZMin))
    m = MeshPart.meshFromShape(Shape=c, LinearDeflection=0.02, AngularDeflection=math.radians(8))
    m.write(str(O / ('Gladiator_%s.stl' % n)))
    bb = c.BoundBox
    stl[n] = dict(is_solid=m.isSolid(), non_manifold=m.hasNonManifolds(), size_mm=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)])
chk['stl'] = stl
(O / 'validation.json').write_text(json.dumps(chk, indent=1, default=str))
print(json.dumps(chk, indent=1, default=str)[:4500], flush=True)
os._exit(0)
