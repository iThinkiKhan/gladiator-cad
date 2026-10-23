from pathlib import Path
import hashlib,json,subprocess,shutil,time,traceback,zipfile
root=Path('/home/buralien/projects/gladiator-cad');N=root/'cad/v2/enclosure/round5-calibrated-28-20261022';P=N/'print';O=root/'cad/v2/enclosure/round5-print-20261022'
def phase(name):
 (N/'pipeline-status.json').write_text(json.dumps({'phase':name,'unix_time':time.time()},indent=2));print(name,flush=True)
def run(script,outputs,args=[],gui=False):
 phase(script.name)
 log=(N/(script.stem+'-run.log')).open('w')
 cmd=['xvfb-run','-a','freecad',str(script)] if gui else ['python3',str(script)]+args
 p=subprocess.run(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=1800);assert p.returncode==0,(script,p.returncode)
 for f in outputs:assert f.exists(),('missing',str(f))
 for f in list(N.glob('*ERROR*'))+list((N/'style').glob('*ERROR*'))+list(P.glob('*ERROR*')):raise RuntimeError(str(f)+': '+f.read_text()[-5000:])
try:
 phase('Waiting for calibrated style build')
 for _ in range(180):
  if (N/'style/BUILD_ERROR.txt').exists():raise RuntimeError((N/'style/BUILD_ERROR.txt').read_text())
  if (N/'style/validation.json').exists():break
  time.sleep(5)
 assert (N/'style/validation.json').exists()
 run(N/'native_mount_envelopes.py',[P/'native-mount-envelopes.json'],gui=True)
 run(N/'build_print_variant.py',[P/'Gladiator_Round5_Print.FCStd',P/'crest-clamp-reinforcement.json'],gui=True)
 run(N/'prepare_fit_samples.py',[P/'fit-test-sources.json'],gui=True)
 run(N/'verify_saved_28.py',[N/'saved-cad-verification.json'],gui=True)
 shutil.copy2(O/'fit-test-stl/M2_D3_L3_Sideways_Optional.stl',P/'fit-test-stl/M2_D3_L3_Sideways_Optional.stl')
 shutil.copy2(O/'optional-horizontal-coupon.json',P/'optional-horizontal-coupon.json')
 run(P/'build_print_plates.py',[P/'build-summary.json'])
 # The approved stronger 04B replaces the old thin white plate.
 B=json.loads((P/'build-summary.json').read_text());strong=O/'emblem-v2/R5_04B_White_Shield_Emblems_v2_STRONGER.3mf'
 shutil.copy2(strong,P/'plates'/strong.name);oldplate=P/'plates'/B['plates']['04']['file'];oldplate.rename(oldplate.with_suffix('.3mf.superseded'))
 B['plates']['04']['file']=strong.name
 with zipfile.ZipFile(strong) as z:cfg=json.loads(z.read('Metadata/project_settings.config'))
 B['plates']['04']['settings_overrides']=cfg
 stl=O/'emblem-v2/Scutum_Emblem_v2.stl'
 for entry in B['plates']['04']['parts']:
  entry['source']=str(stl.relative_to(root));entry['size_mm']=[27.3,41.6,5.41];entry['brim_mm']=3
 B['source_hashes'][str(stl.relative_to(root))]=hashlib.sha256(stl.read_bytes()).hexdigest()
 B['insert_bore_mm']=2.8;B['insert_bore_basis']='Jim coupon result 2026-10-22';B['white_insets']='stronger v2, approved 04B plate'
 (P/'build-summary.json').write_text(json.dumps(B,indent=2))
 run(P/'add_support_blockers.py',[P/'support-blockers.json'])
 for k in ['00','00H','03','05','06','09']:
  shutil.copytree(O/'slice-check'/k,P/'slice-check'/k,dirs_exist_ok=True)
 run(P/'slice_and_check.py',[P/'slice-check'/k/'check.json' for k in ['01','02','04','07','08']],args=['01','02','04','07','08'])
 # Reuse the established finite-segment support/bore verification with new radius and paths.
 text=(O/'verify_print_release.py').read_text().replace('cad/v2/enclosure/round5-print-20261022','cad/v2/enclosure/round5-calibrated-28-20261022/print')
 text=text.replace('root=R.parents[3]',"root=Path('/home/buralien/projects/gladiator-cad')")
 a=text.index('covered=set(');b=text.index("rep['all_22_source_parts_covered']",a)
 text=text[:a]+"expected=set(p.name for p in (root/'cad/v2/enclosure/round5-calibrated-28-20261022/style/stl').glob('*.stl'))\ncovered={p['name']+'.stl' for info in B['plates'].values() for p in info['parts'] if p['name']+'.stl' in expected}\n"+text[b:]
 text=text.replace(',1.8,4',',1.4,4').replace(',1.8,3.9',',1.4,3.9')
 (P/'verify_print_release.py').write_text(text)
 run(P/'verify_print_release.py',[P/'print-verification.json'])
 rep=json.loads((P/'print-verification.json').read_text())
 assert rep['source_hashes_unchanged'] and rep['all_22_source_parts_covered'] and rep['all_slicer_guards_passed'] and rep['all_extrusions_fit_220']
 assert len(rep['support_inside_new_insert_bores'])==13
 assert all(v['centreline_samples_inside']==0 and v.get('segments_intersecting_bore_with_0_20mm_bead_allowance',0)==0 for v in rep['support_inside_new_insert_bores'].values())
 assert not any(rep['slicer_errors'].values()),rep['slicer_errors']
 protected=json.loads((N/'protected-source-hashes.json').read_text())
 for rel,h in protected.items():assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==h
 phase('CAD and slice checks PASSED; ready for packaging')
except BaseException:
 (N/'PIPELINE_ERROR.txt').write_text(traceback.format_exc());phase('FAILED; see PIPELINE_ERROR.txt')
