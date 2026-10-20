import importlib.util
import json
import threading
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
spec=importlib.util.spec_from_file_location("bench", Path(__file__).resolve().parents[1]/"serve.py")
bench=importlib.util.module_from_spec(spec);spec.loader.exec_module(bench)
class Fake(BaseHTTPRequestHandler):
    calls=[]
    def log_message(self,*_): pass
    def do_GET(self):
        self.calls.append(("GET",self.path,None))
        if self.path=="/api/status":
            self.send_response(302);self.send_header("Location","http://example.com/");self.end_headers();return
        self.send_response(200);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(b'{"fresh":true}')
    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.calls.append(("POST",self.path,body))
        self.send_response(202);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(b'{"queued":true}')
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.robot=ThreadingHTTPServer(("127.0.0.1",0),Fake)
        cls.server=bench.make_server(port=0)
        for s in (cls.robot,cls.server): threading.Thread(target=s.serve_forever,daemon=True).start()
        cls.base="http://127.0.0.1:"+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):
        for s in (cls.server,cls.robot):s.shutdown();s.server_close()
    def setUp(self):
        Fake.calls.clear()
        self.server.state.target="http://127.0.0.1:"+str(self.robot.server_port)
        self.server.state.generation="test"
    def request(self,path,body=None,generation="test",origin=None):
        headers={"Content-Type":"application/json","X-Hardware-Generation":generation}
        if origin:headers["Origin"]=origin
        req=urllib.request.Request(self.base+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
        try:
            with urllib.request.build_opener(bench.NoRedirect()).open(req,timeout=3) as r:return r.status,r.read()
        except urllib.error.HTTPError as e:return e.code,e.read()
    def test_assets_do_not_contact_robot(self):
        for asset in ("/","/app.js","/styles.css","/health"):
            status,data=self.request(asset);self.assertEqual(status,200);self.assertTrue(data)
        self.assertEqual(Fake.calls,[])
    def test_allowlist(self):
        self.assertEqual(self.request("/robot/api/maintenance",{})[0],403)
        self.assertEqual(self.request("/robot/api/visual/config",{})[0],403)
        self.assertEqual(Fake.calls,[])
    def test_no_drive_or_arm(self):
        for body in ({"operation":1,"deadman":0,"left":0,"right":0},{"operation":0,"deadman":1,"left":0,"right":0},{"operation":0,"deadman":0,"left":10,"right":0}):
            self.assertEqual(self.request("/robot/api/control",body)[0],400)
        self.assertFalse(Fake.calls)
        self.assertEqual(self.request("/robot/api/control",{"operation":0,"deadman":0,"left":0,"right":0})[0],202)
    def test_connection_generation(self):
        self.assertEqual(self.request("/robot/api/mast",generation="old")[0],409)
        status,data=self.request("/connection",{"target":"192.168.8.1"})
        self.assertEqual(status,200);self.assertEqual(json.loads(data)["target"],"http://192.168.8.1")
        self.assertFalse(Fake.calls)
        self.assertEqual(self.request("/robot/api/mast")[0],409)
    def test_post_forward(self):
        body={"action":"test","pin":13,"firstUs":1400,"minUs":1350,"maxUs":1450,"frequencyHz":50}
        self.assertEqual(self.request("/robot/api/mast/config",body)[0],202)
        self.assertEqual(Fake.calls[-1],("POST","/api/mast/config",body))
    def test_robot_setup_forward(self):
        body={"revision":3,"fields":{"panNeutral":"1490","tiltPin":"13","panMin":"-5"}}
        self.assertEqual(self.request("/robot/api/mast/setup",body)[0],202)
        self.assertEqual(Fake.calls[-1],("POST","/api/mast/setup",body))
        self.assertEqual(self.request("/robot/api/mast/setup")[0],200)
        with self.assertRaises(ValueError):
            bench.validate_body("/api/mast/setup",{"revision":3,"fields":{"junk":"x"*2048}})
    def test_cross_origin(self):
        self.assertEqual(self.request("/robot/api/mast",{"operation":7},origin="http://evil.example")[0],403)
        self.assertFalse(Fake.calls)
    def test_profile_size_and_finite(self):
        with self.assertRaises(ValueError):bench.validate_body("/api/mast/config",{"action":"calibrate","junk":"x"*800})
        with self.assertRaises(ValueError):bench.validate_body("/api/mast",{"pan":float("nan")})
    def test_no_redirect(self):
        self.assertEqual(self.request("/robot/api/status")[0],302)
        self.assertEqual(len(Fake.calls),1)
    def test_target_bounds(self):
        for value in ("https://192.168.8.1","http://127.0.0.1","http://example.com","http://192.168.8.1/a","http://user:pass@192.168.8.1","http://192.168.8.1?x=1","http://8.8.8.8"):
            with self.subTest(value=value), self.assertRaises(ValueError):bench.validate_target(value)
        self.assertEqual(bench.validate_target("192.168.8.1"),"http://192.168.8.1")
if __name__=="__main__":unittest.main(verbosity=2)
