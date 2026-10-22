"""Document verified CAD revisions and prepare a portable review bundle."""
import json,hashlib,shutil,zipfile
from pathlib import Path
ROOT=Path('/home/buralien/projects/gladiator-cad')
V4=ROOT/'cad/head/v04-pan-stack'
V5=ROOT/'cad/head/v05-sensor-mounts'
INTEGRATION=ROOT/'cad/head/integration-20261005'

v4=json.loads((V4/'validation.json').read_text())
assert v4['checks']['sampled_geometry_pass']
assert (V4/'artifact-verification.json').exists()
v5=json.loads((V5/'validation.json').read_text())
assert v5['checks']['sampled_geometry_pass']
config=json.loads((V5/'head-config.json').read_text())
config['sensor_mounts']=v5['sensor_mounts']
config['sensor_configuration_source']='validation.json from verified v05 build'
(V5/'head-config.json').write_text(json.dumps(config,indent=2)+'\n')
verified=json.loads((V5/'artifact-verification.json').read_text())
assert verified['native_reopened_valid'] and verified['step_valid']
v4readme='''# Gladiator head v0.4 — corrected mechanical head, 2026-10-05

The current native CAD, STEP, STL and Plates 2–4 include the reviewed tilt screw fix.
The 1.2 mm retaining roof remains intact and the final screw passage is cut after the
support arm is fused. Plate 3 is the corrected receiver version.

Jim's 16.5 mm horn-height measurement is to the raised center hub. The calibrated
post20.05, M2 pilots2.35, horn pocket0.15 and nut pockets6.0AF remain in use.
Circlip seating is confirmed. Neck_Main is on Plate4; the old horn-height hold is closed.

The master and inherited v03 source are unchanged. 117,950 sampled part/pose comparisons
pass, with zero detected collision, zero modeled ToF obstruction and a clear11.9 mm axial
cable probe. All24 assembly solids and11 print meshes pass. Native/STEP reopens pass;
every Plate1–4 triangle matches its canonical STL within export precision.

The v04 sensor carrier and square ToF reference are historical placeholders. Use
**../v05-sensor-mounts/** for the measured42 x27.5 ToF and22 x30 radar mounting system.
v05 preserves all v04 mechanical parts except its widened sensor carrier; Plate5 adds
the carrier and two removable sensor frames.

Print orientations and support requirements:

| Plate | Parts | Supports |
|---|---|---|
|1|Raised pedestal, retainer, clamp cap|Pedestal top plate only; keep belt channel clear|
|2|Rotor, drive pulley, servo carriage|None|
|3|Tilt yoke, corrected receiver, rear display frame|Display tabs only|
|4|Neck_Main|C arm, pad and riser; brim recommended|

PLA,0.2 mm layers,4 walls,30–40% infill; verify slicer preview. Plate containers are
geometry only and do not include printer profiles. Do not auto-orient.

Assemble yoke-to-pedestal bolts before fitting tilt servo and receiver. Fit the receiver
horn screw along the tilt axis from the left. Pan60 degrees gives access to the pan-drive
service screws. Bearing/spacer/screw/belt fit must still be checked in actual assembly.
The modeled9 mm inner-race spacer is reference hardware, not confirmed stock.
Complete flex harness, strain relief and mechanical stops remain unfinished.

Files: native FCStd and STEP at real robot position; stl/; plates/; validation.json,
artifact-verification.json and build-summary.txt. The original README is preserved in
cad/head/integration-20261005/before/20261005T160338Z/.
'''
# Preserve the in-place documentation before replacing stale release statements.
for relative in ('README.md','plates/START_HERE_head-v04.txt'):
    current=V4/relative
    backup=INTEGRATION/('before-document-update/'+relative)
    backup.parent.mkdir(parents=True,exist_ok=True)
    if current.exists() and not backup.exists():shutil.copy2(current,backup)
(V4/'README.md').write_text(v4readme)
(V4/'plates/START_HERE_head-v04.txt').write_text('GLADIATOR HEAD v04 — CORRECTED PLATES, 2026-10-05\n\n'+
    'Plate3 includes the corrected horn screw roof and fully open screw passage.\n'+
    'Plate4 Neck_Main uses the measured16.5 mm horn hub height; no horn-height hold.\n'+
    'Plate1 pedestal supports under top plate only; none in belt groove.\n'+
    'Plate2 no supports. Plate3 support display tabs only.\n'+
    'Plate4 brim and supports under C arm, riser and pad.\n'+
    'PLA,0.2 mm,4 walls,30–40% infill. Do not auto-orient.\n'+
    'For actual sensor mounting use v05 Plate5 and its assembly instructions.\n'+
    'Physical belt/screw/spacer/harness checks remain. No print initiated.\n')

