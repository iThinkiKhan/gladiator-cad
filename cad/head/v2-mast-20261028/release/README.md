# Masthead v2 - RELEASE (current head)

**This folder is the current masthead.** Built by ONE script: `scripts/build_head_v2_release.py`
(consolidated 2026-11-01 at Jim's request, replacing four patch folders that each modified the last).

    python3 scripts/build_head_v2_release.py          # full build + motion sweep (cad-lab, about 10+ min)
    python3 scripts/build_head_v2_release.py --quick  # skip the motion sweep

Input: the v2 base, `scripts/build_head_v2_mast.py` -> `../Gladiator_Head_v2_Mast.FCStd` (unchanged).
Steps applied in order (each one is proven identical to the folder it replaces, see `validation.json` "steps"):

| step | change | replaces |
|---|---|---|
| 1 | tilt balance (receiver front -2.5 mm, payload 2.5 mm rearward) + M3x20 tensioner | `balance-tensioner-20261030/` |
| 2 | pan-servo lead path: slot under the neck flange, collar tunnel, groove, tube-top notch | `pcb-floor-20261030/` (its yoke PCB pocket was rejected and is NOT applied) |
| 3 | solid tube: rear slot filled, 10 x 12 window at Z 90-102 (bottom window Z 24-36 kept) | `solid-tube-20261101/` |
| 4 | yoke: 45 deg tapers under the plate ledges (joint 30 -> 89 / 18 -> 59 mm2) | `yoke-taper-20261101/` |

**Future changes: add a step 5, 6 ... to the script. Do not start a new patch folder.**

Outputs:
- `Gladiator_Head_v2_RELEASE.FCStd` / `_assembly.step`: the whole head at its world position.
- `stl/01..07_*.stl`: the 7 print parts in print orientation; `MANIFEST.json` has size, grams, bed chamfers, sha256.
- `validation.json`: step equivalence, home clashes, tensioner travel (C 38-48), tilt -38..34 x pan -20..180 sweep,
  and the two known end stops (receiver at -40, camera tray at +36).

Bed chamfers (0.5 mm on hole edges that print on the bed, Jim 2026-10-15) are applied to all 7 parts. The patch
folders had dropped them on the tube, yoke and receiver. The pulley now gets both bed circles chamfered; the v2
export's chamfer loop had skipped one (-12 mm3).

Not included: camera case (left off this print, drafts in `cad/head/camera-service-v3/v4`), side-window perfboard
(set aside, `side-window-pcb-20261030/`). Nothing here has been printed.
