#!/usr/bin/env python3
"""给库存补齐批次的「招牌识字 / 交通标志」画牌面底图（程序化，不走出图服务）。

ThaiLearningCards 的招牌版式把泰文压在 y≈600 的位置、深色字，所以每张图在
y 520–820 留一块浅色牌面；交通标志在牌面上方另画图形（红圈、三角、蓝底箭头）。
泰文本身由 Remotion 排，这里一个字都不画 —— 免得 PIL 的泰文排版把声调符排歪。

    python3 scripts/draw_topup_signs.py <project_id>
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

REPO = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
PLATE = (110, 500, 970, 840)  # 文字牌面
RED, BLUE, GREEN, YELLOW, WHITE = (204, 36, 40), (24, 86, 168), (22, 128, 74), (246, 196, 40), (250, 250, 246)
INK = (24, 27, 30)


def backdrop(tone: tuple[int, int, int]) -> Image.Image:
    """V1.0 家族背景：主色 → 夜蓝 → 深青的斜向渐变 + 两条淡弧线（2026-11 ChatGPT 稿）。"""
    top, mid, bot = tone, (52, 52, 83), (12, 32, 44)
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        for x in range(0, W, 4):
            k = min(1.0, max(0.0, (y * 0.9 + x * 0.35) / (H * 0.9 + W * 0.35)))
            a, b, t = (top, mid, k / .55) if k < .55 else (mid, bot, (k - .55) / .45)
            c = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
            for dx in range(4):
                px[x + dx, y] = c
    d = ImageDraw.Draw(img)
    d.arc([200, -500, 1300, 420], 160, 330, fill=(214, 168, 222), width=3)
    d.arc([-500, 1500, 700, 2400], 200, 330, fill=(164, 162, 206), width=3)
    return img.filter(ImageFilter.GaussianBlur(1.2))


def post(d: ImageDraw.ImageDraw, top: int) -> None:
    """金属立杆：中间亮、两边暗的竖向条纹模拟圆管。"""
    cx, r = W // 2, 26
    for dx in range(-r, r + 1):
        k = 1 - abs(dx) / r
        g = int(110 + 120 * k ** 2)
        d.line([(cx + dx, top), (cx + dx, 1300)], fill=(g, g + 4, g + 8))


def screw(d: ImageDraw.ImageDraw, x: int, y: int, r: int = 13) -> None:
    d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 156, 162))
    d.ellipse([x - r + 3, y - r + 3, x + r - 3, y + r - 3], fill=(205, 210, 214))
    d.line([(x - r + 5, y), (x + r - 5, y)], fill=(120, 124, 130), width=3)


def plate(d: ImageDraw.ImageDraw, fill=WHITE, border=None, stripe=None) -> None:
    x0, y0, x1, y1 = PLATE
    d.rounded_rectangle([x0 + 10, y0 + 14, x1 + 10, y1 + 14], 30, fill=(0, 0, 0))  # 投影
    d.rounded_rectangle(PLATE, 30, fill=border or fill)
    if border:
        d.rounded_rectangle([x0 + 18, y0 + 18, x1 - 18, y1 - 18], 20, fill=fill)
    if stripe:
        d.rounded_rectangle([x0 + 18, y1 - 74, x1 - 18, y1 - 18], 14, fill=stripe)


def circle_sign(d, cx, cy, r, ring=RED, fill=WHITE):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ring)
    d.ellipse([cx - r * .8, cy - r * .8, cx + r * .8, cy + r * .8], fill=fill)


def slash(d, cx, cy, r):
    a = math.radians(45)
    d.line([(cx - r * .8 * math.cos(a), cy - r * .8 * math.sin(a)), (cx + r * .8 * math.cos(a), cy + r * .8 * math.sin(a))], fill=RED, width=int(r * .2))


def cross(d, cx, cy, r):
    slash(d, cx, cy, r)
    d.line([(cx + r * .56, cy - r * .56), (cx - r * .56, cy + r * .56)], fill=RED, width=int(r * .2))


def arrow(d, cx, cy, s, direction, color=INK, w=34):
    if direction in ("left", "right"):
        sgn = -1 if direction == "left" else 1
        d.line([(cx - sgn * s * .1, cy + s * .55), (cx - sgn * s * .1, cy - s * .05), (cx + sgn * s * .45, cy - s * .05)], fill=color, width=w, joint="curve")
        tip = cx + sgn * s * .6
        d.polygon([(tip, cy - s * .05), (tip - sgn * s * .26, cy - s * .27), (tip - sgn * s * .26, cy + s * .17)], fill=color)
    elif direction == "uturn":
        d.arc([cx - s * .4, cy - s * .55, cx + s * .2, cy + s * .05], 180, 360, fill=color, width=w)
        d.line([(cx - s * .4 + w / 2, cy - s * .25), (cx - s * .4 + w / 2, cy + s * .55)], fill=color, width=w)
        d.line([(cx + s * .2 - w / 2, cy - s * .25), (cx + s * .2 - w / 2, cy + s * .1)], fill=color, width=w)
        d.polygon([(cx + s * .2 - w / 2, cy + s * .42), (cx - s * .02, cy + s * .1), (cx + s * .42, cy + s * .1)], fill=color)
    elif direction == "up":
        d.line([(cx, cy + s * .55), (cx, cy - s * .2)], fill=color, width=w)
        d.polygon([(cx, cy - s * .6), (cx - s * .3, cy - s * .15), (cx + s * .3, cy - s * .15)], fill=color)


def walker(d, cx, cy, s, color=INK):
    d.ellipse([cx - s * .09, cy - s * .62, cx + s * .09, cy - s * .44], fill=color)
    d.line([(cx, cy - s * .4), (cx - s * .05, cy + s * .05)], fill=color, width=int(s * .1))
    d.line([(cx - s * .05, cy + s * .05), (cx - s * .25, cy + s * .5)], fill=color, width=int(s * .09))
    d.line([(cx - s * .05, cy + s * .05), (cx + s * .2, cy + s * .5)], fill=color, width=int(s * .09))
    d.line([(cx - s * .25, cy - s * .15), (cx + s * .22, cy - s * .25)], fill=color, width=int(s * .08))


def triangle(d, cx, cy, s, fill=YELLOW, ring=RED):
    pts = [(cx, cy - s * .62), (cx - s * .66, cy + s * .48), (cx + s * .66, cy + s * .48)]
    d.polygon(pts, fill=ring)
    k = .74
    d.polygon([(cx + (x - cx) * k, cy + 18 + (y - cy) * k) for x, y in pts], fill=fill)


def draw(kind: str) -> Image.Image:
    tone = {"green": (20, 70, 52), "red": (70, 30, 32), "yellow": (82, 58, 22)}.get(kind, (30, 44, 60))
    img = backdrop(tone)
    d = ImageDraw.Draw(img)
    cx, cy, r = W // 2, 370, 200
    if kind in ("green", "red", "yellow"):
        post(d, 900)  # 店招：牌面（Remotion 画）下面只露一截立杆
    else:
        post(d, 470)
        d.rounded_rectangle([cx - 44, 585, cx + 44, 625], 8, fill=(170, 176, 182))  # 抱箍
        if kind in ("no_park", "no_stop", "no_uturn", "uturn", "no_right", "no_left"):
            d.ellipse([cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], fill=(196, 202, 208))  # 圆牌的金属外圈
        if kind in ("no_park", "no_stop"):
            circle_sign(d, cx, cy, r, RED, BLUE)
            (slash if kind == "no_park" else cross)(d, cx, cy, r)
        elif kind in ("park", "park_disabled"):
            d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], 30, fill=BLUE)
            d.rounded_rectangle([cx - r + 16, cy - r + 16, cx + r - 16, cy + r - 16], 22, outline=WHITE, width=8)
            if kind == "park":  # 大写 P（几何画，不用字体）
                d.rectangle([cx - 70, cy - 110, cx - 30, cy + 115], fill=WHITE)
                d.pieslice([cx - 110, cy - 110, cx + 85, cy + 35], 270, 90, fill=WHITE)
                d.pieslice([cx - 70, cy - 70, cx + 45, cy - 5], 270, 90, fill=BLUE)
                d.rectangle([cx - 30, cy - 70, cx - 12, cy - 5], fill=BLUE)
            else:
                d.ellipse([cx - 25, cy - 120, cx + 15, cy - 80], fill=WHITE)
                d.line([(cx - 5, cy - 70), (cx - 5, cy + 10), (cx + 60, cy + 10), (cx + 85, cy + 80)], fill=WHITE, width=24, joint="curve")
                d.arc([cx - 100, cy - 30, cx + 50, cy + 120], 90, 300, fill=WHITE, width=20)
        elif kind == "crosswalk":
            d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], 30, fill=BLUE)
            d.polygon([(cx, cy - r + 30), (cx - r + 30, cy + r - 30), (cx + r - 30, cy + r - 30)], fill=WHITE)
            for i in range(4):
                d.rectangle([cx - 90 + i * 50, cy + 70, cx - 65 + i * 50, cy + 110], fill=INK)
            walker(d, cx, cy + 10, 170)
        elif kind == "school":
            triangle(d, cx, cy, 2 * r)
            walker(d, cx - 40, cy + 30, 160)
            walker(d, cx + 55, cy + 45, 120)
        elif kind == "slow":
            triangle(d, cx, cy, 2 * r)
            d.rectangle([cx - 14, cy - 80, cx + 14, cy + 40], fill=INK)
            d.ellipse([cx - 16, cy + 60, cx + 16, cy + 92], fill=INK)
        elif kind == "pedestrian":
            triangle(d, cx, cy, 2 * r)
            walker(d, cx, cy + 40, 190)
        elif kind == "stop":
            pts = [(cx + r * math.cos(math.radians(22.5 + 45 * i)), cy + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
            d.polygon(pts, fill=RED)
            d.polygon([(cx + (x - cx) * .86, cy + (y - cy) * .86) for x, y in pts], outline=WHITE, width=10)
            # 泰国的停车让行牌是红八角 + หยุด 字样；字在下方牌面上，这里不画横杠（那是禁止驶入）
        elif kind in ("no_uturn", "uturn"):
            if kind == "no_uturn":
                circle_sign(d, cx, cy, r)
                arrow(d, cx + 10, cy, 280, "uturn")
                slash(d, cx, cy, r)
            else:
                circle_sign(d, cx, cy, r, BLUE, BLUE)
                arrow(d, cx + 10, cy, 280, "uturn", WHITE)
        elif kind in ("no_right", "no_left"):
            circle_sign(d, cx, cy, r)
            arrow(d, cx, cy, 280, "right" if kind == "no_right" else "left")
            slash(d, cx, cy, r)
        elif kind == "oneway":
            d.rounded_rectangle([cx - r - 60, cy - 90, cx + r + 60, cy + 90], 20, fill=BLUE)
            d.line([(cx - r, cy), (cx + r - 40, cy)], fill=WHITE, width=46)
            d.polygon([(cx + r + 30, cy), (cx + r - 70, cy - 70), (cx + r - 70, cy + 70)], fill=WHITE)
        else:
            raise ValueError(kind)
        if kind != "oneway":
            screw(d, cx, cy - int(r * .62))
            screw(d, cx, cy + int(r * .62))
    return img


def main() -> int:
    project_id = sys.argv[1]
    project = REPO / "projects" / project_id
    out_root = REPO / "remotion-composer" / "public"
    n = 0
    for ep in sorted((project / "artifacts" / "episodes").glob("ep*.json")):
        data = json.loads(ep.read_text())
        for item in data["items"]:
            if not item.get("imageSrc"):
                continue
            target = out_root / item["imageSrc"]
            target.parent.mkdir(parents=True, exist_ok=True)
            draw(item["sign_kind"]).save(target, optimize=True)
            n += 1
    print(f"{n} 张牌面 → remotion-composer/public/series/{project_id}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
