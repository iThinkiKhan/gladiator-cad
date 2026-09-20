"""Build real, arranged build plates as 3MF files - one file per plate, parts already
laid out on the bed, ready to open and slice.

The earlier output was nine loose STLs plus a document explaining which ones belonged
together. That is a reading order, not a plate. This produces the actual thing.

Each part is oriented by the same derived down-direction used by export_prints.py (the
direction in the part's own coordinates that must face the bed), meshed at 0.01 mm
deflection, then TRANSLATED INTO POSITION so the 3MF carries identity transforms only -
no transform-convention ambiguity for the slicer to get wrong.

Layout is checked, not assumed: every pair of footprints is tested for overlap and every
part is tested against the bed envelope before a file is written.
"""
import os
import sys
import zipfile

import FreeCAD as App
import MeshPart

_p = print


def print(*a, **k):
    _p(*a, **k)
    sys.stdout.flush()


REPO = '/home/buralien/projects/gladiator-cad'
MASTER = REPO + '/cad/master/Gladiator_Master.FCStd'
OUT = '/home/buralien/Desktop/3D-Printer-Incoming'
MIRROR = REPO + '/cad/print-ready'

LIN, ANG = 0.01, 0.05
BED_X, BED_Y, BED_Z = 220.0, 220.0, 250.0
MARGIN = 10.0          # keep off the very edge of the bed
GAP = 8.0              # between parts, enough for brims to not merge

V = App.Vector

# plate file name, human title, [(object, down-direction, label)]
PLATES = [
    ('Gladiator_PlateA_BODY_rails-and-upper-deck.3mf',
     'Plate A - the body: both side rails and the upper deck',
     [('UpperDeck', V(0, 0, -1), 'upper deck, flat, bosses up, no support'),
      ('SideRailLeft', V(-1, 0, 0), 'left rail, outboard face down'),
      ('SideRailRight', V(1, 0, 0), 'right rail, outboard face down')]),

    ('Gladiator_PlateB_MAST-AND-FITTINGS.3mf',
     'Plate B - mast base, antenna post, power shield',
     [('MastBase', V(0, 0, 1), 'mast base, spigot UP, needs a brim'),
      ('AntennaPost', V(0, -1, 0), 'antenna post, on its front face'),
      ('PowerShield', V(0, -1, 0), 'power shield, on its side, needs a brim')]),

    ('Gladiator_PlateC_MAST-TUBE.3mf',
     'Plate C - mast tube, on its own (see the buy-a-tube note)',
     [('MastTube', V(0, 0, -1), 'mast tube, vertical, needs a brim')]),

    ('Gladiator_PlateD_DRIVER-MOUNTS.3mf',
     'Plate D - driver mounts. Board interface measured and closed 2026-09-20',
     [('DriverMountLeft', V(0, 0, 1),
       'driver mount L, inverted. Arms relieved 2.0 for the header tails; '
       '3.6 clearance holes - needs M3 x 18-20 with nuts and washers behind the frame'),
      ('DriverMountRight', V(0, 0, 1), 'driver mount R, inverted, same hardware')]),
]


def oriented_mesh(doc, name, down):
    s = doc.getObject(name).Shape.copy()
    d = App.Vector(down)
    d.normalize()
    s.Placement = App.Placement(V(0, 0, 0), App.Rotation(d, V(0, 0, -1))).multiply(s.Placement)
    bb = s.BoundBox
    s.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=LIN,
                               AngularDeflection=ANG, Relative=False)
    return m


