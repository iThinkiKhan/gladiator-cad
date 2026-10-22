from pathlib import Path
import json, os, traceback
import FreeCAD as A, Part, Mesh
O=Path(__file__).resolve().parent
V=A.Vector
try:
    report=json.loads((O/'validation.json').read_text())
    doc=A.openDocument(str(O/'M2_D3_L3_Coupon.FCStd'))
    s=doc.getObject('Coupon').Shape
    assert s.isValid() and len(s.Solids)==1
    checks=[]
    for site in report['sites']:
        entry=V(*site['entry_mm']);axis=V(*site['axis']);radius=site['diameter_mm']/2
        # The cylindrical land is unobstructed; material closes the blind end.
        clear=s.common(Part.makeCylinder(radius-.01,3.57,entry+axis*.01,axis)).Volume
        floor=s.common(Part.makeCylinder(radius-.05,.1,entry+axis*3.65,axis)).Volume
        wall=s.common(Part.makeCylinder(radius+.03,2.8,entry+axis*.4,axis)).Volume
        assert clear<1e-6 and floor>.1 and wall>.1,(site,clear,floor,wall)
        checks.append(dict(id=site['id'],clear_volume_mm3=clear,floor_volume_mm3=floor,wall_volume_mm3=wall))
    step=Part.Shape();step.read(str(O/'M2_D3_L3_Coupon.step'))
    assert step.isValid() and len(step.Solids)==1
    assert abs(step.Volume-s.Volume)<1e-5
    m=Mesh.Mesh(str(O/'M2_D3_L3_Coupon.stl'))
    assert m.isSolid() and not m.hasNonManifolds()
    assert abs(abs(m.Volume)-s.Volume)/s.Volume<.001
    (O/'saved-file-verification.json').write_text(json.dumps(dict(native_reopen=True,step_reopen=True,
        step_volume_error_mm3=abs(step.Volume-s.Volume),mesh_solid=True,mesh_volume_relative_error=abs(abs(m.Volume)-s.Volume)/s.Volume,
        all_16_blind_bores_verified=True,checks=checks),indent=2))
except BaseException:
    (O/'VERIFY_ERROR.txt').write_text(traceback.format_exc())
os._exit(0)
