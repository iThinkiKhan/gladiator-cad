"""Gladiator head: combined, support-painted OrcaSlicer project plates (EnderNeo, Generic PLA).

Reads the released geometry-only plates (v04 Plates 1-4, v05 Plate 5), keeps every part in its
released print orientation, packs them onto three beds and writes OrcaSlicer project 3MFs that
carry Jim's EnderNeo / Generic PLA / 0.20 Standard settings plus painted supports:

  * Pan_Raised_Pedestal   manual support: enforcer under the top-plate underside only,
                          kept 1.2 mm clear of the 40T belt-groove flange.
  * Rear_Display_Frame    manual support: enforcers under the four corner tabs only.
  * Neck_Main             auto support, with blockers in the two bores (mast bore ceiling
                          and the stepped ledge) so no support ever fills a bore; 8 mm brim.
  * everything else       no support (bridged roofs, nut-slot roofs, 45 degree flanges).

Run on the CAD server:  freecadcmd scripts/build_head_orca_plates.py
Sources are read only. Outputs: cad/head/orca-plates/.
"""
import sys, re, json, zipfile, uuid, math, hashlib
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod', '/usr/lib/freecad-python3/lib'])
import numpy as np
import FreeCAD as A
import Part

ROOT = Path('/home/buralien/projects/gladiator-cad')
HEAD = ROOT / 'cad/head'
OUT = HEAD / 'orca-plates'
TPL = OUT / 'template'
USER = Path.home() / '.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer/user/default'
SYSTEM = Path.home() / '.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer/system'
OUT.mkdir(exist_ok=True)

SRC = {
    1: HEAD / 'v04-pan-stack/plates/Gladiator_Head_v04_PLATE1_Pedestal-Retainer-Cap.3mf',
    2: HEAD / 'v04-pan-stack/plates/Gladiator_Head_v04_PLATE2_PanDrive_Rotor-Pulley-Carriage.3mf',
    3: HEAD / 'v04-pan-stack/plates/Gladiator_Head_v04_PLATE3_Tilt_Yoke-Receiver-DisplayFrame.3mf',
    4: HEAD / 'v04-pan-stack/plates/Gladiator_Head_v04_PLATE4_Neck_Main.3mf',
    5: HEAD / 'v05-sensor-mounts/plates/Gladiator_Head_v05_PLATE5_SensorCarrier-ToF-Radar.3mf',
}
BED = 220.0
GAP = 12.0

# rows of part names per combined plate (left to right, bottom to top)
PLATES = [
    dict(key='A', name='Gladiator_Head_ORCA-A_PanStack_Pedestal-Retainer-Cap_Rotor-Pulley-Carriage',
         rows=[['Pan_Raised_Pedestal', 'Pan_Rotor', 'Pan_Drive_Pulley'],
               ['Pan_Retainer', 'Pan_Servo_Carriage', 'Neck_Clamp_Cap']]),
    dict(key='B', name='Gladiator_Head_ORCA-B_TiltAndSensors_Yoke-Receiver-DisplayFrame-Carrier-ToF-Radar',
         rows=[['Rear_Display_Frame', 'GH44_Dual_Carrier'],
               ['GH44_Tilt_Receiver', 'Tilt_Yoke', 'ToF_Sensor_Frame'],
               ['Radar_Sensor_Frame']]),
    dict(key='C', name='Gladiator_Head_ORCA-C_Neck_Main_brim-and-supports',
         rows=[['Neck_Main']]),
]

# --------------------------------------------------------------------------- mesh helpers
def load_3mf(path):
    x = zipfile.ZipFile(path).read('3D/3dmodel.model').decode()
    out = {}
    for m in re.finditer(r'<object id="(\d+)"[^>]*name="([^"]*)"[^>]*>(.*?)</object>', x, re.S):
        _, name, body = m.groups()
        v = np.array(re.findall(r'<vertex x="([-\d.eE+]+)" y="([-\d.eE+]+)" z="([-\d.eE+]+)"', body), float)
        t = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', body), int)
        out[name] = (v, t)
    return out

PARTS = {}
for k, p in SRC.items():
    for name, vt in load_3mf(p).items():
        PARTS[name] = vt

