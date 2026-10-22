from pathlib import Path
root=Path('/home/buralien/projects/gladiator-cad')
s=(root/'cad/head/integration-20261005/diagnose_radar_clearance.py').read_text()
s=s.replace('range(0,9)','range(9,13)').replace('radar-forward-clearance.json','radar-forward-clearance-final.json')
exec(compile(s,'radar_offset_followup','exec'))
