# Round 5 calibrated release - completed 22 October 2026

Jim accepted **2.8 mm** for his M2 heat-set coupon. Insert-bore sizing gate CLEARED; all 13 new accessory bores updated, depth 4.0 mm retained. Older large structural heat-set sizes, M2 clearance and thread-forming pilots unchanged. No new measured insert OD/length, iron temperature or separate horizontal-test claim is recorded.

Current source: cad/v2/enclosure/round5-calibrated-28-20261022/ (style/, print/, independent saved-CAD check and source builders). Saved manufacturing native and 22-solid STEP include the reinforced calibrated crest clamp and the approved stronger white emblem v2. Shield bosses and illustrative screws sit 0.8 mm higher to match v2; their printed geometry and already printed red fields are unchanged. Original styling/print natives and stronger-v2 sources remain hash-unchanged.

Checks passed: 13 bores sampled clear at r1.35 and solid at r1.60; original material retained in the six changed mount-bearing solids; unchanged production parts verified; 22 valid saved STEP solids; no new inset/red-field overlap; source STL hashes stable; all slice SAFE guards and actual extrusion bounds inside 220x220; support finite segments clear of all thirteen insert bores. Full current inherited Neo SAFE/PLA/silk fields match. Released shell SD pauses replayed with exact modal/XYZ/extrusion/feed/heater restoration. No M600 or EEPROM writes. These do not newly claim physical assembly or loaded-clamp retention tested.

Printed per Jim: tablets, red shields/crest, coupon; first white insets superseded and need reprint. Remaining accessories: stronger white v2 (58m19), silk (unchanged 35m36), calibrated black clamps (31m53). Shells prepared: hood9h43m33 and panels8h31m20, each starts RED then GREY/RED/GREY. No LCD diagnostic or further coupon gate required. LED window left open; cover omitted. Fit seats are optional, newly regenerated at2.8.

Release: SD_PACKAGE/ and Gladiator_Calibrated_M2_28_20261022.zip. Incoming: ~/3D-Printer/Incoming/Gladiator/Round5_CALIBRATED_M2_28_20261022/. Windows package: X:/Projects/Gladiator/print-release-M2-28-20261022/. Five current G-code jobs copied directly to X:/3D Printer; CAD/3MF/reports in GLAD_CAD_3MF_M2_28_20261022. Existing historical Incoming packages are marked superseded. Root project ROUND5_CURRENT.md and CALIBRATED_PRINT_DELIVERY_20261022.json identify current files. No printer was started by this task.


## Five-hour window - individual front panels, 2026-10-22

Jim has red loaded and about five printing hours today. Prepared separate front-panel jobs in cad/v2/enclosure/round5-calibrated-28-20261022/single-panels-5h/. Source meshes, positions, full project settings and local support blockers preserved from the calibrated combined plate. Fresh slices: LEFT4h11m13s (61.06g), RIGHT4h15m (61.46g). Both start RED and use the same SD GREY/RED/GREY boundaries. Source-byte/settings checks, SAFE start guards, 220mm extrusion bounds, finite support/bore clearance and full pause-state replay pass.

Delivered GLAD_05L_PANEL_SD_M2_28.gcode and GLAD_05R_PANEL_SD_M2_28.gcode directly to X:/3D Printer; left recommended today with roughly49min handling margin. Combined panel file moved into GLAD_OPTIONAL to prevent duplicates. Local package X:/Projects/Gladiator/single-front-panels-5h-20261022/; Incoming Round5_SINGLE_PANELS_5h_20261022/. No printer started and neither panel marked completed.


## Combined panels restored; support-only time reduction - 2026-10-22

Jim declined separate-panel printing: keep both panels on one plate and reduce time without compromising structure; all day 2026-10-23 available for shell printing. The single-panel plan above is now optional.

Benchmarked eight support-only variants. Current release: shell-time-optimized/DELIVERY and Gladiator_Combined_Shells_Time_Optimized_20261022.zip; Incoming Round5_COMBINED_SHELLS_20261022/. Panels: normal(auto),snug,closing-radius0,base-spacing3.5mm instead of tree/default2.5. Original support speed60,interface speed40,dense interface2layers/0.5spacing,gaps,all machine/PLA/Neo SAFE settings retained. Hood is byte-identical to its previously released G-code; none of the exploratory hood changes are released.

