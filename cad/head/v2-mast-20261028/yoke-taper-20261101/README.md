# Tilt yoke v2 - tapered joints (2026-11-01)

Jim: the yoke looked weak where the upper plates meet the narrowed columns, and Orca gave support warnings.

- v2 narrowed both towers to columns below the servo for tilt sweep. The pivot plate (5 x 18) sat on 5 x 6 mm of
  its 10 x 6 column; the servo ear plate (3 x 20) on 3 x 6 mm of its 12.2 x 6 column. Flat 6-7 mm ledges either side.
- Added 45 deg tapers under each ledge, through the plate thickness: +327 mm3 (+0.4 g).
  Section at the old junction: pivot 30 -> 89 mm2, ear plate 18 -> 59 mm2.
- Checks (`validation.json`, `build_yoke_taper.py`, source `balance-tensioner-20261030/Gladiator_Head_v2_Balanced.FCStd`):
  staged STL = CAD yoke; sweep reproduces the known first contacts (receiver at -40, camera tray at +36);
  every degree -40..+36, the tapers add no contact with any tilt part; no overlap with fixed parts;
  receiver and screen frame pass no closer to the tapers than to the existing yoke.
- Not printed or load-tested.