counts=v5['checks']
total=sum(counts[k] for k in ('head_pair_pose_tests','robot_pair_pose_tests','carriage_end_pose_tests'))
readme=f'''# Gladiator mast head — measured sensor mounts, 2026-10-05

This v05 prototype adds removable mounts for the actual **42 x27.5 mm laser board** and
**22 x30 mm presence detector**. The radar's corner holes are diameter3, with2 mm edge
gaps: centers3.5 from each edge, **15 x23 mm pitch**. Radar is upright,30 mm tall.
The laser mounting holes come from the official SEN0628 dimension drawing. Four of
its six holes are used: top two and bottom two. No dimensions were scaled from photos.

![Saved CAD and board arrangement](sensor-mounts.png)

The carrier is84 mm wide and keeps the tested GH44 key and mounting interface.
Each adapter uses four M3 screws with side-loaded captive nuts and three M2 screws
from the carrier rear. ToF rear stand-off14 mm; radar22 mm. These include room for nut
feet as well as the component reservations. The measured8 mm radar rear components
have11 mm clearance to the nearest nut foot. The ToF uses a conservative9.9 mm rear
reservation from the published11.5 mm whole stack and1.6 mm PCB.
The radar is10 mm farther forward than the first candidate: its wider field otherwise
reached the S3 board and antenna at25 degrees downward tilt. The full tilt range is retained.

The corrected tilt receiver retains the1.2 mm horn screw seat and fully open passage.
All other mechanical parts match the reviewed v04 exactly; the master is unchanged.

## Files and checks

Native FreeCAD and STEP include26 valid single assembly solids at real robot position.
All13 print-oriented STL files are solid/manifold, onZ0, with valid feature probes.
**{total:,} sampled part/pose comparisons pass**, pan-20..180 and tilt-25..25 degrees
every5 degrees; both carriage ends include negative tilt. No detected rigid collision,
ToF or radar field-reservation obstruction, or axial cable-probe overlap. Field checks
use whole-board lateral bounds at assumed front planes. Lens/antenna planes remain
unmeasured; these checks do not establish radar RF performance.
The first rigid/ToF sweep covered all comparisons. After the radar adjustment,
24 unchanged solids were proven identical by exact BRep symmetric difference before
reusing their comparisons; every pair involving the two changed radar solids was
retested. The radar field was swept again over every pose. See validation_reuse in
validation.json for fresh/reused counts and baseline hashes.
Saved native/STEP files independently reopen and the expected five changed/added
objects are verified. Every Plate5 triangle matches its canonical STL within export
precision; the plate fits the220 x220 bed and has no overlapping footprints.

**Plate5: carrier + ToF frame + radar frame.** Carrier sensor face down/key up; adapters
carrier-mating face down/posts up. No supports; small nut-slot roofs bridge6 mm.
PLA,0.2 mm layers,4 walls,30–40% infill. Use brim if needed. Do not auto-orient.
The3MF carries geometry, not a printer profile. The corrected v04 Plates1–4 are included
in mechanical-plates-v04/; see its instruction sheet for their support requirements.
No print was started or new coupon made.

## Fasteners and assembly

Nominal sensor fasteners: **ToF4 x M3 x16; radar4 x M3 x25;8 M3 nuts**. Adapter fasteners: **6 x M2 x6**,
head diameter at most4.5 mm and height at most2.6 mm. M2 machine screws form threads
in the tested2.35 mm pilots. M3 printed passages are3.6; nut pockets6.0AF x2.6 deep.
No washer is assumed under the PCB screw heads; a washer changes required screw length.
Check actual screw lengths, head lands and connector orientation before tightening.

1. Build the v04 mechanical head; yoke-to-pedestal bolts go in before tilt servo/receiver.
2. Slide M3 nuts into the ToF frame from each post's outboard slot. Attach this frame
   to the carrier with3 M2x6 from rear **before fitting the carrier**.
3. Attach carrier to receiver with4 M3; radar frame and both PCBs must still be absent.
4. Fit the radar frame's nuts, then attach it with3 M2x6 from rear, **before display frame**.
5. Attach rear display frame with4 M2 from front. Adapter reliefs provide a passage for
   a screwdriver shaft up to4.8 mm diameter. Fit the screen as described by v04.
6. Fit sensor PCBs last: ToF4 M3x16, radar4 M3x25. Route leads, then check complete unpowered
   pan and tilt motion before energizing the servos. For carrier removal reverse this order.

CAD probes verify all8 PCB screw passages, intact seating annuli, nut insertion sweeps,
adapter pilots and all11 relevant screwdriver paths for this assembly order.

## Remaining physical checks

Radar PCB thickness1.6 mm and front reservation8 mm remain assumptions. ToF uses its
rectangular outer envelope including ears, deliberately over-reserving the cutouts.
Both boards need a component-free3.5 mm radius mounting land around each hole. Plugged
connector outlines, wire bends and precise optical/antenna positions are not measured.

The complete flex harness, strain relief and mechanical stops remain unfinished.
Actual horn screw fit, belt installation/alignment/tension,9 mm inner-race spacer stock,
display window alignment and loaded stiffness need actual assembly checks. No payload
or torque rating is claimed. Swept checks are samples, not proof between samples.

Provenance: measurements/mast-head.md; sensor_mounts in validation.json; source
scripts/build_head_v05.py. DFRobot drawing: https://wiki.dfrobot.com/sen0628/.
'''
(V5/'README.md').write_text(readme)
(V5/'plates/START_HERE_head-v05.txt').write_text('GLADIATOR HEAD v05 — SENSOR PLATE5\n\n'+
    'Carrier + orange/ToF frame + radar frame. PLA,0.2 mm,4 walls,30–40% infill.\n'+
    'Carrier face DOWN/key UP. Adapter mating face DOWN/posts UP. No supports.\n'+
    'Do not auto-orient. Check short6 mm nut-slot bridges in slicer.\n'+
    'ToF4 M3x16; radar4 M3x25;8 M3 nuts;6 M2x6 for adapter frames. No washers assumed.\n'+
    'Assembly: ToF frame -> carrier to receiver -> radar frame -> display frame -> PCBs.\n'+
    'Rear stand-offs14 mm ToF/22 mm radar. Radar holes15 x23 centres.\n'+
    'Read README.md for screw limits, assumptions and remaining physical checks.\n')
