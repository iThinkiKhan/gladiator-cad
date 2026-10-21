"""INA226 mount v3 (2026-10-19, Claude): an ADAPTER that clips onto the printed power-board tray (v5) and holds the INA226 UPRIGHT behind it.

Run: freecadcmd build_ina_mount_v3.py

Jim 2026-10-19: mount the INA at the rear of the batteries and the power-board tray, board flat against them (underside toward the tray),
header pins facing LEFT when you look at the robot from the rear with the mast forward; make it part of the power-board assembly later,
use an adapter on the existing tray for now (no reprint of the tray, rails or deck).

Frame (master): +X right (looking forward), +Y forward (mast end), +Z up. The tray's rear wall (the 'front wall' in the tray scripts) outer face is Y23.7,
top Z33.4, 2.4 thick; the battery holder's end face is Y21.0 (Z2..21.5). Rails, deck and tray are only read.

The hook (lip over the wall top, two toes down the inside between the corner blocks, every gap 0.3) is the v2 cassette hook unchanged, so it fits the printed tray.
Below it, instead of v2's cantilevered shelf, an upright 2 mm backplate runs down to 0.5 mm above the aluminium deck, bearing on the tray wall (spacer block) and on the
battery holder's end face. The board stands on four 4 mm stand-offs on the plate's rear face: two M2 bosses in the header-edge corners (holes 2.0 from the edges, as v2)
and two pads 12..14 mm from the header edge, so the 3 mm terminal pin tails clear the plate.
"""
import FreeCAD as A, Part, MeshPart, math, json, os, traceback
from pathlib import Path

V = A.Vector
R = Path('/home/buralien/projects/gladiator-cad')
O = R / 'cad/v2/ina-mount/v3-20261019'
O.mkdir(parents=True, exist_ok=True)


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


def hit(a, b):
    if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


def prism_yz(pts, x0, x1):
    vs_ = [V(x0, y, z) for y, z in pts]
    return Part.Face(Part.makePolygon(vs_ + [vs_[0]])).extrude(V(x1 - x0, 0, 0))


tv = json.load(open(R / 'cad/power-board/v5-tray/validation.json'))
WALL_OUT_Y = tv['front_wall_outer_y']        # 23.7 (the tray end that faces the robot's rear)
WALL_T = tv['wall_t']['front']               # 2.4
INNER_Y = WALL_OUT_Y + WALL_T                # 26.1
WALL_TOP = tv['wall_top']                    # 33.4
IX0, IX1 = tv['inner_xy'][0], tv['inner_xy'][1]
CORNER = tv['corner_block']

cd = A.openDocument(str(R / 'cad/enclosure/concept-20261013/Gladiator_Enclosure_Concept.FCStd'))
BBOX = plain(cd.getObject('Ref_BatteryBox').Shape)
CELLS = plain(cd.getObject('Ref_BatteryCells').Shape)
Y_BATT = BBOX.BoundBox.YMin                  # 21.0
Z_CELLS = max(BBOX.BoundBox.ZMax, CELLS.BoundBox.ZMax)   # 22.0

P = dict(CLR=0.3, plate_t=2.0, plate_x=(21.0, 58.0), plate_z0=2.5, lip_t=1.6, toe_t=1.6, toe_w=8.0, toe_z0=29.0,
         standoff=4.0, boss=(5.0, 5.0), pilot_d=1.6, pilot_depth=3.6, pad=(2.0, 4.0),
         board=(26.0, 22.0, 1.6), header_x=32.0, board_z0=8.5, hole_edge=2.0, tail=3.0, tallest=11.8, term_depth=8.5, pin_out=7.0)
p = P
C = p['CLR']
PLATE_Y = (Y_BATT - C - p['plate_t'], Y_BATT - C)                  # 18.7 .. 20.7, bears on the battery holder's end face
SPACER_Y = (PLATE_Y[1], WALL_OUT_Y - C)                             # 20.7 .. 23.4, bears on the tray wall
SPACER_Z0 = Z_CELLS + 0.5
LIP_Z = (WALL_TOP + C, WALL_TOP + C + p['lip_t'])                   # 33.7 .. 35.3
TOE_Y = (INNER_Y + C, INNER_Y + C + p['toe_t'])                     # 26.4 .. 28.0
TOE_X = [(IX0 + CORNER + C, IX0 + CORNER + C + p['toe_w']), (IX1 - CORNER - C - p['toe_w'], IX1 - CORNER - C)]
X0, X1 = p['plate_x']

