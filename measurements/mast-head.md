# Mast-head hardware dimensions

Recorded from Jim's measurements and supplied specification table, 2026-09-16. All dimensions in mm unless stated. CAD-server copy: `measurements/mast-head.md`. Keep raw measurements distinct from design allowances and inferred geometry.

## SG90 servos — physical measurements

| Feature | Value | Interpretation/status |
| --- | ---: | --- |
| Tested servo-body gauge opening | 22.8 × 12.0 | Smallest opening fitted perfectly; recovered from original gauge source. Opening is through a 4 mm plate, not a complete body measurement. |
| Ear-tip to ear-tip overall span | 32.5 | Overall length, **not** mounting-hole spacing. |
| Mounting-hole center spacing | about 27.2 | New measurement; use as provisional hole pitch. |
| Ear thickness | 2.5 | Measured. |
| Ear-hole diameter | 2.5 | Measured; not a nominal M3 clearance hole. |
| Individual tab length | 5 | User description; do not infer body length from overall span minus two tabs without checking tab overlap. |
| Body bottom to ear underside | 17 | Ear underside is mounting seating plane. |
| Ear underside to installed horn underside | about 13.2 | Installed horn clearance datum. |
| Shaft center to short body side | 8.3 | User-reported body-end offset. Cross-width shaft offset remains unmeasured. |
| Shaft center to long horn tip | 17 | Jim clarified this is a horn radius, **not a body-side offset**. Other tips/full sweep still need checking against the approximately 36 overall horn length. |
| Long horn end-to-end | about 36 | Does not establish symmetry about shaft. |
| Shorter/wider horn portion end-to-end | about 18 | User-described horn geometry. |
| Horn extension beyond tab | at most 5 | Orientation-specific observation; not full swept radius. |

Derived vertical distance: body bottom to installed horn underside is approximately **30.2** (17 + 13.2), assuming both measurements use the same ear underside datum and horn installation. This is not total servo height.

Hardware available: SG90 servos with standard gears; predominantly M2/M3 screws, nuts and bolts. Servo count, screw lengths and horn fixing pattern remain unrecorded. Do not force an M3 screw through the measured Ø2.5 ear hole.

Only the smallest servo gauge is accepted from the previous experimental print batch. All other historical coupon dimensions/results are excluded by Jim's instruction.

## Sensors — user-supplied published dimensions

These are supplied reference values, not new physical measurements or independently checked manufacturer drawings. Verify original drawings before fixing mounting geometry. Clearance envelopes are planning allowances, not guaranteed plugged-in envelopes.

| Device | Board/body size | Mounting/geometry supplied | Height/protrusion supplied | Provisional CAD envelope |
| --- | --- | --- | --- | --- |
| DFRobot SEN0628 8×8 Matrix LiDAR | 27.5 × 27.5 | Ø3.1 holes; drawing references 22 / 15 / 5.5; R3.5 corner lobes | Maximum stack 11.5 | 29 × 29 × 13 |
| DFRobot SEN0610 C4001 | 22 × 30 | Hole coordinates not established | Component/connector height unknown | 24 × 32 XY; Z pending measurement |
| AI-Thinker ESP32-CAM | 27 × 40.5 × 4.5 ±0.2 | DIP-16, 2.54 pitch; approximately 22.86 between header-row references | Board/module body 4.5–4.58 excluding lens/headers | 28.5 × 42 × approximately 15 with OV2640; must check actual protrusions |

SEN0628 reference spacings are not yet assigned to coordinates. ESP32-CAM header references are not mounting holes. C4001 front/rear height, connector clearance and mounting points still need measurement for a tight carrier. Sensor mass and the selected installed configurations remain unknown.

## Current mast and deck — saved CAD audit

Source: saved `cad/master/Gladiator_Master.FCStd` at CAD repository HEAD `cdf813c`, audited 2026-09-16. Live GUI may contain unsaved differences. These are model dimensions, not new caliper readings.

