"""v2 OrcaSlicer plates with the 2026-10-19 time/material savings (Jim's choice).

  D2  deck v4:  3 walls, 3 top / 3 bottom layers, 15 % gyroid, 0.20 mm layers (precision holes/pegs unchanged), 4 mm outer brim as before
  H   rear hood:            0.28 mm layers, tree supports (auto), rest of the profile unchanged
  P   front left + right:   same as H, both panels on one bed
The driver bases stay on the baseline profile (plate K, scripts/build_drv_v5d_headrelief.py).

Template = the D plate 3MF (Jim's EnderNeo PLA profile); only the meshes, placement and the process keys below change.
"""
import json, re, struct, zipfile, shutil
from pathlib import Path
import numpy as np

HOME = Path.home()
REPO = HOME / 'projects/gladiator-cad/cad/v2'
TPL = REPO / 'print-plates/Gladiator_v2_ORCA-D_Upper_Deck_v4.3mf'
OUT = REPO / 'print-plates'
INCOMING = HOME / '3D-Printer/Incoming/Gladiator'
ENC = REPO / 'enclosure/v2-20261013/Gladiator_Enclosure_v2_'

DECK_KEYS = {'wall_loops': '3', 'top_shell_layers': '3', 'bottom_shell_layers': '3',
             'sparse_infill_density': '15%', 'sparse_infill_pattern': 'gyroid'}
SHELL_KEYS = {'layer_height': '0.28', 'enable_support': '1', 'support_type': 'tree(auto)'}

PLATES = [
    ('Gladiator_v2_ORCA-D2_Upper_Deck_v4_light.3mf', 'D2', DECK_KEYS,
     [('Upper_Deck_v4', REPO / 'upper-deck/v4-20261016/Gladiator_UpperDeck_v4.stl', (110, 110), 'outer_only', 4)]),
    ('Gladiator_v2_ORCA-H_Rear_Hood_0.28_tree.3mf', 'H', SHELL_KEYS,
     [('Rear_Hood', Path(str(ENC) + 'Rear_Hood.stl'), (110, 110), 'no_brim', 0)]),
    ('Gladiator_v2_ORCA-P_Front_Panels_0.28_tree.3mf', 'P', SHELL_KEYS,
     [('Front_Left', Path(str(ENC) + 'Front_Left.stl'), (65, 110), 'no_brim', 0),
      ('Front_Right', Path(str(ENC) + 'Front_Right.stl'), (155, 110), 'no_brim', 0)]),
]


def read_stl(p):
    b = p.read_bytes()
    if b[:5] == b'solid' and b'facet' in b[:300]:
        return np.array(re.findall(r'vertex\s+(\S+)\s+(\S+)\s+(\S+)', b.decode(errors='ignore')), dtype=float).reshape(-1, 3, 3)
    n = struct.unpack('<I', b[80:84])[0]
    a = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]))
    return a['v'].reshape(-1, 3, 3).astype(float)


def mesh_xml(tris, oid):
    pts = tris.reshape(-1, 3)
    u, inv = np.unique(np.round(pts, 5), axis=0, return_inverse=True)
    inv = inv.reshape(-1, 3)
    lo, hi = u.min(axis=0), u.max(axis=0)
    u = u - np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    head = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
            'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
            'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
            ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n  <object id="%d" type="model">\n   <mesh>\n    <vertices>\n' % oid)
    body = '\n'.join('     <vertex x="%.5f" y="%.5f" z="%.5f"/>' % tuple(r) for r in u)
    tri = '\n'.join('     <triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t) for t in inv)
    return head + body + '\n    </vertices>\n    <triangles>\n' + tri + '\n    </triangles>\n   </mesh>\n  </object>\n </resources>\n <build/>\n</model>\n', len(inv), (hi - lo)


def build(fname, plate, keys, parts):
    zin = zipfile.ZipFile(TPL)
    objs, comps, items, ms_objs, ms_inst, sizes = [], [], [], [], [], {}
    files = {}
    for i, (name, stl, (cx, cy), brim, bw) in enumerate(parts):
        mesh_id, obj_id = 2 * i + 1, 2 * i + 2
        xml, nf, size = mesh_xml(read_stl(stl), mesh_id)
        files['3D/Objects/%s.model' % name] = xml
        sizes[name] = [round(float(s), 1) for s in size]
        objs.append('  <object id="%d" type="model">\n   <components>\n    <component p:path="/3D/Objects/%s.model" objectid="%d" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n   </components>\n  </object>' % (obj_id, name, mesh_id))
        items.append('  <item objectid="%d" transform="1 0 0 0 1 0 0 0 1 %.4f %.4f 0" printable="1"/>' % (obj_id, cx, cy))
        ms_objs.append('  <object id="%d">\n    <metadata key="name" value="%s"/>\n    <metadata key="extruder" value="1"/>\n'
                       '    <metadata key="brim_type" value="%s"/>\n    <metadata key="brim_width" value="%d"/>\n'
                       '    <part id="1" subtype="normal_part">\n      <metadata key="name" value="%s"/>\n'
                       '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
                       '      <mesh_stat face_count="%d" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n'
                       '    </part>\n  </object>' % (obj_id, name, brim, bw, name, nf))
        ms_inst.append('    <model_instance>\n      <metadata key="object_id" value="%d"/>\n      <metadata key="instance_id" value="0"/>\n      <metadata key="identify_id" value="%d"/>\n    </model_instance>' % (obj_id, 100 + i))
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
             'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
             ' <metadata name="Application">BambuStudio-02.06.00.51</metadata>\n <metadata name="OrcaSlicer">2.4.2</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
             ' <metadata name="Title">%s</metadata>\n <resources>\n%s\n </resources>\n <build>\n%s\n </build>\n</model>\n' % (fname[:-4], '\n'.join(objs), '\n'.join(items)))
    mset = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n%s\n  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value="%s"/>\n'
            '    <metadata key="locked" value="false"/>\n    <metadata key="filament_map_mode" value="Auto For Flush"/>\n    <metadata key="gcode_file" value=""/>\n%s\n  </plate>\n  <assemble>\n  </assemble>\n</config>\n'
            % ('\n'.join(ms_objs), plate, '\n'.join(ms_inst)))
    out = OUT / fname
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
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
                d.update(keys)
                data = json.dumps(d, indent=4).encode()
            z.writestr(fn, data)
        for fn, x in files.items():
            z.writestr(fn, x)
        rels = ['<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
        for i, (name, *_r) in enumerate(parts):
            rels.append(' <Relationship Target="/3D/Objects/%s.model" Id="rel-%d" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' % (name, i + 1))
        rels.append('</Relationships>')
        z.writestr('3D/_rels/3dmodel.model.rels', '\n'.join(rels))
    shutil.copy2(out, INCOMING / fname)
    return out, sizes


summary = {}
for fname, plate, keys, parts in PLATES:
    out, sizes = build(fname, plate, keys, parts)
    summary[fname] = dict(plate=plate, process_overrides=keys, sizes_mm=sizes)
    print(fname, sizes)
(OUT / 'savings-plates-20261019.json').write_text(json.dumps(summary, indent=1) + '\n')
