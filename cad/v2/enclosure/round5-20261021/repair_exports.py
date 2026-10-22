from pathlib import Path
import FreeCAD as A,Part,MeshPart,Mesh,json,math,os,traceback,collections,time
R=Path('/home/buralien/projects/gladiator-cad');O=R/'cad/v2/enclosure/round5-20261021';out={}
try:
 d=A.openDocument(str(O/'Gladiator_Round5.FCStd'));b=A.openDocument(str(O/'baseline-v28/Gladiator_Enclosure_v2.FCStd'))
 def clean(s):
  q=Part.Shape();q.importBrepFromString(s.exportBrepToString());return q.Solids[0] if len(q.Solids)==1 else q
 s=clean(d.Front_Left.Shape)
 m=Mesh.Mesh(str(O/'stl/Front_Left.stl'));points,faces=m.Topology
 edges=collections.Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3))
 boundary=[e for e,n in edges.items() if n==1]
 out['original_mesh']=dict(facets=m.CountFacets,solid=m.isSolid(),nonmanifold=m.hasNonManifolds(),boundary_edges=len(boundary),boundary_vertices=[[list(points[v]) for v in e] for e in boundary[:60]])
 out['mesh_methods']=[n for n in dir(m) if any(w in n.lower() for w in('hole','fix','duplic','degener','normal','solid'))]
 out['variants']=[]
 (O/'export-diagnostic.json').write_text(json.dumps(out,indent=2))
 # Isolate the core left after removing only exterior half-spaces; compare it geometrically to baseline.
 h=clean(d.Rear_Hood.Shape);old=clean(b.Rear_Hood.Shape)
 masks=[Part.makeBox(30,70,40,A.Vector(-39,-12,50)),Part.makeBox(30,70,40,A.Vector(88,-12,50)),Part.makeBox(110,20,80,A.Vector(-10,-52,40))]
 core=h
 for mask in masks:core=clean(core.cut(mask,.00001))
 core_added=core.cut(old,.00001);core_lost=old.cut(core,.00001)
 core_added.exportBrep(str(O/'unintended-interior.brep'))
 out['extra_bbox']=[core_added.BoundBox.XMin,core_added.BoundBox.XMax,core_added.BoundBox.YMin,core_added.BoundBox.YMax,core_added.BoundBox.ZMin,core_added.BoundBox.ZMax]
 out['extra_vertices']=[list(v.Point) for v in core_added.Vertexes][:60]
 out['core_comparison']=dict(valid=core.isValid(),core_volume_mm3=core.Volume,baseline_volume_mm3=old.Volume,added_to_core_mm3=core_added.Volume,removed_from_core_mm3=core_lost.Volume,added_solids=len(core_added.Solids),removed_solids=len(core_lost.Solids))
 (O/'export-diagnostic.json').write_text(json.dumps(out,indent=2))
except BaseException:out['error']=traceback.format_exc();(O/'export-diagnostic.json').write_text(json.dumps(out,indent=2))
os._exit(0)