| Feature | Value |
| --- | --- |
| Lower deck | 79 wide × 140 long × 2 thick |
| Mast center | X 39.5, Y 113; origin front-left, X right, Y rearward, Z up |
| Lower deck mast opening | Ø14 |
| Mast locating spigot | Ø13.8, bottom Z -5 |
| Documented motor clearance below spigot | 1 |
| Mast OD / bore | 20 / 12 |
| Mast bottom / top | Z 6 / 120; tube length 114 |
| Mast height above deck top | 68 |
| Lower socket ID / collar OD | 20.4 / 26; collar top Z 20 |
| Mast retention cross-hole | Ø3.4 at Z 13 |
| Upper deck slab | 79 × 140; Z 48–52; thickness 4 |
| Upper deck mast collar | Ø28 outside, Ø20.4 bore; Z 38–52; length 14 |
| Intended rear wire window | 10 wide × 12 high; Z 24–36 |
| S3/expander envelope | X 1–43, Y 15–89, Z 58–86.3 |
| Breadboard/C6/BNO envelope | X 43.5–79, Y 15–61.3, Z 52–73.5 |
| Driver support extent | Y 90–139.5; top Z 94 |
| Antenna post extent | X 65–75, Y 3–13, Z 52–78 |

The saved wire-window pocket does not actually open the tube. An unsaved trial with Reversed=True and Length=12 opens the rear wall into the bore. See `docs/mast-head/cad-audit-20260916.txt` on the CAD server. No master geometry was changed by that audit.

## Harness

Not yet designed. Preserve the 12 mm mast bore; develop conductors, accessible disconnects and flex loops alongside the neck. There are no actual bundle/connector dimensions to report yet. Reserve separate provision for future camera/data wiring rather than assuming a four-wire sensor connection covers it.

## ST7789 display — Jim's measurements, 2026-09-20

