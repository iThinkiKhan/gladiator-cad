"""Plate F - every coupon still worth printing.

Plate F = Plate E, minus Coupon C, plus Coupon D.

  - Coupon C (self-tap pilots) is OBSOLETE. Jim settled on nuts and washers on
    2026-09-20, so the driver pilots became 3.6 clearance holes and there is no
    thread to form. Dropping it saves 2.7 g and, more to the point, stops a stale
    test producing an answer nobody needs.
  - Coupon D (SMA bore) did not exist when Plate E was built - it was committed
    two minutes earlier - so Plate E never picked it up. It is the last guessed
    dimension on plate B.

The head coupons' geometry is taken straight out of Plate E rather than
regenerated, so it stays byte-identical to what the head workstream built in
`scripts/build_coupon_plate.py`. This script only re-packs the bed.
"""
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

import FreeCAD as App
import Mesh

_p = print


def print(*a, **k):
    _p(*a, **k)
    sys.stdout.flush()


REPO = '/home/buralien/projects/gladiator-cad'
OUT = '/home/buralien/Desktop/3D-Printer-Incoming'
MIRROR = REPO + '/cad/print-ready'
NS = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'

PLATE_E = os.path.join(MIRROR, 'Gladiator_PlateE_ALL-COUPONS.3mf')
COUPON_D = os.path.join(MIRROR, 'Gladiator_CouponD_SmaBore_counterbore-DOWN.stl')
DROP = ('CouponC_SelfTapPilots',)

BED_X, BED_Y, MARGIN, GAP = 220.0, 220.0, 10.0, 8.0
NL = chr(10)


def read_3mf(path):
    z = zipfile.ZipFile(path)
    root = ET.fromstring(z.read('3D/3dmodel.model').decode('utf-8'))
    out = []
    for o in root.findall('.//%sobject' % NS):
        vs = [(float(v.get('x')), float(v.get('y')), float(v.get('z')))
              for v in o.findall('.//%svertex' % NS)]
        ts = [(int(t.get('v1')), int(t.get('v2')), int(t.get('v3')))
              for t in o.findall('.//%striangle' % NS)]
        out.append([o.get('name'), vs, ts])
    return out


def read_stl(path, name):
    m = Mesh.Mesh(path)
    pts, fcs = m.Topology
    return [name, [(p.x, p.y, p.z) for p in pts], [tuple(f) for f in fcs]]


def normalise(item):
    """drop to the bed and to the origin corner"""
    name, vs, ts = item
    xs = [v[0] for v in vs]
    ys = [v[1] for v in vs]
    zs = [v[2] for v in vs]
    dx, dy, dz = -min(xs), -min(ys), -min(zs)
    return [name, [(v[0] + dx, v[1] + dy, v[2] + dz) for v in vs], ts,
            max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)]


def write_3mf(path, title, items):
    md = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<model unit="millimeter" xml:lang="en-US" '
          'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
          '<metadata name="Title">%s</metadata>' % title,
          '<metadata name="Application">gladiator-cad build_plate_f.py</metadata>',
          '<resources>']
    for oid, (nm, vs, ts) in enumerate(items, start=1):
        md.append('<object id="%d" type="model" name="%s"><mesh><vertices>' % (oid, nm))
        for q in vs:
            md.append('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % q)
        md.append('</vertices><triangles>')
        for f in ts:
            md.append('<triangle v1="%d" v2="%d" v3="%d"/>' % f)
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


raw = read_3mf(PLATE_E)
print('plate E carries %d objects' % len(raw))
kept = [r for r in raw if r[0] not in DROP]
for r in raw:
    if r[0] in DROP:
        print('   dropping %s (obsolete - nuts and washers chosen)' % r[0])
kept.append(read_stl(COUPON_D, 'CouponD_SmaBore'))
print('   adding CouponD_SmaBore (postdates plate E)')
print('plate F will carry %d objects' % len(kept))

items = [normalise(k) for k in kept]

# shelf pack, tallest footprint first
items.sort(key=lambda r: -r[4])
x, y, shelf = MARGIN, MARGIN, 0.0
placed = []
for name, vs, ts, w, d, h in items:
    if x + w > BED_X - MARGIN:
        x = MARGIN
        y += shelf + GAP
        shelf = 0.0
    placed.append((name, [(v[0] + x, v[1] + y, v[2]) for v in vs], ts, x, y, w, d, h))
    x += w + GAP
    shelf = max(shelf, d)
top = y + shelf

print()
ok = True
if top > BED_Y - MARGIN:
    print('*** does not fit: needs %.1f of bed depth' % top)
    ok = False
for i, (n, vs, ts, px, py, w, d, h) in enumerate(placed):
    print('   %-30s %6.1f x %-6.1f h %5.1f   at X %6.1f Y %6.1f' % (n, w, d, h, px, py))
    if px < MARGIN - 0.01 or px + w > BED_X - MARGIN + 0.01 \
       or py < MARGIN - 0.01 or py + d > BED_Y - MARGIN + 0.01:
        print('      *** outside the usable bed')
        ok = False
    for j in range(i + 1, len(placed)):
        n2, _, _, qx, qy, w2, d2, _ = placed[j]
        if not (px + w <= qx or qx + w2 <= px or py + d <= qy or qy + d2 <= py):
            print('      *** overlaps %s' % n2)
            ok = False

print()
print('bed used: %.1f x %.1f of %.0f x %.0f' % (BED_X - 2 * MARGIN, top - MARGIN, BED_X, BED_Y))
if not ok:
    raise SystemExit('layout failed - nothing written')

final = [(n, vs, ts) for n, vs, ts, _, _, _, _, _ in placed]
for d in (OUT, MIRROR):
    write_3mf(os.path.join(d, 'Gladiator_PlateF_ALL-COUPONS.3mf'),
              'Gladiator Plate F - every coupon still worth printing', final)
print('wrote Gladiator_PlateF_ALL-COUPONS.3mf (%.0f kB)'
      % (os.path.getsize(os.path.join(OUT, 'Gladiator_PlateF_ALL-COUPONS.3mf')) / 1024.0))