parts = [box(X0, X1, PLATE_Y[0], PLATE_Y[1], p['plate_z0'], LIP_Z[1]),            # backplate
         box(X0, X1, SPACER_Y[0], SPACER_Y[1], SPACER_Z0, LIP_Z[1]),               # spacer onto the tray wall (above the cells)
         box(X0, X1, PLATE_Y[0], TOE_Y[1], LIP_Z[0], LIP_Z[1])]                     # lip over the wall top
for xa, xb in TOE_X:
    parts.append(box(xa, xb, TOE_Y[0], TOE_Y[1], p['toe_z0'], LIP_Z[0] + 0.01))       # toes down the inside of the wall

# board stand-offs on the rear face (Y = PLATE_Y[0]); each has a 45 degree slope on its upper side so it prints without support upside down
BW, BH, BT = p['board']
XH, XT = p['header_x'], p['header_x'] + BW          # header edge (left), terminal edge (right)
ZB0, ZB1 = p['board_z0'], p['board_z0'] + BH
YF = PLATE_Y[0]                                     # plate rear face 18.7
YU = YF - p['standoff']                             # board underside 14.7
YC = YU - BT                                        # component side 13.1
he = p['hole_edge']
holes = [(XH + he, ZB0 + he), (XH + he, ZB1 - he)]
s = p['standoff']


def standoff(xc, zc, w, h):
    return prism_yz([(YF + 0.01, zc - h / 2), (YU, zc - h / 2), (YU, zc + h / 2), (YF + 0.01, zc + h / 2 + s)], xc - w / 2, xc + w / 2)


for (hx, hz) in holes:
    parts.append(standoff(hx, hz, *p['boss']))
pw, ph = p['pad']
for zc in (ZB0 + 3.0, ZB1 - 3.0):
    parts.append(standoff(XH + 13.0, zc, pw, ph))
mount = fuse(*parts)
mount = cut(mount, *[Part.makeCylinder(p['pilot_d'] / 2, p['pilot_depth'] + 0.1, V(hx, YU - 0.1, hz), V(0, 1, 0)) for (hx, hz) in holes])

chk = dict(status='v3 DRAFT adapter - not printed', parameters=P, derived=dict(plate_y=PLATE_Y, spacer_y=SPACER_Y, spacer_z0=SPACER_Z0, lip_z=LIP_Z, toe_y=TOE_Y, toe_x=TOE_X,
           board_x=(XH, XT), board_z=(ZB0, ZB1), board_y=(YC, YU), holes_xz=holes, battery_face_y=Y_BATT, cells_top_z=Z_CELLS))
bb = mount.BoundBox
chk['part'] = dict(valid=mount.isValid(), solids=len(mount.Solids), volume_mm3=round(mount.Volume, 1), grams_pla=round(mount.Volume * 1.24e-3, 1),
                   bbox=[round(v, 2) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)])

# ------------------------------------------------------------- envelopes of the INA and its wiring
pcb = cut(box(XH, XT, YC, YU, ZB0, ZB1), *[Part.makeCylinder(1.0, 3, V(hx, YC - 1, hz), V(0, 1, 0)) for (hx, hz) in holes])
terms = box(XT - p['term_depth'], XT, YU - p['tallest'], YU, ZB0, ZB1)                  # terminal blocks on the component side
tails = box(XT - p['term_depth'], XT, YU, YU + p['tail'], ZB0, ZB1)                    # their pin tails behind the board
zc_h = (ZB0 + ZB1) / 2
header = box(XH - p['pin_out'], XH + 2.0, YC - 2.5, YC, zc_h - 5.1, zc_h + 5.1)       # 4 pins out of the left edge
dupont = box(XH - p['pin_out'] - 8.0, XH - p['pin_out'], YC - 3.5, YC + 1.0, zc_h - 6.0, zc_h + 6.0)
wires = box(XT, XT + 10.0, YU - p['tallest'] + 0.5, YU - 1.5, ZB0, ZB1)              # leads leaving the terminals to the right
drivers = [Part.makeCylinder(2.5, 60.0, V(hx, YC - 0.1, hz), V(0, -1, 0)) for (hx, hz) in holes]   # screwdriver from the rear
term_driver = Part.makeCylinder(2.5, 60.0, V(XT - 4.0, YU - p['tallest'] - 0.1, zc_h), V(0, -1, 0))

