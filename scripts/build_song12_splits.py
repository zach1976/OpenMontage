"""Materialize the two approved three-line Song 12 teaching edits.

This only transforms already approved local assets and writes pipeline artifacts.
Rendering is performed separately through VideoCompose.
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import write_checkpoint

SOURCE = ROOT / "projects/thai-1000-song-12-sai-naen-hua-jai"
SOURCE_PROPS = json.loads((SOURCE / "composition/props.json").read_text())
SOURCE_PROPOSAL = json.loads((SOURCE / "artifacts/proposal_packet.json").read_text())
SOURCE_URL = "https://www.youtube.com/watch?v=NSm8ZXEuhL0"
CONFIGS = (
    ("thai-1000-song-12-first-three-lines", 1, "前三句", "warm", 0, 3, 0.0, 14.28),
    ("thai-1000-song-12-last-three-lines", 2, "后三句", "indigo", 3, 6, 14.28, 29.42),
)


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def seconds(path: Path) -> float:
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nokey=1:noprint_wrappers=1", str(path),
    ], text=True).strip())


def checkpoint(project: Path, stage: str, status: str, artifacts: dict) -> None:
    write_checkpoint(
        ROOT / "projects", project.name, stage, status, artifacts,
        pipeline_type="animated-explainer",
        human_approved=status == "completed" and stage in {"proposal", "script", "scene_plan", "assets"},
        review={"decision": "pass", "critical": 0, "suggestions": 0,
                "checks": ["approved V4 source only", "three-line split and asset paths checked"]} if status == "completed" else None,
        cost_snapshot={"spent_usd": 0, "estimated_remaining_usd": 0},
        metadata={"approval_source": "User said 出片吧 after the two-video Remotion full-run proposal",
                  "source_project": SOURCE.name},
    )


def make_research(part: str, start: float, end: float, project: Path) -> dict:
    local = (SOURCE / "composition/props.json").resolve().as_uri()
    final = (SOURCE / "renders/final-v4.mp4").resolve().as_uri()
    return {
        "version": "1.0", "topic": f"สายแนนหัวใจ 官方副歌{part}逐词学",
        "research_date": date.today().isoformat(),
        "research_summary": f"本片是已审核第12首V4的衍生教学剪辑。选取官方副歌相对时间{start:.2f}–{end:.2f}秒的三句；泰文、中文和词组边界以V4时间线为准，不新增歌曲事实主张。",
        "landscape": {"existing_content": [
            {"title": "第12首V4六句逐词版", "source": "local approved video", "angle": "六句完整教学", "what_it_covers": "六句原唱、32词组和回听", "what_it_misses": "三句短版"},
            {"title": "SOUND ME HANG Official MV", "url": SOURCE_URL, "source": "youtube", "angle": "官方原唱", "what_it_covers": "第一轮副歌音源", "what_it_misses": "泰中逐词讲解"},
            {"title": "第12首V3逐词版", "source": "local approved video", "angle": "逐词卡片", "what_it_covers": "每个词组的原唱、泰语和中文", "what_it_misses": "独立的三句短版"},
        ], "saturated_angles": ["完整六句版已制作"],
            "underserved_gaps": ["独立观看时长更短的前三句与后三句教学"]},
        "trending": {"recent_developments": [], "active_discussions": [], "timeliness_window": "evergreen"},
        "data_points": [
            {"claim": "官方副歌选段长29.42秒", "source_url": local, "source_name": "V4 props", "credibility": "primary_source", "usable_as": "timing"},
            {"claim": "第4句从选段14.28秒开始", "source_url": local, "source_name": "V4 props", "credibility": "primary_source", "usable_as": "split boundary"},
            {"claim": f"{part}选段为{start:.2f}–{end:.2f}秒", "source_url": final, "source_name": "V4 approved render", "credibility": "primary_source", "usable_as": "source section"},
        ],
        "audience_insights": {"common_questions": ["这一句泰文怎么唱？", "每个词是什么意思？", "三句连起来表达什么？"],
                              "misconceptions": [], "knowledge_level": "以已有泰语歌曲教学观众为主，可从零听懂这一小段。",
                              "pain_points": ["六句版本较长，回看指定三句不够方便。"]},
        "angles_discovered": [
            {"name": "三句原唱逐词学", "hook": "先听原唱，再听懂这三句每个词。", "type": "evergreen", "why_now": "用户要求把已审定V4拆为两支。", "grounded_in": ["V4 props", "用户指令"]},
            {"name": "三句跟唱短版", "hook": "只用三句练熟这段旋律。", "type": "evergreen", "why_now": "可缩短复习时间。", "grounded_in": ["V4 approved render"]},
            {"name": "重点词速学版", "hook": "三个词抓住这段歌词。", "type": "evergreen", "why_now": "适合极短平台版本。", "grounded_in": ["V4 props"]},
        ],
        "sources": [
            {"url": SOURCE_URL, "title": "SOUND ME HANG Official MV", "used_for": "官方原唱", "reliability": "primary"},
            {"url": local, "title": "Song12 V4 composition props", "used_for": "六句与词组时间点", "reliability": "primary"},
            {"url": final, "title": "Song12 V4 approved render", "used_for": "音画基准", "reliability": "primary"},
            {"url": "https://musicstation.kapook.com/สายแนนหัวใจ.html", "title": "Kapook lyrics", "used_for": "已核对泰文歌词", "reliability": "secondary"},
            {"url": "https://esan108.com/dict/view/สายแนน", "title": "อีสานร้อยแปด", "used_for": "已核对伊森语释义", "reliability": "secondary"},
        ],
        "metadata": {"derivative_of": SOURCE.name, "local_source_audit": True},
    }


def make_proposal(project: Path, number: int, part: str, start: float, end: float, word_count: int, target: float) -> tuple[dict, dict]:
    packet = copy.deepcopy(SOURCE_PROPOSAL)
    packet["concept_options"] = [
        {"id": "three-line-word-cards", "title": f"{part}逐词学", "hook": "先听三句原唱，再把每个词听懂。",
         "narrative_structure": "tutorial", "visual_approach": "三句原唱、逐词卡、三句回听；沿用已审核的伊森田野视觉方向。",
         "target_duration_seconds": round(target), "why_this_works": f"精确覆盖原曲第{1 if number == 1 else 4}–{3 if number == 1 else 6}句和{word_count}张词卡。"},
        {"id": "three-line-singalong", "title": f"{part}跟唱版", "hook": "三句连唱，把旋律唱熟。",
         "narrative_structure": "tutorial", "visual_approach": "减少词卡，突出原唱字幕。",
         "target_duration_seconds": 40, "why_this_works": "更短，但用户此前明确偏好逐词解释。"},
        {"id": "three-keywords", "title": f"{part}重点词速学", "hook": "三个词听懂这段歌词。",
         "narrative_structure": "tutorial", "visual_approach": "只讲重点词。",
         "target_duration_seconds": 30, "why_this_works": "节奏快，但会丢失完整逐词覆盖。"},
    ]
    packet["selected_concept"] = {"concept_id": "three-line-word-cards",
        "rationale": "用户要把已审定第12首拆为前后三句两个独立视频；保留此前要求的逐词教学。",
        "modifications": [f"仅含原曲第{1 if number == 1 else 4}–{3 if number == 1 else 6}句", f"{word_count}张词卡", "独立片名、句序和回听"]}
    plan = packet["production_plan"]
    plan.update({"pipeline": "animated-explainer", "render_runtime": "remotion", "renderer_family": "explainer-teacher",
                 "composition_mode": "atelier", "art_direction": "art-direction.md；同曲拆分版保留系列色彩和田野素材，以暖金/靛蓝区分上下篇。",
                 "music_source": {"source_type": "none", "mood_direction": "歌曲原唱自带音乐，不叠加背景音乐。", "estimated_cost_usd": 0}})
    plan["taste_profile"] = {"design_read": f"第12首{part}歌曲课：保持系列识别度，让三句原唱与逐词中文清晰可读。",
        "visual_variance": 4, "motion_intensity": 3, "information_density": 4,
        "reference_strategy": "沿用用户已审定的V4音源、田野影像和词组释义；逐场核对新三句时间线。",
        "anti_patterns": ["误播另外三句", "片内仍写六句", "逐词卡音画错位"]}
    for stage in plan["stages"]:
        stage["approach"] = {
            "script": f"只写{part}独立讲解，复用已审定泰中读音。",
            "scene_plan": f"三句原唱、{word_count}张词卡、三句回听和收尾。",
            "assets": "复用V4原唱、泰中配音和画面；本地无损截取三句音轨。",
            "edit": "逐帧重排三句时间线，并按本片重编号。",
            "compose": "用VideoCompose的Remotion atelier路径输出独立MP4并审片。",
        }[stage["stage"]]
        if stage["stage"] == "compose":
            stage["tools"] = [{"tool_name": "video_compose", "role": "Remotion atelier 渲染", "provider": "local", "available": True, "estimated_cost_usd": 0}]
    packet["cost_estimate"] = {"total_estimated_usd": 0, "line_items": [
        {"tool": "ffmpeg", "operation": "本地音轨裁切", "quantity": 1, "estimated_usd": 0},
        {"tool": "video_compose", "operation": "本地Remotion渲染", "quantity": 1, "estimated_usd": 0},
    ], "budget_verdict": "within_budget"}
    packet["approval"] = {"status": "approved", "user_notes": "用户在看过Remotion全流程方案后回复‘出片吧’，授权直接制作两支并交审片。"}
    packet["metadata"] = {"source_project": SOURCE.name, "source_url": SOURCE_URL,
                           "source_range_seconds": [start, end], "word_count": word_count,
                           "delivery_promise": "三句独立逐词学；原片V4不改动"}

    def option(option_id: str, label: str, score: float, reason: str, rejected: str | None = None) -> dict:
        d = {"option_id": option_id, "label": label, "score": score, "reason": reason}
        if rejected:
            d["rejected_because"] = rejected
        return d

    decisions = {"version": "1.0", "project_id": project.name, "decisions": [
        {"decision_id": "split-runtime", "stage": "proposal", "category": "render_runtime_selection",
         "subject": "Video composition runtime", "options_considered": [
             option("remotion", "Remotion", 1, "已有逐词同步技术路径，适合本次独立剪辑"),
             option("hyperframes", "HyperFrames", .6, "可重做动效，但需重建逐词同步", "用户批准推荐的Remotion出片路径"),
             option("ffmpeg", "FFmpeg", .3, "能裁切视频，但无法便捷重排逐词卡", "无法满足独立教学结构"),
         ], "selected": "remotion", "reason": "用户在运行时对比后回复‘出片吧’，同意推荐的Remotion方案。", "user_visible": True, "user_approved": True},
        {"decision_id": "split-mode", "stage": "proposal", "category": "composition_mode",
         "subject": "Composition authoring mode", "options_considered": [
             option("atelier", "Atelier", 1, "定制三句逐词布局、重排时间线，并延续同曲系列识别"),
             option("templated", "Templated", .4, "出片快，但 stock 场景难呈现三步词音与原唱高亮", "逐词同步表现不足"),
         ], "selected": "atelier", "reason": "该作品是同曲派生片，用户认可保留系列视觉方向；为上下篇手工编排专用画面。", "user_visible": True, "user_approved": True},
        {"decision_id": "split-approval", "stage": "proposal", "category": "approval_policy",
         "subject": "Two-video production approval policy", "options_considered": [
             option("full-run", "直接出两支片", 1, "用户明确回复出片吧"),
             option("guided", "每阶段等待审批", 0, "分阶段审批", "用户要求现在出片"),
         ], "selected": "full-run", "reason": "用户针对已展示的两视频方案说‘出片吧’，覆盖脚本、场景、素材、剪辑和渲染；入库另行确认。", "user_visible": True, "user_approved": True},
        {"decision_id": "split-music", "stage": "proposal", "category": "music_source",
         "subject": "Music source", "options_considered": [
             option("original", "歌曲原唱", 1, "原唱片段自带音乐"),
             option("extra", "额外背景音乐", .1, "可增加气氛", "会掩盖教学人声"),
         ], "selected": "original", "reason": "只用已审定官方原唱，不叠加新音乐。", "user_visible": True, "user_approved": True},
    ]}
    return packet, decisions


def build_one(config: tuple) -> None:
    project_id, number, part, theme, first, last, song_start, song_end = config
    project = ROOT / "projects" / project_id
    art = project / "artifacts"
    local_lines = copy.deepcopy(SOURCE_PROPS["lines"][first:last])
    for line in local_lines:
        line["at"] = round(max(0, line["at"] - song_start), 3)
    source_words = [b for b in SOURCE_PROPS["blocks"] if b["kind"] == "word" and first < b["line"] <= last]
    assert len(local_lines) == 3
    expected_words = sum(len(line["pairs"]) for line in local_lines)
    assert len(source_words) == expected_words
    song_path = project / "assets/audio/chorus_part.wav"
    assert song_path.exists(), song_path
    assert abs(seconds(song_path) - (song_end - song_start)) < .03

    public = project / "composition/public"
    for name in ("isan-fields.png", "isan-thread.png", "promo-card-v4.png"):
        src = SOURCE / "composition/public/images" / name
        for dest in (project / "assets/images" / name, public / "images" / name):
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    font = SOURCE / "composition/public/fonts/Sarabun-Bold.ttf"
    (public / "fonts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(font, public / "fonts/Sarabun-Bold.ttf")

    refs = {"bridge_v4_zh.mp3", "outro_zh.mp3"}
    for word in source_words:
        refs.update(word[key]["file"] for key in ("source", "thaiAudio", "zhAudio"))
    for name in refs:
        src = SOURCE / "assets/audio" / name
        assert src.exists(), src
        for dest in (project / "assets/audio" / name, public / "audio" / name):
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    shutil.copy2(song_path, public / "audio/chorus_part.wav")

    blocks = []
    cursor = 0
    def append(block: dict) -> None:
        nonlocal cursor
        block["startFrame"] = cursor
        block["frames"] = max(1, round(block["dur"] * 30))
        cursor += block["frames"]
        blocks.append(block)
    song_clip = {"file": "chorus_part.wav", "dur": seconds(song_path)}
    append({"id": "song_open", "kind": "song_open", "audio": song_clip, "dur": song_clip["dur"]})
    bridge = next(b for b in SOURCE_PROPS["blocks"] if b["id"] == "bridge")
    append({"id": "bridge", "kind": "bridge", "nar": bridge["nar"], "dur": bridge["dur"]})
    for idx, old in enumerate(source_words):
        b = copy.deepcopy(old)
        b["sourceLine"] = b["line"]
        b["line"] -= first
        b["id"] = f"l{b['line']}_w{b['word']}"
        b["index"] = idx
        append({k: v for k, v in b.items() if k not in ("startFrame", "frames")})
    append({"id": "song_replay", "kind": "song_replay", "audio": song_clip, "dur": song_clip["dur"]})
    outro = next(b for b in SOURCE_PROPS["blocks"] if b["id"] == "outro")
    append({"id": "outro", "kind": "outro", "nar": outro["nar"], "dur": outro["dur"]})

    review = []
    script_sections = []
    scenes = []
    for block in blocks:
        start = block["startFrame"] / 30
        end = (block["startFrame"] + block["frames"]) / 30
        label = block.get("th", {"song_open": f"{part}原唱", "bridge": "逐词拆解",
                                 "song_replay": f"{part}回听", "outro": "泰语千词"}.get(block["id"], block["id"]))
        text = block.get("th", label) + (("，" + block["zh"]) if block["kind"] == "word" else "")
        review.append({"id": block["id"], "label": label, "title": block["id"], "text": text,
                       "start": start, "end": end, "credit": SOURCE_URL})
        script_sections.append({"id": block["id"], "label": label, "text": text,
            "start_seconds": start, "end_seconds": end,
            "speaker_directions": "复用已审核的原唱、泰语跟读和中文解释。" if block["kind"] == "word" else "按已审核音频播放。",
            "enhancement_cues": [{"type": "overlay", "description": label, "timestamp_seconds": start}]})
        scenes.append({"id": block["id"],
            "type": "broll" if block["kind"].startswith("song") else "text_card" if block["kind"] in {"bridge", "outro"} else "animation",
            "description": label, "start_seconds": start, "end_seconds": end,
            "script_section_id": block["id"],
            "required_assets": [{"type": "audio", "description": "已审核原唱或泰中配音", "source": "source"},
                                {"type": "image", "description": "伊森田野及靛蓝织物", "source": "provided"}]})

    props = {"fps": 30, "totalFrames": cursor, "totalSeconds": cursor / 30,
             "title": "สายแนนหัวใจ", "artist": "ก้อง ห้วยไร่", "partLabel": part,
             "partNumber": number, "theme": theme, "lines": local_lines,
             "blocks": blocks, "review_timeline": review}
    save(project / "composition/props.json", props)
    save(art / "props.json", props)

    research = make_research(part, song_start, song_end, project)
    proposal, decisions = make_proposal(project, number, part, song_start, song_end, expected_words, cursor / 30)
    script = {"version": "1.0", "title": f"สายแนนหัวใจ｜{part}逐词学", "total_duration_seconds": cursor / 30,
        "sections": script_sections,
        "voice_performance": {"performance_intent": "原唱、泰语跟读、中文词义三步清楚交替。", "pacing_profile": "custom",
            "energy_curve": "三句原唱开场，逐词拆解，完整回听。", "pause_policy": "沿用已审核V4间隔。",
            "sample_section_id": next(b["id"] for b in blocks if b["kind"] == "word"), "provider_notes": {"reuse": "复用第12首已审核音频。"}},
        "metadata": {"source_project": SOURCE.name, "source_range_seconds": [song_start, song_end],
                     "phrase_count": expected_words}}
    scene_plan = {"version": "1.0", "style_playbook": "isan-song-split", "scenes": scenes,
                  "metadata": {"part": part, "source_project": SOURCE.name}}
    assets = []
    for name in ["chorus_part.wav", *sorted(refs)]:
        file = project / "assets/audio" / name
        assets.append({"id": file.stem, "type": "audio", "path": str(file.relative_to(project)),
            "source_tool": "ffmpeg" if name == "chorus_part.wav" else "approved-song12-source",
            "scene_id": "all", "cost_usd": 0, "duration_seconds": seconds(file),
            "format": file.suffix[1:]})
    for name in ("isan-fields.png", "isan-thread.png", "promo-card-v4.png"):
        file = project / "assets/images" / name
        assets.append({"id": file.stem, "type": "image", "path": str(file.relative_to(project)),
                       "source_tool": "approved-song12-source", "scene_id": "all", "cost_usd": 0, "format": "png"})
    manifest = {"version": "1.0", "assets": assets, "total_cost_usd": 0,
                "metadata": {"source_project": SOURCE.name, "music_status": "original-song-audio", "part": part}}
    cuts = [{"id": b["id"], "source": "composition:SaiNaenHuaJaiSplit#" + b["id"],
             "in_seconds": b["startFrame"] / 30, "out_seconds": (b["startFrame"] + b["frames"]) / 30,
             "transition_out": "cut", "transition_duration": 0, "reason": b["kind"]} for b in blocks]
    edit = {"version": "1.0", "renderer_family": "explainer-teacher", "render_runtime": "remotion",
            "composition_mode": "atelier", "cuts": cuts, "music": {"volume": 1, "ducking": False},
            "subtitles": {"enabled": False},
            "bespoke": {"entry": str((project / "composition/index.tsx").resolve()),
                "composition_id": "SaiNaenHuaJaiSplit", "props_path": str((project / "composition/props.json").resolve()),
                "public_dir": str(public.resolve()), "crf": 18, "concurrency": 2,
                "art_direction": "art-direction.md — series-specific three-line lyric teaching with warm/indigo contrast"},
            "metadata": {"fps": 30, "resolution": "1080x1920", "total_seconds": cursor / 30,
                         "proposal_render_runtime": "remotion", "subtitles_reason": "泰中歌词和逐词卡面已内嵌"}}

    save(art / "research_brief.json", research)
    save(art / "proposal_packet.json", proposal)
    save(art / "decision_log.json", decisions)
    save(art / "script.json", script)
    save(art / "scene_plan.json", scene_plan)
    save(art / "asset_manifest.json", manifest)
    save(art / "edit_decisions.json", edit)
    (project / "art-direction.md").write_text(
        f"# {part}视觉方向\n\n同曲独立教学短片；延续用户认可的伊森田野与命运线视觉。"
        f"第{number}支以{'暖金' if number == 1 else '靛蓝'}为强调色。原唱画面突出三句歌词，词卡突出原唱→泰语→中文三步。"
        "两个衍生片共享系列识别度，但标题、句序、进度和回听都各自独立。\n"
    )
    source_publish = json.loads((SOURCE / "artifacts/publish.json").read_text())
    pub = {"series_id": 1, "sub_series": "泰语神曲", "slug": f"thai_song_12_{'first' if number == 1 else 'last'}_three_lines",
           "title": f"泰语千词｜สายแนนหัวใจ {part}逐词学", "video_path": "renders/final-v1.mp4",
           "cover_path": "renders/cover-v1.jpg",
           "publish_copy": f"《สายแนนหัวใจ》{part}：先听原唱，再逐词听懂，最后完整回听。\n\n#泰语 #泰语学习 #泰语千词 #泰语歌曲",
           "credits": source_publish["credits"], "note": "待审片；未入库。"}
    save(art / "publish.json", pub)

    checkpoint(project, "research", "in_progress", {})
    checkpoint(project, "research", "completed", {"research_brief": research})
    for stage, artifact in (("proposal", {"proposal_packet": proposal, "decision_log": decisions}),
                            ("script", {"script": script}),
                            ("scene_plan", {"scene_plan": scene_plan}),
                            ("assets", {"asset_manifest": manifest}),
                            ("edit", {"edit_decisions": edit})):
        checkpoint(project, stage, "in_progress", {})
        checkpoint(project, stage, "completed", artifact)
    print(project.name, expected_words, "cards", round(cursor / 30, 2), "seconds")


if __name__ == "__main__":
    for cfg in CONFIGS:
        build_one(cfg)