> **Superseded the same day.** `measurements/components.md`, section "Display (ST7789)", records
> the plate F gauge result. The hole pattern is **26.00 x 58.25 centres, confirmed** ("fits the
> back of the board perfectly"), and the visible area is **51.2 x 25.6**. Its position was
> measured on 2026-10-01 (see the end of this file). The raw readings below are kept as history.
> (Cross-reference added by Claude, 2026-09-30.)

Board outline **62.5 long x 29 wide**. Thickness not re-read; the 2026-09-17
record says 3.2 and that is still what the CAD uses. Mounting holes are M2 size.

Raw readings as given:

| Reading | Value |
| --- | ---: |
| Board, long | 62.5 |
| Board, wide | 29 |
| Hole inside-to-inside, widthwise | 24 |
| Hole outside-to-outside, widthwise | 29 |
| Hole inside-to-inside, lengthwise | 56.25 |
| Hole outside-to-outside, lengthwise | 61.5 ("maybe") |
| Hole edge to board edge, lengthwise | 1.3 |

### These do not reconcile — NOT resolved, NOT in the CAD

The same hole cannot have three diameters. Derived from each pair:

| From | Hole dia | Centre spacing |
| --- | ---: | ---: |
| Widthwise 24 / 29 | **2.50** | 26.50 |
| Lengthwise 56.25 / 61.5 | **2.625** | 58.875 |
| Lengthwise 56.25 with the 1.3 edge gap (outside = 62.5 - 2.6 = 59.9) | **1.825** | 58.075 |

Two separate problems:

1. **Lengthwise is self-contradictory.** Outside-to-outside 61.5 implies a 0.5 mm
   gap to the board edge, not 1.3. Either the 61.5 or the 1.3 is wrong. The two
   candidate centre spacings differ by 0.8 mm.
2. **Widthwise outside-to-outside equals the board width exactly** (29 and 29),
   which puts the hole's outer edge flush with the board edge. Possible, but
   unusual, and it decides whether a bezel opening has to dodge the screws or
   can run past them.

**Do not build the display frame from these.** See
[[feedback-gladiator-never-confirm-an-inference]] — an inferred hole pattern has
already cost one printed part on this project.

### Still needed for the frame

- Hole diameter, measured directly. Two readings.
- Outside-to-outside both directions, re-read. Two readings each. Centres are
  then outside-to-outside minus one hole diameter.
- Whether there is any board material outboard of the widthwise holes.
- **Active window rectangle** — position and size within the 62.5 x 29 outline.
  Completely unmeasured, and the bezel opening is meaningless without it. The
  current CAD opening is the whole-board rectangle, which is a placeholder.
- Header/connector side and its projection.

## SG90 stock

Jim reports **about six SG90s** in stock, 2026-09-20. Pan and tilt need two.
This closes the open "confirm how many servos are available" item.

Usable travel per unit remains **unmeasured**, and it still sets the belt ratio.

## Hardware in hand (Jim, 2026-09-20)

Measured or purchased, not assumed. This is the head workstream's file; recorded here by the
chassis side because Jim reported it while we were on the deck, and the belt spec in particular
gates the pedestal.

| Item | Value | Note |
| --- | --- | --- |
| **Servo usable sweep** | **160 degrees, measured** | An actual sweep on the real units, not a datasheet figure. The v0.1 candidate asks for +-40 pan and +-25 tilt, i.e. 80 and 50 total, so both sit well inside this with room for horn indexing. |
| **Timing belt** | **GT2, 2 mm pitch, 6 mm wide, 180 mm long, x5** | A **closed loop of fixed length** - the pedestal's centre distance is now a constraint, not a free variable. Five of them, so one can be cut/sacrificed for a fit test. |
| Ball bearings | purchased | The three bearing-seat and three spindle-post coupons on plate F can be read as soon as it comes off. |
| Circlips | purchased | |

**What the belt length forces.** A 180 mm closed loop around two pulleys of pitch radius `r1` and
`r2` fixes the centre distance: for equal pulleys, `180 = 2C + pi*d`, so `C = (180 - pi*d) / 2`.
That is a single number once the pulley is chosen, and the pedestal has to be built around it
rather than the other way round. If the geometry wants a different centre distance, the options are
a different belt length or an idler - not a small adjustment.

**Still open on the belt:** tooth count and pitch diameter of the pulleys the design intends, which
is what turns the 180 into a centre distance.

## Fit-coupon results — Jim, 2026-09-21–22

These are physical print observations. Keep printer artefacts separate from CAD
geometry decisions.

| Coupon / feature | Result | CAD or validation disposition |
| --- | --- | --- |
| GH44 locating register | Perfect fit | Retain the current register profile. |
| GH44 male-side M3 through-holes | No hole passes M3; the hole nearest the locating notch is the best of the four | Revise the male-side M3 clearance in the next GH44 iteration. |
| GH44 female-plate M3 through-holes | All pass M3 | Successful clearance reference. |
| GH44 female-side M3 nut sockets | No socket accepts an M3 nut | Unresolved: may be a print error. Do not alter modeled socket dimensions until a clean reprint or physical measurement separates printer error from CAD clearance. |
| Tongue-and-groove, latest coupon | Perfect fit; no notes | No geometry change requested. This supersedes the earlier suggestion to reduce tongue height by 0.20 mm. |
| Bearing/post coupon #2 | Both parts fit perfectly, especially the post | Preferred bearing/post result. |
| Bearing full insertion | Elephant foot prevents full insertion | Mitigate with printer settings first, then local sanding; do not change the bearing CAD fit on this result alone. |
| Outer-ring coupon #3 | Can just fit with elephant foot present, but contact is poor | Marginal and print-condition-dependent; not the preferred outer-ring fit. |

### Still required before head release

- **Belt validation:** Fit the actual GT2 belt, then verify pulley tooth count/pitch diameter,
  centre distance, tension, hub/horn attachment, and full motion without binding.
- **ST7789 installed fit coupon:** Check the actual board and screen relationship, retention,
  bezel opening, connector/cable clearance, and service removal. The board-envelope CAD alone
  is not a final display fit.
- **GH44 nut-socket diagnosis:** Reprint cleanly or measure a socket before assigning a CAD
  correction.

### Belt mesh fit — Jim, 2026-09-22

The delivered GT2 belt fits the **two-notch** arc of the 3-up belt mesh coupon. This is the middle groove profile, radius 0.65 mm at nominal 0.75 mm depth. Keep this profile for the next printed pulley candidate. This closes the tooth-profile coupon gate only; pulley ratio, fixed center distance, tension, shaft attachment, and full-motion fit remain open.

### Pulley inventory clarification — Jim, 2026-09-22

Jim has the belts, ball bearings, and circlips, **but no timing pulleys**. The v0.3 README's statement that a 40T drive pulley was bought is superseded. Both pulley tooth counts and printed/bought construction remain design choices. The physically passing two-notch groove profile may be carried into printed pulley candidates, with whole-loop fit and horn attachment checked separately.

### Pan horn selection clarification — Jim, 2026-09-22

Both single-arm and cross SG90 horns are available. The existing measured shaft-center-to-long-horn-tip distance is 17 mm; do not request it again or treat it as screw-hole spacing. The v0.3 CAD's 9 mm radius round-horn reference does not represent either available long horn. A cross horn with a printed pulley and radial mounting slots is a candidate for a fit coupon, while actual hole locations and vertical screw clearance still need physical verification.

### Cross-horn hole count — Jim, 2026-09-22

Each arm of the cross horn has **five holes**, described as slightly closer to the tip than the shaft center. This is a qualitative location, not a measured hole pitch. The 60T drive-pulley fit coupon uses radial slots from 7 to 14 mm center radius so an actual opposing hole pair can be selected physically. Do not treat the slot span or the 17 mm tip radius as measured hole coordinates.

## Jim, 2026-10-01 — screen window position, SG90 spline, horn screw

### ST7789 visible area position (measured)

| Reading | Value |
| --- | ---: |
| Left edge to visible area. This is the edge with the pin holes; **no header soldered yet** | **6.2** |
| Top edge to visible area | **1.5** |

Derived, not measured: from the 62.5 x 29 board and the 51.2 x 25.6 visible area (both in
`components.md`, Display), the right margin is **5.1** and the bottom margin **1.9**.

The header is not fitted yet, so its height depends on the header used. The frame needs a relief
along the left (pin-hole) edge, sized for a standard 2.54 header.

### SG90 output spline position (measured; one conflict open)

| Reading as given | Value |
| --- | ---: |
| Near side of the spline to the "longest edge" (far end), not counting the ears | **about 15** |
| Near side of the spline to "the other" edge (near end), not counting the ears | **4** |

**Interpretation:** these run along the body's length, toward the ends where the ears are. They
cannot be across the 12.2 width, since 15 + 4 alone exceeds it. As a check, 4 + the published
4.8 spline + ~15 = ~23.8, against a body length of 22.8-23. That is consistent with "about 15"
being nearer 14. The shaft centre then sits about **6.4** from the near end.

**This conflicts with the 2026-09-16 record "shaft center to short body side 8.3".** It is not
resolved. Settle it physically: the next servo-mount coupon carries a spline clearance hole at
6.4 and a mark at 8.3.

**Across the width, still unmeasured.** Published SG90 drawings show the shaft on the width
centreline. That is an **assumption** until a tilt-mount coupon confirms it.

### Horn screw (measured)

An M2 machine screw does **not** thread into the top of the output spline. The horn stays on
with its own screw, so the pulley must attach to the horn, not to the shaft.

### Published reference values (not measured on Jim's parts)

SG90 output spline **Ø4.8**; body about **23 x 12.2**. Sources: AliExpress SG90 dimensions
article, Handsontec SG90 datasheet. No published source found gives the cross horn's dimensions,
which is why Jim measured it (next section).

### SG90 cross horn — Jim's calipers, 2026-10-01

Photo with the rule in frame: `measurements/photos/sg90-cross-horn-with-rule_20261001.jpg`.

| Feature | Value |
| --- | ---: |
| Long arms, tip to tip | **36** |
| Short arms, tip to tip | **19** |
| Long arm width at the hub | **6.8** |
| Long arm width at the tip | **4.8** (tapers) |
| Short arm width | **3.8**, constant |
| Round hub, outside diameter | **7.1** |
| Hub boss above the arms, when fitted | **about 1** |

**Correction to my first reading:** Jim wrote "7.1 5." and I took the diameter as 7.15. The "5."
was his list number. The diameter is 7.1.

**Not given yet:** arm thickness, total height. The first H6 coupon assumes a 1.2 pocket depth, so
whether the arms stand proud of the pocket rim will give the thickness indirectly.

**From the photo only, NOT measured:**
- Each long arm has five holes in a line, close-spaced at roughly 2.5 mm. Each short arm has two.
  This corrects the 09-22 note "five holes in each arm", which holds for the long arms only.
- The arm tips are rounded.
- Hole positions along the arms were not read off the photo. The two-screws-as-pins readings are
  still needed, and only if a design screws through the plate into the horn.

### SG90 body photo — Jim, 2026-10-01 (estimates read off the picture, NOT measured)

Photo: `measurements/photos/sg90-body-side-view_20261001.jpg`. A translucent-blue "Beffkkip"
SG90, one ear broken off. Hand-held and at a slight angle, so everything below is good to about
+-1 mm at best. Scale taken from the body length (22.8 = about 450 px); that scale reproduces the
recorded 17 mm body-bottom-to-ear-underside, which is a fair cross-check.

What the photo shows:
- The ears are on the two **short ends**. The output spline stands on a round boss near **one
  end**, with a second, smaller bump (the idler gear housing) beside it toward the middle.
- **It supports reading Jim's "4" and "about 15" as distances along the body length.** The spline
  sits a few mm from the near end and about 15 from the far end.
- **Shaft position along the body:** the eyeballed centre is about 4.5-6.5 from the near end. That
  agrees with Jim's 4 + half the spline = about 6.4, and **not** with the older 8.3.
- The photo cannot show whether the shaft is centred across the 12.2 width. That stays an
  assumption.

**An unresolved conflict, worth one reading.** In the picture the spline top is about 30 above the
body bottom (an upper bound, since it is nearer the camera and magnified; the published overall
height is about 29-30). The case boss it comes out of is about 26-27. So:
- the spline top is roughly 12-14 above the ear underside, which matches the recorded "ear
  underside to installed horn underside, about 13.2" only if that was taken to the spline top, and
- a horn resting on the boss would have its underside nearer 10 above the ear underside.

This matters. It sets the height of the drive pulley's belt channel against the head pulley's. A
3 mm error would leave a 6 mm belt only half on its groove. The three readings that settle it are
in the coupon README under "Still missing".

### SG90 heights and body length — Jim's calipers, 2026-10-01 (MEASURED)

Servo standing on its flat bottom, horn off, readings from the table up.

| Reading | Value |
| --- | ---: |
| To the top of the output spline | **32** |
| To the top of the round case boss the spline comes out of | **28.5** |
| To the underside of an ear (intact ear) | **17.5** |
| Body length, end to end, ears not counted | **22.7** |

**Reading note.** Jim's reply was "3. 17. 5mm". I read it as **17.5** with a stray space. It
rechecks the earlier 17 and agrees within 0.5. The alternative reading, 17, changes nothing below
by more than 0.5.

**Derived, not measured:**
- The case boss top is **11.0** above the ear underside, and the spline top **14.5** above it. (Or
  11.5 and 15.0, if the older 17 is the truer ear height.)
- The spline stands **3.5** proud of its boss.
- A horn seated on the boss therefore has its underside about **11.0-11.5** above the ear
  underside. It cannot be seated and also be at 13.2.

**Superseded. Do not use either:**
- "Ear underside to installed horn underside, about 13.2" (09-16), and the 30.2 total derived
  from it. A horn at 13.2 would grip only about 1.3 mm of the 3.5 mm spline: that horn was not
  fully seated, or the reading was taken to a different face. The v0.3 CAD modelled the servo with
  a 27.5 body top and a 30.2 spline top. The real servo is 28.5 and 32, so v0.3 put the horn about
  1.2-1.7 too high.
- "Shaft centre to the short body side, 8.3" (09-16). Jim's 4 and about 15 are along the length. With the
  22.7 length they put the shaft centre at **about 5.9, +-0.6**:
  - 4 + half the spline (published Ø4.8) = 6.4 from the near end;
  - 22.7 - 15 - 2.4 = 5.3 from the far side. The "about 15" is the looser reading.
  - Neither comes near 8.3. The published spline diameter is not a measurement on Jim's parts.
  - To nail it later: one caliper reading of the spline's diameter, then centre = 4 + D/2.

**What this does to the head.** The belt channels of the two pulleys must line up to within about
0.5 mm (6 mm belt, 7 mm channel). v0.4 takes the drive pulley height from the real numbers, not
from 30.2. Belt alignment is still unverified until a physical fit, so the first build should
leave room to shim it.

The photo-based estimates in the previous section are kept as history. The measured numbers
replace them. The photo estimates read the spline top low and the boss top low by about 1.5-2.

## Round-2 coupon results — Jim, 2026-10-01 (first nine pieces, as printed)

All five of the first coupons have now been reported: H5 and H3 here, H1, H2 and H4 in the next section.

| Coupon | Result | Disposition |
| --- | --- | --- |
| **H5** M3 nut pockets | **The middle pocket (2 notches, 6.0 across flats) takes an M3 nut "perfectly".** | Use **6.0 AF modelled** for M3 captive nuts in v0.4 and the GH44 receiver. The 5.7 pockets on the earlier receiver were too small (flat walls print over, so openings shrink). The other two sizes were not reported. |
| **H3** circlip post (20.20 modelled) | **Too tight.** The bearing would not pass fully down the post, and could not be pulled back off with two pairs of pliers after forcing it. | See below. The circlip was not tested, since the bearing never seated. |

**H3 needs explaining.** The same 20.20 modelled diameter was the plate F post #2 on 09-22, which
Jim reported as fitting "perfectly, especially the post". So the post size is not repeatable from
one print to the next, or something else differs. Candidates, none of them confirmed:
- the printer's round-feature error has changed since plate F (a settings change, a different
  spool or temperature), so the post now prints nearer 20.20 than the 19.95 the calibration
  predicted;
