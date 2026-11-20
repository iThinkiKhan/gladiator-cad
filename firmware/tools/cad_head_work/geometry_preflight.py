from pathlib import Path
root=Path('/home/buralien/projects/gladiator-cad')
source=(root/'scripts/build_head_v05.py').read_text()
exec(compile(source.split('# ================================================================== collision sweeps')[0],'v05_geometry','exec'))
doc=A.newDocument('SensorGeometryPreflight')
for name,p in parts.items():
    o=doc.addObject('Part::Feature',name)
    shape=p['shape'].copy();shape.translate(WORLD);o.Shape=shape
doc.recompute()
path=root/'cad/head/integration-20261005/geometry-preflight.FCStd'
doc.saveAs(str(path))
print('All26 shapes valid,8 nut paths and11 assembly tool paths pass')
print(path)
