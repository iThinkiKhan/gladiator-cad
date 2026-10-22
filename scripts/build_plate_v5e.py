"""Plate L: both v5e driver bases (original v5c + countersink), deck face down, with SUPPORT ENFORCERS inside the
boss pockets (the D9.8 pockets over the deck heat-set inserts open toward the bed, so their ceilings are bridges that
sag). Everything else keeps Jim's baseline D profile (4 walls, 30 % crosshatch, 0.20 mm). No brim.
Run: freecadcmd scripts/build_plate_v5e.py
"""
import sys, json, zipfile, shutil
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad-python3/lib'])
import FreeCAD as A, Part, MeshPart
from pathlib import Path

V = A.Vector
HOME = Path.home()
REPO = HOME / 'projects/gladiator-cad'
SRC = REPO / 'cad/drivers/v5-interlock/DriverMount_v5.FCStd'
TPL = REPO / 'cad/v2/print-plates/Gladiator_v2_ORCA-D_Upper_Deck_v4.3mf'
OUTS = [REPO / 'cad/print-ready', HOME / '3D-Printer/Incoming/Gladiator']
NAME = 'Gladiator_PlateL_DRIVER-V5e-BASES-ONLY_countersunk-M3_pocket-supports_deck-face-down.3mf'
POCKET_R, POCKET_Z0, POCKET_Z1 = 4.9, 52.0, 58.0      # the D9.8 boss pocket in the base, deck face = Z52
ENF_R, ENF_ABOVE = 4.7, 0.3
CENTERS = {'Base_Left': [(14.5, 95.0), (14.5, 135.0)], 'Base_Right': [(64.5, 95.0), (64.5, 135.0)]}
PLACE = {'Base_Left': (92.0, 110.0), 'Base_Right': (128.0, 110.0)}

doc = A.openDocument(str(SRC))


def mesh_of(shape):
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.01, AngularDeflection=0.0872665, Relative=False)
    pts = [(p.x, p.y, p.z) for p in m.Points]
    tri = [tuple(f.PointIndices) for f in m.Facets]
    return pts, tri


def model_objects(objs):
    out = ['<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
           'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
           'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
           ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>']
    for oid, (pts, tri) in objs:
        out.append('  <object id="%d" type="model">\n   <mesh>\n    <vertices>' % oid)
        out += ['     <vertex x="%.5f" y="%.5f" z="%.5f"/>' % p for p in pts]
        out.append('    </vertices>\n    <triangles>')
        out += ['     <triangle v1="%d" v2="%d" v3="%d"/>' % t for t in tri]
        out.append('    </triangles>\n   </mesh>\n  </object>')
    out.append(' </resources>\n <build/>\n</model>\n')
    return '\n'.join(out)


files, comps, items, ms_objs, summary = {}, [], [], [], {}
nid = 1
for k, nm in enumerate(['Base_Left', 'Base_Right']):
    sh = doc.getObject(nm).Shape.copy()
    bb = sh.BoundBox
    ox, oy, oz = (bb.XMin + bb.XMax) / 2, (bb.YMin + bb.YMax) / 2, bb.ZMin
    assert abs(oz - POCKET_Z0) < 1e-6, (nm, oz)
    sh.translate(V(-ox, -oy, -oz))
    parts = [('normal_part', nm, mesh_of(sh))]
    for j, (x, y) in enumerate(CENTERS[nm]):
        cyl = Part.makeCylinder(ENF_R, (POCKET_Z1 - POCKET_Z0) + ENF_ABOVE, V(x - ox, y - oy, 0.0))
        parts.append(('support_enforcer', 'Pocket support %d' % (j + 1), mesh_of(cyl)))
    objs = [(nid + i, p[2]) for i, p in enumerate(parts)]
    mesh_file = '3D/Objects/%s.model' % nm
    files[mesh_file] = model_objects(objs)
    obj_id = nid + len(parts)
    comps.append('  <object id="%d" type="model">\n   <components>\n%s\n   </components>\n  </object>' % (
        obj_id, '\n'.join('    <component p:path="/%s" objectid="%d" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>' % (mesh_file, o) for o, _ in objs)))
    cx, cy = PLACE[nm]
    items.append('  <item objectid="%d" transform="1 0 0 0 1 0 0 0 1 %.4f %.4f 0" printable="1"/>' % (obj_id, cx, cy))
    ms = ['  <object id="%d">\n    <metadata key="name" value="%s"/>\n    <metadata key="extruder" value="1"/>\n'
          '    <metadata key="brim_type" value="no_brim"/>' % (obj_id, nm)]
    for (sub, pname, (pts, tri)), (o, _) in zip(parts, objs):
        ms.append('    <part id="%d" subtype="%s">\n      <metadata key="name" value="%s"/>\n      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
                  '      <mesh_stat face_count="%d" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n    </part>' % (o, sub, pname, len(tri)))
    ms.append('  </object>')
    ms_objs.append('\n'.join(ms))
    summary[nm] = dict(size_mm=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)], enforcers=len(CENTERS[nm]))
    nid = obj_id + 1

model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
         'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
         ' <metadata name="Application">BambuStudio-02.06.00.51</metadata>\n <metadata name="OrcaSlicer">2.4.2</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
         ' <metadata name="Title">%s</metadata>\n <resources>\n%s\n </resources>\n <build>\n%s\n </build>\n</model>\n' % (NAME[:-4], '\n'.join(comps), '\n'.join(items)))
insts = ''.join('    <model_instance>\n      <metadata key="object_id" value="%s"/>\n      <metadata key="instance_id" value="0"/>\n      <metadata key="identify_id" value="%d"/>\n    </model_instance>\n'
                % (it.split('objectid="')[1].split('"')[0], 100 + i) for i, it in enumerate(items))
mset = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n%s\n  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value="L"/>\n'
        '    <metadata key="locked" value="false"/>\n    <metadata key="filament_map_mode" value="Auto For Flush"/>\n    <metadata key="gcode_file" value=""/>\n%s  </plate>\n  <assemble>\n  </assemble>\n</config>\n'
        % ('\n'.join(ms_objs), insts))

zin = zipfile.ZipFile(TPL)
out0 = OUTS[0] / NAME
with zipfile.ZipFile(out0, 'w', zipfile.ZIP_DEFLATED) as z:
    for it in zin.infolist():
        fn = it.filename
        if fn.startswith('3D/Objects/') or fn.endswith('_rels/3dmodel.model.rels'):
            continue
        data = zin.read(fn)
        if fn == '3D/3dmodel.model':
            data = model.encode()
        elif fn == 'Metadata/model_settings.config':
            data = mset.encode()
        elif fn == 'Metadata/project_settings.config':
            d = json.loads(data)
            d.update({'enable_support': '1', 'support_type': 'normal(manual)', 'support_on_build_plate_only': '1',
                      'brim_type': 'no_brim'})
            data = json.dumps(d, indent=4).encode()
        z.writestr(fn, data)
    for fn, x in files.items():
        z.writestr(fn, x)
    rels = ['<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for i, nm in enumerate(['Base_Left', 'Base_Right']):
        rels.append(' <Relationship Target="/3D/Objects/%s.model" Id="rel-%d" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' % (nm, i + 1))
    rels.append('</Relationships>')
    z.writestr('3D/_rels/3dmodel.model.rels', '\n'.join(rels))
for d_ in OUTS[1:]:
    shutil.copy2(out0, d_ / NAME)
print(json.dumps(dict(plate=NAME, parts=summary), indent=1))
