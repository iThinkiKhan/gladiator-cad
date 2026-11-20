"""Installer integration tests. All HTTP, socket and timing operations are mocked."""
import contextlib, gzip, importlib.util, io, json, re, shutil, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
VERSION=re.search(r'VERSION\[\]="([^"]+)"',(ROOT/'gateway/src/GatewayConfig.h').read_text()).group(1)
spec=importlib.util.spec_from_file_location('deploy_c6',ROOT/'tools/booth/deploy_c6.py');deploy=importlib.util.module_from_spec(spec);spec.loader.exec_module(deploy)

class InstallerTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name)
  for name in ['gateway/src/GatewayConfig.h','gateway/.pio/build/gladiator_c6/firmware.bin']+[f'tools/booth/{n}' for n in ['index.html','app.js','mast-settings.js','mast-workbench.js']]+[f'tools/hardware-test/{n}' for n in ['app.js','styles.css']]:
   target=cls.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
  (cls.root/'diagnostics/gateway-private').mkdir(parents=True);(cls.root/'diagnostics/gateway-private/credentials.json').write_text('{"adminKey":"TEST-ONLY"}')
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def setUp(self):
  self.connected=True;self.fresh=True;self.armed=False;self.enabled=False;self.lockout=False;self.volts=16.;self.badsetup=False;self.afterconnected=None;self.uploads=0;self.statusreads=0;self.setupreads=0;self.paths=[];self.sent=[]
  self.out='diagnostics/test-'+self._testMethodName
 def open(self,url,timeout=0):
  path=url.removeprefix('http://192.168.8.1');self.paths.append(path)
  if path=='/api/status':
   self.statusreads+=1;after=self.statusreads>1
   data=dict(firmware=VERSION if after else 'gateway-2.3.9',bootId=2 if after else 1,uptimeMs=30000,otaSlot='ota_0' if after else 'ota_1',peerBootId=5,robotConnected=(self.afterconnected if after and self.afterconnected is not None else self.connected))
  elif path=='/api/field':data=dict(connected=self.connected,powerValid=True,volts=self.volts,controller=dict(armed=self.armed,deadman=False,leftPercent=0,rightPercent=0,batteryLockout=self.lockout))
  elif path=='/api/mast':data=dict(fresh=self.fresh,enabled=self.enabled,testActive=False,calibrated=True,profile={'immutable':'profile'})
  elif path=='/api/mast/setup':
   self.setupreads+=1;data=dict(schema=1,revision=9+(1 if self.badsetup and self.setupreads>1 else 0),fields={'panPin':'10','tiltLow':'1150'})
  elif path=='/api/crowd':data=dict(schema=1,grid={'fresh':False})
  else:
   files={'/booth/':'tools/booth/index.html','/booth/app.js':'tools/booth/app.js','/booth/mast-settings.js':'tools/booth/mast-settings.js','/booth/mast-workbench.js':'tools/booth/mast-workbench.js','/hardware-test/app.js':'tools/hardware-test/app.js'}
   file=self.root/files[path];raw=file.read_text(encoding='utf-8').encode() if 'hardware-test' in path else file.read_bytes();return io.BytesIO(gzip.compress(raw,mtime=0))
  return io.BytesIO(json.dumps(data).encode())
 def connection(self,*args,**kwargs):
  self.uploads+=1;owner=self
  class Connection:
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def settimeout(self,*args):pass
   def sendall(self,b):owner.sent.append(b)
  return Connection()
 def execute(self,flags=()):
  owner=self
  class Opener:
   def open(self,*a,**kw):return owner.open(*a,**kw)
  class Response:
   status=200
   def __init__(self,*a):pass
   def begin(self):pass
   def read(self,*a):return b'{"updated":true}'
  with patch.object(deploy,'ROOT',self.root),patch.object(sys,'argv',['deploy_c6.py','--host','192.168.8.1','--receipt-dir',self.out,*flags]),patch.object(deploy.urllib.request,'build_opener',return_value=Opener()),patch.object(deploy.socket,'create_connection',side_effect=self.connection),patch.object(deploy.http.client,'HTTPResponse',Response),patch.object(deploy.time,'sleep'),contextlib.redirect_stdout(io.StringIO()):deploy.main()
 def receipt(self):return json.loads((self.root/self.out/f'c6-{VERSION}-installed.json').read_text())
 def test_normal_success(self):
  self.execute();self.assertEqual(self.uploads,1);self.assertTrue(self.receipt()['s3ContinuityVerified']);self.assertEqual(self.receipt()['savedSetup']['revision'],9)
 def test_default_rejects_usb_voltage(self):
  self.lockout=True;self.volts=4.28
  with self.assertRaisesRegex(AssertionError,'healthy power'):self.execute()
  self.assertEqual(self.uploads,0)
 def test_usb_success_preserves_lockout_and_profile(self):
  self.lockout=True;self.volts=4.28;self.execute(['--usb-powered']);r=self.receipt();self.assertEqual(r['mode'],'usb-powered');self.assertTrue(r['field']['controller']['batteryLockout']);self.assertEqual(r['mast']['profile'],{'immutable':'profile'});self.assertEqual(self.uploads,1)
  self.assertTrue(self.sent[0].startswith(b'POST /api/ota '));self.assertNotIn(b'POST /api/mast',b''.join(self.sent));self.assertTrue(all(p.startswith('/api/') or p.startswith('/booth/') or p.startswith('/hardware-test/') for p in self.paths))
 def test_usb_rejects_depleted_pack_voltage(self):
  self.lockout=True;self.volts=13.0
  with self.assertRaisesRegex(AssertionError,'3.5-5.5'):self.execute(['--usb-powered'])
  self.assertEqual(self.uploads,0)
 def test_usb_rejects_armed_tracks(self):
  self.lockout=True;self.volts=4.28;self.armed=True
  with self.assertRaisesRegex(AssertionError,'disarmed'):self.execute(['--usb-powered'])
  self.assertEqual(self.uploads,0)
 def test_usb_rejects_enabled_mast(self):
  self.lockout=True;self.volts=4.28;self.enabled=True
  with self.assertRaisesRegex(AssertionError,'outputs must be off'):self.execute(['--usb-powered'])
  self.assertEqual(self.uploads,0)
 def test_c6_only_disconnected(self):
  self.connected=False;self.fresh=False;self.execute(['--c6-only']);r=self.receipt();self.assertFalse(r['s3ContinuityVerified']);self.assertIsNone(r['s3Unchanged']);self.assertTrue(r['savedSetupUnchanged'])
 def test_c6_only_rejects_connected_robot(self):
  with self.assertRaisesRegex(AssertionError,'disconnected'):self.execute(['--c6-only'])
  self.assertEqual(self.uploads,0)
 def test_setup_change_stops_verification_without_reupload(self):
  self.badsetup=True
  with self.assertRaisesRegex(AssertionError,'Saved setup changed'):self.execute()
  self.assertEqual(self.uploads,1);self.assertFalse((self.root/self.out/f'c6-{VERSION}-installed.json').exists())
 def test_c6_only_rejects_reconnected_robot_after_upload(self):
  self.connected=False;self.fresh=False;self.afterconnected=True
  with self.assertRaisesRegex(AssertionError,'S3 connected'):self.execute(['--c6-only'])
  self.assertEqual(self.uploads,1)
 def test_maintenance_modes_exclusive(self):
  with self.assertRaisesRegex(AssertionError,'one maintenance'):self.execute(['--c6-only','--usb-powered'])
  self.assertEqual(self.uploads,0)
if __name__=='__main__':unittest.main()
