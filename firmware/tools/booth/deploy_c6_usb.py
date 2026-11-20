"""Guarded app-only recovery update for Jim's exact C6 over existing WinUSB.
Requires the separately captured full backup. Never writes bootloader, NVS,
partition table, OTA selection data, eFuses, or the other application slot.
"""
from pathlib import Path
import argparse,hashlib,json,sys,subprocess,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path.home()/'.platformio/packages/tool-esptoolpy'))
from winusb_c6 import WinUsbC6
from esptool.cmds import detect_chip
from esptool.reset import HardReset
p=argparse.ArgumentParser();p.add_argument('--expect-sha256',required=True);a=p.parse_args()
out=ROOT/'diagnostics/operator-20261023/usb-recovery';backup=(out/'c6-before-241-full-flash.bin').read_bytes();record=json.loads((out/'backup.json').read_text())
assert len(backup)==0x400000 and hashlib.sha256(backup).hexdigest()==record['sha256'] and record['appOffset']==0x20000 and record['activeAppVerified']=='gateway-2.4.0'
check=json.loads(subprocess.check_output([sys.executable,str(ROOT/'tools/booth/deploy_c6.py'),'--check-only'],text=True));assert check['candidate']=='gateway-2.4.3' and check['sha256']==a.expect_sha256
image=(ROOT/'gateway/.pio/build/gladiator_c6/firmware.bin').read_bytes();assert hashlib.sha256(image).hexdigest()==a.expect_sha256 and len(image)<0x1e0000
old=(ROOT/'diagnostics/operator-20261023/release/gateway-2.4.2-candidate.bin').read_bytes();assert hashlib.sha256(old).hexdigest()=='6b06162e912ec343e7c76f640be7c843917e1afde4bcc75e0eb75b1f7a67fc6b'
original=(ROOT/'diagnostics/operator-20261023/release/gateway-2.4.0-candidate.bin').read_bytes();assert backup[0x20000:0x20000+len(original)]==original
with WinUsbC6() as port:
 port.timeout=1;preflight={}
 for command in ['status','saved','field']:
  port.write((command+'\n').encode());text=port.read(10000).decode('utf-8','replace')
  for pos,ch in enumerate(text):
   if ch!='{':continue
   try:d,_=json.JSONDecoder().raw_decode(text[pos:])
   except ValueError:continue
   if isinstance(d,dict) and ((command=='status' and d.get('role')=='network-gateway') or (command=='saved' and 'fields' in d and d.get('schema')==1) or (command=='field' and 'controller' in d)):preflight[command]=d;break
 assert len(preflight)==3 and preflight['status']['firmware']=='gateway-2.4.2','Read current USB status/setup before recovery'
 controller=preflight['field']['controller'];mast=preflight['field']['mast'];assert not controller['armed'] and not controller['deadman'] and controller['leftPercent']==controller['rightPercent']==0 and not mast['enabled'] and not mast['testActive'],'All outputs must be off'
 (out/'pre242-logical.json').write_text(json.dumps(preflight,indent=2))
 try:
  chip=detect_chip(port=port,connect_mode='usb_reset',connect_attempts=2);mac=':'.join(f'{x:02x}' for x in chip.read_mac());assert chip.CHIP_NAME=='ESP32-C6' and mac=='f0:f5:bd:2d:07:ec'
  stub=chip.run_stub();stub.flash_spi_attach(0);assert stub.flash_id()>>16==0x16
  prefix=stub.read_flash(0,0x20000)
  assert prefix[:0x9000]==backup[:0x9000] and prefix[0xf000:]==backup[0xf000:0x20000],'Boot/partitions/OTA selection changed; inspect before writing'
  prefixHash=hashlib.sha256(prefix).hexdigest();(out/('prefix-before-242-'+prefixHash[:12]+'.bin')).write_bytes(prefix)
  assert stub.flash_md5sum(0x20000,len(old))==hashlib.md5(old).hexdigest(),'Running app region changed since backup'
  print('Verified exact device, backup and unchanged boot/calibration storage. Writing app0 only.',flush=True)
  stub.FLASH_WRITE_SIZE=1024
  count=stub.flash_begin(len(image),0x20000)
  for seq in range(count):
   chunk=image[seq*stub.FLASH_WRITE_SIZE:(seq+1)*stub.FLASH_WRITE_SIZE];stub.flash_block(chunk.ljust(stub.FLASH_WRITE_SIZE,b'\xff'),seq)
   if seq%200==0:print('Application progress',round((seq+1)*100/count),'%',flush=True)
  stub.flash_finish(reboot=False)
  (out/'application-write-attempt.json').write_text(json.dumps({'candidate':check['candidate'],'sha256':check['sha256'],'appOffset':0x20000,'writeCompleted':True,'verificationPending':True},indent=2))
  assert stub.flash_md5sum(0x20000,len(image))==hashlib.md5(image).hexdigest(),'Application verification failed; retain recovery backup'
  assert stub.read_flash(0,0x20000)==prefix,'Current boot/NVS/OTA selection unexpectedly changed'
  assert stub.flash_md5sum(0x200000,0x200000)==hashlib.md5(backup[0x200000:]).hexdigest(),'Other application slot unexpectedly changed'
  receipt={'candidate':check['candidate'],'sha256':check['sha256'],'bytes':len(image),'mac':mac,'appOffset':0x20000,'imageReadbackVerified':True,'bootAndNvsByteIdentical':True,'otherAppHashIdentical':True,'backupSha256':record['sha256'],'currentPrefixSha256':prefixHash,'savedSetupBefore':preflight['saved'],'s3BootIdBefore':preflight['status']['peerBootId'],'runtimeVerified':False,'motionCommands':0,'s3FirmwareChanged':False}
  (out/'app-write-verified.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
 finally:HardReset(port,uses_usb=True)()
print('C6 restarted. Read runtime status before claiming installation complete.')
