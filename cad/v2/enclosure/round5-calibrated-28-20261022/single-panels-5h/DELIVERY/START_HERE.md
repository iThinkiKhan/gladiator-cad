# Individual front panels for a five-hour print window

These are the same calibrated 2.8 mm front panels, separated into individual jobs. Geometry, orientation, positions, Neo SAFE, brim, supports and PLA settings are preserved. Both start RED and pause for GREY, RED, GREY. These replace the combined front-panel job when printing separately; do not print the same panels twice.

GLAD_05L_PANEL_SD_M2_28.gcode: Front_Left, 4h 11m 13s, 61.06 g.
  Change to GREY at approximately 1h 07m, colour boundary 12.01 mm.
  Change to RED at approximately 2h 25m, colour boundary 52.05 mm.
  Change to GREY at approximately 2h 45m, colour boundary 57.93 mm.
GLAD_05R_PANEL_SD_M2_28.gcode: Front_Right, 4h 15m 00s, 61.46 g.
  Change to GREY at approximately 1h 08m, colour boundary 12.01 mm.
  Change to RED at approximately 2h 27m, colour boundary 52.05 mm.
  Change to GREY at approximately 2h 47m, colour boundary 57.93 mm.

Times exclude warm-up, waiting at colour stops and manual purging. At each change: first click acknowledges you and reheats; at the second stop change/purge/wipe, reengage idler and click. Keep head and bed still.

Verification: source mesh bytes, full project settings and support blockers preserved; SAFE starts pass; extrusion bounds within 220x220; supports clear of both insert bores; all released pause states restore XYZ, extrusion mode/coordinate, feed and heaters. No printer job started.
