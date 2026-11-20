// Field page spotlight controls against an in-memory CAM fixture. No hardware access.
const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require(process.env.GLADIATOR_NODE_MODULES+'/playwright');
const root=path.resolve(__dirname,'..');
const html=file=>fs.readFileSync(path.join(root,file),'utf8').split('R"HTML(')[1].split(')HTML"')[0];
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.GLADIATOR_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const context=await browser.newContext({viewport:{width:390,height:844}}),page=await context.newPage(),errors=[],posts=[];
  page.on('pageerror',e=>errors.push(e.message));
  let level=0,busyOnce=false,camDown=false,mastPosts=0;
  const mast={fresh:true,enabled:false,calibrated:true,safe:true,testActive:false,owner:0,session:0,sequence:0,reason:'off',panMinDeg:-20,panMaxDeg:180,tiltMinDeg:-38,tiltMaxDeg:34};
  await context.route('http://gladiator.test/**',async route=>{
   const req=route.request(),url=new URL(req.url());let body='{}',status=200,type='application/json';
   if(url.pathname==='/'){body=html('shared/FieldPage.h');type='text/html';}
   else if(url.pathname==='/api/mast'){if(req.method()==='POST')++mastPosts;body=JSON.stringify(mast);}
   else if(url.pathname==='/api/camera/light'){
    if(camDown){status=502;body='{"error":"Camera unavailable or settings rejected"}';}
    else if(req.method()==='POST'&&busyOnce){busyOnce=false;status=503;type='text/plain';body='Camera request already pending';}
    else{if(req.method()==='POST'){const b=JSON.parse(req.postData());posts.push(b.level);level=b.level;}body=JSON.stringify({level,remainingMs:level?120000:0,timeoutMs:120000,maxDutyPercent:50});}
   }
   else{status=404;type='text/plain';body='not found';}
   await route.fulfill({status,contentType:type,body});
  });
  const status=()=>page.textContent('#lightStatus');
  const settle=async want=>{for(let i=0;i<40;i++){if((await status())===want)return;await page.waitForTimeout(50);}assert.strictEqual(await status(),want);};
  await page.goto('http://gladiator.test/');
  await settle('Off');
  assert(await page.isVisible('#lightBox'),'spotlight is in the visible Aim camera panel');
  assert(await page.isDisabled('[data-aim="up"]'),'aim pad stays locked while the mast is off');
  for(const id of ['#lightLevel','#lightFull','#lightOff'])assert(!(await page.isDisabled(id)),id+' works without enabling the mast');
  // Slider release sends one level; dragging does not.
  await page.$eval('#lightLevel',e=>{e.value=60;e.dispatchEvent(new Event('input'));});
  assert.strictEqual(await page.textContent('#lightLabel'),'60%');assert.deepStrictEqual(posts,[]);
  await page.$eval('#lightLevel',e=>e.dispatchEvent(new Event('change')));
  await settle('On · 60%');assert.deepStrictEqual(posts,[60]);
  // A busy gateway proxy (503) is retried.
  busyOnce=true;await page.click('#lightFull');await settle('On · 100%');assert.deepStrictEqual(posts,[60,100]);
  await page.click('#lightOff');await settle('Off');assert.deepStrictEqual(posts,[60,100,0]);
  await page.click('#lightFull');await settle('On · 100%');const before=posts.length;
  // Hiding the page turns the light off.
  await page.evaluate(()=>{Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'));});
  for(let i=0;i<40&&posts[posts.length-1]!==0;i++)await page.waitForTimeout(50);
  assert.strictEqual(posts[posts.length-1],0,'hidden page sends light off');assert(posts.length>before);
  assert(mastPosts>=1,'hidden page also sends mast off as before');
  // Camera unreachable: clear message, no page error.
  await page.evaluate(()=>{Object.defineProperty(document,'hidden',{value:false,configurable:true});});
  camDown=true;await page.click('#lightFull');
  for(let i=0;i<40&&!(await status()).startsWith('Unavailable');i++)await page.waitForTimeout(50);
  assert((await status()).startsWith('Unavailable: '),await status());
  // Renewal every 45 s while on and visible (fake page clock from load).
  camDown=false;const p2=await context.newPage();p2.on('pageerror',e=>errors.push(e.message));await p2.clock.install();await p2.goto('http://gladiator.test/');
  const tick=async(ok,ms=50)=>{for(let i=0;i<80;i++){if(await ok())return true;await p2.clock.runFor(ms);await p2.waitForTimeout(10);}return ok();};
  assert(await tick(async()=>(await p2.textContent('#lightStatus'))==='Off'));
  await p2.click('#lightFull');assert(await tick(async()=>(await p2.textContent('#lightStatus'))==='On · 100%'));
  const sent=posts.length;await p2.clock.runFor(30000);await p2.waitForTimeout(200);assert.strictEqual(posts.length,sent,'no renewal before 45 s');
  assert(await tick(async()=>posts.length>sent,1000),'renewal after 45 s');assert.strictEqual(posts[posts.length-1],100);
  await p2.close();
  assert.deepStrictEqual(errors,[]);
  console.log('Spotlight UI passed: read on load, 45 s renewal, works with mast off, slider sends on release, 503 retry, off button, off when hidden, camera-down message.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
