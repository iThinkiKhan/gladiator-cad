"""Head v0.4 print plate 1: the three parts that wait on no coupon result.

    Pan_Raised_Pedestal   the belt line is set by this part, so it is printed first
    Pan_Retainer
    Neck_Clamp_Cap

Reads the STLs written by build_head_v04.py, arranges them on the 220 x 220 bed, writes a 3MF.
Run with freecadcmd on the CAD server.
"""
import sys, zipfile, json
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod', '/usr/lib/freecad-python3/lib'])
import Mesh

ROOT = Path('/home/buralien/projects/gladiator-cad')
OUT = ROOT / 'cad/head/v04-pan-stack'
STL = OUT / 'stl'
(OUT / 'plates').mkdir(exist_ok=True)
BED_X, BED_Y, MARGIN, GAP = 220.0, 220.0, 10.0, 12.0
NAMES = ['Pan_Raised_Pedestal', 'Pan_Retainer', 'Neck_Clamp_Cap']

items = []
for n in NAMES:
    m = Mesh.Mesh(str(STL / ('Gladiator_Head_v04_%s.stl' % n)))
    b = m.BoundBox
    m.translate(-b.XMin, -b.YMin, -b.ZMin)
    items.append([n, m])
items.sort(key=lambda it: -it[1].BoundBox.YLength)

total_w = sum(it[1].BoundBox.XLength for it in items) + GAP * (len(items) - 1)
x = BED_X / 2.0 - total_w / 2.0
for it in items:
    b = it[1].BoundBox
    it[1].translate(x - b.XMin, BED_Y / 2.0 - b.YLength / 2.0 - b.YMin, 0)
    x += b.XLength + GAP

offbed = overlaps = 0
for n, m in items:
    b = m.BoundBox
    if not (b.XMin >= MARGIN and b.XMax <= BED_X - MARGIN and b.YMin >= MARGIN and b.YMax <= BED_Y - MARGIN
            and abs(b.ZMin) < 1e-6):
        offbed += 1
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        a, b = items[i][1].BoundBox, items[j][1].BoundBox
        if a.XMin < b.XMax and b.XMin < a.XMax and a.YMin < b.YMax and b.YMin < a.YMax:
            overlaps += 1

NL = chr(10)


def write_3mf(path, title, its):
    md = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<model unit="millimeter" xml:lang="en-US" '
          'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
          '<metadata name="Title">%s</metadata>' % title,
          '<metadata name="Application">gladiator-cad build_head_v04_plate1.py</metadata>', '<resources>']
    for oid, (nm, m) in enumerate(its, start=1):
        pts, fcs = m.Topology
        md.append('<object id="%d" type="model" name="%s"><mesh><vertices>' % (oid, nm))
        for q in pts:
            md.append('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % (q.x, q.y, q.z))
        md.append('</vertices><triangles>')
        for f in fcs:
            md.append('<triangle v1="%d" v2="%d" v3="%d"/>' % (f[0], f[1], f[2]))
        md.append('</triangles></mesh></object>')
    md.append('</resources><build>')
    for oid in range(1, len(its) + 1):
        md.append('<item objectid="%d" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>' % oid)
    md.append('</build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?>'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
          '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', ct)
        z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', NL.join(md))


plate = OUT / 'plates' / 'Gladiator_Head_v04_PLATE1_Pedestal-Retainer-Cap.3mf'
write_3mf(str(plate), 'Gladiator head v0.4 plate 1', items)
xml = zipfile.ZipFile(str(plate)).read('3D/3dmodel.model').decode()
n_obj, n_tri = xml.count('<object '), xml.count('<triangle ')
tri_expected = sum(len(m.Topology[1]) for _, m in items)
vol = sum(m.Volume for _, m in items)
rep = {'file': plate.name, 'parts': NAMES, 'objects_in_3mf': n_obj, 'triangles_ok': n_tri == tri_expected,
       'offbed': offbed, 'overlaps': overlaps, 'volume_cm3': round(vol / 1000, 2),
       'grams_pla': round(vol * 0.00124), 'unit_mm': 'unit="millimeter"' in xml,
       'footprints_mm': {n: [round(m.BoundBox.XLength, 1), round(m.BoundBox.YLength, 1), round(m.BoundBox.ZLength, 1)]
                         for n, m in items}}
(OUT / 'plates' / 'plate1-validation.json').write_text(json.dumps(rep, indent=2) + NL)
print(json.dumps(rep, indent=2))
