import sys,json,hashlib
from pathlib import Path
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A
import Part
D=Path('/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/closed-tube-review-20261030')
r=json.loads((D/'validation.json').read_text())
d=A.openDocument(str(D/'Gladiator_Closed_Mast_Review.FCStd'))
s=d.getObject('Mast_Tube_v2').Shape.copy();s.translate(A.Vector(-39.5,-113,0))
checks={}
checks['saved_native_single_valid_solid']=s.isValid() and len(s.Solids)==1
checks['source_hash_preserved']=hashlib.sha256((D.parent/'Gladiator_Head_v2_Mast.FCStd').read_bytes()).hexdigest()==r['source_sha256']
checks['saved_height_144']=abs(s.BoundBox.ZLength-144)<1e-6
for side in (-1,1):
    plug=Part.makeBox(2.84,2.84,113,A.Vector(-1.42,side*4.4-1.42,37))
    checks['full_upper_wire_path_'+str(side)]=s.common(plug).Volume<1e-5
    # Nominal 3.2-mm round gauge along the full upper wire route.
    gauge=Part.makeCylinder(1.6,113,A.Vector(0,side*4.4,37))
    checks['round_wire_path_'+str(side)]=s.common(gauge).Volume<1e-5
# Verify material replacing the old rear slot through the unsupported middle span.
probe=Part.makeBox(4,2,65,A.Vector(-2,-9,40))
checks['rear_wall_restored']=abs(s.common(probe).Volume-probe.Volume)<1e-5
for name in ('Closed_Tube','Closed_Tube_Bolt_Guard'):
    step=Part.Shape();step.read(str(D/(name+'.step')))
    checks[name+'_step_valid_solid']=step.isValid() and len(step.Solids)==1
r['independent_saved_checks']=checks
(D/'validation.json').write_text(json.dumps(r,indent=2)+'\n')
assert all(checks.values()),checks
print(json.dumps(checks,indent=2))
A.closeDocument(d.Name)
