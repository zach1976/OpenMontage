#!/usr/bin/env python3
"""分段渲染 atelier 合成再无损拼接 —— 整片长任务渲不动时的出片路径。

为什么要它：Remotion 的本地静态服务在长任务里会中途挂掉，一挂，OffthreadVideo
取帧和字体请求一起吊住，表现出来是 `Could not extract frame from compositor:
Request closed` 外加 `delayRender(...) not cleared`。**字体超时只是后果，不是原因**，
所以调 --timeout / --concurrency 都没用（实测四次都固定停在同一秒）。
分段渲染每段只开一次浏览器，跑完就回收，稳定通过。

    python3 scripts/render_chunked.py <project_id> <composition_id> <out_name> [--chunk 700]

读 artifacts/edit_decisions.json 的 bespoke 段拿入口与 public 目录，产物落在
projects/<id>/renders/<out_name>.mp4。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMPOSER = REPO / "remotion-composer"


def probe(p: Path) -> float:
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return float(o.stdout.strip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_id")
    ap.add_argument("composition_id")
    ap.add_argument("out_name")
    ap.add_argument("--chunk", type=int, default=700, help="每段帧数")
    ap.add_argument("--concurrency", type=int, default=2)
    args = ap.parse_args()

    proj = REPO / "projects" / args.project_id
    ed = json.loads((proj / "artifacts" / "edit_decisions.json").read_text())
    bes = ed["bespoke"]
    props_path = Path(bes["props_path"])
    props = json.loads(props_path.read_text())
    total, last = props["totalFrames"], props["totalFrames"] - 1

    tmp = proj / "renders" / "_chunks"
    tmp.mkdir(parents=True, exist_ok=True)
    for old in tmp.glob("*.mp4"):
        old.unlink()

    parts, t0 = [], time.time()
    for i, a in enumerate(range(0, total, args.chunk)):
        b = min(a + args.chunk - 1, last)
        out = tmp / f"c{i:02d}.mp4"
        r = subprocess.run(
            ["npx", "remotion", "render", bes["entry"], args.composition_id, str(out),
             f"--props={props_path}", f"--public-dir={bes['public_dir']}",
             f"--crf={bes.get('crf', 18)}", f"--concurrency={args.concurrency}",
             f"--frames={a}-{b}"],
            cwd=COMPOSER, capture_output=True, text=True)
        if r.returncode != 0 or not out.exists():
            print(f"  段 {i} 失败（帧 {a}-{b}）：\n{r.stderr[-800:]}")
            return 1
        parts.append(out)
        print(f"  段 {i}: 帧 {a}-{b}  ✓  {time.time() - t0:.0f}s", flush=True)

    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    final = proj / "renders" / f"{args.out_name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c", "copy", str(final)], cwd=tmp, check=True)
    for p in parts:
        p.unlink()
    lst.unlink()
    tmp.rmdir()

    got = probe(final)
    print(f"\n✓ {final.relative_to(REPO)}  {got:.2f}s"
          f"（props 期望 {props['totalSeconds']}s）  {final.stat().st_size/1e6:.1f}MB"
          f"  {len(parts)} 段  用时 {time.time() - t0:.0f}s")
    if abs(got - props["totalSeconds"]) > 0.6:
        print("  ⚠️  拼接后时长与 props 差得多，检查分段边界")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
