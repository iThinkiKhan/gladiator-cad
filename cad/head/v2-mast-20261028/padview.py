import FreeCAD as A, Part, MeshPart, math, json, numpy as np
D="/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/"
v=json.load(open(D+"validation.json"))["v2"]; P=v["params"]
d=A.openDocument(D+"Gladiator_Head_v2_Mast.FCStd")
S={o.Name:o.Shape for o in d.Objects if o.TypeId=="Part::Feature"}
W=A.Vector(39.5,113,P["LIFT"])
ang=math.radians(225.0)
u=A.Vector(math.cos(ang),math.sin(ang),0)
out={}
def dump(tag,s):
    s=s.copy(); s.translate(-W)
    # into servo frame F: rotate so the servo direction is -Y
    s.rotate(A.Vector(),A.Vector(0,0,1),-(225.0-270.0))
    m=MeshPart.meshFromShape(Shape=s,LinearDeflection=0.05,AngularDeflection=0.3)
    out[tag]=[[list(p) for p in f.Points] for f in m.Facets]
dump("neck",S["Neck_Main"])
for C in (P["C_MIN"],P["C_MAX"]):
    for n in ("SG90_Pan_Reference","Pan_Servo_Carriage"):
        s=S[n].copy(); s.translate(u*(C-P["C_NOM"])); dump("%s_%g"%(n,C),s)
json.dump(out,open("/tmp/padview.json","w"))
print("ok")
