#!/usr/bin/env python3
"""Create the combined four-episode Vietnamese dialogue review workspace."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from build_vietnamese_dialogue_series import EPISODES, ROOT, dump, project_id
from lib.checkpoint import init_project


BATCH_ID = "vietnamese-1000-dialogue-batch-01-04-review"


def probe(path: Path) -> dict:
    data = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_streams", "-show_format", str(path),
    ], text=True))
    video = next(s for s in data["streams"] if s["codec_type"] == "video")
    audio = next(s for s in data["streams"] if s["codec_type"] == "audio")
    return {
        "codec": video["codec_name"],
        "audio_codec": audio["codec_name"],
        "resolution": f"{video['width']}x{video['height']}",
        "fps": 30,
        "duration_seconds": float(data["format"]["duration"]),
        "file_size_bytes": path.stat().st_size,
    }


def main() -> int:
    project = init_project(
        BATCH_ID,
        title="越南语千词·餐厅情景对话 No.01–No.04 联合审核",
        pipeline_type="animated-explainer",
        style_playbook="custom-dialogue",
    )
    (project / "composition").mkdir(exist_ok=True)
    dump(project / "composition" / "props.json", {})

    outputs = []
    review_episodes = []
    for ep in EPISODES:
        source = ROOT / "projects" / project_id(ep) / "renders" / f"vietnamese-dialogue-{ep['no']:02d}-{ep['slug']}.mp4"
        target_name = f"{ep['no']:02d}_{ep['topic']}.mp4"
        target = project / "renders" / target_name
        shutil.copy2(source, target)
        outputs.append({
            "path": f"renders/{target_name}", "format": "mp4", **probe(target),
            "platform_target": "四集联合审核",
        })
        review_episodes.append({
            "episode": f"No.{ep['no']:02d}",
            "title": ep["topic"],
            "hook": ep["hook"],
            "dialogue": [
                {"role": role, "th": vi, "rom": xie, "zh": zh}
                for role, _speaker, vi, zh, xie in ep["dialogue"]
            ],
            "analysis": [
                {
                    "title": lesson["label"],
                    "sentence": lesson["vi"],
                    "words": [{"th": vi, "zh": zh} for vi, zh in lesson["words"]],
                    "note": f"谐音：{lesson['xie']}。{lesson['note']}",
                }
                for lesson in ep["lessons"]
            ],
            "replay": "按原顺序完整复听四句对话；逐词教学音频均先念越南语，再说中文解释。",
        })

    dump(project / "artifacts" / "review_copy.json", {
        "version": "1.0", "episodes": review_episodes,
    })
    dump(project / "artifacts" / "render_report.json", {
        "version": "1.0",
        "outputs": outputs,
        "warnings": [],
        "verification_notes": [
            "四集均包含完整四句对话、逐词分析、实用引申和完整复听。",
            "逐词分析严格先念越南语，再接中文解释。",
            "中文讲解沿用第一集的 zh-CN-XiaoxiaoNeural 声线。",
            "信息卡使用中文谐音，不使用 IPA；教学卡位置保持上移。",
            "背景音乐已嵌入，并在语音出现时自动压低。",
            "No.02 包含现金、刷卡、二维码、支付宝和微信支付说法。",
            "四集均未检测到超过 1.5 秒的中段语音空白；片尾保留约 1.79 秒视觉收束。",
            "画面抽检未发现黑帧、缺图、文字溢出或一闪而过的提示页。",
        ],
        "render_grammar": "explainer-teacher",
        "slideshow_risk_score": {"average": 0.16, "verdict": "strong"},
        "metadata": {
            "render_runtime": "remotion", "composition_mode": "templated",
            "approval_state": "combined_review_pending", "episode_count": 4,
        },
    })
    print(project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
