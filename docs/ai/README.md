# AI Collaboration

This directory coordinates state between Codex, Claude, Micro, and human work.

Engineering truth remains in the normal repository documentation,
measurements, CAD files, scripts, and Git history.

Files:

- SHARED.md - concise current cross-agent project state
- DECISIONS.md - accepted durable design decisions
- HANDOFF.md - current unfinished work and next actions
- agents/codex.md - Codex-owned notes
- agents/claude.md - Claude-owned notes
- agents/micro.md - Micro-owned notes

Agents may read all of these files. Each agent owns only its corresponding
file under agents/ unless explicitly asked to update shared state.
