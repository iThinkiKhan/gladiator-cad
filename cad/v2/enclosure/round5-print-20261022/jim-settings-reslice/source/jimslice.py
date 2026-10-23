"""Re-slice the GLAD jobs with Jim's own Orca presets (Claude 2026-10-22).
Every preset key in each 3MF's project settings is replaced by Jim's flattened preset value (EnderNeo SAFE + his process + his filament).
Only intentional change: supports switched on for parts that need them (his own support values, tree(auto)).
Per-object brim overrides removed so his brim applies. Parts, positions and support blockers unchanged.
post_process is blank only for the CLI slice; the SAFE guard is run on every output and kept in the delivered 3MF."""
import json, re, shutil, subprocess, sys, zipfile
from pathlib import Path
sys.path.insert(0, str(Path.home() / 'scratch_claude'))
from jimflat import preset_values
W = Path.home() / 'scratch_claude/jimslice'
INC = Path.home() / '3D-Printer/Incoming/Gladiator'
CAD = Path.home() / 'projects/gladiator-cad/cad/v2/enclosure'
JOBS = {
 '01': ('GLAD_01_WHITE_EMBLEMS_V2', CAD / 'round5-print-20261022/emblem-v2/R5_04B_White_Shield_Emblems_v2_STRONGER.3mf', 'std', True, None),
 '02': ('GLAD_02_SILK_DETAILS', CAD / 'round5-calibrated-28-20261022/print/plates/R5_06_Silk_Aquila_and_Trim.3mf', 'silk', True, None),
 '03': ('GLAD_03_BLACK_CLAMPS', CAD / 'round5-calibrated-28-20261022/print/plates/R5_02_Black_Clamps.3mf', 'std', False, None),
 '04': ('GLAD_04_HOOD_SD', INC / 'Round5_MOUNT_CHECKED_20261022/plates/GLAD_04_HOOD_SD_M2_28.3mf', 'std', True, '07'),
 '05': ('GLAD_05_PANELS_SD', INC / 'Round5_MOUNT_CHECKED_20261022/plates/GLAD_05_PANELS_SD_M2_28.3mf', 'std', True, '08'),
}
PRE = {'std': ('0.20mm Standard - FIrst Layer Comp', 'Generic PLA @System - First Print'),
       'silk': ('0.20mm Silk Toys @ First Print - SAFE', 'Generic PLA Silk @System - First Print')}
SD = str(INC / 'Round5_CALIBRATED_M2_28_20261022/source/postprocess_sd_colours.py')
GUARD = '/usr/bin/python3 /home/buralien/bin/check-ender3-start.py'
def settings(ps, kind, sup, cli):
    proc, fil = PRE[kind]
    pv = preset_values(proc, fil)
    for k, v in pv.items():
        if k in ('compatible_printers', 'compatible_printers_condition', 'print_host', 'printhost_apikey'): continue
        old = ps.get(k)
        if isinstance(old, list):
            v = v if isinstance(v, list) else [v]
            if len(old) > 1 and len(v) == 1: v = v * len(old)
        elif isinstance(v, list) and old is not None:
            v = ','.join(v) if k not in ('post_process',) else v
        ps[k] = v
    ps['enable_support'] = '1' if sup else '0'
    ps['input_shaping_type'] = 'Default'
    ps['print_settings_id'] = proc; ps['filament_settings_id'] = [fil] * max(1, len(ps.get('filament_settings_id', [1])) if isinstance(ps.get('filament_settings_id'), list) else 1)
    ps['printer_settings_id'] = 'EnderNeo SAFE'
    ps['post_process'] = [] if cli else [GUARD]
    return ps
def build3mf(src, dst, kind, sup, cli):
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            b = zi.read(it.filename)
            if it.filename == 'Metadata/model_settings.config':
                b = re.sub(rb'\s*<metadata key="brim_(type|width)" value="[^"]*"\s*/>', b'', b)
            if it.filename == 'Metadata/project_settings.config':
                b = json.dumps(settings(json.loads(b), kind, sup, cli), indent=4).encode()
            zo.writestr(it, b)
for key in sys.argv[1:]:
    name, src, kind, sup, sd = JOBS[key]
    d = W / key; shutil.rmtree(d, ignore_errors=True); (d / 'out').mkdir(parents=True)
    build3mf(src, d / (name + '_JIM.3mf'), kind, sup, False)
    cli3 = d / 'cli.3mf'; build3mf(src, cli3, kind, sup, True)
    cmd = ['flatpak', 'run', '--filesystem=' + str(Path.home()), 'com.orcaslicer.OrcaSlicer', '--slice', '1', '--orient', '0', '--arrange', '0',
           '--outputdir', str(d / 'out'), str(cli3)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3000)
    (d / 'slice.log').write_text(r.stdout + r.stderr)
    gs = list((d / 'out').glob('*.gcode'))
    if not gs:
        print(key, 'SLICE FAILED rc', r.returncode, (r.stdout + r.stderr)[-800:], flush=True); continue
    g = d / (name + '_JIM.gcode'); shutil.move(str(gs[0]), g)
    guard = subprocess.run(GUARD.split() + [str(g)], capture_output=True, text=True).stdout.strip().splitlines()[-1]
    if sd:
        subprocess.run(['python3', SD, '--plate', sd, str(g)], check=True)
    txt = g.read_text(errors='ignore')
    t = re.search(r'estimated printing time \(normal mode\) = (.*)', txt)
    print(key, name, '|', guard, '| time', t.group(1) if t else '?', '| %.1f MB' % (g.stat().st_size / 1e6), '| M0 pauses', txt.count('\nM0 '), flush=True)
