#!/usr/bin/env python3
"""把官方 MV 的一段切成 9:16 底片（模糊填充 + 去色 + 压暗），给「拆歌名」那一路用。

为什么要压这么狠：MV 是 16:9 的成品画面，直接铺到 1080×1920 会跟前景的教学文字抢；
底片的职责是给画面一点呼吸和「这是哪首歌」的暗示，不是主角。
做法与禅意系列的 prep_bg.py 一个思路，区别是这里要先做模糊填充补上下两条。

    python3 scripts/prep_mv_bg.py <src.mp4> <start_s> <dur_s> <out.mp4> [dim] [contrast]

`dim`（黑罩不透明度，默认 0.42）与 `contrast`（清晰层对比，默认 1.04）可调。
2026-09-10 用户看夜舞加长版：「整个画面太暗了」—— 压暗是三层叠出来的
（这里 0.42 + 组件里 0.22 罩 + 上下渐变 + 暗角），单看哪一层都不算狠，叠起来就闷。
禅意那批也踩过同一件事，结论一样：**先修明暗，再谈别的**。
调用方按需传参，别再改这里的默认值 —— 已经交付的几支还在用老数值。
"""
import subprocess
import sys
from pathlib import Path


def build_vf(dim: float, contrast: float) -> str:
    """模糊填充：原片等比放大铺满 1080×1920 再重模糊当底，清晰的一层居中叠上去。"""
    # 罩子越薄，底片本身就得越有层次，否则读作"糊掉的实拍"而不是"底纹"；
    # 所以提亮时对比要跟着往上走，暗部才不会连成一片。
    # 罩子薄了还得**把曝光抬起来**：这支 MV 是夜戏，只减黑罩只能让它从"黑"变成"灰黑"。
    bg_bright = -0.10 + (0.42 - dim) * 0.30
    fg_bright = (0.42 - dim) * 0.22
    return ("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,gblur=sigma=42,eq=saturation=0.30:brightness={bg_bright:.3f}[bgl];"
            "[0:v]scale=1080:-2,gblur=sigma=1.6,"
            f"eq=saturation=0.48:contrast={contrast:.3f}:brightness={fg_bright:.3f}[fg];"
            "[bgl][fg]overlay=(W-w)/2:(H-h)/2,"
            # 压暗：四角与上下更沉，中间留一点亮，字压得住
            f"drawbox=x=0:y=0:w=1080:h=1920:color=black@{dim:.3f}:t=fill")


def main() -> int:
    if len(sys.argv) not in (5, 6, 7):
        print(__doc__); return 1
    src, start, dur, out = sys.argv[1], sys.argv[2], sys.argv[3], Path(sys.argv[4])
    dim = float(sys.argv[5]) if len(sys.argv) > 5 else 0.42
    contrast = float(sys.argv[6]) if len(sys.argv) > 6 else 1.04
    VF = build_vf(dim, contrast)
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
