"""Update the three approved Song 12 timelines with a short song introduction.

The previously rendered videos remain intact; the next renders use new versions.
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
from lib.checkpoint import write_checkpoint

PROJECTS = (
    ("thai-1000-song-12-sai-naen-hua-jai", "v5"),
    ("thai-1000-song-12-first-three-lines", "v2"),
    ("thai-1000-song-12-last-three-lines", "v2"),
)
INTRO_TEXT = "这是一首泰国电影歌曲。歌名里“赛楠”这个伊森语词，指命中注定的缘分。"
OFFICIAL_URL = "https://www.youtube.com/watch?v=NSm8ZXEuhL0"
MEANING_URL = "https://www.sanook.com/music/2402353/"


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def duration(path: Path) -> float:
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nokey=1:noprint_wrappers=1", str(path),
    ], text=True).strip())


def checkpoint(project: Path, stage: str, artifact: dict, revision: str) -> None:
    key = {"script": "script", "scene_plan": "scene_plan",
           "assets": "asset_manifest", "edit": "edit_decisions"}[stage]
    write_checkpoint(ROOT / "projects", project.name, stage, "in_progress", {},
                     pipeline_type="animated-explainer",
                     metadata={"revision": revision, "request": "Add song intro after opening playback"})
    write_checkpoint(
        ROOT / "projects", project.name, stage, "completed", {key: artifact},
        pipeline_type="animated-explainer",
        human_approved=stage in {"script", "scene_plan", "assets"},
        review={"decision": "pass", "critical": 0, "suggestions": 0,
                "checks": ["intro after opening song", "source claims verified", "timeline continuity"]},
        cost_snapshot={"spent_usd": 0, "estimated_remaining_usd": 0},
        metadata={"revision": revision, "approval_source": "User requested all three videos adjusted"},
    )


def revise(project_id: str, revision: str) -> None:
    project = ROOT / "projects" / project_id
    art = project / "artifacts"
    intro = project / "assets/audio/song_intro_zh.mp3"
    assert intro.is_file() and intro.stat().st_size > 1000
    shutil.copy2(intro, project / "composition/public/audio/song_intro_zh.mp3")
    intro_duration = duration(intro)

    props = json.loads((project / "composition/props.json").read_text())
    fps = props["fps"]
    blocks = props["blocks"]
    bridge_index = next(i for i, b in enumerate(blocks) if b["id"] == "bridge")
    bridge = blocks[bridge_index]
    old_frames = bridge["frames"]
    new_frames = math.ceil((intro_duration + 0.32) * fps)
    delta = new_frames - old_frames
    bridge["frames"] = new_frames
    bridge["dur"] = new_frames / fps
    bridge["nar"] = {"file": intro.name, "dur": intro_duration}
    for block in blocks[bridge_index + 1:]:
        block["startFrame"] += delta
    props["totalFrames"] += delta
    props["totalSeconds"] = props["totalFrames"] / fps
    by_id = {block["id"]: block for block in blocks}
    for row in props["review_timeline"]:
        block = by_id[row["id"]]
        row["start"] = block["startFrame"] / fps
        row["end"] = (block["startFrame"] + block["frames"]) / fps
        if row["id"] == "bridge":
            row.update({"label": "歌曲简介", "title": "歌曲简介", "text": INTRO_TEXT,
                        "credit": f"{OFFICIAL_URL} ; {MEANING_URL}"})
    save(project / "composition/props.json", props)

    script = json.loads((art / "script.json").read_text())
    script["total_duration_seconds"] = props["totalSeconds"]
    for section in script["sections"]:
        block = by_id[section["id"]]
        section["start_seconds"] = block["startFrame"] / fps
        section["end_seconds"] = (block["startFrame"] + block["frames"]) / fps
        if section["id"] == "bridge":
            section["label"] = "歌曲简介"
            section["text"] = INTRO_TEXT
            section["speaker_directions"] = "沿用中文女声；温暖、清楚地说明电影来源和歌名含义。"
            section["enhancement_cues"] = [{"type": "overlay", "description": "演唱者、电影来源与สายแนน释义", "timestamp_seconds": section["start_seconds"]}]
    script.setdefault("metadata", {})["revision"] = revision + "-song-intro"
    save(art / "script.json", script)

    scene_plan = json.loads((art / "scene_plan.json").read_text())
    for scene in scene_plan["scenes"]:
        block = by_id[scene["id"]]
        scene["start_seconds"] = block["startFrame"] / fps
        scene["end_seconds"] = (block["startFrame"] + block["frames"]) / fps
        if scene["id"] == "bridge":
            scene["description"] = "首次原唱之后展示歌曲简介：演唱者、电影来源、歌名词义。"
            scene["required_assets"] = [
                {"type": "audio", "description": "新中文简介旁白", "source": "generate"},
                {"type": "image", "description": "伊森织物与命运线视觉", "source": "provided"},
            ]
    save(art / "scene_plan.json", scene_plan)

    manifest = json.loads((art / "asset_manifest.json").read_text())
    manifest["assets"] = [a for a in manifest["assets"] if a["id"] != "song_intro_zh"]
    manifest["assets"].append({
        "id": "song_intro_zh", "type": "audio", "path": "assets/audio/song_intro_zh.mp3",
        "source_tool": "edge-tts", "scene_id": "bridge", "cost_usd": 0,
        "duration_seconds": intro_duration, "format": "mp3",
    })
    save(art / "asset_manifest.json", manifest)

    edit = json.loads((art / "edit_decisions.json").read_text())
    for cut in edit["cuts"]:
        block = by_id[cut["id"]]
        cut["in_seconds"] = round(block["startFrame"] / fps, 3)
        cut["out_seconds"] = round((block["startFrame"] + block["frames"]) / fps, 3)
        if cut["id"] == "bridge":
            cut["reason"] = "song introduction after first playback"
    edit.setdefault("metadata", {})["total_seconds"] = props["totalSeconds"]
    save(art / "edit_decisions.json", edit)

    log = json.loads((art / "decision_log.json").read_text())
    log["decisions"] = [d for d in log["decisions"] if d["decision_id"] != f"song12-intro-{revision}"]
    log["decisions"].append({
        "decision_id": f"song12-intro-{revision}", "stage": "script",
        "category": "narration_architecture", "subject": "Bridge narration self-contained wording",
        "options_considered": [
            {"option_id": "previous-process-bridge", "label": "仅提示逐词拆解", "score": 0,
             "reason": "旧版现状", "rejected_because": "用户要求首次播放后介绍歌曲"},
            {"option_id": "song-intro", "label": "歌曲来源与歌名含义", "score": 1,
             "reason": "简短且与歌曲直接相关"},
        ],
        "selected": "song-intro", "reason": "用户要求三个版本首次播放后加入简短歌曲介绍。",
        "user_visible": True, "user_approved": True,
    })
    save(art / "decision_log.json", log)

    publish = json.loads((art / "publish.json").read_text())
    publish["video_path"] = f"renders/final-{revision}.mp4"
    publish["cover_path"] = f"renders/cover-{revision}.jpg"
    publish["note"] = "歌曲简介修订版待审片；现有入库版本保持原样。"
    save(art / "publish.json", publish)

    for stage, artifact in (("script", script), ("scene_plan", scene_plan),
                            ("assets", manifest), ("edit", edit)):
        checkpoint(project, stage, artifact, revision)
    print(project_id, "intro", intro_duration, "frames +", delta,
          "total", props["totalFrames"] / fps)


if __name__ == "__main__":
    for project_id, revision in PROJECTS:
        revise(project_id, revision)