Final panels7h00m34 (was8h31m20),hood9h43m33,total16h44m07,save1h30m46; add heating,pause waiting,handling. Actual model centerline multiset matches baseline after direction normalization; model extrusion amount differs by less than0.005mm filament. Model geometry/blocker bytes and all non-support settings match. Four walls,30% crosshatch,0.28mm,four top/bottom layers and2.8mm bores unchanged. All7shell insert paths support-clear with0.20mm bead allowance; SAFE guards,220mm bounds and emitted SD pause modal-state replays pass. Final top/side preview visually inspected. Source benchmarking artifact selected directly; a repeated slice with small infill-path variations was rejected. No new physical strength test claimed.

Installed same main names in X:/3D Printer: GLAD_05_PANELS_SD_M2_28.gcode and GLAD_04_HOOD_SD_M2_28.gcode. Split versions moved into GLAD_OPTIONAL. Panel changes: GREY~2h09,RED~4h42,GREY~5h04; both shells startRED. Local current package shell-time-optimized-20261022/; ROUND5_CURRENT.md and SHELL_TIME_OPTIMIZED_DELIVERY_20261022.json identify current artifacts. Native CAD/STEP22STLs from calibrated release remain current because geometry is unchanged. Remaining accessories total2h06. No printer started and no additional prints marked completed.


## Mount access audit and corrected hood - 2026-10-22

Jim requested antenna nut/tool access, speaker mounting and rail mount verification before printing the shell. Current CAD and hood release is now mount-checked-release/DELIVERY, Incoming Round5_MOUNT_CHECKED_20261022, Windows X:/Projects/Gladiator/mount-checked-release-20261022. Direct X:/3D Printer/GLAD_04_HOOD_SD_M2_28.gcode replaced with hash6cfe805e60420ccb2da8c9ebdba458df0741d5f0953293578d4e37a1b6c64cf6; old hood archived GLAD_OPTIONAL/BEFORE_MOUNT_CHECK_20261022. Updated native/22-solid STEP/all22STLs/3MF delivered and destination checksums verified. Combined panels remain byte-identical at7h00m34s.

Antenna passes recorded geometry checks:7mm bore,2mm land,22mm flat-zone diameter;12mm nut/flange and20mm short-tool envelopes clear shell and assembled refs. X ribs reinforce outside this clear zone. Actual hardware newly measured/physical fit not claimed.

Found two older speaker1.6mm pilots missed by original13-new-M2 update. Corrected only these pockets to accepted2.8mm diameter,4mm usable depth,0.15mm lead. Seven-mm pads/roof retained;3.2mm nominal screw reach through measured2.8mm ears means M2x6 clears pocket end. Install speaker while hood OFF:front screw driver hits breadboard in assembled state. Current M2 count15 including these2; rail structural M3 bores untouched.

All six rail hood fasteners reference saved installed left/right v4 rails:centresY22/35.5/59,Z40/46/45,slight0.644degree splay. Nominal M3 fit original straight3.6mm passages, but +0.1mm radial printer allowance touched. Added local3.6mm relief along actual rail insert axes, retaining old holes and all other material outside explicit tools. Rechecked3.2mm shaft envelope clear and full sampled screw head bearing radius2.6. Six M3x20 clear with3.48-3.89mm reach into rails;M3x25 hits blind floors. Six6mm driver envelopes clear. Four roof-seam M3 tab positions remain aligned,front panels mount to hood rather than rails.

Support blockers now include legacy rail/roof/SMA passages as well as speaker and badges; all22 finite checked cylinders show zero support hits with0.20mm bead allowance. Byte-identical machine/material/process config;4walls,30%infill,0.28mm retained. No simplified-face invalid CAD released:retained valid boolean faces instead of OCC removeSplitter failure. New solid,22 reopened STEP solids,manifold STL,bbox/source preservation,warning-free slice,SAFE/bounds and both final SD pause replays pass. Final actual-toolpath overview visually inspected. Only hood geometry and local exclusions changed; native original unchanged.

Hood9h39m04s,156.64g;panels7h00m34s,total16h39m38s. Hood starts RED thenGREY~2h56,RED~7h04,GREY~7h24. Existing two-stage SD M0 heat/purge/wipe/modal-state restoration maintained,noM600/EEPROM. Package zipSHA2bda3e4e8cc8d4be46020d9ea8700eaac00217de6c87a56fcc17a6eb344c12e2. No printer started; no physical prints newly marked complete.
