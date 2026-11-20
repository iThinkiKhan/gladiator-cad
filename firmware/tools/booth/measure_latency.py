"""Measure C6 GET latency without issuing motion or configuration commands."""
import argparse,ipaddress,json,socket,statistics,time
from pathlib import Path

def measure(host,path):
 started=time.perf_counter();first=None;headers=None;received=bytearray()
 with socket.create_connection((host,80),3) as sock:
  connected=time.perf_counter();sock.settimeout(3);sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
  sock.sendall((f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n").encode())
  while len(received)<131072:
   chunk=sock.recv(4096);now=time.perf_counter()
   if not chunk:raise RuntimeError('Response closed before complete body')
   if first is None:first=now
   received.extend(chunk)
   if headers is None and b'\r\n\r\n' in received:
    headers=now;head,body=bytes(received).split(b'\r\n\r\n',1)
    if not head.startswith(b'HTTP/1.1 200'):raise RuntimeError('Expected HTTP 200')
    fields=dict(l.split(b':',1) for l in head.split(b'\r\n')[1:] if b':' in l)
    length=int(next(v for k,v in fields.items() if k.lower()==b'content-length'))
   if headers is not None:
    body=received.split(b'\r\n\r\n',1)[1]
    if len(body)>=length:
     state=json.loads(body[:length]);break
  else:raise RuntimeError('Response exceeds bound')
 def ms(a,b):return round((a-b)*1000,2)
 return dict(connectMs=ms(connected,started),firstByteMs=ms(first,connected),headersMs=ms(headers,connected),bodyMs=ms(now,headers),totalMs=ms(now,started),firmware=state.get('firmware'),bootId=state.get('bootId'),peerBootId=state.get('peerBootId'),rssi=state.get('rssi'),frameErrors=state.get('frameErrors'),drops=state.get('drops'),fresh=state.get('fresh'))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--host',required=True);p.add_argument('--path',choices=['/api/status','/api/crowd','/api/field','/api/mast'],default='/api/status');p.add_argument('--samples',type=int,default=20);p.add_argument('--out',type=Path);a=p.parse_args()
 assert ipaddress.ip_address(a.host).is_private and 1<=a.samples<=100
 rows=[]
 for _ in range(a.samples):
  try:rows.append(measure(a.host,a.path))
  except (OSError,ValueError,RuntimeError,StopIteration) as e:rows.append(dict(error=str(e)))
  time.sleep(.15)
 good=[x['totalMs'] for x in rows if 'totalMs' in x]
 result=dict(host=a.host,path=a.path,samples=rows,success=len(good),errors=len(rows)-len(good))
 if good:result.update(minMs=min(good),medianMs=round(statistics.median(good),2),averageMs=round(statistics.mean(good),2),maxMs=max(good))
 if a.out:a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in result.items() if k!='samples'},indent=2),flush=True)
 if not good:raise SystemExit(1)
if __name__=='__main__':main()
