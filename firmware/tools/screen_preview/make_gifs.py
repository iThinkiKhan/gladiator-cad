"""Turn preview.exe output (raw RGB888 frames + timing.json) into GIFs and a contact sheet."""
import json, sys, pathlib
from PIL import Image, ImageDraw
src = pathlib.Path(sys.argv[1]); dst = pathlib.Path(sys.argv[2]); dst.mkdir(parents=True, exist_ok=True)
W, H, S = 320, 170, 2
timing = json.loads((src / "timing.json").read_text())
sheet_rows = []
for sc in timing["scenarios"]:
    raw = (src / f"{sc['name']}.rgb").read_bytes(); n = len(raw) // (W * H * 3)
    frames = [Image.frombytes("RGB", (W, H), raw[i*W*H*3:(i+1)*W*H*3]) for i in range(n)]
    big = [f.resize((W*S, H*S), Image.NEAREST) for f in frames]
    durs = [max(20, int(round(p / 10.0)) * 10) for p in sc["periodsMs"]]
    big[0].save(dst / f"{sc['name']}.gif", save_all=True, append_images=big[1:], duration=durs, loop=0, optimize=False)
    picks = [frames[int(k * (n - 1) / 3)] for k in range(4)]
    sheet_rows.append((sc, picks))
pad = 10; label = 22
sheet = Image.new("RGB", (pad + 4 * (W + pad), pad + len(sheet_rows) * (H + label + pad)), (24, 28, 34))
d = ImageDraw.Draw(sheet)
for r, (sc, picks) in enumerate(sheet_rows):
    y = pad + r * (H + label + pad)
    d.text((pad, y + 4), f"{sc['name']}  -  {sc['fps']} fps simulated at 4 MHz SPI", fill=(200, 210, 220))
    for c, f in enumerate(picks):
        sheet.paste(f, (pad + c * (W + pad), y + label))
sheet.save(dst / "contact-sheet.png")
print("wrote", dst)
