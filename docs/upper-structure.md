# Upper structure design log

Running record of decisions for the second-floor electronics deck and its supporting rails.
Started 2026-09-15. Component dimensions live in `measurements/components.md`; chassis/deck
geometry in `measurements/chassis.md`.

## Intended architecture

- Two structural rails running front-to-back along the sides, carrying a second-floor
  electronics deck above the battery.
- Rails double as protected wire raceways where practical.
- Upper deck spans essentially the full 140 front-to-rear length.
- Upper deck is removable while the rails stay mounted to the aluminum lower deck.
- Reinforced opening / support point in the upper deck for the sensor tower mast.
- No extra rear T-support unless the geometry demands it — the two rails plus the upper deck
  should form the structural box on their own.
- Battery and wiring stay serviceable. Deck area on both levels should be useful space.

Goal is a body that supports development and organization, replacing the current pile of parts
and wiring sitting on and around the battery.

## Decisions locked

| Decision | Choice | Rationale |
| --- | --- | --- |
| Process / material | FDM printed, PETG | Heat tolerance near motor drivers and battery |
| Upper deck fastening | Heat-set brass inserts in the rails | Deck opens repeatedly; self-tapped plastic threads strip |
| Component split | Power hardware low, logic up top | Keeps heat, noise and thick cable away from the S3 and IMU |
| Deck removal | Lifts off loaded, boards attached | Deck acts as a removable tray |
| Rail-to-deck mounting | **Via the outermost slits at both ends, not the holes** | Slots give fore-aft adjustment when setting the rails |
| **Aluminum lower deck** | **Existing physical part — do not add features to it** | It is already fabricated. The CAD is a faithful reverse-model. New features would mean hand-machining a finished plate |
| Lateral adjustment | Crosswise slots in the **printed rail feet**, not the aluminum | Some play, but not much. Keeps all tolerance absorption in the cheap-to-reprint part |
| Slot fastening | Plain M3 screw, nut and washer under the deck | A screw through a slot has nothing to self-tap into |
| Upper deck width | **79**, flush with the lower deck | Narrowed 2026-09-16. The 100 was driven by bus edge lanes that no longer exist; 79 still covers the rails with 6 to spare and keeps driver mounts inside the track envelope |
| Motor drivers | One per side, **canted diagonally outward** | Fins (which hang below the board) aim down-and-out into moving air; flared "exhaust header" look; avoids a 49.5-tall vertical board punching through the upper deck |
| Power distribution board | **Unresolved** — gets a clip-on backing shield over its solder side; location is a wiring question, tentatively rear | Will not fit the rear zone flat (the mast bisects it). Hanging under the deck remains an option but is no longer assumed |
| Power rails | Fore-aft only; **placement unresolved** | At 84 long they exceed the 79 deck width, so they cannot run crosswise |

## Mast

The mast **penetrates the upper deck**, and the upper deck acts as its structural support. It
carries a **swappable sensor head**. Servo placement undecided.

**The lower deck 14 opening at (39.5, 113) is the anchor point.** The upper deck is a secondary
bearing, not the primary support.

That ordering matters structurally. The cantilever moment from the sensor head is reacted by the
aluminum lower deck, and the upper deck only has to restrain the mast laterally — a much smaller
load. So the upper deck opening needs a modest collar or bushing rather than a heavy reinforced
boss with ribs, which is what keeps the second-floor area around the mast usable rather than
sacrificed to structure. The two bearings sit roughly 38 apart vertically, which stiffens the mast
considerably against deflection compared with anchoring at one deck alone.

### Role

Vertical, removable / swappable sensor mast. It is a **standardized backbone and interface**, not
a housing for one specific sensor — the head swaps. Servo placement undecided.

### The 6 mm constraint

There is only **6 of clearance between the underside of the aluminum deck and the motor**, directly
below the mast bore. That rules out:

- a through-mast with a nut, clamp or collar underneath
- any deep socket reaching below the plate
- long fasteners protruding under the mast centreline

Usable engagement is 2 (plate thickness) + about 5 (leaving 1 of safety) = **7 total**.

### Why shallow engagement is acceptable anyway

