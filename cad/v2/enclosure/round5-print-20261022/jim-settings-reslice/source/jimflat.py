"""Flatten Jim's Orca user presets through their exact system parents (Custom vendor for machine/process, OrcaFilamentLibrary for filament)."""
import json
from pathlib import Path
H = Path.home() / '.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer'
U = H / 'user/default'; S = H / 'system'
DIRS = {'machine': [U / 'machine', S / 'Custom/machine'], 'process': [U / 'process', S / 'Custom/process'],
        'filament': [U / 'filament', S / 'OrcaFilamentLibrary/filament', S / 'OrcaFilamentLibrary/filament/base']}
def find(kind, name):
    for d in DIRS[kind]:
        p = d / (name + '.json')
        if p.exists(): return p
    raise FileNotFoundError(kind + ':' + name)
def flat(kind, name, chain=None):
    p = find(kind, name); d = json.load(open(p))
    if chain is not None: chain.append(str(p))
    base = flat(kind, d['inherits'], chain) if d.get('inherits') else {}
    base.update({k: v for k, v in d.items() if k != 'inherits'}); return base
META = {'name', 'from', 'version', 'setting_id', 'instantiation', 'inherits', 'type', 'renamed_from', 'filament_id', 'is_custom_defined'}
def preset_values(proc, fil, chains=None):
    out = {}
    for kind, n in (('machine', 'EnderNeo SAFE'), ('process', proc), ('filament', fil)):
        c = []; v = flat(kind, n, c)
        if chains is not None: chains[kind] = c
        out.update({k: x for k, x in v.items() if k not in META})
    return out
if __name__ == '__main__':
    import sys
    ref = {}; on = False
    for l in open('/home/buralien/Desktop/3D-Printer-Outgoing/display2.gcode', errors='ignore'):
        l = l.rstrip('\r\n')
        if 'CONFIG_BLOCK_START' in l: on = True; continue
        if 'CONFIG_BLOCK_END' in l: break
        if on and l.startswith('; ') and ' = ' in l:
            k, v = l[2:].split(' = ', 1); ref[k] = v
    ch = {}
    pv = preset_values('0.20mm Standard - FIrst Layer Comp', 'Generic PLA @System - First Print', ch)
    print(json.dumps(ch, indent=1))
    def norm(v):
        if isinstance(v, list): v = ','.join(str(x) for x in v)
        return str(v).replace('\n', '\n').replace('"', '').strip()
    n = 0
    for k, v in sorted(pv.items()):
        if k in ref and norm(v) != ref[k].replace('"', '').strip():
            n += 1; print('DIFF %-40s preset=%-40s display2=%s' % (k, norm(v)[:40], ref[k][:40]))
    print('keys compared', sum(1 for k in pv if k in ref), 'diffs', n, '| preset keys not in gcode:', [k for k in pv if k not in ref][:30])
