"""Install the booth C6 candidate without changing S3 calibration or pairing."""
from pathlib import Path
import argparse,gzip,hashlib,http.client,ipaddress,json,re,socket,time,urllib.request
ROOT=Path(__file__).resolve().parents[2]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--host');parser.add_argument('--check-only',action='store_true');parser.add_argument('--usb-powered',action='store_true',help='USB-powered electronics maintenance: requires fresh 3.5-5.5 V telemetry, battery lockout and all outputs off');parser.add_argument('--c6-only',action='store_true',help='USB-powered gateway maintenance with the S3 disconnected; never applies calibration');parser.add_argument('--expect-sha256');parser.add_argument('--expect-version',default='gateway-2.3.9');parser.add_argument('--receipt-dir',default='diagnostics/operator-20261023');args=parser.parse_args()
 assert not (args.usb_powered and args.c6_only),'Choose one maintenance power mode'
 if not args.check_only:
  if not args.host:parser.error('--host is required unless --check-only is used')
  address=ipaddress.ip_address(args.host);assert address.version==4 and any(address in ipaddress.ip_network(n) for n in ['10.0.0.0/8','172.16.0.0/12','192.168.0.0/16']),'Use the private IPv4 address of this gateway'
 version=re.search(r'constexpr char VERSION\[\]="([^"]+)";', (ROOT/'gateway/src/GatewayConfig.h').read_text(encoding='utf-8')).group(1)
 base='http://'+(args.host or '');op=urllib.request.build_opener(urllib.request.ProxyHandler({}));out=(ROOT/args.receipt_dir).resolve();assert out.is_relative_to(ROOT.resolve()),'Receipts must stay in the project';out.mkdir(parents=True,exist_ok=True)
 def get(path):
  # Only reads may retry; an accepted firmware upload is never repeated.
  for attempt in range(3):
   try:
    with op.open(base+path,timeout=4) as r:return json.load(r)
   except (OSError,ValueError):
    if attempt==2:raise
    time.sleep(.25)
 def safe():
  f=get('/api/field');m=get('/api/mast')
  if args.c6_only:
   assert not f['connected'] and not m['fresh'],'C6-only maintenance requires the S3 to remain disconnected'
   return f,m
  c=f['controller']
  if args.usb_powered:
   assert f['connected'] and f['powerValid'] and c['batteryLockout'] and 3.5<=f['volts']<=5.5,'USB maintenance requires fresh 3.5-5.5 V electronics power with movement lockout active'
  else:assert f['connected'] and f['powerValid'] and not c['batteryLockout'],'Fresh healthy power required'
  assert not c['armed'] and not c['deadman'] and c['leftPercent']==c['rightPercent']==0,'Tracks must be disarmed'
  assert m['fresh'] and not m['enabled'] and not m['testActive'],'Mast outputs must be off'
  return f,m
 image=(ROOT/'gateway/.pio/build/gladiator_c6/firmware.bin').read_bytes();assert 512<len(image)<=0x1e0000 and image[0]==0xe9 and version.encode() in image
 for n in ['index.html','app.js','mast-settings.js','mast-workbench.js']:assert gzip.compress((ROOT/'tools/booth'/n).read_bytes(),mtime=0) in image,'Final source mismatch'
 for n in ['app.js','styles.css']:assert gzip.compress((ROOT/'tools/hardware-test'/n).read_text(encoding='utf-8').encode('utf-8'),mtime=0) in image,'Hardware-test asset mismatch'
 digest=hashlib.sha256(image).hexdigest()
 if args.expect_sha256:assert digest==args.expect_sha256,'Image differs from the reviewed release'
 if args.check_only:
  print(json.dumps(dict(candidate=version,bytes=len(image),sha256=digest,boothAssets=4,hardwareAssets=2,robotRequests=0)));return
 key=json.loads((ROOT/'diagnostics/gateway-private/credentials.json').read_text())['adminKey']
 before=get('/api/status');assert before['firmware']==args.expect_version,'Gateway changed since the expected baseline'
 if args.c6_only:
  assert not before['robotConnected'],'C6-only maintenance requires the S3 to be disconnected'
  safe();time.sleep(2) # Confirm absence across two observations, without sending S3 commands.
 field,mast=safe();beforeMast=mast;setup=get('/api/mast/setup');digest=hashlib.sha256(image).hexdigest()
 (out/('c6-'+version+'-pre-upload.json')).write_text(json.dumps({'status':before,'field':field,'mast':mast,'savedSetup':setup},indent=2))
 print(json.dumps({'phase':'upload','from':before['firmware'],'version':version,'bytes':len(image),'sha256':digest}),flush=True)
 header=('POST /api/ota HTTP/1.1\r\nHost: '+args.host+'\r\nContent-Type: application/octet-stream\r\nX-Gladiator-Key: '+key+'\r\nX-Gladiator-SHA256: '+digest+'\r\nContent-Length: '+str(len(image))+'\r\nConnection: close\r\n\r\n').encode()
 with socket.create_connection((args.host,80),10) as connection:
  connection.settimeout(90);connection.sendall(header)
  for i in range(0,len(image),4096):connection.sendall(image[i:i+4096]);time.sleep(.003)
  response=http.client.HTTPResponse(connection);response.begin();body=response.read(4096)
  assert response.status==200 and json.loads(body).get('updated'),f'C6 refused update (HTTP {response.status}): {body.decode("utf-8","replace")[:512]}'
 deadline=time.monotonic()+90;after=None
 while time.monotonic()<deadline:
  time.sleep(2)
  try:
   s=get('/api/status')
   if s['bootId']==before['bootId'] or s['uptimeMs']<20000:continue
   assert s['firmware']==version and s['otaSlot']!=before['otaSlot'],'Unexpected image/slot'
   if args.c6_only:assert not s['robotConnected'],'S3 connected during C6-only maintenance; inspect before further operations'
   else:assert s['peerBootId']==before['peerBootId'] and s['robotConnected'],'S3 continuity lost'
   field,mast=safe();after=s;break
  except (OSError,ValueError):continue
 assert after,'Update accepted, but reboot not verified; do not upload again blindly'
 afterSetup=get('/api/mast/setup');assert afterSetup==setup,'Saved setup changed during update; inspect its revision before another operation'
 if not args.c6_only:
  assert mast['calibrated']==beforeMast['calibrated'],'Unexpected mast calibration state change'
  if beforeMast.get('profile'):assert mast.get('profile')==beforeMast['profile'],'Applied S3 profile changed during update; inspect before another operation'
 for path,source in [('/booth/','index.html'),('/booth/app.js','app.js'),('/booth/mast-settings.js','mast-settings.js'),('/booth/mast-workbench.js','mast-workbench.js')]:
  with op.open(base+path,timeout=4) as r:data=r.read()
  assert gzip.decompress(data)==(ROOT/'tools/booth'/source).read_bytes(),'Hosted asset mismatch'
 with op.open(base+'/hardware-test/app.js',timeout=4) as r:assert gzip.decompress(r.read()).decode('utf-8')==(ROOT/'tools/hardware-test/app.js').read_text(encoding='utf-8'),'Manual-aim asset mismatch'
 crowd=get('/api/crowd');assert crowd['schema']==1 and 'grid' in crowd
 receipt={'beforeVersion':before['firmware'],'version':after['firmware'],'sha256':digest,'oldSlotPreserved':before['otaSlot'],'slot':after['otaSlot'],'bootId':after['bootId'],'s3BootId':after['peerBootId'],'mode':'c6-only' if args.c6_only else 'usb-powered' if args.usb_powered else 'connected-robot','s3Unchanged':None if args.c6_only else True,'s3ContinuityVerified':not args.c6_only,'field':field,'mast':mast,'crowd':crowd,'savedSetupUnchanged':True,'savedSetup':afterSetup}
 (out/('c6-'+version+'-installed.json')).write_text(json.dumps(receipt,indent=2))
 print(json.dumps({'installed':after['firmware'],'slot':after['otaSlot'],'mode':'c6-only' if args.c6_only else 'usb-powered' if args.usb_powered else 'connected-robot','s3ContinuityVerified':not args.c6_only,'outputsOff':not args.c6_only,'hostedAssets':'verified','savedSetupUnchanged':True,'grid':crowd['grid']}),flush=True)
if __name__=='__main__':main()
