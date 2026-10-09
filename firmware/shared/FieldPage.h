#pragma once
// The same phone interface is served by C6 and by S3 recovery. S3 validates all
// commands. No cached armed state, motion replay, automatic arm or retry queue.
static const char FIELD_PAGE[]=R"HTML(<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gladiator · Field</title>
<style>:root{color-scheme:dark;font-family:system-ui}*{box-sizing:border-box}pre{white-space:pre-wrap;overflow-wrap:anywhere}body{background:#0c131a;color:#eaf1f5;max-width:480px;margin:auto;padding:20px}h1{margin-bottom:4px}small,p{color:#a6b8c4}section{background:#17232d;padding:18px;border-radius:16px;margin:16px 0}[hidden]{display:none!important}.facts{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.facts strong{display:block;margin-top:8px}#warnings{color:#ffce7b;white-space:pre-line}iframe{border:0}button,input,select{font:inherit;padding:14px;border:0;border-radius:10px}button{background:#304654;color:white;touch-action:none}button:disabled{opacity:.35}.pad{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:15px}.pad button{min-height:76px;padding:8px 2px}.arm{background:#e8ad42;color:#111}.stop{background:#bb3944}#state{font-size:28px;font-weight:700}.row{display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px}a{color:#82d6ec}input{box-sizing:border-box;width:100%;background:#0c131a;color:white}output{display:block;margin-top:12px;min-height:24px}</style>
<h1>Gladiator</h1><small>Interface v1 · Field</small><p id="link">Connecting…</p><section><div class="row"><span id="state">UNKNOWN</span><span id="power">—</span></div><p id="owner">S3 controls motors and safety.</p><p id="warnings" role="status">Waiting for robot state.</p><div class="row"><button id="arm" class="arm" disabled>ARM</button><button id="stop" class="stop">DISARM</button><select id="speed" aria-label="Drive power"><option value="25">25%</option><option value="50">50%</option><option value="75">75%</option><option value="100">100%</option><option value="255">Overdrive</option></select></div><div class="pad"><span></span><button data-drive="f" disabled>Forward</button><span></span><button data-drive="l" disabled>Left</button><button data-drive="s" disabled>Coast</button><button data-drive="r" disabled>Right</button><span></span><button data-drive="b" disabled>Reverse</button></div><output id="reply" aria-live="polite"></output><small>Hold to move. Release to coast. After any timeout or reconnect, arm again.</small></section>
<section><div class="row"><span id="quality">UNKNOWN</span><strong id="transport">NONE</strong></div><p id="battery">Battery UNKNOWN</p><div class="facts"><div><small>Heading</small><strong id="heading">—</strong></div><div><small>Range</small><strong id="range">—</strong></div><div><small>Presence</small><strong id="presence">UNKNOWN</strong></div></div></section>
<details id="diagnostics"><summary>Diagnostics</summary><p id="reportedPower"></p><pre id="sensorHealth"></pre><details id="trackTest" hidden><summary>Independent track test</summary><p>Values are signed percent. Hold Test tracks to run; release to coast. S3 validates every request.</p><label>Left<input id="testLeft" type="number" min="-100" max="100" value="0"></label><label>Right<input id="testRight" type="number" min="-100" max="100" value="0"></label><button data-drive="test" disabled>Test tracks</button></details></details>
<p><a id="dev" href="/dev">Development & diagnostics</a></p><details id="keyBox"><summary>Field access key</summary><p>Use the C6 maintenance key from USB provisioning. It stays in this page's memory.</p><input id="key" type="password" maxlength="32" autocomplete="off" aria-label="Field access key"></details>
<script>
const $=id=>document.getElementById(id);let snapshot=null,held=null,armed=false,arming=false,busy=false,seq=0,epoch=0,updated=0,lastRejected=0;
const random=new Uint32Array(1);crypto.getRandomValues(random);const client=random[0]||1;
function reset(message){held=null;armed=false;arming=false;render();if(message)$('reply').textContent=message;}
function render(){document.querySelectorAll('[data-drive]').forEach(b=>b.disabled=!armed);$('arm').disabled=armed||arming||!snapshot?.connected||!['SAFE','ARMED','DRIVE'].includes(snapshot?.controller?.state)||snapshot?.controller?.batteryLockout;}
async function command(operation){
  if(busy){if(operation===0)reset('Stopped locally; watchdog will disarm.');return;}
  if(!snapshot?.controller||performance.now()-updated>250){reset('State is stale. Reconnect and arm again.');return;}
  busy=true;let l=0,r=0,p=Number($('speed').value);if(held==='f')l=r=p;if(held==='b')l=r=-p;if(held==='l'){l=-p;r=p;}if(held==='r'){l=p;r=-p;}if(held==='test'){l=Number($('testLeft').value);r=Number($('testRight').value);}const overdrive=p===255?1:0;if(overdrive){p=100;l=Math.max(-100,Math.min(100,l));r=Math.max(-100,Math.min(100,r));}
  const body={epoch,client,sequence:++seq,observedMs:snapshot.controller.s3Ms,operation,deadman:operation===2&&held!==null?1:0,overdrive,power:p,left:operation===2?l:0,right:operation===2?r:0};
  try{const response=await fetch('/api/control',{method:'POST',headers:{'Content-Type':'application/json','X-Gladiator-Key':$('key').value.trim()},body:JSON.stringify(body),signal:AbortSignal.timeout(250)});const text=await response.text();if(!response.ok)throw Error(text);const result=JSON.parse(text);if(result.result&&result.result!==0)throw Error('S3 rejected command');}
  catch(e){reset('Control interrupted. Release, then arm again.');}finally{busy=false;}
}
async function refresh(){
 try{const response=await fetch('/api/field',{cache:'no-store',signal:AbortSignal.timeout(400)});if(!response.ok)throw Error();const s=await response.json(),c=s.controller;
   if(!s.connected||!c){snapshot=s;reset('S3 unavailable.');$('state').textContent='UNKNOWN';}
   else{if(epoch!==c.epoch){reset(epoch?'Session ended. Arm again.':'');epoch=c.epoch;}snapshot=s;updated=performance.now();
     const ours=c.armed&&c.client===client;if(arming&&ours){armed=true;arming=false;$('reply').textContent='Armed. Hold a direction.';}
     if(armed&&!ours)reset('Control ownership ended. Arm again.');
     if(s.lastResult?.client===client&&s.lastResult.result&&s.lastResult.sequence>lastRejected){lastRejected=s.lastResult.sequence;reset('S3 rejected control: '+(['accepted','session expired','another controller owns motion','invalid or inhibited command','duplicate command','stale command','link offline'][s.lastResult.result]||'unknown result'));}
     $('state').textContent=c.state||'UNKNOWN';$('owner').textContent=ours?'Your field session':c.armed?'Another controller owns the robot':'Ready to arm';
     if(c.batteryLockout)$('owner').textContent='Battery lockout · motors inhibited';
     $('power').textContent=s.powerValid&&Number.isFinite(s.volts)?(c.benchPower?'BENCH · ':'')+Number(s.volts).toFixed(2)+' V':'Power unavailable';
   }
   $('keyBox').hidden=!s.requiresKey;$('dev').href=s.requiresKey?'/dev':'/service';$('dev').textContent=s.requiresKey?'Open development interface':'Open recovery service';$('link').textContent=s.requiresKey?'Field connection':'Recovery field connection';drawField(s);render();
 }catch(e){snapshot=null;reset('Connection lost. Arm again after recovery.');$('state').textContent='UNKNOWN';drawField(null);}setTimeout(refresh,100);
}
$('arm').onclick=()=>{if(!snapshot?.connected)return;held=null;epoch=snapshot.controller.epoch;arming=true;render();command(1);setTimeout(()=>{if(arming)reset('No arm confirmation. Try again.');},600);};
$('stop').onclick=()=>{held=null;command(0);reset('DISARM requested. Waiting for S3 state.');};
function release(){held=null;if(armed)command(2);}
document.querySelectorAll('[data-drive]').forEach(b=>{b.onpointerdown=e=>{e.preventDefault();if(!armed)return;b.setPointerCapture(e.pointerId);held=b.dataset.drive;command(2);};b.onpointerup=release;b.onpointercancel=release;b.onlostpointercapture=release;});
$('speed').onchange=release;window.onblur=()=>{held=null;command(0);reset('Paused. Arm again.');};document.onvisibilitychange=()=>{if(document.hidden)window.onblur();};
function drawField(s){
 const fresh=!!s?.connected,c=s?.controller,r=s?.sensors||{},good=k=>fresh&&r[k]?.meta?.health==='OK'&&Number.isFinite(r[k]?.meta?.ageMs)&&r[k].meta.ageMs<(k==='tofFront'||k==='presence'?1000:500);
 $('quality').textContent=fresh?'CONNECTED · '+(s.telemetryAgeMs??'—')+' ms':'UNAVAILABLE';$('transport').textContent=fresh?(s.transport||'UNKNOWN'):'NONE';
 $('battery').textContent=fresh?'Battery '+(c?.battery||'UNKNOWN'):'Battery UNKNOWN';
 if(!fresh){$('power').textContent='—';$('owner').textContent='Robot state unavailable';}
 $('heading').textContent=good('imu')&&r.imu.derived?.headingValid&&Number.isFinite(r.imu.derived.yawDeg)?r.imu.derived.yawDeg.toFixed(0)+'°':'—';
 $('range').textContent=good('tofFront')&&r.tofFront.derived?.valid&&Number.isFinite(r.tofFront.derived.nearestMm)?r.tofFront.derived.nearestMm+' mm':'—';
 $('presence').textContent=good('presence')&&r.presence.derived?.presenceValid?(r.presence.derived.present?'PRESENT':'CLEAR'):'UNKNOWN';
 const warnings=[];
 if(!fresh)warnings.push('Connection lost. Motion controls unavailable.');
 else {if(c?.batteryLockout)warnings.push('Battery lockout · motors inhibited');if(c?.battery==='WARN'||c?.battery==='CRITICAL')warnings.push('Battery '+c.battery);if(c?.benchPower)warnings.push('BENCH power');if(c?.watchdogStopped)warnings.push('Watchdog stopped motion. Arm again.');if(c?.state==='UNKNOWN')warnings.push('Robot state unavailable. S3 Interface v1 firmware required.');for(const [k,label] of [['power','Battery monitor'],['imu','Heading'],['tofFront','Range'],['presence','Presence']])if(!good(k))warnings.push(label+' unavailable');if(good('imu')&&!r.imu.derived?.headingValid)warnings.push('Heading not calibrated');}
 $('warnings').textContent=warnings.join('\n')||'No reported warnings';
 $('reportedPower').textContent='S3 power level: '+(fresh&&c?.power!=null?(c.power===255?'Overdrive':c.power+'%'):'UNKNOWN');
 $('sensorHealth').textContent=JSON.stringify({telemetryAgeMs:s?.telemetryAgeMs,health:Object.fromEntries(Object.entries(r).map(([k,v])=>[k,v.meta]))},null,2);
}
$('diagnostics').append($('dev').parentElement);$('testLeft').oninput=release;$('testRight').oninput=release;
const embedded=new URLSearchParams(location.search).has('embedded');
if(embedded){$('trackTest').hidden=false;$('dev').hidden=true;document.querySelector('h1').hidden=true;}
window.addEventListener('message',e=>{if(!embedded||e.origin!==location.origin||e.source!==parent)return;if(e.data?.type==='interface-key')$('key').value=e.data.key;if(e.data?.type==='interface-stop'){held=null;command(0);reset('Paused. Arm again.');}});
if(embedded)parent.postMessage({type:'interface-ready'},location.origin);
setInterval(()=>{if(armed&&!document.hidden)command(2);},100);refresh();
</script></html>)HTML";
