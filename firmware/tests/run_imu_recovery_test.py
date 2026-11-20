from pathlib import Path
import os,subprocess,shutil
r=Path(__file__).resolve().parents[1];out=r/'build-output/imu-host';out.mkdir(parents=True,exist_ok=True)
cc=Path(r'C:\Users\jimsc\.platformio\packages\toolchain-gccmingw32\bin\g++.exe');env=os.environ.copy();env['PATH']=str(cc.parent)+os.pathsep+env['PATH']
lib=r/'.pio/libdeps/gladiator_s3/Adafruit BNO08x/src';test=r/'tests/imu_recovery_test.cpp'
def build(header,source,label):
 shutil.copy2(header,out/'BNO085Sensor.h');shutil.copy2(source,out/'BNO085Sensor.cpp')
 exe=out/(label+'.exe');subprocess.run([str(cc),'-std=c++17','-I',str(out),'-I',str(r/'tests/imu_mocks'),'-I',str(r/'src/sensors'),'-I',str(lib),str(test),str(out/'BNO085Sensor.cpp'),'-o',str(exe)],check=True,env=env);return exe
old=r/'diagnostics/s3-imu-recovery-20261023/before/src/sensors'
exe=build(old/'BNO085Sensor.h',r/'diagnostics/s3-camera-errors-20261023/before/BNO085Sensor.cpp','original');p=subprocess.run([str(exe)],env=env,capture_output=True,timeout=3);assert p.returncode!=0,'Original driver unexpectedly passed';print('Reproduced original driver failure: configuration continues after a failed report.',flush=True)
exe=build(r/'src/sensors/BNO085Sensor.h',r/'src/sensors/BNO085Sensor.cpp','fixed');subprocess.run([str(exe)],check=True,env=env,timeout=3)
