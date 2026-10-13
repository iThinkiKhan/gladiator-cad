"""Authenticated CAM maintenance. Keys stay in a local JSON file, not arguments."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def request(url, path, data=None, key=None, digest=None, timeout=5):
    headers = {'Content-Type': 'application/octet-stream' if path == '/api/ota' else 'application/json'}
    if key: headers['X-Gladiator-Key'] = key
    if digest: headers['X-Gladiator-SHA256'] = digest
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(urllib.request.Request(url.rstrip('/') + path, data=data, headers=headers), timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'CAM returned HTTP {exc.code}: {exc.read().decode("utf-8", "replace")}') from None

def update(url, image, key, confirm=True, timeout=95):
    before = request(url, '/api/status')
    if before.get('role') != 'masthead-camera' or not before.get('otaEnabled'):
        raise RuntimeError('Target is not an OTA-enabled Gladiator CAM')
    if before.get('otaPendingVerification'):
        raise RuntimeError('Confirm the current firmware before another update')
    digest = hashlib.sha256(image).hexdigest()
    result = request(url, '/api/ota', image, key, digest, 130)
    if result.get('sha256') != digest:
        raise RuntimeError('Device upload digest differs from local image')
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        time.sleep(2)
        try:
            after = request(url, '/api/status', timeout=3)
            if after['bootId'] == before['bootId'] or after['uptimeMs'] < 5000: continue
            if after['otaSlot'] == before['otaSlot']: raise RuntimeError('OTA slot did not change')
            if confirm:
                request(url, '/api/confirm', b'', key)
                after = request(url, '/api/status')
                if after['otaPendingVerification']: continue
            return {'before': before, 'after': after, 'imageSha256': digest, 'imageBytes': len(image), 'confirmed': confirm}
        except (OSError, ValueError):
            continue
    raise RuntimeError('New CAM boot not verified; unconfirmed firmware will roll back')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'upload', 'confirm'])
    parser.add_argument('--url', default='http://192.168.8.2')
    parser.add_argument('--key-file', type=Path, default=ROOT / 'diagnostics/cam-private/credentials.json')
    parser.add_argument('--firmware', type=Path, default=ROOT / 'cam/.pio/build/gladiator_cam/firmware.bin')
    parser.add_argument('--no-confirm', action='store_true', help='Only for testing automatic rollback')
    parser.add_argument('--record', type=Path)
    args = parser.parse_args()
    if args.action == 'status': result = request(args.url, '/api/status')
    else:
        key = json.loads(args.key_file.read_text(encoding='utf-8'))['adminKey']
        if args.action == 'confirm': result = request(args.url, '/api/confirm', b'', key)
        else: result = update(args.url, args.firmware.read_bytes(), key, not args.no_confirm)
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__': main()
