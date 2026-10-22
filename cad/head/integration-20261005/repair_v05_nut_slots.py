from pathlib import Path
root=Path('/home/buralien/projects/gladiator-cad')
p=root/'scripts/build_head_v05.py'
s=p.read_text()
old="        body = body.cut(box(x-5.2,-63.7,TZ+z-3,5.2,2.8,6))"
assert s.count(old)==1
s=s.replace(old,"        side = -1 if x<center else 1\n        body = body.cut(box(x-5.2 if side<0 else x,-63.7,TZ+z-3,5.2,2.8,6))")
s=s.replace("        for shift in (0,-1,-2,-3,-4,-5,-6,-7,-8,-9,-10):","        side = -1 if x<center else 1\n        for shift in [side*k for k in range(11)]:")
s=s.replace('from -X side; fit nuts before installing the adapters','from outboard side of each post; fit nuts before installing the adapters')
(root/'cad/head/integration-20261005/v05-nut-slots-before.py').write_text(p.read_text())
p.write_text(s)
print('Nut insertion slots point outboard to avoid the neighboring posts')
