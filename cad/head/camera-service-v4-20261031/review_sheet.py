"""Labelled review sheet for camera service v4 (run on cad-lab with python3)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
OUT = Path('/home/buralien/projects/gladiator-cad/cad/head/camera-service-v4-20261031')
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'
title_f = ImageFont.truetype(F % '-Bold', 36)
lab_f = ImageFont.truetype(F % '-Bold', 24)
small_f = ImageFont.truetype(F % '', 21)
S = 0.5
W, H = 1640, 1460
sheet = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(sheet)
d.text((24, 18), 'Camera case v4 - LED spotlight window + plug clips (CAD draft, not printed)', fill='black', font=title_f)
panels = [('front_led_window.png', 'Front: LED window beside the lens', (20, 80),
           [((1018, 850), (1180, 1080), 'flash LED window'), ((860, 530), (1100, 360), 'lens')]),
          ('cover_inside.png', 'Cover, inside: light tube', (820, 80),
           [((690, 760), (300, 1000), 'light tube to LED'), ((745, 668), (900, 560), 'notch for camera flex')]),
          ('plugs_rear.png', 'Back of the board: plug clips', (20, 700),
           [((550, 600), (180, 300), 'plug clip (print 2)'), ((460, 640), (200, 900), 'wire lanes (comb)'),
            ((965, 640), (1120, 1000), 'plug clip')]),
          ('open_tray_clips.png', 'In the tray (board hidden)', (820, 700),
           [((560, 540), (200, 330), 'clip on 8 plugs'), ((1000, 520), (1180, 420), 'clip'),
            ((695, 352), (850, 200), 'M2 insert')])]
for fn, cap, (x0, y0), labels in panels:
    im = Image.open(OUT / fn).convert('RGB')
    im = im.resize((int(im.width * S), int(im.height * S)), Image.LANCZOS)
    sheet.paste(im, (x0, y0))
    d.rectangle([x0, y0, x0 + im.width, y0 + im.height], outline=(200, 200, 200))
    d.text((x0 + 14, y0 + 8), cap, fill=(60, 60, 60), font=lab_f)
    for (px, py), (tx, ty), txt in labels:
        P = (x0 + px * S, y0 + py * S); T = (x0 + tx * S, y0 + ty * S)
        d.line([P, T], fill=(200, 30, 30), width=3)
        d.ellipse([P[0] - 5, P[1] - 5, P[0] + 5, P[1] + 5], outline=(200, 30, 30), width=3)
        bb = d.textbbox(T, txt, font=small_f)
        d.rectangle([bb[0] - 4, bb[1] - 3, bb[2] + 4, bb[3] + 3], fill='white', outline=(200, 30, 30))
        d.text(T, txt, fill=(150, 20, 20), font=small_f)
notes = ['LED: 6.3 x 6.6 window; light tube stops 0.33 mm above the LED. Beam cut off at about 42 deg, centre-weighted',
         '(about 40% brightness at the edge of the camera picture). Needs firmware to turn the LED on (GPIO4 PWM).',
         'Plugs: each clip turns a row of 8 single Dupont plugs into one block. Wires drop sideways into the comb lanes',
         '(1.74 mm), then turn out to the wall exits. Floor pads sit 0.4 mm behind the clips once the case is closed.',
         'Same outside shape as v3 (inserts, bumps, head clearance unchanged). Both clips are the same part: print 2.']
for i, t in enumerate(notes):
    d.text((24, 1310 + i * 29), t, fill='black', font=small_f)
sheet.save(OUT / 'review_sheet.png')
print('ok')
