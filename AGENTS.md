# Gladiator CAD Agent Instructions

This repository is shared by human work and multiple AI assistants.

## Read first

Before substantial work, read:

- docs/ai/SHARED.md
- docs/ai/DECISIONS.md
- docs/ai/HANDOFF.md

Then read the engineering documents relevant to the task, especially:

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