The mast has two bearings: the aluminum deck at Z 2 and the upper deck at Z 48..52, roughly **46
apart**. A sensor head's bending moment is reacted as a *couple* between those two bearings — the
lower one carries **shear**, not moment. So socket depth is not the governing factor; a 7 socket
resists shear easily.

Stiffness is not a concern either. A 14 OD / 9 ID PETG tube has I = 1563 mm4; a 100 g head on a
100 cantilever above the upper deck deflects about 0.11. Even 300 g at 150 is only ~1.1.

**The real gap is torsion.** A round spigot in a round hole cannot resist the head being twisted.
Anti-rotation has to come from fasteners off the centreline.

### Anchoring opportunity, and a correction

Checked against the built rails (script `check_mast_zone.py`):

| Rear M2 pilot | Status |
| --- | --- |
| (19, 111) | **usable** — rail is overhead at Z 30+, screw head has clear room |
| (60, 111) | **usable** — same |
| (19, 128) | **BLOCKED** — buried under the rail's rear foot (Y 119..135) |
| (60, 128) | **BLOCKED** — same |

This corrects an earlier note claiming all four rear pilots stayed free for board mounts. Only the
Y 111 pair is actually reachable.

That pair is well placed for the mast: **41 apart, straddling the bore at Y 113**, and clear of the
rails. Two M2 screws there give both clamping and the anti-rotation the socket cannot provide. A
base plate can span X 16..63, Y 104..118 — fully clear of the rail feet, which only come down to
deck level at Y 2..13 and Y 119..135.

The inner long slits (X 23.5..27.5 and 51.5..55.5, running Y 58.75..132.5) are also unused and sit
just **5 from the bore edge**, offering a supplementary or alternative anchor — but they need nuts
underneath, and under-deck clearance at that location is still unmeasured.

### Decided

| | |
| --- | --- |
| Rotation | **Fixed mast**; any pan lives inside the swappable head |
| Mast | **20 OD / 12 bore**, stepping to a **13.8 spigot** at the base |
| Why 20 not 14 | Stiffness was never the constraint (14 deflects only 0.11 under a 100 g head at 100). A 4 wall gives real meat for head-interface features and a 12 wire path; 14 would leave 2.5 |

### Mast — BUILT

Three pieces: `MastBase`, `MastTube`, and a bearing collar added to `UpperDeck`.

**MastBase.** Plate at Z 2..6, outline X 16..63 over Y 99..115 with a tongue X 26..53 out to
Y 127 so the bore and collar stay fully supported. Fixed by **two M2 screws into the usable
aluminum pilots at (19, 111) and (60, 111)** — 41 apart, straddling the bore, which is what
supplies the anti-rotation a round spigot cannot. A 13.8 spigot drops through the aluminum to
**Z -5, leaving 1 to the motor**. Above the plate, a 26 OD collar to Z 20 bored 20.4 forms the
mast socket; the mast bottoms on the plate at Z 6. A 3.4 cross-hole at Z 13 through both collar
walls takes a retaining pin or M3, so the mast pulls straight out.

The wide section stops at Y 115 rather than 118: at Y 118 the rails' rear haunch underside is
exactly Z 6, the same as the plate top, and the corners grazed it.

**MastTube.** 20 OD / 12 bore, Z 6..120. A 10 x 12 wire window on the rear face at Z 24..36 lets
the loom out into the rear zone, below the deck collar. Matching 3.4 cross-hole at Z 13.

**UpperDeck bearing collar.** The mast bore is 20.4 through the deck, with a 28 OD collar hanging
below to Z 38 — so the bearing is **14 long** rather than just the deck's 4.

Bearing centres end up **32 apart** (socket centred Z 13, deck collar centred Z 45), which is the
couple that resists head wobble. Clearances: spigot 0.10 per side in the aluminum, mast 0.20 per
side in both socket and deck bore.

Verified: zero clash against the aluminum, both rails, the battery, or between mast parts.

**Still open:** head interface geometry, final mast height (120 is a placeholder giving 68 of
cantilever above the deck), and servo placement.

## Consequences of those choices

