"""Exercise finite recovery-radio leases with all motion outputs kept OFF."""
import json,time,urllib.request,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--host',required=True);p.add_argument('--cycles',type=int,default=3);a=p.parse_args();assert a.host=='172.23.44.190' and 1<=a.cycles<=3
op=urllib.request.build_opener(urllib.request.ProxyHandler({}));key=json.loads((ROOT/'diagnostics/gateway-private/credentials.json').read_text())['adminKey'];rows=[]
def api(path,body=None):
 req=urllib.request.Request('http://'+a.host+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json','X-Gladiator-Key':key} if body is not None else {})
 with op.open(req,timeout=5) as r:return json.load(r)
def sample(cycle):
 s=api('/api/status');f=api('/api/field');m=f['sensors']['mast'];robot=api('/api/robot');crowd=api('/api/crowd')
 assert s['bootId']==baseline['bootId'] and s['peerBootId']==baseline['peerBootId'],'Controller reset during recovery test'
 c=f['controller'];assert not c['armed'] and not c['deadman'] and c['leftPercent']==c['rightPercent']==0 and not c['batteryLockout']
 if f['powerValid']:assert f['volts']>14
 assert not m['enabled'] and not m['testActive'] and not m['gpio10OutputEnabled'] and not m['gpio13OutputEnabled']
 assert robot.get('gateway') and robot.get('robot') and robot.get('native') and robot.get('system'),'Diagnostics returned incomplete JSON'
 sys=robot['system'];assert 'Mast operator v6 / radio dwell / bounded IMU' in sys['firmware'] and sys['resetReason']!='PANIC'
 row=dict(cycle=cycle,at=time.time(),s3Ms=c['s3Ms'],peer=s['peerBootId'],boot=s['bootId'],volts=f['volts'],heap=s['freeHeap'],minHeap=s['minimumFreeHeap'],frameErrors=s['frameErrors'],drops=s['drops'],detailErrors=s['detailErrors'],connected=f['connected'],powerValid=f['powerValid'],telemetryAgeMs=f['telemetryAgeMs'],controllerState=c['state'],gridFresh=crowd['grid']['fresh'],gridAgeMs=crowd['grid']['ageMs'],apUp=sys['apUp'],systemAgeMs=robot['systemAgeMs'],leaseMs=s['wifiLeaseMs'],rssi=s['rssi'])
 rows.append(row);return row
baseline=api('/api/status');assert baseline['firmware'] in ('gateway-2.3.9','gateway-2.4.0','gateway-2.4.1','gateway-2.4.2','gateway-2.4.3')
api('/api/subscribe',dict(intervalMs=1000,leaseMs=60000));time.sleep(3)
try:
 sample(0)
 for cycle in range(1,a.cycles+1):
  api('/api/subscribe',dict(intervalMs=1000,leaseMs=60000));api('/api/link',dict(leaseMs=6000));print(json.dumps(dict(cycle=cycle,phase='6-second Wi-Fi lease requested; checking 15-second dwell')),flush=True)
  start=time.monotonic();observed=[]
  while time.monotonic()-start<23:
   observed.append(sample(cycle));time.sleep(1.5)
  assert any(x['apUp'] for x in observed),'Radio never observed ON'
  assert not observed[-1]['apUp'] and not observed[-1]['leaseMs'],'Radio did not settle OFF'
  assert observed[-1]['connected'] and observed[-1]['powerValid'] and observed[-1]['controllerState']=='SAFE','Fresh safe telemetry must recover after the transition'
  print(json.dumps(dict(cycle=cycle,stable=True,radioOnThenOff=True,volts=observed[-1]['volts'],gridFresh=observed[-1]['gridFresh'])),flush=True)
 assert all(any(x['gridFresh'] for x in rows if x['cycle']==cycle) for cycle in range(1,a.cycles+1))
 print('PASS recovery cycles: both boot IDs unchanged; outputs OFF; live grid and full diagnostics intact',flush=True)
finally:
 (ROOT/'diagnostics/booth-20261022/s3-canonical-merge/recovery-cycles.json').write_text(json.dumps(dict(baseline=baseline,samples=rows),indent=2),encoding='utf-8')
