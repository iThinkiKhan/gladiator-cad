"""Camera service v2: review redesign derived from measured ESP32 case v4.
Run on cad-lab with xvfb-run -a freecad this-file.py. Baseline is source-v4.py.
"""
from pathlib import Path
import hashlib, json, os, traceback
ROOT = Path('/home/buralien/projects/gladiator-cad')
OUT = ROOT / 'cad/head/camera-service-v2-20261021'
OUT.mkdir(parents=True, exist_ok=True)
BASE = Path('/home/buralien/projects/gladiator-cad/cad/head/camera-service-v2-20261021/source-v4.py')
source = BASE.read_text()

def replace_once(old, new):
    global source
    assert source.count(old) == 1, (old[:80], source.count(old))
    source = source.replace(old, new)

replace_once("OUT = ROOT / 'cad/head/esp32-cam-case-v4'", "OUT = ROOT / 'cad/head/camera-service-v2-20261021'")
replace_once('XC = 26.5', 'XC = 28.0')
replace_once('EAR_R, EAR_DX = 3.0, 12.5', 'EAR_R, EAR_DX = 4.4, 10.0')
replace_once("ears = []\nfor end, z in EAR_Z.items():\n    for sx in (-1, 1):\n        ears.append((XC + sx * EAR_DX, z))", "ears = [(XC - EAR_DX, EAR_Z['sd']), (XC + EAR_DX, EAR_Z['far'])]")
start = source.index('STRUT = 0.8')
end = source.index('# carrier interface through the floor', start)
source = source[:start] + '''# Each side channel opens to the cover seam: wires lay in with plugs attached.
STRUT = 0.0
_mid = (PIN_Z[3] + PIN_Z[4]) / 2
SLOT_Z = [(PIN_Z[7] - 1.6, PIN_Z[0] + 1.6)]
SLOT_Y = (Y_FLOOR_IN - 4.5, Y_FLOOR_IN)
SLOTS = []
for z0, z1 in SLOT_Z:
    for x0, x1 in ((OX0 - 0.1, CX0 + 0.1), (CX1 - 0.1, OX1 + 0.1)):
        sl = (x0, x1, Y_LID_IN - 0.1, Y_FLOOR_IN, z0, z1)
        SLOTS.append(sl)
        tray = tray.cut(lbox(*sl))
''' + source[end:]
replace_once('for x, z in ears:\n    tray = tray.cut(cy(PILOT_M2 / 2, Y_LID_IN - 0.1, Y_LID_IN + EAR_PILOT_DEPTH, x, z))', '''NUT_AF, NUT_DEPTH = 6.0, 2.8  # AF is tested; depth is a design allowance.
NUT_Y = Y_LID_IN + 7.0
nut_cuts = []
for x, z in ears:
    tray = tray.cut(cy(1.8, Y_LID_IN - 0.1, Y_LID_IN + 13.0, x, z))
    rr = NUT_AF / math.sqrt(3)
    vv = [A.Vector(x + rr * math.cos(math.radians(30 + 60*k)), NUT_Y,
                   z + rr * math.sin(math.radians(30 + 60*k))) for k in range(6)]
    pocket = Part.Face(Part.makePolygon(vv + [vv[0]])).extrude(A.Vector(0, NUT_DEPTH, 0))
    if z > 0:
        entry = lbox(x-NUT_AF/2, x+NUT_AF/2, NUT_Y, NUT_Y+NUT_DEPTH, z, z+EAR_R+.2)
    else:
        entry = lbox(x-NUT_AF/2, x+NUT_AF/2, NUT_Y, NUT_Y+NUT_DEPTH, z-EAR_R-.2, z)
    nut_cuts.append(pocket)
    tray = tray.cut(pocket.fuse(entry))
    # 3.6 x 2.4 tie passage through the exposed rear end of each lug.
    tray = tray.cut(lbox(x-EAR_R-.1, x+EAR_R+.1, Y_FACE-7, Y_FACE-3.4, z-1.2, z+1.2))
''')
replace_once('for x, z in ears:\n    lid = lid.cut(cy(M2_CLEAR / 2, Y_LID_OUT - 0.1, Y_LID_IN + 0.1, x, z))\n    lid = lid.cut(cy(2.4, Y_LID_OUT - 0.1, Y_LID_OUT + 1.2, x, z))', '''# Skirts close the open channels after insertion; wires stay at the rear floor.
skirts = []
for z0, z1 in SLOT_Z:
    for x0, x1 in ((OX0+.3, CX0-.3), (CX1+.3, OX1-.3)):
        sk = lbox(x0,x1,Y_LID_IN-.2,SLOT_Y[0],z0+.3,z1-.3)
        # 0.4 mm chamfers where each skirt borders the wire exit.
        for xx,sgn in ((x0,1),(x1,-1)):
            vv=[A.Vector(xx,SLOT_Y[0],z0+.3),A.Vector(xx+sgn*.4,SLOT_Y[0],z0+.3),
                A.Vector(xx,SLOT_Y[0]-.4,z0+.3)]
            sk=sk.cut(Part.Face(Part.makePolygon(vv+[vv[0]])).extrude(A.Vector(0,0,z1-z0-.6)))
        skirts.append(sk)
        lid = fuse(lid,sk)
for x,z in ears:
    lid = lid.cut(cy(1.8,Y_LID_OUT-.1,Y_LID_IN+.1,x,z))
    lid = lid.cut(Part.makeCone(2.15,1.8,.35,A.Vector(x,Y_LID_OUT,z),A.Vector(0,1,0)))
''')
replace_once('lid = fuse(lid, lip_out.cut(lip_in))', '''lip = lip_out.cut(lip_in)
for z0,z1 in SLOT_Z:
    lip = lip.cut(lbox(OX0-1,CX0+1.3,Y_LID_IN-.1,Y_LID_IN+1.4,z0-.1,z1+.1))
    lip = lip.cut(lbox(CX1-1.3,OX1+1,Y_LID_IN-.1,Y_LID_IN+1.4,z0-.1,z1+.1))
lid = fuse(lid,lip)''')

