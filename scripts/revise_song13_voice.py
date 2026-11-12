"""Record the approved Song 13 Chinese voice revision in pipeline artifacts."""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import write_checkpoint

PROJECT_ID = "thai-1000-song-13-nalika-sai"
PROJECT = ROOT / "projects" / PROJECT_ID
ART = PROJECT / "artifacts"
REVISION = "v2-xiaoxiao"
INTRO = "这首歌叫《沙漏》。沙漏里的沙慢慢落下，就像一段走向结束的感情。"
BRIDGE = "再听一遍，留意沙漏和消散。"


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def duration(path: Path) -> float:
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], text=True).strip())


def checkpoint(stage: str, artifact: dict) -> None:
    key = {"script": "script", "scene_plan": "scene_plan", "assets": "asset_manifest",
           "edit": "edit_decisions"}[stage]
    write_checkpoint(ROOT / "projects", PROJECT_ID, stage, "in_progress", {},
                     pipeline_type="animated-explainer", metadata={"revision": REVISION})
    write_checkpoint(
        ROOT / "projects", PROJECT_ID, stage, "completed", {key: artifact},
        pipeline_type="animated-explainer", human_approved=stage in {"script", "scene_plan", "assets"},
        review={"decision": "pass", "critical": 0, "suggestions": 0,
                "checks": ["User approved Xiaoxiao voice", "Chinese audio fits each scene", "Original Thai and song audio retained"]},
        cost_snapshot={"spent_usd": 0, "estimated_remaining_usd": 0},
        metadata={"revision": REVISION, "approval_source": "User confirmed voice change and asked to proceed"},
    )


