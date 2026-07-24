from PIL import Image, ImageFilter, ImageDraw
import os

src = r"F:\资料\kimi\new game\game\public\scenes\event06\ch4.png"
dst = r"F:\资料\kimi\new game\game\public\scenes\event06\ch4.jpg"

im = Image.open(src).convert("RGB")
w, h = im.size  # 2048x1152

# 水印区域（AI生成，左下角深色木板）: x 0-160, y 1075-1150
wm_x0, wm_y0, wm_x1, wm_y1 = 0, 1075, 160, 1150
bw, bh = wm_x1 - wm_x0, wm_y1 - wm_y0

# 克隆源：水印正上方同尺寸木板区域（保持竖向板缝连续）
src_y0 = wm_y0 - bh - 10
patch = im.crop((wm_x0, src_y0, wm_x1, src_y0 + bh))

# 羽化蒙版，边缘无痕融合
mask = Image.new("L", (bw, bh), 0)
d = ImageDraw.Draw(mask)
d.rectangle((0, 0, bw, bh), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(8))

im.paste(patch, (wm_x0, wm_y0), mask)

im.save(dst, "JPEG", quality=90)
print("saved", dst, os.path.getsize(dst), "bytes")
