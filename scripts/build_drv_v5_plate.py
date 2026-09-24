"""Build the print-ready driver-v5 plate and representative interlock coupon.

The bases print on their deck faces.  OrcaSlicer 2.4.2's orientation analysis
selects an end face for the wedges; that keeps the four standoff bores open and
avoids trying to print them blind against the bed.  A brim and automatic normal
supports are still required for the two tall wedge parts.
"""
import json
import os
import shutil
import sys
import zipfile

sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import FreeCAD as App
import MeshPart
import Part


REPO = '/home/buralien/projects/gladiator-cad'
SOURCE = REPO + '/cad/drivers/v5-interlock/DriverMount_v5.FCStd'
OUT = REPO + '/cad/print-ready'
INCOMING = '/home/buralien/Desktop/3D-Printer-Incoming'
BED_X = BED_Y = 220.0
MARGIN = 10.0
GAP = 8.0
LIN = 0.01
ANG = 0.05
V = App.Vector


def oriented_mesh(shape, down):
    """Rotate the model-space direction *down* onto -Z and place it on Z=0."""
    s = shape.copy()
    d = V(down)
    d.normalize()
    s.Placement = App.Placement(V(), App.Rotation(d, V(0, 0, -1))).multiply(s.Placement)
    mesh = MeshPart.meshFromShape(Shape=s, LinearDeflection=LIN,
                                  AngularDeflection=ANG, Relative=False)
    # Place the tessellated result, not just the B-rep, on the bed.  Curved
    # fillets/cones can move the mesh bound by numerical microns.
    bb = mesh.BoundBox
    mesh.translate(-bb.XMin, -bb.YMin, -bb.ZMin)
    return mesh


