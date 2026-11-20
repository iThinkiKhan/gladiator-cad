"""Bounded GET-only gateway check, including the crowd feed and full diagnostics.
/api/crowd renews only a six-second sensor-detail lease. No actuator or setup POST.
"""
import argparse,ipaddress,json,statistics,time,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--host',required=True);p.add_argument('--seconds',type=int,default=60);p.add_argument('--out',type=Path,required=True);p.add_argument('--expect-version',default='gateway-2.4.3');a=p.parse_args();assert 15<=a.seconds<=180
address=ipaddress.ip_address(a.host);assert address.version==4 and any(address in ipaddress.ip_network(n) for n in ['10.0.0.0/8','172.16.0.0/12','192.168.0.0/16'])
op=urllib.request.build_opener(urllib.request.ProxyHandler({}));rows=[];baseline=None;start=time.monotonic();index=0
while time.monotonic()-start<a.seconds:
 row={'sample':index,'elapsedSeconds':round(time.monotonic()-start,2)};tick=time.monotonic()
 for endpoint in ['status','crowd','field']+(['robot'] if index%5==0 else []):
  try:
   began=time.perf_counter()
   with op.open('http://'+a.host+'/api/'+endpoint,timeout=2) as r:d=json.load(r)
   row[endpoint+'Ms']=round((time.perf_counter()-began)*1000,2)
   if endpoint=='status':
    row.update({k:d[k] for k in ['firmware','bootId','peerBootId','uptimeMs','freeHeap','largestFreeBlock','minimumFreeHeap','previousFailedAllocationBytes','frameErrors','detailErrors','drops']})
    if baseline is None:baseline={'bootId':d['bootId'],'peerBootId':d['peerBootId']}
    row['sameBoots']=all(d[k]==v for k,v in baseline.items());row['expectedFirmware']=d['firmware']==a.expect_version
   elif endpoint=='crowd':row.update(gridFresh=d['grid']['fresh'],gridAgeMs=d['grid']['ageMs'])
   elif endpoint=='field':
    c=d['controller'];m=d['sensors']['mast'];row.update(connected=d['connected'],volts=d['volts'],locked=c['batteryLockout'],outputsOff=not c['armed'] and not c['deadman'] and c['leftPercent']==c['rightPercent']==0 and not m['enabled'] and not m['testActive'])
   else:row.update(fullJson=True,nativeBytes=len(json.dumps(d.get('native'))),logBytes=len(d.get('logs','')))
  except Exception as error:row[endpoint+'Error']=type(error).__name__
 rows.append(row)
 if index%20==0:print(json.dumps(row),flush=True)
 if row.get('outputsOff') is False or row.get('sameBoots') is False:break
 index+=1;time.sleep(max(0,1-(time.monotonic()-tick)))
status=[r for r in rows if 'bootId' in r];fields=[r for r in rows if 'outputsOff' in r];crowds=[r for r in rows if 'gridFresh' in r];errors=sum(k.endswith('Error') for r in rows for k in r)
result={'host':a.host,'durationSeconds':round(time.monotonic()-start,2),'samples':len(rows),'errors':errors,'allBootsUnchanged':bool(status) and all(r['sameBoots'] for r in status),'allOutputsOff':bool(fields) and all(r['outputsOff'] for r in fields),'expectedFirmware':bool(status) and all(r['expectedFirmware'] for r in status),'fullJsonResponses':sum(r.get('fullJson',False) for r in rows),'freshGridResponses':sum(r['gridFresh'] for r in crowds),'crowdResponses':len(crowds),'minimumObservedHeap':min((r['freeHeap'] for r in status),default=None),'minimumLargestBlock':min((r['largestFreeBlock'] for r in status),default=None),'medianCrowdMs':statistics.median(r['crowdMs'] for r in crowds) if crowds else None,'maximumFailedAllocationBytes':max((r['previousFailedAllocationBytes'] for r in status),default=None),'motionCommands':0,'rows':rows}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
if not(result['allBootsUnchanged'] and result['allOutputsOff'] and result['expectedFirmware']) or errors:raise SystemExit(1)
