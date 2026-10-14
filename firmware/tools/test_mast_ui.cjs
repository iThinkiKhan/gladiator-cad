// Real browser, in-memory robot only. Never opens the physical gateway.
const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require(process.env.GLADIATOR_NODE_MODULES+'/playwright');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'shared/FieldPage.h'),'utf8').split('R"HTML(')[1].split(')HTML"')[0];
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.GLADIATOR_CHROME||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844}}),errors=[],posts=[];
  page.setDefaultTimeout(3000);
  page.on('pageerror',e=>errors.push(e.message));
  let fail=false,mast={schema:1,fresh:true,enabled:false,calibrated:false,referenced:false,session:0,sequence:0,safe:true,reason:'boot: position unknown',panMinDeg:-5,panMaxDeg:0,tiltMinDeg:-3,tiltMaxDeg:3};
  await page.route('http://gladiator.test/**',async route=>{
   const req=route.request(),url=new URL(req.url());let status=200,type='application/json',body={};
   if(url.pathname==='/'){body=html;type='text/html';}
   else if(url.pathname==='/api/field')body={connected:true,requiresKey:true,controller:{state:'SAFE',s3Ms:1,epoch:1,battery:'OK',armed:false},sensors:{}};
   else if(url.pathname==='/api/mast'){
    if(fail){status=503;body={error:'fixture offline'};}
    else if(req.method()==='POST'){const c=JSON.parse(req.postData());posts.push(c);assert.equal(req.headers()['x-gladiator-key'],'a'.repeat(32));
      assert.equal(c.session,mast.session);assert(c.sequence>mast.sequence);mast.sequence=c.sequence;
      if(c.operation===0){mast.enabled=false;mast.session=0;}
      body={queued:true};status=202;
    }else body=mast;
   }else if(url.pathname==='/api/visual'){status=404;}
   await route.fulfill({status,contentType:type,body:typeof body==='string'?body:JSON.stringify(body)});
  });
  await page.goto('http://gladiator.test/');await page.waitForTimeout(350);
  assert.equal(posts.length,0);assert(await page.locator('#mastMove').isDisabled());
  await page.locator('#keyBox summary').click();await page.locator('#key').fill('a'.repeat(32));
  mast={...mast,enabled:true,calibrated:true,referenced:true,session:99};
  await page.waitForTimeout(250);assert.equal(posts.length,0); // USB reference alone cannot start a sweep.
  await page.locator('#mastMaintain').check();await page.waitForTimeout(300);
  assert(posts.some(c=>c.operation===4));assert(!posts.some(c=>c.operation===2||c.operation===3));
  assert.equal(await page.locator('#mastPan').getAttribute('max'),'0');
  await page.locator('#mastPan').fill('-1.5');await page.locator('#mastTilt').fill('1');await page.locator('#mastMove').click();
  await page.waitForTimeout(200);assert(posts.some(c=>c.operation===2&&c.pan===-15&&c.tilt===10));
  await page.locator('#mastScan').click();await page.waitForTimeout(150);assert(posts.some(c=>c.operation===3));
  fail=true;await page.waitForTimeout(500);assert.equal(await page.locator('#mastMaintain').isChecked(),false);
  const count=posts.length;fail=false;mast={...mast,enabled:false,session:0};await page.waitForTimeout(350);
  assert.equal(posts.length,count);assert(await page.locator('#mastMove').isDisabled());
  mast={...mast,enabled:true,session:100,sequence:0};await page.waitForTimeout(250);assert.equal(posts.length,count);
  await page.locator('#mastMaintain').check();await page.waitForTimeout(200);
  await page.evaluate(()=>window.dispatchEvent(new Event('blur')));await page.waitForTimeout(200);
  assert.equal(await page.locator('#mastMaintain').isChecked(),false);assert(posts.some(c=>c.operation===0));
  assert.deepEqual(errors,[]);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  await page.screenshot({path:path.join(root,'build-output/mast-field.png'),fullPage:true});
  console.log('Mast browser passed: no startup commands, explicit keepalive, calibrated bounds, signed head angles, scan, stop, loss and no reconnect resume.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
