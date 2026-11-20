"""Back up this exact C6 using its existing WinUSB driver. No flash writes."""
from pathlib import Path
import sys,json,hashlib,struct
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path.home()/'.platformio/packages/tool-esptoolpy'))
from winusb_c6 import WinUsbC6
from esptool.cmds import detect_chip
from esptool.reset import HardReset
out=ROOT/'diagnostics/operator-20261023/usb-recovery';out.mkdir(exist_ok=True)
assert not (out/'c6-before-241-full-flash.bin').exists(),'Recovery backup already exists; do not reset or replace it blindly'
with WinUsbC6() as port:
 try:
  chip=detect_chip(port=port,connect_mode='usb_reset',connect_attempts=2)
  mac=':'.join(f'{x:02x}' for x in chip.read_mac());assert chip.CHIP_NAME=='ESP32-C6' and mac=='f0:f5:bd:2d:07:ec'
  stub=chip.run_stub();stub.flash_spi_attach(0);flash_id=stub.flash_id();assert flash_id>>16==0x16,f'Expected 4 MiB flash, got {flash_id:#x}'
  flash=stub.read_flash(0,0x400000);assert len(flash)==0x400000
  partitions={}
  for offset in range(0x8000,0x9000,32):
   magic,kind,subtype,base,size,label,flags=struct.unpack('<HBBII16sI',flash[offset:offset+32])
   if magic!=0x50aa:break
   partitions[label.split(b'\0')[0].decode()]={'type':kind,'subtype':subtype,'offset':base,'size':size}
  expected={'nvs':(0x9000,0x6000),'otadata':(0xf000,0x2000),'ota_0':(0x20000,0x1e0000),'ota_1':(0x200000,0x1e0000)}
  assert all((partitions[n]['offset'],partitions[n]['size'])==values for n,values in expected.items()),'Unexpected partition layout'
  installed=(ROOT/'diagnostics/operator-20261023/release/gateway-2.4.0-candidate.bin').read_bytes();assert hashlib.sha256(installed).hexdigest()=='0cb89c8b2026b49207667cf8ea99a1aada0bd3ff6b5ea21b5a154ee4a7409453'
  assert flash[0x20000:0x20000+len(installed)]==installed,'App0 differs from verified installed image'
  backup=out/'c6-before-241-full-flash.bin';assert not backup.exists(),'A recovery backup already exists; inspect before replacing it';backup.write_bytes(flash)
  receipt={'mac':mac,'flashId':hex(flash_id),'bytes':len(flash),'sha256':hashlib.sha256(flash).hexdigest(),'partitions':partitions,'activeAppVerified':'gateway-2.4.0','appOffset':0x20000,'flashWrites':0}
  (out/'backup.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
 finally:HardReset(port,uses_usb=True)()
print('Backup saved locally; existing C6 application restarted. No flash write.')
