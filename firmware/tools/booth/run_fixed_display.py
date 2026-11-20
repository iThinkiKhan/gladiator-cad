"""Fixed-mast event eyes. Only GET health and temporary display POSTs; no actuators.
Run on the event PC: run_fixed_display.py --seconds 7200. Ctrl+C restores auto.
"""
import argparse, ipaddress, json, time, urllib.request
from pathlib import Path

GET_PATHS = {'status', 'field', 'camera/status'}

def validate_request(method, endpoint, body):
    if method == 'GET' and endpoint in GET_PATHS and body is None:
        return
    if method == 'POST' and endpoint == 'visual' and isinstance(body, dict):
        if body == {'mode': 'auto'}:
            return
        if body == {'mode': 'greeting', 'leaseMs': 5000, 'message': 'Welcome!'}:
            return
    raise ValueError('Only health reads and the fixed display-only expressions are allowed')

class Client:
    def __init__(self, host):
        address = ipaddress.ip_address(host)
        if address.version != 4 or not any(address in ipaddress.ip_network(n) for n in ('10.0.0.0/8','172.16.0.0/12','192.168.0.0/16')):
            raise ValueError('Use a private robot IPv4 address')
        self.base = 'http://' + str(address) + '/api/'
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    def request(self, endpoint, body=None):
        method = 'GET' if body is None else 'POST'
        validate_request(method, endpoint, body)
        req = urllib.request.Request(self.base + endpoint, data=None if body is None else json.dumps(body).encode(), headers={'Content-Type':'application/json'}, method=method)
        with self.opener.open(req, timeout=2) as response:
            return json.load(response)

def check_field(field):
    c = field['controller']; m = field['sensors']['mast']; p = field['sensors']['power']
    age = field['telemetryAgeMs']
    if not field['connected'] or type(age) not in (int,float) or not 0 <= age < 250:
        raise RuntimeError('Fresh robot telemetry unavailable; show stopped')
    if not field['powerValid'] or c['batteryLockout'] or c['battery'] != 'OK':
        raise RuntimeError('Battery/power is not OK; show stopped')
    if p['meta']['health'] != 'OK' or not p['meta']['hasSample'] or not 0 <= p['meta']['ageMs'] < 500:
        raise RuntimeError('Power-monitor samples unavailable/stale; show stopped')
    if c['state'] != 'SAFE' or any(c[k] for k in ('armed','deadman','leftPercent','rightPercent')):
        raise RuntimeError('Tracks are not stationary and disarmed; show stopped')
    if any(m[k] for k in ('enabled','testActive','gpio10OutputEnabled','gpio13OutputEnabled')):
        raise RuntimeError('Mast output is active; this fixed-mast show stopped without taking control')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', help='Default: try Opal, then direct Wi-Fi')
    parser.add_argument('--seconds', type=int, default=7200)
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parents[2]/'diagnostics/field-fixed-display-latest.json')
    args = parser.parse_args()
    if not 5 <= args.seconds <= 7200:
        parser.error('Choose 5 to 7200 seconds')
    report = {'date':'2026-10-24','motionCommands':0,'enableCommands':0,'configurationWrites':0,'samples':0,'greetings':0,'status':'not started'}
    client = None; greeted = False; start = time.monotonic(); exit_code = 0
    try:
        for host in ([args.host] if args.host else ['172.23.44.190','192.168.8.1']):
            candidate = Client(host)
            try:
                boot = candidate.request('status')
                check_field(candidate.request('field'))
            except (OSError, ValueError, KeyError, RuntimeError) as error:
                print(host + ': ' + str(error), flush=True)
                continue
            client = candidate; report['host'] = host
            break
        if client is None:
            raise RuntimeError('Robot not ready. Check power and Wi-Fi, then start again deliberately')
        camera = client.request('camera/status')
        if not camera.get('cameraReady') or camera.get('cameraError'):
            raise RuntimeError('Camera is not ready; repair/reconnect it before starting')
        camera_boot = camera['bootId']; boots = (boot['bootId'],boot['peerBootId'])
        report.update(gatewayBootId=boots[0],s3BootId=boots[1],cameraBootId=camera_boot,status='running')
        deadline = time.monotonic() + args.seconds; next_greeting = 0; next_health = 0
        print('FIXED MAST: servos OFF, tracks disarmed. Greeting every minute; camera on demand. Ctrl+C stops.', flush=True)
        while time.monotonic() < deadline:
            tick = time.monotonic(); field = client.request('field'); check_field(field); report['samples'] += 1
            if tick >= next_health:
                status = client.request('status'); camera = client.request('camera/status')
                if (status['bootId'],status['peerBootId']) != boots or camera['bootId'] != camera_boot:
                    raise RuntimeError('A controller/camera restarted; inspect connections before restarting show')
                if not camera.get('cameraReady') or camera.get('cameraError'):
                    raise RuntimeError('Camera failed; inspect its power/ground connection')
                report['lastVolts'] = field['volts']; next_health = tick + 15
            if tick >= next_greeting:
                reply = client.request('visual', {'mode':'greeting','leaseMs':5000,'message':'Welcome!'})
                if reply.get('accepted') is not True or reply.get('scope') != 'display-only':
                    raise RuntimeError('Display greeting was not confirmed')
                greeted = True; report['greetings'] += 1; next_greeting = tick + 60
                print('Greeting %d | %.2f V | %.3f A | all motion outputs OFF' % (report['greetings'],field['volts'],field['amps']), flush=True)
            time.sleep(max(0,min(2-(time.monotonic()-tick),deadline-time.monotonic())))
        report['status'] = 'completed'
    except KeyboardInterrupt:
        report['status'] = 'stopped by operator'
    except Exception as error:
        report.update(status='stopped on fault',error=str(error)); exit_code = 1; print(str(error),flush=True)
    finally:
        if client and greeted:
            try: report['restoredAuto'] = client.request('visual', {'mode':'auto'}).get('accepted') is True
            except Exception: report['restoredAuto'] = False
        report['elapsedSeconds'] = round(time.monotonic()-start,1)
        args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(report,indent=2))
        print(json.dumps(report),flush=True)
    return exit_code

if __name__ == '__main__':
    raise SystemExit(main())
