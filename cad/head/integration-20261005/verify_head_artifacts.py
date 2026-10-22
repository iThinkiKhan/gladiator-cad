"""Independent native/STEP/plate verification for v04 integration and v05 mounts."""
import sys,json,hashlib,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad/Mod'])
import FreeCAD as A
import Part, Mesh

ROOT=Path('/home/buralien/projects/gladiator-cad')
version=sys.argv[1]
out=ROOT/('cad/head/v04-pan-stack' if version=='v04' else 'cad/head/v05-sensor-mounts')
validation=json.loads((out/'validation.json').read_text())
assert validation['checks']['sampled_geometry_pass']
native=A.openDocument(str(out/('Gladiator_Head_%s_PanStack.FCStd'%version)))
names=[o.Name for o in native.Objects if hasattr(o,'MotionGroup')]
comparison={}
baseline=ROOT/'cad/head/review-20261005/candidate/Gladiator_Head_v04_PanStack.FCStd' if version=='v04' else ROOT/'cad/head/v04-pan-stack/Gladiator_Head_v04_PanStack.FCStd'
old=A.openDocument(str(baseline))
changed=[]
for n in names:
    saved=native.getObject(n).Shape
    assert saved.isValid() and len(saved.Solids)==1,n
    previous=old.getObject(n)
    if previous is None:
        changed.append(n);continue
    diff=saved.cut(previous.Shape).Volume+previous.Shape.cut(saved).Volume
    comparison[n]=round(diff,8)
    if diff>1e-5:changed.append(n)
expected=[] if version=='v04' else ['GH44_Dual_Carrier','ToF_Sensor_Frame','Radar_Sensor_Frame','Dual_ToF_Envelope','Dual_Radar_Envelope']
assert set(changed)==set(expected),(changed,expected)
if version=='v05':
    preview=json.loads((out/'sensor-preview-source.json').read_text())
    assert preview['native_sha256']==hashlib.sha256((out/'Gladiator_Head_v05_PanStack.FCStd').read_bytes()).hexdigest()
    assert preview['image_sha256']==hashlib.sha256((out/'sensor-mounts.png').read_bytes()).hexdigest()
step=Part.Shape();step.read(str(out/('Gladiator_Head_%s_PanStack.step'%version)))
assert step.isValid() and len(step.Solids)==len(names)
total=sum(native.getObject(n).Shape.Volume for n in names)
relative=abs(step.Volume-total)/total
assert relative<1e-6

# Match every stored triangle and vertex to its canonical STL, allowing only plate translation.
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
plates={}
for file in sorted((out/'plates').glob('*.3mf')):
    with zipfile.ZipFile(file) as z:
        assert z.testzip() is None
        root=ET.fromstring(z.read('3D/3dmodel.model'))
    assert root.attrib['unit']=='millimeter'
    objects=root.findall('m:resources/m:object',ns)
    for o in objects:
        name=o.attrib['name']
        verts=[tuple(float(v.attrib[k]) for k in ('x','y','z')) for v in o.findall('m:mesh/m:vertices/m:vertex',ns)]
        triangles=[tuple(int(t.attrib[k]) for k in ('v1','v2','v3')) for t in o.findall('m:mesh/m:triangles/m:triangle',ns)]
        mesh=Mesh.Mesh(str(out/'stl'/('Gladiator_Head_%s_%s.stl'%(version,name))))
        points,facets=mesh.Topology
        assert len(verts)==len(points) and triangles==facets,(file,name,'topology')
        offset=tuple(verts[0][k]-tuple(points[0])[k] for k in range(3))
        error=max(abs(verts[i][k]-tuple(points[i])[k]-offset[k]) for i in range(len(points)) for k in range(3))
        # Four-decimal XML plus float32 STL translation introduces up to ~0.00012 mm.
        assert error<.00013,(name,error)
        assert all(10-.001<=v[0]<=210+.001 and 10-.001<=v[1]<=210+.001 and v[2]>=-.001 for v in verts)
    plates[file.name]={'objects':len(objects),'canonical_stl_topology_match':True,'vertices_within_bed':True}
result={'native_reopened_valid':True,'step_valid':True,'step_solids':len(names),'step_relative_volume_error':relative,
        'preview_matches_final_native':version=='v05',
        'geometry_changes_vs_reviewed_v04':changed,'symmetric_difference_mm3':comparison,'plates':plates}
(out/'artifact-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
