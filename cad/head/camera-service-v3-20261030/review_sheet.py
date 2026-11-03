"""Labelled review sheet for camera service v3 (run on cad-lab with python3)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
OUT = Path('/home/buralien/projects/gladiator-cad/cad/head/camera-service-v3-20261030')
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'
title_f = ImageFont.truetype(F % '-Bold', 38)
lab_f = ImageFont.truetype(F % '-Bold', 24)
small_f = ImageFont.truetype(F % '', 22)
S = 0.625
W, H = 2000, 1000
sheet = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(sheet)
d.text((30, 20), 'Camera case v3 - cover on M2 heat-set inserts (CAD draft, not printed)', fill='black', font=title_f)
panels = [('exploded.png', 'Assembly: cover + 2 x M2x6', 0,
           [((598, 352), (150, 250), 'M2 insert'), ((777, 745), (300, 1020), 'M2 insert'),
            ((1030, 555), (1240, 420), 'M2x6 screw'), ((1210, 945), (1300, 1080), 'M2x6 screw'),
            ((1015, 625), (1150, 860), 'lens chamfer')]),
          ('open_tray.png', 'Tray, cover off', 1000,
           [((697, 352), (900, 230), 'insert in lug top (2.8 x 4 deep)'), ((1070, 1047), (1160, 1110), 'insert'),
            ((1018, 928), (1160, 820), 'snap bump'), ((670, 980), (230, 1060), 'snap bump')])]
for fn, cap, x0, labels in panels:
    im = Image.open(OUT / fn).convert('RGB')
    im = im.resize((int(im.width * S), int(im.height * S)), Image.LANCZOS)
    y0 = 90
    sheet.paste(im, (x0, y0))
    d.text((x0 + 30, y0 + 10), cap, fill=(60, 60, 60), font=lab_f)
    for (px, py), (tx, ty), txt in labels:
        P = (x0 + px * S, y0 + py * S); T = (x0 + tx * S, y0 + ty * S)
        d.line([P, T], fill=(200, 30, 30), width=3)
        d.ellipse([P[0] - 6, P[1] - 6, P[0] + 6, P[1] + 6], outline=(200, 30, 30), width=3)
        bb = d.textbbox(T, txt, font=small_f)
        d.rectangle([bb[0] - 4, bb[1] - 3, bb[2] + 4, bb[3] + 3], fill='white', outline=(200, 30, 30))
        d.text(T, txt, fill=(150, 20, 20), font=small_f)
notes = ['Cover: 2 x M2x6 into heat-set inserts (replaces M3 screws + side-loaded nuts). M2x8 also fits.',
         'Lugs smaller (radius 4.4 -> 3.6), about 0.9 g lighter on the camera side. Snap bumps hold the board with the cover off.',
         'Unchanged: wire channels, skirts, tie passages, SD slot, lens position, 3 x M2x6 carrier screws.']
for i, t in enumerate(notes):
    d.text((30, 860 + i * 40), t, fill='black', font=small_f)
sheet.save(OUT / 'review_sheet.png')
print('ok')
