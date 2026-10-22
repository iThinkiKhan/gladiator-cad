"""Independent saved-file and hardware checks for camera service v2."""
import sys
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A, Part, Mesh, _PartDesign, json, math
from pathlib import Path
P=Path('/home/buralien/projects/gladiator-cad/cad/head/camera-service-v2-20261021')
report={}
d=A.openDocument(str(P/'Gladiator_Camera_Service_v2_REVIEW.FCStd'))
c=json.loads((P/'validation.json').read_text())
assert c['checks']['all_asserts_pass']
printed=[d.getObject(n).Shape for n in ('Mount_Tray','Screw_Cover')]
for nm,key,shape in zip(('Tray','Lid'),('tray','lid'),printed):
    mesh=Mesh.Mesh(str(P/'stl'/('Camera_Service_v2_%s.stl'%nm)))
    assert mesh.isSolid()
    assert shape.isValid() and len(shape.Solids)==1
    rel=abs(mesh.Volume-shape.Volume)/shape.Volume
    assert rel<.005,(nm,rel)
    rebuilt=Part.Shape(); rebuilt.makeShapeFromMesh(mesh.Topology,.02)
    solid=Part.makeSolid(Part.Shell(rebuilt.Faces))
    assert solid.isValid() and len(solid.Solids)==1
    report[nm]={'native_valid':True,'stl_closed':True,'stl_reconstructed_solid_valid':True,'stl_volume_relative_error':rel}
step=Part.read(str(P/'Gladiator_Camera_Service_v2.step'))
assert step.isValid() and len(step.Solids)==2
diffs=[]
for s in printed:
    t=min(step.Solids,key=lambda q:abs(q.Volume-s.Volume))
    dif=s.cut(t).Volume+t.cut(s).Volume
    assert dif<1e-4,dif
    diffs.append(dif)
report['step_native_symmetric_difference_mm3']=diffs
board=d.getObject('ESP32_CAM_measured_reference').Shape
screws=[o.Shape for o in d.getObject('Fasteners').Group if o.Name.startswith('M3x12')]
nuts=[o.Shape for o in d.getObject('Fasteners').Group if o.Name.startswith('M3_nut')]
wires=[o.Shape for o in d.getObject('BoardAndWiring').Group if o.Name.startswith('Wire_route')]
dups=[o.Shape for o in d.getObject('BoardAndWiring').Group if o.Name.startswith('Dupont')]
hardware=screws+nuts
for i,h in enumerate(hardware):
    assert h.common(board).Volume<1e-6
    assert all(h.common(p).Volume<1e-6 for p in printed)
    assert all(h.common(p).Volume<1e-6 for p in dups)
report['hardware_board_case_connector_checks_pass']=True
other=[o for o in d.getObject('HeadContext').Group]
wire_hits=[]
for ob in other:
    for w in wires:
        ov=w.common(ob.Shape).Volume
        if ov>1e-6: wire_hits.append([ob.Name,ov])
report['installed_wire_head_context_hits']=wire_hits
assert not wire_hits,wire_hits
# All work below uses the original construction frame, matching v05's saved source.
def unpose(s):
    t=s.copy(); t.rotate(A.Vector(39.5,113,0),A.Vector(0,0,1),-180); return t
asm=A.openDocument('/home/buralien/projects/gladiator-cad/cad/head/v05-sensor-mounts/Gladiator_Head_v05_PanStack.FCStd')
G={o.Name:o.Shape for o in asm.Objects if hasattr(o,'Shape') and not o.Shape.isNull()}
static=[n for n in G if n.startswith('Ctx_') or n in ('Neck_Main','Neck_Clamp_Cap','Pan_Servo_Carriage','SG90_Pan_Reference')]
panmov=['Pan_Rotor','Pan_Retainer','Pan_Raised_Pedestal','Pan_Drive_Pulley','Pan_Belt_Reference','Pan_Bearing_Lower','Pan_Bearing_Upper','Pan_Inner_Spacer','Pan_Circlip_Envelope','Tilt_Yoke','SG90_Tilt_Reference','Tilt_Pivot_Bolt']
h0=[unpose(h) for h in hardware]
hits=[]; count=0
for tilt in range(-25,26):
    ht=[s.copy() for s in h0]
    for h in ht:
        h.rotate(A.Vector(0,87,216.5),A.Vector(1,0,0),tilt)
        for n in panmov:
            if h.BoundBox.intersect(G[n].BoundBox):
                ov=h.common(G[n]).Volume
                if ov>1e-6:hits.append([tilt,n,ov])
    for pan in range(-20,181,10):
        count+=1
        for h in ht:
            t=h.copy(); t.rotate(A.Vector(39.5,113,0),A.Vector(0,0,1),pan)
            for n in static:
                if t.BoundBox.intersect(G[n].BoundBox):
                    ov=t.common(G[n]).Volume
                    if ov>1e-6:hits.append([tilt,pan,n,ov])
report['hardware_motion_poses']=count
report['hardware_motion_hits']=hits
assert not hits,hits
report['pass']=True
(P/'independent-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

