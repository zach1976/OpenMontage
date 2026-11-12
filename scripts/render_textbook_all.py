#!/usr/bin/env python3
"""串行重渲教材带货（泰 20 + 越 15），输出下一个版本号的 mp4，不覆盖旧版。
    python3 scripts/render_textbook_all.py [--only=pid,pid]
"""
import re, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from tools.video.video_compose import VideoCompose

only = next((a.split("=", 1)[1].split(",") for a in sys.argv[1:] if a.startswith("--only=")), None)
projs = sorted(REPO.glob("projects/thai-book-jichu-*")) + sorted(REPO.glob("projects/viet-book-coso-*"))
for proj in projs:
    comp = proj / "composition"
    if (only and proj.name not in only) or not (comp / "Root.tsx").exists():
        continue
    cid = re.search(r'id="([^"]+)"', (comp / "Root.tsx").read_text()).group(1)
    mp4s = [p for p in proj.glob("renders/*.mp4") if "cover" not in p.name]
    pre = "book-v" if proj.name.startswith("thai") else "v"
    vers = [int(m.group(1)) for p in mp4s if (m := re.fullmatch(rf"{re.escape(pre)}(\d+)\.mp4", p.name))]
    out = proj / "renders" / f"{pre}{max(vers, default=0) + 1}.mp4"
    entry = VideoCompose()._stage_atelier_project((comp / "index.tsx").resolve(), REPO / "remotion-composer")
    print(f"RENDER {proj.name} → {out.name}", flush=True)
    r = subprocess.run(["npx", "remotion", "render", str(entry), cid, str(out), f"--props={(comp / 'props.json').resolve()}",
                        f"--public-dir={(comp / 'public').resolve()}", "--codec", "h264", "--crf", "20",
                        "--pixel-format", "yuv420p", "--audio-codec", "aac", "--concurrency", "4", "--timeout=120000"],
                       cwd=REPO / "remotion-composer", capture_output=True, text=True)
    if r.returncode == 0:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out), "-frames:v", "1", "-q:v", "2",
                        str(out.with_name(out.stem + "_cover.jpg"))])
    print(("DONE " if r.returncode == 0 else "FAIL ") + proj.name + ("" if r.returncode == 0 else r.stderr[-800:]), flush=True)
