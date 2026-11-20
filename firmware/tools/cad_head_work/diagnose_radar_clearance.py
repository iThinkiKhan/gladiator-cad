import sys,json,math
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad/Mod'])
import FreeCAD as A
import Part
root=Path('/home/buralien/projects/gladiator-cad')
out=root/'cad/head/v05-sensor-mounts'
r=json.loads((out/'validation.json').read_text())
doc=A.openDocument(str(out/'Gladiator_Head_v05_PanStack.FCStd'))
T=A.Vector(0,-26,206.5)
WORLD=A.Vector(39.5,113,10)
robot={}
for name in r['checks']['robot_solids_compared']:
    s=doc.getObject('Ctx_'+name).Shape.copy();s.translate(-WORLD);robot[name]=s
def rect(y,hw,hh):
    vs=[A.Vector(24+x,y,T.z+z) for x,z in [(-hw,-hh),(hw,-hh),(hw,hh),(-hw,hh)]]
    return Part.makePolygon(vs+[vs[0]])
poses=set((p['pan'],p['tilt']) for p in r['radar_fov_reservation']['intersections'])
results=[]
for distance in range(0,9):
    front=-82.6-distance
    frustum=Part.makeLoft([rect(front,11,15),rect(front-150,11+150*math.tan(math.radians(50)),15+150*math.tan(math.radians(40)))],True)
    hits=[]
    for pan,tilt in sorted(poses):
        f=frustum.copy();f.rotate(T,A.Vector(1,0,0),tilt);f.rotate(A.Vector(),A.Vector(0,0,1),pan)
        for name,shape in robot.items():
            if not f.BoundBox.intersect(shape.BoundBox):continue
            vol=f.common(shape).Volume
            if vol>.05:hits.append({'pan':pan,'tilt':tilt,'object':name,'mm3':vol})
    result={'forward_shift_mm':distance,'hits':len(hits),'maximum_intersection_mm3':max([p['mm3'] for p in hits]+[0])}
    results.append(result);print(json.dumps(result),flush=True)
(root/'cad/head/integration-20261005/radar-forward-clearance.json').write_text(json.dumps(results,indent=2)+'\n')
