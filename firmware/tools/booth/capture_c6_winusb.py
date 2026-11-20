"""C6 USB console capture; optional queries are read-only and never request credentials."""
import argparse,time
from pathlib import Path
from winusb_c6 import WinUsbC6
p=argparse.ArgumentParser();p.add_argument('--seconds',type=int,default=15);p.add_argument('--out',type=Path,required=True);p.add_argument('--command',choices=['status','saved','field']);a=p.parse_args();assert 1<=a.seconds<=600
a.out.parent.mkdir(parents=True,exist_ok=True);count=0
with WinUsbC6() as port,a.out.open('wb') as file:
 port.timeout=.2
 if a.command:port.write((a.command+'\n').encode());print('Read-only USB query:',a.command,flush=True)
 else:print('Passive USB capture ready; zero TX.',flush=True)
 end=time.monotonic()+a.seconds
 while time.monotonic()<end:
  data=port.read(4096)
  if data:file.write(data);file.flush();count+=len(data)
print('Captured',count,'bytes; private log saved.',flush=True)
