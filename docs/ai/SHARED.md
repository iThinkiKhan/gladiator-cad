# Shared Project State

## PRINTER HARD LIMITS (2026-10-31)
A 34 mm end-of-print retract (`G1 Z... E-34.0`, inherited from Orca's "MyMarlin 0.4 nozzle" end G-code)
destroyed the Ender-3 Neo's direct-drive hotend. For any G-code from any agent:
- **No retract over 2.0 mm anywhere** (start, print or end G-code, including back-to-back retracts).
  No XY move outside 0-220 mm, no bed shape larger than 220 x 220, and no Z over 250.
- Every G-code must pass `python3 ~/bin/check-ender3-start.py <file>` (guard v2, whole-file scan).
  Never weaken, bypass or edit it, or raise its limits, without Jim's explicit OK.
- **Every G-code made before 31 Oct 2026 contains the 34 mm retract: never print, copy or upload one.**
  That includes everything in this repo's SD_PACKAGE / DELIVERY / print folders. Re-slice instead.
- The `EnderNeo SAFE` preset was fixed on 31 Oct (end G-code without the long retract, 220 bed). Jim now
  slices his own G-code; deliver models unless he asks for G-code.

### Agent files are MODEL ONLY (2026-11-01, Jim, a solid rule for everyone)
- Jim opens every agent-made file as model/geometry only, never as a project, so Orca slices with his own
  saved presets. Never tell him to open a project, and never rely on settings saved inside a 3MF.
- Anything a part needs beyond his presets goes in the folder's START_HERE as a plain instruction
  (e.g. "supports ON for 01 and 03 only, tree"). Working rule only; do not enforce it with code.

### Jim's settings ONLY, every agent (2026-11-01, Jim)
- Orca silently sliced Jim's project with stock MyMarlin settings: a 34 mm end retract, a 250 bed and no guard.
  The agent-made 3MF had an empty `different_settings_to_system`, and when the GUI opens such a project it
  rebuilds every preset from the stock parent.
- Use ONLY Jim's presets:
  - printer EnderNeo SAFE;
  - process 0.20mm Standard - FIrst Layer Comp (silk: 0.20mm Silk Toys @ First Print - SAFE);
  - filament Generic PLA @System - First Print (silk: Generic PLA Silk @System - First Print).
- Every 3MF you write must pass `python3 ~/bin/orca_guard/fix_diff_lists.py --check <file.3mf>`.
  Fix it with `python3 ~/bin/orca_guard/fix_diff_lists.py <backup_dir> <file.3mf>`.
- Always-on guards, never disable or bypass them:
  - systemd user `orca-guard.timer`, every 15 s. It blocks unsafe G-code (renamed to .BLOCKED_UNSAFE), auto-fixes
    Incoming 3MFs and heals Orca's stock profile. Log: ~/3D-Printer/GUARD_LOG.txt.
  - PC Task Scheduler `Ender3 NAS G-code Guard`, which guards X:\3D Printer.
- Full record: `~/Desktop/3D-Printer-Library/PRINTER_BASELINE.txt`.

This file contains concise project state useful across AI assistants.

## Sources of truth

Use the repository's engineering documentation and measurements for detailed
technical facts, including:

- ../GLADIATOR_DESIGN.md
- ../components.md
- ../deck-v2.md
- ../upper-structure.md
- ../print-plan.md
- ../../measurements/chassis.md
- ../../measurements/components.md
- ../../measurements/mast-head.md
- ../../measurements/printer-calibration.md

Do not copy large sections of those files here. This is a map and current-state
summary, not a second documentation tree.

## Current shared state

2026-10-09 — **Mast is FRONT**, per Jim. Current frame +Y forward, +X right,
+Z up; origin rear-left. Low X LEFT, high X RIGHT. No geometry or wiring move.
See ../ORIENTATION.md before interpreting older front/rear or left/right notes.
Firmware swaps logical tracks and reverses both polarities; native CAD carries
the same frame. Head master faces +Y at legacy pan180 (a travel endpoint, not
a centered servo home). Historical aliases and print plates stay unchanged.

No cross-agent state has been formally summarized here yet.

Agents should add concise, verified current state as work proceeds.

## Current measured head prototype — 2026-10-05

cad/head/v05-sensor-mounts/README.md: reviewed v04 mechanics with corrected tilt screw
roof/passage,42x27.5 ToF and22x30 radar on removable frames. CAD/meshes/plates validated;
canonical v04 Plates1–4 plus sensor Plate5 delivered. Measurement provenance in
measurements/mast-head.md; remaining physical/harness work in HANDOFF.md.


2026-10-22 — Current Round 5 M2 heat-set bore: **2.8 mm**, accepted by Jim from his coupon. Current derivative: `cad/v2/enclosure/round5-calibrated-28-20261022/`. Stronger inset v2 reprint and silk remain; tablets/red shields/crest completed. See current HANDOFF and printer-calibration.md.

2026-10-22 — Current shell/CAD release:mount-checked-release/DELIVERY under calibrated derivative. Hood9h39m04,combined panels7h00m34;two speaker M2 pockets corrected (15 current M2 total),rail clearance follows saved splay;6xM3x20, speakerM2x6 with hood off. Antenna access and22 support-free fastener paths pass. Neo SAFE/SD colour rules retained. See HANDOFF/agent note.

2026-10-30 - Current head v2 CAD derivative: `cad/head/v2-mast-20261028/balance-tensioner-20261030/` (compact receiver balance change and M3x20 tensioner). Slotted tube retained. See current HANDOFF; not sliced/physically validated.
