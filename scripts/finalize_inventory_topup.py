#!/usr/bin/env python3
"""库存补齐批次的收尾：封面 + 横屏预览 + 旁白有声自查。

- renders/epNN_cover.jpg            第 0 帧（平台就拿它当封面）
- renders/epNN_cover_landscape.jpg  16:9 版位只剩 y 656–1264，裁出来预览
- 旁白自查：量**纯人声轨** narration.wav（不含垫乐）里每一段 speechRanges 的 mean_volume，
  低于 −40dB 就判「没响」。量人声轨而不是成片，是因为成片里垫乐会把静音段抬高，
  固定阈值分不清；人声轨里没有垫乐，静音就是静音。

    python3 scripts/finalize_inventory_topup.py <project_id>
退出码 2 = 有没响的段。
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def mean_db(mp4: Path, start: float, dur: float) -> float:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(mp4),
                        "-vn", "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
    return float(m.group(1)) if m else -99.0


def main() -> int:
    project = REPO / "projects" / sys.argv[1]
    bad = 0
    for props_path in sorted((project / "composition").glob("ep*/props.json")):
        eid = props_path.parent.name
        mp4 = project / "renders" / f"{eid}.mp4"
        if not mp4.exists():
            print(f"  · {eid} 未渲染")
            continue
        props = json.loads(props_path.read_text())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-frames:v", "1", "-q:v", "2",
                        str(project / "renders" / f"{eid}_cover.jpg")], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-frames:v", "1", "-q:v", "3",
                        "-vf", "crop=1080:608:0:656", str(project / "renders" / f"{eid}_cover_landscape.jpg")], check=True)
        voice = REPO / "remotion-composer" / "public" / props["narrationSrc"]
        quiet = []
        for r in props.get("speechRanges", []):
            d = mean_db(voice, r["start"], max(0.2, r["end"] - r["start"]))
            if d < -40:
                quiet.append(f"{r['start']:.1f}s({d:.1f}dB)")
        status = "✓" if not quiet else "✗ 没响：" + " ".join(quiet)
        bad += bool(quiet)
        print(f"  {eid} {props['durationSeconds']:.1f}s {status}")
    return 2 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