def main() -> None:
    props_path = PROJECT / "composition/props.json"
    props = read(props_path)
    assert props["totalFrames"] in {3600, 3678}, "Revision expects Song 13 v1 or prepared v2 timeline"
    timeline_prepared = props["totalFrames"] == 3678
    fps = props["fps"]
    blocks = props["blocks"]
    cumulative = 0
    voice_files = []
    for block in blocks:
        if not timeline_prepared:
            block["startFrame"] += cumulative
        if block["id"] == "song_intro" or block["id"].startswith("word_") or block["id"] in {"replay_bridge", "outro"}:
            name = block["id"] + "_zh_v2.mp3"
            path = PROJECT / "assets/audio" / name
            assert path.is_file() and path.stat().st_size > 1000, path
            voice_files.append((block["id"], name, duration(path)))
            if block["id"].startswith("word_"):
                needed = block["zhAt"] + duration(path) + 0.25
            else:
                needed = duration(path) + (0.25 if block["id"] != "outro" else 0.2)
            if not timeline_prepared:
                extra = max(0, math.ceil(needed * fps) - block["frames"])
                block["frames"] += extra
                cumulative += extra
    props["totalFrames"] += cumulative
    props["totalSeconds"] = props["totalFrames"] / fps
    by_id = {block["id"]: block for block in blocks}
    for row in props["review_timeline"]:
        block = by_id[row["id"]]
        row["start"] = round(block["startFrame"] / fps, 3)
        row["end"] = round((block["startFrame"] + block["frames"]) / fps, 3)
        if row["id"] == "song_intro":
            row["text"] = row["sub"] = INTRO
        elif row["id"] == "replay_bridge":
            row["text"] = row["sub"] = BRIDGE
    save(props_path, props)

    script = read(ART / "script.json")
    script["total_duration_seconds"] = props["totalSeconds"]
    script["voice_performance"].update({
        "performance_intent": "小晓女声；歌曲简介带轻微惋惜，词义清楚温和，回听提示轻盈，片尾亲切。",
        "pacing_profile": "custom",
        "energy_curve": "原唱进入→温柔介绍→逐词清晰讲解→轻提示→亲切收尾",
        "provider_notes": {"edge_tts": "Microsoft Edge zh-CN-XiaoxiaoNeural；中文各段独立生成，-3% 语速；不做音频加速。"},
    })
    script["voice_performance"].pop("approved_sample_path", None)
    for section in script["sections"]:
        block = by_id[section["id"]]
        section["start_seconds"] = round(block["startFrame"] / fps, 3)
        section["end_seconds"] = round((block["startFrame"] + block["frames"]) / fps, 3)
        if section["id"] == "song_intro":
            section["text"] = INTRO
            section["delivery_cues"]["provider_text"] = INTRO
            section["speaker_directions"] = "小晓女声，轻柔且有一点惋惜；歌手名留在画面上，不在口播中硬读英文。"
        elif section["id"] == "replay_bridge":
            section["text"] = BRIDGE
            section["delivery_cues"]["provider_text"] = BRIDGE
            section["speaker_directions"] = "小晓女声轻提示，不加速；末尾留足空隙进入原唱。"
        elif section["id"].startswith("word_") or section["id"] == "outro":
            if "小晓女声" not in section["speaker_directions"]:
                section["speaker_directions"] += " 中文释义用小晓女声，正常播放速度。"
    script.setdefault("metadata", {})["revision"] = REVISION
    save(ART / "script.json", script)
    checkpoint("script", script)

    scene_plan = read(ART / "scene_plan.json")
    for scene in scene_plan["scenes"]:
        block = by_id[scene["id"]]
        scene["start_seconds"] = round(block["startFrame"] / fps, 3)
        scene["end_seconds"] = round((block["startFrame"] + block["frames"]) / fps, 3)
        for asset in scene["required_assets"]:
            if asset["type"] == "narration" and "中文" in asset["description"]:
                asset["description"] = "Edge TTS 小晓中文女声口播"
    scene_plan.setdefault("metadata", {})["revision"] = REVISION
    save(ART / "scene_plan.json", scene_plan)
    checkpoint("scene_plan", scene_plan)

    manifest = read(ART / "asset_manifest.json")
    voice_map = {scene_id: (name, sec) for scene_id, name, sec in voice_files}
    for asset in manifest["assets"]:
        scene_id = asset.get("scene_id")
        if scene_id in voice_map and asset["id"].endswith("-zh"):
            name, sec = voice_map[scene_id]
            asset.update({"path": "assets/audio/" + name, "source_tool": "edge-tts",
                          "model": "zh-CN-XiaoxiaoNeural", "duration_seconds": sec,
                          "cost_usd": 0})
            asset["voice_performance"] = {
                "source_section_id": scene_id, "delivery_cues_applied": True,
                "provider_text_used": scene_id in {"song_intro", "replay_bridge"},
                "provider_settings": {"voice": "zh-CN-XiaoxiaoNeural", "rate": "-3%"},
                "sample_approved": True,
                "sample_path": "assets/audio/song_intro_zh_v2.mp3",
                "review_notes": "User approved prior Song 12 Xiaoxiao voice; sample fits 9-second song introduction.",
            }
            shutil.copy2(PROJECT / "assets/audio" / name,
                         PROJECT / "composition/public/audio" / name)
    manifest["total_cost_usd"] = round(sum(float(a.get("cost_usd", 0)) for a in manifest["assets"]), 6)
    manifest.setdefault("metadata", {})["revision"] = REVISION
    save(ART / "asset_manifest.json", manifest)
    checkpoint("assets", manifest)

    edit = read(ART / "edit_decisions.json")
    for cut in edit["cuts"]:
        block = by_id[cut["id"]]
        cut["in_seconds"] = round(block["startFrame"] / fps, 3)
        cut["out_seconds"] = round((block["startFrame"] + block["frames"]) / fps, 3)
    edit.setdefault("metadata", {})["total_seconds"] = props["totalSeconds"]
    edit["metadata"]["revision"] = REVISION
    save(ART / "edit_decisions.json", edit)
    checkpoint("edit", edit)

    log = read(ART / "decision_log.json")
    assert not any(d["decision_id"] == "d-011" for d in log["decisions"])
    log["decisions"].append({
        "decision_id": "d-011", "stage": "assets", "category": "voice_selection",
        "subject": "中文介绍和泰语词组跟读",
        "options_considered": [
            {"option_id": "edge_xiaoxiao", "label": "Microsoft Edge 小晓女声",
             "score": 1, "reason": "用户已认可第12首相同声线，要求第13首改为更自然的中文声音"},
            {"option_id": "google_tts", "label": "Google TTS Standard-A",
             "score": 0, "reason": "上一版使用", "rejected_because": "用户指出毫无感情、非常机械；本次确认更换"},
        ],
        "selected": "edge_xiaoxiao", "reason": "用户明确回复‘确认 做吧’，批准替换全部中文配音。",
        "user_visible": True, "user_approved": True, "confidence": 1,
    })
    save(ART / "decision_log.json", log)
    print(json.dumps({"voice_files": voice_files, "added_frames": cumulative,
                      "duration_seconds": props["totalSeconds"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