def overhang_clusters(v, t, minarea=10.0):
    """Connected groups of faces overhanging more than 45 degrees, not on the bed."""
    p = v[t]
    cr = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    a = 0.5 * np.linalg.norm(cr, axis=1)
    n = cr / np.maximum(np.linalg.norm(cr, axis=1, keepdims=True), 1e-12)
    z = p[:, :, 2]
    zmin = z.min()
    zc = z.mean(axis=1)
    bed = (z.max(axis=1) < zmin + 0.05) & (n[:, 2] < -0.9)
    ov = np.where((n[:, 2] < -0.7071) & ~bed & (zc > zmin + 0.05))[0]
    par = {i: i for i in ov}

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    seen = {}
    for i in ov:
        for k in t[i]:
            key = tuple(np.round(v[k], 3))
            if key in seen:
                ra, rb = find(i), find(seen[key])
                if ra != rb:
                    par[ra] = rb
            else:
                seen[key] = i
    groups = {}
    for i in ov:
        groups.setdefault(find(i), []).append(i)
    res = []
    for g in groups.values():
        g = np.array(g)
        if a[g].sum() < minarea:
            continue
        pts = p[g].reshape(-1, 3)
        res.append(dict(idx=g, area=float(a[g].sum()), z0=float(pts[:, 2].min()), z1=float(pts[:, 2].max()),
                        xmin=float(pts[:, 0].min()), xmax=float(pts[:, 0].max()),
                        ymin=float(pts[:, 1].min()), ymax=float(pts[:, 1].max())))
    return sorted(res, key=lambda c: -c['area'])

def shape_to_mesh(shape, tol=0.03):
    vs, ts = shape.tessellate(tol)
    pts = np.array([[q.x, q.y, q.z] for q in vs])
    key = {}
    remap, newv = [], []
    for q in pts:
        kk = tuple(np.round(q, 4))
        if kk not in key:
            key[kk] = len(newv)
            newv.append(q)
        remap.append(key[kk])
    tris = np.array([[remap[a], remap[b], remap[c]] for a, b, c in ts])
    tris = np.array([tr for tr in tris if len(set(tr)) == 3])
    return np.array(newv), tris

def enforcer_from_cluster(v, t, cl, z_below, z_above=0.4, keep_out=None):
    """Prism under an overhang cluster: its exact plan view, from the bed up to just inside the roof."""
    faces = []
    for i in cl['idx']:
        p = [A.Vector(float(v[k][0]), float(v[k][1]), 0.0) for k in t[i]]
        w = Part.makePolygon([p[0], p[1], p[2], p[0]])
        try:
            f = Part.Face(w)
        except Exception:
            continue
        if f.Area > 1e-6:
            faces.append(f)
    fused = faces[0].fuse(faces[1:]) if len(faces) > 1 else faces[0]
    fused = fused.removeSplitter()
    height = cl['z0'] - z_below + z_above
    solids = [f.extrude(A.Vector(0, 0, height)) for f in fused.Faces]
    sol = solids[0].fuse(solids[1:]) if len(solids) > 1 else solids[0]
    sol.translate(A.Vector(0, 0, z_below))
    if keep_out is not None:
        sol = sol.cut(keep_out)
    return sol

def cylinder_blocker(cx, cy, r, z0, z1):
    return Part.makeCylinder(r, z1 - z0, A.Vector(cx, cy, z0), A.Vector(0, 0, 1))