# ------------------------------------------------------------- references: tray v5, battery, deck, rails AS INSTALLED, deck v4, switch holder, hood
tray = plain(A.openDocument(str(R / 'cad/power-board/v5-tray/PowerBoardTray_v5.FCStd')).getObject('PowerBoardTray').Shape)
SPL = math.atan(1.0 / 89.0)
rd = A.openDocument(str(R / 'cad/v2/rails/v4-20261015/Gladiator_ArchRails_v4.FCStd'))
railL = plain(rd.getObject('Arch_Rail_Left_v4').Shape); railL.translate(V(-2.0, 0, 0)); railL.rotate(V(12.0, 23.85, 0), V(0, 0, 1), math.degrees(SPL))
railR = plain(rd.getObject('Arch_Rail_Right_v4').Shape); railR.translate(V(2.0, 0, 0)); railR.rotate(V(67.0, 23.85, 0), V(0, 0, 1), -math.degrees(SPL))
deck4 = plain(A.openDocument(str(R / 'cad/v2/upper-deck/v4-20261016/Gladiator_UpperDeck_v4.FCStd')).getObject('UpperDeck_v4').Shape)
holder = plain(A.openDocument(str(R / 'cad/v2/switch-enclosure/v3-20261016/Gladiator_SwitchHolder_v3.FCStd')).getObject('Switch_Holder_v3').Shape)
holder.translate(V(71.0 + 2.0 + SPL * (-10.0 - 23.85), -22.0, 12.0))
REFS = {'tray_v5': tray, 'battery_box': BBOX, 'battery_cells': CELLS, 'aluminium_deck': plain(cd.getObject('Ref_ChassisDeck').Shape),
        'rail_left_installed': railL, 'rail_right_installed': railR, 'upper_deck_v4': deck4, 'switch_holder_on_rail_shelf': holder,
        'mast_tube': plain(cd.getObject('Ref_MastTube').Shape), 'mast_base': plain(cd.getObject('Ref_MastBase').Shape)}
try:
    hood = plain(A.openDocument(str(R / 'cad/v2/enclosure/v2-20261013/Gladiator_Enclosure_v2.FCStd')).getObject('Rear_Hood').Shape)
    REFS['rear_hood'] = hood
except Exception:
    traceback.print_exc()

res = {}
for nm, shp in (('adapter', mount), ('pcb', pcb), ('terminals', terms), ('terminal_tails', tails), ('header_pins', header), ('dupont_on_pins', dupont),
                ('leads_out_right', wires), ('m2_screwdriver_top', drivers[0]), ('m2_screwdriver_bottom', drivers[1]), ('terminal_screwdriver', term_driver)):
    col = {}
    for rn, rs in REFS.items():
        v_ = hit(shp, rs)
        if v_ > 0.01 or v_ < 0:
            col[rn] = round(v_, 3)
    res[nm] = col or 'clear'
chk['collisions'] = res
chk['board_vs_adapter'] = dict(pcb=round(hit(pcb, mount), 3), terminals=round(hit(terms, mount), 3), tails=round(hit(tails, mount), 3), header=round(hit(header, mount), 3))
chk['gaps_mm'] = {rn: round(mount.distToShape(rs)[0], 2) for rn, rs in REFS.items() if mount.distToShape(rs)[0] < 6}
chk['ina_gaps_mm'] = {rn: round(Part.makeCompound([pcb, terms, header]).distToShape(rs)[0], 2) for rn, rs in REFS.items()
                      if Part.makeCompound([pcb, terms, header]).distToShape(rs)[0] < 8}