- The actual inserts on hand are **M3 thread, 7.05 long, 5.0 OD at the thickest knurl**. Bore is
  4.4 (convention is ~0.6 under the knurl) x 7.5 deep. They need 9 of slab to sit in, which is what
  set the rail top at Z 48 — see below. Wall around a 4.4 bore is 3.8 each side in a 12 rail.
- Two different joints, two fastener types: rails bolt **down** to aluminum with M2 screws
  self-tapping into the existing 1.6 pilots; the upper deck bolts **up** into heat-set inserts in
  the printed rails. Only the second joint is opened repeatedly.
- Because the deck lifts off loaded, the rail-to-deck wiring interface is a real design item.
  Leading approach: wires run up inside a rail and break at a connector near the top, so the deck
  disconnects at two points rather than twenty.

## Rail mounting geometry

Rails anchor through the outermost slits. Relevant existing slot geometry:

| Slot | X extent | Y extent |
| --- | --- | --- |
| Front left | 8.5 .. 12.5 | 7.5 .. 40.5 |
| Front right | 66.5 .. 70.5 | 7.5 .. 40.5 |
| Rear outer left | 11.5 .. 15.5 | 99.5 .. 132.5 |
| Rear outer right | 63.5 .. 67.5 | 99.5 .. 132.5 |

Note the **3mm lateral offset** between the front and rear outer slots (front centers X 10.5 /
68.5, rear outer centers X 13.5 / 65.5). A rail at constant X cannot sit centered in both, which
is what the added crosswise adjustment slots are meant to absorb. Size and placement of those
slots are not yet decided.

## Upper deck area problem

Recessing the power rails into the rail tops was considered and **rejected**: the upper deck sits
on top of the rails and spans the full width, so it would cover them. The buses need to be
reachable while the bot is running, so they have to live on an exposed surface.

That pushes them onto the upper deck, which is then tight. At 79 x 140 the deck must hold:

| Item | Footprint | Area |
| --- | --- | ---: |
| S3 + expander | 42 x 74 | 3108 |
| Breadboard (C6 + BNO) | 46.3 x 35.5 | 1644 |
| Power rails x2 | 84 x 9.5 each | 1596 |
| | **total** | **6348 of 11060** |

57% raw coverage sounds workable, but it does not lay out cleanly. Two buses along the side edges
leave a 60-wide central channel; the S3 (42) and breadboard (35.5) fit that channel individually
but not side by side (77.5), so they must sit fore-and-aft — 74 + 46.3 = 120.3 end to end. With
the mast at Y 113 eating the rear, only ~103 of length is clear ahead of it. Doesn't fit. Nor can
the breadboard be relegated downstairs: the rear zone is 43.5 deep (breadboard is 46.3 long, and
rotating it into the zone collides with the mast), and the front zone is only 21 deep.

Levers, roughly in order of preference:

1. **Make the upper deck wider than the lower deck.** Nothing constrains it to 79 — it sits above
   the tracks, which are free space. Going to ~95-100 wide buys 2000-3000 mm2, gives the buses
   their own edge lanes, and provides outer edges to hang the canted driver mounts from (the
   stated fallback). Also shelters the tracks.
2. Stack the breadboard above the S3 on standoffs.
3. Relocate the buses vertically onto the inner faces of the rails, reachable from above through a
   gap between the deck edge and the rail.

## Consequence of mounting through slots rather than holes

Self-tapping into the aluminum only works at the 1.6 pilot holes. A screw passing through a
**slot** has nothing to bite, so rail mounting needs a nut, T-nut or backing bar on the
**underside** of the lower deck. Under-deck clearance beneath the slots is therefore a new
requirement and is not yet measured — the track units and motors live down there.

## Side rails — BUILT

Modeled in `Gladiator_Master.FCStd` as `SideRailLeft` (PartDesign body) and `SideRailRight`
(mirrored about the deck centerline). Fully parametric off the `Parameters` spreadsheet.

**They are arches, not straight beams.** The battery holder fills the full deck width (X 0..79)
from Y 21..96.5 up to Z 21.5, so a constant-section rail sitting on the deck would pass straight
through it. The rails instead land on the exposed deck ahead of and behind the battery and span
over it.

