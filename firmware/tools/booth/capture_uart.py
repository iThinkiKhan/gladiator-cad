"""Passive UART capture: does not transmit or assert DTR/RTS."""
import argparse,time,serial
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',required=True);p.add_argument('--baud',type=int,default=115200);p.add_argument('--seconds',type=int,default=1800);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.parent.mkdir(parents=True,exist_ok=True)
s=serial.Serial();s.port=a.port;s.baudrate=a.baud;s.timeout=.2;s.dtr=False;s.rts=False
count=0;tail=b''
with s,a.out.open('wb') as f:
 print('Passive recorder ready on '+a.port,flush=True);end=time.monotonic()+a.seconds
 while time.monotonic()<end:
  b=s.read(max(1,s.in_waiting))
  if not b:continue
  f.write(b);f.flush();count+=len(b);tail=(tail+b)[-4096:]
  if any(x in b.lower() for x in [b'panic',b'backtrace',b'guru',b'assert',b'watchdog']):print(b.decode('utf-8','replace')[:1000],flush=True)
print('Captured '+str(count)+' bytes.',flush=True)
