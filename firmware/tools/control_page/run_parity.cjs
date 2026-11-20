// Re-runs the existing Interface v1 browser suites against the C6 control page
// (gateway/src/ControlPage.h) instead of shared/FieldPage.h. Fixtures only; no
// hardware. Screenshots go to <out>, never over the original evidence files.
// Usage: node run_parity.cjs <out-folder> [--original]  (--original: unchanged FieldPage.h, e.g. after /dev edits)
const fs=require('fs'),path=require('path'),{spawnSync}=require('child_process');
const root=path.resolve(__dirname,'..','..'),out=path.resolve(process.argv[2]||path.join(__dirname,'out')),original=process.argv.includes('--original');
fs.mkdirSync(out,{recursive:true});
const suites=['test_interface_v1','test_link_ui','test_camera_status_ui','test_mast_positions_ui','test_spotlight_ui'];
let failed=0;
for(const name of suites){
 let src=fs.readFileSync(path.join(root,'tools',name+'.cjs'),'utf8');
 const before=src;
 src=src.split("path.resolve(__dirname,'..')").join(JSON.stringify(root));
 if(!original)src=src.split("'shared/FieldPage.h'").join("'gateway/src/ControlPage.h'");
 src=src.split("path.join(root,'diagnostics/").join('path.join('+JSON.stringify(out)+",'"+name+'-');
 if(src===before||(!original&&!src.includes('ControlPage.h'))){console.log(name+': could not retarget');failed++;continue;}
 const file=path.join(out,name+'.control.cjs');fs.writeFileSync(file,src);
 const r=spawnSync(process.execPath,[file],{encoding:'utf8',env:process.env});
 const ok=r.status===0&&!/Error|AssertionError/.test(r.stderr);
 console.log((ok?'PASS ':'FAIL ')+name+'\n  '+(r.stdout.trim()||'')+(ok?'':'\n'+r.stderr.trim().split('\n').slice(0,12).join('\n')));
 if(!ok)failed++;
}
process.exitCode=failed?1:0;console.log(failed?failed+' suite(s) failed':'All suites passed'+(original?' (original FieldPage.h)':' against ControlPage.h')+'');