**Faceted arch, not a portal.** The first version had legs sized by filling the footprint rather
than by load — a 37-long solid slab at the rear. Each rail carries roughly 2.5 N, which against a
12 x 8 PETG section is about 0.02 MPa versus PETG's ~50 MPa yield: over-built by three orders of
magnitude. Stiffness and printability set the minimum, not strength. The legs are now slender
haunches and the material between them is gone.

| Property | Value |
| --- | --- |
| Left rail X | 6 .. 18 (12 wide) |
| Right rail X | 61 .. 73 (mirrored) |
| Length | Y 2 .. 135 |
| Top face | Z 48, flat full length — carries the upper deck |
| Front foot | Y 2 .. 13, underside Z 2 |
| Front haunch | 4 chords, Y 13 -> 20, rising Z 2 -> 30 |
| Soffit | Y 20 .. 112, flat at Z 30 (8.5 clear over battery holder top Z 21.5) |
| Rear post | 4 chords, Y 112 -> 119, falling Z 30 -> 2 — 7 of run, matching the front |
| Rear foot | Y 119 .. 135, underside Z 2 |
| Beam depth over battery | 18 |
| Section | **Solid member with a raceway worked into it**, not a hollow shell |
| Raceway groove | Z 32..39 (7 tall) x 8.5 deep = 59.5 mm2, inboard corners rounded R2, open on the inboard face, Y 5..132 |
| Top slab | Z 39..48 (9 solid, full 12 width) — hosts the heat-set inserts |
| Bottom flange over arch | Z 30..32 |
| Outboard web | X 6..9.5 (3.5 solid) |
| Volume | 23930 mm3 each |

**Posts at both ends, not a diagonal.** v3 ran the rear haunch as a 24-long rake from Y 97 down to
Y 121, which meant the deck load was carried by that diagonal — the triangle was doing the work
rather than a post. The rear now drops in 7 of run, matching the front, and the soffit instead
runs flat all the way to Y 112. Side effect: the rear zone gains usable volume, because the old
rake cut down through exactly where the power hardware lives.

**Raceway capacity.** Wire counts are large and will keep changing as the build iterates, so the
groove is deepened to 8.5 (59.5 mm2 per rail, ~119 mm2 across both). At roughly 2.3 mm2 per
22 AWG wire including packing slop that is about 50 wires total. It cannot grow vertically — the
7 top slab is needed for the inserts and the beam is only 16 deep — so any further capacity comes
from depth, at the cost of the outboard web (now 3.5).

**Battery clearance raised, and it moved the whole deck.** 2.5 over the holder left nothing for
18650 cells sitting proud of their channels, nor for wires running over or around the pack. The
soffit could not simply rise on its own: the beam needs 16 (7 insert slab + 7 groove + 2 flange),
so with the rail top at Z 40 the soffit was already as low as it could go. Raising clearance
therefore raises the deck with it. Soffit 24 -> 30 (clearance 2.5 -> **8.5**), rail top 40 -> 46.

Knock-ons:

- The **upper deck underside is now Z 46**, so the whole vehicle is 6 taller. If that hurts the CG
  on a tracked chassis, `rail_soffit_z` and `rail_top_z` move together as a pair.
- The power distribution board hanging under the deck now occupies roughly Z 30..46, level with
  the rail beams. It has to pass **between** the rails, and the gap there is X 18..61 = 43. The
  board is 40 x 60, so it fits only with its **40 dimension across X** — 1.5 clearance each side.
- Actual cell protrusion above the 19.5 holder is still unmeasured, so 8.5 is an estimate, not a
  verified fit.

**Raised again, to Z 48, for the inserts (v8).** The real inserts are 7.05 long, needing a 7.5
bore — but the top slab was only 7, so the bore would have punched through into the raceway. The
beam budget had no slack: 2 flange + 7 raceway + 7 slab = 16. Options were a through-bore (insert
bottom open to the wire channel), thinning the flange to 1, cutting the raceway to 5 tall, or
raising the top. Raising won: **rail top 46 -> 48**, slab 39..48 = 9, blind bore with 1.5 of
material beneath it, raceway untouched at 7. Beam is now 18 deep. Cumulative height added this
session is 8 (soffit 24 -> 30, top 40 -> 48).

