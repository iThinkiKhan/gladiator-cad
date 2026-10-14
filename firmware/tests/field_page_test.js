const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(require('node:path').join(__dirname,'../shared/FieldPage.h'),'utf8');
const script=source.match(/<script>([\s\S]*?)<\/script>/)[1];
const elements=new Map(),events=new Map(),calls=[];
const element=id=>{if(!elements.has(id))elements.set(id,{id,hidden:true,disabled:true,value:'',textContent:'',style:{},parentElement:{},append(){},after(){},before(){},removeAttribute(k){delete this[k]}});return elements.get(id)};
element('expression').value='greeting';element('key').value='test-key';
let visual={schema:1,mode:'ready',fresh:true,override:false,cameraIp:'192.168.8.2',streamUrl:'http://192.168.8.2:81/stream'};
let holdControl=false,releaseControl=null;
const document={createElement:()=>({innerHTML:""}),getElementById:element,querySelectorAll:()=>[],querySelector:()=>element('h1'),addEventListener:(k,f)=>events.set(k,[...(events.get(k)||[]),f]),hidden:false,activeElement:null};
const window={addEventListener(){}};
const context=vm.createContext({document,window,location:{search:'',origin:'http://gateway'},parent:{postMessage(){}},crypto:require('node:crypto').webcrypto,Uint32Array,URLSearchParams,performance:{now:()=>100},AbortSignal,console,setTimeout(){},setInterval(){},
fetch:async(url,opts={})=>{calls.push({url,opts});if(url==='/api/control'&&holdControl)await new Promise(resolve=>releaseControl=resolve);return {ok:true,status:200,json:async()=>url==='/api/visual'?visual:{connected:true,requiresKey:true,transport:'UART',controller:{state:'SAFE',battery:'OK',s3Ms:50,epoch:1,armed:false,client:0},sensors:{}},text:async()=>'{"accepted":true}'}}});
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
  vm.runInContext(script,context);await flush();
  assert.equal(element('visualPanel').hidden,false);assert.equal(element('videoToggle').disabled,false);
  assert.equal(element('cameraFeed').src,undefined); // Video starts only on an explicit click.
  element('videoToggle').onclick();assert.equal(element('cameraFeed').src,visual.streamUrl);
  element('setExpression').onclick();await flush();
  const command=calls.find(x=>x.url==='/api/visual'&&x.opts.method==='POST');assert(command);
  assert.deepEqual(JSON.parse(command.opts.body),{mode:'greeting',leaseMs:30000});assert.equal(command.opts.headers['X-Gladiator-Key'],'test-key');
  element('cameraIp').value='192.168.8.5';element('saveCamera').onclick();await flush();assert(calls.some(x=>x.url==='/api/visual/config'));
  document.hidden=true;events.get('visibilitychange').forEach(f=>f());assert.equal(element('cameraFeed').src,undefined);assert.equal(element('cameraFeed').hidden,true);
  document.hidden=false;element('videoToggle').onclick();element('cameraFeed').onerror();assert.equal(element('cameraFeed').src,undefined);assert.match(element('videoStatus').textContent,/unavailable/);
  element('videoToggle').onclick();visual={...visual,streamUrl:'http://192.168.8.5:81/stream',cameraIp:'192.168.8.5'};vm.runInContext('refreshVisual()',context);await flush();assert.equal(element('cameraFeed').src,undefined);
  assert.equal(calls.filter(x=>x.url==='/api/control').length,0); // Expression/video controls cannot drive motors.
  holdControl=true;vm.runInContext('armed=true;held=null;command(2)',context);await flush();
  vm.runInContext('command(0)',context);await flush();
  assert.equal(calls.filter(x=>x.url==='/api/control').length,1,'no parallel control writes');
  holdControl=false;releaseControl();await flush();await flush();
  const requests=calls.filter(x=>x.url==='/api/control').map(x=>JSON.parse(x.opts.body));
  assert.deepEqual(requests.map(x=>x.operation),[2,0],'busy DISARM is sent after the in-flight command');
  assert(requests.every(x=>x.left===0&&x.right===0&&x.deadman===0),'queued stop never replays held motion');
  console.log('Browser script checks passed (opt-in video, stop-on-hide/error, display commands, camera address changes, motion isolation).');
})().catch(e=>{console.error(e);process.exitCode=1});
