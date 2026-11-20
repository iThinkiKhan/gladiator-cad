import sys
sys.path.extend(['/usr/lib/freecad/lib', '/usr/lib/freecad/Mod',
                 '/usr/lib/freecad-python3/lib'])
import Mesh

paths = [
    '/home/buralien/projects/gladiator-cad/cad/power-board/v1-cradle/stl/PowerBoardCradle_v1_installed.stl',
    '/home/buralien/projects/gladiator-cad/cad/power-board/v1-cradle/stl/PowerBoardCradle_v1_print-on-rear-face.stl',
]
for path in paths:
    mesh = Mesh.Mesh(path)
    bb = mesh.BoundBox
    print(path.rsplit('/', 1)[-1], 'facets', mesh.CountFacets,
          'points', mesh.CountPoints,
          'components', mesh.countSeparateComponents(),
          'bbox', round(bb.XLength, 2), round(bb.YLength, 2), round(bb.ZLength, 2),
          'volume', round(mesh.Volume, 2),
          'nonmanifold', len(mesh.getNonManifolds()),
          'self_intersections', len(mesh.getSelfIntersections()))
