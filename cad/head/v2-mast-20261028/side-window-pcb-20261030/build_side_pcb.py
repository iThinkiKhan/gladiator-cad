"""Masthead v2: head distro perfboard in the screen frame's side window (Jim, 2026-10-30).

Jim's 30 mm wide perfboard (70 long, cut to length) covers the side window of the screen frame on the side away from
the camera. It rests on the outer faces of the two frame rails and is held by two printed clamp bars screwed into
M2 heat-set inserts at the middle of each rail. The board rides with the head (tilts).
Base: ../pcb-floor-20261030/Gladiator_Head_v2_PCB_Floor.FCStd for the pan-lead window (Neck_Main, Mast_Tube_v2);
the yoke goes back to the Codex balanced yoke (the floor pocket is dropped). Run: xvfb-run -a freecadcmd build_side_pcb.py
"""
import json, math, os, hashlib
from pathlib import Path
import FreeCAD as App, Part, Mesh

V = App.Vector
HERE = Path(os.path.abspath(__file__)).parent
BASE = HERE.parent
SRC = BASE / 'pcb-floor-20261030' / 'Gladiator_Head_v2_PCB_Floor.FCStd'
BAL = BASE / 'balance-tensioner-20261030' / 'Gladiator_Head_v2_Balanced.FCStd'
OUT = HERE / 'Gladiator_Head_v2_Side_PCB.FCStd'
R = {'source': str(SRC.relative_to(BASE.parent.parent.parent)), 'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
     'yoke_from': str(BAL.relative_to(BASE.parent.parent.parent))}

d = App.openDocument(str(SRC))
bal = App.openDocument(str(BAL))
groups = json.loads((BASE / 'validation.json').read_text())['v2']['groups']
groups['fixed'] += ['Tensioner_M3x20_Envelope', 'Tensioner_Nut_Envelope']

# yoke back to the balanced (unpocketed) one; drop the floor-PCB objects
d.getObject('Tilt_Yoke').Shape = bal.getObject('Tilt_Yoke').Shape.copy()
for n in [o.Name for o in d.Objects]:
    if n.startswith(('Head_Distro_PCB_Placeholder', 'M2_Insert_', 'Yoke_Bolt_Head_M3', 'PCB_Part_Height_Zone_', 'Tilt_Lead_Route')):
        d.removeObject(n)
App.closeDocument(bal.Name)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cx(r, x0, x1, y, z):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


frame = d.getObject('Rear_Display_Frame').Shape
# ---------------------------------------------------------------- measured window (asserted from the CAD)
RAIL_X0, RAIL_X1 = 1.0, 5.5                     # rail outer face, inner face (measured)
BOT_RAIL = (226.0, 235.5); TOP_RAIL = (259.5, 269.0)
WIN_Y0, WIN_Y1 = 90.9, 140.5                     # carrier plate edge .. screen bezel
AXIS_Y, AXIS_Z = 113.0, 247.5
for z0, z1 in (BOT_RAIL, TOP_RAIL):
    probe = box(RAIL_X0 + 0.05, RAIL_X1 - 0.05, 100, 130, z0 + 0.05, z1 - 0.05)
    assert abs(frame.common(probe).Volume - probe.Volume) < 0.5, ('rail not solid where measured', z0)
win = box(RAIL_X0 - 0.5, 12.0, WIN_Y0 + 0.5, WIN_Y1 - 0.5, BOT_RAIL[1] + 0.05, TOP_RAIL[0] - 0.05)
assert frame.common(win).Volume < 0.5, 'window not open'

