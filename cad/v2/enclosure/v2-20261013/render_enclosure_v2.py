import FreeCAD as A, FreeCADGui as G, Part, os, traceback
V=A.Vector
O="/home/buralien/projects/gladiator-cad/cad/v2/enclosure/v2-20261013/"
try:
    d=A.openDocument(O+"Gladiator_Enclosure_v2.FCStd")
    A.setActiveDocument(d.Name); G.setActiveDocument(d.Name)
    def style(o,col,tr=0,line=(.10,.12,.14)):
        v=o.ViewObject; v.ShapeColor=col; v.LineColor=line; v.Transparency=tr; v.DisplayMode='Flat Lines'; v.Visibility=True
    names={o.Name:o for o in d.Objects}
    for n,o in names.items():
        if n=="Rear_Hood": style(o,(.17,.19,.22))
        elif n.startswith("Front_"): style(o,(.27,.30,.34))
        elif n=="Lens_Plate": style(o,(.15,.85,.95),30)
        elif "Holder" in n or "Speaker" in n or n=="Switch_Bezel": style(o,(.80,.62,.30))
        elif "Fins" in n: style(o,(.80,.62,.30))          # heatsinks read as copper/bronze accent
        elif n.startswith("Ref_DrvV5_Board"): style(o,(.19,.42,.34))
        elif n.startswith("Head_"): style(o,(.55,.59,.62))
        elif n.startswith(("Track","Wheel")): style(o,(.13,.15,.17))
        else: style(o,(.30,.34,.37))
    # illustrative antenna: bulkhead nut, 90-degree elbow, whip (not a validated part)
    sx,sz=68.0,84.5
    for nm,sh in (("Antenna_Whip",Part.makeCylinder(3.5,66,V(sx,-40,sz+3))),("Antenna_Elbow",Part.makeCylinder(4,10,V(sx,-42,sz),V(0,1,0))),("Antenna_Nut",Part.makeCylinder(4.6,3,V(sx,-35,sz),V(0,1,0)))):
        o=d.addObject("Part::Feature",nm); o.Shape=sh; style(o,(.08,.08,.09))
    d.recompute()
    view=G.activeDocument().activeView()
    def shot(name,dirv,w=1500,h=1150,hide=(),trans=None):
        for n,o in names.items():
            o.ViewObject.Visibility=True
        for n in hide:
            for k,o in names.items():
                if k.startswith(n): o.ViewObject.Visibility=False
        if trans:
            for k in ("Rear_Hood","Front_Left","Front_Right"): names[k].ViewObject.Transparency=trans
        else:
            for k in ("Rear_Hood","Front_Left","Front_Right"): names[k].ViewObject.Transparency=0
        import math
        dx,dy,dz=dirv; l=math.sqrt(dx*dx+dy*dy+dz*dz); dvec=V(dx/l,dy/l,dz/l)
        up=V(0,0,1) if abs(dvec.z)<0.99 else V(0,1,0)
        right=dvec.cross(up); right.normalize(); tup=right.cross(dvec); tup.normalize()
        view.setCameraOrientation(A.Rotation(right,tup,dvec*-1,'ZXY')); view.fitAll(); G.updateGui()
        view.saveImage(O+name,w,h,'White')
    shot("render_front_right.png",(-1,-1.1,-0.75))
    shot("render_rear_left.png",(1,1.1,-0.75))
    shot("render_side_right.png",(-1,0,-0.12),1500,900)
    shot("render_top.png",(0,0,-1),1300,1300)
    shot("render_clearance.png",(-1,-1.1,-0.75),trans=80)
    shot("render_switch.png",(1,1.2,-0.5),1300,1000,hide=("Head_","Track","Wheel","Front_","Lens","Ref_Drv","Ref_Mast","Ref_S3","Ref_Bread","Ref_Upper","Ref_Battery","Ref_Power","Ref_Base","Ref_INA","Ref_Board"))
    shot("render_front_right.png",(-1,-1.1,-0.75))
    shot("render_no_head_rear.png",(1,1.1,-0.75),hide=("Head_",))
    print("renders ok",flush=True)
except Exception:
    traceback.print_exc()
os._exit(0)