The upper deck followed automatically to Z 48..52 — its placement is expression-bound to
`rail_top_z`, so nothing needed rebuilding on that side.

**Why solid rather than a shell.** v2 was a 2.4 thin-walled box section — structurally fine but it
read as a wall with a hole in it, and worse, a 2.4 top wall cannot host an M3 heat-set insert
(they need ~5.7 of depth). Making the member solid and cutting only a channel into it gives both
the bridge-arch look and a 7 top slab with somewhere for the inserts to actually live.

**The arch is asymmetric by necessity.** The battery sits 21 from the front deck edge but 43.5
from the rear, and the soffit has to be at Z 24 before it reaches the battery. The front haunch
therefore climbs 22 in 7 of run and is near-vertical whatever shape is drawn; the rear has three
times the room and gets the long sweep. Forcing symmetry would only waste the rear space.

The raceway is offset perpendicular to each haunch rather than vertically, so wall thickness
stays at 2.4 around the curve instead of thinning on the shallow rear chords.

**Mounting:** slots at both ends, per decision — no reliance on the 4mm locating hole. Each leg
has a crosswise adjustment slot giving 4 total lateral play (M3 clearance, 3.4 wide):

| Foot | Foot slot | Screw nominal | Lands in deck slot |
| --- | --- | --- | --- |
| Front | X 7.3..13.7, Y 8.3..11.7 | X 10.5, Y 10 | Front slot X 8.5..12.5, Y 7.5..40.5 |
| Rear | X 10.3..16.7, Y 125.3..128.7 | X 13.5, Y 127 | Rear outer slit X 11.5..15.5, Y 99.5..132.5 |

Travel is 3 total (±1.5) at each foot — "some play, but not much". The rail X range 6..18 is
centred on the midpoint of the two screw positions so both slots keep equal edge margin.

The 3 lateral offset between the front and rear deck slots is absorbed by the feet, so the rail
itself runs dead straight. Fastening is a plain M3 screw with a nut and washer under the deck.

**Wire retention.** Six tabs sit inside the raceway at Y 25, 45, 65, 85, 105 and 125, each 4 long and
2 thick at the groove opening, alternating bottom (Z 26..30) and top (Z 29..33). They leave a 3
gap to press wire through and then hold it captive behind them; alternating sides makes the run a
shallow labyrinth so nothing works its way back out. Printed with the rail on its side the groove
opens upward, so the tabs need no support.

**Heat-set inserts.** Three M3 bores per rail (4.4 dia, 7.5 deep from the top face) at Y 16, 68 and
120, on the rail centreline X 12 — 3.9 of material either side. They sit in the 9 top slab with 1.5
to spare above the raceway ceiling. Positions dodge the driver shafts at Y 10 and 127.

**Foot wells.** At each foot the inboard face is opened out to 9.5 deep, from the floor at Z 6 up
to the raceway, so a driver can reach the mounting screw. Front well Y 5..13 (stops at the foot
end), rear Y 119..132.

**Front post fix (v7).** The front well previously ran to Y 15 while the foot ends at Y 13, so it
undercut the rising haunch: where the well floor at Z 6 crossed the soffit line the wall thinned
to nothing, leaving a knife edge that was not carrying anything. The well now stops at Y 13, the
same way the rear well starts exactly at its foot (Y 119) — which is why only the front showed the
problem. Verified as a single solid, single shell.

**Rounded raceway.** The channel is now cut as a true cross-section swept along Y rather than a
rectangle pocketed sideways, so the two inboard corners carry an R2 fillet running the full
length. Easier on wire insulation, and no sharp internal corner for the slicer to fight.

**Well tabs and future use.** Each foot well also gets a retention tab (front at Y 5..6.5 against
the sealed end wall, rear at Y 120..123 ahead of the screw slot), both 8 tall off the well floor.
The wells are 9.5 deep x 26 tall x 8 (front) / 13 (rear) long — genuinely usable volume. Candidate
later uses: small fuse holder, buck converter, or a terminal block. Nothing is committed; the
volume is simply kept clear so the option stays open. Note the front well is largely taken up by
screw access (slot Y 8.3..11.7, driver shaft Y 7..13), so the rear well is the roomier of the two.

