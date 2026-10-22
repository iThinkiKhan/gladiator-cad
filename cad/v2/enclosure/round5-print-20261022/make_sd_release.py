from pathlib import Path
import json,zipfile,hashlib,shutil,subprocess,xml.etree.ElementTree as E,re,sys
import postprocess_sd_colours as colour
ROOT=Path('/home/buralien/projects/gladiator-cad');R=ROOT/'cad/v2/enclosure/round5-print-20261022';SRC=R.parent/'round5-20261021'
B=json.loads((R/'build-summary.json').read_text());S={k:json.loads((R/'slice-check'/k/'check.json').read_text()) for k in B['plates']};V=json.loads((R/'print-verification.json').read_text());PK=R/'SD_PACKAGE';PK.mkdir(exist_ok=True)
for n in ['PRINT_FIRST','HOLD_INSERTS','plates','reports','previews','CAD']:(PK/n).mkdir(exist_ok=True)
assert V['all_22_source_parts_covered'] and V['all_slicer_guards_passed'] and V['all_extrusions_fit_220'] and V['source_hashes_unchanged']
assert len(V['support_inside_new_insert_bores'])==13
assert all(x['centreline_samples_inside']==0 for x in V['support_inside_new_insert_bores'].values())
assert not any(V['slicer_errors'].values())
# Verify presets independently against their full local inheritance, excluding profile metadata and host credentials.
P=Path.home()/'.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer'
def flat(path):
 d=json.loads(path.read_text());o={}
 if d.get('inherits'):
  nm=d['inherits']+'.json';hits=list((P/'user/default').rglob(nm))+list((P/'system').rglob(nm));assert hits,nm;o=flat(hits[0])
 o.update(d);return o
machine=flat(P/'user/default/machine/EnderNeo SAFE.json')
mat={name:flat(P/'user/default/filament'/(name+'.json')) for name in ['Generic PLA @System - First Print','Generic PLA Silk @System - First Print']}
SKIP={'name','type','from','version','inherits','compatible_printers','compatible_printers_condition','print_settings_id','printer_settings_id','filament_settings_id','printhost_apikey','print_host','printhost_user','printhost_password','default_print_profile','default_filament_profile'}
audit={'profiles':{},'original_source_hashes_unchanged':True,'SD_colour_stops':{},'print_file_guards':{},'status':'Prepared; actual M2 insert dimensions/coupon and physical joint checks pending.'}
for path,h in json.loads((SRC/'validation.json').read_text())['source_hashes'].items():
 assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
