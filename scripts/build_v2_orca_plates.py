"""Gladiator v2: OrcaSlicer project plates for the arch rails and upper deck v3 (EnderNeo, Generic PLA First Print, 0.20 Standard).

Re-uses the helper code of scripts/build_head_orca_plates.py (read, not modified) by slicing its source.
Inputs (already in print orientation): cad/v2/rails/v4-20261015/*.stl, cad/v2/upper-deck/v3-20261015/*.stl
Outputs: cad/v2/print-plates/
Run: freecadcmd scripts/build_v2_orca_plates.py
"""
import sys, re, json, zipfile, uuid, math, hashlib, struct
from pathlib import Path
sys.path.extend(["/usr/lib/freecad/lib", "/usr/lib/freecad/Mod", "/usr/lib/freecad-python3/lib"])
import numpy as np
import FreeCAD as A
import Part

ROOT = Path("/home/buralien/projects/gladiator-cad")
OUT = ROOT / "cad/v2/print-plates"
TPL = ROOT / "cad/head/orca-plates/template"
USER = Path.home() / ".var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer/user/default"
SYSTEM = Path.home() / ".var/app/com.orcaslicer.OrcaSlicer/config/OrcaSlicer/system"
OUT.mkdir(parents=True, exist_ok=True)
BED = 220.0
GAP = 12.0

HS = (ROOT / "scripts/build_head_orca_plates.py").read_text()
BAR = "# ---------------------------------------------------------------------------"
exec(HS[HS.index("def overhang_clusters"):HS.index(BAR + " support painting")], globals())
exec(HS[HS.index("def flatten_json"):HS.index(BAR + " layout")], globals())

BRIM = {"Upper_Deck_v4": 4}
LAYOUT_SRC = HS[HS.index(BAR + " layout"):HS.index("cfg, applied = build_settings()")]
old_brim = LAYOUT_SRC[LAYOUT_SRC.index("        if o['name'] == 'Neck_Main':"):LAYOUT_SRC.index("        for mid, (kind, label, vv, tt)")]
new_brim = ("        if o['name'] in BRIM:\n"
            "            ms += '    <metadata key=\"brim_type\" value=\"outer_only\"/>\\n    <metadata key=\"brim_width\" value=\"%d\"/>\\n' % BRIM[o['name']]\n")
LAYOUT_SRC = LAYOUT_SRC.replace(old_brim, new_brim)
assert "BRIM[o['name']]" in LAYOUT_SRC
exec(LAYOUT_SRC, globals())


