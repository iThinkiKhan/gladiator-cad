from pathlib import Path
import json,zipfile,hashlib,math,shutil
import numpy as np
R=Path('/home/buralien/projects/gladiator-cad');S=R/'cad/v2/enclosure/round5-20261021';OUT=R/'cad/v2/enclosure/round5-print-20261022'
OUT.mkdir(exist_ok=True);(OUT/'plates').mkdir(exist_ok=True)
# Reuse reviewed 3MF packaging helpers without executing their previous plate builds.
code=(R/'scripts/build_v2_savings_plates.py').read_text().split('summary = {}')[0]
ns={};exec(compile(code,'existing-3mf-packager','exec'),ns)
ns['OUT']=OUT/'plates';ns['INCOMING']=OUT/'plates';ns['shutil'].copy2=lambda *a,**k:None
oldread=ns['read_stl'];rotations={};rotationsY={'Crest_Clamp':90,'Neck_Clamp_0':90,'Neck_Clamp_1':90}
def read(p):
 t=oldread(p);a=rotations.get(p.stem)
 if a is not None:
  th=math.radians(a);m=np.array([[1,0,0],[0,math.cos(th),-math.sin(th)],[0,math.sin(th),math.cos(th)]])
  t=t@m.T
 if p.stem in rotationsY:
  th=math.radians(rotationsY[p.stem]);m=np.array([[math.cos(th),0,math.sin(th)],[0,1,0],[-math.sin(th),0,math.cos(th)]]);t=t@m.T
 return t