# --------------------------------------------------------------------------- support painting
def paint(name, v, t):
    """Returns (support_mode, [(kind, mesh_v, mesh_t, label)]) in the part's own (released) coordinates."""
    cl = overhang_clusters(v, t)
    vols, notes = [], []
    if name == 'Pan_Raised_Pedestal':
        top = cl[0]                      # the 50 x 51.5 top-plate underside, flat at z 18.5
        assert top['area'] > 1500 and abs(top['z0'] - 18.5) < 0.2, top
        cx = (v[:, 0].min() + v[:, 0].max()) / 2
        cy = (v[:, 1].min() + v[:, 1].max()) / 2
        keep = Part.makeCylinder(14.7, 40, A.Vector(cx, cy, -5), A.Vector(0, 0, 1))   # belt flange (r 13.3) + 1.4
        e = enforcer_from_cluster(v, t, top, 0.0, keep_out=keep)
        vols.append(('support_enforcer', *shape_to_mesh(e), 'Top-plate underside support'))
        notes.append('top-plate underside %.0f mm2 at z %.1f, kept clear of r<14.7 around the belt groove' % (top['area'], top['z0']))
        return 'normal(manual)', vols, notes
    if name == 'Rear_Display_Frame':
        tabs = [c for c in cl if 40 < c['area'] < 80 and abs(c['z0'] - 58.2) < 0.3]
        assert len(tabs) == 4, [(c['area'], c['z0']) for c in cl]
        for k, c in enumerate(tabs, 1):
            e = enforcer_from_cluster(v, t, c, 0.0)
            vols.append(('support_enforcer', *shape_to_mesh(e), 'Corner tab support %d' % k))
        notes.append('4 corner tabs at z 58.2, %.0f mm2 each' % tabs[0]['area'])
        return 'normal(manual)', vols, notes
    if name == 'Neck_Main':
        # the two round ceilings: 22.5 mm mast-bore ceiling (z 16.0) and the stepped ledge (z 15.5)
        bores = [c for c in cl if (abs(c['z0'] - 16.0) < 0.1 and 250 < c['area'] < 270) or
                 (abs(c['z0'] - 15.5) < 0.1 and 110 < c['area'] < 130)]
        assert len(bores) == 2, [(c['area'], c['z0']) for c in cl]
        for c in bores:
            cx, cy = (c['xmin'] + c['xmax']) / 2, (c['ymin'] + c['ymax']) / 2
            r = max(c['xmax'] - c['xmin'], c['ymax'] - c['ymin']) / 2 + 0.3
            vols.append(('support_blocker', *shape_to_mesh(cylinder_blocker(cx, cy, r, 0.0, c['z0'] + 0.3)),
                         'Bore ceiling z %.1f (keep clear)' % c['z0']))
        lip = [c for c in cl if abs(c['z0'] - 41.5) < 0.1 and 10 < c['area'] < 40]
        assert len(lip) == 1, [(c['area'], c['z0']) for c in cl]
        c = lip[0]
        cx, cy = (c['xmin'] + c['xmax']) / 2, (c['ymin'] + c['ymax']) / 2
        vols.append(('support_blocker', *shape_to_mesh(cylinder_blocker(cx, cy, 11.5, 36.0, 44.0)),
                     'Tube-top lip z 41.5 (0.8 mm step, no support)'))
        ears = [c for c in cl if abs(c['z0'] - 0.5) < 0.1 and 15 < c['area'] < 25]      # the two clamp-bolt ears
        assert len(ears) == 2, [(c['area'], c['z0']) for c in cl]
        for c in ears:
            box = Part.makeBox(c['xmax'] - c['xmin'] + 2.0, c['ymax'] - c['ymin'] + 2.0, 11.0,
                               A.Vector(c['xmin'] - 1.0, c['ymin'] - 1.0, 0.0))
            vols.append(('support_blocker', *shape_to_mesh(box), 'Clamp-bolt ear (keep the bolt hole clear)'))
        notes.append('blockers in the two bore ceilings, over the tube-top lip and the two clamp-bolt ears; everything else auto')
        return 'normal(auto)', vols, notes
    return None, vols, notes

# --------------------------------------------------------------------------- settings
def flatten_json(path):
    d = json.load(open(path))
    base = {}
    if d.get('inherits'):
        hits = list(SYSTEM.glob('**/' + d['inherits'] + '.json'))
        base = flatten_json(hits[0])
    base.update({k: v for k, v in d.items() if k != 'inherits'})
    return base

