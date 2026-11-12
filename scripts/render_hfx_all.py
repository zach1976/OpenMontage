#!/usr/bin/env python3
"""串行重渲全部高频词（泰 16 + 越 15），输出 renders/<stem>_v<N+1>.mp4，不覆盖旧版本。
    python3 scripts/render_hfx_all.py [--only pid,pid]
"""
import json, re, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from tools.video.video_compose import VideoCompose

only = next((a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--only=")), None)
for proj in sorted((REPO / "projects").glob("*-1000-hfx-*")):
    if only and proj.name not in only:
        continue
    comp = proj / "composition"
    old = sorted(proj.glob("renders/*_v*.mp4"))
    stem = proj.name.replace("-", "_")
    vers = [int(m.group(1)) for p in old if (m := re.search(r"_v(\d+)\.mp4$", p.name))]
    out = proj / "renders" / f"{stem}_v{max(vers, default=0) + 1}.mp4"
    entry = VideoCompose()._stage_atelier_project((comp / "index.tsx").resolve(), REPO / "remotion-composer")
    print(f"RENDER {proj.name} → {out.name}", flush=True)
    r = subprocess.run(["npx", "remotion", "render", str(entry), "HF", str(out), f"--props={(comp / 'props.json').resolve()}",
                        f"--public-dir={(comp / 'public').resolve()}", "--codec", "h264", "--crf", "20",
                        "--pixel-format", "yuv420p", "--audio-codec", "aac", "--concurrency", "4", "--timeout=120000"],
                       cwd=REPO / "remotion-composer", capture_output=True, text=True)
    print(("DONE " if r.returncode == 0 else "FAIL ") + proj.name + ("" if r.returncode == 0 else r.stderr[-800:]), flush=True)
