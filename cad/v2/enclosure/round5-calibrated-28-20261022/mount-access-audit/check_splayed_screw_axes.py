from pathlib import Path
import FreeCAD as A,Part,json,traceback,os
V=A.Vector
N=Path('/home/buralien/projects/gladiator-cad/cad/v2/enclosure/round5-calibrated-28-20261022');O=N/'mount-access-audit'
try:
 d=A.openDocument(str(N/'print/Gladiator_Round5_Print.FCStd'));hood=d.Rear_Hood.Shape;report=json.loads((O/'mount-access-audit.json').read_text());checks=[]
 for record in report['rail_mounts']:
  side=record['side'];seat=sum(record['screw_head_bearing_x_range_mm'])/2;grip=record['grip_to_rail_mm'];entry=seat+grip*(1 if side=='L' else -1);p=V(*record['actual_rail_bore']['center']);axis=V(*record['actual_rail_bore']['axis']);start=p+axis*((seat-p.x)/axis.x);direction=axis if axis.x*(1 if side=='L' else -1)>0 else -axis
  lengths=grip/abs(axis.x)-.21
  values={}
  for radius in [1.5,1.6]:
   probe=Part.makeCylinder(radius,lengths,start,direction);values[str(radius)]=hood.common(probe).Volume
  checks.append({'side':side,'hole_yz':record['hole_yz'],'axis_matched_start':[start.x,start.y,start.z],'nominal_M3_shaft_intersection_mm3':values['1.5'],'plus_0_1mm_radius_print_allowance_intersection_mm3':values['1.6']})
 (O/'splayed-axis-clearance.json').write_text(json.dumps(checks,indent=2))
except BaseException:(O/'AXIS_ERROR.txt').write_text(traceback.format_exc())
os._exit(0)
