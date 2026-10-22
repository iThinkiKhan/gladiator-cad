"""Preserve rejected candidate; advance radar10 mm to clear its reserved downward field."""
import shutil,json
from pathlib import Path
root=Path('/home/buralien/projects/gladiator-cad')
out=root/'cad/head/v05-sensor-mounts'
backup=root/'cad/head/integration-20261005/v05-before-radar-shift'
assert not backup.exists()
shutil.copytree(out,backup)
p=root/'scripts/build_head_v05.py'
shutil.copy2(p,backup/'build_head_v05.py')
s=p.read_text()
def replace(a,b):
    global s
    assert s.count(a)==1,(a[:100],s.count(a))
    s=s.replace(a,b)
replace('TOF_SEAT, RAD_SEAT = -75.0, -73.0  # 14 / 12 mm from adapter\'s front plane -61',
        'TOF_SEAT, RAD_SEAT = -75.0, -83.0  #14 /22 mm from adapter front plane -61; radar advanced10 for full downward field')
replace('    pts = [(center+x,z) for x,z in holes]',
        '    screw_length = 25 if name==\'Radar_Sensor_Frame\' else16\n    pts = [(center+x,z) for x,z in holes]'.replace('else16','else 16'))
replace("addp(name,body,'tilt','four M3 x16 PCB screws, 6 AF side-loaded nuts; three rear M2 x6 adapter screws','Tilt')",
        "addp(name,body,'tilt','four M3 x%d PCB screws,6 AF side-loaded nuts; three rear M2 x6 adapter screws'%screw_length,'Tilt')")
replace("'m3x16_tip_y_mm':seat-1.6+16,'minimum_carrier_tip_clearance_mm':-58-(seat-1.6+16)",
        "'pcb_screw_length_mm':screw_length,'screw_tip_y_mm':seat-1.6+screw_length,'minimum_carrier_tip_clearance_mm':-58-(seat-1.6+screw_length)")
replace("'center_x_mm':RAD_X,'rear_standoff_mm':12", "'center_x_mm':RAD_X,'rear_standoff_mm':22")
replace("'rear_component_to_nut_foot_mm':1", "'rear_component_to_nut_foot_mm':11")
replace("'pcb_mount_screws':'8 x M3 x16 with 8 M3 nuts; nominal length includes assumed 1.6 radar PCB; verify actual hardware'",
        "'pcb_mount_screws':'ToF4 x M3 x16; radar4 x M3 x25;8 M3 nuts. No washers assumed; verify actual hardware'")
replace("'Attach PCBs last with 8 M3 x16. Fit connector leads and check unpowered complete motion.'",
        "'Attach PCBs last: ToF4 x M3 x16, radar4 x M3 x25. Fit leads and check unpowered complete motion.'")
# These parts share exactly the same rigid transform as each cone: one relative pose suffices.
replace("            if p['name'] == 'Dual_ToF_Envelope':",
        "            if p['motion']=='tilt' and (pan!=0 or tilt!=0):continue\n            if p['name'] == 'Dual_ToF_Envelope':")
replace("            if item['name']=='Dual_Radar_Envelope':continue",
        "            if item['motion']=='tilt' and (pan!=0 or tilt!=0):continue\n            if item['name']=='Dual_Radar_Envelope':continue")
s=s.replace("report['radar_fov_reservation']={'full_angle_degrees'", "report['radar_fov_reservation']={'forward_adjustment_mm':10,'full_angle_degrees'")
p.write_text(s)
with (root/'measurements/mast-head.md').open('a') as f:
    f.write('''
### v05 radar field clearance correction — 2026-10-05

The first12 mm stand-off prototype cleared rigid parts but its conservative whole-board
100 x80 degree radar field reached S3Board/AntennaPost at25 degrees downward tilt.
Targeted forward shifts0..12 were checked:9 still intersects0.1293 mm3,10 clears all11
previously affected poses. The final radar PCB is advanced10 mm, giving **22 mm rear
stand-off** and **4 M3x25 radar screws** (ToF stays14 mm /4 M3x16). The radar clearance
to nut feet is now11 mm. These are design allowances, not new hardware measurements.
The whole field sweep and changed-part checks must pass before release. Initial failed
candidate is preserved in cad/head/integration-20261005/v05-before-radar-shift/.
''')
print('Radar advanced10 mm; stand-off22; nominal radar screws M3x25')