- the H3 post is 9 mm of full-diameter length against plate F's 6, so a small taper or a seam
  ridge matters more;
- a different bearing (bore tolerance), or a bore that is slightly tight.

**Needed from Jim to tell them apart:** the H3 post's outside diameter by calipers (two readings,
near the top and near the shoulder), and whether the slicer or printer settings changed since
plate F. **Do not infer the cause until then.**

**Consequence for v0.4.** A spindle that fits one print and wedges the next is not acceptable for
a bearing that must be serviceable. v0.4 will not use a 20.20 post. The next post coupon will
bracket lower sizes (centred once the post's measured diameter is known) and will be tested
without force: if the bearing does not slide on by hand, stop.

**Process note.** Jim said he did not know what the other post and the collars were for. The
README never reached the printer, and the files carry only terse names. A plain one-page sheet,
`START_HERE_head-coupons.txt`, now sits beside them.

### Round-2 results, continued — Jim, 2026-10-01 (H1, H2, H4)

| Coupon | What Jim reported | Disposition |
| --- | --- | --- |
| **H1** belt | "The centre of these pulley shanks are **38.4 mm apart**." One reading. He did not say whether the belt was taut or whether it ran clean, or whether 38.4 was (I+O)/2 or a single caliper reading. | **Unresolved. Do not set the v0.4 spacing from it.** See below. |
| **H2** collars | "The collar with **two notches grips tighter**." He did not say whether "grips" means slide friction or hold when bolted. | **Unresolved, and the opposite of what the model predicts.** See below. |
| **H4** M2 pilots | "**Def the biggest hole for the M2**, maybe slightly bigger." The biggest is the 3-notch hole, 2.2 modelled. He did not report the SG90 ear screw. | Use **2.2 modelled** as the tested M2 pilot. "Slightly bigger" is a hint, not a measurement. Bracket 2.3 / 2.4 / 2.5 in H4b. |

**H1 against the geometry** (checked 2026-10-01). Theory for the modelled 60T and 40T pulleys on
the 180 mm belt: **39.486**. If both print 0.25 small, 39.884. The reading is 1.1 below theory and
1.5 below that prediction. For a *taut* belt:

| Pulleys, diameter vs modelled | Taut centre distance |
| ---: | ---: |
| -0.25 | 39.884 |
| 0.00 | 39.486 |
| +0.50 | 38.690 |
| +0.75 | 38.291 |

So 38.4 needs **both pulleys about 0.68 mm bigger in diameter than modelled**, or the belt is
**slack by about 2.1 mm of its length** (it would visibly sag, a few mm on each straight run), or the
belt rides high on mushy teeth. All three are untested. Modelled tip diameters: 60T 37.689, 40T 24.957.

**H2 against the geometry.** The printed solids were checked: the 1-notch collar (H2a) puts its
key face at 9.22 from the bore axis and the 2-notch (H2b) at 9.35. The mast flat is at 9.1. By
the model, then, the 1-notch key is the closer, tighter one, and the labels are right. A tighter
grip from H2b cannot come from the key. The likelier sources are the clamp bore or bolt tension,
or print differences between the two pieces. Not inferred.

**One hypothesis ties H1 and H3 together, and is NOT confirmed:** round external features may now
print larger than the 0.25-under calibration (printer-calibration.md, 2026-09-18) predicts. Both
the pulleys (oversize) and the post (too tight) point that way. Three caliper readings test it
without printing anything: the H3 post, the H1 60T tip and the H1 40T tip. If true, the master's
compensated sizes need a fresh look, which is a bigger question than this head.

**H4b** (M2 pilots 2.3 / 2.4 / 2.5) was generated 2026-10-01 and placed in the incoming folder.
Why a new bracket: the first one was off-centre, with its best hole at the top edge.

### Round-2 follow-up answers — Jim, 2026-10-01

| Topic | What Jim said | Disposition |
| --- | --- | --- |
| **H1** belt spacing | The first reading "probably wasn't super tight and there is error in the measurement." The belt was **tightest about midway up the slot.** | The slot runs 37.5 to 42.0, so midway is **about 39.75**. That is an eyeball position, not a caliper reading. It sits between the 39.49 theory and the 39.88 prediction for pulleys that print 0.25 small. **The 38.4 reading is withdrawn** as slack plus measurement error. v0.4 gets a tension slot about 2.5 mm long centred near 39.7. |
| **H2** collars | Tested by squeezing each over the mast and feeling the turning force. Re-tested: **"you're right and notch one is tighter."** "Just go with one." | The 1-notch key (0.10 from the flat) wins, matching the model. **v0.4 uses it.** The earlier "two notches grips tighter" is withdrawn. |
| **60T pulley rim** | "The 60 tooth pulley's outer rim diameter is **40.65**." | I read this as the **flange**, modelled 40.689, **not** the tooth tips (37.689). That is **-0.04**. A large round part printed almost to size, not 0.25 small. The loss may depend on radius, so a small post may lose more, but one reading does not show that. |
| **H4** M2 | The biggest hole, "maybe slightly bigger". | H4b brackets 2.3 / 2.4 / 2.5. |

**What the 40.65 does to the calibration.** `measurements/printer-calibration.md` says round
external features print about 0.25 small. The flange says 0.04 for a 40 mm circle, whereas that
calibration came from 9 and 14 mm features. If the error shrinks as the radius grows, the 20.20 post
(radius 10) may lose only about 0.1 and so print near 20.10, which would jam a 20.00 bore. That fits H3
but is **not proven**. H3b brackets 19.95 / 20.05 / 20.15 so the answer comes from the fit, not from
an argument. Nothing in the master has been changed.

## Final coupon plate results — Jim, 2026-10-01

| Coupon | Jim's words | Value used in head v0.4 |
| --- | --- | --- |
| **H3b** bearing posts 19.95 / 20.05 / 20.15 | "two notch post wins" | spindle post **20.05** modelled |
| **H6** horn pockets, snug 0.15 / easy 0.30 | "one notch horn pocket" | pocket clearance **0.15** per side |
| **H4b** M2 pilots 2.3 / 2.4 / 2.5 | "right in the middle between 1 and 2" | M2 pilot **2.35** modelled |

**Read as:** the 2-notch H3b post is 20.05. The 1-notch H6 pocket is H6a, the snug one. For the M2
sizer, the middle of 1 notch (2.3) and 2 notches (2.4) is 2.35. Stated back to Jim.

**On the post:** 20.20 jammed and 20.05 fits, both modelled values. The real post diameter was never
calipered, so this sets no new calibration rule. It is one fit, for this size of post.

**Not reported, and still open:**
- whether the circlip seated in the groove on the winning post
- how far the horn arms stand above the H6 rim, which would give the arm thickness
- whether the horn screw's head sits on H6's 3.4 centre hole

**The one measurement the head still needs:** with the horn pushed fully onto the spline, measure
from the **underside of an ear** to the **top of the horn arms**. The model assumes 11.0 (boss) + 0.25
(gap) + 2.0 (arm) = **13.25**. It sets the height of the pan servo pad, and so the belt alignment.
(The old "13.2, ear underside to installed horn underside" may in fact have been this reading, but
that is not assumed.)

## Round-3 coupon results — Jim, 2026-10-03

| Coupon | Jim's words | Read as |
| --- | --- | --- |
| **R3a** screen slice | "Screen is a good fit" | the ST7789 fits the frame's pocket; the 62.5 x 29 board size and 0.3 pocket clearance are good |
| **R3b** sideways nut block | "the sideways nut block fits 1" | the **1-notch pocket (6.0 AF) takes an M3 nut printed on its side**; the 2-notch (6.2) is not needed |

**Read as:** "fits 1" means the 1-notch pocket, which is 6.0. If "1" meant something else, correct this.
Head v0.4 already models NUT_AF = 6.0 for every nut pocket, including the sideways ones (neck collar,
tilt pivot, GH44 receiver), so nothing in the generator changes.

**Not reported, still open:** whether the visible area sat squarely in the window and whether the four
M2 screws took in the corner pilots (the hole-to-edge offset is still assumed symmetric); R3c (GH44
register, recess down); the circlip on the 2-notch post; the horn screw head on H6a; the horn height
reading (model 13.25) that still holds Neck_Main.

### Round-3 follow-up — Jim, 2026-10-03

| Check | Jim's words | Read as |
| --- | --- | --- |
| **Circlip** on the 2-notch H3b post | "circlip fits well" | the groove on the 20.05 post seats a circlip; closed |
| **R3c** GH44 register, recess printed DOWN | "The GH44 fits, but isnt quite deep enough." Then: "its a lot, prolly 1mm. A lot shallower than the first pocket i printed. It goes in one way only." | the profile fits and keys one way only, but the printed recess is about **1 mm shallower than modelled** (eyeball, not calipered) |

**Model vs print:** the recess is modelled 1.6 deep into a 3.0 block (1.7 cut from y -52.1, face at -52), with
the plate F blank carrier's key 1.4 tall, so the design slack is about 0.2. The earlier fit coupon printed
the recess facing UP and was "perfect". R3c prints it facing DOWN, so its 1.4 roof is a bridge over a
26.4 x 22.4 pocket.
**Cause is NOT established.** Roof sag over the bridge is the leading suspect, which would also hit the real
`GH44_Tilt_Receiver` (same recess, same orientation). Not yet known: the measured recess depth.
**Consequence:** do not print the receiver in Plate 3 as released until this is settled.