replace_once('tray = tray.removeSplitter()', '''# Chamfer the wire-contact edges of the rear floor by 0.6 mm.
for z0,z1 in SLOT_Z:
    for xx,sgn in ((OX0,1),(OX1,-1)):
        vv=[A.Vector(xx,Y_FLOOR_IN,z0),A.Vector(xx+sgn*.6,Y_FLOOR_IN,z0),
            A.Vector(xx,Y_FLOOR_IN+.6,z0)]
        tray=tray.cut(Part.Face(Part.makePolygon(vv+[vv[0]])).extrude(A.Vector(0,0,z1-z0)))
tray = tray.removeSplitter()''')


replace_once('for x, z in M3_HEADS:\n    tray = tray.cut(cy(3.4, Y_FLOOR_IN - 0.1, Y_FACE + 0.1, x, z))', '''for x, z in M3_HEADS:
    tray = tray.cut(cy(3.4, Y_FLOOR_IN - 0.1, Y_FACE + 0.1, x, z))
    # Shifting the cradle needs a local scallop to preserve carrier-driver access.
    # Radius 2.4 leaves the corner support pads intact (their tips start at 18.6).
    tray = tray.cut(cy(2.4, Y_LID_IN - 0.1, Y_FLOOR_IN + 0.1, x, z))''')

