#!/usr/bin/env python3
"""Prepare four approved three-letter derivatives of the Kiddy Melody lesson."""

import copy
import json
from pathlib import Path

from lib.checkpoint import write_checkpoint
from schemas.artifacts import validate_artifact

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"
PARENT = PROJECTS / "thai-alphabet-ma-word-analysis"
PARENT_ART = PARENT / "artifacts"
source_props = json.loads((PARENT_ART / "props.json").read_text())
source_assets = json.loads((PARENT_ART / "asset_manifest.json").read_text())

GROUPS = [
    ("thai-alphabet-three-letters-01", "泰文字母歌马巨人船", "ม ย ร", "马、巨人、船", 8.6, 14.9),
    ("thai-alphabet-three-letters-02", "泰文字母歌猴子戒指凉亭", "ล ว ศ", "猴子、戒指、凉亭", 14.9, 20.6),
    ("thai-alphabet-three-letters-03", "泰文字母歌隐士豹箱子", "ษ ส ห", "隐士、豹、箱子", 20.6, 26.4),
    ("thai-alphabet-three-letters-04", "泰文字母歌风筝盆猫头鹰", "ฬ อ ฮ", "风筝、盆、猫头鹰", 26.4, 34.4),
]

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")

def checkpoint(project_id, stage, name, data, gated):
    validate_artifact(name, data)
    write_checkpoint(PROJECTS, project_id, stage, "completed", {name: data},
                     pipeline_type="hybrid", human_approved=gated,
                     review={"status": "pass", "summary": "沿用已审核整集的原片、脚本、配音和版式；三字母拆条。"})

