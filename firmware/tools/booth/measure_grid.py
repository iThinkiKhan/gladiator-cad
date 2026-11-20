"""Measure real compact-grid updates using GETs only; no configuration or motion."""
import argparse,ipaddress,json,statistics,time,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--host',required=True);p.add_argument('--seconds',type=int,default=30);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert 10<=a.seconds<=180
assert ipaddress.ip_address(a.host).is_private
op=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def get(path):
 with op.open('http://'+a.host+path,timeout=2) as r:return json.load(r)
before=get('/api/status');field=get('/api/field');saved=get('/api/mast/setup')
def off(f):
 c=f['controller'];m=f['sensors']['mast'];return f['connected'] and not c['armed'] and not c['deadman'] and c['leftPercent']==c['rightPercent']==0 and not m['enabled'] and not m['testActive']
assert off(field),'Outputs must be off before this observation-only test'
start=time.monotonic();rows=[]
while time.monotonic()-start<a.seconds:
 tick=time.monotonic();row={'elapsed':round(tick-start,4)}
 try:
  d=get('/api/crowd');g=d['grid'];row.update(ms=round((time.monotonic()-tick)*1000,2),fresh=g['fresh'],ageMs=g['ageMs'],source=g.get('source','diagnostic-snapshot'),sample=g.get('sample'),cells=len(g['mm']) if g['mm'] is not None else 0)
 except Exception as e:row['error']=type(e).__name__
 rows.append(row);time.sleep(max(0,.1-(time.monotonic()-tick)))
after=get('/api/status');final=get('/api/field');finalSaved=get('/api/mast/setup');good=[x for x in rows if x.get('fresh')];compact=[x for x in good if x['source']=='range-telemetry'];changes=[];last=None
for row in compact:
 if row['sample']!=last:changes.append(row['elapsed']);last=row['sample']
gaps=[1000*(y-x) for x,y in zip(changes,changes[1:])]
result={'host':a.host,'durationSeconds':round(time.monotonic()-start,2),'samples':len(rows),'errors':sum('error' in x for x in rows),'freshResponses':len(good),'compactResponses':len(compact),'distinctCompactSamples':len(changes),'observedGridHz':round((len(changes)-1)/(changes[-1]-changes[0]),3) if len(changes)>1 else 0,'medianUpdateGapMs':statistics.median(gaps) if gaps else None,'maxUpdateGapMs':max(gaps) if gaps else None,'medianFreshAgeMs':statistics.median(x['ageMs'] for x in good) if good else None,'medianHttpMs':statistics.median(x['ms'] for x in rows if 'ms' in x) if good else None,'sameBoots':all(before[k]==after[k] for k in ['bootId','peerBootId']),'outputsOff':off(final),'savedSetupUnchanged':saved==finalSaved,'firmware':after['firmware'],'bootId':after['bootId'],'s3BootId':after['peerBootId'],'frameErrorDelta':after['frameErrors']-before['frameErrors'],'detailErrorDelta':after['detailErrors']-before['detailErrors'],'dropDelta':after['drops']-before['drops'],'failedAllocationBytes':after['previousFailedAllocationBytes'],'minimumObservedHeap':min(before['freeHeap'],after['freeHeap']),'motionCommands':0,'rows':rows}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
assert not result['errors'] and result['sameBoots'] and result['outputsOff'] and result['savedSetupUnchanged']
