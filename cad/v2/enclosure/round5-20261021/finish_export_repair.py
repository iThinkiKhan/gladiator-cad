from pathlib import Path
import FreeCAD as A,Part,Mesh,json,collections,math,os,traceback
O=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-20261021');out={}
try:
 m=Mesh.Mesh(str(O/'stl/Front_Left.stl'));pts,faces=m.Topology
 edge=collections.Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3));vv=sorted({v for e,n in edge.items() if n==1 for v in e});assert len(vv)==4
 anchor=pts[vv[0]];dis=max((pts[i]-anchor).Length for i in vv);assert dis<.001,dis
 replace={i:vv[0] for i in vv};newfaces=[]
 for f in faces:
  ff=tuple(replace.get(i,i) for i in f)
  if len(set(ff))==3:newfaces.append(ff)
 repaired=Mesh.Mesh([[pts[i] for i in f] for f in newfaces]);repaired.harmonizeNormals()
 out['mesh']=dict(original_boundary_vertices=len(vv),maximum_vertex_displacement_mm=dis,solid=repaired.isSolid(),nonmanifold=repaired.hasNonManifolds(),facets=repaired.CountFacets)
 assert repaired.isSolid() and not repaired.hasNonManifolds(),out
 repaired.write(str(O/'stl/Front_Left.stl'))
 d=A.openDocument(str(O/'Gladiator_Round5.FCStd'));b=A.openDocument(str(O/'baseline-v28/Gladiator_Enclosure_v2.FCStd'))
 def clean(s):
  q=Part.Shape();q.importBrepFromString(s.exportBrepToString());return q.Solids[0] if len(q.Solids)==1 else q
 h=clean(d.Rear_Hood.Shape);old=clean(b.Rear_Hood.Shape)
 core=h
 for mask in[Part.makeBox(30,70,40,A.Vector(-39,-12,50)),Part.makeBox(30,70,40,A.Vector(88,-12,50)),Part.makeBox(110,20,80,A.Vector(-10,-52,40))]:core=clean(core.cut(mask,.00001))
 added=core.cut(old,.00001);bb=added.BoundBox
 out['interior_extra']=dict(volume=added.Volume,bbox=[bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax],centre=list(added.CenterOfMass),vertex_count=len(added.Vertexes))
 added.exportBrep(str(O/'unintended-interior.brep'))
 # Determine whether this is actual intrusion or a sub-micron remnant on the original outer skin.
 out['extra_vertices']=[list(v.Point) for v in added.Vertexes][:40]
 (O/'repair-check.json').write_text(json.dumps(out,indent=2))
except BaseException:out['error']=traceback.format_exc();(O/'repair-check.json').write_text(json.dumps(out,indent=2))
os._exit(0)
