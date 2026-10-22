import os, traceback
from pathlib import Path
p=Path('/home/buralien/projects/gladiator-cad/cad/head/camera-service-v2-20261021')
try:
    exec(compile((p/'verify_saved_v2.py').read_text(),str(p/'verify_saved_v2.py'),'exec'))
except Exception:
    (p/'verification-error.txt').write_text(traceback.format_exc())
    os._exit(1)
os._exit(0)

