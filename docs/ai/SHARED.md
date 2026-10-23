# Shared Project State

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
