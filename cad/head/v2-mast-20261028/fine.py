import FreeCAD as A, json
D='/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/'
v=json.load(open(D+'validation.json'))['v2']
d=A.openDocument(D+'Gladiator_Head_v2_Mast.FCStd')
S={o.Name:o.Shape for o in d.Objects if o.TypeId=='Part::Feature'}
tilt=v['groups']['tilt']; pan=v['groups']['pan']; fixed=v['groups']['fixed']
T=A.Vector(*v['tilt_axis_world'])
for sign,lab in ((-1,'UP'),(1,'DOWN')):
    for k in range(20,61):
        t=sign*k; hits=[]
        for a in tilt:
            s=S[a].copy(); s.rotate(T,A.Vector(1,0,0),t)
            for b in pan+fixed:
                if not s.BoundBox.intersect(S[b].BoundBox): continue
                c=s.common(S[b])
                if c.Volume>0.05:
                    bb=c.BoundBox
                    hits.append((a,b,round(c.Volume,1),'x%.0f..%.0f y%.0f..%.0f z%.0f..%.0f'%(bb.XMin-39.5,bb.XMax-39.5,bb.YMin-113,bb.YMax-113,bb.ZMin-50,bb.ZMax-50)))
        if hits:
            print('camera',lab,'first contact at',k,'deg'); [print('   ',h) for h in hits]; break
