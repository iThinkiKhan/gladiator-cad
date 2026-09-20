"""Belt mesh coupon plate: three groove widths, one print, one question.

Which groove radius meshes with a real 2GT belt? Depth is held at the 2GT
nominal 0.75 mm for all three, so groove WIDTH is the only variable.
Scallop count on the inner face identifies each: 1 = narrowest.
"""
import sys, math
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A, Part, MeshPart
from pathlib import Path
O=[]
def p(s): O.append(s)

PITCH, PLD, DEPTH, N, W, ARC = 2.0, 0.254, 0.75, 60, 6.0, 60.0
VARIANTS = [(1, 0.60), (2, 0.65), (3, 0.70)]     # (scallops, groove radius)
OUT = Path('/home/buralien/projects/gladiator-cad/cad/head/v03-belt/stl')

def cyl(r,z,h,x=0,y=0): return Part.makeCylinder(r,h,A.Vector(x,y,z))
def fuse(*ss):
    s=ss[0]
    for t in ss[1:]: s=s.fuse(t)
    return s.removeSplitter()
def sector(r, z, h, a0, a1):
    keep=[]; a=a0; step=10.0
    while a < a1-1e-9:
        b=min(a+step,a1)
        tri=Part.makePolygon([A.Vector(0,0,z),
            A.Vector(2*r*math.cos(math.radians(a)),2*r*math.sin(math.radians(a)),z),
            A.Vector(2*r*math.cos(math.radians(b)),2*r*math.sin(math.radians(b)),z),
            A.Vector(0,0,z)])
        keep.append(Part.Face(tri).extrude(A.Vector(0,0,h)))
        a=b
    return cyl(r,z,h).common(fuse(*keep))

pd = N*PITCH/math.pi; od = pd-2*PLD; ro = od/2.0
p('2GT %dT   pitch dia %.4f   OD %.4f   depth held at %.2f mm' % (N,pd,od,DEPTH))
p('')
p('%-9s %-9s %-11s %-11s %-11s' % ('scallops','groove r','width@OD','land@OD','root dia'))

parts=[]
for idx,(marks, gr) in enumerate(VARIANTS):
    rc = ro - DEPTH + gr
    body = cyl(ro, 0, W)
    for i in range(N):
        a = 2*math.pi*i/N
        body = body.cut(cyl(gr, -0.1, W+0.2, rc*math.cos(a), rc*math.sin(a)))
    body = body.common(sector(30, -1, W+2, -ARC/2, ARC/2)).cut(cyl(12, -1, W+2))
    # identifying scallops on the inner face
    for k in range(marks):
        ang = math.radians((k - (marks-1)/2.0) * 7.0)
        body = body.cut(cyl(1.0, -1, W+2, 12*math.cos(ang), 12*math.sin(ang)))
    assert body.isValid() and len(body.Solids)==1, 'variant %d' % marks
    half = math.sqrt(max(gr**2-(ro-rc)**2, 0))
    p('%-9d %-9.2f %-11.4f %-11.4f %-11.4f'
      % (marks, gr, 2*half, 2*math.pi*ro/N - 2*half, 2*(rc-gr)))
    bb = body.BoundBox
    body.translate(A.Vector(-bb.XMin + idx*20.0, -bb.YMin, -bb.ZMin))
    parts.append(body)

plate = fuse(*parts) if False else Part.makeCompound(parts)
bb = plate.BoundBox
p('')
p('plate  %.1f x %.1f x %.1f mm   %.2f cm3   3 pieces' % (bb.XLength,bb.YLength,bb.ZLength,plate.Volume/1000.))
contact = sum(f.Area for f in plate.Faces
              if f.Surface.__class__.__name__=='Plane'
              and abs(f.BoundBox.ZMax) < 1e-6 and abs(f.BoundBox.ZMin) < 1e-6)
p('bed contact %.1f mm2 total, %.1f mm2 each  -> USE A BRIM' % (contact, contact/3))
mesh = MeshPart.meshFromShape(Shape=plate, LinearDeflection=0.01,
                              AngularDeflection=0.0872665, Relative=False)
f = OUT/'Gladiator_HeadCoupon_BeltMesh_3up.stl'
mesh.write(str(f))
p('wrote %s  (%d facets, solid=%s)' % (f.name, mesh.CountFacets, mesh.isSolid()))
open('/tmp/plate.txt','w').write('\n'.join(O))