# Normal meshes stay fixed; fix part-ID metadata, retain the user's SAFE guard, add SD colour hook where needed.
C='{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
for key,info in B['plates'].items():
 f=R/'plates'/info['file']
 with zipfile.ZipFile(f) as z:files={n:z.read(n) for n in z.namelist() if n!='Metadata/slice_info.config'}
 d=json.loads(files['Metadata/project_settings.config']);which='Generic PLA Silk @System - First Print' if key=='06' else 'Generic PLA @System - First Print'
 mm={k:(v,d.get(k)) for k,v in machine.items() if k in d and k not in SKIP and d[k]!=v}
 ff={k:(v,d.get(k)) for k,v in mat[which].items() if k in d and k not in SKIP and d[k]!=v}
 assert not mm,(key,'machine differs',mm)
 assert not ff,(key,'filament differs',ff)
 assert d['printer_settings_id']=='EnderNeo SAFE' and d['filament_settings_id']==[which]
 assert '/usr/bin/python3 /home/buralien/bin/check-ender3-start.py' in d['post_process']
 assert d['curr_bed_type']=='High Temp Plate' and d['hot_plate_temp']==['60']
 audit['profiles'][key]={'machine':'EnderNeo SAFE','filament':which,'machine_fields_match':True,'filament_fields_match':True,'selected_bed':'High Temp Plate / user 60 C','declared_bed':d['printable_area'],'verified_extrusions_within_mm':[220,220]}
 if key in colour.TARGETS:
  hook=f'/usr/bin/python3 {R}/postprocess_sd_colours.py --plate {key}'
  if hook not in d['post_process']:d['post_process'].append(hook)
 files['Metadata/project_settings.config']=json.dumps(d,indent=2).encode()
 model=E.fromstring(files['3D/3dmodel.model']);ms=E.fromstring(files['Metadata/model_settings.config'])
 for obj in ms.findall('object'):
  parent=next(x for x in model.find(C+'resources') if x.get('id')==obj.get('id'))
  obj.find('part').set('id',parent.find(C+'components')[0].get('objectid'))
 files['Metadata/model_settings.config']=E.tostring(ms,encoding='utf-8',xml_declaration=True)
 with zipfile.ZipFile(f,'w',zipfile.ZIP_DEFLATED) as z:
  for n,dat in files.items():z.writestr(n,dat)
 destname=('HOLD_' if key in ['01','02','07','08'] else '')+info['file'];shutil.copy2(f,PK/'plates'/destname)
 # Plain, already-sliced SD print code. Long insert-dependent jobs have a nonprintable suffix.
 name={'00':'R5_00_M2_COUPON','00H':'R5_00C_SIDE_OPTIONAL','01':'R5_01_FIT_SEATS','02':'R5_02_BLACK_CLAMPS','03':'R5_03_RED_PARTS','04':'R5_04_WHITE_INSETS','05':'R5_05_TABLETS_SD','06':'R5_06_SILK_DETAIL','07':'R5_07_HOOD_SD','08':'R5_08_PANELS_SD','09':'R5_09_LENS_NATURAL'}[key]
 source=R/'slice-check'/key/'plate_1.gcode';data=source.read_bytes().decode('utf-8')
 held=key in ['01','02','07','08'];directory=PK/('HOLD_INSERTS' if held else 'PRINT_FIRST');dest=directory/(name+('.gcode.pending' if held else '.gcode'))
 if key in colour.TARGETS:
  data,rep=colour.make(data,key);audit['SD_colour_stops'][key]=rep
  (PK/'reports'/(name+'-colour-stops.json')).write_text(json.dumps(rep,indent=2))
 dest.write_bytes(data.encode('utf-8'))
 guard=subprocess.run(['python3','/home/buralien/bin/check-ender3-start.py',str(dest)],capture_output=True,text=True);assert guard.returncode==0,(name,guard.stdout)
 audit['print_file_guards'][dest.name]=True
 if key in ['07','08']:
  plain=directory/(name.replace('_SD','_SINGLE_COLOUR')+'.gcode.pending');shutil.copy2(source,plain)
  guard=subprocess.run(['python3','/home/buralien/bin/check-ender3-start.py',str(plain)],capture_output=True,text=True);assert guard.returncode==0
  audit['print_file_guards'][plain.name]=True
# Remove only the obsolete, previously generated unheld fit-seat file.
stale=PK/'PRINT_FIRST/R5_01_FIT_SEATS.gcode'
if stale.exists():stale.unlink()
stale=Path.home()/'3D-Printer/Incoming/Gladiator/Round5_SD_20261022/PRINT_FIRST/R5_01_FIT_SEATS.gcode'
if stale.exists():stale.unlink()
for stale in [PK/'plates/R5_01_Fit_Seats.3mf',Path.home()/'3D-Printer/Incoming/Gladiator/Round5_SD_20261022/plates/R5_01_Fit_Seats.3mf']:
 if stale.exists():stale.unlink()