**Ends are sealed.** Up to v4 both the raceway and the foot wells ran straight out through the
rail's front and rear end faces. That made the front end a scoop: driving forward would funnel
whatever the tracks throw up directly into the wire channel. Both now stop 3 short of each end,
so the cavities are closed on the outside and open only inward, toward the sheltered arch. Cost
is about 1500 mm3 of added material per rail; worth it to keep grit out of the loom.

**Driver access:** a 6 dia shaft through the top slab directly above each mounting screw. The
raceway is continuous, so a driver drops straight down through the hole to the screw head. The
upper deck covers these in normal use — they're only needed with the deck off, which is exactly
when rails get adjusted.

Verified: zero clash against the battery, the lower deck, or each other.

Insert positions (Y 16, 68, 120) are provisional — the upper deck's hole pattern must be drilled
to match them, or they get moved when the deck is laid out. Three per rail gives six fixings
across a 140 deck.

## Upper deck — pass 1 BUILT

Modeled as the `UpperDeck` body. Structure and fixings only; layout comes in pass 2.

| Property | Value |
| --- | --- |
| Outline | 100 wide x 140 long, corners R6 |
| X extent | -10.5 .. 89.5, centred on the chassis centreline X 39.5 |
| Y extent | 0 .. 140, matching the lower deck |
| Z | 48 .. 52 (sits directly on the rail tops) |
| Thickness | 4 |
| Rail fixings | 6 x M3 clearance (3.4) at X 12 and 67, Y 16 / 68 / 120 |

Verified: hole positions match the rail insert bores exactly, and zero clash against the rails,
battery or lower deck.

Spans and overhangs: the deck is unsupported for **43 between the rails** and overhangs the lower
deck by **10.5 each side**, out over the tracks. At 4 PETG both are comfortable; the overhangs are
where the canted driver mounts are expected to attach.

### Deck narrowed to 79 (2026-09-16)

100 was chosen when the deck had to carry two 9.5 bus lanes on its edges *and* the S3 and
breadboard side by side. The buses are gone, so that driver disappeared. The deck is now **79,
X 0..79, flush with the aluminum below**, leaving 6 of deck outboard of each rail.

Track measurement that made this safe: **tracks sit ~5 above the deck**, so their tops are around
Z 7 while the upper deck is at Z 48 — about 41 of vertical clearance. Driver mounts hanging off
the deck edge cannot foul them. Only *width* matters, and narrowing helps there too: a driver
flaring ~50 outboard from X 0 lands at the track line (X -50) instead of 10-16 proud of it.

### Layout consequence of 79

Breadboard is 46.3 x 35.5, adhesive-mounted, and goes on the **top deck** to keep leads short.

| Region of the deck top | Size | Verdict |
| --- | --- | --- |
| Beside the mast bore (X 0..29.3, X 49.7..79) | 29.3 wide | **Too narrow** — needs 35.5 |
| Aft of the bore (Y 123.2..140) | 16.8 long | Too short |
| Between S3 rear edge and the bore (Y 89..102.8) | 13.8 long | Too short |
| Forward region (Y 0..102.8) | 79 x 102.8 | **The only place it fits** |

So at 79 the breadboard must share the forward region with the S3, side by side: 42 + 35.5 = 77.5
in 79, leaving 1.5 total. Adhesive mounting makes that workable — no screw heads needing edge
margin — but it forces the S3 off centre, which in turn puts one of its standoff bosses within
about 0.25 of a rail fixing hole. Alternatives are stacking the breadboard above the S3, or
recovering a few mm of deck width.

### Mounting approach (2026-09-16)

**Only the S3 gets screwed down. Everything else is adhesive.** That removes the need for hole
patterns on the breadboard, INA226 and power board, which were the main outstanding measurements
for deck layout.