def load_stl(f):
    b = Path(f).read_bytes()
    if b[:5] == b"solid" and b"facet" in b[:400]:
        v = np.array(re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", b), float).reshape(-1, 3)
    else:
        n = struct.unpack("<I", b[80:84])[0]
        a = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
        v = a["v"].reshape(-1, 3).astype(float)
    key = {}
    vv = []
    idx = []
    for q in v:
        k = tuple(np.round(q, 4))
        if k not in key:
            key[k] = len(vv)
            vv.append(q)
        idx.append(key[k])
    t = np.array(idx).reshape(-1, 3)
    t = np.array([x for x in t if len(set(x)) == 3])
    return np.array(vv), t


RAIL = ROOT / "cad/v2/rails/v4-20261015"
DECK = ROOT / "cad/v2/upper-deck/v4-20261016"
PARTS = {
    "Arch_Rail_Left_v4": load_stl(RAIL / "Gladiator_Arch_Rail_Left_v4.stl"),
    "Arch_Rail_Right_v4": load_stl(RAIL / "Gladiator_Arch_Rail_Right_v4.stl"),
    "Upper_Deck_v4": load_stl(DECK / "Gladiator_UpperDeck_v4.stl"),
    "Switch_Holder_v3": load_stl(ROOT / "cad/v2/switch-enclosure/v3-20261016/Gladiator_SwitchHolder_v3.stl"),
    "INA_Mount_v3": load_stl(ROOT / "cad/v2/ina-mount/v3-20261019/Gladiator_INA_Mount_v3.stl"),
    "Speaker_Rail_Bracket_v1": load_stl(ROOT / "cad/v2/speaker-mount/v1-20261020/Gladiator_Speaker_Rail_Bracket_v1.stl"),
    "Coupon_M2_Inserts": load_stl(ROOT / "cad/coupons/m2-insert-v1/Gladiator_Coupon_M2_Inserts.stl"),
    "Scutum_Emblem_v2_L": load_stl(ROOT / "cad/v2/enclosure/round5-print-20261022/emblem-v2/Scutum_Emblem_v2.stl"),
    "Scutum_Emblem_v2_R": load_stl(ROOT / "cad/v2/enclosure/round5-print-20261022/emblem-v2/Scutum_Emblem_v2.stl"),
}
v, t = PARTS["Upper_Deck_v4"]
PARTS["Upper_Deck_v4"] = (v - np.array([0, 0, v[:, 2].min()]), t)     # top-up: underside (Z54.5) onto the glass

PLATES = [
    dict(key="R", name="Gladiator_v2_ORCA-R_Arch_Rails_Left-Right", rows=[["Arch_Rail_Left_v4", "Arch_Rail_Right_v4"]]),
    dict(key="D", name="Gladiator_v2_ORCA-D_Upper_Deck_v4", rows=[["Upper_Deck_v4"]]),
    dict(key="SW", name="Gladiator_v2_ORCA-SW_Switch_Holder_v3", rows=[["Switch_Holder_v3"]], gap=10.0),
    dict(key="IM", name="Gladiator_v2_ORCA-IM_INA226_Mount_v3_adapter", rows=[["INA_Mount_v3"]], gap=10.0),
    dict(key="SPK", name="Gladiator_v2_ORCA-SPK_Speaker_Rail_Bracket_v1", rows=[["Speaker_Rail_Bracket_v1"]], gap=10.0),
    dict(key="CM2", name="Gladiator_COUPON-M2_Insert_Bores_upright-and-sideways", rows=[["Coupon_M2_Inserts"]], gap=10.0),
    dict(key="EMB", name="R5_04B_White_Shield_Emblems_v2_STRONGER", rows=[["Scutum_Emblem_v2_L", "Scutum_Emblem_v2_R"]], gap=12.0),
    dict(key="ALL", name="Gladiator_v2_ORCA-ALL_Rails-and-Deck_one-plate", rows=[["Arch_Rail_Left_v4", "Arch_Rail_Right_v4", "Upper_Deck_v4"]], gap=5.0, deck_brim=3),
]


def paint(name, v, t):
    """Rails: an enforcer under every overhang cluster of 10 mm2 or more (deck pegs, retention pad, hard-point pads, switch shelf). Deck: none."""
    if name.startswith("Arch_Rail"):
        cl = [c for c in overhang_clusters(v, t, minarea=10.0) if c["z0"] > 1.0]
        assert len(cl) in (6, 9), [(round(c['area']), round(c['z0'], 1)) for c in cl]
        vols, notes = [], []
        for k, c in enumerate(cl, 1):
            e = enforcer_from_cluster(v, t, c, 0.0, z_above=(c["z1"] - c["z0"]) + 0.3)
            vols.append(("support_enforcer", *shape_to_mesh(e), "Support %d (%.0f mm2, roof z %.1f)" % (k, c["area"], c["z0"])))
            notes.append("support %d: %.0f mm2 at x %.0f..%.0f y %.0f..%.0f, roof z %.1f" % (k, c["area"], c["xmin"], c["xmax"], c["ymin"], c["ymax"], c["z0"]))
        return "normal(manual)", vols, notes
    if name.startswith(("Switch_", "INA_", "Speaker_", "Coupon_", "Scutum_")):
        big = [c for c in overhang_clusters(v, t, minarea=3.0)]
        return "normal(manual)", [], ["no supports painted; overhang clusters seen (area, z0): %s" % [(round(c["area"], 1), round(c["z0"], 2)) for c in big]]
    return "normal(manual)", [], ["no supports: the bed-side hole chamfers are 45 degrees, everything else rises from the glass"]


def add_rail_gap(path, gap="1"):
    """Object-level settings: rails get a 1.0 mm support top Z gap (Jim 2026-10-15); the switch holder gets 6 walls and 100% infill (Jim 2026-10-16: wall joints separate on his printer)."""
    META = {"Arch_Rail_Left_v4": {"support_top_z_distance": gap}, "Arch_Rail_Right_v4": {"support_top_z_distance": gap},
            "Switch_Holder_v3": {"wall_loops": "6", "sparse_infill_density": "100%"}}
    src = zipfile.ZipFile(path)
    items = [(i, src.read(i.filename)) for i in src.infolist()]
    src.close()
    zo = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED)
    for it, d in items:
        if it.filename == "Metadata/model_settings.config":
            t_ = d.decode()
            for nm, kv in META.items():
                key = '<metadata key="name" value="%s"/>' % nm
                if key in t_:
                    a_ = t_.index(key)
                    e_ = t_.index("\n", a_)
                    ins = "".join('    <metadata key="%s" value="%s"/>\n' % (k, v) for k, v in kv.items())
                    t_ = t_[:e_ + 1] + ins + t_[e_ + 1:]
            d = t_.encode()
        zo.writestr(it, d)
    zo.close()


cfg, applied = build_settings()
summary = {"plates": {}, "settings_overridden_vs_template": {k: {"template": a, "now": b} for k, (a, b) in applied.items()}}
for pl in PLATES:
    GAP = pl.get("gap", 12.0)
    BRIM["Upper_Deck_v4"] = pl.get("deck_brim", 4)
    path, report, extent = write_plate(pl, cfg)
    add_rail_gap(path)
    summary["plates"][pl["key"]] = dict(file=path.name, extent_mm=[round(extent[0], 1), round(extent[1], 1)], parts=report,
                                        sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    print(pl["key"], path.name, "extent %.0f x %.0f" % extent, flush=True)
(OUT / "build-summary.json").write_text(json.dumps(summary, indent=1, default=str))
print("DONE", flush=True)
import os
os._exit(0)
