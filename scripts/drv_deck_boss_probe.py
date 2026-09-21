import sys
sys.path.append('/usr/lib/freecad-python3/lib')
import FreeCAD as A, Part
O=[]
def p(s): O.append(s)
d=A.openDocument('/home/buralien/projects/gladiator-cad/cad/master/Gladiator_Master.FCStd')
deck=d.getObject('UpperDeck').Shape
def hit(a,b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox): return 0.0
        return a.common(b).Volume
    except Exception: return 0.0
p('Scanning a D3.0 column straight down the deck boss axis at (14.5, 95).')
p('Deck slab is Z 48..52; the boss runs Z 52..58.')
p('')
p('%8s %12s %10s' % ('Z band','deck material','state'))
for z in [float(i) for i in range(46,60)]:
    pr=Part.makeCylinder(1.5,1.0,A.Vector(14.5,95.0,z))
    v=hit(pr,deck); full=pr.Volume
    st='OPEN' if v<0.3 else ('solid' if v>full*0.8 else 'partial')
    p('%5.0f..%-3.0f %12.2f %10s' % (z,z+1,v,st))
p('')
p('So the D4.6 feature is a BLIND pocket opening upward at the boss top,')
p('with deck slab closing it underneath. That is an insert pocket, not a')
p('clearance hole - the insert goes in the DECK and the screw comes DOWN.')
p('')
p('For a screw to come UP from below instead, that floor must be drilled')
p('through. Thickness of the floor:')
solid=0.0
for z in [46+0.25*i for i in range(0,40)]:
    pr=Part.makeCylinder(1.5,0.25,A.Vector(14.5,95.0,z))
    if hit(pr,deck)>0.2: solid+=0.25
p('   about %.2f mm of deck under the pocket' % solid)
open('/tmp/db.txt','w').write(chr(10).join(O))
