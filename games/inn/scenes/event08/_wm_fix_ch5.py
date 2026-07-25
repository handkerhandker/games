# -*- coding: utf-8 -*-
"""EVENT-08 ch5 v3: opaque core clone (guaranteed full cover) + outer feather blend."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC = r"F:\资料\kimi\new game\game\public\scenes\event08\ch5.png"
DST = r"F:\资料\kimi\new game\game\public\scenes\event08\ch5.jpg"

img = Image.open(SRC).convert("RGB")

SHIFT = 76  # clone from 76px directly above (same continuous dark wood floor)

# Step 1: opaque paste over text zone + margin (text x17-124 y1088-1124 fully inside)
core = (4, 1072, 142, 1140)
w, h = core[2] - core[0], core[3] - core[1]
patch = img.crop((core[0], core[1] - SHIFT, core[2], core[3] - SHIFT))
img.paste(patch, (core[0], core[1]))

# Step 2: feather pass on a 16px-larger frame, softening the seam ring
fx0, fy0, fx1, fy1 = core[0] - 16, core[1] - 16, core[2] + 16, core[3] + 16
fx0, fy0 = max(0, fx0), max(0, fy0)
fw, fh = fx1 - fx0, fy1 - fy0
fpatch = img.crop((fx0, fy0 - SHIFT, fx1, fy1 - SHIFT))
mask = Image.new("L", (fw, fh), 0)
d = ImageDraw.Draw(mask)
d.rectangle([8, 8, fw - 9, fh - 9], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(5))
img.paste(fpatch, (fx0, fy0), mask)

img.save(DST, quality=90, subsampling=0)

arr = np.asarray(Image.open(DST).convert("RGB")).astype(int)
zone = arr[1072:1140, 4:142].mean(axis=2)
print("residual bright>60:", int((zone > 60).sum()), "| max:", zone.max(), "| size:", os.path.getsize(DST))
