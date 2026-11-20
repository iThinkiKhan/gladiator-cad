color([0.68, 0.70, 0.72, 0.42])
    import("/tmp/power_preview_refs.stl", convexity=10);
color([0.16, 0.52, 0.82])
    import("/home/buralien/projects/gladiator-cad/cad/power-board/v1-cradle/stl/PowerBoardCradle_v1_installed.stl", convexity=10);
color([0.10, 0.42, 0.16, 0.70])
    translate([19.5, 29, 31.2]) cube([40, 60, 1.6]);
