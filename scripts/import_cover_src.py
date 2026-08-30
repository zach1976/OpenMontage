#!/usr/bin/env python3
"""把 ChatGPT 生成的封面底图接进各集（只换封面那一帧，正片的空镜不动）。

底图放在 `projects/_shared/cover_src/`，文件名就是提示词末尾写死的那个。
这里做三件事：
  1. 拉到 1080×1920（生成出来是 941×1672，正好 9:16，只是尺寸小）。
  2. 量标题带（画面高度 39%–55%，即 y 760–1060）的平均亮度并报出来 ——
     白色大字压在那儿，这一带太亮就读不出来。**这是验收指标，不是装饰。**
  3. 拷进 `<project>/composition/public/img/cover.png` 并写进 props。

    python3 scripts/import_cover_src.py
"""
import json, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "projects" / "_shared" / "cover_src"

MAP = {
    "thai_zen_01_impermanence_cover.png": "thai-zen-01-impermanence-v2",
    "thai_zen_02_letgo_cover.png":        "thai-zen-02-letgo-v2",
    "thai_zen_03_calm_cover.png":         "thai-zen-03-calm-v2",
    "thai_zen_04_enough_cover.png":       "thai-zen-04-enough-v2",
    "thai_zen_05_beginagain_cover.png":   "thai-zen-05-beginagain-v2",
    "viet_zen_01_mainmai_cover.png":      "viet-zen-01-mainmai",
    "viet_zen_02_buongbo_cover.png":      "viet-zen-02-buongbo",
    "viet_zen_03_binhtinh_cover.png":     "viet-zen-03-binhtinh",
    "viet_zen_04_hanhphuc_cover.png":     "viet-zen-04-hanhphuc",
    "viet_zen_05_batdaulai_cover.png":    "viet-zen-05-batdaulai",
}
BAND_MAX = 90.0    # 标题带 YAVG 上限；超了白字压不住，得回去重出图或加压制


def band_luma(p: Path) -> tuple[float, float]:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p),
                          "-vf", "crop=iw:ih*0.16:0:ih*0.39,signalstats,metadata=print",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    y = re.search(r"lavfi\.signalstats\.YAVG=([\d.]+)", out)
    m = re.search(r"lavfi\.signalstats\.YMAX=([\d.]+)", out)
    return (float(y.group(1)) if y else -1.0, float(m.group(1)) if m else -1.0)


def main() -> int:
    bad = 0
    for fn, pid in MAP.items():
        src = SRC / fn
        if not src.exists():
            print(f"✗ 缺 {fn}", file=sys.stderr); bad += 1; continue
        proj = REPO / "projects" / pid
        dst = proj / "composition" / "public" / "img" / "cover.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                        "-vf", "scale=1080:1920:flags=lanczos", str(dst)], check=True)
        yavg, ymax = band_luma(dst)
        flag = "  ⚠ 标题带偏亮" if yavg > BAND_MAX else ""
        if yavg > BAND_MAX:
            bad += 1
        pp = proj / "composition" / "props.json"
        props = json.loads(pp.read_text())
        props["cover"] = "img/cover.png"
        pp.write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✓ {pid:28} 标题带 YAVG={yavg:5.1f} YMAX={ymax:5.1f}{flag}")
    print(f"\n上限 YAVG≤{BAND_MAX:.0f}（白字压在画面 39%–55% 那一带）")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
