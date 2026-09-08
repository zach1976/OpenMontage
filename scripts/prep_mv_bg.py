#!/usr/bin/env python3
"""把官方 MV 的一段切成 9:16 底片（模糊填充 + 去色 + 压暗），给「拆歌名」那一路用。

为什么要压这么狠：MV 是 16:9 的成品画面，直接铺到 1080×1920 会跟前景的教学文字抢；
底片的职责是给画面一点呼吸和「这是哪首歌」的暗示，不是主角。
做法与禅意系列的 prep_bg.py 一个思路，区别是这里要先做模糊填充补上下两条。

    python3 scripts/prep_mv_bg.py <src.mp4> <start_s> <dur_s> <out.mp4>
"""
import subprocess
import sys
from pathlib import Path

# 模糊填充：原片等比放大铺满 1080×1920 再重模糊当底，清晰的一层居中叠上去
VF = ("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
      "crop=1080:1920,gblur=sigma=42,eq=saturation=0.30:brightness=-0.10[bgl];"
      "[0:v]scale=1080:-2,gblur=sigma=1.6,eq=saturation=0.42:contrast=1.04[fg];"
      "[bgl][fg]overlay=(W-w)/2:(H-h)/2,"
      # 压暗：四角与上下更沉，中间留一点亮，字压得住
      "drawbox=x=0:y=0:w=1080:h=1920:color=black@0.42:t=fill")


def main() -> int:
    if len(sys.argv) != 5:
        print(__doc__); return 1
    src, start, dur, out = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4])
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", start, "-t", dur, "-i", src,
                    "-filter_complex", VF, "-an", "-r", "30",
                    "-c:v", "libx264", "-crf", "23", "-pix_fmt", "yuv420p",
                    # 每秒一个关键帧、恒定帧率。Remotion 的 OffthreadVideo 是按时间点
                    # 逐帧去抽的，关键帧太稀会让每次 seek 都要解一大段，
                    # 表现出来是渲染卡死在 "Fetching …/proxy?src=…mv_bg.mp4" 上
                    # （报错却写着 delayRender: cjk-fonts，很误导）。
                    "-g", "30", "-keyint_min", "30", "-sc_threshold", "0",
                    "-fps_mode", "cfr", str(out)], check=True)
    print(f"✓ {out}  ({out.stat().st_size/1e6:.1f}MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
