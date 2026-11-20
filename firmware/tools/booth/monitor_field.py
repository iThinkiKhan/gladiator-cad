"""No-motion field monitor: diagnostic GETs, bounded detail leases, read-only USB queries.

Never opens video or sends motor/servo, calibration, light, reset or firmware commands.
"""
import argparse,concurrent.futures,datetime,json,sys,threading,time,urllib.request
from pathlib import Path
from winusb_c6 import WinUsbC6

ROOT=Path(__file__).resolve().parents[2]
GETS={'/api/status','/api/field','/api/crowd','/api/visual','/api/mast/setup','/api/robot','/api/camera/status'}
USB_COMMANDS={b'status\n',b'field\n'}

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--seconds',type=int,default=1800);p.add_argument('--camera',default='192.168.8.3');a=p.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT.resolve()) and 10<=a.seconds<=43200
    out.mkdir(parents=True,exist_ok=True);control=out/'control.json'
    if not control.exists():control.write_text(json.dumps({'durationSeconds':a.seconds}))
    key=json.loads((ROOT/'diagnostics/gateway-private/credentials.json').read_text())['adminKey']
    op=urllib.request.build_opener(urllib.request.ProxyHandler({}));stop=threading.Event();usb_latest={};usb_lock=threading.Lock();event_lock=threading.Lock();events=[];states={}
    started=time.monotonic();latest={};stats={'samples':0,'httpErrors':{},'events':0,'motionCommandsSent':0,'usbQueries':0,'cameraFramesObserved':0};first={}

    def event(kind,value):
        if states.get(kind)==value:return
        states[kind]=value;r={'atUtc':now(),'elapsedSeconds':round(time.monotonic()-started,2),'kind':kind,'value':value}
        with event_lock:
            events.append(r)
            with (out/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(r)+'\n')
        print('EVENT '+json.dumps(r),flush=True)

    def get(host,path):
        assert path in GETS
        with op.open('http://'+host+path,timeout=3) as r:return json.load(r)

    def details(lease):
        # The ONLY HTTP POST this monitor can send is a finite diagnostic lease.
        assert 0<=lease<=20000
        body=json.dumps({'intervalMs':2000,'leaseMs':lease}).encode()
        q=urllib.request.Request('http://192.168.8.1/api/subscribe',data=body,headers={'Content-Type':'application/json','X-Gladiator-Key':key})
        with op.open(q,timeout=3) as r:return json.load(r)

    def usb_worker():
        try:
            with WinUsbC6() as port,(out/'usb-console-private.log').open('ab') as raw:
                port.timeout=.3;next_query=0;pending=b''
                event('usb','connected; no reset or control-line changes')
                while not stop.is_set():
                    if time.monotonic()>=next_query:
                        for command in (b'status\n',b'field\n'):
                            assert command in USB_COMMANDS;port.write(command);stats['usbQueries']+=1
                            block=port.read(14000)
                            if block:raw.write(block);raw.flush();pending+=block
                        next_query=time.monotonic()+10
                    else:
                        block=port.read(4096)
                        if block:raw.write(block);raw.flush();pending+=block
                    while b'\n' in pending:
                        line,pending=pending.split(b'\n',1);text=line.decode('utf8','replace');at=text.find('{')
                        if at>=0:
                            try:d=json.JSONDecoder().raw_decode(text[at:])[0]
                            except ValueError:continue
                            label='gateway' if d.get('role')=='network-gateway' else 'field' if 'controller'in d else None
                            if label:
                                with usb_lock:usb_latest[label]={'atUtc':now(),'data':d}
                    if len(pending)>65536:pending=pending[-8192:]
        except Exception as e:event('usb',{'error':str(e)})

    thread=threading.Thread(target=usb_worker,daemon=True);thread.start()
    next_cam=next_native=next_setup=next_heartbeat=0;camera_host=a.camera;previous={};last_frame_progress=time.monotonic();next_lease=0;previous_detail_mode=None
    try:
        with (out/'samples.jsonl').open('a',encoding='utf-8') as samples,concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            while not stop.is_set():
                tick=time.monotonic();config=json.loads(control.read_text());limit=int(config.get('durationSeconds',a.seconds))
                if config.get('stop') or tick-started>=limit:break
                details_enabled=bool(config.get('detailsEnabled',True))
                if details_enabled!=previous_detail_mode:
                    event('diagnostic-detail-mode','enabled' if details_enabled else 'paused');next_lease=0
                row={'atUtc':now(),'elapsedSeconds':round(tick-started,2)}
                jobs={'gateway':('192.168.8.1','/api/status'),'field':('192.168.8.1','/api/field'),'grid':('192.168.8.1','/api/crowd')}
                if tick>=next_cam:jobs['camera']=(camera_host,'/api/status');next_cam=tick+5
                if details_enabled and tick>=next_native:jobs['native']=('192.168.8.1','/api/robot');next_native=tick+10
                if tick>=next_setup:jobs['setup']=('192.168.8.1','/api/mast/setup');next_setup=tick+30
                futures={name:pool.submit(get,*args) for name,args in jobs.items()}
                for name,future in futures.items():
                    try:
                        d=future.result();row[name]=d;latest[name]=d;event('http:'+name,'ok')
                    except Exception as e:
                        row[name]={'error':str(e)};stats['httpErrors'][name]=stats['httpErrors'].get(name,0)+1;event('http:'+name,{'error':str(e)})
                g=row.get('gateway',{})
                if 'bootId'in g:
                    first.setdefault('gateway',g);event('gateway-firmware',g['firmware']);event('gateway-boot',g['bootId']);event('controller-boot',g['peerBootId']);event('link',{'uartStable':g['uartStable'],'stale':g['telemetryStale']})
                    for k in ('frameErrors','jsonErrors','sequenceGaps','drops','detailErrors'):
                        old=previous.get('link:'+k)
                        if old is not None and g[k]>old:event('link-counter:'+k,g[k])
                        previous['link:'+k]=g[k]
                f=row.get('field',{})
                if 'controller'in f:
                    first.setdefault('field',f);c=f['controller'];m=f['sensors']['mast']
                    output={'armed':c['armed'],'left':c['leftPercent'],'right':c['rightPercent'],'mastEnabled':m['enabled'],'testActive':m['testActive'],'gpio10':m['gpio10OutputEnabled'],'gpio13':m['gpio13OutputEnabled'],'testPin':m['testPin'],'testPulseUs':m['testPulseUs']}
                    event('outputs',output);event('battery',c['battery'])
                    for sensor in ('power','imu','tofFront','presence'):
                        d=f['sensors'][sensor];meta=d['meta'];health={'health':meta['health'],'online':meta['online']}
                        if sensor=='imu':health['poseValid']=d['gameDerived']['valid'];health['headingValid']=d['derived']['headingValid']
                        event('sensor:'+sensor,health)
                        old=previous.get('sensor:'+sensor)
                        if sensor!='presence' and old is not None and meta['errorCount']>old:event('sensor-errors:'+sensor,meta['errorCount'])
                        previous['sensor:'+sensor]=meta['errorCount']
                grid=row.get('grid',{}).get('grid')
                if grid:event('laser-grid',{'fresh':grid['fresh'],'cells':len(grid.get('mm')or[])})
                cam=row.get('camera',{})
                if cam.get('role')=='masthead-camera':
                    first.setdefault('camera',cam);event('camera-boot',cam['bootId']);event('camera',{'ready':cam['cameraReady'],'error':cam['cameraError'],'displayCode':cam['displayCode'],'indicator':cam['indicator']['code']})
                    before=previous.get('camera')
                    if before:
                        delta=cam['frames']-before['data']['frames'];seconds=tick-before['time'];row['cameraObservedFps']=round(max(0,delta)/seconds,3);stats['cameraFramesObserved']+=max(0,delta)
                        if delta>0 or not cam['streaming']:last_frame_progress=tick
                        event('camera-stalled',bool(cam['streaming'] and tick-last_frame_progress>8))
                        if cam['pollErrors']>before['data']['pollErrors']:event('camera-poll-errors',cam['pollErrors'])
                    previous['camera']={'time':tick,'data':cam}
                elif 'error'in cam:
                    try:
                        proxy=get('192.168.8.1','/api/camera/status')
                        if proxy.get('role')=='masthead-camera' and proxy.get('ip'):
                            camera_host=proxy['ip'];event('camera-address',camera_host)
                    except Exception:pass
                native=row.get('native',{});n=native.get('native')
                if n and native.get('nativeAgeMs',99999)<6000:
                    event('i2c-bus',n['bus']);i=n['imu'];event('imu-recovery-count',i['recoveryCount']);event('imu-reset-count',i['resetCount']);event('imu-fresh-reports',[k for k,v in i['reports'].items() if v['fresh']]);event('imu-config-errors',i['configurationErrors']);event('imu-calibration-errors',{'config':i['calibration']['configErrors'],'save':i['calibration']['saveErrors']})
                setup=row.get('setup',{})
                if 'revision'in setup:
                    first.setdefault('setup',setup);event('saved-endpoints',{'revision':setup['revision'],'unchanged':setup==first['setup']})
                with usb_lock:row['usb']=dict(usb_latest)
                samples.write(json.dumps(row)+'\n');samples.flush();stats['samples']+=1
                if tick>=next_lease:
                    try:
                        if details_enabled or previous_detail_mode!=details_enabled:details(20000 if details_enabled else 0)
                        event('detail-lease','ok' if details_enabled else 'not renewing')
                    except Exception as e:event('detail-lease',{'error':str(e)})
                    next_lease=tick+10
                previous_detail_mode=details_enabled
                snapshot={'atUtc':now(),'elapsedSeconds':round(time.monotonic()-started,1),'stats':stats,'states':states,'latest':latest,'first':first,'running':True,'cameraHost':camera_host}
                (out/'latest.json').write_text(json.dumps(snapshot,indent=2))
                if tick>=next_heartbeat:
                    print('HEARTBEAT '+json.dumps({'elapsedSeconds':snapshot['elapsedSeconds'],'samples':stats['samples'],'httpErrors':stats['httpErrors'],'framesObserved':stats['cameraFramesObserved'],'imu':states.get('sensor:imu'),'outputs':states.get('outputs')}),flush=True);next_heartbeat=tick+60
                stop.wait(max(0,2-(time.monotonic()-tick)))
    finally:
        stop.set();thread.join(4)
        try:details(0)
        except Exception:pass
        stats['events']=len(events);snapshot={'atUtc':now(),'elapsedSeconds':round(time.monotonic()-started,1),'stats':stats,'states':states,'latest':latest,'first':first,'running':False,'cameraHost':camera_host}
        (out/'latest.json').write_text(json.dumps(snapshot,indent=2));(out/'summary.json').write_text(json.dumps(snapshot,indent=2));print('COMPLETE '+json.dumps({'elapsedSeconds':snapshot['elapsedSeconds'],'stats':stats}),flush=True)

if __name__=='__main__':main()