def write_3mf(path, title, items):
    model = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
        '<metadata name="Title">%s</metadata>' % title,
        '<metadata name="Application">gladiator-cad build_drv_v5_plate.py</metadata>',
        '<resources>',
    ]
    for oid, (name, mesh) in enumerate(items, start=1):
        pts, facets = mesh.Topology
        model.append('<object id="%d" type="model" name="%s"><mesh><vertices>'
                     % (oid, name))
        for p in pts:
            model.append('<vertex x="%.6f" y="%.6f" z="%.6f"/>' % (p.x, p.y, p.z))
        model.append('</vertices><triangles>')
        for f in facets:
            model.append('<triangle v1="%d" v2="%d" v3="%d"/>' % (f[0], f[1], f[2]))
        model.append('</triangles></mesh></object>')
    model.append('</resources><build>')
    for oid in range(1, len(items) + 1):
        model.append('<item objectid="%d" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>' % oid)
    model.append('</build></model>')

    content_types = ('<?xml version="1.0" encoding="UTF-8"?>'
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
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', '\n'.join(model))


def validate_mesh(name, mesh):
    bb = mesh.BoundBox
    if not mesh.isSolid() or mesh.hasSelfIntersections():
        raise RuntimeError('%s is not a clean solid' % name)
    if abs(bb.ZMin) > 1e-6:
        raise RuntimeError('%s is not on the bed' % name)
    return {
        'name': name,
        'x_mm': round(bb.XLength, 2),
        'y_mm': round(bb.YLength, 2),
        'z_mm': round(bb.ZLength, 2),
        'volume_cm3': round(mesh.Volume / 1000.0, 2),
        'solid': True,
        'self_intersections': False,
    }


def arrange_one_row(items):
    total_x = sum(m.BoundBox.XLength for _, m in items) + GAP * (len(items) - 1)
    max_y = max(m.BoundBox.YLength for _, m in items)
    if total_x > BED_X - 2 * MARGIN or max_y > BED_Y - 2 * MARGIN:
        raise RuntimeError('driver plate does not fit the Ender-3 Neo bed')
    x = (BED_X - total_x) / 2.0
    placed = []
    for name, mesh in items:
        y = (BED_Y - mesh.BoundBox.YLength) / 2.0
        mesh.translate(x - mesh.BoundBox.XMin, y - mesh.BoundBox.YMin, 0)
        placed.append((name, mesh))
        x += mesh.BoundBox.XLength + GAP
    return placed, round(total_x, 2), round(max_y, 2)


def build_driver_plate(doc):
    specs = [
        ('Base_L', 'Base_Left', V(0, 0, -1), 'flat deck face down'),
        ('Base_R', 'Base_Right', V(0, 0, -1), 'flat deck face down'),
        # OrcaSlicer 2.4.2 chose an end face over every sloped/board-facing option.
        ('Wedge_L', 'Wedge_Left', V(0, 1, 0), 'rear end face down; brim + supports'),
        ('Wedge_R', 'Wedge_Right', V(0, 1, 0), 'rear end face down; brim + supports'),
    ]
    items = []
    report = []
    for short, obj_name, down, note in specs:
        mesh = oriented_mesh(doc.getObject(obj_name).Shape, down)
        row = validate_mesh(short, mesh)
        row['orientation'] = note
        report.append(row)
        stl_name = 'Gladiator_DriverV5_%s.stl' % short
        mesh.write(os.path.join(OUT, stl_name))
        items.append((short, mesh))

    placed, used_x, used_y = arrange_one_row(items)
    plate_name = 'Gladiator_PlateI_DRIVER-V5-INTERLOCK.3mf'
    plate_path = os.path.join(OUT, plate_name)
    write_3mf(plate_path, 'Gladiator Plate I - v5 interlocked driver mounts', placed)
    shutil.copy2(plate_path, os.path.join(INCOMING, plate_name))
    return plate_name, report, used_x, used_y


def build_base_reprint(doc):
    # v5c: only the bases changed (cup relief); the printed wedges are reused.
    items = []
    report = []
    for short, obj_name in [('Base_L', 'Base_Left'), ('Base_R', 'Base_Right')]:
        mesh = oriented_mesh(doc.getObject(obj_name).Shape, V(0, 0, -1))
        row = validate_mesh(short, mesh)
        row['orientation'] = 'flat deck face down; no supports needed'
        report.append(row)
        items.append((short, mesh))
    placed, used_x, used_y = arrange_one_row(items)
    name = 'Gladiator_PlateJ_DRIVER-V5c-BASES-ONLY_deck-face-down.3mf'
    path = os.path.join(OUT, name)
    write_3mf(path, 'Gladiator Plate J - v5c driver bases with cup relief', placed)
    shutil.copy2(path, os.path.join(INCOMING, name))
    return name, report, used_x, used_y


def build_coupon(doc):
    # These are full-length sections cut from the actual v5 joint by
    # build_drv_v5.py.  Each uses the production part's print orientation so
    # layer direction, accumulated length error, lead-ins and locator all match.
    specs = [
        ('BaseSection', 'Coupon_Base', V(0, 0, -1),
         'full 51.5 mm length; production base orientation'),
        ('WedgeSection', 'Coupon_Wedge', V(0, 1, 0),
         'full 51.5 mm length; production wedge end-face orientation'),
    ]
    # These flat 20 mm samples were superseded by the representative sections.
    for legacy in ['Gladiator_DriverV5_Coupon_Tongue.stl',
                   'Gladiator_DriverV5_Coupon_Groove.stl']:
        path = os.path.join(OUT, legacy)
        if os.path.exists(path):
            os.remove(path)
    items = []
    report = []
    for name, obj_name, down, note in specs:
        mesh = oriented_mesh(doc.getObject(obj_name).Shape, down)
        row = validate_mesh(name, mesh)
        row['orientation'] = note
        report.append(row)
        mesh.write(os.path.join(OUT, 'Gladiator_DriverV5_Coupon_%s.stl' % name))
        items.append((name, mesh))
    placed, used_x, used_y = arrange_one_row(items)
    name = 'Gladiator_DriverV5_INTERLOCK-FIT-COUPON.3mf'
    path = os.path.join(OUT, name)
    write_3mf(path, 'Gladiator driver v5 interlock fit coupon', placed)
    shutil.copy2(path, os.path.join(INCOMING, name))
    return name, report, used_x, used_y


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(INCOMING, exist_ok=True)
    doc = App.openDocument(SOURCE)
    plate_name, parts, plate_x, plate_y = build_driver_plate(doc)
    coupon_name, coupons, coupon_x, coupon_y = build_coupon(doc)
    bases_name, bases, bases_x, bases_y = build_base_reprint(doc)
    report = {
        'driver_plate': plate_name,
        'driver_plate_used_mm': [plate_x, plate_y],
        'parts': parts,
        'base_reprint_plate': bases_name,
        'base_reprint_plate_used_mm': [bases_x, bases_y],
        'base_reprint_parts': bases,
        'coupon_plate': coupon_name,
        'coupon_plate_used_mm': [coupon_x, coupon_y],
        'coupon_parts': coupons,
        'settings': {
            'printer': 'Ender-3 Neo, 0.4 mm nozzle',
            'material': 'PLA',
            'layer_height_mm': 0.20,
            'walls': 4,
            'infill': '30%',
            'brim_mm': 5,
            'supports': 'normal(auto), build plate only; driver plate only',
            'auto_orient': False,
        },
    }
    report_path = os.path.join(REPO, 'cad/drivers/v5-interlock/print-validation.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    print(json.dumps(report, indent=2))


main()
