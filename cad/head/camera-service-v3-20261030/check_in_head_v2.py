"""Check camera service v3 in the current head v2 (Codex balanced model), against v2 as a baseline.
Run on cad-lab: python3 cad/head/camera-service-v3-20261030/check_in_head_v2.py
Swaps Camera_Tray/Camera_Cover for the v3 parts (same carrier screw pattern, same placement) and re-runs the
balanced model's motion grid (tilt -38..34 by 2, pan -20..180 by 20), then finds first-contact tilt angles.
"""
import sys, json, math
from pathlib import Path
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A, Part
V = A.Vector
ROOT = Path('/home/buralien/projects/gladiator-cad/cad/head')
BASE = ROOT / 'v2-mast-20261028'
BAL = BASE / 'balance-tensioner-20261030'
OUT = ROOT / 'camera-service-v3-20261030'
old = json.loads((BASE / 'validation.json').read_text())['v2']
T = V(*old['tilt_axis_world']); p = old['params']
tilt, pan, fixed = old['groups']['tilt'], old['groups']['pan'], old['groups']['fixed']
doc = A.openDocument(str(BAL / 'Gladiator_Head_v2_Balanced.FCStd'))
S = {o.Name: o.Shape.copy() for o in doc.Objects if o.TypeId == 'Part::Feature'}


def step_parts(fn):
    sh = Part.Shape(); sh.read(str(fn))
    sol = sorted(sh.Solids, key=lambda s: -s.Volume)
    for s in sol:                               # undo the review files' pan180 viewing pose
        s.rotate(V(39.5, 113, 0), V(0, 0, 1), 180)
    return sol[0], sol[1]                       # tray (bigger), cover


v2t, v2c = step_parts(ROOT / 'camera-service-v2-20261021/Gladiator_Camera_Service_v2.step')
v3t, v3c = step_parts(OUT / 'Gladiator_Camera_Service_v3.step')
d = S['Camera_Tray'].BoundBox.Center - v2t.BoundBox.Center
chk = v2t.copy(); chk.translate(d)
fit = chk.common(S['Camera_Tray']).Volume / S['Camera_Tray'].Volume
assert fit > 0.999, ('v2 tray does not map onto the balanced model by translation', fit)
chk = v2c.copy(); chk.translate(d)
fitc = chk.common(S['Camera_Cover']).Volume / S['Camera_Cover'].Volume
assert fitc > 0.999, ('cover mapping', fitc)
for s in (v3t, v3c): s.translate(d)
rep = {'placement_translation_from_v2_step': [round(d.x, 3), round(d.y, 3), round(d.z, 3)],
       'v2_mapping_fit': [round(fit, 5), round(fitc, 5)]}


def ov(a, b): return a.common(b).Volume if a.BoundBox.intersect(b.BoundBox) else 0.0


cases = {'v2': {'Camera_Tray': S['Camera_Tray'], 'Camera_Cover': S['Camera_Cover']},
         'v3': {'Camera_Tray': v3t, 'Camera_Cover': v3c}}
others = [n for n in S if n not in ('Camera_Tray', 'Camera_Cover')]
# home pose: the v3 parts against everything else in the head and robot context
rep['v3_home_overlaps_mm3'] = {n + ' vs ' + o: round(ov(s, S[o]), 4) for n, s in cases['v3'].items()
                               for o in others if o not in ('ESP32_CAM_Reference',) and ov(s, S[o]) > .05}
rep['v3_vs_ESP32_ref_mm3'] = round(ov(v3t, S['ESP32_CAM_Reference']) + ov(v3c, S['ESP32_CAM_Reference']), 4)
# fixed obstacles brought into the head frame at each pan angle (as the balanced builder does)
unit = V(*old.get('servo_unit', [0, 1, 0])) if 'servo_unit' in old else None
fixed_in_head = {}
for pn in range(-20, 181, 20):
    fixed_in_head[pn] = {}
    for n in fixed:
        if n not in S or n in ('Pan_Drive_Pulley', 'Pan_Horn_Reference'):
            continue
        q = S[n].copy(); q.rotate(V(39.5, 113, 0), V(0, 0, 1), -pn)
        fixed_in_head[pn][n] = q
for name, parts in cases.items():
    hits = []
    for t in range(-38, 35, 2):
        for pn_, s in parts.items():
            q = s.copy(); q.rotate(T, V(1, 0, 0), t)
            for b in pan:
                if b in S and ov(q, S[b]) > .05: hits.append([pn_, b, 'any-pan', t])
            for pn, obs in fixed_in_head.items():
                for b, o in obs.items():
                    if ov(q, o) > .05: hits.append([pn_, b, pn, t])
    rep[name + '_motion_hits_tilt-38..34'] = hits
    # first contact against the pan-side parts (yoke etc.), 1 degree steps
    first = {}
    for sgn, key in ((1, 'positive_tilt'), (-1, 'negative_tilt')):
        for a in range(0, 91):
            hit = None
            for pn_, s in parts.items():
                q = s.copy(); q.rotate(T, V(1, 0, 0), sgn * a)
                for b in pan:
                    if b in S and ov(q, S[b]) > .05: hit = [pn_, b]
            if hit:
                first[key] = [sgn * a] + hit
                break
    rep[name + '_first_contact_vs_pan_side'] = first
    print(name, first, len(hits), flush=True)
rep['v3_motion_clear'] = not rep['v3_motion_hits_tilt-38..34']
(OUT / 'check_in_head_v2.json').write_text(json.dumps(rep, indent=1))
print(json.dumps(rep, indent=1))
