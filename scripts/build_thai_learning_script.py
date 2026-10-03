#!/usr/bin/env python3
"""Convert a reviewed episode_source.json into the canonical script artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_id")
    args = parser.parse_args()
    project = REPO / "projects" / args.project_id
    source = json.loads((project / "artifacts" / "episode_source.json").read_text())
    items = source["items"]
    cover_end = float(source["render_config"].get("cover_end", 2.4))
    card_seconds = float(source["render_config"].get("minimum_card_seconds", 3.4))
    sections = []
    units = []
    cursor = cover_end
    prefix = source.get("unit_prefix", "ep01")
    for i, item in enumerate(items, start=1):
        sid = f"ep01-item{i:02d}"
        end = cursor + card_seconds
        sections.append({
            "id": sid,
            "label": item["chinese"],
            "text": f"{item['thai']} → {item['chinese']}",
            "start_seconds": round(cursor, 3),
            "end_seconds": round(end, 3),
            "speaker_directions": "泰语先念，中文紧接；不留答题空白。",
            "delivery_cues": {"pace": "brisk", "energy": source["voice_energy"], "emphasis_words": [item["thai"]], "pause_after_seconds": 0.2},
            "enhancement_cues": [{"type": "animation", "description": f"第{i}张中央信息卡弹入并高亮。", "timestamp_seconds": round(cursor, 3)}],
        })
        units.extend([
            {"id": f"{prefix}_{i:02d}_th", "section": sid, "lang": "th", "text": item["thai"]},
            {"id": f"{prefix}_{i:02d}_zh", "section": sid, "lang": "zh", "text": item["spoken_chinese"]},
        ])
        cursor = end
    script = {
        "version": "1.0",
        "title": source["title"],
        "total_duration_seconds": round(cursor + float(source["render_config"].get("outro_seconds", 3.5)), 3),
        "voice_performance": {
            "performance_intent": source["performance_intent"],
            "pacing_profile": "energetic",
            "energy_curve": source["energy_curve"],
            "pause_policy": "泰语与中文之间0.16秒，词条之间不超过0.4秒。",
            "sample_section_id": "ep01-item01",
            "provider_notes": {"edge": "泰语Premwadee常速，中文Xiaoxiao常速；依靠分段控制停顿。"},
        },
        "sections": sections,
        "metadata": {
            "batch_status": "template_episode_ready",
            "planned_episode_count": source["planned_episode_count"],
            "render_config": source["render_config"],
            "tts": {"engine": "edge", "voices": {"th": "th-TH-PremwadeeNeural", "zh": "zh-CN-XiaoxiaoNeural"}, "rates": {"th": "+0%", "zh": "+0%"}},
            "tts_units": units,
            "items": [{k: v for k, v in item.items() if k != "spoken_chinese"} for item in items],
        },
    }
    (project / "artifacts" / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2))
    print(project / "artifacts" / "script.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
