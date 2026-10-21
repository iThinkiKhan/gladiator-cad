"""Speaker bracket for shell-off running (2026-10-20, Claude).

Run: freecadcmd build_speaker_rail_bracket.py

Jim 2026-10-20: the speaker lives under the hood roof when the shell is on; with the shell off, a cradle screws into the shell's hard points on the side of a rail.
This bracket uses the LEFT rail's two rear hood inserts (CAD (Y22, Z40) and (Y35.5, Z46) on the rail's outer face X9.5; the right rail carries the switch and INA leads).
The speaker faces outward (-X) over the left track.

Speaker (Jim): box 28 wide x 31 high x 15 deep, ears tip to tip 44, ear holes 36.5 apart. Ears 2.8 thick, centred between the front and rear faces, M2 screws (Jim 2026-10-21).
Built in the CAD rail frame, then moved with the rail to its installed position (left rail 2.0 mm out, turned 0.64 degrees about the rear peg).
Fitting order: screw the plate to the rail (2 x M3 x 10 into the inserts), then the speaker onto the posts (2 x M2 through the ears from the front).
"""
import FreeCAD as A, Part, MeshPart, math, json, os, traceback
from pathlib import Path

V = A.Vector
R = Path('/home/buralien/projects/gladiator-cad')
O = R / 'cad/v2/speaker-mount/v1-20261020'
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
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


SPL = math.atan(1.0 / 89.0)


def real_left(shp):
    q = plain(shp)
    q.translate(V(-2.0, 0, 0))
    q.rotate(V(12.0, 23.85, 0), V(0, 0, 1), math.degrees(SPL))
    return q


P = dict(face_x=9.5, inserts=[(22.0, 40.0), (35.5, 46.0)], plate_t=3.0, plate_y=(5.0, 52.0), plate_z=(30.0, 52.5), m3_clear=3.6, m3_head_gap=5.2,
         spk=dict(w=28.0, h=31.0, d=15.0, ear_tip=44.0, hole_c=36.5, ear_t=2.8, ear_mid=7.5, ear_w=10.0), spk_cy=28.75, spk_cz=37.0,
         post_d=7.0, pilot_d=1.6, pilot_depth=6.0)
p = P
FX = p['face_x']
PX0 = FX - p['plate_t']                       # plate outer face 6.5
SPK_BACK = PX0 - p['m3_head_gap']             # speaker back clears the M3 heads: 2.9
sp = p['spk']
SPK_FRONT = SPK_BACK - sp['d']                # -12.1, facing -X
EAR_FRONT = SPK_FRONT + sp['ear_mid'] - sp['ear_t'] / 2     # ears centred between the faces (Jim 2026-10-21)
EAR_BACK = SPK_FRONT + sp['ear_mid'] + sp['ear_t'] / 2
cy, cz = p['spk_cy'], p['spk_cz']
EARS = [(cy - sp['hole_c'] / 2, cz), (cy + sp['hole_c'] / 2, cz)]

plate = box(PX0, FX, p['plate_y'][0], p['plate_y'][1], p['plate_z'][0], p['plate_z'][1])
posts = []
for (ey, ez) in EARS:
    posts.append(Part.makeCylinder(p['post_d'] / 2, PX0 - EAR_BACK + 0.01, V(EAR_BACK, ey, ez), V(1, 0, 0)))
    # gusset above each post, inside the plate outline (prints flat on the plate, the post standing up)
    g = Part.Face(Part.makePolygon([V(PX0, ey - 1.5, ez + 3.0), V(PX0, ey - 1.5, ez + 3.0 + (PX0 - EAR_BACK) * 0.6), V(EAR_BACK + 2.0, ey - 1.5, ez + 3.0),
                                    V(PX0, ey - 1.5, ez + 3.0)])).extrude(V(0, 3.0, 0))
    posts.append(g)
bracket = fuse(plate, *posts)
cuts = []
for (iy, iz) in p['inserts']:
    cuts.append(Part.makeCylinder(p['m3_clear'] / 2, p['plate_t'] + 2, V(PX0 - 1, iy, iz), V(1, 0, 0)))
for (ey, ez) in EARS:
    cuts.append(Part.makeCylinder(p['pilot_d'] / 2, p['pilot_depth'] + 0.1, V(EAR_BACK - 0.1, ey, ez), V(1, 0, 0)))
bracket = cut(bracket, *cuts)

spk = fuse(box(SPK_FRONT, SPK_BACK, cy - sp['w'] / 2, cy + sp['w'] / 2, cz - sp['h'] / 2, cz + sp['h'] / 2),
           box(EAR_FRONT, EAR_BACK, cy - sp['ear_tip'] / 2, cy + sp['ear_tip'] / 2, cz - sp['ear_w'] / 2, cz + sp['ear_w'] / 2))