bundle=INTEGRATION/'delivery'
bundle.mkdir(exist_ok=True)
target=bundle/'Gladiator_MastHead_v05_20261005'
if target.exists():
    raise RuntimeError('Delivery already exists; preserve it and inspect before updating')
shutil.copytree(V5,target,ignore=shutil.ignore_patterns('*.FCStd1','*.FCBak','*.log'))
shutil.copytree(V4/'plates',target/'mechanical-plates-v04')
(target/'source').mkdir()
for name in ('build_head_v04.py','build_head_v04_plates.py','build_head_v05.py','build_head_v05_plate5.py'):
    shutil.copy2(ROOT/'scripts'/name,target/'source'/name)
shutil.copy2(INTEGRATION/'validate_v05_changed_parts.py',target/'source')
shutil.copy2(INTEGRATION/'v05-before-radar-shift/validation.json',target/'source'/'baseline-validation-before-radar-shift.json')
shutil.copy2(ROOT/'measurements/mast-head.md',target/'source'/'mast-head-measurements.md')
shutil.copy2(V4/'artifact-verification.json',target/'mechanical-plates-v04'/'artifact-verification.json')
shutil.copy2(V4/'README.md',target/'mechanical-plates-v04'/'README.md')
shutil.copy2(INTEGRATION/'SEN0628-manufacturer-dimensions.webp',target/'source')
manifest={str(f.relative_to(target)):hashlib.sha256(f.read_bytes()).hexdigest()
          for f in target.rglob('*') if f.is_file()}
(target/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=INTEGRATION/'Gladiator_MastHead_v05_20261005.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for f in target.rglob('*'):
        if f.is_file():z.write(f,str(f.relative_to(bundle)))
print(json.dumps({'archive':str(archive),'size_bytes':archive.stat().st_size,'sampled_tests':total},indent=2))
