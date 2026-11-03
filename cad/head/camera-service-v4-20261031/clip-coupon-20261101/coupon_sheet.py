"""Plate layout + labelled preview sheet for the clip coupon (python3 on cad-lab)."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
D = Path(__file__).resolve().parent


def load(fn):
    b = Path(fn).read_bytes(); n = int.from_bytes(b[80:84], 'little')
    a = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([('n', '<3f4'), ('v', '<3f4', (3,)), ('a', '<u2')]))
    return a['v'].astype(float)


stl = sorted((D / 'stl').glob('*.stl'))
fig, ax = plt.subplots(figsize=(7, 7))
ax.add_patch(plt.Rectangle((0, 0), 220, 220, fill=False, lw=1.5))
place = [(load(stl[3]), 85.0, 87.0, (.55, .58, .62), '04')] + [(load(f), 130.0 + 12 * i, 99.0, (.2, .5, .9), '0%d' % (i + 1)) for i, f in enumerate(stl[:3])]
for t, x0, y0, col, lab in place:
    t2 = t[:, :, :2] + [x0, y0]
    for tri in t2:
        ax.fill(tri[:, 0], tri[:, 1], color=col, lw=0)
    c = t2.reshape(-1, 2); ax.text(c[:, 0].mean(), c[:, 1].max() + 3, lab, ha='center', fontsize=12)
ax.set_xlim(-5, 225); ax.set_ylim(-5, 225); ax.set_aspect('equal'); ax.set_xlabel('mm'); ax.grid(alpha=.2)
fig.tight_layout(); fig.savefig(D / 'plate_layout.png', dpi=110)

F = '/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'
tf, lf, sf = ImageFont.truetype(F % '-Bold', 34), ImageFont.truetype(F % '-Bold', 23), ImageFont.truetype(F % '', 21)
W, H, PW, PH = 2130, 1290, 700, 560
sheet = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(sheet)
d.text((24, 16), 'Camera case v4 - plug clip test coupon (STL for you to slice; no G-code made)', fill='black', font=tf)
panels = [('plate_layout.png', 'Suggested layout, 220 x 220 bed, top view'),
          ('view_clips_iso.png', 'Clips: 1 / 2 / 3 notches = pocket 2.56 / 2.66 / 2.76 mm'),
          ('view_tray_coupon.png', '04: bottom of the v4 tray (floor, pads, 4 board seats)'),
          ('view_in_use_board_hidden.png', 'Test, board hidden: clipped plugs over the pads'),
          ('view_in_use.png', 'Test: board pressed onto its 4 seats'),
          (None, None)]
for i, (fn, cap) in enumerate(panels):
    x0, y0 = 15 + (i % 3) * (PW + 10), 75 + (i // 3) * (PH + 50)
    if fn is None:
        notes = ['How to test:', '1. Plugs on a header row as now; wires sideways', '   into the comb lanes; slide a clip on.',
                 '2. Pick the clip that slides on with light', '   pressure and holds 8 plugs as one block.',
                 '3. Put the board in 04, wires out the side', '   openings; press it onto the 4 seats.',
                 '   It should sit flat, not rock.', '4. Tug each wire: the plug should stay on.',
                 '', 'Clips stand 13 mm tall on a 4 mm footprint:', 'use a brim.', 'About 9 g of PLA if printed solid.']
        for k, t in enumerate(notes):
            d.text((x0 + 10, y0 + 10 + k * 33), t, fill='black', font=lf if k == 0 else sf)
        continue
    im = Image.open(D / fn).convert('RGB'); im.thumbnail((PW, PH))
    sheet.paste(im, (x0 + (PW - im.width) // 2, y0 + 30))
    d.text((x0 + 6, y0), cap, fill=(40, 40, 40), font=lf)
sheet.save(D / 'coupon_preview.png')
print('ok')