ns['read_stl']=read
rotations.update(Scutum_Field_L=-90,Scutum_Field_R=-90,Neck_Guard=180)
PROFILE_ROOT=Path.home()/'.var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer'
profile_files={}
def flatten_profile(path):
 d=json.loads(path.read_text());q={}
 if d.get('inherits'):
  nm=d['inherits']+'.json'
  hits=list((PROFILE_ROOT/'user/default').rglob(nm))+list((PROFILE_ROOT/'system').rglob(nm))
  if not hits:raise RuntimeError('Missing inherited preset: '+nm)
  q=flatten_profile(hits[0])
 q.update(d);profile_files[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest();return q
presets={}
for kind,name in [('machine','EnderNeo SAFE'),('filament','Generic PLA @System - First Print'),('filament','Generic PLA Silk @System - First Print'),('process','0.20mm Standard - FIrst Layer Comp'),('process','0.20mm Silk Toys @ First Print - SAFE')]:
 presets[name]=flatten_profile(PROFILE_ROOT/'user/default'/kind/(name+'.json'))
SKIP={'name','type','from','version','inherits','compatible_printers','compatible_printers_condition','print_settings_id','printer_settings_id','filament_settings_id','printhost_apikey','print_host','printhost_user','printhost_password'}
template_config=json.loads(zipfile.ZipFile(ns['TPL']).read('Metadata/project_settings.config'))
def full_profile(filament,process):
 out={}
 for p in [presets['EnderNeo SAFE'],presets[filament],presets[process]]:
  out.update({k:v for k,v in p.items() if k in template_config and k not in SKIP})
 out.update(printer_settings_id='EnderNeo SAFE',filament_settings_id=[filament],print_settings_id=process,
            curr_bed_type='High Temp Plate',printhost_apikey='',print_host='')
 return out
base=full_profile('Generic PLA @System - First Print','0.20mm Standard - FIrst Layer Comp')
user_silk=full_profile('Generic PLA Silk @System - First Print','0.20mm Silk Toys @ First Print - SAFE')
(OUT/'preset-provenance.json').write_text(json.dumps({'request':'Use Jim EnderNeo SAFE and separate silk filament settings. Full inheritance resolved.',
 'profile_file_sha256':profile_files,'machine_preset':'EnderNeo SAFE','PLA_filament_preset':'Generic PLA @System - First Print',
 'silk_filament_preset':'Generic PLA Silk @System - First Print','PLA_process_preset':'0.20mm Standard - FIrst Layer Comp',
 'silk_process_preset':'0.20mm Silk Toys @ First Print - SAFE','plate_overrides':'Layer height, support setup, brim and detail speeds as listed in build-summary. Machine and filament values retained. High Temp Plate selects user hot_plate_temp60; real toolpaths checked against220 although SAFE declares235.',
 'PLA_flat_settings':{k:v for k,v in base.items() if k not in SKIP},'silk_flat_settings':{k:v for k,v in user_silk.items() if k not in SKIP}},indent=2))
shell={**base,'support_threshold_angle':'45','layer_height':'0.28','enable_support':'1','support_type':'tree(auto)'}
fine={**base,'support_threshold_angle':'45','layer_height':'0.16','initial_layer_print_height':'0.2','wall_loops':'4','enable_support':'1','support_type':'tree(auto)','support_top_z_distance':'0.16','outer_wall_speed':'30','inner_wall_speed':'45','top_surface_speed':'30','elefant_foot_compensation':base['elefant_foot_compensation']}
white={**fine,'layer_height':'0.12','initial_layer_print_height':'0.2','outer_wall_speed':'25','inner_wall_speed':'35','support_top_z_distance':'0.12','support_object_xy_distance':'0.3','support_interface_top_layers':'3'}
tablet={**white,'initial_layer_print_height':'0.18','enable_support':'0'}
black={**fine,'enable_support':'0','outer_wall_speed':'30','inner_wall_speed':'40','sparse_infill_density':'40%'}
silk={**user_silk,**{k:v for k,v in white.items() if k not in base or v!=base[k]},'filament_settings_id':['Generic PLA Silk @System - First Print'],'print_settings_id':'0.20mm Silk Toys @ First Print - SAFE'}
# Use the user's existing silk temperatures. Conservative speeds, not a newly calibrated filament profile.
def part(n,xy,brim=4,source=None):return (n,source or S/'stl'/(n+'.stl'),xy,'outer_only' if brim else 'no_brim',brim)
P=[]
def plate(key,title,settings,parts):P.append((key,'R5_'+key+'_'+title+'.3mf',settings,parts))
mini_files=list((R/'cad/coupons/m2-d3-l3-mini-20261022').glob('*.stl'));assert len(mini_files)==1
calibration={**base,'enable_support':'0','layer_height':'0.2','sparse_infill_density':'25%'}
plate('00','M2_Insert_Calibration',calibration,[part('M2_D3_L3_Mini',(110,110),0,mini_files[0])])
plate('00H','M2_Sideways_OPTIONAL',calibration,[part('M2_D3_L3_Sideways_Optional',(110,110),0,OUT/'fit-test-stl/M2_D3_L3_Sideways_Optional.stl')])
plate('01','Fit_Seats',{**shell,'support_type':'normal(auto)','support_style':'snug','support_closing_radius':'0'},[part('FIT_Scutum_Seat',(65,90),4,OUT/'fit-test-stl/FIT_Scutum_Seat.stl'),part('FIT_Tablet_End',(115,90),4,OUT/'fit-test-stl/FIT_Tablet_End.stl'),part('FIT_Aquila_Seat',(110,140),4,OUT/'fit-test-stl/FIT_Aquila_Seat.stl')])
plate('02','Black_Clamps',black,[part('Crest_Clamp',(75,95),source=OUT/'print-stl/Crest_Clamp.stl'),part('Neck_Clamp_0',(105,95)),part('Neck_Clamp_1',(130,95)),part('Crest_Clamp_Shoe',(80,130),2),part('Neck_Clamp_Shoe_21_5',(100,130),2),part('Neck_Clamp_Shoe_57_5',(120,130),2),part('SPARE_Crest_Shoe',(80,145),2,S/'stl/Crest_Clamp_Shoe.stl'),part('SPARE_Neck_Shoe_A',(100,145),2,S/'stl/Neck_Clamp_Shoe_21_5.stl'),part('SPARE_Neck_Shoe_B',(120,145),2,S/'stl/Neck_Clamp_Shoe_57_5.stl')])
plate('03','Red_Shields_and_Crest',fine,[part('Scutum_Field_L',(75,70)),part('Scutum_Field_R',(115,70)),part('Galea_Crest',(110,140))])
plate('04','White_Curved_Emblems',white,[part('Scutum_Emblem_L',(80,110),6),part('Scutum_Emblem_R',(130,110),6)])
plate('05','Tablets_White_then_Red',tablet,[part('Tablet_L',(110,90)),part('Tablet_R',(110,130))])
plate('06','Silk_Aquila_and_Trim',silk,[part('Aquila_Relief',(105,70)),part('Scutum_Boss_L',(75,105),3),part('Scutum_Boss_R',(95,105),3),part('Crest_Holder_Trim',(130,105),3),part('Neck_Guard',(110,145))])
plate('07','Rear_Hood',{**shell,'support_type':'normal(auto)','support_style':'snug','support_closing_radius':'0'},[part('Rear_Hood',(110,110),4)])
plate('08','Front_Panels',shell,[part('Front_Left',(65,110),4),part('Front_Right',(155,110),4)])
plate('09','Lens_Natural', {**fine,'layer_height':'0.2'},[part('Lens_Plate',(110,110))])
summary={'source_cad':str(OUT/'Gladiator_Round5_Print.FCStd'),'styling_source_cad':str(S/'Gladiator_Round5.FCStd'),'status':'Slicing and physical fit checks pending','bed_mm':[220,220,250],'rotations_about_print_X_degrees':rotations,'rotations_about_print_Y_degrees':rotationsY,'plates':{},'source_hashes':{}}
for key,fname,settings,parts in P:
 out,sizes=ns['build'](fname,key,settings,parts)
 pp=[]
 for n,p,(x,y),br,bw in parts:
  t=read(p).reshape(-1,3);lo,hi=t.min(0),t.max(0);sz=hi-lo
  b=[x-sz[0]/2-bw,y-sz[1]/2-bw,x+sz[0]/2+bw,y+sz[1]/2+bw]
  assert min(b[:2])>=15 and max(b[2:])<=205,(n,b)
  pp.append({'name':n,'source':str(p.relative_to(R)),'at_mm':[x,y],'size_mm':sz.tolist(),'brim_mm':bw})
  summary['source_hashes'][str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 summary['plates'][key]={'file':fname,'settings_overrides':settings,'parts':pp}
 print(key,fname,sizes,flush=True)
(OUT/'build_print_plates.py').write_text(Path(__file__).read_text())
(OUT/'build-summary.json').write_text(json.dumps(summary,indent=2))








