#!/usr/bin/env python3
"""Prepare the source-led episode workspaces for approved Pinkfong alphabet lessons.

This only builds the verified script, source excerpts, stills, and draft pipeline
artifacts. Narration synthesis and rendering happen in later pipeline stages.
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import init_project

PROJECTS = ROOT / "projects"
PARENT = PROJECTS / "thai-alphabet-pinkfong-three-letter"
SERIES = PROJECTS / "thai-alphabet-pinkfong-lesson-batch"
FIRST = PROJECTS / "thai-alphabet-pinkfong-01-lesson"
SOURCE = PARENT / "assets/video/source.mp4"
SOURCE_URL = "https://www.youtube.com/watch?v=pxLHURprYuI"


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def probe(path: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                             "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def run_ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, args)], check=True)


def mnemonic_meaning(item: dict) -> str:
    return next((meaning for thai, meaning in item["words"] if thai == item["mnemonic"]), item["words"][0][1])


def relation(item: dict) -> tuple[str, str]:
    if item.get("note"):
        if item["letter"] == "ฅ":
            return item["note"], "这句用传统字母记人。现在写人，开头用的是上一句的字母。"
        return item["note"], "这是传统字母。现代写这个词时，通常使用另一个字母。"
    letter, mnemonic = item["letter"], item["mnemonic"]
    meaning = mnemonic_meaning(item).split("，", 1)[0]
    first_consonant = mnemonic[1] if mnemonic and mnemonic[0] in "เแโใไ" and len(mnemonic) > 1 else mnemonic[0]
    if first_consonant == letter:
        return f"{letter} 是 {mnemonic}（{meaning}）的首个辅音。", f"{meaning}这个泰语词，开头辅音就是本句字母。"
    if letter in mnemonic:
        return f"{letter} 出现在 {mnemonic}（{meaning}）里，不在词首。", f"{meaning}这个泰语词里，也能找到本句字母。"
    raise ValueError(f"Mnemonic does not contain its letter: {letter} {mnemonic}")


def make_words(project: Path, letter_index: int, item: dict, start: float, end: float) -> list[dict]:
    """Cut each sung word from its verified line; weights follow visible word lengths."""
    out = project / "public/song_words"
    out.mkdir(parents=True, exist_ok=True)
    words = item["words"]
    weights = [max(2, len(th)) for th, _ in words]
    total = sum(weights)
    line_duration = end - start
    sung_start = start + min(0.27, line_duration * 0.15)
    sung_duration = end - sung_start
    cursor = sung_start
    result = []
    for index, ((thai, meaning), weight) in enumerate(zip(words, weights)):
        word_end = end if index == len(words) - 1 else cursor + sung_duration * weight / total
        word_id = f"l{letter_index:02d}_w{index}"
        clip = out / f"{word_id}_song.mp3"
        clip_duration = word_end - cursor
        fade_end = max(0.02, clip_duration - 0.04)
        run_ffmpeg("-ss", f"{cursor:.3f}", "-t", f"{clip_duration:.3f}", "-i", SOURCE,
                   "-vn", "-af", f"afade=t=in:st=0:d=0.02,afade=t=out:st={fade_end:.3f}:d=0.02,"
                   "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-b:a", "192k", clip)
        result.append({"id": word_id, "th": thai, "zh": meaning,
                       "song_start_seconds": round(cursor, 3), "song_end_seconds": round(word_end, 3),
                       "song_duration_seconds": round(probe(clip), 3)})
        cursor = word_end
    return result


def one(episode: int, timeline: list, lyric_items: list) -> None:
    group = timeline[(episode - 1) * 3:episode * 3]
    entries = lyric_items[(episode - 1) * 3 - 3:episode * 3 - 3]
    assert len(group) == len(entries) and 2 <= len(group) <= 3
    for source, item in zip(group, entries):
        assert source[0] == item["letter"]

    project_id = f"thai-alphabet-pinkfong-{episode:02d}-lesson"
    project = PROJECTS / project_id
    letters_label = " ".join(x["letter"] for x in entries)
    title = f"泰文字母歌 第{episode:02d}集｜{letters_label} 逐词教学"
    init_project(project_id, title=title, pipeline_type="hybrid")
    public = project / "public"
    public.mkdir(parents=True, exist_ok=True)
    source_clip = PARENT / f"assets/video/letter_group_{episode:02d}_cover.mp4"
    shutil.copy2(source_clip, public / "song.mp4")
    shutil.copy2(FIRST / "public/app_icon.png", public / "app_icon.png")
    shutil.copy2(FIRST / "public/app_home_zh.png", public / "app_home_zh.png")

    count_text = "三个" if len(group) == 3 else "两个"
    intro = f"泰国小朋友都会唱的字母歌，这{count_text}字母你听得懂吗？"
    bridge = f"下面逐词听懂这{count_text}字母。"
    outro = "想学泰文，就用学泰文字母。"
    sections = []
    units = []
    song_letters = []
    cursor = 0.0
    group_song_seconds = probe(public / "song.mp4")
    section_estimates = [("intro", "引导", 5.0), ("song", "原唱", group_song_seconds),
                         ("bridge", "过渡", 2.5)]
    word_records = []
    for local_index, (source, item) in enumerate(zip(group, entries)):
        letter_index = (episode - 1) * 3 + local_index + 1
        letter_id = f"l{letter_index:02d}"
        image_name = f"letter_{letter_index:02d}.jpg"
        still_time = source[1] + min(0.75, (source[2] - source[1]) * 0.45)
        run_ffmpeg("-ss", f"{still_time:.3f}", "-i", SOURCE, "-frames:v", "1", "-q:v", "2",
                   public / image_name)
        words = make_words(project, letter_index, item, source[1], source[2])
        word_records.extend(words)
        mnemonic_zh = mnemonic_meaning(item).split("，", 1)[0]
        intro_text = f"第{local_index+1}句，记住{mnemonic_zh}这个字母。"
        relation_display, relation_speech = relation(item)
        song_letters.append({**item, "chinese": item["zh"], "id": letter_id, "image": image_name,
                             "source_start_seconds": source[1], "source_end_seconds": source[2],
                             "words_detailed": words, "intro_text": intro_text,
                             "relation": relation_display, "relation_speech": relation_speech})
        section_estimates.append((f"lesson_{letter_id}", item["letter"], 18.0 + len(words) * 2.4))
        units += [{"id": f"{letter_id}_intro", "section": f"lesson_{letter_id}", "lang": "zh", "text": intro_text},
                  {"id": f"{letter_id}_name", "section": f"lesson_{letter_id}", "lang": "th", "text": item["name"]}]
        for word in words:
            units += [{"id": word["id"] + "_th", "section": f"lesson_{letter_id}", "lang": "th", "text": word["th"]},
                      {"id": word["id"] + "_zh", "section": f"lesson_{letter_id}", "lang": "zh", "text": f"是{word['zh']}。"}]
        units.append({"id": f"{letter_id}_relation", "section": f"lesson_{letter_id}",
                      "lang": "zh", "text": relation_speech})
    section_estimates.append(("outro", "应用", 4.0))
    for section_id, label, length in section_estimates:
        text = ({"intro": intro, "song": " / ".join(x["phrase"] for x in entries),
                 "bridge": bridge, "outro": outro}).get(section_id, "")
        if section_id.startswith("lesson_"):
            letter = next(x for x in song_letters if section_id == "lesson_" + x["id"])
            text = f"{letter['phrase']} → {letter['chinese']} → " + " → ".join(f"{w['th']}：{w['zh']}" for w in letter["words_detailed"])
        sections.append({"id": section_id, "label": label, "text": text,
                         "start_seconds": round(cursor, 3), "end_seconds": round(cursor + length, 3)})
        cursor += length
    units = [{"id": "intro", "section": "intro", "lang": "zh", "text": intro},
             {"id": "bridge", "section": "bridge", "lang": "zh", "text": bridge}] + units + [
                 {"id": "outro", "section": "outro", "lang": "zh", "text": outro}]

    script = {"version": "1.0", "title": title, "total_duration_seconds": round(cursor, 3),
              "sections": sections, "metadata": {"source_url": SOURCE_URL,
              "source_windows_seconds": [[x[1], x[2]] for x in group],
              "letters": song_letters, "episode": episode, "approval_policy": "User reviews final videos only",
              "tts": {"engine": "azure", "provider_switch_approved": True,
                      "thai_provider_switch_approved": False,
                      "azure": {"resource_name": "caigentan", "resource_group": "NewGroup", "region": "eastasia"},
                      "voices": {"zh": "zh-CN-XiaoxiaoNeural", "th": "th-TH-PremwadeeNeural"},
                      "styles": {"zh": "chat-casual", "th": "plain"},
                      "rates": {"zh": 1.0, "th": 0.86}},
              "tts_units": units}}
    brief = {"version": "1.0", "title": title, "hook": intro,
             "key_points": ["只用原片对应字母的原唱和画面。", "原唱显示泰语与中文对应字幕。",
                            "每个词按原唱、标准泰语读音、中文解释的顺序教学。",
                            "每句说明字母与关键词的关系；特殊传统字母说明现代拼写。",
                            "结尾展示学泰文字母 App 图标和真实界面。"],
             "core_message": f"听懂 {letters_label} 的歌词并记住每个字母的助记词。",
             "cta": "想学泰文，就用学泰文字母。", "tone": "口语、清楚、童趣",
             "style": "沿用已审核的第 1 集竖屏教学设计", "target_audience": "中文母语的泰语初学者",
             "target_platform": "generic", "target_duration_seconds": 75,
             "reference_material": [SOURCE_URL, str(FIRST / "renders/final_azure.mp4")],
             "metadata": {"pipeline": "hybrid", "anchor_medium": "source video",
                          "music_source": "Pinkfong 原唱", "render_runtime": "remotion",
                          "batch_policy": "第一集已审核并入库，用户授权制作其余所有集，仅审最终成片"}}
    scenes = [{"id": section["id"], "type": "broll" if section["id"] == "song" else "transition" if section["id"] == "bridge" else "text_card",
               "description": ("保留 Pinkfong 原唱和画面，泰语歌词下显示中文含义" if section["id"] == "song" else
                               "逐词展示原唱、标准泰语读法和中文，并解释字母与关键词的关系" if section["id"].startswith("lesson_") else
                               "学泰文字母应用图标及真实界面" if section["id"] == "outro" else "字母画面可作首帧封面"),
               "start_seconds": section["start_seconds"], "end_seconds": section["end_seconds"],
               "script_section_id": section["id"], "framing": "1080x1920 竖屏；原片 16:9 完整展示，中文低于泰语"}
              for section in sections]
    scene_plan = {"version": "1.0", "style_playbook": "approved alphabet lesson visual style",
                  "scenes": scenes, "metadata": {"source_attribution": "Pinkfong", "episode": episode}}

    assets = [{"id": "source_song", "type": "video", "path": "public/song.mp4", "source_tool": "verified Pinkfong excerpt",
               "scene_id": "song", "duration_seconds": group_song_seconds, "resolution": "1280x720", "original_url": SOURCE_URL},
              {"id": "app_icon", "type": "image", "path": "public/app_icon.png", "source_tool": "approved app asset", "scene_id": "outro"},
              {"id": "app_home", "type": "image", "path": "public/app_home_zh.png", "source_tool": "approved app asset", "scene_id": "outro"}]
    for letter in song_letters:
        assets.append({"id": "still_" + letter["id"], "type": "image", "path": "public/" + letter["image"],
                       "source_tool": "ffmpeg/Pinkfong source", "scene_id": "lesson_" + letter["id"], "original_url": SOURCE_URL})
    for word in word_records:
        assets.append({"id": word["id"] + "_song", "type": "audio", "path": "public/song_words/" + word["id"] + "_song.mp3",
                       "source_tool": "ffmpeg/Pinkfong source", "scene_id": "lesson_" + word["id"].split("_", 1)[0],
                       "duration_seconds": word["song_duration_seconds"], "original_url": SOURCE_URL})
    asset_manifest = {"version": "1.0", "assets": assets, "total_cost_usd": 0,
                      "metadata": {"narration_pending": True, "source_vs_generated_map": "Pinkfong source footage and excerpts; approved app visuals; Azure F0 narration planned"}}

    save(project / "artifacts/brief.json", brief)
    save(project / "artifacts/script.json", script)
    save(project / "artifacts/scene_plan.json", scene_plan)
    save(project / "artifacts/asset_manifest.json", asset_manifest)
    save(project / "artifacts/source_word_ranges.json", {"version": "1.0", "words": word_records})
    save(project / "artifacts/proposal_packet.json", {"version": "1.0", "project_id": project_id,
         "production_plan": {"pipeline": "hybrid", "render_runtime": "remotion", "composition_mode": "templated"},
         "approval": {"status": "approved", "user_notes": "First sample approved; produce remaining episodes and review only final videos."}})
    decisions = [
        {"decision_id": "d-001", "stage": "idea", "category": "pipeline_selection", "subject": "Production pipeline",
         "options_considered": [{"option_id": "hybrid", "label": "Original song with bilingual teaching graphics", "score": 1,
                                 "reason": "Matches the approved first lesson"}],
         "selected": "hybrid", "reason": "Keep the original song central", "user_visible": True, "user_approved": True},
        {"decision_id": "d-002", "stage": "idea", "category": "render_runtime_selection", "subject": "Composition runtime",
         "options_considered": [{"option_id": "remotion", "label": "Remotion", "score": 1,
                                 "reason": "Reuses the approved source video and bilingual cards"},
                                {"option_id": "hyperframes", "label": "HyperFrames", "score": 0.6,
                                 "reason": "Available for HTML motion", "rejected_because": "Would change the approved look"},
                                {"option_id": "ffmpeg", "label": "FFmpeg", "score": 0.3,
                                 "reason": "Good for trims", "rejected_because": "Limited dynamic word cards"}],
         "selected": "remotion", "reason": "Same engine and design as the approved first lesson",
         "user_visible": True, "user_approved": True},
        {"decision_id": "d-003", "stage": "idea", "category": "composition_mode", "subject": "Composition authoring mode",
         "options_considered": [{"option_id": "templated", "label": "Approved lesson design", "score": 1,
                                 "reason": "Keeps the series consistent"},
                                {"option_id": "atelier", "label": "A new design per episode", "score": 0.3,
                                 "reason": "More visual variety", "rejected_because": "Breaks continuity with the approved sample"}],
         "selected": "templated", "reason": "Reuse the approved first-episode design",
         "user_visible": True, "user_approved": True},
        {"decision_id": "d-004", "stage": "idea", "category": "approval_policy", "subject": "Human review scope",
         "options_considered": [{"option_id": "batch_final_only", "label": "Produce the rest; review final videos", "score": 1,
                                 "reason": "The user approved the first episode and authorized all remaining episodes"},
                                {"option_id": "sample_only", "label": "Stop after first episode", "score": 0,
                                 "reason": "Previous plan", "rejected_because": "Superseded by the user's batch instruction"}],
         "selected": "batch_final_only", "reason": "User explicitly authorized the full remaining run",
         "user_visible": True, "user_approved": True},
        {"decision_id": "d-005", "stage": "assets", "category": "voice_selection", "subject": "Narration TTS provider",
         "options_considered": [{"option_id": "azure_mandarin", "label": "Azure F0 Xiaoxiao Mandarin", "score": 1,
                                 "reason": "Approved in the first full lesson"},
                                {"option_id": "google_thai", "label": "Existing Google Thai reading voice", "score": 0.6,
                                 "reason": "Used in the first full lesson", "rejected_because": "New paid synthesis requires separate authorization"},
                                {"option_id": "azure_thai", "label": "Azure F0 Premwadee Thai reading voice", "score": 0.8,
                                 "reason": "Free standard voice, pending user approval for provider switch"}],
         "selected": "azure_mandarin_thai_pending", "reason": "Mandarin is locked; no new Thai synthesis until the user decides",
         "user_visible": True, "user_approved": False},
    ]
    save(project / "artifacts/decision_log.json", {"version": "1.0", "project_id": project_id, "decisions": decisions})
    save(project / "decision_log.json", {"version": "1.0", "project_id": project_id, "decisions": decisions})
    print(f"{project_id}: {letters_label}, {len(word_records)} word excerpts, {len(units)} TTS units")


def main() -> None:
    timeline = json.loads((PARENT / "artifacts/letter_timeline.json").read_text())["letter_segments"]
    lyric_items = json.loads((SERIES / "artifacts/lyrics_verified.json").read_text())["letters"]
    assert len(timeline) == 44 and len(lyric_items) == 41
    for episode in range(2, 16):
        one(episode, timeline, lyric_items)


if __name__ == "__main__":
    main()
