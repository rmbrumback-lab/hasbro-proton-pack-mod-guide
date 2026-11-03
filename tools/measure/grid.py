"""Overlay a labeled pixel grid on an image (or a crop of it) for reading coordinates.

python tools/measure/grid.py IMAGE OUT [x0 y0 x1 y1] [--step N] [--scale S]
Coordinates printed on the grid are in the ORIGINAL image's pixels.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

args = [a for a in sys.argv[1:] if not a.startswith("--")]
opts = dict(a[2:].split("=") for a in sys.argv[1:] if a.startswith("--"))
src, out = args[0], args[1]
im = Image.open(src).convert("RGB")
x0, y0, x1, y1 = (map(int, args[2:6]) if len(args) >= 6 else (0, 0, *im.size))
step = int(opts.get("step", 100))
scale = float(opts.get("scale", 1))
crop = im.crop((x0, y0, x1, y1))
if scale != 1:
    crop = crop.resize((int(crop.width * scale), int(crop.height * scale)), Image.LANCZOS)
d = ImageDraw.Draw(crop)
try:
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except OSError:
    f = ImageFont.load_default()
for gx in range((x0 // step) * step, x1 + 1, step):
    if gx < x0:
        continue
    X = (gx - x0) * scale
    d.line([(X, 0), (X, crop.height)], fill=(0, 255, 255), width=1)
    d.text((X + 2, 2), str(gx), fill=(255, 255, 0), font=f)
for gy in range((y0 // step) * step, y1 + 1, step):
    if gy < y0:
        continue
    Y = (gy - y0) * scale
    d.line([(0, Y), (crop.width, Y)], fill=(0, 255, 255), width=1)
    d.text((2, Y + 2), str(gy), fill=(255, 255, 0), font=f)
crop.save(out, quality=92)
print(out, crop.size)
