# -*- coding: utf-8 -*-
"""Final: clone dark table front-face (x200-375) over watermark (x5-180, y1065-1140)."""
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

src = r"F:\资料\kimi\new game\game\public\scenes\event07\ch3.png"
dst = r"F:\资料\kimi\new game\game\public\scenes\event07\ch3.jpg"

im = Image.open(src).convert("RGB")
tx0, ty0, tx1, ty1 = 5, 1065, 180, 1140
w, h = tx1 - tx0, ty1 - ty0

donor = im.crop((200, ty0, 200 + w, ty1)).filter(ImageFilter.GaussianBlur(0.8))
darr = np.asarray(donor).mean(axis=2)
print("donor lum max/mean:", darr.max(), round(float(darr.mean()), 1))

mask = Image.new("L", (w, h), 0)
ImageDraw.Draw(mask).rectangle([8, 7, w - 8, h - 7], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(6))

im.paste(donor, (tx0, ty0), mask)
after = np.asarray(im.crop((tx0, ty0, tx1, ty1))).mean(axis=2)
print("after target lum max/mean:", after.max(), round(float(after.mean()), 1))

im.save(dst, quality=90)
print("saved", dst)