replace_once('for pan in range(-200, 201, 10):','for pan in range(-20, 181, 10):')
replace_once("extra['wire_slot_strut_to_nearest_wire_mm'] = round(min(abs(PIN_Z[3] - (_mid + STRUT / 2)), abs(PIN_Z[4] - (_mid - STRUT / 2))) - 0.7, 3)", "extra['wire_slot_strut_removed'] = True")
replace_once("('ESP32_CAM_Case_v4_%s.stl' % name.capitalize())","('Camera_Service_v2_%s.stl' % name.capitalize())")
replace_once("print(json.dumps(report, indent=1))", "print('BASE_CHECKS_PASS', flush=True)")
extra = '''# Additional service assembly checks.
service = {}
dups,wire_shapes = [],[]
for s in pin_solids:
    px,pz = xb(s.BoundBox.Center.z),zb(s.BoundBox.Center.x)
    d = lbox(px-1.3,px+1.3,Y_BACK+HDR_PLASTIC,Y_BACK+HDR_PLASTIC+LC,pz-1.3,pz+1.3)
    dups.append(d)
    path = lbox(px-1.3,px+1.3,Y_LID_OUT-20,Y_BACK+HDR_PLASTIC+LC,pz-1.3,pz+1.3)
    service.setdefault('connector_insertion_hits_mm3',[]).append(path.common(tray).Volume)
    xo = OX0-1.1 if px < XC else OX1+4
    yend = Y_BACK+HDR_PLASTIC+LC
    yc = Y_FLOOR_IN-1.7
    wire_shapes += [lbox(px-.7,px+.7,yend,yc,pz-.7,pz+.7),
                    lbox(min(px,xo)-.7,max(px,xo)+.7,yc-.7,yc+.7,pz-.7,pz+.7)]
    wire_sweep = lbox(min(px,xo)-.7,max(px,xo)+.7,Y_LID_OUT-20,yc+.7,pz-.7,pz+.7)
    service.setdefault('wire_lay_in_hits_mm3',[]).append(wire_sweep.common(tray).Volume)
service['dupont_vs_lid_max_mm3'] = max(d.common(lid).Volume for d in dups)
service['wires_vs_lid_max_mm3'] = max(w.common(lid).Volume for w in wire_shapes)
service['board_insertion_max_mm3'] = 0.0
for off in (0,-1,-3,-6,-10,-20,-35):
    b=board_comp.copy(); b.translate(A.Vector(0,off,0))
    service['board_insertion_max_mm3']=max(service['board_insertion_max_mm3'],b.common(tray).Volume)
service['cover_removal_max_mm3']=0.0
for off in (0,-.25,-1,-3,-10,-25,-35):
    l=lid.copy(); l.translate(A.Vector(0,off,0))
    service['cover_removal_max_mm3']=max(service['cover_removal_max_mm3'],l.common(tray).Volume,l.common(board_comp).Volume)
hardware=[]
for x,z in ears:
    screw=cy(1.5,Y_LID_OUT,Y_LID_OUT+12,x,z).fuse(cy(3,Y_LID_OUT-3,Y_LID_OUT,x,z))
    hardware.append(screw)
    service.setdefault('screw_vs_print_mm3',[]).append(screw.common(tray).Volume+screw.common(lid).Volume)
    service.setdefault('driver_vs_case_mm3',[]).append(cy(3.2,Y_LID_OUT-35,Y_LID_OUT-.1,x,z).common(tray.fuse(lid)).Volume)
service['nut_seat_mm']=[NUT_AF,NUT_DEPTH]
service['nominal_screw_length_mm']=12
service['screw_tip_beyond_nut_pocket_mm']=Y_LID_OUT+12-(NUT_Y+NUT_DEPTH)
service['closed_exit_height_mm']=4.5
for k,v in service.items():
    if k.endswith('_mm3'):
        assert (max(v) if isinstance(v,list) else v)<1e-4,(k,v)
service['wire_edge_chamfers_mm']=[.6,.4]
service['camera_side_shift_mm']=1.5
service['left_wire_exit_centre_outside_wall_mm']=1.1
report['service_v2']=service
'''
replace_once('# ---------------------------------------------------------------- hard assertions', extra+'\n# ---------------------------------------------------------------- hard assertions')
ns={'__name__':'__camera_build__'}
try:
    (OUT/'generated-build.py').write_text(source)
    exec(compile(source,str(OUT/'generated-build.py'),'exec'),ns)
    import FreeCAD as A, FreeCADGui as Gui, Part, Import, math
    doc=A.newDocument('Camera_Service_v2_Review')
    groups={n:doc.addObject('App::DocumentObjectGroup',n) for n in ('PrintedParts','BoardAndWiring','Fasteners','HeadContext')}
    def pose(shape):
        s=shape.copy(); s.rotate(A.Vector(39.5,113,0),A.Vector(0,0,1),180); return s
    def add(name,shape,group,color,visible=True,alpha=0):
        ob=doc.addObject('PartDesign::Feature',name); ob.Shape=shape; groups[group].addObject(ob)
        ob.ViewObject.ShapeColor=color; ob.ViewObject.Transparency=alpha; ob.ViewObject.Visibility=visible
        return ob
    gl=ns['glob']
    printed=[]
    for name,s,col in [('Mount_Tray',ns['tray'],(.22,.26,.31)),('Screw_Cover',ns['lid'],(.95,.49,.13))]:
        ob=add(name,pose(gl(s)),'PrintedParts',col); printed.append(ob)
        ob.addProperty('App::PropertyString','ReviewStatus'); ob.ReviewStatus='CAD review draft; physical harness fit unverified'
    add('ESP32_CAM_measured_reference',pose(gl(ns['board_comp'])),'BoardAndWiring',(.1,.5,.24))
    for i,d in enumerate(ns['dups']): add('Dupont_%02d'%i,pose(gl(d)),'BoardAndWiring',(.16,.16,.16),False)
    for i,w in enumerate(ns['wire_shapes']): add('Wire_route_%02d'%i,pose(gl(w)),'BoardAndWiring',(.8,.15,.1),False)
    for i,s in enumerate(ns['hardware']): add('M3x12_screw_%d'%i,pose(gl(s)),'Fasteners',(.72,.72,.76))
    for i,(x,z) in enumerate(ns['ears']):
        rr=5.5/math.sqrt(3); yy=ns['NUT_Y']+.1
        vv=[A.Vector(x+rr*math.cos(math.radians(30+60*k)),yy,z+rr*math.sin(math.radians(30+60*k))) for k in range(6)]
        nut=Part.Face(Part.makePolygon(vv+[vv[0]])).extrude(A.Vector(0,2.4,0))
        nut=nut.cut(ns['cy'](1.5,yy-.1,yy+2.5,x,z))
        add('M3_nut_%d'%i,pose(gl(nut)),'Fasteners',(.72,.72,.76))
    for n in ('GH44_Dual_Carrier','ToF_Sensor_Frame','Dual_ToF_Envelope','Rear_Display_Frame','GH44_Tilt_Receiver'):
        add(n,pose(ns['G'][n]),'HeadContext',(.45,.53,.6),n in ('GH44_Dual_Carrier','ToF_Sensor_Frame'),65)
    doc.recompute()
    direction=A.Vector(1,1,.75)
    right=A.Vector(0,0,1).cross(direction)
    up=direction.cross(right)
    Gui.activeDocument().activeView().setCameraOrientation(A.Rotation(right,up,direction,'ZXY').Q)
    Gui.activeDocument().activeView().fitAll()
    doc.saveAs(str(OUT/'Gladiator_Camera_Service_v2_REVIEW.FCStd'))
    Import.export(printed,str(OUT/'Gladiator_Camera_Service_v2.step'))
    Gui.activeDocument().activeView().saveImage(str(OUT/'assembled.png'),1600,1200,'White')
    for ob in groups['HeadContext'].Group+groups['Fasteners'].Group: ob.ViewObject.Visibility=False
    printed[1].Placement.Base += A.Vector(0,40,0)
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()
    Gui.activeDocument().activeView().saveImage(str(OUT/'exploded.png'),1600,1200,'White')
    doc.saveAs(str(OUT/'Gladiator_Camera_Service_v2_EXPLODED.FCStd'))
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*') if p.is_file()}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print('SERVICE_V2_COMPLETE',str(OUT),flush=True)
except Exception:
    (OUT/'error.txt').write_text(traceback.format_exc())
    traceback.print_exc()
    import sys; sys.stdout.flush(); sys.stderr.flush()
    os._exit(1)
import sys; sys.stdout.flush(); sys.stderr.flush()
os._exit(0)

