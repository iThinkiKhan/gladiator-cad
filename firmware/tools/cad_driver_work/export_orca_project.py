"""Try embedding the selected Orca profiles in the driver plate project."""
import subprocess
from pathlib import Path

home = Path('/home/buralien')
cache = home / '.cache/gladiator-driver-v5-slice-check'
incoming = home / '3D-Printer/Incoming'
source = incoming / 'Gladiator_PlateI_DRIVER-V5-INTERLOCK.3mf'
target = cache / 'Gladiator_PlateI_DRIVER-V5-INTERLOCK-Orca.3mf'
cmd = [
    'flatpak', 'run', '--command=entrypoint', 'com.orcaslicer.OrcaSlicer',
    '--debug', '4', '--logfile', str(cache / 'export-project.debug.log'),
    '--load-settings', ';'.join(str(cache / n) for n in
                                ('EnderNeo-slice-only.json', 'Driver-v5-slice-only.json')),
    '--load-filaments', str(cache / 'PLA-slice-only.json'),
    '--export-3mf', str(target), str(source),
]
run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     text=True, timeout=180)
print('exit', run.returncode, 'output', run.stdout[-1000:])
print('target_exists', target.exists(), 'target_bytes', target.stat().st_size if target.exists() else 0)
