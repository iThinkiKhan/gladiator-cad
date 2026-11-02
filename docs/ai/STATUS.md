# Gladiator — Current Status

Last reviewed: 2026-11-02
Status: Active development
Authority: Project engineering files and Jim's confirmations

## Project

DFRobot Black Gladiator robotic platform with
ESP32-based control, custom CAD, masthead sensors,
camera, and printed structural components.

## Current Design

- Mast is FRONT (+Y); +X is right, +Z is up.
- Slotted masthead v2 design selected.
- Balanced head and revised tensioner designed.
- Camera service case v4 under development.
- Latest printed-part validation is incomplete.

## Recent Progress

- Masthead v2 print set staged for Jim to slice.
- Camera plug-clip test coupon staged 2026-11-01.
- Camera flash LED firmware built but not flashed
  according to the latest handoff.

## Waiting on Jim

- Print and evaluate camera plug-clip coupon.
- Test new masthead parts for physical fit.
- Confirm any changes made since the last handoff.

## Printer Safety

Printer: Ender-3 Neo with Pro hotend and
Sprite direct-drive extruder.

Jim slices delivered models using his own presets.
Do not use legacy generated G-code.

Existing safety rules and automated guards remain
authoritative until formally migrated.

## Sources

- docs/ORIENTATION.md
- docs/GLADIATOR_DESIGN.md
- docs/ai/DECISIONS.md
- docs/ai/HISTORY.md
- measurements/printer-calibration.md

## Agent Instructions

Read this file first for project status.
Consult engineering documentation for technical details.
Verify live hardware state before claiming operation.
Update this file after meaningful project changes.
