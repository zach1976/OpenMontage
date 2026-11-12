#!/usr/bin/env python3
"""Build one canonical batch script from reviewed per-episode source files."""

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
    source_dir = project / "artifacts" / "episodes"
    sources = [json.loads(p.read_text()) for p in sorted(source_dir.glob("ep*.json"))]
    if not sources:
        raise FileNotFoundError(f"No episode sources in {source_dir}")

    target_lang = sources[0].get("target_lang", "th")
    if any(s.get("target_lang", "th") != target_lang for s in sources):
        raise ValueError("A batch must use one target language")
    target_label = "越南语" if target_lang == "vi" else "泰语"
    target_voice = "vi-VN-HoaiMyNeural" if target_lang == "vi" else "th-TH-PremwadeeNeural"
    brand = "越南语千词" if target_lang == "vi" else "泰语千词"
    country = "越南" if target_lang == "vi" else "泰国"

    sections: list[dict] = []
    units: list[dict] = []
    episodes: list[dict] = []
    timeline_cursor = 0.0
    for source in sources:
        episode_id = source["id"]
        render = source["render_config"]
        hook_section_id = f"{episode_id}-hook"
        episode_sections: list[str] = [hook_section_id]
        local_cursor = float(render.get("cover_end", 2.4))
        card_seconds = float(render.get("minimum_card_seconds", 3.5))
        sections.append({
            "id": hook_section_id,
            "label": "开场引导",
            "text": render["hook"],
            "start_seconds": round(timeline_cursor, 3),
            "end_seconds": round(timeline_cursor + local_cursor, 3),
            "speaker_directions": "晓晓中文声，直接朗读本集标题，明快自然。",
            "delivery_cues": {"pace": "brisk", "energy": "medium-high", "emphasis_words": [render["topic"]], "pause_after_seconds": 0.25},
            "enhancement_cues": [{"type": "animation", "description": "封面标题保持完整可读。", "timestamp_seconds": round(timeline_cursor, 3)}],
        })
        units.append({
            "id": f"{episode_id}_hook_zh",
            "section": hook_section_id,
            "lang": "zh",
            "text": render.get("spoken_hook", render["hook"]),
        })
        # 实拍招牌（2026-11-11）：封面后先看整张海报，结尾对着整张海报再读一遍
        if render.get("overview"):
            units.append({"id": f"{episode_id}_overview_zh", "section": hook_section_id, "lang": "zh", "text": render["overview"]["say"]})
        if render.get("poster_review"):
            units.append({"id": f"{episode_id}_review_intro_zh", "section": hook_section_id, "lang": "zh", "text": render["poster_review"]["say"]})
        episode_items = [dict(item, phase="lesson") for item in source["items"]]
        episode_items.extend(dict(item, phase="analysis") for item in source.get("analysis_items", []))
        for i, item in enumerate(episode_items, start=1):
            sid = f"{episode_id}-item{i:02d}"
            episode_sections.append(sid)
            end = timeline_cursor + local_cursor + card_seconds
            sections.append({
                "id": sid,
                "label": ("常用词分析：" if item.get("phase") == "analysis" else "") + item["chinese"],
                "text": f"{item['thai']} → {item['chinese']}",
                "start_seconds": round(timeline_cursor + local_cursor, 3),
                "end_seconds": round(end, 3),
                "speaker_directions": f"{target_label}先念，中文紧接；不留答题空白。",
                "delivery_cues": {"pace": "brisk", "energy": source.get("voice_energy", "medium-high"), "emphasis_words": [item["thai"]], "pause_after_seconds": 0.2},
                "enhancement_cues": [{"type": "animation", "description": f"第{i}张中央信息卡弹入并高亮。", "timestamp_seconds": round(timeline_cursor + local_cursor, 3)}],
            })
            units.extend([
                {"id": f"{episode_id}_{i:02d}_th", "section": sid, "lang": target_lang, "text": item["thai"]},
                {"id": f"{episode_id}_{i:02d}_zh", "section": sid, "lang": "zh", "text": item.get("spoken_chinese", item["chinese"])},
            ])
            for word_index, word in enumerate(item.get("breakdown", []), start=1):
                units.extend([
                    {"id": f"{episode_id}_{i:02d}_word{word_index:02d}_th", "section": sid, "lang": target_lang, "text": word["thai"]},
                    {"id": f"{episode_id}_{i:02d}_word{word_index:02d}_zh", "section": sid, "lang": "zh", "text": word.get("spoken_chinese", word["chinese"])},
            ])
            local_cursor += card_seconds
        recap_words = source.get("recap_words", [])
        if recap_words:
            recap_sid = f"{episode_id}-recap"
            episode_sections.append(recap_sid)
            recap_seconds = float(render.get("recap_seconds", 10.0))
            sections.append({
                "id": recap_sid,
                "label": "核心词复习",
                "text": source.get("recap_intro", "最后，核心词再来一遍。"),
                "start_seconds": round(timeline_cursor + local_cursor, 3),
                "end_seconds": round(timeline_cursor + local_cursor + recap_seconds, 3),
                "speaker_directions": f"中文简短引入；随后每个{target_label}词先念，再念中文。",
                "delivery_cues": {"pace": "brisk", "energy": "clear", "pause_after_seconds": 0.2},
                "enhancement_cues": [{"type": "animation", "description": "核心词逐个高亮复听。", "timestamp_seconds": round(timeline_cursor + local_cursor, 3)}],
            })
            units.append({"id": f"{episode_id}_recap_intro_zh", "section": recap_sid, "lang": "zh", "text": source.get("recap_intro", "最后，核心词再来一遍。")})
            for word_index, word in enumerate(recap_words, start=1):
                units.extend([
                    {"id": f"{episode_id}_recap_word{word_index:02d}_th", "section": recap_sid, "lang": target_lang, "text": word["thai"]},
                    {"id": f"{episode_id}_recap_word{word_index:02d}_zh", "section": recap_sid, "lang": "zh", "text": word.get("spoken_chinese", word["chinese"])},
                ])
            local_cursor += recap_seconds
        local_duration = local_cursor + float(render.get("outro_seconds", 3.5))
        episodes.append({
            "id": episode_id,
            "title": source["title"],
            "render_config": render,
            "items": [{k: v for k, v in item.items() if k != "spoken_chinese"} for item in episode_items],
            "recap_words": recap_words,
            "recap_intro": source.get("recap_intro"),
            "section_ids": episode_sections,
            "nominal_duration_seconds": round(local_duration, 3),
        })
        timeline_cursor += local_duration

    units.append({
        "id": "series_outro_zh",
        "section": "series-outro-shared",
        "lang": "zh",
        "text": f"{brand}，在{country}生活够用了。",
    })

    script = {
        "version": "1.0",
        "title": sources[0]["series_title"],
        "total_duration_seconds": round(timeline_cursor, 3),
        "voice_performance": {
            "performance_intent": f"{target_label}先念、中文紧接，像短视频教学口播，清楚但不拖沓。",
            "pacing_profile": "energetic",
            "energy_curve": "开场明快，逐条稳定推进，收尾利落。",
            "pause_policy": f"{target_label}与中文之间0.16秒，词条之间不超过0.4秒。",
            "sample_section_id": episodes[0]["section_ids"][0],
            "provider_notes": {"edge": f"{target_label}{target_voice}常速，中文Xiaoxiao常速；依靠分段控制停顿。"},
        },
        "sections": sections,
        "metadata": {
            "batch_status": "full_batch_script_ready",
            "planned_episode_count": len(sources),
            "outro_slogan": f"{brand}，在{country}生活够用了。",
            "target_lang": target_lang,
            "tts": {"engine": "edge", "voices": {target_lang: target_voice, "zh": "zh-CN-XiaoxiaoNeural"}, "rates": {target_lang: "+0%", "zh": "+0%"}},
            "tts_units": units,
            "episodes": episodes,
        },
    }
    output = project / "artifacts" / "script.json"
    output.write_text(json.dumps(script, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"script": str(output), "episodes": len(episodes), "tts_units": len(units)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
