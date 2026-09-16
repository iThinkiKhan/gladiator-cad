# Gladiator — consolidated design document

Single entry point for the whole vehicle: aluminum chassis, upper structure, mast, and the
modular sensor head. Replaces the previously separate `docs/upper-structure.md` design log
(retired, pointer left in its place) and summarizes the mast-head workstream's own documents,
which remain the source of truth for that subsystem's full detail and reasoning.

Master CAD file: `cad/master/Gladiator_Master.FCStd` on the CAD server
(`buralien@192.168.0.21`), fully parametric via its `Parameters` spreadsheet. STEP export at
`cad/master/Gladiator_Master.step`. Repo mirrored at github.com/iThinkiKhan/gladiator-cad.

**Two active workstreams share this repo and this master file:**
- **Chassis/upper-structure/mast** (this document's main subject) — edits
  `Gladiator_Master.FCStd` directly.
- **Mast head** (modular sensor head, pan/tilt neck, sensor carriers) — works in its own file
  tree under `cad/head/`, does not touch the master. See the Mast Head section below.

## Coordinate conventions

X right, Y rearward, Z upward. Origin at the front-left corner of the lower aluminum deck.
A forward-facing sensor or the vehicle's front looks toward **negative Y**.

## Status at a glance

| Subsystem | State |
| --- | --- |
| Lower aluminum deck | Existing fabricated part, reverse-modeled in CAD. **Never add features to it** — see below. |
| Battery holder | Reference envelope only (open 4S 18650 holder, not a sealed box) |
| Side rails (x2) | Built — faceted arch, raceway, retention tabs, M3 inserts |
| Upper deck | Built — tapered width (85 front / 79 rear), rail fixings, mast collar |
| Mast base + tube | Built — see Mast section for the wire-window bug fix |
| S3 + breadboard | Laid out on the upper deck, reference envelopes modeled |
| Driver mounts (x2) | Built — open frame, PCB-flush mounting, gusseted joint |
| Driver board reference envelope | Built (2026-09-17) — closes a real gap, see Known Issues |
| Power board shield | Built, but its *position* is still an open wiring question |
| Antenna pylon | Built — real through-panel SMA bulkhead mount |
| Mast head (sensor carrier, pan/tilt) | Separate workstream, v0.1 review candidate exists in `cad/head/v01/`, not yet installed on the master |

## The aluminum lower deck is fixed hardware

`ChassisDeck` in the CAD file is a faithful reverse-model of an **already-fabricated** aluminum
plate — every slit, hole, and the tower opening were measured off the real part. **Do not add
features to it.** Any new mounting or adjustment need goes into a printed part instead (e.g. the
side rails' foot slots absorb a 3mm front/rear offset between two existing deck slots, rather than
asking for a new slot in the aluminum). Full measurement detail: `measurements/chassis.md`.

Key figures: deck 79 x 140 x 2mm. Battery holder (open 4-cell 18650, not sealed) occupies the full
width at Y 21-96.5, Z 2-21.5, leaving a 21mm-deep front zone and a 43.5mm-deep rear zone. Tower/mast
opening: Ø14 at (39.5, 113). Tracks sit about 5mm above the deck and extend about 50mm outboard of
each deck edge (overall vehicle width 179mm).

## Side rails

Two arched structural members, `SideRailLeft`/`SideRailRight`, spanning front-to-back and carrying
the upper deck above the battery. Mount through the aluminum deck's **outermost slits at both
ends** (not the pilot holes), via crosswise adjustment slots in the printed feet — never in the
aluminum.

- **Arch, not a portal**: front foot Y 2-13, faceted haunch rising to a flat soffit at Z 30
  (8.5mm clear of the battery top), a matching haunch back down to a rear foot Y 121-135. Both
  haunches climb in the same 7mm of run, so the rear is a real post, not a shallow diagonal doing
  double duty as the roof.
- **Solid member with a raceway cut into it**, not a hollow shell: 12mm wide, with a 7x8.5mm
  wire channel (rounded R2 inboard corners) sealed at both rail ends so debris thrown up by the
  tracks can't scoop into the wire run. Six retention tabs alternate top/bottom inside the
  channel. Two foot wells (front smaller, rear roomier) sit clear for future small components
  (fuse, buck converter) — nothing committed yet.
- **Rail top is Z 48** (raised twice this session: once for battery/cell clearance, once because
  the real heat-set inserts are 7.05mm long and need a 9mm-thick top slab, not the original 7mm).
  Three M3 insert bores per rail at Y 16/68/120.

Full build history and every dimension: git log on `docs/upper-structure.md` (retired, but its
history remains in git) plus the script files in `scripts/`.

## Upper deck

`UpperDeck`, 4mm PETG plate sitting on the rail tops (Z 48-52). **Tapered width**: 85mm through
the board zone (Y 0-89), stepping back to 79mm — flush with the aluminum below — exactly where
the driver mounts start (Y 89). The taper exists purely to fix a tight board layout up front
without touching driver clearance at the rear; see Known Issues for a correction to the original
reasoning.

**Board layout** (adhesive-mounted except the S3, which is screwed to 4 bosses with M3 inserts):

| Item | X range | Y range |
| --- | --- | --- |
| S3 + expander | -0.5 .. 41.5 | 15 .. 89 |
| Breadboard + C6 + BNO | 44.0 .. 79.5 | 15 .. 61.3 |

2.5mm margin on every boundary (left edge, gap between boards, right edge).

**Mast bearing collar**: Ø20.4 bore, Ø28 collar hanging to Z 38, giving a 14mm-long upper bearing
(vs. the bare 4mm deck thickness) — paired with the lower socket in `MastBase`, bearing centres
32mm apart.

## Mast

`MastBase` (the aluminum-anchored socket) and `MastTube` (the removable Ø20/Ø12 tube).

- **Role**: fixed, non-rotating backbone. It is an interface, not a housing for one sensor — the
  head above it swaps. Any pan/tilt motion lives in the head, not the mast.
- **Anchored at the aluminum deck's existing Ø14 hole** (the primary structural bearing, resisting
  moment as a couple against the upper deck's bearing 32mm above). Two M2 screws into the two
  *usable* rear pilot holes at (19,111)/(60,111) supply the anti-rotation a round spigot alone
  cannot — the other two rear pilots are buried under the rail feet and are not usable.
- Ø13.8 spigot drops to Z -5, leaving only 1mm to the motor below the deck — deliberately shallow,
  since the bearing pair 32mm apart means the lower anchor only carries shear, not the head's full
  bending moment.
- **Bug found and fixed (2026-09-17)**: the wire-exit window (`MastWindowCut`) had
  `Reversed=False`/`Length=20`, cutting *away* from the tube — its volume was bit-for-bit identical
  to the uncut tube, meaning the rear wall had been solid the entire time despite looking finished.
  Found by the mast-head workstream's audit (`docs/mast-head/cad-audit-20260916.txt`), which
  isolated the fix without touching the saved master; applied here as `Reversed=True`,
  `Length=12` — volume dropped by exactly 523.4 mm3, matching their trial. Verified open at the
  rear wall, still solid at the front.
- Mast top is Z 120, a **placeholder** — see Mast Head section; the head workstream's sightline
  analysis suggests it may need to go taller.

## Driver mounts (motor driver + heatsink)

One BTS7960 driver per side, canted 60 deg with the heatsink facing outward/upward into clean air
and the component/terminal side facing inboard toward the vehicle interior, mounted rear of the
S3 (Y 90-139.5).

- **Open frame, not a backing plate**: after an early solid-plate version blocked airflow around
  the heatsink, the mount was rebuilt so the PCB bolts flat to a frame lying in its own plane —
  the heatsink passes clean through the frame's open middle into open air, using the true
  square 39.5x39.5mm hole pattern and the 8.75mm of bare board the 32mm heatsink leaves at each
  end.
- **Joint reinforced twice**: first by matching the root members' thickness to the frame (they'd
  been left at half the section while the frame was thickened, silently moving the weak point
  inboard); then by enlarging the transition into a real gusset that engulfs the frame's inboard
  edge with margin, rather than meeting it at a thin corner-to-corner touch.
