// Development Overview camera status fixtures; never contacts hardware.
const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require(process.env.GLADIATOR_NODE_MODULES+'/playwright');
const root=path.resolve(__dirname,'..'),out=path.join(root,'diagnostics/camera-status-20261109');
const html=fs.readFileSync(path.join(root,'gateway/src/GatewayPage.h'),'utf8').split('R"HTML(')[1].split(')HTML"')[0];
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844}}),errors=[],writes=[];
  let address='192.168.8.4',gatewayDown=false,httpStatus=200,cam={cameraReady:true,streaming:false,rssi:-40,firmware:'masthead-1.3.2',frames:42,streamErrors:0,pollErrors:2};
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('http://gladiator.test/**',async route=>{
   const req=route.request(),url=new URL(req.url());let body={},status=200;
   if(req.method()!=='GET')writes.push(url.pathname);
   if(url.pathname==='/dev')return route.fulfill({contentType:'text/html',body:html});
   if(url.pathname==='/api/visual'){if(gatewayDown)status=502;body={schema:1,cameraIp:address};}
   else if(url.pathname==='/api/camera/status'){status=httpStatus;body=cam;}
   else if(url.pathname==='/api/robot')body={gateway:{robotConnected:true,transport:'uart'},robot:{}};
   await route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
  });
  const expect=async(text,health)=>{await page.waitForFunction(text=>document.querySelector('#cameraStatus').textContent===text,text);assert.equal(await page.getAttribute('#cameraStatus','data-health'),health);};
  const poll=()=>page.evaluate(()=>refreshCameraStatus());
  await page.goto('http://gladiator.test/dev');await expect('Ready · idle','ok');assert(await page.isVisible('#cameraStatus'));
  assert.match(await page.textContent('#cameraSummary'),/192\.168\.8\.4 · Wi-Fi -40 dBm · masthead-1\.3\.2/);
  assert.match(await page.textContent('#cameraStats'),/Frames: 42 · Stream errors: 0 · Gateway poll errors: 2/);
  await page.locator('#cameraJson').evaluate(e=>e.closest('details').open=true);assert.equal(JSON.parse(await page.textContent('#cameraJson')).cameraReady,true);
  await page.locator('#cameraJson').evaluate(e=>e.closest('details').open=false);
  fs.mkdirSync(out,{recursive:true});await page.screenshot({path:path.join(out,'dev-phone-ready.png'),fullPage:true});
  cam.streaming=true;await poll();await expect('Ready · streaming','ok');
  cam={cameraReady:false,streaming:false,cameraError:0x105};await poll();await expect('Camera not detected','bad');
  await page.setViewportSize({width:320,height:720});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  cam={cameraReady:false,streaming:false,cameraError:0};await poll();await expect('Not ready','bad');
  cam={cameraReady:true,streaming:false,otaUpdating:true};await poll();await expect('Updating firmware','warn');
  cam={cameraReady:true,streaming:false};await poll();await expect('Ready · idle','ok');
  httpStatus=503;await poll();await expect('Ready · idle','ok');
  await page.evaluate(()=>{cameraStatusAt=performance.now()-13000;});await poll();await expect('Status stale','warn');assert.equal(await page.textContent('#cameraJson'),'null');
  httpStatus=502;await poll();await expect('Not reachable','bad');
  httpStatus=200;cam={error:'invalid reply'};await poll();await expect('Not reachable','bad');
  address='';await poll();await expect('Not configured','unknown');
  address='192.168.8.5';cam={cameraReady:true,streaming:false};await poll();await expect('Ready · idle','ok');assert.match(await page.textContent('#cameraSummary'),/192\.168\.8\.5/);
  gatewayDown=true;await poll();await expect('Unknown','warn');assert.equal(await page.textContent('#cameraSummary'),'Gateway unavailable.');
  gatewayDown=false;await poll();await expect('Ready · idle','ok');
  assert.deepEqual(errors,[]);assert.deepEqual(writes,[]);
  console.log('Development camera status passed: overview visibility, readiness/streaming, firmware/Wi-Fi/counters/native diagnostics, busy/stale, failure/recovery, address changes, narrow layout; GET only.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