# Two click checks, with no homing, axis motion, heating or extrusion. This is a diagnostic, not a production print.
(PK/'PRINT_FIRST/R5_00A_LCD_PAUSE_TEST.gcode').write_text('; SD LCD-only diagnostic: no heat, homing, axis motion or extrusion.\n; It must wait twice for separate button clicks.\nM84 S0\nM117 Pause test 1 click\nM300 S880 P200\nM0 Test 1 click\nM117 Pause test 2 click\nM300 S1100 P200\nM0 Test 2 click\nM84 S120\nM117 SD pause test PASS\nM300 S1320 P500\n')
# Complete native print variant; the earlier styling model and original v2.8 remain untouched.
reinforcement=json.loads((R/'crest-clamp-reinforcement.json').read_text());assert reinforcement['passed']
for nm in ['Gladiator_Round5_Print.FCStd','Gladiator_Round5_PrintParts.step']:shutil.copy2(R/nm,PK/'CAD'/nm)
shutil.copy2(R/'print-stl/Crest_Clamp.stl',PK/'CAD/Reinforced_Crest_Clamp.stl')
for nm in ['crest-clamp-reinforcement.json','SD-pause-state-verification.json','optional-horizontal-coupon.json']:shutil.copy2(R/nm,PK/'reports'/nm)
B['status']='All slicing checks complete. Physical M2 sizing, joint checks and LCD test pending.'
(R/'build-summary.json').write_text(json.dumps(B,indent=2))
# Critical source provenance and concise reports, not intermediate toolpath JSON.
for n in ['build-summary.json','slice-summary.json','print-verification.json','support-blockers.json','fit-test-sources.json','native-mount-envelopes.json','preset-provenance.json']:
 shutil.copy2(R/n,PK/'reports'/n)
for n in ['independent-verification.json','final-export-verification.json']:
 shutil.copy2(SRC/n,PK/'reports'/('CAD-'+n))
for p in (R/'previews').glob('*.png'):shutil.copy2(p,PK/'previews'/p.name)
shutil.copy2(R/'postprocess_sd_colours.py',PK/'postprocess_sd_colours.py')
shutil.copy2(Path('/home/buralien/bin/check-ender3-start.py'),PK/'check-ender3-start.py')
(PK/'reports/release-audit.json').write_text(json.dumps(audit,indent=2))
def dur(sec):return f'{sec//3600}h {(sec%3600)//60:02d}m' if sec>=3600 else f'{sec//60}m {sec%60:02d}s'
rows=[]
for k in sorted(B['plates']):
 t=V['plate_times'][k];rows.append(f'| {k} | {B["plates"][k]["file"].split("_",2)[2][:-4].replace("_"," ")} | {dur(t["seconds"])} | {t["grams"]:.1f} g |')
changes=[]
for k,r in audit['SD_colour_stops'].items():
 total=V['plate_times'][k]['seconds']
 for c in r['changes']:
  elapsed=max(0,total-int((c.get('remaining_estimated_minutes') or 0)*60))
  changes.append(f'| {k} | {c["load_colour"]} | {c["actual_model_boundary_mm"]:.2f} mm | about {dur(elapsed)} after start |')
