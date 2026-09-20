"""Plate E - every remaining coupon, arranged on the bed.

Round features on this printer come out about 0.25 mm UNDER, convex and concave
alike (measurements/printer-calibration.md, round 1). Every bracket below is
centred on the COMPENSATED value, not the nominal, so the winner goes straight
into the CAD.
"""
import sys, math, zipfile
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as A, Part, Mesh, MeshPart
from pathlib import Path

ROOT = Path('/home/buralien/projects/gladiator-cad')
O = []
def p(s): O.append(s)
BED_X, BED_Y, MARGIN, GAP = 220.0, 220.0, 10.0, 8.0
LIN, ANG = 0.01, 0.0872665
CURVE_ERR = 0.25

def cyl(r, z, h, x=0, y=0): return Part.makeCylinder(r, h, A.Vector(x, y, z))
def box(x, y, z, dx, dy, dz): return Part.makeBox(dx, dy, dz, A.Vector(x, y, z))
def fuse(*ss):
    s = ss[0]
    for t in ss[1:]: s = s.fuse(t)
    return s.removeSplitter()
def marks(shape, n, r_at, z, h, start=0.0, step=11.0, rad=1.0):
    for k in range(n):
        a = math.radians(start + (k - (n - 1) / 2.0) * step)
        shape = shape.cut(cyl(rad, z - 0.5, h + 1.0,
                              r_at * math.cos(a), r_at * math.sin(a)))
    return shape

NL = chr(10)

def write_3mf(path, title, items):
    md = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<model unit="millimeter" xml:lang="en-US" '
          'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
          '<metadata name="Title">%s</metadata>' % title,
          '<metadata name="Application">gladiator-cad build_coupon_plate.py</metadata>',
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

pieces = []

# ---- 1. belt mesh, three groove widths ------------------------------------
PITCH, PLD, DEPTH, N, W, ARC = 2.0, 0.254, 0.75, 60, 6.0, 60.0

def sector(r, z, h, a0, a1):
    keep = []
    a = a0
    while a < a1 - 1e-9:
        b = min(a + 10.0, a1)
        tri = Part.makePolygon([
            A.Vector(0, 0, z),
            A.Vector(2 * r * math.cos(math.radians(a)), 2 * r * math.sin(math.radians(a)), z),
            A.Vector(2 * r * math.cos(math.radians(b)), 2 * r * math.sin(math.radians(b)), z),
            A.Vector(0, 0, z)])
        keep.append(Part.Face(tri).extrude(A.Vector(0, 0, h)))
        a = b
    return cyl(r, z, h).common(fuse(*keep))

pd = N * PITCH / math.pi
ro = (pd - 2 * PLD) / 2.0
p('BELT MESH   2GT 60T, pitch dia %.3f, depth held at %.2f' % (pd, DEPTH))
for mk, gr in [(1, 0.60), (2, 0.65), (3, 0.70)]:
    rc = ro - DEPTH + gr
    b = cyl(ro, 0, W)
    for t in range(N):
        a = 2 * math.pi * t / N
        b = b.cut(cyl(gr, -0.1, W + 0.2, rc * math.cos(a), rc * math.sin(a)))
    b = b.common(sector(30, -1, W + 2, -ARC / 2, ARC / 2)).cut(cyl(12, -1, W + 2))
    b = marks(b, mk, 12.0, -1, W + 2, 0.0, 7.0, 1.0)
    half = math.sqrt(max(gr ** 2 - (ro - rc) ** 2, 0))
    p('  %d marks  groove r %.2f -> width %.3f  land %.3f'
      % (mk, gr, 2 * half, 2 * math.pi * ro / N - 2 * half))
    pieces.append(('BeltMesh_%dmark_r%.2f' % (mk, gr), b))

# ---- 2. bearing outer seat -------------------------------------------------
p('')
p('BEARING SEAT   6804 OD 32.00, want a physical 32.05 to 32.10')
for mk, d in [(1, 32.20), (2, 32.35), (3, 32.50)]:
    r = cyl(18.5, 0, 4).cut(cyl(d / 2.0, -0.5, 5))
    r = marks(r, mk, 18.5, 0, 4, 90.0, 9.0, 1.0)
    p('  %d marks  modelled %.2f -> expect printed ~%.2f' % (mk, d, d - CURVE_ERR))
    pieces.append(('BearingSeat_%dmark_%.2f' % (mk, d), r))

