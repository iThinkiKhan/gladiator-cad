// Main-page camera health against fixtures only; no hardware requests.
const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require(process.env.GLADIATOR_NODE_MODULES+'/playwright');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'shared/FieldPage.h'),'utf8').split('R"HTML(')[1].split(')HTML"')[0];
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844}}),errors=[],writes=[];
  let address='192.168.8.4',gatewayDown=false,httpStatus=200,cam={cameraReady:true,streaming:false,rssi:-40};
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('http://gladiator.test/**',async route=>{
   const req=route.request(),url=new URL(req.url());let body={},status=200;
   if(req.method()!=='GET')writes.push(url.pathname);
   if(url.pathname==='/')return route.fulfill({contentType:'text/html',body:html});
   if(url.pathname==='/api/visual'){
    if(gatewayDown)status=502;
    body={schema:1,mode:'ready',cameraIp:address,streamUrl:address?'http://'+address+':81/stream':''};
   }else if(url.pathname==='/api/camera/status'){status=httpStatus;body=cam;}
   else if(url.pathname==='/api/camera/light')body={level:0};
   else if(url.pathname==='/api/mast')body={fresh:true,enabled:false,calibrated:false,safe:true};
   else if(url.pathname==='/api/field')body={connected:false,requiresKey:false};
   await route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
  });
  const expect=async(text,health)=>{
   await page.waitForFunction(text=>document.querySelector('#cameraStatus').textContent.includes(text),text);
   assert.equal(await page.getAttribute('#cameraStatus','data-health'),health);
  };
  const poll=async()=>{await page.evaluate(()=>{cameraPollAt=0;return refreshCameraStatus();});};
  await page.goto('http://gladiator.test/');await expect('Ready · idle · 192.168.8.4 · Wi-Fi -40 dBm','ok');
  assert(await page.isVisible('#cameraStatus'));
  assert.deepEqual(writes,[],'opening the page only reads camera status');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'fits phone width');
  const out=path.join(root,'diagnostics/camera-status-20261109');fs.mkdirSync(out,{recursive:true});
  await page.screenshot({path:path.join(out,'phone-ready.png'),fullPage:true});
  cam.streaming=true;await poll();await expect('Ready · streaming','ok');
  cam={cameraReady:false,streaming:false,cameraError:0x105};await poll();await expect('Camera not detected','bad');
  cam={cameraReady:false,streaming:false,cameraError:0};await poll();await expect('Not ready','bad');
  cam={cameraReady:true,streaming:false,otaUpdating:true};await poll();await expect('Updating firmware','warn');
  cam={cameraReady:true,streaming:false};await poll();await expect('Ready · idle','ok');
  httpStatus=503;await poll();await expect('Ready · idle','ok');
  await page.evaluate(()=>{cameraStatusAt=performance.now()-13000;});await poll();await expect('Status stale','warn');
  httpStatus=502;await poll();await expect('Not reachable','bad');
  httpStatus=200;cam={error:'invalid status'};await poll();await expect('Not reachable','bad');
  cam={cameraReady:true,streaming:false};await poll();await expect('Ready · idle','ok');
  address='';await page.evaluate(()=>refreshVisual());await expect('Not configured','unknown');
  address='192.168.8.5';await page.evaluate(()=>refreshVisual());await expect('192.168.8.5','ok');
  gatewayDown=true;await page.evaluate(()=>refreshVisual());await expect('Unknown · gateway unavailable','warn');
  gatewayDown=false;await page.evaluate(()=>refreshVisual());await expect('Ready · idle','ok');
  assert.deepEqual(writes,[],'status transitions never send commands');assert.deepEqual(errors,[]);
  console.log('Camera status passed: idle/streaming, sensor failure, update, busy/stale, unreachable, invalid reply, address change, gateway loss/recovery, phone layout; GET only.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
