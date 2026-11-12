#!/usr/bin/env python3
"""按各集上次渲染留下的 artifacts/edit_decisions.json（bespoke 段）原样重渲，输出下一个版本号。

为什么要这个脚本：改了共享底盘（例如 2026-10-21 品牌行去掉「app」）之后，
几十集要用**完全相同的参数**重渲一遍。各集的合成 ID、入口、props、public 目录都已经
记在 edit_decisions.json 里，不需要再逐集手写命令。

    python3 scripts/rerender_from_edit_decisions.py <project_id> [<project_id> ...]
    python3 scripts/rerender_from_edit_decisions.py --list ids.txt

每集：渲到 renders/<上一版主名>_v<N+1>.mp4，渲完核对片长与上一版相差 ≤0.15s、有音轨；
不过就删掉新文件并报失败，旧片不动。推送脚本永远取最新 mp4，所以失败的那集不会被误推。
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMPOSER = REPO / "remotion-composer"
sys.path.insert(0, str(REPO))
from tools.video.video_compose import VideoCompose  # noqa: E402


def probe(p: Path) -> tuple[float, bool]:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
                          "-of", "json", str(p)], capture_output=True, text=True).stdout
    d = json.loads(out)
    return float(d["format"]["duration"]), any(s.get("codec_type") == "audio" for s in d.get("streams", []))


def next_name(renders: Path) -> tuple[Path, Path]:
    mp4s = sorted(renders.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
    last = mp4s[-1]
    m = re.match(r"(.*)_v(\d+)$", last.stem)
    base, n = (m.group(1), int(m.group(2)) + 1) if m else (last.stem, 2)
    out = renders / f"{base}_v{n}.mp4"
    while out.exists():
        n += 1
        out = renders / f"{base}_v{n}.mp4"
    return last, out


def render(pid: str) -> bool:
    proj = REPO / "projects" / pid
    b = json.loads((proj / "artifacts/edit_decisions.json").read_text())["bespoke"]
    # 走 video_compose 官方的暂存：把 composition/ 下的源码按 mtime 拷进 remotion-composer/projects/<id>/。
    # 那里是一份**拷贝**，不是软链 —— 自己拼路径会渲到旧源码。
    entry = VideoCompose()._stage_atelier_project(Path(b["entry"]).resolve(), COMPOSER)
    last, out = next_name(proj / "renders")
    cmd = ["npx", "remotion", "render", str(entry), b["composition_id"], str(out),
           f"--props={Path(b['props_path']).resolve()}", f"--public-dir={Path(b['public_dir']).resolve()}"]
    for k, flag in (("concurrency", "--concurrency"), ("crf", "--crf"), ("scale", "--scale")):
        if b.get(k) is not None:
            cmd.append(f"{flag}={b[k]}")
    print(f"▶ {pid}  {last.name} → {out.name}", flush=True)
    r = subprocess.run(cmd, cwd=COMPOSER, capture_output=True, text=True)
    subprocess.run(["pkill", "-f", "chrome-headless-shell"], capture_output=True)
    if r.returncode != 0 or not out.exists():
        print(f"  ✗ 渲染失败\n{r.stderr[-1500:]}", flush=True)
        out.unlink(missing_ok=True)
        return False
    (d0, _), (d1, a1) = probe(last), probe(out)
    if abs(d0 - d1) > 0.15 or not a1:
        print(f"  ✗ 校验不过：片长 {d0:.2f}→{d1:.2f}s，音轨={a1}；已删新文件", flush=True)
        out.unlink(missing_ok=True)
        return False
    print(f"  ✓ {d1:.2f}s", flush=True)
    return True


def main() -> int:
    a = sys.argv[1:]
    ids = [l.strip() for l in Path(a[1]).read_text().splitlines() if l.strip()] if a[:1] == ["--list"] else a
    # 字体 delayRender 超时、offthread 解码中断都是偶发的：杀掉残留 chrome 后单独再试一次通常就过。
    bad = [p for p in ids if not render(p)]
    bad = [p for p in bad if not render(p)]
    print(f"\n完成 {len(ids) - len(bad)}/{len(ids)}" + (f"；失败：{' '.join(bad)}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
