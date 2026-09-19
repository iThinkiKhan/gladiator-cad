"""Render the two CAD candidates at the same scale from tessellated solids."""
import json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
SCRIPT=Path(__file__).resolve()
OUT=(SCRIPT.parent.parent if SCRIPT.parent.name=='generator'
     else SCRIPT.parents[1]/'docs/mast-head/v02-screen-180')
BASE=OUT.parent
old=[m for m in json.loads((OUT/'reference/head-preview-mesh.json').read_text()) if not m.get('context')]
new=[m for m in json.loads((OUT/'head-preview-mesh.json').read_text()) if not m.get('context')]
def posed(items, angle):
    result=[]; a=math.radians(angle)
    rot=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    for m in items:
        q=dict(m); v=np.array(m['vertices'])
        if m['motion'] in ['pan','tilt']: v=v@rot.T
        if m['motion']=='servo':
            origin=np.array([0,42,0]); v=(v-origin)@rot.T+origin
        q['vertices']=v.tolist();result.append(q)
    return result
presented=posed(new,180)
S=2; W,H=1680,1000
im=Image.new('RGB',(W*S,H*S),'#f2f4f5');d=ImageDraw.Draw(im)
def font(n,bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),n*S)
def text(x,y,s,size=18,fill='#263b45',bold=False):
    d.text((x*S,y*S),s,font=font(size,bold),fill=fill)
eye=np.array([-1,-1.35,.85]);eye/=np.linalg.norm(eye)
u=np.cross([0,0,1],eye);u/=np.linalg.norm(u);v=np.cross(eye,u)
allv=np.concatenate([np.array(m['vertices']) for items in [old,new,presented] for m in items])
q=np.column_stack([allv@u,allv@v]);lo=q.min(0);hi=q.max(0)
center=(lo+hi)/2;scale=min(490/(hi[0]-lo[0]),575/(hi[1]-lo[1]))
def render(items,x,y):
    tris=[]
    light=np.array([-.35,-.6,.72]);light/=np.linalg.norm(light)
    def project(p):return ((x+245+(p[0]-center[0])*scale)*S,(y+287.5-(p[1]-center[1])*scale)*S)
    for m in items:
        verts=np.array(m['vertices']);col=np.array(m['color'])*255
        for f in m['faces']:
            pts=verts[np.array(f)];n=np.cross(pts[1]-pts[0],pts[2]-pts[0]);length=np.linalg.norm(n)
            if length<1e-9:continue
            n/=length
            if n@eye<-.001:continue
            rgb=tuple(int(c) for c in np.clip(col*(.65+.35*max(0,n@light)),0,255))
            xy=[project((p@u,p@v)) for p in pts]
            tris.append((float(pts.mean(0)@eye),xy,rgb))
    for _,poly,color in sorted(tris,key=lambda t:t[0]):d.polygon(poly,fill=color)
text(42,26,'GLADIATOR  /  TWO HEAD DESIGNS',30,bold=True)
text(42,73,'Actual CAD geometry · matching camera and scale · original design preserved',19)
for x,title,subtitle,items in [
    (42,'01  Original head','Sensor carrier · ±40° pan',old),
    (593,'02  Screen head / travel','Sensors forward · 0°',new),
    (1144,'02  Screen head / present','Rear screen forward · 180°',presented)]:
    text(x,139,title,23,bold=True);text(x,177,subtitle,18)
    render(items,x,220)
text(42,825,'Original mast, GH44 interface, sensors and tilt geometry carried forward',22,bold=True)
text(42,868,'New: 62 × 29 × 3.2 mm screen board · removable rear frame · belt-drive concept · head raised 28 mm',19)
text(42,920,'Comparison candidate: pulley teeth, screen retention, connectors and actual servo travel still need validation.',17,fill='#536a75')
text(42,950,'Dark rectangle represents the measured whole display board; its active screen window has not been measured.',17,fill='#536a75')
im.resize((W,H),Image.Resampling.LANCZOS).save(OUT/'head-v01-v02-comparison.png')
print(OUT/'head-v01-v02-comparison.png')
