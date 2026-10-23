import sys, glob
sys.path.insert(0, '/home/buralien/scratch_claude')
from jimflat import preset_values
FMT = ('machine_max_', '_gcode', 'extruder_colour', 'compatible_printers', 'print_host', 'printhost_apikey', 'post_process')
def norm(v):
    if isinstance(v, list): v = ','.join(str(x) for x in v)
    return str(v).replace('\n', '\n').replace('"', '').strip()
for g in sorted(glob.glob(sys.argv[1])):
    cfg = {}; on = False
    for l in open(g, errors='ignore'):
        l = l.rstrip('\r\n')
        if 'CONFIG_BLOCK_START' in l: on = True; continue
        if 'CONFIG_BLOCK_END' in l: break
        if on and l.startswith('; ') and ' = ' in l:
            k, v = l[2:].split(' = ', 1); cfg[k] = v
    silk = 'Silk' in cfg.get('print_settings_id', '')
    pv = preset_values(*(('0.20mm Silk Toys @ First Print - SAFE', 'Generic PLA Silk @System - First Print') if silk else ('0.20mm Standard - FIrst Layer Comp', 'Generic PLA @System - First Print')))
    diffs = []
    for k, v in sorted(pv.items()):
        if k.startswith(FMT) or k.endswith(FMT) or k not in cfg: continue
        a, b = norm(v), cfg[k].replace('"', '').strip()
        if a != b:
            try:
                if abs(float(a.rstrip('%')) - float(b.rstrip('%'))) < 1e-9: continue
            except ValueError: pass
            diffs.append('%s: preset %s -> gcode %s' % (k, a[:30], b[:30]))
    # gcode-valued keys compared after unescaping
    for k in ('machine_start_gcode', 'machine_end_gcode', 'layer_change_gcode', 'before_layer_change_gcode'):
        if k not in pv: continue
        want = (','.join(pv[k]) if isinstance(pv[k], list) else pv[k]).strip()
        got = cfg.get(k, '').strip().strip('"').replace('\\n', '\n').strip()
        if want != got: diffs.append(k + ' DIFFERS')
    print(g.split('/')[-1], '| process', cfg.get('print_settings_id'), '| filament', cfg.get('filament_settings_id'), '| layer', cfg.get('layer_height'), 'first', cfg.get('initial_layer_print_height'))
    print('   differences from Jim presets:', diffs or 'none', '(prime tower is switched off automatically for single-filament jobs)')
