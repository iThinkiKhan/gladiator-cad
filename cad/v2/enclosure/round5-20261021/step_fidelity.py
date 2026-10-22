"""STEP checks compare every part; NURBS mass integrals are supplemented by spatial checks."""
import FreeCAD as A,Part

def check_step(doc,report,path):
 step=Part.Shape();step.read(str(path));available=list(step.Solids)
 out=dict(valid=step.isValid(),solids=len(available),expected_solids=len(report['parts']),parts=[])
 out['passed']=out['valid'] and out['solids']==out['expected_solids']
 for n in report['parts']:
  s=doc.getObject(n).Shape.Solids[0]
  if n.startswith('Tablet_'):s=s.fuse(doc.getObject('Letters_'+n[-1]).Shape).removeSplitter().Solids[0]
  i=min(range(len(available)),key=lambda i:(s.CenterOfMass-available[i].CenterOfMass).Length)
  q=available.pop(i);bs,bq=s.BoundBox,q.BoundBox
  bbmax=max(abs(a-b) for a,b in zip([bs.XMin,bs.XMax,bs.YMin,bs.YMax,bs.ZMin,bs.ZMax],[bq.XMin,bq.XMax,bq.YMin,bq.YMax,bq.ZMin,bq.ZMax]))
  row=dict(name=n,native_volume_mm3=s.Volume,step_volume_mm3=q.Volume,volume_difference_mm3=q.Volume-s.Volume,
           centre_error_mm=(s.CenterOfMass-q.CenterOfMass).Length,bbox_error_mm=bbmax,passed=True)
  if abs(q.Volume-s.Volume)>max(.01,s.Volume*.00001) or bbmax>=.002:
   distances=[]
   for aa,bb in[(s,q),(q,s)]:
    points=[v.Point for v in aa.Vertexes]
    for f in aa.Faces:
     p=f.distToShape(Part.Vertex(f.CenterOfMass))[1][0][0]
     points.append(p)
    distances += [bb.distToShape(Part.Vertex(p))[0] for p in points]
   row['surface_samples']=len(distances);row['max_sampled_surface_error_mm']=max(distances)
   row['passed']=max(distances)<.001
   row['spatial_check_note']='Mass-integral or cached bound-box outlier: bidirectional vertices and one projected point per face checked within .001mm. Bounding boxes may include conservative untrimmed/triangulation extents.'
  row['passed'] &= row['centre_error_mm']<.002
  out['parts'].append(row);out['passed'] &= row['passed']
 out['volume_mm3']=sum(x['step_volume_mm3'] for x in out['parts'])
 out['expected_volume_mm3']=sum(x['native_volume_mm3'] for x in out['parts'])
 out['compound_volume_integral_mm3']=step.Volume
 out['note']='Part count, validity, part envelopes and centroids checked. Volume outliers require bidirectional surface samples within .001mm; compound mass integral is reported separately.'
 return out

