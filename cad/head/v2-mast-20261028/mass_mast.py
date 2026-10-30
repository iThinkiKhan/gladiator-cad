"""Mass and centre of mass of the whole mast assembly (tube, neck, pan stack, head) for v1 and v2,
from the render meshes (world coordinates). Printed parts: PLA 1.24 g/cc x 0.85. Bought parts: point
masses at their mesh centroid. ESTIMATES, not weighed."""
import json, struct, sys
from pathlib import Path
import numpy as np

RD = Path(sys.argv[1])
idx = json.loads((RD / 'index.json').read_text())
BOUGHT = {'SG90_Pan_Reference': 9.0, 'SG90_Tilt_Reference': 9.0, 'Pan_Bearing_Lower': 10.0, 'Pan_Bearing_Upper': 10.0,
          'Pan_Inner_Spacer': 1.0, 'Pan_Circlip_Envelope': 0.5, 'Pan_Belt_Reference': 2.0, 'Pan_Horn_Reference': 1.0,
          'Tilt_Horn_Reference': 1.0, 'Tilt_Pivot_Bolt': 1.0, 'ST7789_Board': 7.0, 'ESP32_CAM_Reference': 10.0,
          'Dual_ToF_Envelope': 5.0}
LUMPS = {'GH44_Dual_Carrier': 8.0, 'Camera_Tray': 4.0, 'Neck_Main': 4.0}   # screws/nuts/wires/wingnut
RHO = 1.24e-3 * 0.85


def read_stl(p):
    b = p.read_bytes()
    if b[:5] == b'solid' and b'facet' in b[:300]:
        v = [list(map(float, l.split()[1:4])) for l in b.decode().splitlines() if l.strip().startswith('vertex')]
        return np.array(v).reshape(-1, 3, 3)
    n = struct.unpack('<I', b[80:84])[0]
    a = np.frombuffer(b[84:84 + n * 50], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]))
    return a['v'].reshape(-1, 3, 3).astype(float)


def vol_com(t):
    v6 = np.einsum('ij,ij->i', t[:, 0], np.cross(t[:, 1], t[:, 2]))
    V = v6.sum() / 6.0
    c = (v6[:, None] * (t[:, 0] + t[:, 1] + t[:, 2])).sum(0) / (4.0 * v6.sum())
    return abs(V), c


out = {}
for tag in ('v1', 'v2'):
    M, MC, rows = 0.0, np.zeros(3), []
    for e in idx[tag]:
        n = e['name']
        V, c = vol_com(read_stl(RD / e['file']))
        if n in BOUGHT:
            g = BOUGHT[n]
        elif e["kind"] == "context" or (e["kind"] == "hardware" and n not in BOUGHT):
            continue
        else:
            g = RHO * V
        g += LUMPS.get(n, 0.0)
        M += g; MC += g * c
        rows.append((n, round(g, 1), [round(x, 1) for x in c]))
    com = MC / M
    out[tag] = {'mass_g': round(M, 1), 'com_world': [round(x, 1) for x in com],
                'com_ahead_of_mast_mm': round(113.0 - com[1], 1),   # construction pose: head faces -Y
                'parts': rows}
    print(tag, 'mass %.0f g, CoM world Z %.1f, %.1f mm ahead of the mast axis (head facing forward)'
          % (M, com[2], 113.0 - com[1]))
(RD.parent / 'mast_mass_estimate.json').write_text(json.dumps(out, indent=1))
