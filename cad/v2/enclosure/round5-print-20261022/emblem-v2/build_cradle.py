"""Printed cradle under the white shield emblem (Claude 2026-10-22).
The emblem prints as an arch standing on two 0.5 mm edge lines; its lattice strokes hang over sparse tree tips and ball up.
The cradle fills the arch with solid plastic 0.2 mm below the emblem's back (one empty layer, like support top distance),
0.4 mm clear of its edges and ends, flat on the bed. Emblem geometry unchanged. Prints in the same job, supports off."""
import FreeCAD as A, Part, Mesh, MeshPart, re, zipfile, json, os
V = A.Vector
w, h = 27.3, 41.6
outline = [(-w / 2 + 2, -h / 2), (w / 2 - 2, -h / 2), (w / 2, -h / 2 + 2), (w / 2, h / 2 - 2), (w / 2 - 2, h / 2), (-w / 2 + 2, h / 2), (-w / 2, h / 2 - 2), (-w / 2, -h / 2 + 2)]
CY = 6.25 - 28.0; R_IN = 27.6; GAP = 0.2; END_GAP = 0.4
ZMIN = CY + (R_IN ** 2 - (w / 2) ** 2) ** .5          # emblem's lowest point (inner edge line) = bed
face = Part.Face(Part.makePolygon([V(x, y, ZMIN) for x, y in outline] + [V(outline[0][0], outline[0][1], ZMIN)]))
face = face.makeOffset2D(-END_GAP)
prism = face.extrude(V(0, 0, 12))
cyl = Part.makeCylinder(R_IN - GAP, h + 8, V(0, -h / 2 - 4, CY), V(0, 1, 0))
cradle = prism.common(cyl)
cradle.translate(V(0, 0, -ZMIN))
src = '/home/buralien/scratch_claude/jimslice/01/GLAD_01_WHITE_EMBLEMS_V2_JIM.3mf'
dst = '/home/buralien/scratch_claude/emblem_cradle/GLAD_01_WHITE_EMBLEMS_V2_CRADLE_src.3mf'
os.makedirs(os.path.dirname(dst), exist_ok=True)
m = MeshPart.meshFromShape(Shape=cradle, LinearDeflection=.01, AngularDeflection=.05, Relative=False)
m.write('/home/buralien/scratch_claude/emblem_cradle/Emblem_Cradle.stl')
rep = dict(cradle_volume_mm3=round(cradle.Volume, 1), bbox=[round(x, 3) for x in (cradle.BoundBox.XMin, cradle.BoundBox.XMax, cradle.BoundBox.YMin, cradle.BoundBox.YMax, cradle.BoundBox.ZMin, cradle.BoundBox.ZMax)],
           mesh_solid=m.isSolid(), mesh_nonmanifold=m.hasNonManifolds())
# check against the emblem mesh actually in the 3MF
z = zipfile.ZipFile(src)
t = z.read('3D/Objects/Scutum_Emblem_v2_L.model').decode()
vs = [tuple(map(float, g)) for g in re.findall(r'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"', t)]
tris = [tuple(map(int, g)) for g in re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', t)]
em = Mesh.Mesh([[vs[a], vs[b], vs[c]] for a, b, c in tris])
es = Part.Shape(); es.makeShapeFromMesh(em.Topology, 0.01); es = Part.Solid(Part.Shell(es.Faces)) if not es.Solids else es.Solids[0]
rep['emblem_mesh_volume_mm3'] = round(es.Volume, 1)
rep['cradle_emblem_overlap_mm3'] = round(es.common(cradle).Volume, 4)
rep['min_gap_mm'] = round(es.distToShape(cradle)[0], 3)
# write the combined mesh (emblem shell + cradle shell) into each emblem object
cv = [(p.x, p.y, p.z) for p in m.Points]; ct = [tuple(f.PointIndices) for f in m.Facets]
def merged(text):
    n = len(re.findall(r'<vertex ', text))
    vx = ''.join('     <vertex x="%.5f" y="%.5f" z="%.5f"/>\n' % p for p in cv)
    tx = ''.join('     <triangle v1="%d" v2="%d" v3="%d"/>\n' % (a + n, b + n, c + n) for a, b, c in ct)
    text = text.replace('    </vertices>', vx + '    </vertices>', 1)
    return text.replace('    </triangles>', tx + '    </triangles>', 1)
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zo:
    for it in z.infolist():
        b = z.read(it.filename)
        if it.filename.startswith('3D/Objects/Scutum_Emblem_v2_'):
            s = b.decode(); assert '    </vertices>' in s and '    </triangles>' in s; b = merged(s).encode()
        if it.filename == 'Metadata/model_settings.config':
            b = b.replace(b'face_count="14222"', b'face_count="%d"' % (14222 + len(ct)))
        zo.writestr(it, b)
rep['faces_added'] = len(ct)
print(json.dumps(rep, indent=1), flush=True)
json.dump(rep, open('/home/buralien/scratch_claude/emblem_cradle/cradle-check.json', 'w'), indent=1)
os._exit(0)