readme=f'''# Round 5: SD print preparation, 22 October 2026

**CAD and slicing checks pass. The insert-dependent production files remain on HOLD.** The latest listing identifies nominal M2 D3 L3 inserts (3 mm OD, 3 mm length); delivered stock and the physical bore winner remain unconfirmed. Your selected four-hole mini replaces the earlier large coupon in this pack. Current CAD assumes a 3.6 mm bore, 4.0 mm depth and 3.0 mm insert. The3.6mm candidate bores are not a recommendation for nominalD3 stock. Replace them with the tested winning size before releasing production; stock dimensions alone do not approve a pilot bore. These files are separate from the old CAD; the old model is untouched.

Use the supplied **SD G-code**, which includes the verified SAFE start and the SD colour stops. No printer or queue was started or changed. The LCD-only diagnostic is explicitly a nonprinting test.

## Your presets

- Printer: **EnderNeo SAFE**, with its full inherited machine settings and original start-code guard.
- PLA: **Generic PLA @System - First Print**, process based on **0.20mm Standard - FIrst Layer Comp**.
- Silk: **Generic PLA Silk @System - First Print**, process based on **0.20mm Silk Toys @ First Print - SAFE**. Its 220 C first layer / 215 C other layers, 0.98 flow ratio, 7.5 mm3/s filament limit and 0.5 mm filament retraction override are retained.
- Both use your **60 C hot-plate setting**, selected as High Temp Plate. No global preset file was edited. SAFE declares 235 mm; every actual extrusion was independently checked against the printer's 220 x 220 mm configured print area.
- Per-plate process changes are listed in reports/build-summary.json: layer height, detail speeds, supports and brims. Shells retain four walls and 30% infill. The 45-degree support threshold is intentional for these shell overhangs. Clamps print on their broad sides without supports; red shield fields print on their flat backs. Hood uses snug normal supports, with local blockers keeping insert paths clear.

## Start with the short checks

1. Run **PRINT_FIRST/R5_00A_LCD_PAUSE_TEST.gcode** from SD. It must stop twice and wait for a separate LCD click each time. It does not heat, home, move or extrude. If it runs straight through, do not run a colour-change job: report that result first.
2. Print **00 M2 coupon**, in regular PLA: your selected four-hole mini, upright bores 2.8, 2.9, 3.0, 3.1 mm left to right, 3.6 mm deep. Clipped corner is the 2.8 end. **00C SIDE OPTIONAL** is a separate small strip with the same four sizes, printing the holes horizontally; use it to confirm the sideways result before committing the shell mounts. Current **01 fit seats** still contain provisional 3.6 mm bores and are held until the winning bore is applied. Nominal 3 mm OD does not make a 3.6 mm bore acceptable.
3. Print **03 red parts**, **04 white insets**, **05 tablets** and **06 silk detail**. Use the actual intended filaments. The 05 tablets start WHITE and stop for RED after the 1.5 mm base. Keep the exported orientations. The thin white emblems stand on their lower edges; leave them on the bed until cool and clip away tree supports in small pieces while supporting the white part.
4. Fit the full curved white inset to a red shield without forcing it. After the tested bore is applied and01 fit seats are regenerated, fit the red field to the sample seat, and check the boss screw stack after inserting a correctly sized insert. Test the tablet end and the aquila's two locator holes on their sample seats. The fit-seat samples are clipped from the actual CAD, not simplified substitute joints.
5. When the inserts arrive, measure outside diameter and length; check the upright and sideways bore winners and actual M2 screw-head diameter/height. Current decorative counterbores are 4.5 mm diameter. Report those values and the inset fit before the long prints. If the bore/depth changes, the affected CAD and sliced files need updating; do not force a larger insert into a provisional mount.
6. **HOLD_INSERTS/** contains fit seats, black clamps and both shell jobs with a `.pending` suffix. Leave that suffix until hardware/fit is confirmed. The clamp set is a short job and includes three spare shoes. Confirm the clamps seat on the actual head, and check the loaded head movement before the event.

CAD/Gladiator_Round5_Print.FCStd is the current print variant. Only the new crest clamp received a lower web to enclose its insert bore, with a small yoke-clearance relief; its original contact faces remain unchanged. The added material clears the head at51 sampled tilt poses, one degree apart, and a full0.5mm material ring around the assumed3mm insert engagement was checked at432 points. Test retention on the actual printed clamp before fitting the crest. The earlier styling CAD and original v2.8 remain untouched. The original v2.8 fit interfaces remain unchanged in CAD. There is no recorded confirmation here that the complete v2.8 shell has been fitted over the current wiring on the assembled robot. If you already have that shell, dry-fit it now; real wiring clearance still needs checking on the robot.

## SD colour changes

The stop uses Marlin **M0** and the printer LCD ([Marlin reference](https://marlinfw.org/docs/gcode/M000-M001.html)). There are two clicks per change: first click confirms you are present, then the nozzle reheats; at the second stop release the extruder idler, change filament, hand-purge until the new colour is pure, wipe the nozzle, reengage the idler, then click. Keep the head and bed still. The script parks at X10 Y180, 5 mm above the saved nozzle height, then restores XYZ, relative extrusion, the saved extrusion coordinate and feed rate. It temporarily holds the axes with M84 S0 and restores a 120-second runtime idle timeout after resume; it writes no EEPROM settings. Attend the actual swap promptly after the second stop.

| Plate | Load | Actual body colour boundary | Estimated stop time |
| --- | --- | --- | --- |
{chr(10).join(changes)}

Both shell jobs start RED and have three changes: GREY, RED, GREY. The hood and panels have different belt heights because their roofs have different heights. **Do not use one shell's pause heights for the other.** Optional SINGLE_COLOUR shell files have the identical geometry and no colour stops, for a grey print with painted red bands if timing makes attended swaps impractical. They remain held for insert sizing too.

The 3MFs in plates/ retain your Linux SAFE checker and add the SD colour processor for plates 05, 07, 08. Those script paths refer to cad-lab. On Windows, use the supplied G-code for SD; reslicing there requires configuring equivalent local script paths. Changing layer heights or orientations requires reslicing and regenerating the stops.

## Print budget

| Plate | Contents | Slicer time | Filament including support |
| --- | --- | --- | --- |
{chr(10).join(rows)}

All {len(B["plates"])} jobs (including the optional sideways strip): **{dur(V['all_plates_seconds'])}**, about **{sum(t['grams'] for t in V['plate_times'].values()):.0f} g**. The two shell jobs total **{dur(V['shells_seconds'])}**. These estimates exclude warm-up/cooldown between jobs, manual purge waste, waiting at colour stops, support removal and assembly. Reserve at least 6-8 additional hours for handling, fit checks and assembly within the two-day window; keep extra time for a small correction.

While waiting for the inserts, use the short checks and decorative jobs to confirm fit and colour changes. Once insert sizing is settled, the long shells can occupy the next two available attended print windows.

## What has actually been verified

All 22 source print parts are present. Original CAD/source hashes remain unchanged; prior saved-file checks prove original wall material, rail/deck/head interfaces and service paths are retained. All {len(B["plates"])} final slices pass the original Ender SAFE start checker and produce extrusions within 220 x 220. No lost-branch or other reported slicer errors remain. Analytic support segment checks, including a0.20mm bead-radius allowance, are clear of all thirteen new insert bores; clamps use no support at all. These are CAD/toolpath checks, not a promise of physical fit, actual insert retention or loaded servo performance.

Reports include preset provenance, final process values, source hashes, clearance evidence, support blockers and per-file SD colour-stop states. SHA256SUMS.json authenticates the supplied package.
'''
(PK/'START_HERE.md').write_text(readme)
manifest={str(p.relative_to(PK)):hashlib.sha256(p.read_bytes()).hexdigest() for p in PK.rglob('*') if p.is_file() and p.name!='SHA256SUMS.json'}
(PK/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=2))
archive=R/'Gladiator_Round5_SD_PRINT_PREP_20261022.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in PK.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(PK))
incoming=Path.home()/'3D-Printer/Incoming/Gladiator/Round5_SD_20261022';incoming.mkdir(exist_ok=True)
for p in PK.rglob('*'):
 if p.is_file():dst=incoming/p.relative_to(PK);dst.parent.mkdir(exist_ok=True);shutil.copy2(p,dst)
print(json.dumps({'package':str(PK),'zip':str(archive),'zip_mb':round(archive.stat().st_size/1e6,2),'files':len(manifest),'total_time':dur(V['all_plates_seconds']),'shell_time':dur(V['shells_seconds']),'profile_audit':all(a['machine_fields_match'] and a['filament_fields_match'] for a in audit['profiles'].values()),'colour_stops':audit['SD_colour_stops']},indent=2))