- Deck-fixing holes were initially missing entirely (the foot rested on its two bosses with
  nothing to bolt through) — added, and verified to land exactly on the boss/insert centres.
- Fin envelope reaches to about X -47 to -58 depending on height, staying inside the ~50mm track
  line with a few mm of margin; independently verified via `DriverBoardLeft`/`DriverBoardRight`
  (below) rather than by hand.

## Power board shield

`PowerShield` exists as a built part (floor + end lip, open along the long sides where the rails
are, legs sharing the mast base's existing M2 screws), but its concept was corrected mid-session:
it's a **clip-on backing shield covering the board's solder side**, not a screw-down tray. Its
final position is explicitly an open wiring question, tentatively rear, not yet resolved.

## Antenna pylon

`AntennaPost`: tapered post, Y 1-13 (front-right of the deck, near the C6). Rebuilt once after a
real bug was caught — the first version's "SMA hole" was a blind 10mm pocket with no path through
for a connector or a shoulder for its nut to clamp against. Now a proper through-panel bulkhead
mount: hollow cavity (Z 62-78) behind a solid top panel (Z 78-80) that the Ø6.5 SMA hole actually
passes through, plus an Ø8 cable exit through the rear wall into the cavity.

## Known issues, fixed and open

**Fixed this session:**
- Mast wire window cut the wrong way (see Mast section).
- Antenna mount was a blind hole with no clamping mechanism (see Antenna section).
- Driver mount joint was under-sized relative to the member it fed into (see Driver Mounts).
- Deck fixing holes were missing from the driver mount foot entirely.
- A spreadsheet row mix-up (`bb_x0` vs `bb_y0`, rows 80/81) briefly moved the breadboard's Y
  position by mistake instead of its X position — caught immediately by the same clash-check habit
  that caught everything else here, fixed before it reached a commit others would build on.

**Corrected finding, not a fix but worth knowing:** an earlier hand-trigonometry check claimed
widening the upper deck would interfere with the driver board's component envelope (margin -2.7mm
at 85mm width), and that dropping the driver height for mast FOV had only ~2.5mm of room before
hitting the deck edge. Building the actual `DriverBoardLeft` reference solid and querying it
directly (rather than trusting the hand calculation, which had inconsistently used 49.5mm instead
of 51mm for the board's canted dimension across different scripts) shows **no such conflict
exists** — real clearance to even an 85mm-wide deck is 12-14mm, and there's 32mm of vertical
clearance above the tracks. The tapered deck is still a valid, working fix for the board-layout
tightness that motivated it, but the driver-drop question for mast FOV is more open than
previously stated — worth revisiting if head FOV still matters, this time gated by the frame's
structural rebuild effort rather than a clearance ceiling.

**Standing caution:** the mast's rear-pilot-hole audit found only 2 of 4 rear M2 pilots are
actually usable (the other 2 are buried under the rail feet) — corrected a note that had claimed
all 4 were free for board mounts.

## Open items

1. **Power board shield position** — explicitly deferred, needs the wiring plan.
2. **Mast top height (Z 120)** — placeholder; the mast-head sightline analysis suggests a ToF
   sensor may need more height to clear the S3 board's front/top corner in its lower FOV cone.
   Coordinate with the mast-head workstream before changing.
3. **Driver height / mast FOV** — see the corrected finding above; real room exists if this
   becomes a priority again.
4. **Antenna whip/pigtail exact envelope** — not yet measured against the pylon's cable exit.
5. **INA226 placement** — deliberately not designed yet, per earlier instruction.
6. Anything the mast-head workstream's own "Exact measurements needed" and "Next design gate"
   sections still list (servo/sensor dimensions, harness design, interface freeze) — see below.

## Mast head (modular sensor head) — separate workstream

Full detail, reasoning, and the evidence trail live in the mast-head workstream's own files,
which this document does not duplicate and which continue to evolve independently:

- `docs/MAST_HEAD_DIRECTION.md` — design direction, architecture rationale, hardware findings
- `docs/mast-head/cad-audit-20260916.txt` — raw audit of the saved master (the source that found
  the mast window bug)
- `measurements/mast-head.md` — hardware measurement log (servos, sensors)
- `cad/head/v01/README.md` and `validation.json` — the v0.1 review candidate: file inventory, the
  GH44-v0.1 carrier interface spec, validation results

**Summary, as of the v0.1 review candidate (2026-09-16), for coordination purposes only —
treat the files above as authoritative for anything more specific:**

- Architecture: fixed mast -> removable neck (pan/tilt motion unit) -> standardized GH44 carrier
  interface -> interchangeable sensor carriers (blank, SEN0628 ToF, SEN0610 radar, ESP32-CAM,
  combined dual). A fixed (non-moving) adapter reuses the same carrier interface for early sensor
  work.
- GH44-v0.1 interface (proposed, not frozen): 44x44mm mating plate, four M3 holes on a 32x32mm
  square, a keyed 26x22mm locating register with one clipped corner (prevents 180 deg misalignment),
  18x10mm cable window through both halves.
- Motion: limited-angle pan (+-40 deg) and tilt (+-25 deg) via SG90 servos — explicitly not
  continuous rotation, to keep a simple wire path through the mast bore. Pan load goes through a
  dedicated bearing pair, not the servo output shaft alone.
- The v0.1 candidate lives entirely in `cad/head/v01/`, built from `source-master.FCStd` (a
  captured copy, hash-verified against this repo's commit `5489d23`) — **the actual
  `Gladiator_Master.FCStd` was never touched**, confirmed by `validation.json`'s
  `master_unchanged` / `master_unchanged_after_save` checks.
- Extensive caveats throughout their documents on what is measured vs. assumed vs. provisional
  (servo shaft centering, sensor hole coordinates, bearing/PETG fit, RF transparency of a radar
  cover, etc.) — this summary does not carry that nuance forward; read their documents before
  acting on any specific number.
- **Coordination note for whoever next edits the master**: adding the head's interface features
  (e.g. a mast anti-rotation key/flat, proposed over Z 105-120 in the candidate) to the real mast
  should happen as a deliberate, coordinated change once the interface is closer to frozen, not
  silently — both workstreams edit the same underlying geometry conceptually even though the files
  are currently separate.

## Sources

- `measurements/chassis.md` — aluminum deck measurements, with explicit uncertainty notes
- `measurements/components.md` — board/battery/track measurements, caliper-verified 2026-09-15/16
- `docs/upper-structure.md` — retired; full build history preserved in git log
- Mast-head workstream files listed above
- `scripts/` — every build script used to construct the master file, kept for reproducibility and
  as the actual source of truth for exact parametric relationships (the CAD file's `Parameters`
  spreadsheet is the runtime source of truth; the scripts are how it got there)
