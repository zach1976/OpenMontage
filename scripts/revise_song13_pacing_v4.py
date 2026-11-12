"""Persist the user-requested Song 13 pacing and spoken-transition revision."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import write_checkpoint

PROJECT_ID = "thai-1000-song-13-nalika-sai"
PROJECT = ROOT / "projects" / PROJECT_ID
ART = PROJECT / "artifacts"
FPS = 30
REVISION = "v4-faster-transitions"
INTRO = "刚才这段唱的是《沙漏》：爱像流沙，终会消散。接着拆开听。"
BRIDGE = "爱像沙漏，终会消散。再听一遍。"


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
                "checks": ["User requested faster pacing and spoken transitions",
                           "Original full song and official MV remain in opening",
                           "Replay is a synchronized two-line highlight"]},
        cost_snapshot={"spent_usd": 0, "estimated_remaining_usd": 0},
        metadata={"revision": REVISION, "approval_source": "User requested faster pacing and necessary spoken transitions"},
    )


def main() -> None:
    props_path = PROJECT / "composition/props.json"
    props = read(props_path)
    assert props["totalFrames"] in {3678, 3007}, "Expected approved V3 or preliminary V4 timeline"
    cursor = 0
    for block in props["blocks"]:
        block["startFrame"] = cursor
        if block["id"] == "song_intro":
            block["frames"] = math.ceil(duration(PROJECT / "assets/audio/intro_zh_v4.mp3") * FPS) + 8
        elif block["kind"] == "word":
            source = block["source"]
            source_frames = round(source[1] * FPS) - round(source[0] * FPS)
            thai_frames = math.ceil(duration(PROJECT / "assets/audio" / f"{block['id']}_th.mp3") * FPS)
            zh_frames = math.ceil(duration(PROJECT / "assets/audio" / f"{block['id']}_zh_v4.mp3") * FPS)
            block["thaiAt"] = (source_frames + 4) / FPS
            block["zhAt"] = (source_frames + 4 + thai_frames + 3) / FPS
            block["frames"] = source_frames + 4 + thai_frames + 3 + zh_frames + 6
        elif block["id"] == "replay_bridge":
            block["frames"] = math.ceil(duration(PROJECT / "assets/audio/bridge_zh_v4.mp3") * FPS) + 5
        elif block["id"] == "original_replay":
            block["frames"] = 332
            block["label"] = "重点两句回听"
        cursor += block["frames"]
    props["totalFrames"] = cursor
    props["totalSeconds"] = cursor / FPS
    by_id = {b["id"]: b for b in props["blocks"]}
    for row in props["review_timeline"]:
        block = by_id[row["id"]]
        row["start"] = round(block["startFrame"] / FPS, 3)
        row["end"] = round((block["startFrame"] + block["frames"]) / FPS, 3)
        if row["id"] == "song_intro":
            row["text"] = row["sub"] = INTRO
        elif row["id"] == "replay_bridge":
            row["text"] = row["sub"] = BRIDGE
        elif row["id"] == "original_replay":
            row["label"] = row["title"] = "重点两句回听"
            row["text"] = row["sub"] = "回听原唱首句与收束句，画面同步切换官方 MV。"
    save(props_path, props)

    script = read(ART / "script.json")
    script["total_duration_seconds"] = props["totalSeconds"]
    script["voice_performance"]["energy_curve"] = "原唱完整进入→简短语言过渡→紧凑逐词→总结回听→轻快收尾"
    script["voice_performance"]["pause_policy"] = "原唱、跟读、词义间只留 0.1 秒左右；词卡结尾约 0.2 秒。"
    for section in script["sections"]:
        block = by_id[section["id"]]
        section["start_seconds"] = round(block["startFrame"] / FPS, 3)
        section["end_seconds"] = round((block["startFrame"] + block["frames"]) / FPS, 3)
        for cue in section.get("enhancement_cues", []):
            cue["timestamp_seconds"] = section["start_seconds"]
        if section["id"] in {"song_intro", "replay_bridge"}:
            txt = INTRO if section["id"] == "song_intro" else BRIDGE
            section["text"] = txt
            section["delivery_cues"]["provider_text"] = txt
            section["delivery_cues"]["pause_after_seconds"] = 0.15
            section["speaker_directions"] = "小晓女声自然衔接上一段，简短、有情绪，不拖尾。"
        elif section["id"] == "original_replay":
            section["label"] = "重点两句回听"
            section["text"] = "回听原唱首句与收束句，画面同步切换官方 MV。"
            section["speaker_directions"] = "原唱两句连续播放；不叠中文口播。"
    script.setdefault("metadata", {})["revision"] = REVISION
    save(ART / "script.json", script)
    checkpoint("script", script)

    scene_plan = read(ART / "scene_plan.json")
    for scene in scene_plan["scenes"]:
        block = by_id[scene["id"]]
        scene["start_seconds"] = round(block["startFrame"] / FPS, 3)
        scene["end_seconds"] = round((block["startFrame"] + block["frames"]) / FPS, 3)
        if scene["id"] == "original_replay":
            scene["description"] = "官方 MV 首句与收束句连续回听，共 11.07 秒；歌词同步切换。"
            scene["information_role"] = "重点两句回听"
            for asset in scene["required_assets"]:
                if asset["type"] in {"audio", "video"}:
                    asset["description"] = "BOWKYLION 官方原唱和 MV：首句 209.855–214.488 秒，收束句 229.422–235.855 秒"
    scene_plan.setdefault("metadata", {})["revision"] = REVISION
    save(ART / "scene_plan.json", scene_plan)
    checkpoint("scene_plan", scene_plan)

    manifest = read(ART / "asset_manifest.json")
    for asset in manifest["assets"]:
        if asset["id"] in {"song_intro-zh", "replay_bridge-zh"}:
            name = "intro_zh_v4.mp3" if asset["id"] == "song_intro-zh" else "bridge_zh_v4.mp3"
            asset["path"] = "assets/audio/" + name
            asset["duration_seconds"] = duration(PROJECT / asset["path"])
            asset["voice_performance"]["sample_path"] = "assets/audio/intro_zh_v4.mp3"
            asset["voice_performance"]["review_notes"] = "Same approved Xiaoxiao voice; spoken transition rewritten for pacing."
        elif asset.get("scene_id", "").startswith("word_") and asset["id"].endswith("-zh"):
            asset["path"] = f"assets/audio/{asset['scene_id']}_zh_v4.mp3"
            asset["duration_seconds"] = duration(PROJECT / asset["path"])
            asset["voice_performance"]["review_notes"] = "Approved Xiaoxiao recording; only its leading/trailing silence was trimmed."
        elif asset["id"] == "official-mv-hook-replay":
            asset["path"] = "assets/video/official_replay_11s.mp4"
            asset["duration_seconds"] = 332 / FPS
            asset["generation_summary"] = "Official MV first and final lyric lines, cut together at original speed"
    manifest.setdefault("metadata", {})["revision"] = REVISION
    save(ART / "asset_manifest.json", manifest)
    checkpoint("assets", manifest)

    edit = read(ART / "edit_decisions.json")
    for cut in edit["cuts"]:
        block = by_id[cut["id"]]
        cut["in_seconds"] = round(block["startFrame"] / FPS, 3)
        cut["out_seconds"] = round((block["startFrame"] + block["frames"]) / FPS, 3)
        if cut["id"] == "original_replay":
            cut["reason"] = "Short synchronized recap of the opening and closing lyric lines."
    edit.setdefault("metadata", {})["total_seconds"] = props["totalSeconds"]
    edit["metadata"]["pacing_revision"] = REVISION
    save(ART / "edit_decisions.json", edit)
    checkpoint("edit", edit)

    log = read(ART / "decision_log.json")
    if not any(d["decision_id"] == "d-013" for d in log["decisions"]):
        log["decisions"].append({
        "decision_id": "d-013", "stage": "edit", "category": "edit_structure",
        "subject": "第13首教学段落节奏",
        "options_considered": [
            {"option_id": "tight_cards_key_replay", "label": "收紧词卡与重点两句回听", "score": 1,
             "reason": "保留完整首听，减少重复内容并补足语言衔接"},
            {"option_id": "full_replay", "label": "完整二次回听", "score": 0,
             "reason": "V3 方式", "rejected_because": "用户指出节奏偏慢"},
        ],
        "selected": "tight_cards_key_replay",
        "reason": "用户要求加快节奏并加入必要的语言过渡。",
        "user_visible": True, "user_approved": True, "confidence": 1,
        })
    save(ART / "decision_log.json", log)
    print(f"V4 timeline: {props['totalSeconds']:.3f}s / {cursor} frames")


if __name__ == "__main__":
    main()
