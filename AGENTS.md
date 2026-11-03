# Gladiator CAD Agent Instructions

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
- Full record: `~/Desktop/3D-Printer-Library/PRINTER_BASELINE.txt`.

This repository is shared by human work and multiple AI assistants.

## Read first

Before substantial work, read:

- docs/ai/SHARED.md
- docs/ai/DECISIONS.md
- docs/ai/HANDOFF.md

Then read the engineering documents relevant to the task, especially:

- docs/ORIENTATION.md — current robot frame: mast is FRONT (+Y); +X right,
  +Z up, rear-left origin. Read before any directional CAD/wiring/firmware change.
- docs/GLADIATOR_DESIGN.md
- docs/components.md
- docs/deck-v2.md
- docs/upper-structure.md
- docs/print-plan.md
- measurements/chassis.md
- measurements/components.md
- measurements/mast-head.md
- measurements/printer-calibration.md

The engineering documents and measurements are the technical sources of truth.
The files under docs/ai coordinate work between agents; they do not replace
measurements, CAD, scripts, or design documentation.

## Shared-agent rules

- Read notes written by the other agents when relevant.
- Do not overwrite another agent's agent-specific note file.
- Record durable observations in your own file under docs/ai/agents/.
- Update docs/ai/HANDOFF.md when leaving meaningful unfinished work.
- Add to docs/ai/DECISIONS.md only for actual project decisions, not speculation.
- Keep docs/ai/SHARED.md concise and current.
- Preserve provenance for measurements and configuration values.
- Historical values must not silently become current values.

## Git safety

This repository may contain local commits not yet pushed to origin.

- Do not force-push.
- Do not rewrite or amend existing commits unless explicitly requested.
- Inspect git status before changing files.
- Do not discard human or other-agent work.