# the hook: play in every direction is the 0.3 gap and no more; drops on from above and lifts off
play = {}
for nm, d in (('forward', (0, 0.5, 0)), ('back', (0, -0.5, 0)), ('left', (-0.5, 0, 0)), ('right', (0.5, 0, 0)), ('down', (0, 0, -0.5))):
    t = plain(mount); t.translate(V(*d))
    play[nm] = 'stopped by ' + ', '.join(k for k in ('tray_v5', 'battery_box', 'aluminium_deck') if hit(t, REFS[k]) > 1e-3) if any(hit(t, REFS[k]) > 1e-3 for k in ('tray_v5', 'battery_box', 'aluminium_deck')) else 'FREE'
chk['play_0p5mm'] = play
worst = 0.0
for i in range(1, 81):
    t = plain(mount); t.translate(V(0, 0, 0.5 * i))
    worst = max(worst, max(hit(t, REFS[k]) for k in ('tray_v5', 'battery_box', 'battery_cells', 'rail_left_installed', 'rail_right_installed', 'aluminium_deck')))
chk['drop_on_from_40mm_worst_overlap_mm3'] = round(worst, 4)

doc = A.newDocument('Gladiator_INA_Mount_v3')
for n, s_ in (('INA_Mount_v3', mount), ('INA226_board_envelope', Part.makeCompound([pcb, terms, header]))):
    o = doc.addObject('Part::Feature', n)
    o.Shape = s_
doc.recompute()
doc.saveAs(str(O / 'Gladiator_INA_Mount_v3.FCStd'))
Part.export([doc.getObject('INA_Mount_v3')], str(O / 'Gladiator_INA_Mount_v3.step'))
# print orientation: upside down, the lip's top face on the bed (installed +Z becomes -Z)
c = plain(mount)
c.rotate(V(0, 0, 0), V(1, 0, 0), 180)
c.translate(V(-c.BoundBox.XMin, -c.BoundBox.YMin, -c.BoundBox.ZMin))
m = MeshPart.meshFromShape(Shape=c, LinearDeflection=0.02, AngularDeflection=math.radians(8))
m.write(str(O / 'Gladiator_INA_Mount_v3.stl'))
chk['stl'] = dict(is_solid=m.isSolid(), non_manifold=m.hasNonManifolds(), size_mm=[round(c.BoundBox.XLength, 1), round(c.BoundBox.YLength, 1), round(c.BoundBox.ZLength, 1)],
                  orientation='upside down: the top of the lip on the bed, toes and stand-offs pointing up/sideways')
(O / 'validation.json').write_text(json.dumps(chk, indent=1, default=str))
print(json.dumps(chk, indent=1, default=str)[:6000], flush=True)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(16, 8))

    def sl(ax, shape, nrm, val, ix, iz, color, lw=1.3):
        for w in shape.slice(nrm, val):
            pts = w.discretize(150)
            ax.plot([getattr(q, ix) for q in pts], [getattr(q, iz) for q in pts], color=color, lw=lw)
    for shp, col in ((tray, '#7f8c8d'), (BBOX, '#c0a000'), (REFS['aluminium_deck'], '#34495e'), (mount, '#c0392b'), (pcb, '#1e8449'), (terms, '#e67e22'), (deck4, '#2c3e50')):
        sl(axs[0], shp, V(1, 0, 0), XH + 13.0 if shp is not terms else XT - 3.0, 'y', 'z', col)
    axs[0].set_xlim(0, 40); axs[0].set_ylim(0, 60); axs[0].set_aspect('equal'); axs[0].grid(alpha=.3)
    axs[0].set_title('Side section (X through the pads): adapter red, tray grey, battery holder yellow, board green, terminals orange; robot rear to the LEFT', fontsize=8)
    for shp, col in ((mount, '#c0392b'), (pcb, '#1e8449'), (header, '#8e44ad'), (railL, '#555'), (railR, '#555'), (BBOX, '#c0a000')):
        sl(axs[1], shp, V(0, 1, 0), 16.0 if shp in (pcb, header) else 19.5, 'x', 'z', col)
    axs[1].set_xlim(0, 80); axs[1].set_ylim(0, 60); axs[1].set_aspect('equal'); axs[1].grid(alpha=.3)
    axs[1].set_title('Seen from the rear (section at Y16 / 19.5): board green, header pins purple to the LEFT, rails grey', fontsize=8)
    fig.savefig(str(O / 'ina_mount_v3_sections.png'), dpi=70, bbox_inches='tight')
except Exception:
    traceback.print_exc()
os._exit(0)
