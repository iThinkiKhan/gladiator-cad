"""Finish assembly access after the first geometric mount build."""
from pathlib import Path
root=Path('/home/buralien/projects/gladiator-cad')
p=root/'scripts/build_head_v05.py'
s=p.read_text()
(root/'cad/head/integration-20261005/v05-before-access-refinement.py').write_text(s)

def replace(a,b):
    global s
    assert s.count(a)==1,(a[:100],s.count(a))
    s=s.replace(a,b)

replace('RAD_ATTACH = [(37.5, 8.0), (37.5, -8.0), (24.0, 17.5)]',
        'RAD_ATTACH = [(37.5, 8.0), (37.5, -8.0), (24.5, 12.0)]')
replace("    body = body.removeSplitter()\n    addp(name,body",'''    # Preserve a 5 mm screwdriver passage to the four display screws.
    # This trims only a crescent of the radar nut feet, leaving >1 mm to their pockets.
    for sx in (-32,32):
        for sz in (-18,18):
            body = body.cut(cy(2.5,seat-.1,-58-seat+.2,sx,TZ+sz))
    body = body.removeSplitter()
    addp(name,body''')
replace("report['checks']['sensor_mounts_pass'] = True",'''report['checks']['sensor_mounts_pass'] = True
# Verify screw access in the assembly order, with the rest of the head assembled.
# ToF adapter must be fitted before carrier. Radar adapter fits afterward from rear.
access_checks = {}
def access_probe(label, probe, omitted):
    bad = {n: p['shape'].common(probe).Volume for n,p in parts.items()
           if n not in omitted and p['shape'].BoundBox.intersect(probe.BoundBox)}
    bad = {n:v for n,v in bad.items() if v>1e-6}
    access_checks[label] = bad
    assert not bad,(label,bad)
for x,dz in RAD_ATTACH:
    access_probe('radar rear M2 %.1f %.1f'%(x,dz),cy(2.4,-54.95,85,x,TZ+dz),
                 {'Rear_Display_Frame','ST7789_Board'})
for x in (-16,16):
    for dz in (-16,16):
        access_probe('GH44 before radar %.1f %.1f'%(x,dz),cy(3.5,-140,81.8,x,TZ+dz),
                     {'Radar_Sensor_Frame','Dual_ToF_Envelope','Dual_Radar_Envelope'})
for x in (-32,32):
    for dz in (-18,18):
        access_probe('display M2 before PCBs %.1f %.1f'%(x,dz),cy(2.4,-140,81.8,x,TZ+dz),
                     {'Dual_ToF_Envelope','Dual_Radar_Envelope'})
report['sensor_mounts']['assembly_tool_access_blockers'] = access_checks
report['sensor_mounts']['assembly_order'] = [
    'Fit nuts and attach ToF frame to carrier with 3 M2 x6 from rear, before carrier installation.',
    'Attach carrier to receiver with 4 M3, with radar frame and both PCBs still absent.',
    'Fit nuts and attach radar frame with 3 M2 x6 from rear, before display frame installation.',
    'Attach rear display frame with 4 M2 from front, using a driver shaft no more than4.8 mm diameter.',
    'Attach PCBs last with 8 M3 x16. Fit connector leads and check unpowered complete motion.']
''')
# PCB screw-head positions and their clear component-free lands are covered by the board model.
# Check the conservative radar cone as well as the ToF one, including the adjacent sensor.
marker="report['checks']['all_parts_single_valid_solid'] ="
radar='''# Radar geometric field reservation: whole-board near plane, nominal100 x80 degrees.
# Physical RF/antenna performance cannot be established by a solid-clearance check.
RAD_FRONT_Y = RAD_SEAT-1.6-8.0
radar_fov = Part.makeLoft([rect_wire(RAD_FRONT_Y,RAD_X,11,15),
                         rect_wire(RAD_FRONT_Y-150,RAD_X,11+150*math.tan(math.radians(50)),
                                   15+150*math.tan(math.radians(40)))],True)
radar_fov_hits=[]
for pan in PAN_SAMPLES:
    for tilt in TILTS:
        f=radar_fov.copy(); f.rotate(T,A.Vector(1,0,0),tilt); f.rotate(A.Vector(),A.Vector(0,0,1),pan)
        for n,shape in robot:
            v=overlap(f,shape)
            if v>.05: radar_fov_hits.append({'pan':pan,'tilt':tilt,'object':n,'mm3':v})
        for item in plist:
            if item['name']=='Dual_Radar_Envelope':continue
            v=overlap(f,posed(item,pan,tilt))
            if v>.05:radar_fov_hits.append({'pan':pan,'tilt':tilt,'object':item['name'],'mm3':v})
report['radar_fov_reservation']={'full_angle_degrees':[100,80],'near_plane_mm':[22,30],
                                  'length_mm':150,'front_y_mm':RAD_FRONT_Y,'intersections':radar_fov_hits,
                                  'note':'whole-board geometric clearance reservation; no RF performance claim'}

'''
assert s.count(marker)==1
s=s.replace(marker,radar+marker)
replace("    and report['checks']['sensor_mounts_pass']","    and report['checks']['sensor_mounts_pass']\n    and not radar_fov_hits")
start=s.index('"""');end=s.index('"""',start+3)+3
s='''"""Gladiator head v0.5: corrected v04 mechanical head plus measured removable sensors.

42 x27.5 SEN0628; upright22 x30 C4001 with15 x23 corner-hole pitch.
Preserves the tested GH44 key and corrected tilt screw roof/passage.
Builds native CAD, STEP, print-oriented STL and assembly/motion evidence.
Source master is read only. Run with initialized FreeCAD Python on CAD server.
"""'''+s[end:]
p.write_text(s)
print('Refined assembly order, rear radar screws, display tool clearance and radar FOV checks')
