"""OTA the C6 hardware-test release and verify slot, page assets and S3 continuity."""
from pathlib import Path
import hashlib,http.client,json,re,socket,time,urllib.request,gzip
ROOT=Path(__file__).resolve().parents[2]
RUNTIME=ROOT/"tools/hardware-test/.runtime"
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
HOST="192.168.0.230"
BASE="http://"+HOST
def get(path,timeout=4):
    with opener.open(BASE+path,timeout=timeout) as response:return json.load(response)
def post(path,body,key=None):
    headers={"Content-Type":"application/json"}
    if key:headers["X-Gladiator-Key"]=key
    request=urllib.request.Request(BASE+path,data=json.dumps(body).encode(),headers=headers)
    with opener.open(request,timeout=5) as response:return json.load(response)
def safe():
    f=get("/api/field");m=get("/api/mast");c=f["controller"]
    assert f["connected"] and f["powerValid"] and not c["batteryLockout"],"Fresh healthy power/controller required"
    assert not c["armed"] and not c["deadman"] and c["leftPercent"]==c["rightPercent"]==0,"Tracks must be disarmed/stationary"
    assert m["fresh"] and not m["enabled"] and not m["testActive"],"Mast/test must be off"
    return f,m
def main():
    image=(ROOT/"gateway/.pio/build/gladiator_c6/firmware.bin").read_bytes()
    assert 512<len(image)<=0x1e0000 and image[0]==0xe9 and b"gladiator_gateway" in image and b"gateway-2.2.4" in image,"Unexpected firmware image"
    key=json.loads((ROOT/"diagnostics/gateway-private/credentials.json").read_text())["adminKey"]
    secret=(ROOT/"shared/secrets.h").read_text()
    for name in ["GLADIATOR_FIELD_PASSWORD","GLADIATOR_MAINTENANCE_AP_PASSWORD"]:
        value=re.search(r'#define\s+'+name+r'\s+"([^"]+)"',secret).group(1)
        if name=="GLADIATOR_FIELD_PASSWORD":assert value.encode() in image,"Field credentials missing from image"
    assert b"change-me-field" not in image,"Placeholder field credentials"
    before=get("/api/status")
    field,mast=safe()
    post("/api/mast",{"session":1,"sequence":1,"operation":0,"pan":0,"tilt":0})
    post("/api/mast/config",{"action":"stop"})
    c=field["controller"]
    post("/api/control",{"epoch":c["epoch"],"client":1,"sequence":1,"observedMs":c["s3Ms"],"operation":0,"deadman":0,"overdrive":0,"power":25,"left":0,"right":0})
    safe()
    digest=hashlib.sha256(image).hexdigest()
    print(json.dumps({"phase":"upload","bytes":len(image),"sha256":digest,"from":before["firmware"],"slot":before["otaSlot"],"volts":field["volts"]}),flush=True)
    header=("POST /api/ota HTTP/1.1\r\nHost: "+HOST+"\r\nContent-Type: application/octet-stream\r\nX-Gladiator-Key: "+key+"\r\nX-Gladiator-SHA256: "+digest+"\r\nContent-Length: "+str(len(image))+"\r\nConnection: close\r\n\r\n").encode()
    with socket.create_connection((HOST,80),10) as connection:
        connection.settimeout(90);connection.sendall(header)
        for offset in range(0,len(image),4096):
            connection.sendall(image[offset:offset+4096]);time.sleep(.003)
        response=http.client.HTTPResponse(connection);response.begin();reply=response.read(4096)
        assert response.status==200 and json.loads(reply).get("updated"),"Gateway rejected OTA: "+reply.decode("utf-8","replace")
    print("Upload accepted. Waiting for changed C6 boot and verified running slot.",flush=True)
    deadline=time.monotonic()+100
    while time.monotonic()<deadline:
        time.sleep(2)
        try:
            after=get("/api/status")
            if after["bootId"]==before["bootId"] or after["uptimeMs"]<18000:continue
            assert after["firmware"]=="gateway-2.2.4","Unexpected running firmware"
            assert after["otaSlot"]!=before["otaSlot"],"OTA slot did not change"
            assert after["peerBootId"]==before["peerBootId"] and after["robotConnected"],"S3 continuity lost"
            field,mast=safe()
            break
        except (OSError,ValueError):continue
    else:raise RuntimeError("C6 OTA reboot not verified; upload ended, do not upload again blindly")
    for path,source in [("/hardware-test/","index.html"),("/hardware-test/app.js","app.js"),("/hardware-test/styles.css","styles.css")]:
        with opener.open(BASE+path,timeout=5) as response:
            payload=response.read();encoding=response.headers.get("Content-Encoding")
        assert encoding=="gzip","Embedded assets should be compressed"
        text=gzip.decompress(payload).decode("utf-8")
        expected=(ROOT/"tools/hardware-test"/source).read_text(encoding="utf-8")
        if source=="index.html":
            expected=expected.replace('<html lang="en">','<html lang="en" data-hosted="c6">').replace('href="/styles.css"','href="/hardware-test/styles.css"').replace('src="/app.js"','src="/hardware-test/app.js"')
        assert text==expected,"Served asset differs: "+source
    with opener.open(BASE+"/",timeout=5) as response:assert b'/hardware-test' in response.read(),"Field shortcut missing"
    result={"firmware":after["firmware"],"beforeBootId":before["bootId"],"bootId":after["bootId"],"fromSlot":before["otaSlot"],"otaSlot":after["otaSlot"],"s3BootId":after["peerBootId"],"s3BootUnchanged":True,"volts":field["volts"],"armed":field["controller"]["armed"],"mastEnabled":mast["enabled"],"testActive":mast["testActive"],"calibrated":mast["calibrated"],"assetsVerified":3,"imageSha256":digest,"bytes":len(image),"url":"http://192.168.8.1/hardware-test/"}
    RUNTIME.mkdir(parents=True,exist_ok=True)
    (RUNTIME/"c6-hardware-test-ota.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result),flush=True)
if __name__=="__main__":main()
