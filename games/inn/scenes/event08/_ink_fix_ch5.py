# -*- coding: utf-8 -*-
"""EVENT-08 ch5 v3: erase pseudo-glyphs at true location (1490-1540, 932-986) via bright-stroke suppression."""
import os
import numpy as np
from PIL import Image, ImageFilter

DST = r"F:\资料\kimi\new game\game\public\scenes\event08\ch5.jpg"
img = Image.open(DST).convert("RGB")
arr = np.asarray(img).astype(np.float32)

x0, y0, x1, y1 = 1488, 930, 1542, 988
box = arr[y0:y1, x0:x1].copy()
lum = box.mean(axis=2)
dark = box[lum < 45]
ref = np.median(dark, axis=0) if len(dark) else np.array([20.0, 13.0, 8.0])
print("dark ref:", ref, "dark count:", len(dark))

base = box.copy()
base[lum > 55] = ref
base = np.asarray(Image.fromarray(base.astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))).astype(np.float32)

m = np.clip((lum - 48.0) / 35.0, 0.0, 1.0)
m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255.0
m = m[..., None]

arr[y0:y1, x0:x1] = box * (1 - m) + base * m
Image.fromarray(arr.astype(np.uint8)).save(DST, quality=90, subsampling=0)

chk = np.asarray(Image.open(DST).convert("RGB")).astype(int)[y0:y1, x0:x1].mean(axis=2)
print("glyph zone bright>60:", int((chk > 60).sum()), "| max:", chk.max(), "| size:", os.path.getsize(DST))
