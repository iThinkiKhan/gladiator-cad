"""Depth map: free room inward (+X) from the board's inner face, through the side window."""
import json, os, traceback
from pathlib import Path
HERE = Path('/home/buralien/projects/gladiator-cad/cad/head/v2-mast-20261028/side-window-pcb-20261030')
try:
    import FreeCAD as App, Part
    V = App.Vector
    d = App.openDocument(str(HERE / 'Gladiator_Head_v2_Side_PCB.FCStd'))
    groups = json.loads((HERE.parent / 'validation.json').read_text())['v2']['groups']
    tilt = set(groups['tilt'])
    X0, X1 = 1.0, 40.0
    REG = App.BoundBox(X0, 88, 230, X1, 146, 266)
    T = V(39.5, 113, 247.5)
    solids = []
    for o in d.Objects:
        if o.TypeId != 'Part::Feature' or o.Name.startswith('Side_PCB') or not o.Shape.Solids:
            continue
        if o.Name in tilt or o.Name == 'Rear_Display_Frame':
            cands = [(o.Name, o.Shape)]
        else:
            cands = []
            for t in (-38, -28, -18, -8, 0, 8, 18, 26, 34):
                s = o.Shape.copy(); s.rotate(T, V(1, 0, 0), -t); cands.append((o.Name + '@%d' % t, s))
        for n, s in cands:
            if s.BoundBox.intersect(REG):
                solids.append((n, s))
    print('candidates', sorted({n.split('@')[0] for n, _ in solids}))
    out = []
    for y10 in range(915, 1406, 10):
        for z10 in range(2355, 2596, 10):
            y, z = y10 / 10, z10 / 10
            e = Part.makeLine(V(X0, y, z), V(X1, y, z))
            best, who = X1, ''
            for n, s in solids:
                bb = s.BoundBox
                if not (bb.YMin - .01 <= y <= bb.YMax + .01 and bb.ZMin - .01 <= z <= bb.ZMax + .01) or bb.XMin >= best:
                    continue
                c = s.common(e)
                for ed in c.Edges:
                    x = min(ed.Vertexes[0].Point.x, ed.Vertexes[-1].Point.x)
                    if x < best:
                        best, who = x, n
            out.append([y, z, round(best, 2), who])
    (HERE / 'inward_depth.json').write_text(json.dumps(out))
    print('ok', len(out))
except Exception:
    traceback.print_exc()
os._exit(0)
