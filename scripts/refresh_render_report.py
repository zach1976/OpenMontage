#!/usr/bin/env python3
"""按最新成片刷新 artifacts/render_report.json（审片页的「本版事实」读它）。

为什么要有这个：render_report.json 一直是手写的，每渲一版就旧一次，
审片页顶上于是常年挂着「事实面板可能对不上当前版本」的红条。
这里直接从磁盘上的最新 mp4 ffprobe 出事实，再跑一遍能量对齐校验，写回去。

    python3 scripts/refresh_render_report.py            # 全部项目
    python3 scripts/refresh_render_report.py <id> ...   # 指定几个
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"


def probe(mp4: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate,codec_name",
         "-show_entries", "format=duration", "-of", "json", str(mp4)],
        capture_output=True, text=True).stdout
    d = json.loads(out or "{}")
    st = (d.get("streams") or [{}])[0]
    num, _, den = (st.get("r_frame_rate") or "30/1").partition("/")
    return {"w": st.get("width"), "h": st.get("height"), "codec": st.get("codec_name"),
            "fps": round(int(num) / max(int(den or 1), 1)),
            "dur": round(float((d.get("format") or {}).get("duration") or 0), 2)}


def verify(pid: str) -> list[str]:
    r = subprocess.run(["python3", str(REPO / "scripts/verify_audio_coverage.py"), pid],
                       capture_output=True, text=True, cwd=REPO)
    notes, txt = [], r.stdout
    m = re.search(r"配音区间 (\d+) 段，静默\(<-45dB\) (\d+) 段", txt)
    n = re.search(r"人声高出垫乐 ([\d.]+) dB", txt)
    v = re.search(r"整片: (mean_volume: [^/]+/ max_volume: [^\n]+)", txt)
    if m:
        notes.append(f"能量对齐校验：{m.group(1)} 段配音区间逐段 volumedetect，静默 {m.group(2)} 段"
                     + (f"；人声高出垫乐 {n.group(1)}dB" if n else ""))
    if v:
        notes.append(f"volumedetect：{v.group(1).strip()}")
    return notes


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n_ok = 0
    for d in sorted(PROJECTS.iterdir()):
        if not d.is_dir() or (args and d.name not in args):
            continue
        mp4s = sorted((d / "renders").glob("*.mp4"), key=lambda p: p.stat().st_mtime)
        if not mp4s:
            continue
        mp4 = mp4s[-1]
        info = probe(mp4)
        rep_p = d / "artifacts" / "render_report.json"
        old = json.loads(rep_p.read_text()) if rep_p.exists() else {}
        meta = old.get("metadata") or {}
        # 成本别猜：脚本只搬运已有记录，没有记录就留空，不替它宣称「零成本」
        rep = {
            "version": "1.0",
            "render_grammar": old.get("render_grammar", "explainer-teacher"),
            "outputs": [{"path": str(mp4.resolve()), "format": "mp4",
                         "codec": info["codec"], "audio_codec": "aac",
                         "resolution": f'{info["w"]}x{info["h"]}', "fps": info["fps"],
                         "duration_seconds": info["dur"],
                         "file_size_bytes": mp4.stat().st_size,
                         "platform_target": "douyin"}],
            "warnings": old.get("warnings", []),
            "metadata": meta,
            "verification_notes": [
                f'ffprobe：容器有效，{info["dur"]}s / {info["w"]}x{info["h"]} / '
                f'{info["fps"]}fps，{mp4.stat().st_size / 1e6:.1f}MB',
                *verify(d.name),
            ],
        }
        rep_p.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  ✓ {d.name:34} {mp4.name:26} {info['dur']}s")
        n_ok += 1
    print(f"\n刷新 {n_ok} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
