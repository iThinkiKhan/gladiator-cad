"""Render actual tessellated CAD geometry without a GUI or generative imagery."""
import json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]/'docs/mast-head/v01'
mesh=json.loads((ROOT/'head-preview-mesh.json').read_text())
S=2; W,H=1500,1000
im=Image.new('RGB',(W*S,H*S),'#f2f4f5');d=ImageDraw.Draw(im)
def font(n,bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),n*S)
def text(x,y,s,size=18,fill='#263b45',bold=False): d.text((x*S,y*S),s,font=font(size,bold),fill=fill)
def render(items,rect,cam):
    eye=np.array(cam,dtype=float);eye/=np.linalg.norm(eye)
    u=np.cross([0,0,1],eye);u/=np.linalg.norm(u);v=np.cross(eye,u)
    allv=np.concatenate([np.array(o['vertices']) for o in items]); q=np.column_stack([allv@u,allv@v])
    lo=q.min(0);hi=q.max(0); x,y,w,h=rect
    scale=min(w/(hi[0]-lo[0]),h/(hi[1]-lo[1]));center=(lo+hi)/2
    def project(p): return ((x+w/2+(p[0]-center[0])*scale)*S,(y+h/2-(p[1]-center[1])*scale)*S)
    tris=[]
    light=np.array([-.35,-.6,.72]);light/=np.linalg.norm(light)
    for o in items:
        vs=np.array(o['vertices']);col=np.array(o['color'])*255
        for f in o['faces']:
            pts=vs[np.array(f)];n=np.cross(pts[1]-pts[0],pts[2]-pts[0]);ln=np.linalg.norm(n)
            if ln<1e-9:continue
            n/=ln
            if n@eye<-.001: continue
            shade=.65+.35*max(0,n@light)
            rgb=tuple(int(c) for c in np.clip(col*shade,0,255))
            p=[project((a@u,a@v)) for a in pts]
            tris.append((float(pts.mean(0)@eye),p,rgb))
    for _,p,c in sorted(tris,key=lambda a:a[0]):d.polygon(p,fill=c)
text(44,25,'GLADIATOR  /  MODULAR SENSOR HEAD',29,bold=True)
text(44,68,'v0.1 geometry candidate · sensor blocks show clearance envelopes',18)
text(52,130,'Robot context',22,bold=True)
text(770,130,'Head and removable neck',22,bold=True)
render(mesh,(40,180,680,660),(-1,-1.3,.9))
head=[m for m in mesh if not m.get('context')]
render(head,(760,180,690,650),(-1,-1.35,.85))
text(52,850,'Fixed mast and neck',18)
text(770,850,'Keyed carrier face · separate motion assembly',18)
legend=[('#385766','Fixed structure'),('#29939b','Pan / tilt parts'),('#e89238','Carrier'),('#405ab8','Hardware / sensor envelopes')]
xx=52
for color,label in legend:
 d.rectangle((xx*S,907*S,(xx+17)*S,924*S),fill=color);text(xx+26,902,label,16);xx+=340
text(52,953,'Prototype geometry. Bearings, horn connections, sensor retention and harness require physical validation.',15,fill='#536a75')
im.resize((W,H),Image.Resampling.LANCZOS).save(ROOT/'modular-head-preview.png')
print(ROOT/'modular-head-preview.png')
