"""Headless OrcaSlicer check of the queued driver v5 coupon and plate."""
import json
import subprocess
from pathlib import Path

home = Path('/home/buralien')
repo = home / 'projects/gladiator-cad'
incoming = home / '3D-Printer/Incoming'
profiles = home / '.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer/user/default'
out = home / '.cache/gladiator-driver-v5-slice-check'
out.mkdir(exist_ok=True)

machine = json.loads((profiles / 'machine/EnderNeo.json').read_text())
machine.pop('printhost_apikey', None)
machine.pop('print_host', None)
machine['type'] = 'machine'
machine_path = out / 'EnderNeo-slice-only.json'
machine_path.write_text(json.dumps(machine))
process = json.loads((profiles / 'process/0.20mm Standard @ First Print.json').read_text())
override = json.loads((repo / 'cad/drivers/v5-interlock/orca-v5-process.json').read_text())
override.pop('inherits', None)
process.update(override)
process['type'] = 'process'
process['compatible_printers'] = ['EnderNeo']
process_path = out / 'Driver-v5-slice-only.json'
process_path.write_text(json.dumps(process))
filament = json.loads((profiles / 'filament/Generic PLA @System - First Print.json').read_text())
filament['type'] = 'filament'
filament_path = out / 'PLA-slice-only.json'
filament_path.write_text(json.dumps(filament))

results = []
for name in ('Gladiator_DriverV5_INTERLOCK-FIT-COUPON.3mf',
             'Gladiator_PlateI_DRIVER-V5-INTERLOCK.3mf'):
    path = incoming / name
    cmd = [
        'flatpak', 'run', '--command=entrypoint', 'com.orcaslicer.OrcaSlicer',
        '--debug', '4', '--logfile', str(out / (path.stem + '.debug.log')),
        '--load-settings', ';'.join(map(str, (machine_path, process_path))),
        '--load-filaments', str(filament_path),
        '--slice', '0', '--outputdir', str(out), str(path),
    ]
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, timeout=240)
    log = out / (path.stem + '.log')
    log.write_text(run.stdout)
    results.append({'file': name, 'exit_code': run.returncode,
                    'log': str(log), 'log_tail': run.stdout[-700:]})
    if run.returncode:
        break

results_path = out / 'summary.json'
results_path.write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
raise SystemExit(0 if len(results) == 2 and all(r['exit_code'] == 0 for r in results) else 1)
