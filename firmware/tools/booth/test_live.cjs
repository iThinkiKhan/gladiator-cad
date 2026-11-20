const fs=require('node:fs'),http=require('node:http'),assert=require('node:assert/strict');
const {BoothRunner}=require('./app.js');
const host=process.argv[2];assert.equal(host,'172.23.44.190');
const out=process.argv[3];assert(out);const rows=[],posts=[];
const agent=new http.Agent({keepAlive:true,maxSockets:3});
async function api(path,body){const start=performance.now();return new Promise((resolve,reject)=>{const data=body?JSON.stringify(body):null;const req=http.request({host,port:80,path,method:body?'POST':'GET',agent,headers:body?{'Content-Type':'application/json','Content-Length':Buffer.byteLength(data)}:{}},res=>{let text='';res.on('data',c=>text+=c);res.on('end',()=>{clearTimeout(timer);rows.push({path,ms:Math.round(performance.now()-start),code:res.statusCode});try{if(res.statusCode<200||res.statusCode>=300)throw Error('HTTP '+res.statusCode);resolve(JSON.parse(text));}catch(e){reject(e);}});});req.on('socket',s=>s.setNoDelay(true));req.on('error',e=>{clearTimeout(timer);rows.push({path,ms:Math.round(performance.now()-start),error:e.message});reject(e);});const timer=setTimeout(()=>req.destroy(Error('200 ms request deadline')),200);if(body)posts.push({path,body});req.end(data);});}
const runner=new BoothRunner(api);let status='';runner.onStatus=s=>{status=s;console.log(s);};
(async()=>{const before=await api('/api/status');const field=await api('/api/field');const mast=await api('/api/mast');
 assert(['gateway-2.3.9','gateway-2.4.0','gateway-2.4.1','gateway-2.4.2','gateway-2.4.3'].includes(before.firmware),'Use a verified booth firmware version');assert(field.connected&&field.powerValid&&field.volts>14);assert.equal(field.controller.state,'SAFE');assert(!mast.enabled&&!mast.testActive&&!mast.gpio10OutputEnabled&&!mast.gpio13OutputEnabled);
 const report={before,status:[],results:[]};
 try{
  if(!mast.calibrated){const i=posts.length;await runner.run([{type:'cue',ms:300,left:10,right:10,pan:2,tilt:0}],{motion:true,mast:true,repeats:3,gapMs:1000});assert.match(status,/Mast calibration/);assert.equal(posts.length,i);report.results.push('Uncalibrated coordinated routine blocked before either arm');}
  if(process.argv.includes('--disconnected-tracks')){
   await runner.run([{type:'drive',ms:300,left:10,right:10},{type:'wait',ms:500},{type:'drive',ms:300,left:-10,right:-10}],{motion:true,repeats:3,gapMs:1000});
   assert.match(status,/Routine complete after 3 cycles/);let stopped=false;for(let attempt=0;attempt<10;++attempt){await new Promise(r=>setTimeout(r,50));const current=await api('/api/field');if(!current.controller.armed&&!current.controller.deadman&&!current.controller.leftPercent&&!current.controller.rightPercent){stopped=true;break;}}assert(stopped,'S3 disarm must be confirmed before another run');report.results.push('Three track cycles completed with motors physically disconnected');
  }
  const i=posts.length;runner.onStatus=s=>{status=s;console.log(s);if(s.startsWith('Cycle 3 / until STOP'))void runner.stop('Manual STOP test.');};
  await assert.rejects(runner.run([{type:'face',ms:300,mode:'greeting'}],{repeats:0,gapMs:1000}),/Stopped/);
  assert.equal(runner.cycle,3);assert(!posts.slice(i).some(x=>x.path==='/api/control'||x.path==='/api/mast'));report.results.push('Until STOP advanced two display cycles then cancelled before cycle three command, without motion acquisition');
 }finally{
  if(runner.running||runner.owned||runner.mastOwned)await runner.stop('Test cleanup.');
  await new Promise(r=>setTimeout(r,350));const after=await api('/api/status'),f=await api('/api/field'),m=await api('/api/mast');
  assert.equal(after.bootId,before.bootId);assert.equal(after.peerBootId,before.peerBootId);assert(!f.controller.armed&&!f.controller.deadman&&f.controller.leftPercent===0&&f.controller.rightPercent===0);assert(!m.enabled&&!m.testActive&&!m.gpio10OutputEnabled&&!m.gpio13OutputEnabled);
  report.after=after;report.field=f;report.mast=m;report.requests=rows;report.commands=posts;report.finalStatus=status;fs.writeFileSync(out,JSON.stringify(report,null,2));agent.destroy();
 }
 console.log('PASS live booth checks; all motion outputs OFF; boot IDs unchanged');
})().catch(e=>{console.error(e);agent.destroy();process.exitCode=1;});
