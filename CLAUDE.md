# Claude Project Context

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

This is a shared multi-agent project.

Read AGENTS.md first and follow its repository-wide collaboration rules.

For current cross-agent context read:

- docs/ai/SHARED.md
- docs/ai/DECISIONS.md
- docs/ai/HANDOFF.md
- docs/ai/agents/codex.md
- docs/ai/agents/micro.md

Maintain Claude-specific durable notes in:

- docs/ai/agents/claude.md

Do not treat AI coordination notes as a replacement for the engineering
documents, measurements, CAD files, scripts, or Git history.