def write_3mf(path, title, items):
    """items = [(name, mesh already translated into bed position)]"""
    model = []
    model.append('<?xml version="1.0" encoding="UTF-8"?>')
    model.append('<model unit="millimeter" xml:lang="en-US" '
                 'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">')
    model.append('<metadata name="Title">%s</metadata>' % title)
    model.append('<metadata name="Application">gladiator-cad build_plates.py</metadata>')
    model.append('<resources>')
    for oid, (name, m) in enumerate(items, start=1):
        pts, facets = m.Topology
        model.append('<object id="%d" type="model" name="%s"><mesh><vertices>' % (oid, name))
        for p in pts:
            model.append('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % (p.x, p.y, p.z))
        model.append('</vertices><triangles>')
        for f in facets:
            model.append('<triangle v1="%d" v2="%d" v3="%d"/>' % (f[0], f[1], f[2]))
        model.append('</triangles></mesh></object>')
    model.append('</resources>')
    model.append('<build>')
    for oid in range(1, len(items) + 1):
        # geometry is already at its bed position, so the transform is identity
        model.append('<item objectid="%d" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>' % oid)
    model.append('</build>')
    model.append('</model>')

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
        z.writestr('3D/3dmodel.model', '\n'.join(model))


def main():
    doc = App.openDocument(MASTER)
    allok = True

    for fname, title, parts in PLATES:
        print('=' * 78)
        print(title)

        # mesh everything first so we know the real footprints
        meshed = []
        for name, down, note in parts:
            m = oriented_mesh(doc, name, down)
            bb = m.BoundBox
            meshed.append([name, m, bb.XLength, bb.YLength, bb.ZLength, note])

        # lay out left to right, widest first, centred as a group on the bed
        meshed.sort(key=lambda r: -r[2])
        total_w = sum(r[2] for r in meshed) + GAP * (len(meshed) - 1)
        max_d = max(r[3] for r in meshed)
        x = BED_X / 2.0 - total_w / 2.0
        placed = []
        for row in meshed:
            name, m, w, d, h, note = row
            y = BED_Y / 2.0 - d / 2.0
            m.translate(x, y, 0.0)          # mesh currently sits at origin
            placed.append((name, m, x, y, w, d, h, note))
            x += w + GAP

        # ---- checks ----
        ok = True
        if total_w > BED_X - 2 * MARGIN or max_d > BED_Y - 2 * MARGIN:
            print('   *** DOES NOT FIT: %.1f x %.1f against a %.0f x %.0f bed'
                  % (total_w, max_d, BED_X, BED_Y))
            ok = False
        for i in range(len(placed)):
            ni, mi, xi, yi, wi, di, hi, _ = placed[i]
            bb = mi.BoundBox
            if bb.XMin < MARGIN - 0.01 or bb.XMax > BED_X - MARGIN + 0.01 \
               or bb.YMin < MARGIN - 0.01 or bb.YMax > BED_Y - MARGIN + 0.01:
                print('   *** %s lands outside the usable bed' % ni)
                ok = False
            if bb.ZMax > BED_Z or abs(bb.ZMin) > 1e-6:
                print('   *** %s is not sitting on the bed' % ni)
                ok = False
            if not mi.isSolid() or mi.hasSelfIntersections():
                print('   *** %s mesh is not a clean solid' % ni)
                ok = False
            for j in range(i + 1, len(placed)):
                nj, mj = placed[j][0], placed[j][1]
                bj = mj.BoundBox
                overlap = not (bb.XMax <= bj.XMin or bj.XMax <= bb.XMin or
                               bb.YMax <= bj.YMin or bj.YMax <= bb.YMin)
                if overlap:
                    print('   *** %s and %s overlap on the bed' % (ni, nj))
                    ok = False

        for name, m, px, py, w, d, h, note in placed:
            bb = m.BoundBox
            print('   %-18s %6.1f x %-6.1f h %5.1f   at X %5.1f-%5.1f  Y %5.1f-%5.1f'
                  % (name, w, d, h, bb.XMin, bb.XMax, bb.YMin, bb.YMax))
            print('        %s' % note)

        gapmsg = 'group %.1f x %.1f on a %.0f x %.0f bed, %.0f mm between parts' \
                 % (total_w, max_d, BED_X, BED_Y, GAP)
        print('   %s' % gapmsg)

        if not ok:
            print('   NOT WRITTEN')
            allok = False
            continue

        write_3mf(os.path.join(OUT, fname), title, [(n, m) for n, m, _, _, _, _, _, _ in placed])
        write_3mf(os.path.join(MIRROR, fname), title, [(n, m) for n, m, _, _, _, _, _, _ in placed])
        kb = os.path.getsize(os.path.join(OUT, fname)) / 1024.0
        print('   wrote %s  (%.0f kB)' % (fname, kb))
        print()

    print('=' * 78)
    print('ALL PLATES WRITTEN' if allok else 'SOMETHING FAILED - read above')


main()
