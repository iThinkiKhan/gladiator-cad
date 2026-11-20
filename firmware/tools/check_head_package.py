import sys,json,hashlib,zipfile,xml.etree.ElementTree as E
from pathlib import Path
sys.path.extend(['/usr/lib/freecad/lib','/usr/lib/freecad/Mod'])
import FreeCAD as A,Part,PartDesign,Sketcher
root=Path('/home/buralien/projects/gladiator-cad');out=root/'cad/head/v01'
r=json.loads((out/'validation.json').read_text())
assert r['checks']['geometry_review_pass']
assert hashlib.sha256((root/'cad/master/Gladiator_Master.FCStd').read_bytes()).hexdigest()==r['master_sha256']
d=A.openDocument(str(out/'Gladiator_Head_v01.FCStd'))
for p in r['parts']:
 o=d.getObject(p['name']); assert o and o.Shape.isValid() and len(o.Shape.Solids)==1,p['name']
 assert abs(o.Shape.Volume-p['volume_mm3'])<.01,p['name']
A.closeDocument(d.Name)
with zipfile.ZipFile(out/'Gladiator_Head_v01.FCStd') as z:
 x=E.fromstring(z.read('GuiDocument.xml'))
 states={o.get('name'):o.find('./Properties/Property[@name="Visibility"]/Bool').get('value') for o in x.findall('./ViewProviderData/ViewProvider') if o.find('./Properties/Property[@name="Visibility"]/Bool') is not None}
 for n in ['GH44_Dual_Carrier','GH44_Tilt_Receiver','Neck_Main','Pan_Rotor']:assert states[n]=='true',(n,states[n])
 for n in ['GH44_Blank_Carrier','GH44_Camera_Carrier','GH44_Fixed_Head_Adapter','GH44_Receiver_Fit_Coupon']:assert states[n]=='false',(n,states[n])
print('PACKAGE_OK: 29 single valid solids; geometry volumes preserved; intended variants visible; master hash unchanged.')
