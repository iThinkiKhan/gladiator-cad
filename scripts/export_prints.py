"""Export Gladiator parts as print-ready STLs, grouped into build plates.

Two rules this script exists to enforce:

1. **Fine tessellation.** MeshPart.meshFromShape at 0.01 mm linear deflection.
   A mesh approximates a circle from the inside, so every round feature comes out
   undersize by about twice the deflection. FreeCAD's default 0.1 would be 0.2 mm
   on every hole -- exactly one step of the coupon's bore increments.

2. **Orientation is derived, never hand-labelled.** An earlier version of this file
   picked the rotation by testing `ZLength == 12` and taking the first match. Both
   +90 and -90 about Y satisfy that, so it silently laid the side rail on its
   *inboard* face -- 1448 mm2 of support instead of 317 -- while naming the file
   'print-on-outboard-face'. Here each part instead names the direction in ITS OWN
   coordinates that must end up pointing at the bed, the rotation is computed from
   that, and the result is checked against the expected bed-contact area. A part
   laid on the wrong face fails that check instead of shipping a plausible file.
"""
import math
import os
import FreeCAD as App
import MeshPart

REPO = '/home/buralien/projects/gladiator-cad'
OUT = '/home/buralien/Desktop/3D-Printer-Incoming'
MASTER = REPO + '/cad/master/Gladiator_Master.FCStd'
COUPON_A = REPO + '/cad/coupons/Gladiator_Coupon_A_InsertBores.FCStd'
MIRROR = REPO + '/cad/print-ready'

LIN, ANG = 0.01, 0.05
BED_X, BED_Y, BED_Z = 220.0, 220.0, 250.0
OVERHANG = 45.0

DOWN = App.Vector(0, 0, -1)

# plate, object, down-direction in the part's own coords, expected bed area, filename, note
PARTS = [
    (2, 'MastBase', App.Vector(0, 0, 1), 204.1,
     'Gladiator_P2_MastBase_print-spigot-UP.stl',
     'Upside down: spigot points UP, so the deck-mating face prints upward and clean. '
     'Only a thin ring touches the bed - USE A BRIM.'),
    (2, 'AntennaPost', App.Vector(0, -1, 0), 638.8,
     'Gladiator_P2_AntennaPost_print-on-front-face.stl',
     'Lies on its front face (the flat the SMA nut tightens against). Nearly support-free, '
     'and the SMA bore prints vertical so it stays round.'),
    (2, 'PowerShield', App.Vector(0, -1, 0), 252.0,
     'Gladiator_P2_PowerShield_print-on-side.stl',
     'On its side: 73 tall on a 47x24 footprint - USE A BRIM. Flat-down needs 9x the support.'),
    (3, 'SideRailLeft', App.Vector(-1, 0, 0), 3350.2,
     'Gladiator_P3_SideRail_L_print-on-outboard-face.stl',
     'OUTBOARD face down, so the wire raceway opens UPWARD. Inboard-face-down looks identical '
     'in the bounding box but needs 4.5x the support - that is the bug this script now catches.'),
    (3, 'SideRailRight', App.Vector(1, 0, 0), 3350.2,
     'Gladiator_P3_SideRail_R_print-on-outboard-face.stl',
     'Mirror of the left, so its outboard face is +X. Raceway again opens upward.'),
    (4, 'UpperDeck', App.Vector(0, 0, -1), 11182.0,
     'Gladiator_P4_UpperDeck_print-flat-bosses-up.stl',
     'Flat as modelled, bosses and mast collar up. Zero support. The bed face is the '
     'rail-mating face, which is the flattest surface a printer makes.'),
    (5, 'MastTube', App.Vector(0, 0, -1), 200.9,
     'Gladiator_P5_MastTube_print-vertical.stl',
     'Vertical - the only sane orientation for a 20/12 tube. Read the note about buying '
     'an aluminium or carbon tube instead before printing this.'),
    (6, 'DriverMountLeft', App.Vector(0, 0, 1), 528.0,
     'Gladiator_P6_DriverMount_L_print-inverted.stl',
     'Inverted. GATED: check the 2.7 self-tap holes against a real BTS7960 before printing.'),
    (6, 'DriverMountRight', App.Vector(0, 0, 1), 528.0,
     'Gladiator_P6_DriverMount_R_print-inverted.stl',
     'Inverted, mirror of the left. Same gate.'),
]


def orient(shape, down):
    """Rotate so `down` (in the part's own coords) points at the bed, then drop to Z=0."""
    d = App.Vector(down)
    d.normalize()
    s = shape.copy()
    rot = App.Rotation(d, DOWN)          # the rotation carrying d onto -Z
    s.Placement = App.Placement(App.Vector(0, 0, 0), rot).multiply(s.Placement)
    bb = s.BoundBox
    s.translate(App.Vector(-bb.XMin, -bb.YMin, -bb.ZMin))
    return s


