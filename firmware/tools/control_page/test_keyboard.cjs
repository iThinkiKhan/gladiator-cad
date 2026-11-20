// Keyboard driving and desktop layout of the C6 control page. Fixtures only; no hardware.
// Usage: node test_keyboard.cjs <out-folder> [still.jpg used as a fake video frame]
const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require(process.env.GLADIATOR_NODE_MODULES+'/playwright');
const root=path.resolve(__dirname,'..','..'),out=path.resolve(process.argv[2]||path.join(__dirname,'out'));fs.mkdirSync(out,{recursive:true});
const still=process.argv[3]&&fs.existsSync(process.argv[3])?fs.readFileSync(process.argv[3]):null;
const html=fs.readFileSync(path.join(root,'gateway/src/ControlPage.h'),'utf8').split('R"HTML(')[1].split(')HTML"')[0];
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.GLADIATOR_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:900}}),errors=[],commands=[];page.on('pageerror',e=>errors.push(e.message));
  let epoch=7,armed=false,client=0,last=0;const key='k'.repeat(32),now=()=>Date.now()%10000000;
  const meta={health:'OK',ageMs:12,rateHz:20,hasSample:true};
  const controller=()=>{if(armed&&now()-last>350){armed=false;client=0;++epoch;}const driving=armed&&commands.length&&commands.at(-1).deadman===1;return {s3Ms:now(),epoch,client,armed,state:driving?'DRIVE':armed?'ARMED':'SAFE',battery:'OK',power:25};};
  await page.route('http://gladiator.test/**',async route=>{
   const req=route.request(),u=new URL(req.url());let body='{}',type='application/json',status=200;
   if(u.pathname==='/')return route.fulfill({contentType:'text/html',body:html});
   if(u.pathname==='/stream')return still?route.fulfill({contentType:'image/jpeg',body:still}):route.fulfill({status:404,body:''});
   if(u.pathname==='/api/field')body=JSON.stringify({requiresKey:true,connected:true,interface:'C6 field · UART to S3',transport:'UART',telemetryAgeMs:6,powerValid:true,volts:15.84,controller:controller(),sensors:{power:{meta},imu:{meta,derived:{valid:true,headingValid:true,yawDeg:63}},tofFront:{meta,derived:{valid:true,nearestMm:1240}},presence:{meta:{...meta,health:'OFFLINE'}}}});
   else if(u.pathname==='/api/control'){const c=req.postDataJSON();if(req.headers()['x-gladiator-key']!==key){status=401;body='key';}else{commands.push(c);if(c.epoch===epoch){if(c.operation===1&&!armed){armed=true;client=c.client;}if(c.operation===0){armed=false;client=0;++epoch;}last=now();}body='{"queued":true}';}}
   else if(u.pathname==='/api/visual')body=JSON.stringify({schema:1,mode:'ready',cameraIp:'192.168.8.2',streamUrl:'http://gladiator.test/stream'});
   else if(u.pathname==='/api/camera/status')body=JSON.stringify({cameraReady:true,streaming:false,rssi:-41});
   else if(u.pathname==='/api/camera/light')body='{"level":0}';
   else if(u.pathname==='/api/mast')body=JSON.stringify({fresh:true,enabled:false,calibrated:false,positionsReady:true,controlMode:'saved-positions',safe:true,testActive:false,owner:0,session:0,sequence:0,commandedPanUs:1500,commandedTiltUs:1450,positionProfile:{setupRevision:14}});
   await route.fulfill({status,contentType:type,body});
  });
  const drive=()=>commands.filter(c=>c.operation===2);
  await page.goto('http://gladiator.test/');await page.waitForFunction(()=>document.querySelector('#state').textContent==='SAFE');
  await page.keyboard.down('KeyW');await sleep(250);await page.keyboard.up('KeyW');
  assert.equal(commands.length,0,'keys never drive (or arm) an unarmed page');
  await page.locator('#keyBox summary').click();await page.locator('#key').fill(key);
  await page.locator('#key').press('KeyW');await page.locator('#key').press('KeyD');assert.equal(commands.length,0,'typing in a field never drives');
  await page.locator('#keyBox summary').click();
  await page.click('#arm');await page.waitForFunction(()=>document.querySelector('#reply').textContent.startsWith('Armed'));
  await page.keyboard.down('KeyW');await sleep(300);
  assert(drive().some(c=>c.deadman===1&&c.left===25&&c.right===25),'W drives forward at the selected power');
  assert(await page.locator('[data-drive=f].held').count()===1,'held key lights the pad');
  if(still){await page.click('#videoToggle');await page.waitForFunction(()=>document.querySelector('#cameraFeed').naturalWidth>0);}
  await page.waitForFunction(()=>document.body.dataset.state==='DRIVE');await sleep(200);
  await page.screenshot({path:path.join(out,'control-desktop-driving.png')});
  const n=drive().length;await page.keyboard.up('KeyW');await sleep(150);
  assert(drive().slice(n).some(c=>c.deadman===0&&c.left===0&&c.right===0),'releasing the key coasts');
  await page.keyboard.press('Digit2');assert.equal(await page.inputValue('#speed'),'50');
  await page.keyboard.down('ArrowLeft');await sleep(250);assert(drive().some(c=>c.deadman===1&&c.left===-50&&c.right===50),'arrow left turns at 50');await page.keyboard.up('ArrowLeft');
  await page.keyboard.down('KeyA');await page.keyboard.down('KeyD');await sleep(200);assert(!drive().some(c=>c.deadman===1&&c.left===50&&c.right===-50),'second key is ignored while one is held');
  await page.keyboard.up('KeyD');await page.keyboard.up('KeyA');await sleep(150);
  await page.focus('#arm');await page.keyboard.press('Space');await sleep(200);
  assert(commands.some(c=>c.operation===0),'Space disarms');assert(!armed,'S3 fixture disarmed');
  const ops1=commands.filter(c=>c.operation===1).length;assert.equal(ops1,1,'Space on a focused ARM button never re-arms');
  await page.waitForFunction(()=>document.querySelector('#state').textContent==='SAFE');await sleep(300);
  await page.screenshot({path:path.join(out,'control-desktop-safe.png')});
  await page.setViewportSize({width:1100,height:900});await sleep(200);await page.screenshot({path:path.join(out,'control-1100.png'),fullPage:true});
  assert.deepEqual(errors,[]);console.log('Keyboard UI passed: no drive unarmed or while typing, W/arrows hold-to-run with pad highlight, release coasts, 1-4 power, one key at a time, Space disarms without re-arming.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