# ---------------------------------------------------------------- board, bars, inserts
BOARD_W, BOARD_T = 30.0, 1.6
BOARD_Y0, BOARD_Y1 = 91.5, 146.5                # 55 long: carrier edge to the end of the frame (cut Jim's 70)
BZ0, BZ1 = AXIS_Z - BOARD_W / 2, AXIS_Z + BOARD_W / 2     # 232.5 .. 262.5, centred on the window
BX1 = RAIL_X0                                   # solder side on the rail faces
BX0 = BX1 - BOARD_T
ACCESS_D = 6.0                                  # hole for the screwdriver to the tilt horn screw (on the tilt axis)
board = box(BX0, BX1, BOARD_Y0, BOARD_Y1, BZ0, BZ1).cut(cx(ACCESS_D / 2, BX0 - 1, BX1 + 1, AXIS_Y, AXIS_Z))
BAR_T = 3.0                                     # bar material outside the board
BAR_X0 = BX0 - BAR_T
INSERT_BORE, INSERT_DEPTH, M2_CLEAR = 2.8, 4.0, 2.6
SCREW_Y = (97.0, 141.0)
SCREW_Z = {'bottom': (BOT_RAIL[0] + BOT_RAIL[1] - (BZ0 - BOT_RAIL[0])) / 2 - 1.75, 'top': None}
SCREW_Z['bottom'] = BOT_RAIL[0] + 3.5           # 229.5: insert walls 2.1 below, 5.1 above in the 10 mm rail
SCREW_Z['top'] = TOP_RAIL[1] - 3.5              # 265.5
bars, inserts, bores = {}, [], []
for side, (rz0, rz1) in (('bottom', BOT_RAIL), ('top', TOP_RAIL)):
    b = box(BAR_X0, BX1, BOARD_Y0, BOARD_Y1, rz0, rz1)
    # rebate for the board edge (bar grips 3.5 of the board)
    b = b.cut(box(BX0 - 0.1, BX1 + 0.1, BOARD_Y0 - 1, BOARD_Y1 + 1, max(rz0, BZ0) - 0.15 if side == 'bottom' else rz0 - 1,
                  rz1 + 1 if side == 'bottom' else min(rz1, BZ1) + 0.15))
    for y in SCREW_Y:
        z = SCREW_Z[side]
        b = b.cut(cx(M2_CLEAR / 2, BAR_X0 - 1, BX1 + 1, y, z))
        bores.append(cx(INSERT_BORE / 2, RAIL_X0 - 0.01, RAIL_X0 + INSERT_DEPTH, y, z))
        inserts.append(cx(1.6, RAIL_X0, RAIL_X0 + 3.0, y, z).cut(cx(1.0, RAIL_X0 - 1, RAIL_X0 + 4, y, z)))
    b = b.removeSplitter()
    assert b.isValid() and len(b.Solids) == 1
    bars[side] = b
# insert walls: each bore sits in solid rail with material all round
for i, bo in enumerate(bores):
    ring = cx(INSERT_BORE / 2 + 0.9, RAIL_X0, RAIL_X0 + INSERT_DEPTH, bo.BoundBox.Center.y, bo.BoundBox.Center.z)
    frac = frame.common(ring).Volume / ring.Volume
    assert frac > 0.99, ('insert %d wall not solid' % i, frac)
frame_new = frame.copy()
for bo in bores:
    frame_new = frame_new.cut(bo)
frame_new = frame_new.removeSplitter()
assert frame_new.isValid() and len(frame_new.Solids) == len(frame.Solids)
R['frame_change'] = '4 x M2 heat-set bores 2.8 x 4 deep in the outer faces of the side rails (drill into the printed v06 frame, or reprint)'
R['insert_positions_YZ'] = [[y, SCREW_Z[s]] for s in ('bottom', 'top') for y in SCREW_Y]

# component envelope on the outer face (how tall parts may be, outward), and the screwdriver path
COMP_H = 20.0
comps = box(BX0 - COMP_H, BX0, BOARD_Y0, BOARD_Y1, BZ0, BZ1)
driver = cx(1.6, -40.0, 20.0, AXIS_Y, AXIS_Z)

S = {n: d.getObject(n).Shape for g in groups for n in groups[g] if d.getObject(n)}
S['Rear_Display_Frame'] = frame_new
T = V(39.5, 113, 247.5); P = V(39.5, 113, 0)
tilt_set = set(groups['tilt'])
ride = Part.makeCompound([board, comps] + list(bars.values()))

# static: nothing of the head or the robot inside the new parts (the frame rails touch the board/bars face-to-face)
stat = {}
for nm, sh in (('board', board), ('bars', Part.makeCompound(list(bars.values()))), ('components_20mm', comps)):
    stat[nm] = sorted(k for k in S if sh.common(S[k]).Volume > 0.05)
R['static_overlaps'] = stat
# the screwdriver to the tilt horn screw still gets through (only the horn itself may be met)
R['horn_screw_driver_blockers'] = sorted(k for k in S if k != 'Tilt_Horn_Reference' and driver.common(S[k]).Volume > 0.05) + \
    (['Side_PCB'] if driver.common(board).Volume > 0.01 else [])
