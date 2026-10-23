from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,zipfile,collections,traceback
import numpy as np
ROOT=Path('/home/buralien/projects/gladiator-cad');N=ROOT/'cad/v2/enclosure/round5-calibrated-28-20261022';P=N/'print';BENCH=N/'support-time-comparison';O=N/'shell-time-optimized'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def phase(s):js(O/'status.json',{'phase':s});print(s,flush=True)
try:
 phase('Validating selected conservative support changes')
 selected={'07':('hood_base35','GLAD_04_HOOD_SD_M2_28.3mf'),'08':('panels_normal_base35','GLAD_05_PANELS_SD_M2_28.3mf')}
 baseB=json.loads((P/'build-summary.json').read_text());B={'plates':{},'insert_bore_mm':2.8,'structural_changes':False};proof={}
 (O/'plates').mkdir(exist_ok=True)
 for k,(case,name) in selected.items():
  candidate=BENCH/case/(case+'.3mf');baseline=N/'SD_PACKAGE/plates'/name
  with zipfile.ZipFile(candidate) as z:files={f:z.read(f) for f in z.namelist()};cfg=json.loads(files['Metadata/project_settings.config'])
  with zipfile.ZipFile(baseline) as z:
   oldcfg=json.loads(z.read('Metadata/project_settings.config'));geometry=[f for f in files if f.startswith('3D/')]
   assert all(files[f]==z.read(f) for f in geometry)
  changes={name:value for name,value in cfg.items() if oldcfg.get(name)!=value}
  allowed={'support_base_pattern_spacing':'3.5'} if k=='07' else {'support_type':'normal(auto)','support_style':'snug','support_closing_radius':'0','support_base_pattern_spacing':'3.5'}
  assert changes==allowed,(k,changes)
  # Keep the original support speed as well as all extrusion, machine and filament settings.
  assert cfg['support_speed']=='60' and cfg['support_interface_speed']=='40'
  assert cfg['wall_loops']=='4' and cfg['sparse_infill_density']=='30%' and cfg['top_shell_layers']=='4' and cfg['bottom_shell_layers']=='4'
  assert cfg['support_interface_top_layers']=='2' and cfg['support_interface_bottom_layers']=='2' and cfg['support_interface_spacing']=='0.5'
  shutil.copy2(candidate,O/'plates'/name);entry=dict(baseB['plates'][k]);entry['file']=name;entry['settings_overrides']=cfg;B['plates'][k]=entry
  proof[k]={'changes':changes,'all_geometry_and_blockers_byte_identical':True,'all_other_settings_identical':True,'support_speed_unchanged':True,'dense_support_interfaces_unchanged':True}
 js(O/'build-summary.json',B);shutil.copy2(P/'native-mount-envelopes.json',O/'native-mount-envelopes.json')
 text=(P/'slice_and_check.py').read_text().replace(str(P),str(O));(O/'slice_and_check.py').write_text(text)
 phase('Final slices and toolpath checks')
 result=subprocess.run(['python3',str(O/'slice_and_check.py'),'07','08'],capture_output=True,text=True,cwd=ROOT,timeout=1800);(O/'slice-run.log').write_text(result.stdout+'\n'+result.stderr);assert result.returncode==0,result.stderr
 S={k:json.loads((O/'slice-check'/k/'check.json').read_text()) for k in selected}
 for k,s in S.items():
  assert s['exit_code']==0 and s['original_start_guard_passed'] and s['extrusions_fit_220_with_0_5mm_margin']
  warnings=[line for line in (O/'slice-check'/k/'slicer.log').read_text().splitlines() if re.search(r'error|warning|potentially lost|floating',line,re.I)];assert not warnings,(k,warnings)
  baseline=json.loads((P/'slice-check'/k/'segments.json').read_text());current=json.loads((O/'slice-check'/k/'segments.json').read_text())
  def structural_segments(data):return collections.Counter(tuple(round(v,5) for v in row[:5])+(row[5],) for row in data if not row[5].startswith('Support') and row[5] not in ['Custom','Brim','Skirt'])
  old=structural_segments(baseline);new=structural_segments(current);missing=sum((old-new).values());added=sum((new-old).values())
  proof[k]['structural_extrusion_segments_identical']=old==new;proof[k]['different_structural_segments']={'missing':missing,'added':added}
  assert old==new,(k,'Structural toolpaths changed',missing,added)
 # Reuse the established support-segment/cavity check on the new support structures.
 checker=(P/'verify_print_release.py').read_text();a=checker.index('bores=');b=checker.index('# A single-colour shell',a);checker=checker[a:b].replace("for key in ['02','07','08']:","for key in ['07','08']:")
 rep={'support_inside_new_insert_bores':{}};envelopes=json.loads((O/'native-mount-envelopes.json').read_text())
 exec(compile(checker,'optimized-shell-support-clearance','exec'),{'np':np,'json':json,'R':O,'B':B,'N':envelopes,'rep':rep})
 assert len(rep['support_inside_new_insert_bores'])==7
 assert all(x['centreline_samples_inside']==0 and x.get('segments_intersecting_bore_with_0_20mm_bead_allowance',0)==0 for x in rep['support_inside_new_insert_bores'].values())
 js(O/'support-clearance.json',rep);js(O/'structural-preservation.json',proof)
 # Render the final toolpaths for visual inspection of the support scaffolds.
 phase('Rendering toolpath previews')
 render=(P/'verify_print_release.py').read_text();a=render.index('# Toolpath top + side views');b=render.index("(R/'print-verification.json').write_text",a);render=render[a:b].replace("for k in ['01','02','03','04','05','06','07','08','09']:","for k in ['07','08']:")
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 from matplotlib.collections import LineCollection
 exec(compile(render,'optimized-shell-previews','exec'),{'Path':Path,'json':json,'R':O,'B':B,'S':S,'plt':plt,'LineCollection':LineCollection})
 phase('PASSED - ready for SD colour processing and release')
except BaseException:(O/'ERROR.txt').write_text(traceback.format_exc());phase('FAILED - see ERROR.txt')
