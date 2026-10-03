#!/usr/bin/env python3
"""渲染一集 atelier（手写 Remotion 合成）的通用驱动。

为什么要这个脚本：atelier 渲染走的是 tools/video/video_compose.py 的 bespoke 分支，
它要 edit_decisions.bespoke 里那几个绝对路径。以前每集手写一份 edit_decisions.json，
路径写死、改个目录名就断。这里从 composition/props.json + artifacts/script.json
现算：cuts 按 props 的时间轴生成，bespoke 路径按项目目录拼。

    python3 scripts/atelier_render.py <project_id> <composition_id> <out_name> \
        [--art "这一集的美术方向一句话"]

产物：projects/<id>/renders/<out_name>.mp4 与 artifacts/edit_decisions.json。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def build_edit_decisions(proj: Path, comp_id: str, art: str, concurrency: int = 0) -> dict:
    props = json.loads((proj / "composition/props.json").read_text())
    script = json.loads((proj / "artifacts/script.json").read_text())
    labels = {s["id"]: s.get("label", s["id"]) for s in script["sections"]}

    cuts, t = [], 0.0
    def add(cid, sec, dur, reason):
        nonlocal t
        cuts.append({"id": cid, "source": f"composition:{comp_id}#{sec}",
                     "in_seconds": round(t, 3), "out_seconds": round(t + dur, 3),
                     "transition_in": "fade" if cuts else None,
                     "transition_out": "fade", "transition_duration": 0.27,
                     "reason": reason})
        t += dur

    add("sc00_cover", "cover", props["hook"]["dur"],
        "[封面 · 第一帧] frame 0 即成品，核心带 660–1260 内只有一句话")
    for i, c in enumerate(props["cards"], 1):
        add(f"sc{i:02d}_{c['id']}", c["id"], c["dur"],
            f"{c.get('thai') or c.get('vi')} / {c['zh']}｜{labels.get(c['id'], '')}")
    add("sc_reveal", "reveal", props["reveal"]["dur"],
        f"[反转] 落在一条可执行的规则上：「{props['reveal']['rule']}」")
    add("sc_outro", "outro", props["outro"]["dur"], "[片尾] app icon + CTA + 话题标签")
    for c in cuts:
        if c["transition_in"] is None:
            c.pop("transition_in")

    return {
        "version": "1.0",
        "renderer_family": "explainer-teacher",
        "render_runtime": "remotion",
        "composition_mode": "atelier",
        "cuts": cuts,
        "music": {"volume": props["bgm"]["volume"], "ducking": True},
        "subtitles": {"enabled": False},
        "bespoke": {
            "entry": str((proj / "composition/index.tsx").resolve()),
            "composition_id": comp_id,
            "props_path": str((proj / "composition/props.json").resolve()),
            "public_dir": str((proj / "composition/public").resolve()),
            "crf": 18,
            # 字体多的合成在机器忙时会撞上 Remotion 默认的 30s 每帧超时
            "timeout_ms": 180000,
            # 带 OffthreadVideo 底片的合成必须压并发：默认十几个 worker 会同时
            # 往同一支视频里 seek，互相把解码器拖死，表现为渲染几十分钟不出片。
            **({"concurrency": concurrency} if concurrency else {}),
            "art_direction": art,
        },
        "metadata": {
            "fps": props["fps"], "resolution": "1080x1920",
            "total_seconds": props["totalSeconds"],
            "safe_area": "文字全部落在 y=240–1380",
            "proposal_render_runtime": "remotion",
            "subtitles_reason": "卡面本身就是逐词大字，再叠字幕会打架",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_id"); ap.add_argument("composition_id"); ap.add_argument("out_name")
    ap.add_argument("--art", default="")
    ap.add_argument("--concurrency", type=int, default=0,
                    help="0=不指定；带视频底片的合成建议 2")
    ap.add_argument("--use-existing", action="store_true",
                    help="沿用项目已审批的 edit_decisions，不按通用卡片结构重建")
    a = ap.parse_args()

    proj = REPO / "projects" / a.project_id
    if not proj.exists():
        print(f"没有这个项目：{proj}", file=sys.stderr); return 1

    ed_path = proj / "artifacts/edit_decisions.json"
    art = a.art
    if not art and ed_path.exists():
        art = json.loads(ed_path.read_text()).get("bespoke", {}).get("art_direction", "")
    if a.use_existing:
        ed = json.loads(ed_path.read_text())
    else:
        ed = build_edit_decisions(proj, a.composition_id, art or "（未填美术方向）", a.concurrency)
        ed_path.write_text(json.dumps(ed, ensure_ascii=False, indent=2), encoding="utf-8")

    # 音频要在 public/audio 下才被 staticFile 找到
    src, dst = proj / "assets/audio", proj / "composition/public/audio"
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*_x.mp3"):
        (dst / f.name).write_bytes(f.read_bytes())

    from tools.video.video_compose import VideoCompose  # noqa: E402
    out = proj / "renders" / f"{a.out_name}.mp4"
    out.parent.mkdir(exist_ok=True)
    proposal_path = proj / "artifacts/proposal_packet.json"
    proposal = json.loads(proposal_path.read_text()) if proposal_path.exists() else None
    res = VideoCompose().execute({"operation": "render", "edit_decisions": ed,
                                  "proposal_packet": proposal, "output_path": str(out)})
    if not res.success:
        print("渲染失败：", res.error, file=sys.stderr); return 2
    print(f"✓ {out}  ({out.stat().st_size/1e6:.1f}MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