# ---- 3. spindle post -------------------------------------------------------
p('')
p('SPINDLE POST   6804 bore 20.00, want a physical ~19.95, 12 mm bore like the real spindle')
for mk, d in [(1, 20.05), (2, 20.20), (3, 20.35)]:
    t = cyl(d / 2.0, 0, 6).cut(cyl(6.0, -0.5, 7))
    t = marks(t, mk, d / 2.0, 0, 6, 90.0, 13.0, 0.9)
    p('  %d marks  modelled %.2f -> expect printed ~%.2f' % (mk, d, d - CURVE_ERR))
    pieces.append(('SpindlePost_%dmark_%.2f' % (mk, d), t))

# ---- 4. screen mount gauge -------------------------------------------------
CW, CL = 24.0 + 2.0, 56.25 + 2.0
M2_CLEAR = 2.6
p('')
p('SCREEN MOUNT GAUGE')
p('  centres %.2f wide x %.2f long  = your inside readings + the confirmed M2 dia' % (CW, CL))
p('  predicts outside-to-outside %.2f and %.2f, edge gaps %.3f and %.3f'
  % (CW + 2.0, CL + 2.0, (29.0 - (CW + 2.0)) / 2, (62.5 - (CL + 2.0)) / 2))
p('  holes at %.1f - calibrated M2 clearance; 2.2 and 2.4 would not pass' % M2_CLEAR)
g = box(-34, -17, 0, 68, 34, 2).cut(box(-28, -11, -0.5, 56, 22, 3))
for x in (-CL / 2, CL / 2):
    for y in (-CW / 2, CW / 2):
        g = g.cut(cyl(M2_CLEAR / 2.0, -0.5, 3, x, y))
pieces.append(('ScreenMountGauge_26.0x58.25', g))

EXT = [('CouponC_SelfTapPilots',
        ROOT / 'cad/print-ready/Gladiator_CouponC_SelfTapPilots_flat.stl'),
       ('GH44_Blank_Carrier',
        ROOT / 'cad/head/v01/fit-prototypes/GH44_Blank_Carrier.stl'),
       ('GH44_Receiver_Fit',
        ROOT / 'cad/head/v01/fit-prototypes/GH44_Receiver_Fit_Coupon.stl')]

items = []
for name, sh in pieces:
    assert sh.isValid() and len(sh.Solids) == 1, name
    m = MeshPart.meshFromShape(Shape=sh, LinearDeflection=LIN,
                               AngularDeflection=ANG, Relative=False)
    b = m.BoundBox
    m.translate(-b.XMin, -b.YMin, -b.ZMin)
    items.append([name, m])
for name, f in EXT:
    if not f.exists():
        p('  MISSING %s' % f)
        continue
    m = Mesh.Mesh(str(f))
    b = m.BoundBox
    m.translate(-b.XMin, -b.YMin, -b.ZMin)
    items.append([name, m])

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

p('')
p('PLATE')
vol = 0.0
offbed = 0
for name, m in items:
    b = m.BoundBox
    vol += m.Volume
    ok = (b.XMin >= MARGIN - 0.01 and b.XMax <= BED_X - MARGIN + 0.01 and
          b.YMin >= MARGIN - 0.01 and b.YMax <= BED_Y - MARGIN + 0.01 and
          abs(b.ZMin) < 1e-6)
    if not ok:
        offbed += 1
    p('  %-30s %6.1f x %5.1f x %5.1f  at (%6.1f,%6.1f)  %s'
      % (name, b.XLength, b.YLength, b.ZLength, b.XMin, b.YMin,
         'ok' if ok else '*** OFF BED'))
bad = 0
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        a, b = items[i][1].BoundBox, items[j][1].BoundBox
        if a.XMin < b.XMax and b.XMin < a.XMax and a.YMin < b.YMax and b.YMin < a.YMax:
            p('  *** OVERLAP %s / %s' % (items[i][0], items[j][0]))
            bad += 1
p('  %d pieces  %.2f cm3  %.0f g PLA  offbed=%d  overlaps=%d'
  % (len(items), vol / 1000.0, vol * 0.00124, offbed, bad))

out = ROOT / 'cad/print-ready/Gladiator_PlateE_ALL-COUPONS.3mf'
write_3mf(str(out), 'Gladiator Plate E - all remaining coupons',
          [(n, m) for n, m in items])
p('  wrote %s' % out.name)
open('/tmp/plateE.txt', 'w').write(NL.join(O))