def mesh_stats(m):
    """Support area, bed-contact area and signed volume, straight off the facets."""
    zmin = m.BoundBox.ZMin
    thr = math.sin(math.radians(OVERHANG)) + 1e-3
    support = 0.0
    bed = 0.0
    vol = 0.0
    for f in m.Facets:
        p = f.Points
        a = App.Vector(*p[0])
        b = App.Vector(*p[1])
        c = App.Vector(*p[2])
        vol += a.dot(b.cross(c)) / 6.0
        n = (b - a).cross(c - a)
        ar = n.Length / 2.0
        if ar <= 1e-12:
            continue
        n.normalize()
        cz = (a.z + b.z + c.z) / 3.0
        if -n.z > thr:
            if abs(cz - zmin) < 0.05 and n.z < -0.999:
                bed += ar
            else:
                support += ar
    return support, bed, vol


def export(shape, name, expect_bed, note, cad_volume):
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=LIN,
                               AngularDeflection=ANG, Relative=False)
    m.write(os.path.join(OUT, name))
    m.write(os.path.join(MIRROR, name))

    bb = m.BoundBox
    support, bed, vol = mesh_stats(m)
    manifold = (not m.hasNonManifolds()) and m.CountEdges == m.CountFacets * 3 // 2
    volerr = abs(vol - cad_volume) / cad_volume * 100.0

    checks = [
        ('single closed solid', m.isSolid()),
        ('manifold, no free edges', manifold),
        ('no self-intersections', not m.hasSelfIntersections()),
        ('sits on Z=0', abs(bb.ZMin) < 1e-6),
        ('fits the bed', bb.XLength <= BED_X and bb.YLength <= BED_Y and bb.ZLength <= BED_Z),
        ('volume matches CAD to 0.5%%', volerr < 0.5),
    ]
    if expect_bed is not None:
        checks.append(('ORIENTATION: the intended face is the one on the bed',
                       abs(bed - expect_bed) < max(5.0, expect_bed * 0.02)))
    ok = all(v for _, v in checks)

    print('  %s' % name)
    print('     %.1f x %.1f x %.1f mm   %d facets   %.2f cm3 of solid'
          % (bb.XLength, bb.YLength, bb.ZLength, m.CountFacets, vol / 1000.0))
    if expect_bed is None:
        print('     support needed %.0f mm2   touching the bed %.0f mm2' % (support, bed))
    else:
        print('     support needed %.0f mm2   touching the bed %.0f mm2 (expected %.0f)'
              % (support, bed, expect_bed))
    for label, v in checks:
        if not v:
            print('     *** FAILED: %s' % label)
    print('     %s' % ('all checks pass' if ok else '!!! DO NOT SLICE THIS FILE !!!'))
    print('     %s' % note)
    print()
    return ok, bb, support, vol


def main():
    if not os.path.isdir(MIRROR):
        os.makedirs(MIRROR)
    allok = True
    summary = []

    print('=== plate 1 - the gate ===')
    cdoc = App.openDocument(COUPON_A)
    cobj = None
    for o in cdoc.Objects:
        if hasattr(o, 'Shape') and not o.Shape.isNull() and o.Shape.Solids:
            cobj = o
    if cobj is None:
        print('  *** coupon A has no solid')
        allok = False
    else:
        cs = orient(cobj.Shape, App.Vector(0, 0, -1))
        ok, bb, sup, vol = export(
            cs, 'Gladiator_P1_CouponA_InsertBores_flat.stl', None,
            'Flat, no support. MEASURE THIS before slicing plate 3 or plate 4 - '
            'every insert bore on the rails and the deck depends on it.', cs.Volume)
        allok = allok and ok
        summary.append((1, 'Coupon A', bb, sup, vol))

    doc = App.openDocument(MASTER)
    plate = None
    for pl, name, down, expect, fname, note in PARTS:
        if pl != plate:
            plate = pl
            print('=== plate %d ===' % pl)
        o = doc.getObject(name)
        if o is None:
            print('  *** %s NOT FOUND IN THE MASTER' % name)
            allok = False
            continue
        s = orient(o.Shape, down)
        ok, bb, sup, vol = export(s, fname, expect, note, o.Shape.Volume)
        allok = allok and ok
        summary.append((pl, name, bb, sup, vol))

    print('=== plate footprints (bed is %.0f x %.0f) ===' % (BED_X, BED_Y))
    plates = {}
    for pl, name, bb, sup, vol in summary:
        plates.setdefault(pl, []).append((name, bb, sup, vol))
    for pl in sorted(plates):
        items = plates[pl]
        wide = sum(b.XLength for _, b, _, _ in items) + 10.0 * (len(items) - 1)
        deep = max(b.YLength for _, b, _, _ in items)
        tall = max(b.ZLength for _, b, _, _ in items)
        svol = sum(v for _, _, _, v in items)
        ssup = sum(s for _, _, s, _ in items)
        fit = 'fits' if (wide <= BED_X - 10 and deep <= BED_Y - 10) else 'CHECK PACKING'
        print('  plate %d  %-46s %6.1f x %-6.1f tallest %5.1f  %6.2f cm3  support %5.0f mm2  %s'
              % (pl, ', '.join(n for n, _, _, _ in items), wide, deep, tall,
                 svol / 1000.0, ssup, fit))

    print()
    print('=== result ===')
    print('ALL FILES PASSED' if allok else 'SOMETHING FAILED - read the log above')


main()
