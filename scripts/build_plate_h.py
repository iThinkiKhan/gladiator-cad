"""Plate H - a fast one: upper deck v2 and the corrected GH44 receiver.

Both are low and flat, which is the quick case - the deck is 14 tall with 8 mm2 of
support and the receiver is 4 tall with none. No mixed-height stall, no brim
needed, nothing tall enough to knock over.
"""
import os
import sys
import zipfile

import FreeCAD as App
import Mesh

_p = print


def print(*a, **k):
    _p(*a, **k)
    sys.stdout.flush()


REPO = '/home/buralien/projects/gladiator-cad'
SRC = REPO + '/cad/print-ready'
OUT = '/home/buralien/Desktop/3D-Printer-Incoming'
NL = chr(10)

BED_X, BED_Y, MARGIN, GAP = 220.0, 220.0, 10.0, 8.0

PARTS = [
    ('UpperDeck_v2', 'Gladiator_P4_UpperDeck_print-flat-bosses-up.stl',
     'flat, bosses up, 8 mm2 support. Expander pattern now 40.10 x 64.10 in the '
     'front corner, plus the wire pass-through.'),
    ('GH44_Receiver', 'Gladiator_REPRINT_GH44_Receiver_recess-UP.stl',
     'recess UP, flat back on the bed. Replaces the one that printed inverted.'),
]


def load(path, name):
    m = Mesh.Mesh(path)
    b = m.BoundBox
    m.translate(-b.XMin, -b.YMin, -b.ZMin)
    return [name, m]


def write_3mf(path, title, items):
    md = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<model unit="millimeter" xml:lang="en-US" '
          'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
          '<metadata name="Title">%s</metadata>' % title,
          '<metadata name="Application">gladiator-cad build_plate_h.py</metadata>',
          '<resources>']
    for oid, (nm, m) in enumerate(items, start=1):
        pts, fcs = m.Topology
        md.append('<object id="%d" type="model" name="%s"><mesh><vertices>' % (oid, nm))
        for q in pts:
            md.append('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % (q.x, q.y, q.z))
        md.append('</vertices><triangles>')
        for f in fcs:
            md.append('<triangle v1="%d" v2="%d" v3="%d"/>' % (f[0], f[1], f[2]))
        md.append('</triangles></mesh></object>')
    md.append('</resources>')
    md.append('<build>')
    for oid in range(1, len(items) + 1):
        md.append('<item objectid="%d" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>' % oid)
    md.append('</build>')
    md.append('</model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?>'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
          '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
            '</Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', ct)
        z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', NL.join(md))


items = []
for name, fn, note in PARTS:
    p = os.path.join(SRC, fn)
    if not os.path.exists(p):
        raise SystemExit('missing %s' % p)
    items.append(load(p, name))
    print('%-16s %s' % (name, fn))
    print('   %s' % note)

# lay them out left to right, widest first
items.sort(key=lambda it: -it[1].BoundBox.XLength)
x = MARGIN
placed = []
total_vol = 0.0
for name, m in items:
    b = m.BoundBox
    y = BED_Y / 2.0 - b.YLength / 2.0
    m.translate(x - b.XMin, y - b.YMin, 0)
    b = m.BoundBox
    placed.append((name, m, b))
    x += b.XLength + GAP
    total_vol += m.Volume

print()
ok = True
for i, (n, m, b) in enumerate(placed):
    print('   %-16s %6.1f x %-6.1f h %5.1f   at X %6.1f-%6.1f  Y %6.1f-%6.1f'
          % (n, b.XLength, b.YLength, b.ZLength, b.XMin, b.XMax, b.YMin, b.YMax))
    if b.XMin < MARGIN - 0.01 or b.XMax > BED_X - MARGIN + 0.01 \
       or b.YMin < MARGIN - 0.01 or b.YMax > BED_Y - MARGIN + 0.01:
        print('      *** outside the usable bed')
        ok = False
    if abs(b.ZMin) > 1e-6:
        print('      *** not on the bed')
        ok = False
    if not m.isSolid() or m.hasSelfIntersections():
        print('      *** mesh is not a clean solid')
        ok = False
    for j in range(i + 1, len(placed)):
        n2, m2, b2 = placed[j]
        if not (b.XMax <= b2.XMin or b2.XMax <= b.XMin
                or b.YMax <= b2.YMin or b2.YMax <= b.YMin):
            print('      *** overlaps %s' % n2)
            ok = False

used_x = max(b.XMax for _, _, b in placed) - MARGIN
used_y = max(b.YMax for _, _, b in placed) - min(b.YMin for _, _, b in placed)
print()
print('bed used %.1f x %.1f of %.0f x %.0f' % (used_x, used_y, BED_X, BED_Y))
print('total solid %.2f cm3 -> about %.0f g in PLA if it were solid; Orca will say less'
      % (total_vol / 1000.0, total_vol * 1.24 / 1000.0))
print('tallest part %.1f mm' % max(b.ZLength for _, _, b in placed))

if not ok:
    raise SystemExit('layout failed - nothing written')

name = 'Gladiator_PlateH_DECK-AND-GH44.3mf'
for d in (OUT, SRC):
    write_3mf(os.path.join(d, name), 'Gladiator Plate H - upper deck v2 and the GH44 receiver',
              [(n, m) for n, m, _ in placed])
print()
print('wrote %s (%.0f kB)' % (name, os.path.getsize(os.path.join(OUT, name)) / 1024.0))
