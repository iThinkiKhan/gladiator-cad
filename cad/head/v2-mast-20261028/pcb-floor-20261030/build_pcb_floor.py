"""Masthead v2: yoke floor holds the head distro PCB (Jim, 2026-10-30).

Base: Codex balanced derivative (balance-tensioner-20261030/Gladiator_Head_v2_Balanced.FCStd), world coordinates.
Only the Tilt_Yoke changes. Adds a placeholder PCB, three M2 heat-set inserts, a tilt-servo lead channel under the
board edge, and part-height envelopes found by sweeping the tilting head. Run: xvfb-run -a freecadcmd build_pcb_floor.py
"""
import json, math, os, hashlib
from pathlib import Path
import FreeCAD as App, Part, Mesh

V = App.Vector
HERE = Path(os.path.abspath(__file__)).parent
BASE = HERE.parent
SRC = BASE / 'balance-tensioner-20261030' / 'Gladiator_Head_v2_Balanced.FCStd'
OUT = HERE / 'Gladiator_Head_v2_PCB_Floor.FCStd'
R = {'source': str(SRC.relative_to(BASE.parent.parent.parent)),
     'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest()}

d = App.openDocument(str(SRC))
groups = json.loads((BASE / 'validation.json').read_text())['v2']['groups']
groups['fixed'] += ['Tensioner_M3x20_Envelope', 'Tensioner_Nut_Envelope']

# ---------------------------------------------------------------- numbers (world mm)
FLOOR_BOT, FLOOR_TOP = 200.5, 204.5          # yoke floor frame (4 thick) on the pedestal top plate
SEAT_D = 1.0                                  # pocket depth: board top 0.6 above the floor
SEAT_Z = FLOOR_TOP - SEAT_D                   # 203.5, board bottom
PCB_T = 1.6
PCB_TOP = SEAT_Z + PCB_T                      # 205.1
RELIEF_D = 1.5                                # room under the board for trimmed through-hole leads
RELIEF_Z = SEAT_Z - RELIEF_D                  # 202.0
SEAT_CLR = 0.3                                # pocket wall clearance around the board
RELIEF_INSET = 1.8                            # ledge the board rests on
INSERT_BORE, INSERT_LEN = 2.8, 3.0            # Jim's M2 heat-set (settled 2026-10-22); bore runs right through
M2_CLEAR = 2.6
INSERTS = {'A': (44.0, 96.2), 'B': (61.0, 102.5), 'C': (61.0, 120.3)}
ISLAND_R = 2.9                                # full-depth material kept round each insert
YOKE_BOLT = (59.5, 114.0)                     # M3 yoke bolt, head on the floor top
DRIVER_HOLES = [(39.5 + 13.3 * sx, 113 + 13.3 * sy) for sx in (-1, 1) for sy in (-1, 1)]   # to the pan retainer screws, r3.5
# board outline (2D): stepped front (camera case sweeps low at front right), notch round the yoke bolt head
OUTLINE = [(40.6, 93.5), (49.0, 93.5), (49.0, 97.0), (63.5, 97.0), (63.5, 108.5), (56.3, 108.5),
           (56.3, 118.5), (63.5, 118.5), (63.5, 123.0), (40.6, 123.0)]
# tilt servo lead channel: from the open floor in front of the ear column, under the board edge, into the passage
CHANNEL = (30.0, 44.5, 105.8, 109.8)          # x0, x1, y0, y1; full floor depth (pedestal plate is its bottom)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, x, y, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0))


def face_of(pts):
    w = Part.makePolygon([V(x, y, 0) for x, y in pts] + [V(*pts[0], 0)])
    return Part.Face(w)


def prism(face, z0, z1):
    f = face.copy(); f.translate(V(0, 0, z0))
    return f.extrude(V(0, 0, z1 - z0))


board2d = face_of(OUTLINE)
for x, y in DRIVER_HOLES:
    board2d = board2d.cut(Part.Face(Part.Wire(Part.makeCircle(4.0, V(x, y, 0)))))
board2d = board2d.Faces[0]
holes2d = [Part.Face(Part.Wire(Part.makeCircle(M2_CLEAR / 2, V(x, y, 0)))) for x, y in INSERTS.values()]

# ---------------------------------------------------------------- yoke
yoke0 = d.getObject('Tilt_Yoke').Shape.copy()
bb = yoke0.BoundBox
assert abs(bb.ZMin - FLOOR_BOT) < 0.01, bb
# the floor top really is 204.5 here (frame bars), and nothing of the yoke stands inside the board area above it
above = yoke0.common(prism(board2d, FLOOR_TOP + 0.01, FLOOR_TOP + 40)).Volume
assert above < 0.01, ('yoke material above the board area', above)

seat = prism(board2d.makeOffset2D(SEAT_CLR, join=0), SEAT_Z, FLOOR_TOP + 1)
relief_face = board2d.makeOffset2D(-RELIEF_INSET, join=0)
relief = prism(relief_face, RELIEF_Z, SEAT_Z + 0.01)
for x, y in INSERTS.values():
    relief = relief.cut(cyl(ISLAND_R, x, y, RELIEF_Z - 1, SEAT_Z + 1))
bores = [cyl(INSERT_BORE / 2, x, y, FLOOR_BOT - 0.01, SEAT_Z + 0.01) for x, y in INSERTS.values()]
chan = box(CHANNEL[0], CHANNEL[1], CHANNEL[2], CHANNEL[3], FLOOR_BOT - 0.01, FLOOR_TOP + 1)

# every insert must sit in full material: the ring round the bore is solid yoke all the way down
for k, (x, y) in INSERTS.items():
    ring = cyl(INSERT_BORE / 2 + 1.0, x, y, FLOOR_BOT, SEAT_Z).cut(cyl(INSERT_BORE / 2, x, y, FLOOR_BOT - 1, SEAT_Z + 1))
    frac = yoke0.common(ring).Volume / ring.Volume
    assert frac > 0.99, ('insert %s wall not in solid floor' % k, frac)
# the channel must not bite the ear column above the floor
assert yoke0.common(box(CHANNEL[0], CHANNEL[1], CHANNEL[2], CHANNEL[3], FLOOR_TOP + 0.01, FLOOR_TOP + 10)).Volume < 0.01

yoke = yoke0.cut(seat).cut(relief).cut(chan)
for b in bores:
    yoke = yoke.cut(b)
yoke = yoke.removeSplitter()
assert yoke.isValid() and len(yoke.Solids) == 1, (yoke.isValid(), len(yoke.Solids))
R['yoke_volume_mm3'] = {'before': round(yoke0.Volume, 1), 'after': round(yoke.Volume, 1)}
# what is left of the floor between the columns, under the board (structure note)
mid = box(42.0, 56.0, 109.0, 120.0, FLOOR_BOT, FLOOR_TOP)
R['cross_bar_left_between_columns_mm3'] = {'before': round(yoke0.common(mid).Volume, 1), 'after': round(yoke.common(mid).Volume, 1)}

# ---------------------------------------------------------------- new objects
pcb = prism(board2d, SEAT_Z, PCB_TOP)
for h in holes2d:
    pcb = pcb.cut(prism(h, SEAT_Z - 1, PCB_TOP + 1))
inserts = [cyl(1.6, x, y, SEAT_Z - INSERT_LEN, SEAT_Z) .cut(cyl(1.0, x, y, SEAT_Z - INSERT_LEN - 1, SEAT_Z + 1))
           for x, y in INSERTS.values()]
lead = Part.makeCompound([box(33.6, 37.4, 108.4, 109.7, 201.9, 214.0),     # down the front face of the ear column
                          box(33.6, 43.6, 106.0, 109.6, 200.6, 201.9),     # flat along the channel, under the board edge
                          box(40.5, 42.5, 107.5, 110.5, 186.0, 200.6)])    # down into the pedestal bore (r6.5)
bolt_head = cyl(2.75, YOKE_BOLT[0], YOKE_BOLT[1], FLOOR_TOP, FLOOR_TOP + 2.2)

S = {n: d.getObject(n).Shape for g in groups for n in groups[g] if d.getObject(n)}
S['Tilt_Yoke'] = yoke
T = V(39.5, 113, 247.5); P = V(39.5, 113, 0)


def tilt_hits(env, angles=range(-38, 35, 2)):
    out = []
    for t in angles:
        for k in groups['tilt']:
            s = S[k].copy(); s.rotate(T, V(1, 0, 0), t)
            if env.common(s).Volume > 0.05:
                out.append((k, t))
    return out


# static: board, inserts, lead and bolt head against everything on the pan/fixed side
static = {}
for nm, sh in (('pcb', pcb), ('bolt_head', bolt_head), ('lead', lead)):
    static[nm] = sorted(k for k in S if k not in groups['tilt'] and sh.common(S[k]).Volume > 0.05
                        and not (nm == 'lead' and k == 'Pan_Raised_Pedestal'))
static['pcb_vs_bolt_head'] = round(pcb.common(bolt_head).Volume, 3)
static['pcb_vs_new_yoke'] = round(pcb.common(yoke).Volume, 3)
R['static_overlaps'] = static
R['pcb_tilt_hits'] = tilt_hits(pcb)
R['lead_tilt_hits'] = tilt_hits(lead)

# part-height zones: tallest component height above the board top that clears every tilt pose
zones = {
    'front_left (X 40.6-49, Y 93.5-109.5)': board2d.common(face_of([(40, 90), (49, 90), (49, 109.5), (40, 109.5)])),
    'front_right (X 49-63.5, Y 97-108.5)': board2d.common(face_of([(49, 90), (64, 90), (64, 108.5), (49, 108.5)])),
    'connector_band (Y 109.5-118.5, X 40.6-56.3)': board2d.common(face_of([(40, 109.5), (56.3, 109.5), (56.3, 118.5), (40, 118.5)])),
    'rear (Y 118.5-123)': board2d.common(face_of([(40, 118.5), (64, 118.5), (64, 123.5), (40, 123.5)])),
}
heights = {}
env_shapes = {}
for zn, f in zones.items():
    f = f.Faces[0]
    best = 0.0
    for h in (30, 20, 15, 12, 10, 8, 7, 6, 5, 4, 3, 2, 1):
        env = prism(f, PCB_TOP, PCB_TOP + h)
        if not tilt_hits(env):
            best = h; env_shapes[zn] = env
            break
    heights[zn] = best
    print('zone', zn, 'max part height above board', best)
R['max_part_height_above_board_mm'] = heights

# pan: board and envelopes against the fixed side (they turn with the yoke)
pan_hits = set()
allenv = Part.makeCompound([pcb, lead] + list(env_shapes.values()))
for p in range(-20, 181, 10):
    s = allenv.copy(); s.rotate(P, V(0, 0, 1), p)
    for k in groups['fixed']:
        if k in S and s.common(S[k]).Volume > 0.05:
            pan_hits.add(k)
R['pan_fixed_hits'] = sorted(pan_hits)

# ---------------------------------------------------------------- save native file
d.getObject('Tilt_Yoke').Shape = yoke
def add(name, shape):
    o = d.addObject('Part::Feature', name); o.Shape = shape; return o
add('Head_Distro_PCB_Placeholder', pcb)
for k, s in zip(INSERTS, inserts):
    add('M2_Insert_' + k, s)
add('Tilt_Lead_Route', lead)
add('Yoke_Bolt_Head_M3', bolt_head)
for i, (zn, s) in enumerate(env_shapes.items()):
    add('PCB_Part_Height_Zone_%d' % (i + 1), s)
d.recompute()
d.saveAs(str(OUT))

# ---------------------------------------------------------------- print STL (floor on the bed, as v2)
stl = HERE / 'stl'; stl.mkdir(exist_ok=True)
pr = yoke.copy(); pr.translate(V(-pr.BoundBox.XMin, -pr.BoundBox.YMin, -pr.BoundBox.ZMin))
m = Mesh.Mesh(pr.tessellate(0.02)); m.write(str(stl / 'Gladiator_Head_v2_Tilt_Yoke_PCB.stl'))
mb = m.BoundBox
R['print_stl'] = {'file': 'stl/Gladiator_Head_v2_Tilt_Yoke_PCB.stl', 'orientation': 'floor on the bed, no support',
                  'size_mm': [round(mb.XLength, 1), round(mb.YLength, 1), round(mb.ZLength, 1)],
                  'solid': m.isSolid(), 'non_manifold': m.hasNonManifolds(),
                  'grams_solid_pla': round(yoke.Volume * 1.24e-3, 1)}
R['params'] = dict(SEAT_D=SEAT_D, SEAT_Z=SEAT_Z, PCB_T=PCB_T, RELIEF_D=RELIEF_D, RELIEF_INSET=RELIEF_INSET,
                   INSERT_BORE=INSERT_BORE, INSERT_LEN=INSERT_LEN, INSERTS=INSERTS, OUTLINE=OUTLINE, CHANNEL=CHANNEL)
R['pcb_outline_bbox'] = [round(v, 2) for v in (pcb.BoundBox.XMin, pcb.BoundBox.XMax, pcb.BoundBox.YMin, pcb.BoundBox.YMax)]
(HERE / 'validation.json').write_text(json.dumps(R, indent=1))
print(json.dumps(R, indent=1))
os._exit(0)
