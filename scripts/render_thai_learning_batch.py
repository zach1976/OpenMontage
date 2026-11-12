#!/usr/bin/env python3
"""Render every assembled ThaiLearningCards episode, resuming completed files."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_id")
    parser.add_argument("--episode")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    project = REPO / "projects" / args.project_id
    props_files = sorted((project / "composition").glob("ep*/props.json"))
    if args.episode:
        props_files = [p for p in props_files if p.parent.name == args.episode]
    renders = project / "renders"
    renders.mkdir(parents=True, exist_ok=True)
    for props in props_files:
        eid = props.parent.name
        output = renders / f"{eid}.mp4"
        if not args.force and output.exists() and output.stat().st_size > 100_000:
            print(f"SKIP {eid} {output.stat().st_size}", flush=True)
            continue
        payload = json.dumps(json.loads(props.read_text()), ensure_ascii=False, separators=(",", ":"))
        print(f"RENDER {eid}", flush=True)
        result = subprocess.run([
            "npx", "remotion", "render", "src/index.tsx", "ThaiLearningCards", str(output),
            "--props", payload, "--codec", "h264", "--crf", "20", "--pixel-format", "yuv420p",
            "--audio-codec", "aac", "--concurrency", "4", "--timeout", "120000",  # 与别的渲染并行时单帧会超过默认 30s
        ], cwd=REPO / "remotion-composer", capture_output=True, text=True)
        if result.returncode != 0:
            print((result.stdout + "\n" + result.stderr)[-5000:], flush=True)
            result.check_returncode()
        print(f"DONE {eid} {output.stat().st_size}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
