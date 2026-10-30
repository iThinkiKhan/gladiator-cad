import FreeCAD as A, Part, json
D='/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/'
v=json.load(open(D+'validation.json'))['v2']
d=A.openDocument(D+'Gladiator_Head_v2_Mast.FCStd')
S={o.Name:o.Shape for o in d.Objects if o.TypeId=='Part::Feature'}
tilt=v['groups']['tilt']; T0=A.Vector(*v['tilt_axis_world'])
F0w=170.5+50
floor=S['Tilt_Yoke'].common(Part.makeBox(200,200,F0w+4.1-100,A.Vector(-60,-60,100)))
obst=[floor]+[S[n] for n in ('Pan_Raised_Pedestal','Pan_Rotor','Pan_Retainer','Neck_Main','Pan_Drive_Pulley','SG90_Pan_Reference','Pan_Servo_Carriage','Pan_Belt_Reference','Pan_Horn_Reference')]
for H in (0,6,10,14,18):
    T=T0+A.Vector(0,0,H); res={}
    for sign,lab in ((-1,'up'),(1,'down')):
        for k in range(20,91):
            hit=None
            for a in tilt:
                s=S[a].copy(); s.translate(A.Vector(0,0,H)); s.rotate(T,A.Vector(1,0,0),sign*k)
                for o in obst:
                    if s.BoundBox.intersect(o.BoundBox) and s.common(o).Volume>0.05: hit=a; break
                if hit: break
            if hit: res[lab]=(k,hit); break
        else: res[lab]=('>90',None)
    print('H',H,res,flush=True)