heads = [Part.makeCylinder(2.75, 3.0, V(PX0 - 3.0, iy, iz), V(1, 0, 0)) for (iy, iz) in p['inserts']]

bracket_r, spk_r = real_left(bracket), real_left(spk)
heads_r = [real_left(h) for h in heads]

chk = dict(status='v1 DRAFT - not printed', parameters=P, part=dict(valid=bracket.isValid(), solids=len(bracket.Solids), volume_mm3=round(bracket.Volume, 1), grams=round(bracket.Volume * 1.24e-3, 1)))
chk['fit'] = dict(speaker_vs_bracket=round(hit(spk, bracket), 3), heads_vs_speaker=[round(hit(h, spk), 3) for h in heads], heads_vs_bracket=[round(hit(h, bracket), 3) for h in heads])
try:
    cd = A.openDocument(str(R / 'cad/enclosure/concept-20261013/Gladiator_Enclosure_Concept.FCStd'))
    refs = {o.Name: plain(o.Shape) for o in cd.Objects if o.Name.startswith(('Ref_', 'Track_Approx', 'Wheel_Approx'))
            and not o.Name.startswith(('Ref_SideRail', 'Ref_UpperDeck', 'Ref_INA226', 'Ref_PowerSwitch', 'Ref_Switch', 'Ref_PowerBoardTray', 'Ref_Base', 'Ref_BoardReference'))}
    rd = A.openDocument(str(R / 'cad/v2/rails/v4-20261015/Gladiator_ArchRails_v4.FCStd'))
    refs['rail_left_installed'] = real_left(rd.getObject('Arch_Rail_Left_v4').Shape)
    deck = plain(A.openDocument(str(R / 'cad/v2/upper-deck/v4-20261016/Gladiator_UpperDeck_v4.FCStd')).getObject('UpperDeck_v4').Shape)
    refs['deck_v4'] = deck
    for dx in (-2.0, 2.0):
        d2 = plain(deck)
        d2.translate(V(dx, 0, 0))
        refs['deck_v4_x%+.0f' % dx] = d2
    refs['tray_v5'] = plain(A.openDocument(str(R / 'cad/power-board/v5-tray/PowerBoardTray_v5.FCStd')).getObject('PowerBoardTray').Shape)
    col = {}
    for nm, shp in (('bracket', bracket_r), ('speaker', spk_r)):
        c_ = {rn: round(hit(shp, rs), 3) for rn, rs in refs.items() if abs(hit(shp, rs)) > 0.01}
        col[nm] = c_ or 'clear'
    chk['collisions'] = col
    chk['bracket_on_rail_face_gap_mm'] = round(bracket_r.distToShape(refs['rail_left_installed'])[0], 3)
    chk['nearest_mm'] = {nm: sorted([(round(shp.distToShape(rs)[0], 2), rn) for rn, rs in refs.items() if shp.distToShape(rs)[0] < 6])[:5] for nm, shp in (('bracket', bracket_r), ('speaker', spk_r))}
except Exception:
    traceback.print_exc()

doc = A.newDocument('Gladiator_Speaker_Rail_Bracket_v1')
for n, s_ in (('Speaker_Rail_Bracket_v1', bracket_r), ('Speaker_envelope', spk_r)):
    o = doc.addObject('Part::Feature', n)
    o.Shape = s_
doc.recompute()
doc.saveAs(str(O / 'Gladiator_Speaker_Rail_Bracket_v1.FCStd'))
Part.export([doc.getObject('Speaker_Rail_Bracket_v1')], str(O / 'Gladiator_Speaker_Rail_Bracket_v1.step'))
# print: plate flat on the bed (its rail face down), posts standing up
c = plain(bracket)
c.rotate(V(0, 0, 0), V(0, 1, 0), 90)
c.translate(V(-c.BoundBox.XMin, -c.BoundBox.YMin, -c.BoundBox.ZMin))
m = MeshPart.meshFromShape(Shape=c, LinearDeflection=0.02, AngularDeflection=math.radians(8))
m.write(str(O / 'Gladiator_Speaker_Rail_Bracket_v1.stl'))
chk['stl'] = dict(is_solid=m.isSolid(), non_manifold=m.hasNonManifolds(), size_mm=[round(c.BoundBox.XLength, 1), round(c.BoundBox.YLength, 1), round(c.BoundBox.ZLength, 1)],
                  orientation='rail face down on the bed, posts up, no supports')
(O / 'validation.json').write_text(json.dumps(chk, indent=1, default=str))
print(json.dumps(chk, indent=1, default=str)[:4000], flush=True)
os._exit(0)