for index, (project_id, title, letters, labels, source_start, source_end) in enumerate(GROUPS):
    project = PROJECTS / project_id
    art = project / "artifacts"
    selected = source_props["items"][index * 3:index * 3 + 3]
    timings = source_props["lessonTiming"][index * 3:index * 3 + 3]
    song_frames = 90 + round((source_end - source_start) * 30)
    frame = song_frames + 105
    timeline = [("full_listen", 0, song_frames / 30, "先听三句原唱"),
                ("bridge", song_frames / 30, frame / 30, "进入逐词教学")]
    for item, timing in zip(selected, timings):
        end = frame + timing["durationFrames"]
        timeline.append((timing["sceneId"], frame / 30, end / 30, item["source_phrase"]))
        frame = end
    total_frames = frame + 180
    timeline.append(("app_outro", frame / 30, total_frames / 30, "学泰文字母 App"))
    duration = total_frames / 30

    brief = {
        "version": "1.0", "title": title,
        "hook": f"泰国小朋友都会的字母歌，这集听懂 {letters} 三个字母。",
        "key_points": [f"原片仅保留 {letters} 对应的三句原唱，泰文下方同步中文字幕。",
                       "每句先说明字母并读标准名称，再逐词读泰语、讲中文意思和例词关系。",
                       "片尾显示学泰文字母 App，保留 Kiddy Melody 来源标注。"],
        "core_message": f"听懂 {labels} 三句，记住对应的三个泰文字母。",
        "cta": "打开「学泰文字母」，接着听、读、写。",
        "tone": "童趣、清楚、紧凑", "style": "source-led three-letter lesson derived from approved master",
        "target_audience": "中文母语的泰文字母初学者", "target_platform": "generic",
        "target_duration_seconds": duration,
        "reference_material": ["https://www.youtube.com/shorts/fehh9PeVNo8", str(PARENT / "renders/final.mp4")],
        "metadata": {"anchor_medium": "broll_footage", "parent_project": PARENT.name,
                     "group_index": index, "letters": letters, "music_source": "Kiddy Melody original song",
                     "support_layers": ["Chinese song captions", "approved Thai and Chinese narration", "word cards"],
                     "deliverable_mix": "one standalone vertical episode"},
    }
    save(art / "brief.json", brief)
    checkpoint(project_id, "idea", "brief", brief, True)

    sections = []
    for scene_id, start, end, label in timeline:
        if scene_id == "full_listen":
            text = f"开场说泰国小朋友都会的字母歌；直接听 {letters} 三句原唱，同步显示中文字幕。"
        elif scene_id == "bridge":
            text = "下面进入逐词教学，教你听懂这首歌。"
        elif scene_id == "app_outro":
            text = "打开学泰文字母，接着听一听、写一写。"
        else:
            item = next(item for item, timing in zip(selected, timings) if timing["sceneId"] == scene_id)
            text = f"本句字母 {item['letter']}；先听标准泰语名称，再逐词读泰语并解释中文，指出字母在例词中的位置。整句：{item['zh_sense']}。"
        sections.append({"id": scene_id, "label": label, "text": text,
                         "start_seconds": start, "end_seconds": end,
                         "source_ref": str(PARENT / "public/source.mp4")})
    script = {"version": "1.0", "title": title, "total_duration_seconds": duration,
              "sections": sections, "metadata": {"group_index": index, "approved_master": PARENT.name}}
    save(art / "script.json", script)
    checkpoint(project_id, "script", "script", script, True)

    scenes = []
    for section in sections:
        sid = section["id"]
        scenes.append({"id": sid,
                       "type": "broll" if sid == "full_listen" or sid.startswith("letter_") else "transition",
                       "description": section["text"],
                       "start_seconds": section["start_seconds"],
                       "end_seconds": section["end_seconds"],
                       "script_section_id": sid,
                       "framing": "1080×1920 竖屏，原片画面为主，中文卡片在泰文下方",
                       "movement": "原片动态或逐词高亮",
                       "overlay_notes": "每屏最多三词，保留原唱来源；片尾显示 App。"})
    scene_plan = {"version": "1.0", "scenes": scenes,
                  "metadata": {"anchor_rules": "只展示本组三句原唱及回放。",
                               "support_rules": "沿用整集已审核的字母牌、逐词卡和旁白。",
                               "safe_zones": "1080×1920，左右留 70px；中文歌词紧接泰文。",
                               "variant_rules": "仅竖屏独立视频。"}}
    save(art / "scene_plan.json", scene_plan)
    checkpoint(project_id, "scene_plan", "scene_plan", scene_plan, True)

    used_scene_ids = {s["id"] for s in scenes}
    assets = []
    for source_asset in source_assets["assets"]:
        if source_asset.get("scene_id") not in used_scene_ids:
            continue
        asset = copy.deepcopy(source_asset)
        asset["path"] = str((PARENT / asset["path"]).resolve())
        if not Path(asset["path"]).exists():
            raise FileNotFoundError(asset["path"])
        assets.append(asset)
    manifest = {"version": "1.0", "assets": assets, "total_cost_usd": 0,
                "metadata": {"source_project": PARENT.name, "source_vs_generated_map": "全部复用已审核素材，无新生成费用。"}}
    save(art / "asset_manifest.json", manifest)
    checkpoint(project_id, "assets", "asset_manifest", manifest, True)

    props = copy.deepcopy(source_props)
    props["groupIndex"] = index
    props["review_timeline"] = [{"id": sid, "start": start, "end": end, "label": label,
                                 "title": label, "thai": "", "sub": "", "text": next(s["text"] for s in sections if s["id"] == sid),
                                 "credit": "Kiddy Melody" if sid != "app_outro" else "学泰文字母"}
                                for sid, start, end, label in timeline]
    save(art / "props.json", props)
    save(project / "composition/props.json", {"totalSeconds": duration,
           "review_timeline": props["review_timeline"],
           "scenes": [{"start": start, "end": end, "label": label}
                      for _, start, end, label in timeline]})

    cuts = [{"id": "opening", "source": "source_video", "in_seconds": 0, "out_seconds": 3,
             "layer": "primary", "reason": "三秒封面和中文旁白。"},
            {"id": "three_song_lines", "source": "source_video", "in_seconds": source_start,
             "out_seconds": source_end, "layer": "primary", "reason": f"只保留 {letters} 三句原唱。"}]
    cuts += [{"id": f"replay_{i + 1}", "source": "source_video",
              "in_seconds": item["start_approx"], "out_seconds": item["end_approx"],
              "layer": "primary", "reason": f"回放 {item['source_phrase']}。"}
             for i, item in enumerate(selected)]
    edit = {"version": "1.0", "cuts": cuts, "render_runtime": "remotion",
            "renderer_family": "explainer-teacher", "composition_mode": "atelier",
            "bespoke": {"entry": str(PARENT / "split-index.tsx"),
                        "composition_id": "ThaiAlphabetThreeLetters",
                        "art_direction": str(PARENT / "art-direction.md"),
                        "props_path": str(art / "props.json"), "public_dir": str(PARENT / "public"),
                        "scale": 1, "crf": 18, "concurrency": 4},
            "subtitles": {"enabled": True, "style": "sentence", "source": str(PARENT_ART / "zh_song_captions.json"),
                          "position": "bottom-center"},
            "metadata": {"parent_project": PARENT.name, "group_index": index,
                         "letters": letters, "source_window": [source_start, source_end],
                         "approval_policy": "final_only", "proposal_render_runtime": "remotion"}}
    save(art / "edit_decisions.json", edit)
    checkpoint(project_id, "edit", "edit_decisions", edit, False)

    decision_log = {"version": "1.0", "project_id": project_id, "decisions": [
        {"decision_id": "d-001", "stage": "idea", "category": "render_runtime_selection",
         "subject": "Composition render runtime",
         "options_considered": [
             {"option_id": "remotion", "label": "Remotion", "score": 1,
              "reason": "原片、泰中字幕和已有 React 词卡逐帧同步。"},
             {"option_id": "hyperframes", "label": "HyperFrames", "score": 0.6,
              "reason": "适合 HTML 字幕动效。", "rejected_because": "本次沿用已审核 Remotion 版式。"},
             {"option_id": "ffmpeg", "label": "FFmpeg", "score": 0.4,
              "reason": "适合纯裁剪。", "rejected_because": "逐词卡与多语音轨同步需要现有合成组件。"}],
         "selected": "remotion", "reason": "沿用用户已审核的整集运行路径。",
         "user_visible": True, "user_approved": True, "confidence": 1},
        {"decision_id": "d-002", "stage": "idea", "category": "composition_mode",
         "subject": "Composition authoring mode",
         "options_considered": [
             {"option_id": "atelier", "label": "手工制作", "score": 1,
              "reason": "复用已审核整集的手工版式。"},
             {"option_id": "templated", "label": "模板制作", "score": 0.5,
              "reason": "批量速度快。", "rejected_because": "会改变现有教学视觉。"}],
         "selected": "atelier", "reason": "四集保持与已审核整集一致。",
         "user_visible": True, "user_approved": True, "confidence": 1},
        {"decision_id": "d-003", "stage": "idea", "category": "music_source",
         "subject": "Music and song source",
         "options_considered": [{"option_id": "original_audio", "label": "Kiddy Melody 原唱", "score": 1,
                                  "reason": "用户要求使用原片。"}],
         "selected": "original_audio", "reason": "每集只播放对应三句原唱。",
         "user_visible": True, "user_approved": True, "confidence": 1},
        {"decision_id": "d-004", "stage": "idea", "category": "approval_policy",
         "subject": "Remaining production checkpoints",
         "options_considered": [{"option_id": "final_only", "label": "只审最终成片", "score": 1,
                                  "reason": "延续本首歌用户已明确的最终成片审核方式。"}],
         "selected": "final_only", "reason": "用户已审核整集，并明确要求拆成四集。",
         "user_visible": True, "user_approved": True, "confidence": 1},
    ]}
    save(art / "decision_log.json", decision_log)
    save(project / "decision_log.json", decision_log)

    slug = f"thai_alphabet_song_three_letters_{index + 1:02d}"
    publish = {"series_id": 1, "sub_series": "泰语神曲", "slug": slug, "title": title,
               "video_path": "renders/final.mp4", "cover_path": "renders/cover.jpg",
               "publish_copy": f"{title}\n泰国小朋友都会的字母歌，这集只听 {letters} 三个字母：{labels}。先听 Kiddy Melody 原唱，再听标准字母发音，逐词学泰语和中文意思，看清字母在例词中的位置。打开「学泰文字母」，接着听读书写。\n\n#泰语 #泰语学习 #泰文字母 #泰语字母歌 #学泰文字母",
               "credits": "原唱及画面：Kiddy Melody https://www.youtube.com/shorts/fehh9PeVNo8；中文教学与剪辑：学泰文字母。"}
    save(art / "publish.json", publish)
    print(f"{project_id}: {letters}, {duration:.2f}s, {len(assets)} reused assets")
