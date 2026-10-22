from pathlib import Path
import json, zipfile, xml.etree.ElementTree as ET, hashlib, csv
import numpy as np
R=Path('/home/buralien/projects/gladiator-cad')
O=Path(__file__).resolve().parent
# Use existing project packager functions without executing other plate builds.
ns={}
exec(compile((R/'scripts/build_v2_savings_plates.py').read_text().split('summary = {}')[0], 'project-packager', 'exec'),ns)
ns['OUT']=O
ns['INCOMING']=O
ns['shutil'].copy2=lambda *a,**kw:None
settings={'printable_area':['0x0','220x0','220x220','0x220'], 'printable_height':'250',
          'layer_height':'0.2','initial_layer_print_height':'0.2','wall_loops':'4',
          'top_shell_layers':'4','bottom_shell_layers':'4','sparse_infill_density':'25%',
          'enable_support':'0','brim_type':'no_brim','brim_width':'0',
          'post_process':[]}
plate,_=ns['build']('M2_D3_L3_Coupon_EnderNeo_PLA.3mf','M2-D3-L3',settings,
    [('M2_D3_L3_Coupon',O/'M2_D3_L3_Coupon.stl',(110,110),'no_brim',0)])
# Drop unrelated template thumbnails, sliced toolpaths and slice metadata.
with zipfile.ZipFile(plate) as z:
    entries={it.filename:z.read(it.filename) for it in z.infolist()
             if not it.filename.lower().endswith(('.png','.gcode','.gcode.md5'))
             and it.filename not in ['Metadata/slice_info.config','Metadata/filament_sequence.json']}
with zipfile.ZipFile(plate,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in entries.items():z.writestr(name,data)
with zipfile.ZipFile(plate) as z:
    cfg=json.loads(z.read('Metadata/project_settings.config'))
    xml=ET.fromstring(z.read('3D/Objects/M2_D3_L3_Coupon.model'))
    nsxml={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    pts=np.array([[float(v.attrib[c]) for c in ('x','y','z')] for v in xml.findall('.//m:vertex',nsxml)])
    stl=ns['read_stl'](O/'M2_D3_L3_Coupon.stl').reshape(-1,3)
    stl-=np.array([(stl[:,0].min()+stl[:,0].max())/2,(stl[:,1].min()+stl[:,1].max())/2,stl[:,2].min()])
    assert np.array_equal(np.unique(np.round(stl,5),axis=0),np.unique(np.round(pts,5),axis=0))
    assert pts[:,2].min()==0 and np.all(pts.max(0)-pts.min(0)<[220,220,250])
    assert cfg['enable_support']=='0' and cfg['wall_loops']=='4'
    (O/'plate-validation.json').write_text(json.dumps(dict(mesh_matches_stl=True,bed_mm=[220,220,250],
        on_bed=True,settings_overrides=settings,printer=cfg.get('printer_settings_id'),
        filament=cfg.get('filament_settings_id'),status='Project packaged; slicing pending'),indent=2))
with (O/'results.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['orientation','CAD_bore_mm','insert_OD_mm','insert_length_mm','iron_C',
        'flush','bulge_or_split','cold_spin','cold_pullout','notes'])
    for orientation in ['vertical','horizontal']:
        for diameter in [round(2.6+i*.1,2) for i in range(8)]:w.writerow([orientation,f'{diameter:.2f}']+['']*8)
print(plate)
