from pathlib import Path
import os,subprocess,runpy
r=Path(__file__).resolve().parents[1];d=r/'.pio/libdeps/gladiator_s3/Adafruit BNO08x/src';host=r/'build-output/host';host.mkdir(parents=True,exist_ok=True)
cc=Path(r'C:\Users\jimsc\.platformio\packages\toolchain-gccmingw32\bin\gcc.exe');env=os.environ.copy();env['PATH']=str(cc.parent)+os.pathsep+env['PATH']
source=(d/'sh2.c').read_text(encoding='utf-8');exe=host/'sh2_timeout_test.exe'
def build(text):
 (host/'sh2.c').write_text(text,encoding='utf-8')
 subprocess.run([str(cc),'-std=c99','-I',str(d),str(r/'tests/sh2_timeout_test.c'),str(d/'sh2_util.c'),'-lm','-o',str(exe)],check=True,env=env)
build(source)
try:subprocess.run([str(exe)],check=True,timeout=1,env=env);raise AssertionError('Original SH2 unexpectedly returned')
except subprocess.TimeoutExpired:print('Reproduced original SH2 hang on missing product reply.',flush=True)
build(runpy.run_path(str(r/'scripts/bounded_sh2.py'))['bounded_source'](source));subprocess.run([str(exe)],check=True,timeout=2,env=env)
