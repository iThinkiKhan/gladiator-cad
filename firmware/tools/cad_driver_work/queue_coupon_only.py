"""Regenerate only the representative v5 driver joint coupon on cad-lab."""
from pathlib import Path

source = Path('/home/buralien/projects/gladiator-cad/scripts/build_drv_v5_plate.py')
code = source.read_text()
assert code.rstrip().endswith('main()')
code = code.rsplit('\nmain()', 1)[0]
scope = {'__name__': 'driver_coupon_only'}
exec(compile(code, str(source), 'exec'), scope)
app = scope['App']
doc = app.openDocument(scope['SOURCE'])
try:
    name, rows, used_x, used_y = scope['build_coupon'](doc)
    print(name, rows, used_x, used_y)
finally:
    app.closeDocument(doc.Name)
