const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const script=fs.readFileSync(require('node:path').join(__dirname,'../cam/src/MaintenancePage.h'),'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const flush=()=>new Promise(resolve=>setImmediate(resolve));
async function scenario(rollback=false){
  const elements=new Map(),calls=[];
  const element=id=>{if(!elements.has(id))elements.set(id,{value:'',files:[],disabled:false,textContent:''});return elements.get(id)};
  element('key').value='0123456789abcdef0123456789abcdef';
  let state={firmware:'old',otaSlot:'app0',bootId:1,uptimeMs:60000,otaEnabled:true,otaPendingVerification:false,otaMaxBytes:1966080,recoverySsid:'Gladiator-CAM-test'};
  let xhr;
  class XHR{
    constructor(){this.upload={};this.headers={};xhr=this;}
    open(method,url){this.method=method;this.url=url;}
    setRequestHeader(k,v){this.headers[k]=v;}
    send(file){this.file=file;}
  }
  const context=vm.createContext({document:{getElementById:element},AbortSignal,XMLHttpRequest:XHR,console,Date,setTimeout:f=>{f();},fetch:async(url,opts={})=>{
    calls.push({url,opts});
    if(url==='/api/confirm')state.otaPendingVerification=false;
    return {ok:true,json:async()=>({...state}),text:async()=>''};
  }});
  vm.runInContext(script,context);await flush();
  await element('upload').onclick();assert.match(element('reply').textContent,/Select a CAM/);assert(!xhr);
  element('image').files=[{size:1024}];element('key').value='wrong';
  await element('upload').onclick();assert.match(element('reply').textContent,/32-character/);assert(!xhr);
  element('key').value='0123456789abcdef0123456789abcdef';
  await element('upload').onclick();assert.equal(xhr.url,'/api/ota');assert.equal(xhr.method,'POST');assert.equal(xhr.headers['X-Gladiator-Key'],element('key').value);assert.equal(element('upload').disabled,true);
  xhr.status=401;xhr.responseText='Key rejected';xhr.onload();assert.equal(element('upload').disabled,false);assert.equal(element('reply').textContent,'Key rejected');
  await element('upload').onclick();xhr.status=200;
  state={...state,bootId:2,uptimeMs:6000,otaSlot:rollback?'app0':'app1',firmware:rollback?'old':'new',otaPendingVerification:!rollback};
  xhr.onload();await flush();await flush();
  if(rollback){assert.match(element('reply').textContent,/previous firmware/);assert(!calls.some(c=>c.url==='/api/confirm'));}
  else {assert.match(element('reply').textContent,/new confirmed/);const confirmation=calls.find(c=>c.url==='/api/confirm');assert.equal(confirmation.opts.headers['X-Gladiator-Key'],element('key').value);}
  assert.equal(element('upload').disabled,false);
  element('ssid').value='test-network';element('password').value='test-password';element('gateway').value='http://192.168.8.1';
  await element('save').onclick();const config=calls.find(c=>c.url==='/api/config');assert.equal(config.opts.method,'POST');assert.deepEqual(JSON.parse(config.opts.body),{ssid:'test-network',password:'test-password',gatewayUrl:'http://192.168.8.1'});
}
(async()=>{await scenario();await scenario(true);console.log('CAM maintenance browser checks passed (auth, rejected uploads, new-slot confirmation, rollback reporting, Wi-Fi settings).');})().catch(e=>{console.error(e);process.exitCode=1});
