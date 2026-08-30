#!/usr/bin/env python3
"""把成片第 0 帧按三种比例裁一遍，看封面在横屏/方形/竖屏下各剩什么。

平台拿第一帧当封面时，会按自己的版位裁：
    9:16  竖屏  整帧          y 0–1920
    3:4   常见  1080×1440     y 240–1680
    1:1   方形  1080×1080     y 420–1500
    16:9  横屏  1080×608      y 656–1264   ← 最狠的一刀
所以**核心信息必须落在 y 656–1264 这 608 像素里**，否则横屏封面就废了。

    python3 scripts/check_cover_crops.py <project_id> [more_ids...]
"""
import subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
CROPS = [("16:9", int(W * 9 / 16)), ("1:1", W), ("3:4", int(W * 4 / 3))]

# 封面核心带：三种裁切的交集，也就是 16:9 那一刀留下的范围。
# 主标题与关键视觉必须整个落在这里，否则横屏封面必残。
BAND_TOP, BAND_BOT = (H - int(W * 9 / 16)) // 2, (H + int(W * 9 / 16)) // 2

def newest_mp4(proj: Path):
    m = sorted(proj.glob("renders/*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    return m[0] if m else None

def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    for pid in sys.argv[1:]:
        proj = REPO / "projects" / pid
        mp4 = newest_mp4(proj)
        if not mp4:
            print(f"{pid}: 没有 mp4"); continue
        out = proj / "artifacts"
        f0 = out / "_crop_full.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4),
                        "-vf", "select=eq(n\\,0)", "-frames:v", "1", str(f0)], check=True)
        tiles = []
        for name, ch in CROPS:
            y = (H - ch) // 2
            t = out / f"_crop_{name.replace(':','x')}.png"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f0),
                            "-vf", f"crop={W}:{ch}:0:{y}", "-frames:v", "1", str(t)], check=True)
            tiles.append((name, t, y, y + ch))
        # 三种裁切竖着叠起来对照（hstack 要求等高，跟整帧拼会失败，就不拼了）
        ins, filt = [], []
        for i, (name, t, _, _) in enumerate(tiles):
            ins += ["-i", str(t)]
            filt.append(f"[{i}:v]scale=620:-1,pad=620:ih+52:0:52:color=0x141414[c{i}]")
        filt.append("[c0][c1][c2]vstack=inputs=3[v]")
        dst = out / "cover_crops.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins,
                        "-filter_complex", ";".join(filt), "-map", "[v]", str(dst)], check=True)
        # 在整帧上画出核心带，方便直接看有没有越界
        marked = out / "_crop_band.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f0), "-vf",
            f"drawbox=x=0:y={BAND_TOP}:w={W}:h={BAND_BOT-BAND_TOP}:color=#5FD3A8@0.9:t=6",
            "-frames:v", "1", str(marked)], check=True)
        print(f"{pid}   核心带 y {BAND_TOP}–{BAND_BOT}（画在 {marked.name}）")
        for name, _, y0, y1 in tiles:
            print(f"    {name:5} 保留 y {y0}–{y1}")
        print(f"    → {dst}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
