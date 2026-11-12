#!/usr/bin/env python3
"""把 ChatGPT 生成的 7 张蘸酱图裁成卡片照片区的比例（804×300，按 2 倍存 1608×600），
存进项目 assets/images 并拷到 Remotion public。

    python3 scripts/import_sauce_photos.py <ChatGPT 出图目录>
"""
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PID = "thai-food-sauce-202611"
NAMES = ["01_nam_jim_kai", "02_jaew", "03_tao_jiao", "04_seafood", "05_tofu", "06_luk_chin", "07_nam_pla_wan"]

src_dir = Path(sys.argv[1])
assets = REPO / "projects" / PID / "assets" / "images"
public = REPO / "remotion-composer" / "public" / "series" / PID / "ep01"
assets.mkdir(parents=True, exist_ok=True)
public.mkdir(parents=True, exist_ok=True)
for i, name in enumerate(NAMES, 1):
    src = src_dir / f"{name}.png"
    shutil.copy2(src, assets / f"gpt_{name}.png")          # 原图留档
    out = assets / f"sauce_{i:02d}.jpg"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf",
                    "scale=1608:-2,crop=1608:600:0:(ih-600)/2", "-q:v", "2", str(out)], check=True)
    shutil.copy2(out, public / out.name)
    print(out.name)
