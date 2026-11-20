#pragma once
// C6 main control page (http://192.168.8.1/), desktop cockpit layout.
// The control script is the Interface v1 field logic from shared/FieldPage.h,
// unchanged in behaviour: the S3 validates every command, hold-to-run with a
// 100 ms deadman, no cached armed state, no motion replay, no automatic arm.
// Additions: layout, live gauges, held-key highlight and keyboard driving that
// follows the same hold/release path (W A S D or arrows; Space/Esc disarm).
// Presence (radar, never installed) raises no alert here; it stays in Diagnostics.
// shared/FieldPage.h stays as-is for S3 recovery /field and the /dev embed.
static const char CONTROL_PAGE[]=R"HTML(<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gladiator · Control</title>
<style>
:root{color-scheme:dark;--bg:#04080c;--panel:rgba(10,20,28,.78);--line:#173342;--line2:#0f2430;--text:#e4f2f8;--dim:#7f97a6;--faint:#4b6170;--cyan:#00e1ff;--orange:#ff7a12;--red:#ff3b4a;--amber:#ffc23a;--green:#3dff95;--accent:var(--cyan);font-family:"Segoe UI",system-ui,sans-serif}
*{box-sizing:border-box}[hidden]{display:none!important}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px ui-monospace,Consolas,monospace;color:var(--dim)}
body{margin:0;min-height:100vh;color:var(--text);background:radial-gradient(1100px 520px at 50% -12%,#0d2635 0,transparent 62%),repeating-linear-gradient(0deg,transparent 0 31px,#08151d 31px 32px),repeating-linear-gradient(90deg,transparent 0 31px,#08151d 31px 32px),var(--bg)}
body[data-mode=armed]{--accent:var(--amber)}body[data-mode=drive]{--accent:var(--orange)}body[data-mode=lost]{--accent:var(--red)}
a{color:var(--cyan)}small,p{color:var(--dim)}p{margin:.4em 0}
button,input,select{font:inherit;color:var(--text);border-radius:8px}
button{background:#132630;border:1px solid var(--line);padding:10px 12px;cursor:pointer;touch-action:none;transition:background .12s,border-color .12s,box-shadow .12s}
button:hover:not(:disabled){border-color:var(--accent);background:#173342}button:disabled{opacity:.33;cursor:not-allowed}
input,select{background:#061017;border:1px solid var(--line);padding:9px 10px;width:100%}input[type=checkbox]{width:auto;accent-color:var(--amber)}input[type=range]{padding:0;accent-color:var(--cyan)}
label{display:block;color:var(--dim);font-size:13px;margin:8px 0}output{display:block;min-height:20px;font-size:13px;color:var(--dim);margin-top:8px}
details{margin-top:10px}summary{cursor:pointer;color:var(--dim);font-size:13px;letter-spacing:.06em;text-transform:uppercase}summary:hover{color:var(--text)}
kbd{font:11px ui-monospace,Consolas,monospace;border:1px solid currentColor;border-radius:4px;padding:0 4px;opacity:.7;margin-left:6px}
/* top bar */
.top{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:18px;padding:10px 22px;background:linear-gradient(#060d13f0,#060d13d8);border-bottom:1px solid var(--line);backdrop-filter:blur(6px)}
.top::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:1px;background:linear-gradient(90deg,transparent,var(--accent),transparent);background-size:40% 100%;background-repeat:no-repeat;animation:sweep 4.5s linear infinite}
@keyframes sweep{from{background-position:-40% 0}to{background-position:140% 0}}
h1{margin:0;display:flex;align-items:center;gap:10px;font:italic 800 26px/1 "Segoe UI",system-ui,sans-serif;letter-spacing:.04em}
.stripes{display:flex;gap:4px}.stripes b{width:7px;height:20px;background:var(--accent);transform:skewX(-20deg)}.stripes b:nth-child(2){opacity:.65}.stripes b:nth-child(3){opacity:.35}
.chip{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--dim);padding:6px 12px;border:1px solid var(--line);border-radius:999px;background:#07121a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
.dot{width:9px;height:9px;border-radius:50%;background:var(--faint);flex:none}.chip[data-ok=yes] .dot{background:var(--green);box-shadow:0 0 10px var(--green)}.chip[data-ok=no] .dot{background:var(--red);box-shadow:0 0 10px var(--red);animation:blink 1s steps(2) infinite}
@keyframes blink{50%{opacity:.25}}
.batt{display:flex;align-items:center;gap:10px;margin-left:auto}.gauge{position:relative;width:54px;height:24px;border:2px solid var(--dim);border-radius:4px;padding:2px}.gauge::after{content:"";position:absolute;right:-6px;top:6px;width:4px;height:8px;background:var(--dim);border-radius:0 2px 2px 0}
.gauge i{display:block;height:100%;width:0;background:var(--faint);border-radius:2px;transition:width .4s,background .4s}
.batt b{display:block;white-space:nowrap;font:700 20px/1.1 ui-monospace,Consolas,monospace}.batt small{font-size:12px}
.keybox{margin:0;position:relative}.keybox summary{white-space:nowrap;padding:8px 12px;border:1px solid var(--line);border-radius:8px;text-transform:none;letter-spacing:0}.keybox[open]>div{position:absolute;right:0;top:44px;width:320px;padding:14px;background:#08131b;border:1px solid var(--line);border-radius:10px;box-shadow:0 12px 40px #000a}
.stop{background:linear-gradient(#d5303f,#9c1c29);border-color:#ff6a76;color:white;font-weight:800;letter-spacing:.08em;padding:12px 20px;box-shadow:0 0 0 1px #0006,0 0 22px #ff3b4a55}.stop:hover:not(:disabled){background:linear-gradient(#ef3b4b,#b0212f);border-color:white}
/* deck */
.deck{display:grid;grid-template-columns:minmax(280px,320px) minmax(0,1fr) minmax(280px,330px);gap:18px;padding:18px 22px;max-width:1700px;margin:auto}
.col{position:relative;padding:16px;background:var(--panel);border:1px solid var(--line2);border-radius:14px;min-width:0}
.col::before,.col::after{content:"";position:absolute;width:16px;height:16px;border:2px solid var(--accent);opacity:.7;pointer-events:none}.col::before{left:-1px;top:-1px;border-right:0;border-bottom:0;border-top-left-radius:14px}.col::after{right:-1px;bottom:-1px;border-left:0;border-top:0;border-bottom-right-radius:14px}
.ph{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 10px;font:700 12px/1 "Segoe UI",system-ui;letter-spacing:.18em;color:var(--dim);text-transform:uppercase}
#state{font:800 22px/1 ui-monospace,Consolas,monospace;letter-spacing:.06em;padding:6px 10px;border-radius:6px;background:#0a1922;color:var(--dim);border:1px solid var(--line)}
body[data-state=SAFE] #state{color:var(--cyan);border-color:#0a5566}body[data-state=ARMED] #state{color:#111;background:var(--amber);border-color:var(--amber);box-shadow:0 0 18px #ffc23a66}body[data-state=DRIVE] #state{color:#111;background:var(--orange);border-color:var(--orange);box-shadow:0 0 22px #ff7a1288}
.arm{width:100%;padding:14px;font-weight:800;letter-spacing:.14em;background:linear-gradient(#ffcb52,#d99a1d);color:#111;border-color:#ffd77a}.arm:hover:not(:disabled){background:linear-gradient(#ffd56c,#e6a62a);color:#111}
.speed{display:flex;align-items:center;gap:8px;margin:12px 0 4px}.speed>span{font-size:12px;color:var(--dim);letter-spacing:.1em;text-transform:uppercase}.speed select{position:absolute;width:1px;height:1px;opacity:0;pointer-events:none}
.seg{display:flex;flex:1;border:1px solid var(--line);border-radius:8px;overflow:hidden}.seg button{flex:1;border:0;border-radius:0;padding:8px 0;font:600 13px ui-monospace,Consolas,monospace;background:#0a1820}.seg button+button{border-left:1px solid var(--line)}.seg button.on{background:var(--accent);color:#111}.seg button[data-speed="255"].on{background:var(--red);color:white}
.pad{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:12px auto 0;max-width:300px}
.pad button{aspect-ratio:1.15;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;font-size:22px;font-weight:700;background:radial-gradient(circle at 50% 30%,#18303c,#0b1820);user-select:none}
.pad button small{font:11px ui-monospace,Consolas,monospace;color:var(--faint);letter-spacing:.06em}
.pad button.held,.pad button:active:not(:disabled){background:var(--accent);color:#111;border-color:white;box-shadow:0 0 24px var(--accent)}.pad button.held small{color:#111}
.hint{display:block;margin-top:8px;font-size:12px;line-height:1.5}
.alerts{margin-top:14px;padding:10px 12px;border-left:3px solid var(--amber);background:#1b150744;border-radius:0 8px 8px 0}#warnings{margin:0;color:#ffd27e;white-space:pre-line;font-size:13px}.alerts.clear{border-color:var(--green);background:#06180f44}.alerts.clear #warnings{color:#8fe6b2}
/* vision */
.feed{position:relative;aspect-ratio:4/3;max-height:calc(100vh - 290px);min-height:240px;width:100%;background:#020507;border:1px solid var(--line);border-radius:10px;overflow:hidden;display:flex;align-items:center;justify-content:center}
#cameraFeed{width:100%;height:100%;object-fit:contain;background:#000}
.standby{display:flex;flex-direction:column;align-items:center;gap:12px;color:var(--faint);font:700 13px ui-monospace,Consolas,monospace;letter-spacing:.3em}.standby svg{width:120px;opacity:.6;animation:spin 14s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}
.scan{position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,#ffffff06 0 1px,transparent 1px 3px)}
.br{position:absolute;width:26px;height:26px;border:2px solid var(--accent);opacity:.8;pointer-events:none}.br.a{left:10px;top:10px;border-right:0;border-bottom:0}.br.b{right:10px;top:10px;border-left:0;border-bottom:0}.br.c{left:10px;bottom:10px;border-right:0;border-top:0}.br.d{right:10px;bottom:10px;border-left:0;border-top:0}
.feedbar{position:absolute;left:0;right:0;bottom:0;display:flex;align-items:center;gap:10px;padding:10px 14px;background:linear-gradient(transparent,#000c)}
.feedbar .tag{font:700 12px ui-monospace,Consolas,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-right:auto}
.rec{display:none;align-items:center;gap:6px;position:absolute;left:44px;top:16px;font:700 12px ui-monospace,Consolas,monospace;letter-spacing:.2em;color:var(--red)}.rec::before{content:"";width:9px;height:9px;border-radius:50%;background:var(--red);animation:blink 1s steps(2) infinite}.live .rec{display:flex}
#cameraStatus{font-size:13px;margin:10px 0 2px}#videoStatus{font-size:12px;margin:0}
.tele{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:12px}
.tile{padding:10px 12px;border:1px solid var(--line2);border-radius:10px;background:#07121a;display:flex;align-items:center;gap:10px;min-width:0}.tile>div{min-width:0}.tile small{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase}
.tile strong{display:block;font:700 19px/1.25 ui-monospace,Consolas,monospace;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.compass{width:44px;height:44px;flex:none}.compass circle{fill:none;stroke:var(--line)}.compass #needle{transition:transform .3s;transform-origin:22px 22px}
.meter{flex:1;height:6px;border-radius:3px;background:#0d1d26;overflow:hidden;margin-top:6px}.meter i{display:block;height:100%;width:0;background:var(--cyan);transition:width .3s,background .3s}
.face{display:flex;align-items:end;gap:8px;margin-top:12px}.face label{flex:1;margin:0}.face button{white-space:nowrap}
.twocol{display:grid;grid-template-columns:1fr 1fr;gap:0 12px}
/* aim */
#mastStatus{font:12px ui-monospace,Consolas,monospace;color:var(--dim);margin:0 0 8px;line-height:1.5}
.confirm{display:flex;gap:8px;align-items:flex-start;padding:8px 10px;border:1px dashed #6b5517;border-radius:8px;color:#e8c46b}
#mastEnable{width:100%;margin-top:8px;font-weight:700}
.aimpad button{aspect-ratio:1.3;font-size:18px}
.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.row>*{flex:1}
.mastoff{background:#3a1218;border-color:#8a2a35}
#lightBox{margin-top:14px;padding-top:12px;border-top:1px solid var(--line2)}
fieldset{border:1px solid var(--line);border-radius:8px;margin:8px 0}
/* footer */
.foot{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px;padding:0 22px 26px;max-width:1700px;margin:auto}
.foot>details{margin:0;padding:12px 16px;background:var(--panel);border:1px solid var(--line2);border-radius:12px}
@media (max-width:1380px){#link,#link+span{display:none}}
@media (max-width:1180px){.deck{grid-template-columns:minmax(260px,300px) minmax(0,1fr)}.deck>.aim{grid-column:1/-1}}
@media (max-width:760px){.top{flex-wrap:wrap;padding:10px 12px}.deck,.foot{grid-template-columns:minmax(0,1fr);padding:12px}.tele{grid-template-columns:repeat(2,minmax(0,1fr))}.feed{max-height:none}.keybox[open]>div{width:min(320px,90vw)}}
</style>
<header class="top"><h1><span>GLADIATOR</span><span class="stripes"><b></b><b></b><b></b></span></h1>
<div class="chip" id="linkChip"><span class="dot"></span><span id="link">Connecting…</span><span>·</span><span id="quality">UNKNOWN</span><span>·</span><strong id="transport">NONE</strong></div>
<div class="batt" title="Bar spans S3 lockout 13.2 V to a full 4S pack 16.8 V"><div class="gauge"><i id="battFill"></i></div><div><b id="power">—</b><small id="battery">Battery UNKNOWN</small></div></div>
<details id="keyBox" class="keybox"><summary>Access key</summary><div><p>Use the C6 maintenance key from USB provisioning. It stays in this page's memory.</p><input id="key" type="password" maxlength="32" autocomplete="off" aria-label="Field access key"></div></details>
<button id="stop" class="stop">DISARM<kbd>Space</kbd></button></header>
<main class="deck">
<section class="col drive"><div class="ph"><span>Drive</span><span id="state">UNKNOWN</span></div>
<p id="owner">S3 controls motors and safety.</p>
<button id="arm" class="arm" disabled>ARM</button>
<div class="speed"><span>Power</span><select id="speed" aria-label="Drive power"><option value="25">25%</option><option value="50">50%</option><option value="75">75%</option><option value="100">100%</option><option value="255">Overdrive</option></select><div class="seg" id="speedSeg"><button data-speed="25" title="Key 1">25</button><button data-speed="50" title="Key 2">50</button><button data-speed="75" title="Key 3">75</button><button data-speed="100" title="Key 4">100</button><button data-speed="255" title="Overdrive: full battery voltage">OD</button></div></div>
<div class="pad"><span></span><button data-drive="f" disabled>▲<small>W</small></button><span></span><button data-drive="l" disabled>◀<small>A</small></button><button data-drive="s" disabled>■<small>COAST</small></button><button data-drive="r" disabled>▶<small>D</small></button><span></span><button data-drive="b" disabled>▼<small>S</small></button></div>
<output id="reply" aria-live="polite"></output>
<small class="hint">Hold a direction with the mouse, W A S D or the arrow keys. Release to coast. <b>Space</b> or <b>Esc</b> disarms. After any timeout or reconnect, arm again.</small>
<div class="alerts" id="alertBox"><div class="ph" style="margin-bottom:6px"><span>Alerts</span></div><p id="warnings" role="status">Waiting for robot state.</p></div>
</section>
<section class="col vision"><div class="ph"><span>Vision</span><span id="visualMode">Connecting</span></div>
<div class="feed" id="feedBox"><img id="cameraFeed" hidden alt="Live Gladiator camera"><div class="standby" id="standby"><svg viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="2"><circle cx="50" cy="50" r="38"/><circle cx="50" cy="50" r="22" stroke-dasharray="4 6"/><path d="M50 4v20M50 76v20M4 50h20M76 50h20"/></svg>CAMERA STANDBY</div><div class="scan"></div><span class="br a"></span><span class="br b"></span><span class="br c"></span><span class="br d"></span><span class="rec">LIVE</span>
<div class="feedbar"><span class="tag" id="feedTag">Masthead camera</span><button id="videoToggle" disabled>Start video</button></div></div>
<p id="videoStatus">Set the camera address to enable video.</p>
<div class="tele">
<div class="tile"><svg class="compass" viewBox="0 0 44 44"><circle cx="22" cy="22" r="20"/><text x="22" y="9" fill="#4b6170" font-size="7" text-anchor="middle">N</text><g id="needle"><path d="M22 6 L26 22 L22 20 L18 22 Z" fill="#00e1ff"/><path d="M22 38 L26 22 L22 24 L18 22 Z" fill="#2a4351"/></g></svg><div><small>Heading</small><strong id="heading">—</strong></div></div>
<div class="tile"><div style="flex:1"><small>Front range</small><strong id="range">—</strong><div class="meter"><i id="rangeFill"></i></div></div></div>
<div class="tile"><div><small>Drive output</small><strong id="driveOut">—</strong></div><span id="presence" hidden>UNKNOWN</span></div>
<div class="tile"><div><small>Telemetry</small><strong id="ageText">—</strong></div></div>
</div>
<div id="visualPanel" hidden>
<div class="face"><label>Screen face<select id="expression" aria-label="Display expression"><option value="auto">Automatic</option><option value="ready">Ready</option><option value="scanning">Scanning</option><option value="active">Active</option><option value="greeting">Greeting</option><option value="alert">Alert</option></select></label><button id="setExpression">Show for 30 s</button></div>
<output id="visualReply" aria-live="polite"></output>
<details><summary>Camera image settings</summary><div class="twocol"><label>Resolution<select id="camResolution"><option>QQVGA</option><option selected>QVGA</option><option>VGA</option><option>SVGA</option></select></label><label>Brightness<select id="camBrightness"><option>-2</option><option>-1</option><option selected>0</option><option>1</option><option>2</option></select></label><label>Manual exposure (0–1200)<input id="camExposure" type="number" min="0" max="1200" value="300"></label><div><label><input id="camAuto" type="checkbox" checked> Automatic exposure</label><label><input id="camFlip" type="checkbox"> Flip vertically</label><label><input id="camMirror" type="checkbox"> Mirror horizontally</label></div></div><div class="row"><button id="readCamera">Read current settings</button><button id="applyCamera">Apply image settings</button></div><output id="cameraReply"></output></details>
<details><summary>Camera network setup (maintenance key)</summary><p>Camera IPv4 address on the C6 network. Reserve this address in DHCP.</p><div class="row"><input id="cameraIp" maxlength="15" placeholder="192.168.8.2" aria-label="Camera IPv4 address"><button id="saveCamera" style="flex:none">Save camera address</button></div></details>
</div>
</section>
<section class="col aim" id="mastPanel" hidden><div class="ph"><span>Aim</span><span>Mast &amp; light</span></div>
<p id="mastStatus">Uncommissioned · outputs off</p>
<label class="confirm"><input id="enableConfirm" type="checkbox"> Area clear; deliberately move to saved neutral</label><button id="mastEnable" disabled>Enable at neutral</button>
<div class="pad aimpad"><span></span><button data-aim="up" disabled>▲</button><span></span><button data-aim="left" disabled>◀</button><button id="mastCenter" disabled>◎</button><button data-aim="right" disabled>▶</button><span></span><button data-aim="down" disabled>▼</button></div><p style="font-size:12px">Hold an arrow to aim; release to hold. Angles are head degrees. Pan gearing: 60T / 40T = 1.5.</p>
<label>Movement speed (°/s)<input id="mastSpeed" type="range" min="1" max="30" step="1" value="5"></label><output id="mastSpeedLabel">5°/s</output>
<div class="row"><button id="mastScan" disabled>Scan within limits</button><button id="mastHold" disabled>Hold / stop scan</button></div><div class="row" style="margin-top:8px"><button id="mastStop" class="mastoff">Mast OFF</button></div>
<div id="lightBox"><div class="ph" style="margin-bottom:4px"><span>Spotlight</span><span id="lightStatus">Off</span></div><label>Brightness <output id="lightLabel" style="display:inline;margin:0">0%</output><input id="lightLevel" type="range" min="0" max="100" step="10" value="0" aria-label="Spotlight brightness"></label><div class="row"><button id="lightFull">Full</button><button id="lightOff">Light off</button></div><small>Camera flash LED; it points where the camera points and does not need the mast enabled. It turns off when this page is hidden, and the camera turns it off 2 minutes after the last page update.</small></div>
<details><summary>Move to angle</summary><div class="row"><label>Pan °<input id="mastPan" type="number" value="0" step="0.1"></label><label>Tilt °<input id="mastTilt" type="number" value="0" step="0.1"></label></div><button id="mastMove" disabled>Move smoothly</button></details><output id="mastReply" aria-live="polite"></output>
<details id="commission" hidden><summary>Installed servo testing &amp; saved calibration</summary><p>Disarm drive before commissioning. Outputs stay off until you start a test. SG90 has no position feedback: the first pulse can move an unknown position. Watch the installed mechanism and cables. Test one output at a time in a small pulse window; stop before changing outputs.</p><div class="row"><label>Test GPIO<select id="testPin"><option>10</option><option>13</option></select></label><label>Frequency Hz<input id="testHz" type="number" value="50" min="50" max="100"></label></div><label>First pulse µs<input id="testFirst" type="number" placeholder="Choose deliberately" min="500" max="2575"></label><div class="row"><label>Window low µs<input id="testMin" type="number" min="500" max="2575"></label><label>Window high µs<input id="testMax" type="number" min="500" max="2575"></label></div><button id="startTest">Start single output test</button><label>Target pulse µs<input id="testTarget" type="number" min="500" max="2575"></label><button id="jogTest">Move to test pulse</button><button id="stopTest" class="stop">Outputs OFF</button><p>Test expires after 10 seconds without a target command. Later changes slew at 100 µs/s. Record which GPIO controls each axis, neutral, measured shaft angles and cable-safe HEAD limits. Pulse endpoints are measured servo points, not assumed SG90 specifications. Pan head angle = shaft angle × 1.5.</p><div id="calAxes"></div><label><input id="calVerified" type="checkbox"> Positional SG90s, pulse map, direction and installed clearance checked</label><button id="saveMast">Save calibration (outputs off)</button><button id="loadMast">Load saved values into form</button></details>
</section>
</main>
<footer class="foot">
<details id="diagnostics"><summary>Diagnostics &amp; tools</summary><p id="reportedPower"></p><pre id="sensorHealth"></pre><details id="trackTest" hidden><summary>Independent track test</summary><p>Values are signed percent. Hold Test tracks to run; release to coast. S3 validates every request.</p><label>Left<input id="testLeft" type="number" min="-100" max="100" value="0"></label><label>Right<input id="testRight" type="number" min="-100" max="100" value="0"></label><button data-drive="test" disabled>Test tracks</button></details></details>
<details><summary>Keyboard</summary><p><b>W A S D</b> / arrows: hold to drive (only while armed) · <b>1–4</b>: power 25–100% · <b>Space</b> / <b>Esc</b>: disarm drive and mast. Keys are ignored while typing in a field. Leaving or hiding the page disarms.</p></details>
</footer>
<p><a href="/help"><strong>Troubleshoot</strong></a> · <a href="/booth/">Booth routines</a> · <a href="/hardware-test">Hardware setup & servo tests</a> · <a id="dev" href="/dev">Development & diagnostics</a></p>
<script>
const $=id=>document.getElementById(id);let snapshot=null,held=null,armed=false,arming=false,busy=false,stopPending=false,seq=0,epoch=0,updated=0,lastRejected=0;
const random=new Uint32Array(1);crypto.getRandomValues(random);const client=random[0]||1;
function reset(message){held=null;armed=false;arming=false;$('speed').value='25';render();if(message)$('reply').textContent=message;}
function render(){document.querySelectorAll('[data-drive]').forEach(b=>b.disabled=!armed);$('speed').disabled=false;$('arm').disabled=armed||arming||snapshot?.controller?.armed||!snapshot?.connected||!['SAFE','ARMED','DRIVE'].includes(snapshot?.controller?.state)||snapshot?.controller?.batteryLockout;}
async function command(operation){
  if(busy){if(operation===0){stopPending=true;reset('DISARM queued after current request.');}return;}
  if(!snapshot?.controller||performance.now()-updated>250){reset('State is stale. Reconnect and arm again.');return;}
  busy=true;let l=0,r=0,p=Number($('speed').value);if(held==='f')l=r=p;if(held==='b')l=r=-p;if(held==='l'){l=-p;r=p;}if(held==='r'){l=p;r=-p;}if(held==='test'){l=Number($('testLeft').value);r=Number($('testRight').value);}const overdrive=p===255?1:0;if(overdrive){p=100;l=Math.max(-100,Math.min(100,l));r=Math.max(-100,Math.min(100,r));}
  const body={epoch,client,sequence:++seq,observedMs:snapshot.controller.s3Ms,operation,deadman:operation===2&&held!==null?1:0,overdrive,power:p,left:operation===2?l:0,right:operation===2?r:0};
  try{const response=await fetch('/api/control',{method:'POST',headers:{'Content-Type':'application/json','X-Gladiator-Key':$('key').value.trim()},body:JSON.stringify(body),signal:AbortSignal.timeout(250)});const text=await response.text();if(!response.ok)throw Error('HTTP '+response.status+': '+text.slice(0,160));const result=JSON.parse(text);if(result.result&&result.result!==0)throw Error('S3 rejected command');}
  catch(e){reset('Control interrupted: '+e.message+'. Release, then arm again.');}finally{busy=false;if(stopPending){stopPending=false;command(0);}}
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
   const recovery=s.interface==='s3-recovery';$('keyBox').hidden=!s.requiresKey;$('commission').hidden=!recovery;$('dev').href=recovery?'/service':'/dev';$('dev').textContent=recovery?'Open recovery service':'Open development interface';$('link').textContent=recovery?'Recovery field connection':'Field connection · mast is front';drawField(s);hud(s);render();
 }catch(e){snapshot=null;reset('Connection lost. Arm again after recovery.');$('state').textContent='UNKNOWN';drawField(null);hud(null);}setTimeout(refresh,100);
}
$('arm').onclick=()=>{if(!snapshot?.connected)return;held=null;epoch=snapshot.controller.epoch;arming=true;render();command(1);setTimeout(()=>{if(arming)reset('No arm confirmation. Try again.');},600);};
$('stop').onclick=()=>{held=null;command(0);mastOff();reset('DISARM requested. Waiting for S3 state.');};
function release(){held=null;if(armed)command(2);}
document.querySelectorAll('[data-drive]').forEach(b=>{b.onpointerdown=e=>{e.preventDefault();if(!armed)return;b.setPointerCapture(e.pointerId);held=b.dataset.drive;command(2);};b.onpointerup=release;b.onpointercancel=release;b.onlostpointercapture=release;});
$('speed').onchange=()=>{if(armed)command(2);};window.onblur=()=>{held=null;command(0);reset('Paused. Arm again.');};document.onvisibilitychange=()=>{if(document.hidden)window.onblur();};
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
 else {if(c?.batteryLockout)warnings.push('Battery lockout · motors inhibited');if(c?.battery==='WARN'||c?.battery==='CRITICAL')warnings.push('Battery '+c.battery);if(c?.benchPower)warnings.push('BENCH power');if(c?.watchdogStopped)warnings.push('Watchdog stopped motion. Arm again.');if(c?.state==='UNKNOWN')warnings.push('Robot state unavailable. S3 Interface v1 firmware required.');for(const [k,label] of [['power','Battery monitor'],['imu','Heading'],['tofFront','Range']])if(!good(k))warnings.push(label+' unavailable');if(good('imu')&&!r.imu.derived?.headingValid)warnings.push('Heading not calibrated');}
 $('warnings').textContent=warnings.join('\n')||'No reported warnings';
 $('reportedPower').textContent='S3 power level: '+(fresh&&c?.power!=null?(c.power===255?'Overdrive':c.power+'%'):'UNKNOWN');
 $('sensorHealth').textContent=JSON.stringify({telemetryAgeMs:s?.telemetryAgeMs,health:Object.fromEntries(Object.entries(r).map(([k,v])=>[k,v.meta]))},null,2);
}
$('diagnostics').append($('dev').parentElement);$('testLeft').oninput=release;$('testRight').oninput=release;
const embedded=new URLSearchParams(location.search).has('embedded');
if(embedded){$('trackTest').hidden=false;$('dev').hidden=true;document.querySelector('h1').hidden=true;}
window.addEventListener('message',e=>{if(!embedded||e.origin!==location.origin||e.source!==parent)return;if(e.data?.type==='interface-key')$('key').value=e.data.key;if(e.data?.type==='interface-stop'){held=null;command(0);reset('Paused. Arm again.');}});
if(embedded)parent.postMessage({type:'interface-ready'},location.origin);
// Display and video controls never enter the robot's motion command path.
let streamUrl='',videoOn=false,cameraAddress='',cameraStatusAt=0,cameraPollAt=0,cameraStatusBusy=false;
const cameraStatusRow=document.createElement('p');cameraStatusRow.id='cameraStatus';cameraStatusRow.setAttribute('role','status');cameraStatusRow.setAttribute('aria-live','polite');$('videoStatus').before(cameraStatusRow);
function cameraStatus(text,health='unknown'){cameraStatusRow.textContent='● Camera: '+text;cameraStatusRow.dataset.health=health;cameraStatusRow.style.color={ok:'#8cdbac',warn:'#ffce7b',bad:'#ff949b',unknown:'#a6b8c4'}[health];}
cameraStatus('Checking…');
async function refreshCameraStatus(){
 if(document.hidden||cameraStatusBusy||lightBusy||cameraSettingsBusy||!cameraAddress)return;
 const now=performance.now();if(cameraStatusAt&&now-cameraStatusAt>12000)cameraStatus('Status stale · '+cameraAddress,'warn');
 if(cameraPollAt&&now-cameraPollAt<5000)return;cameraPollAt=now;cameraStatusBusy=true;const address=cameraAddress;
 try{const r=await fetch('/api/camera/status',{cache:'no-store',signal:AbortSignal.timeout(1800)});if(address!==cameraAddress)return;
  if(r.status===503){if(!cameraStatusAt)cameraStatus('Checking · camera request busy','warn');return;}
  if(!r.ok)throw Error();const c=await r.json();if(address!==cameraAddress)return;if(typeof c.cameraReady!=='boolean'||typeof c.streaming!=='boolean')throw Error();cameraStatusAt=performance.now();
  cameraStatus((c.otaUpdating?'Updating firmware':c.cameraReady?'Ready · '+(c.streaming?'streaming':'idle'):c.cameraError?'Camera not detected':'Not ready')+' · '+address+(Number.isFinite(c.rssi)?' · Wi-Fi '+c.rssi+' dBm':''),c.otaUpdating?'warn':c.cameraReady?'ok':'bad');
 }catch(e){if(address===cameraAddress){cameraStatusAt=0;cameraStatus('Not reachable · '+address+' · check power, Wi-Fi and saved address','bad');}}
 finally{cameraStatusBusy=false;}
}
function stopVideo(){videoOn=false;$('cameraFeed').removeAttribute('src');$('cameraFeed').hidden=true;$('videoToggle').textContent='Start video';}
$('videoToggle').onclick=()=>{if(videoOn){stopVideo();return;}if(!streamUrl)return;videoOn=true;$('cameraFeed').hidden=false;$('cameraFeed').src=streamUrl;$('videoToggle').textContent='Stop video';};
$('cameraFeed').onerror=()=>{stopVideo();$('videoStatus').textContent='Camera unavailable. Check power and Wi-Fi, then start again.';};
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopVideo();});
async function visualPost(path,body){try{const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Gladiator-Key':$('key').value.trim()},body:JSON.stringify(body),signal:AbortSignal.timeout(1000)});if(!r.ok)throw Error(await r.text());$('visualReply').textContent='Saved. Display changes require fresh S3 state.';}catch(e){$('visualReply').textContent=e.message;}}
$('setExpression').onclick=()=>visualPost('/api/visual',{mode:$('expression').value,leaseMs:30000});
$('saveCamera').onclick=()=>visualPost('/api/visual/config',{cameraIp:$('cameraIp').value.trim()});
async function refreshVisual(){try{const r=await fetch('/api/visual',{cache:'no-store',signal:AbortSignal.timeout(600)});if(r.status===404)return;if(!r.ok)throw Error();const v=await r.json();if(v.schema!==1)throw Error();$('visualPanel').hidden=false;$('visualMode').textContent=v.mode+(v.override?' · temporary':'');const next=v.streamUrl||'';if(next!==streamUrl){stopVideo();streamUrl=next;}$('videoToggle').disabled=!streamUrl;if(document.activeElement!==$('cameraIp'))$('cameraIp').value=v.cameraIp||'';const address=v.cameraIp||'';if(address!==cameraAddress){cameraAddress=address;cameraStatusAt=cameraPollAt=0;cameraStatus(address?'Checking… · '+address:'Not configured · set the camera address');}if(address)refreshCameraStatus();$('videoStatus').textContent=streamUrl?'One video viewer at a time.':'Set the camera address to enable video.';}catch(e){$('visualMode').textContent='Gateway unavailable';cameraAddress='';cameraStatusAt=cameraPollAt=0;cameraStatus('Unknown · gateway unavailable','warn');}setTimeout(refreshVisual,1000);}
// Only this page's deliberately enabled session may renew mast motion.
let mastState=null,mastSeq=0,mastToken=0,mastBusy=false,mastActive=false,mastPending=null,mastEnabling=false,mastArmTimer=0;
const aimControls=['mastMove','mastScan','mastHold','mastCenter','mastSpeed'];
function mastPositions(){return mastState?.controlMode==='saved-positions';}
function mastRate(){return Math.round(number('mastSpeed')*(mastPositions()?1:10));}
function mastRender(){const own=!!(mastActive&&mastState?.fresh&&mastState.enabled&&mastState.owner===client&&mastState.safe);for(const id of aimControls)$(id).disabled=!own;document.querySelectorAll('[data-aim]').forEach(b=>b.disabled=!own);$('mastScan').disabled=!own||mastPositions();$('mastEnable').disabled=mastEnabling||!mastState?.fresh||!(mastState.calibrated||mastState.positionsReady)||mastState.enabled||mastState.testActive||!mastState.safe||!$('enableConfirm').checked;
 $('mastEnable').textContent=mastEnabling?'Arming…':'Arm mast at saved neutral';$('mastStop').textContent='Disarm mast';
 const positions=mastPositions();$('mastMove').closest('details').hidden=positions;$('mastSpeed').closest('label').firstChild.textContent=positions?'Movement speed (% of saved span/s)':'Movement speed (°/s)';$('mastSpeedLabel').textContent=$('mastSpeed').value+(positions?'% of saved span/s':'°/s');
 const usage=$('mastPanel').querySelector('.pad').nextElementSibling;usage.textContent=positions?'Hold an arrow to aim within your saved limits; release to hold. Center returns to recorded neutral. Pulse commands are shown above; actual mast angle is not measured. Scan and angle targets require a separate measured angle profile.':'Hold an arrow to aim; release to hold. Angles are head degrees. Pan gearing: 60T / 40T = 1.5.';
}
function mastPause(message){clearTimeout(mastArmTimer);mastActive=false;mastEnabling=false;$('enableConfirm').checked=false;mastRender();if(message)$('mastReply').textContent=message;}
async function mastPost(operation,pan=0,tilt=0){
 if(mastBusy){if(operation===0||(operation!==4&&mastPending?.operation!==0))mastPending={operation,pan,tilt};return;}
 if(operation!==0&&operation!==7&&operation!==8&&!mastActive)return;
 if(operation!==0&&(!mastState?.fresh||!mastState.safe))return;
 if(!Number.isFinite(pan)||!Number.isFinite(tilt))return;
 mastBusy=true;const token=operation===7||operation===8?client:(mastToken||client);
 try{const r=await fetch('/api/mast',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session:token,sequence:++mastSeq,operation,pan,tilt}),signal:AbortSignal.timeout(350)});if(!r.ok)throw Error(await r.text());if(operation!==4)$('mastReply').textContent='Queued; S3 status confirms the result.';}
 catch(e){mastPending={operation:0,pan:0,tilt:0};mastPause('Mast interrupted: '+e.message+' · outputs will expire.');}
 finally{mastBusy=false;if(mastPending){const next=mastPending;mastPending=null;if(operation!==0)mastPost(next.operation,next.pan,next.tilt);}}
}
$('enableConfirm').onchange=mastRender;
$('mastEnable').onclick=async()=>{if($('mastEnable').disabled)return;mastEnabling=true;mastRender();try{
 if(mastPositions()){
  const r=await fetch('/api/mast/setup',{cache:'no-store',signal:AbortSignal.timeout(800)});if(!r.ok)throw Error('Cannot verify saved positions');const setup=await r.json();
  if(setup.revision!==mastState.positionProfile?.setupRevision)throw Error('Saved positions changed. Load the updated positions before arming.');
 }
 if(!mastEnabling||!$('enableConfirm').checked||document.hidden)return;
 mastPost(mastPositions()?8:7);mastArmTimer=setTimeout(()=>{if(mastEnabling)mastPause('No arm confirmation; check S3 status.');},900);
 }catch(e){mastPause(e.message);}};
$('mastMove').onclick=()=>mastPost(2,Math.round(Number($('mastPan').value)*10),Math.round(Number($('mastTilt').value)*10));
$('mastCenter').onclick=()=>mastPost(2,0,0);$('mastScan').onclick=()=>mastPost(3);$('mastHold').onclick=()=>mastPost(1);
function mastOff(){mastPost(0);mastPause('Outputs OFF requested.');}
$('mastStop').onclick=mastOff;
document.querySelectorAll('[data-aim]').forEach(b=>{b.onpointerdown=e=>{e.preventDefault();if(b.disabled)return;b.setPointerCapture(e.pointerId);const v={left:[-1,0],right:[1,0],up:[0,1],down:[0,-1]}[b.dataset.aim];mastPost(6,...v);};const hold=()=>mastPost(1);b.onpointerup=hold;b.onpointercancel=hold;b.onlostpointercapture=hold;});
$('mastSpeed').oninput=()=>{$('mastSpeedLabel').textContent=$('mastSpeed').value+(mastPositions()?'% of saved span/s':'°/s');};$('mastSpeed').onchange=()=>mastPost(5,mastRate(),0);
window.addEventListener('blur',mastOff);document.addEventListener('visibilitychange',()=>{if(document.hidden)mastOff();});
window.addEventListener('message',e=>{if(e.origin===location.origin&&e.source===parent&&e.data?.type==='interface-stop')mastOff();});
async function mastConfig(body){try{const r=await fetch('/api/mast/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(800)});if(!r.ok)throw Error(await r.text());$('mastReply').textContent='Commissioning request queued; check S3 action below.';}catch(e){$('mastReply').textContent=e.message;}}
const number=id=>Number($(id).value);
$('startTest').onclick=()=>{if(['testFirst','testMin','testMax'].some(id=>!$(id).value.trim())){$('mastReply').textContent='Choose first pulse and both window limits.';return;}mastConfig({action:'test',pin:number('testPin'),firstUs:number('testFirst'),minUs:number('testMin'),maxUs:number('testMax'),frequencyHz:number('testHz')});};
$('jogTest').onclick=()=>{if($('testTarget').value.trim())mastConfig({action:'jog-test',pin:number('testPin'),pulseUs:number('testTarget')});};$('stopTest').onclick=()=>{mastOff();mastConfig({action:'stop'});};
for(const axis of ['pan','tilt']){const box=document.createElement('fieldset');box.innerHTML='<legend>'+axis+' measured calibration</legend><label>GPIO<select id="'+axis+'Pin"><option>10</option><option '+(axis==='tilt'?'selected':'')+'>13</option></select></label>'+[['Low','low pulse µs'],['Neutral','neutral pulse µs'],['High','high pulse µs'],['ShaftMin','negative shaft angle °'],['ShaftMax','positive shaft angle °'],['Min','minimum head angle °'],['Max','maximum head angle °']].map(([key,label])=>'<label>'+label+'<input id="'+axis+key+'" type="number" step="0.1"></label>').join('')+'<label><input id="'+axis+'Reverse" type="checkbox" style="width:auto"> Increasing pulse moves negative head direction</label>';$('calAxes').append(box);}
function axisProfile(axis){for(const key of ['Low','Neutral','High','ShaftMin','ShaftMax','Min','Max'])if(!$(axis+key).value.trim())throw Error('Fill every measured '+axis+' value.');return {pin:number(axis+'Pin'),lowUs:number(axis+'Low'),neutralUs:number(axis+'Neutral'),highUs:number(axis+'High'),shaftMinDeciDeg:Math.round(number(axis+'ShaftMin')*10),shaftMaxDeciDeg:Math.round(number(axis+'ShaftMax')*10),minDeciDeg:Math.round(number(axis+'Min')*10),maxDeciDeg:Math.round(number(axis+'Max')*10),reversed:$(axis+'Reverse').checked};}
$('saveMast').onclick=()=>{try{if(!$('calVerified').checked)throw Error('Verify the installed servos and clearance first.');mastConfig({action:'calibrate',panModel:'SG90',tiltModel:'SG90',positionalVerified:true,clearanceVerified:true,frequencyHz:number('testHz'),speedDeciDegPerSec:Math.round(number('mastSpeed')*10),pan:axisProfile('pan'),tilt:axisProfile('tilt')});}catch(e){$('mastReply').textContent=e.message;}};
$('loadMast').onclick=()=>{const p=mastState?.profile;if(!p){$('mastReply').textContent='No saved calibration.';return;}for(const axis of ['pan','tilt']){const a=p[axis];for(const [key,value] of Object.entries({Pin:a.pin,Low:a.lowUs,Neutral:a.neutralUs,High:a.highUs,ShaftMin:a.shaftMinDeciDeg/10,ShaftMax:a.shaftMaxDeciDeg/10,Min:a.minDeciDeg/10,Max:a.maxDeciDeg/10}))$(axis+key).value=value;$(axis+'Reverse').checked=a.reversed;}$('testHz').value=p.frequencyHz;$('mastSpeed').value=p.speedDeciDegPerSec/10;$('mastSpeed').oninput();};
async function refreshMast(){
 try{const r=await fetch('/api/mast',{cache:'no-store',signal:AbortSignal.timeout(350)});if(r.status===404)return;if(!r.ok)throw Error();const m=await r.json();let justEnabled=false;$('mastPanel').hidden=false;
 if(mastEnabling&&m.fresh&&m.enabled&&m.owner===client){clearTimeout(mastArmTimer);mastActive=true;mastEnabling=false;mastToken=m.session;mastSeq=m.sequence||0;justEnabled=true;}
 if(mastActive&&(!m.fresh||!m.enabled||m.session!==mastToken||m.owner!==client))mastPause('Session ended. Enable deliberately to resume.');
 mastState=m;if(mastActive)mastSeq=Math.max(mastSeq,m.sequence||0);
 $('mastStatus').textContent=(m.fresh?(m.testActive?'TEST GPIO '+m.testPin+' · '+Number(m.testPulseUs).toFixed(0)+' µs':m.enabled?(m.scanning?'Scanning':'ARMED'):'DISARMED'):'UNAVAILABLE')+' · '+(m.controlMode==='saved-positions'?'commanded pan '+(m.commandedPanUs??'?')+' µs / tilt '+(m.commandedTiltUs??'?')+' µs · saved positions r'+(m.positionProfile?.setupRevision??'?'):'commanded '+(m.commandedPanDeg??'?')+'° / '+(m.commandedTiltDeg??'?')+'°')+' · '+(m.action||m.reason||'');
 for(const [id,min,max] of [['mastPan',m.panMinDeg,m.panMaxDeg],['mastTilt',m.tiltMinDeg,m.tiltMaxDeg]]){$(id).min=min;$(id).max=max;}
 mastRender();if(mastActive&&m.fresh&&m.enabled&&m.safe&&!document.hidden)mastPost(justEnabled?5:4,justEnabled?mastRate():0,0);
 }catch(e){mastState=null;mastToken=0;mastPause('Mast connection lost.');}setTimeout(refreshMast,100);
}
// Spotlight: the CAM flash LED. While on, this page renews it; the CAM turns it off if renewals stop.
let lightWant=0,lightBusy=false,lightQueued=false;
function lightShow(level,text){$('lightLevel').value=level;$('lightLabel').textContent=level+'%';$('lightStatus').textContent=text??(level?'On · '+level+'%':'Off');}
async function lightSend(read){if(lightBusy){lightQueued=true;return;}lightBusy=true;lightQueued=false;const level=lightWant;
 try{let r;for(let i=0;i<3;i++){r=await fetch('/api/camera/light',read?{cache:'no-store',signal:AbortSignal.timeout(1800)}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({level}),signal:AbortSignal.timeout(1800)});if(r.status!==503)break;await new Promise(f=>setTimeout(f,350));}
  if(!r.ok)throw Error(r.status===404?'not on this connection':(await r.text()).slice(0,80));const l=await r.json();if(read)lightWant=l.level;if(!lightQueued)lightShow(l.level);}
 catch(e){lightShow(lightWant,'Unavailable: '+(e.name==='TimeoutError'?'camera did not reply':e.message));}
 finally{lightBusy=false;if(lightQueued)lightSend();}}
function lightSet(level){lightWant=level;lightShow(level,'Sending…');lightSend();}
$('lightLevel').oninput=()=>{$('lightLabel').textContent=$('lightLevel').value+'%';};$('lightLevel').onchange=()=>lightSet(number('lightLevel'));
$('lightFull').onclick=()=>lightSet(100);$('lightOff').onclick=()=>lightSet(0);
setInterval(()=>{if(lightWant&&!document.hidden)lightSend();},45000);
document.addEventListener('visibilitychange',()=>{if(document.hidden&&lightWant)lightSet(0);});
let cameraSettingsBusy=false;
async function cameraSettings(body){if(cameraSettingsBusy)return;cameraSettingsBusy=true;try{const r=await fetch('/api/camera',{method:body?'POST':'GET',headers:{'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{}),signal:AbortSignal.timeout(1800)});if(!r.ok)throw Error(await r.text());const c=await r.json();$('camResolution').value=c.resolution;$('camBrightness').value=c.brightness;$('camAuto').checked=!!c.aec;$('camExposure').value=c.aecValue;$('camFlip').checked=!!c.vflip;$('camMirror').checked=!!c.hmirror;$('cameraReply').textContent='Camera settings read back. Settings reset to firmware defaults on camera reboot.';}catch(e){$('cameraReply').textContent=e.message;}finally{cameraSettingsBusy=false;}}
$('readCamera').onclick=()=>cameraSettings();$('applyCamera').onclick=()=>cameraSettings({resolution:$('camResolution').value,brightness:number('camBrightness'),aec:$('camAuto').checked?1:0,aecValue:number('camExposure'),vflip:$('camFlip').checked?1:0,hmirror:$('camMirror').checked?1:0});
// ---- Cockpit presentation (reads state only; sends nothing) ----
function hud(s){
 const c=s?.controller,fresh=!!s?.connected&&!!c,r=s?.sensors||{};
 $('linkChip').dataset.ok=fresh?'yes':'no';
 document.body.dataset.state=fresh?(c.state||'UNKNOWN'):'UNKNOWN';
 const ours=fresh&&c.armed&&c.client===client;document.body.dataset.mode=!fresh?'lost':c.state==='DRIVE'?'drive':ours||c.armed?'armed':'';
 const volts=fresh&&s.powerValid&&Number.isFinite(s.volts)?Number(s.volts):NaN,pct=Number.isFinite(volts)?Math.max(0,Math.min(1,(volts-13.2)/3.6)):0;
 const bc={OK:'var(--green)',WARN:'var(--amber)',LOCKOUT:'var(--red)',CRITICAL:'var(--red)'}[c?.battery]||'var(--faint)';
 $('battFill').style.width=(pct*100).toFixed(0)+'%';$('battFill').style.background=bc;
 const yaw=fresh&&r.imu?.derived?.headingValid?Number(r.imu.derived.yawDeg):NaN;
 $('needle').style.transform='rotate('+(Number.isFinite(yaw)?yaw:0)+'deg)';$('needle').style.opacity=Number.isFinite(yaw)?1:.25;
 const mm=$('range').textContent==='—'?NaN:parseInt($('range').textContent,10);
 $('rangeFill').style.width=Number.isFinite(mm)?(Math.max(0,Math.min(1,(2000-mm)/1800))*100).toFixed(0)+'%':'0%';
 $('rangeFill').style.background=!Number.isFinite(mm)?'var(--faint)':mm<500?'var(--red)':mm<1000?'var(--amber)':'var(--cyan)';
 $('driveOut').textContent=fresh&&c.power!=null?(c.power===255?'OVERDRIVE':c.power+'%'):'—';
 $('ageText').textContent=fresh&&Number.isFinite(s.telemetryAgeMs)?s.telemetryAgeMs+' ms':'—';
 $('alertBox').classList.toggle('clear',$('warnings').textContent==='No reported warnings');
}
function paint(){
 document.querySelectorAll('.pad [data-drive]').forEach(b=>b.classList.toggle('held',armed&&held===b.dataset.drive));
 document.querySelectorAll('#speedSeg button').forEach(b=>b.classList.toggle('on',b.dataset.speed===$('speed').value));
 const live=!$('cameraFeed').hidden;$('standby').hidden=live;$('feedBox').classList.toggle('live',live);
}
setInterval(paint,60);
document.querySelectorAll('#speedSeg button').forEach(b=>b.onclick=()=>{$('speed').value=b.dataset.speed;$('speed').dispatchEvent(new Event('change'));paint();});
// Keyboard driving: same hold/release path as the on-screen pad. Only while
// this page holds an S3-confirmed arm; Space/Esc always disarm.
const driveKeys={KeyW:'f',ArrowUp:'f',KeyS:'b',ArrowDown:'b',KeyA:'l',ArrowLeft:'l',KeyD:'r',ArrowRight:'r'};let driveKey=null;
const typing=e=>e.target.closest?.('input,select,textarea,[contenteditable]');
document.addEventListener('keydown',e=>{
 if(embedded||e.ctrlKey||e.metaKey||e.altKey)return;
 if(e.code==='Space'||e.code==='Escape'){if(e.code==='Space'&&typing(e))return;e.preventDefault();$('stop').click();return;}
 if(typing(e))return;
 if(/^Digit[1-4]$/.test(e.code)){$('speed').value=['25','50','75','100'][Number(e.code.slice(5))-1];$('speed').dispatchEvent(new Event('change'));return;}
 const d=driveKeys[e.code];if(!d)return;e.preventDefault();if(e.repeat||!armed||driveKey)return;
 driveKey=e.code;held=d;command(2);
});
document.addEventListener('keyup',e=>{if(e.code==='Space'&&!embedded&&!typing(e))e.preventDefault();if(e.code===driveKey){driveKey=null;release();}});
window.addEventListener('blur',()=>{driveKey=null;});
refreshMast();lightSend(true);
setInterval(()=>{if(armed&&!document.hidden)command(2);},100);refresh();refreshVisual();
</script></html>)HTML";