# tilt: the board rides with the head, so check it against the pan side and the fixed side
hits = set()
for t in range(-38, 35, 2):
    s = ride.copy(); s.rotate(T, V(1, 0, 0), t)
    for k in S:
        if k in tilt_set:
            continue
        if s.common(S[k]).Volume > 0.05:
            hits.add((k, t))
R['tilt_hits'] = sorted(hits)
# pan with the head tilted to both ends, against the fixed side
ph = set()
for t in (-38, 0, 34):
    s0 = ride.copy(); s0.rotate(T, V(1, 0, 0), t)
    for p in range(-20, 181, 10):
        s = s0.copy(); s.rotate(P, V(0, 0, 1), p)
        for k in groups['fixed']:
            if k in S and s.common(S[k]).Volume > 0.05:
                ph.add(k)
R['pan_fixed_hits'] = sorted(ph)
R['board'] = {'size_mm': [BOARD_Y1 - BOARD_Y0, BOARD_W, BOARD_T], 'world_Y': [BOARD_Y0, BOARD_Y1], 'world_Z': [BZ0, BZ1],
              'overlap_on_each_rail_mm': round(BOT_RAIL[1] - BZ0, 2), 'access_hole_d': ACCESS_D,
              'access_hole_from_front_and_bottom_edges_mm': [AXIS_Y - BOARD_Y0, AXIS_Z - BZ0],
              'component_height_checked_mm': COMP_H}

# mass / balance: board + bars + parts and leads, about the tilt axis (estimate)
m_board = board.Volume * 1.85e-3                 # FR4
m_bars = sum(b.Volume for b in bars.values()) * 1.24e-3 * 0.85
m_parts = 6.0                                    # connectors, cap, leads (guess)
cy = (BOARD_Y0 + BOARD_Y1) / 2
R['mass_estimate_g'] = {'board': round(m_board, 1), 'bars': round(m_bars, 1), 'parts_leads_guess': m_parts,
                        'centre_behind_tilt_axis_mm': round(cy - AXIS_Y, 1),
                        'note': 'behind the axis = screen side, so it slightly offsets the camera-heavy head'}

# ---------------------------------------------------------------- save
d.getObject('Rear_Display_Frame').Shape = frame_new
def add(name, shape):
    o = d.addObject('Part::Feature', name); o.Shape = shape; return o
add('Side_PCB_30x55_Placeholder', board)
add('Side_PCB_Clamp_Bar_Bottom', bars['bottom'])
add('Side_PCB_Clamp_Bar_Top', bars['top'])
for i, s in enumerate(inserts):
    add('Side_PCB_M2_Insert_%d' % (i + 1), s)
add('Side_PCB_Parts_Envelope_20mm', comps)
d.recompute()
d.saveAs(str(OUT))

stl = HERE / 'stl'; stl.mkdir(exist_ok=True)
R['print_stl'] = []
for side, b in bars.items():
    pr = b.copy(); pr.rotate(V(), V(0, 1, 0), -90)            # outer face (X min) down on the bed
    pr.translate(V(-pr.BoundBox.XMin, -pr.BoundBox.YMin, -pr.BoundBox.ZMin))
    m = Mesh.Mesh(pr.tessellate(0.02)); f = 'stl/Side_PCB_Clamp_Bar_%s.stl' % side.capitalize(); m.write(str(HERE / f))
    R['print_stl'].append({'file': f, 'orientation': 'outer face on the bed, rebate up; no support', 'solid': m.isSolid(),
                           'non_manifold': m.hasNonManifolds(),
                           'size_mm': [round(m.BoundBox.XLength, 1), round(m.BoundBox.YLength, 1), round(m.BoundBox.ZLength, 1)]})
pr = frame_new.copy(); pr.translate(V(-pr.BoundBox.XMin, -pr.BoundBox.YMin, -pr.BoundBox.ZMin))
m = Mesh.Mesh(pr.tessellate(0.02)); m.write(str(stl / 'Rear_Display_Frame_v06_with_side_PCB_inserts.stl'))
R['print_stl'].append({'file': 'stl/Rear_Display_Frame_v06_with_side_PCB_inserts.stl',
                       'orientation': 'only if reprinting the frame; same orientation as the v06 frame', 'solid': m.isSolid(),
                       'non_manifold': m.hasNonManifolds()})
(HERE / 'validation.json').write_text(json.dumps(R, indent=1))
os._exit(0)