**The breadboard power rails are probably dropped.** Bus function moves into repurposed breadboard
space instead, so the two 84 x 9.5 strips no longer need edge lanes on the deck. That frees about
1600 mm2 and removes the constraint that drove the deck to 100 wide in the first place — the width
stays, but there is now real slack in the layout.

**The power board needs a cradle**, not adhesive: a closed floor so its underside cannot short
against anything, but removable so components can be added later.

### S3 mounts — BUILT

Four bosses on the deck top, 9 dia x 6 tall, at the **30.9 x 55** pattern centred on (39.5, 52),
so the board sits Y 15..89. Each takes an M3 heat-set insert (4.4 bore, 7.5 deep from the boss
top). Stack is deck 48..52 plus boss 52..58 = 10 of material, bore down to 50.5, leaving 2.5.

The 6 boss height does double duty: it gives the 7.05 insert somewhere to live (the 4 deck alone
cannot hold one, same problem the rails had) and lifts the board clear of its own pin tails.

### Power board protection — concept corrected (2026-09-16)

**It is a backing shield, not a tray.** A separate piece that covers the **back** of the board so
the solder side cannot short, clipping into another part of the body. The board is not dropped
into a deck-mounted carrier — the shield travels with the board.

Requirements as stated:

- Covers the rear/solder face of the board
- Clips to the body rather than being screwed to the deck
- **Connectors stay accessible but secure** — the board is not tall, so the constraint is edge
  access to its connectors, not height
- Position: **rear, tentatively** — but explicitly deferred, because where it lives is a wiring
  question that is not ready to be answered

**Not modeled.** Needs the wiring plan first, plus where the connectors sit on the board edges.
The 43 analysis below still applies to anything that ends up hanging in the rail channel.

### The 43 mm channel constraint

Measured from the built geometry:

| | |
| --- | --- |
| Gap between rails (X 18 .. 61) | **43.0** |
| Power board | 40 x 60 x 16 |
| Vertical room, battery top Z 21.5 to deck underside Z 48 | 26.5 |
| Wall budget each side if hung at beam level | **1.50** |

The board only fits between the rails with its 40 dimension across X, and that leaves 1.5 per side
for cradle walls — before any drop-in clearance. A conventional four-walled tray does not fit.

Two things make it workable:

1. **The floor is what stops the shorting, not the side walls.** A tray with a closed floor and end
   lips, open along the long sides where the rails are, satisfies the requirement and fits easily.
2. **Below Z 30 the channel opens up.** The rails' soffit is at Z 30, so anything under that height
   is not limited to 43. A cradle whose floor and walls sit at Z 26..30 can be wider than the
   channel, with only the board itself (40) poking up into the 43 gap above.

### Pass 2, still to add

Everything here is blocked on measurements or on layout decisions:

1. ~~Mast collar~~ — DONE, see the Mast section.
2. ~~Board mounting patterns~~ - resolved: only the S3 is screwed, rest adhesive.
   breadboard, INA226 and power distro patterns are not measured.
3. ~~Bus lanes~~ - dropped; buses move into repurposed breadboard space.
4. **Driver mounts** on the outer overhangs. Tracks reach 50 outboard of each deck edge (overall width 179), so a driver canted off the deck edge at X -10.5 would reach X -60 to -66 and become the widest point by 10-16. Anchoring nearer X 0 keeps it inside the track envelope.
5. Optional: counterbores on the six fixing holes so the screw heads sit flush. Deliberately left
   plain for now; 4 of thickness leaves room for them later.

## Open questions blocking modeling

1. **Track geometry.** Deck side edge to inner face of each track run, the track's outer extent,
   and its top height relative to the deck top (Z = 2). The canted drivers flare outboard over the
   tracks, so this decides the cant angle and how far out the boards can reach before the fins
   foul the track.
2. **Motor driver height reconciliation** — the reported 41.2 / 18.7 / 32 / 28 figures don't close
   (see `measurements/components.md`).
3. **Mast OD** and whether it penetrates the upper deck.

## Deferred

- Whether the rails taper to follow the 3mm front/rear slot offset, or run straight with offset
  feet. Decide once the crosswise adjustment slots are sized.
- Rail-to-deck wiring connector location.
- Antenna mounting point, clear of the aluminum deck and the drivers.