def build_settings():
    cfg = json.load(open(TPL / 'project_settings.EnderNeo-template.config'))
    skip = {'name', 'type', 'from', 'version', 'inherits', 'compatible_printers', 'compatible_printers_condition',
            'print_settings_id', 'printer_settings_id', 'filament_settings_id', 'default_print_profile',
            'default_filament_profile'}
    applied = {}
    for kind, nm in (('machine', 'EnderNeo'), ('filament', 'Generic PLA @System - First Print'),
                     ('process', '0.20mm Standard @ First Print')):
        flat = flatten_json(USER / kind / (nm + '.json'))
        for k, val in flat.items():
            if k in skip or k not in cfg:
                continue
            if kind == 'filament' and not isinstance(val, list):
                continue
            if cfg[k] != val:
                applied[k] = (cfg[k], val)
            cfg[k] = val
    cfg['print_settings_id'] = '0.20mm Standard @ First Print'
    cfg['printer_settings_id'] = 'EnderNeo'
    cfg['filament_settings_id'] = ['Generic PLA @System - First Print']
    # the support set-up for the head plates
    cfg.update({'enable_support': '1', 'support_type': 'normal(manual)', 'support_on_build_plate_only': '0',
                'support_threshold_angle': '45', 'brim_type': 'no_brim', 'skirt_loops': '0'})
    return cfg, applied

# --------------------------------------------------------------------------- layout
def layout(rows):
    """Shelf layout, centred on the bed. Returns {name: (centre_x, centre_y)} on bed coordinates."""
    dims = {n: (np.ptp(PARTS[n][0][:, 0]), np.ptp(PARTS[n][0][:, 1])) for r in rows for n in r}
    row_w = [sum(dims[n][0] for n in r) + GAP * (len(r) - 1) for r in rows]
    row_h = [max(dims[n][1] for n in r) for r in rows]
    total_h = sum(row_h) + GAP * (len(rows) - 1)
    pos = {}
    y = BED / 2 - total_h / 2
    for r, rw, rh in zip(rows, row_w, row_h):
        x = BED / 2 - rw / 2
        for n in r:
            pos[n] = (x + dims[n][0] / 2, y + rh / 2)
            x += dims[n][0] + GAP
        y += rh + GAP
    return pos, dims, (max(row_w), total_h)

# --------------------------------------------------------------------------- writer
def uid(tag):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'gladiator-head-orca/' + tag))

def mesh_xml(oid, v, t, tag):
    L = ['  <object id="%d" p:UUID="%s" type="model">' % (oid, uid(tag)), '   <mesh>', '    <vertices>']
    L += ['     <vertex x="%.5f" y="%.5f" z="%.5f"/>' % tuple(q) for q in v]
    L += ['    </vertices>', '    <triangles>']
    L += ['     <triangle v1="%d" v2="%d" v3="%d"/>' % tuple(q) for q in t]
    L += ['    </triangles>', '   </mesh>', '  </object>']
    return '\n'.join(L)

MODEL_HEAD = ('<?xml version="1.0" encoding="UTF-8"?>\n<%s unit="millimeter" xml:lang="en-US" '
              'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
              'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
              'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n')

