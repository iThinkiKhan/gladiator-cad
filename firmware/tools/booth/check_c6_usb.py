"""Read-only USB diagnostics via this C6's existing WinUSB driver. No resets."""
from pathlib import Path
import argparse,json
from winusb_c6 import WinUsbC6
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--expect-version');a=p.parse_args();assert a.out.resolve().is_relative_to(ROOT.resolve()),'Keep device diagnostics in the canonical project'
results={}
with WinUsbC6() as port:
 port.timeout=1
 for command in ['status','saved','field']:
  port.write((command+'\n').encode());text=port.read(12000).decode('utf-8','replace');matches=[]
  for pos,ch in enumerate(text):
   if ch!='{':continue
   try:d,_=json.JSONDecoder().raw_decode(text[pos:])
   except ValueError:continue
   if isinstance(d,dict) and ((command=='status' and d.get('role')=='network-gateway') or (command=='saved' and d.get('schema')==1 and 'fields' in d) or (command=='field' and 'controller' in d)):matches.append(d)
  assert len(matches)==1,f'Incomplete USB {command} reply';results[command]=matches[0]
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(results,indent=2),encoding='utf-8')
s=results['status'];f=results['field'];saved=results['saved'];c=f['controller'];m=f['mast']
if a.expect_version:assert s['firmware']==a.expect_version
outputsOff=not c['armed'] and not c['deadman'] and c['leftPercent']==c['rightPercent']==0 and not m['enabled'] and not m['testActive']
print(json.dumps({'firmware':s['firmware'],'bootId':s['bootId'],'s3BootId':s['peerBootId'],'robotConnected':s['robotConnected'],'wifiConfigured':s['wifiConfigured'],'wifiConnected':s['wifiConnected'],'wifiSsid':s['wifiSsid'],'ip':s['ip'],'disconnectReason':s['disconnectReason'],'savedRevision':saved['revision'],'savedFields':saved['fields'],'outputsOff':outputsOff,'batteryLockout':c['batteryLockout'],'freeHeap':s['freeHeap'],'previousFailedAllocationBytes':s['previousFailedAllocationBytes'],'motionCommands':0}))
