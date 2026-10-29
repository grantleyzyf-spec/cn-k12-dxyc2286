#!/usr/bin/env python3
"""生成 1200×630 社交分享图（og:image），微信/QQ/微博转发有缩略图。
用法：python3 scripts/make_og_image.py
输出：assets/og.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (15, 110, 98)          # #0f6e62 站点主色
BG2 = (12, 88, 79)
FG = (255, 255, 255)
ACC = (223, 243, 239)       # #dff3ef

F_BOLD = "/System/Library/Fonts/Hiragino Sans GB.ttc"
F_REG = "/System/Library/Fonts/Hiragino Sans GB.ttc"


def font(size, bold=False):
    for p in ([F_BOLD] if bold else [F_REG]):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size, index=1 if bold else 0)
            except Exception:
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# 底部渐深：画一条半透明带
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(overlay)
for y in range(360, H):
    a = int(60 * (y - 360) / (H - 360))
    od.line([(0, y), (W, y)], fill=BG2 + (a,))
img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
d = ImageDraw.Draw(img)

# 左侧竖条
d.rectangle([80, 96, 88, 300], fill=ACC)

d.text((116, 96), "学科图谱", font=font(96, True), fill=FG)
d.text((118, 226), "找到真正没学会的那一步", font=font(52), fill=ACC)

line = "17 学科 · 1924 知识点 · 2199 条先修关系 · 自适应诊断"
d.text((118, 330), line, font=font(34), fill=(236, 250, 247))

# 三个标签
tags = ["回溯源到根因", "按年级排补学路径", "免费公益"]
x, y = 118, 410
for t in tags:
    tw = d.textlength(t, font=font(28))
    d.rounded_rectangle([x, y, x + tw + 40, y + 56], radius=28,
                        outline=(255, 255, 255), width=2)
    d.text((x + 20, y + 12), t, font=font(28), fill=FG)
    x += tw + 64

d.text((118, 540), "xueketupu.com", font=font(34, True), fill=FG)
d.text((900, 540), "中小学 · 高中", font=font(30), fill=ACC)

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "og.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out, "PNG", optimize=True)
print("saved", out, f"{os.path.getsize(out)/1024:.0f}KB")
