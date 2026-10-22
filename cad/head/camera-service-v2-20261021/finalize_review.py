from pathlib import Path
import json, hashlib, zipfile, os, subprocess, time
root=Path('/home/buralien/projects/gladiator-cad')
p=root/'cad/head/camera-service-v2-20261021'
v=json.loads((p/'validation.json').read_text())
ind=json.loads((p/'independent-verification.json').read_text())
assert v['checks']['all_asserts_pass'] and ind['pass']
assert v['service_v2']['camera_side_shift_mm']==1.5
desktop=Path('/home/buralien/Desktop/Gladiator-Camera-v2.desktop')
content='[Desktop Entry]\nType=Application\nName=Gladiator Camera v2 - Review\nComment=Camera cradle with lay-in wiring and M3 nut-retained cover\nExec=/usr/bin/freecad '+str(p/'Gladiator_Camera_Service_v2_REVIEW.FCStd')+'\nIcon=freecad\nTerminal=false\nCategories=Development;\n'
assert not desktop.exists() or 'Camera v2' in desktop.read_text()
desktop.write_text(content); desktop.chmod(0o755)
note=root/'docs/ai/agents/codex-camera-service-v2-20261021.md'
note.write_text('''# Camera service v2 — 2026-10-21
Jim requested a redesign because the fitted camera cover falls off and Duponts are difficult to thread.
Source on cad-lab: scripts/build_esp32_cam_case_v4.py and cad/head/esp32-cam-case-v4/ (untracked prior work, preserved).
New isolated review folder: cad/head/camera-service-v2-20261021/.
Two printed parts; 2 x M3x12 and side-loaded M3 nuts replace four plastic-threaded M2 cover screws.
Both side slots open to the cover seam; cover skirts close after pre-wired board insertion; exit height 4.5.
Two rear-lug tie passages; chamfers on floor/skirt wire-contact edges.
Camera/cradle shifts head-local +X by 1.5 mm for 2.275 clearance to the ToF frame. Original three carrier mounting holes remain; screwdriver scallops preserve access.
Current robot-facing view is legacy pan180. Existing travel and robot orientation are unchanged.
Checks: 16 connectors/wire lay-in paths, board insertion/cover removal, board/case/driver/SD/field clearance, 231 sampled pan/tilt poses and 51 fine tilt poses.
Independent saved-file checks: native reload, STEP equality, watertight STL/solid reconstruction, mesh volume, installed wire paths versus head context, fasteners and 1071 hardware-motion poses.
Review draft: actual connector dimensions/bend radius, skirt fit and M3 hardware remain unverified. Wires stop just outside the case openings; full route to mast not modeled. Board retention still depends on cover corner posts.
No existing CAD, print plates, printer queue, servo or firmware changes. No print started. No Git commit or push.
Desktop launcher: Gladiator-Camera-v2.desktop. Local mirror: X:/Projects/Gladiator/camera-mount-v2-20261021/.
''')
handoff=root/'docs/ai/HANDOFF.md'
h=handoff.read_text()
entry='''## Camera service v2 review — 2026-10-21 (Codex)

Jim requested a cover/wiring redesign. Isolated native assembled/exploded models, STEP, review STLs, sources and validation: cad/head/camera-service-v2-20261021/. Two M3 nut-retained cover screws, open lay-in side channels with closing skirts, tie passages and wire-edge chamfers. Carrier hole pattern retained; camera moves 1.5 mm sideways for a 2.275 mm ToF-frame gap. Construction and independent saved-file checks passed. Desktop launcher: Gladiator Camera v2 - Review. Await Jim's CAD review; actual harness bend room, skirt fit and M3 stock need physical confirmation. Full bundle-to-mast routing not modeled. Existing CAD/plates/queue unchanged; no print started. Details: agents/codex-camera-service-v2-20261021.md.

'''
if '## Camera service v2 review — 2026-10-21 (Codex)' not in h:
    handoff.write_text(h.replace('# Current Handoff\n','# Current Handoff\n\n'+entry,1))
diag=p/'diagnostics'; diag.mkdir(exist_ok=True)
for name in ('error.txt','verification-error.txt'):
    f=p/name
    if f.exists(): f.rename(diag/('superseded-'+name))
files=[f for f in p.iterdir() if f.is_file() and f.suffix in ('.py','.md','.FCStd','.step','.png','.json') and f.name not in ('manifest.json','validation-prelim.json','finalize_review.py')]
files+=list((p/'stl').glob('*.stl'))
manifest={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
(p/'manifest.json').write_text(json.dumps(manifest,indent=2))
files.append(p/'manifest.json')
with zipfile.ZipFile(p/'Gladiator_Camera_Service_v2_REVIEW.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in files:z.write(f,str(f.relative_to(p)))
env=os.environ.copy()
proc=Path('/proc/2720/environ')
if proc.exists():
    for item in proc.read_bytes().split(b'\0'):
        if b'=' in item:
            k,val=item.split(b'=',1)
            if k in (b'DISPLAY',b'XAUTHORITY',b'DBUS_SESSION_BUS_ADDRESS',b'XDG_RUNTIME_DIR'):
                env[k.decode()]=val.decode()
assert env.get('DISPLAY'), 'No active desktop display found'
with open(p/'desktop-open.log','w') as out:
    proc=subprocess.Popen(['/usr/bin/freecad',str(p/'Gladiator_Camera_Service_v2_REVIEW.FCStd')],env=env,stdout=out,stderr=out,stdin=subprocess.DEVNULL,start_new_session=True)
time.sleep(2)
print(json.dumps({'review_folder':str(p),'desktop_launcher':str(desktop),'review_process':proc.pid,'launcher_returncode':proc.poll(),'construction_pass':True,'independent_pass':True,'bundle_bytes':(p/'Gladiator_Camera_Service_v2_REVIEW.zip').stat().st_size},indent=2))