def write_plate(plate, cfg):
    pos, dims, extent = layout(plate['rows'])
    names = [n for r in plate['rows'] for n in r]
    next_id = [1]
    def nid():
        i = next_id[0]; next_id[0] += 1; return i
    objs, report = [], []
    for n in names:
        v, t = PARTS[n]
        cx = (v[:, 0].min() + v[:, 0].max()) / 2
        cy = (v[:, 1].min() + v[:, 1].max()) / 2
        shift = np.array([cx, cy, 0.0])
        mode, vols, notes = paint(n, v, t)
        meshes = [('normal_part', n, v - shift, t)]
        for kind, vv, tt, label in vols:
            meshes.append((kind, label, vv - shift, tt))
        mids = [nid() for _ in meshes]
        oid = nid()
        objs.append(dict(name=n, oid=oid, mids=mids, meshes=meshes, pos=pos[n], mode=mode))
        report.append(dict(part=n, at=[round(pos[n][0], 1), round(pos[n][1], 1)], size=[round(dims[n][0], 1), round(dims[n][1], 1)],
                           support_mode=mode, painted=[m[1] for m in meshes[1:]], notes=notes))
    out_path = OUT / (plate['name'] + '.3mf')
    zf = zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED)
    ct = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
          ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
          ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
          ' <Default Extension="png" ContentType="image/png"/>\n <Default Extension="gcode" ContentType="text/x.gcode"/>\n</Types>')
    zf.writestr('[Content_Types].xml', ct)
    zf.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>')
    # per-object mesh files
    rels = []
    for o in objs:
        fn = '3D/Objects/%s.model' % o['name']
        body = MODEL_HEAD % 'model' + ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n'
        body += '\n'.join(mesh_xml(mid, m[2], m[3], '%s/%d' % (o['name'], mid)) for mid, m in zip(o['mids'], o['meshes']))
        body += '\n </resources>\n <build/>\n</model>\n'
        zf.writestr(fn, body)
        rels.append(fn)
    zf.writestr('3D/_rels/3dmodel.model.rels', '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n' +
                '\n'.join(' <Relationship Target="/%s" Id="rel-%d" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' % (f, i + 1) for i, f in enumerate(rels)) +
                '\n</Relationships>')
    m = MODEL_HEAD % 'model'
    m += ' <metadata name="Application">BambuStudio-02.06.00.51</metadata>\n <metadata name="OrcaSlicer">2.4.2</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
    m += ' <metadata name="Title">%s</metadata>\n <resources>\n' % plate['name']
    for o in objs:
        m += '  <object id="%d" p:UUID="%s" type="model">\n   <components>\n' % (o['oid'], uid('obj/' + o['name']))
        for mid in o['mids']:
            m += '    <component p:path="/3D/Objects/%s.model" objectid="%d" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n' % (o['name'], mid, uid('comp/%s/%d' % (o['name'], mid)))
        m += '   </components>\n  </object>\n'
    m += ' </resources>\n <build p:UUID="%s">\n' % uid('build/' + plate['key'])
    for o in objs:
        m += '  <item objectid="%d" p:UUID="%s" transform="1 0 0 0 1 0 0 0 1 %.4f %.4f 0" printable="1"/>\n' % (o['oid'], uid('item/' + o['name']), o['pos'][0], o['pos'][1])
    m += ' </build>\n</model>\n'
    zf.writestr('3D/3dmodel.model', m)
    # model_settings.config
    ms = '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'
    for o in objs:
        ms += '  <object id="%d">\n    <metadata key="name" value="%s"/>\n    <metadata key="extruder" value="1"/>\n' % (o['oid'], o['name'])
        if o['name'] == 'Neck_Main':
            ms += ('    <metadata key="support_type" value="normal(auto)"/>\n    <metadata key="brim_type" value="outer_only"/>\n'
                   '    <metadata key="brim_width" value="8"/>\n')
        for mid, (kind, label, vv, tt) in zip(o['mids'], o['meshes']):
            ms += '    <part id="%d" subtype="%s">\n      <metadata key="name" value="%s"/>\n' % (mid, kind, label)
            ms += '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
            ms += '      <mesh_stat face_count="%d" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n    </part>\n' % len(tt)
        ms += '  </object>\n'
    ms += '  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value="%s"/>\n    <metadata key="locked" value="false"/>\n' % plate['key']
    ms += '    <metadata key="filament_map_mode" value="Auto For Flush"/>\n    <metadata key="gcode_file" value=""/>\n'
    for k, o in enumerate(objs):
        ms += '    <model_instance>\n      <metadata key="object_id" value="%d"/>\n      <metadata key="instance_id" value="0"/>\n      <metadata key="identify_id" value="%d"/>\n    </model_instance>\n' % (o['oid'], 100 + k)
    ms += '  </plate>\n  <assemble>\n  </assemble>\n</config>\n'
    zf.writestr('Metadata/model_settings.config', ms)
    zf.writestr('Metadata/project_settings.config', json.dumps(cfg, indent=4))
    zf.writestr('Metadata/filament_sequence.json', (TPL / 'filament_sequence.json').read_text())
    zf.writestr('Metadata/slice_info.config', (TPL / 'slice_info.config').read_text())
    zf.close()
    return out_path, report, extent

cfg, applied = build_settings()
summary = {'plates': {}, 'settings_overridden_vs_template': {k: {'template': a, 'now': b} for k, (a, b) in applied.items()}}
for pl in PLATES:
    path, report, extent = write_plate(pl, cfg)
    summary['plates'][pl['key']] = dict(file=path.name, extent_mm=[round(extent[0], 1), round(extent[1], 1)], parts=report,
                                        sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    print(pl['key'], path.name, 'extent %.0f x %.0f' % extent, flush=True)
(OUT / 'build-summary.json').write_text(json.dumps(summary, indent=1, default=str))
print('DONE')
