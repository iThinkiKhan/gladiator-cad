"""Load the captured v04 geometry without exporting or overwriting any existing CAD."""
import json
from pathlib import Path

root = Path('/home/buralien/projects/gladiator-cad')
out = root / 'cad/head/review-20261005'
source = (out / 'build_head_v04_source.py').read_text(encoding='utf-8-sig')
source = source.replace("OUT = ROOT / 'cad/head/v04-pan-stack'", "OUT = ROOT / 'cad/head/review-20261005/baseline'")
exec(compile(source.split('# ================================================================== collision sweeps')[0], 'captured_v04', 'exec'))

roof_x = TS_X0 - (rim_l + POCKET_DEPTH + BOSS_RECESS + ROOF_T)
roof = cx(2.0, roof_x, ROOF_T, T.y, TZ).cut(cx(CENTRE_HOLE/2, roof_x-.1, ROOF_T+.2, T.y, TZ))
seat = parts['GH44_Tilt_Receiver']['shape'].common(roof)
result = {'tilt_roof_x': roof_x, 'nominal_roof_thickness': ROOF_T,
          'screw_head_assumed_diameter': 4.0,
          'expected_screw_bearing_volume_mm3': roof.Volume,
          'actual_screw_bearing_volume_mm3': seat.Volume,
          'horn_arm_top_above_ear': HORN_TOP-BOSS_UP,
          'pan_servo_ear_real_z': ZP+LIFT,
          'single_solids': {n: p['shape'].isValid() and len(p['shape'].Solids)==1 for n,p in parts.items()}}
(out / 'baseline-audit.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))

