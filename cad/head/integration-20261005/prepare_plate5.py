from pathlib import Path
ROOT=Path('/home/buralien/projects/gladiator-cad')
s=(ROOT/'scripts/build_head_v04_plates.py').read_text()
s=s.replace('v04-pan-stack','v05-sensor-mounts').replace('Gladiator_Head_v04_','Gladiator_Head_v05_')
s=s.replace('build_head_v04_plates.py','build_head_v05_plate5.py')
start=s.index('PLATES = {');end=s.index('\nvalidation = ',start)
s=s[:start]+'''PLATES = {
    'Gladiator_Head_v05_PLATE5_SensorCarrier-ToF-Radar.3mf':
        ['GH44_Dual_Carrier','ToF_Sensor_Frame','Radar_Sensor_Frame'],
}
(OUT / 'plates').mkdir(exist_ok=True)
'''+s[end:]
s=s.replace('plates-2-3-validation.json','plate5-validation.json')
start=s.index('"""');end=s.index('"""',start+3)+3
s='''"""Head v05 measured sensor mounts, geometry-only Plate5.
Run with freecadcmd; requires successful build_head_v05.py validation.
"""'''+s[end:]
target=ROOT/'scripts/build_head_v05_plate5.py'
assert not target.exists()
target.write_text(s)
print(target)
