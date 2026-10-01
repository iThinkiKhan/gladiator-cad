"""Head v0.4 print plates 2 and 3, released after the final coupon plate (2026-10-01).

    Plate 2, pan drive:  Pan_Rotor, Pan_Drive_Pulley, Pan_Servo_Carriage       (no supports)
    Plate 3, tilt side:  Tilt_Yoke, GH44_Tilt_Receiver, Rear_Display_Frame     (supports: frame tabs)

Held back on purpose: Neck_Main (the horn height is not measured) and GH44_Dual_Carrier (no sensor
mounting yet). Plate 1 is built by build_head_v04_plate1.py and is unchanged.
Reads the STLs written by build_head_v04.py. Run with freecadcmd on the CAD server.
"""
import sys, zipfile, json
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod', '/usr/lib/freecad-python3/lib'])
import Mesh

ROOT = Path('/home/buralien/projects/gladiator-cad')
OUT = ROOT / 'cad/head/v04-pan-stack'
STL = OUT / 'stl'
BED_X, BED_Y, MARGIN, GAP = 220.0, 220.0, 10.0, 12.0
PLATES = {
    'Gladiator_Head_v04_PLATE2_PanDrive_Rotor-Pulley-Carriage.3mf':
        ['Pan_Rotor', 'Pan_Drive_Pulley', 'Pan_Servo_Carriage'],
    'Gladiator_Head_v04_PLATE3_Tilt_Yoke-Receiver-DisplayFrame.3mf':
        ['Tilt_Yoke', 'GH44_Tilt_Receiver', 'Rear_Display_Frame'],
}
NL = chr(10)


def write_3mf(path, title, its):
    md = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<model unit="millimeter" xml:lang="en-US" '
          'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
          '<metadata name="Title">%s</metadata>' % title,
          '<metadata name="Application">gladiator-cad build_head_v04_plates.py</metadata>', '<resources>']
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


report = {}
for fname, names in PLATES.items():
    items = []
    for n in names:
        m = Mesh.Mesh(str(STL / ('Gladiator_Head_v04_%s.stl' % n)))
        b = m.BoundBox
        m.translate(-b.XMin, -b.YMin, -b.ZMin)
        items.append([n, m])
    items.sort(key=lambda it: -it[1].BoundBox.YLength)
    shelves, cur, curw, curd = [], [], 0.0, 0.0
    for it in items:
        b = it[1].BoundBox
        if cur and curw + GAP + b.XLength > BED_X - 2 * MARGIN:
            shelves.append((cur, curw, curd))
            cur, curw, curd = [], 0.0, 0.0
        curw = b.XLength if not cur else curw + GAP + b.XLength
        curd = max(curd, b.YLength)
        cur.append(it)
    if cur:
        shelves.append((cur, curw, curd))
    total_d = sum(s[2] for s in shelves) + GAP * (len(shelves) - 1)
    y = BED_Y / 2.0 - total_d / 2.0
    for row, roww, rowd in shelves:
        x = BED_X / 2.0 - roww / 2.0
        for it in row:
            b = it[1].BoundBox
            it[1].translate(x - b.XMin, y + (rowd - b.YLength) / 2.0 - b.YMin, 0)
            x += b.XLength + GAP
        y += rowd + GAP
    offbed = overlaps = 0
    for n, m in items:
        b = m.BoundBox
        if not (b.XMin >= MARGIN - .01 and b.XMax <= BED_X - MARGIN + .01 and b.YMin >= MARGIN - .01
                and b.YMax <= BED_Y - MARGIN + .01 and abs(b.ZMin) < 1e-6):
            offbed += 1
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i][1].BoundBox, items[j][1].BoundBox
            if a.XMin < b.XMax and b.XMin < a.XMax and a.YMin < b.YMax and b.YMin < a.YMax:
                overlaps += 1
    path = OUT / 'plates' / fname
    write_3mf(str(path), fname[:-4], items)
    xml = zipfile.ZipFile(str(path)).read('3D/3dmodel.model').decode()
    vol = sum(m.Volume for _, m in items)
    report[fname] = {'parts': names, 'objects_in_3mf': xml.count('<object '),
                     'triangles_ok': xml.count('<triangle ') == sum(len(m.Topology[1]) for _, m in items),
                     'offbed': offbed, 'overlaps': overlaps, 'volume_cm3': round(vol / 1000, 2),
                     'grams_pla': round(vol * 0.00124), 'tallest_mm': round(max(m.BoundBox.ZLength for _, m in items), 1)}
(OUT / 'plates' / 'plates-2-3-validation.json').write_text(json.dumps(report, indent=2) + NL)
print(json.dumps(report, indent=2))
