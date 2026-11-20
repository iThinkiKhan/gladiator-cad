// Saved-position operator flow against fixtures only. No hardware access.
const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require(process.env.GLADIATOR_NODE_MODULES+'/playwright');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'shared/FieldPage.h'),'utf8').split('R"HTML(')[1].split(')HTML"')[0];
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844}}),posts=[],errors=[];let revision=12,down=false,fieldInterface='C6 field / UART to S3';
  const m={fresh:true,enabled:false,calibrated:false,positionsReady:true,controlMode:'saved-positions',safe:true,testActive:false,owner:0,session:0,sequence:0,commandedPanUs:1500,commandedTiltUs:1450,positionProfile:{setupRevision:12,pan:{lowUs:500,neutralUs:1500,highUs:2000,reversed:true},tilt:{lowUs:1150,neutralUs:1450,highUs:1450,reversed:false}}};
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('http://gladiator.test/**',async route=>{
   const req=route.request(),u=new URL(req.url());let body={},status=200;
   if(u.pathname==='/')return route.fulfill({contentType:'text/html',body:html});
   if(req.method()==='POST'){const c=req.postDataJSON();posts.push({path:u.pathname,...c});
    if(u.pathname==='/api/mast'){
     if(c.operation===8){m.enabled=true;m.owner=c.session;m.session=765;m.sequence=0;}
     else if(c.operation===0){m.enabled=false;m.owner=0;m.session=0;}
     else m.sequence=c.sequence;
    }
   }
   if(u.pathname==='/api/mast'){if(down)status=502;body=m;}
   else if(u.pathname==='/api/mast/setup')body={schema:1,revision};
   else if(u.pathname==='/api/field')body={requiresKey:false,connected:true,interface:fieldInterface,controller:{s3Ms:1,epoch:1,armed:false,state:'SAFE',battery:'OK'},sensors:{},powerValid:true,volts:15.8};
   else if(u.pathname==='/api/visual')body={schema:1,mode:'ready',cameraIp:'',streamUrl:''};
   else if(u.pathname==='/api/camera/light')body={level:0};
   await route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
  });
  await page.goto('http://gladiator.test/');await page.waitForFunction(()=>document.querySelector('#mastStatus').textContent.includes('saved positions r12'));
  assert.deepEqual(posts,[],'opening page never enables or tests a servo');
  assert(await page.isHidden('#commission'),'C6 sends operators through Hardware setup');
  assert.equal(await page.locator('a[href="/hardware-test"]').count(),1);
  fieldInterface='s3-recovery';
  await page.waitForFunction(()=>!document.getElementById('commission').hidden);
  assert.equal(await page.inputValue('#panMin'),'','Recovery calibration starts with blank measured limits');
  assert.equal(await page.inputValue('#tiltMax'),'');
  fieldInterface='C6 field / UART to S3';
  await page.waitForFunction(()=>document.getElementById('commission').hidden);
  assert(await page.isDisabled('#mastEnable'));assert.match(await page.textContent('#mastStatus'),/1500 µs \/ tilt 1450 µs/);
  await page.check('#enableConfirm');assert(!(await page.isDisabled('#mastEnable')));
  await page.click('#mastEnable');await page.waitForFunction(()=>document.querySelector('#mastStatus').textContent.startsWith('ARMED'));
  await page.waitForFunction(()=>!document.querySelector('[data-aim=right]').disabled);
  assert(posts.some(c=>c.operation===8));assert(!posts.some(c=>c.path==='/api/mast/config'));
  assert(posts.some(c=>c.operation===5&&c.pan===5),'rate is percent of recorded span, never guessed degrees');
  assert(await page.isDisabled('#mastScan'));assert(!(await page.isVisible('#mastMove')));
  await page.locator('[data-aim=right]').hover();await page.mouse.down();await page.waitForTimeout(80);const released=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/api/mast')&&r.request().postDataJSON().operation===1);await page.mouse.up();await released;
  assert(posts.some(c=>c.operation===6&&c.pan===1&&c.tilt===0));assert(posts.some(c=>c.operation===1));
  await page.locator('[data-aim=down]').hover();await page.mouse.down();await page.waitForTimeout(80);const releasedTilt=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/api/mast')&&r.request().postDataJSON().operation===1);await page.mouse.up();await releasedTilt;
  assert(posts.some(c=>c.operation===6&&c.pan===0&&c.tilt===-1));
  const centered=page.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/api/mast')&&r.request().postDataJSON().operation===2);await page.click('#mastCenter');await centered;assert(posts.some(c=>c.operation===2&&c.pan===0&&c.tilt===0));
  if(process.env.GLADIATOR_FIXTURE_SCREENSHOT)await page.screenshot({path:process.env.GLADIATOR_FIXTURE_SCREENSHOT,fullPage:true});
  await page.click('#mastStop');await page.waitForFunction(()=>document.querySelector('#mastStatus').textContent.startsWith('DISARMED'));
  assert(!(await page.isChecked('#enableConfirm')));assert(await page.isDisabled('[data-aim=right]'));
  revision=13;await page.check('#enableConfirm');const count=posts.filter(c=>c.operation===8).length;await page.click('#mastEnable');
  await page.waitForFunction(()=>document.querySelector('#mastReply').textContent.includes('Saved positions changed'));
  assert.equal(posts.filter(c=>c.operation===8).length,count,'changed saved record never arms stale positions');
  revision=12;await page.check('#enableConfirm');await page.click('#mastEnable');await page.waitForFunction(()=>!document.querySelector('[data-aim=right]').disabled);
  down=true;await page.waitForFunction(()=>document.querySelector('#mastReply').textContent.includes('connection lost'));
  down=false;m.enabled=false;m.owner=0;m.session=0;await page.waitForFunction(()=>document.querySelector('#mastStatus').textContent.startsWith('DISARMED'));
  assert(await page.isDisabled('#mastEnable'));assert(!(await page.isChecked('#enableConfirm')));
  assert(!posts.some(c=>c.path==='/api/mast/config'),'normal use never enters commissioning');assert.deepEqual(errors,[]);
  console.log('Saved-position UI passed: recorded positions, deliberate arm op8, correct speed/directions, hold/center/disarm, no tests/scan/angle targets, changed-record rejection, disconnect/recovery without auto-arm.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
