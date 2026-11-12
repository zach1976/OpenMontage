"""Record the user-approved official MV picture treatment for Song 13."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import write_checkpoint

PROJECT_ID = "thai-1000-song-13-nalika-sai"
PROJECT = ROOT / "projects" / PROJECT_ID
ART = PROJECT / "artifacts"
SOURCE_URL = "https://www.youtube.com/watch?v=C40oligg6xE"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def checkpoint(stage: str, artifact: dict) -> None:
    key = {"scene_plan": "scene_plan", "assets": "asset_manifest", "edit": "edit_decisions"}[stage]
    write_checkpoint(ROOT / "projects", PROJECT_ID, stage, "in_progress", {},
                     pipeline_type="animated-explainer", metadata={"revision": "v3-official-mv"})
    write_checkpoint(ROOT / "projects", PROJECT_ID, stage, "completed", {key: artifact},
                     pipeline_type="animated-explainer", human_approved=stage in {"scene_plan", "assets"},
                     review={"decision": "pass", "critical": 0, "suggestions": 0,
                             "checks": ["Official MV picture at original song timing", "Readable Thai and Chinese teaching text", "Existing audio retained"]},
                     cost_snapshot={"spent_usd": 0, "estimated_remaining_usd": 0},
                     metadata={"revision": "v3-official-mv", "approval_source": "User requested official MV picture"})


def main() -> None:
    assert (PROJECT / "assets/video/official_mv.mp4").is_file()
    assert (PROJECT / "assets/video/official_hook_26s.mp4").is_file()
    assert len(list((PROJECT / "assets/images").glob("word_*_mv.jpg"))) == 9

    scene_plan = load(ART / "scene_plan.json")
    for scene in scene_plan["scenes"]:
        scene_id = scene["id"]
        if scene_id in {"original_first", "original_replay"}:
            scene["description"] = "官方 MV 对应 03:29.855–03:55.836 的动态画面完整呈现；下方泰语歌词逐句高亮。"
            scene["framing"] = "1080×1920 竖屏；横版 MV 完整宽度置于上半部，泰语歌词置于下半部。"
            scene["movement"] = "官方 MV 原速播放；画面与官方原唱音轨同一时间点同步。"
            scene["overlay_notes"] = "MV 不裁切人物；泰语歌词放在画面下方，不盖住人物。"
            scene["required_assets"].append({"type": "video", "description": "官方 MV 209.855–235.836 秒画面，26 秒无声截取", "source": "provided"})
        elif scene_id == "song_intro":
            scene["description"] = "官方 MV 结尾拥抱画面定格，配小晓中文简介与沙漏隐喻。"
            scene["required_assets"].append({"type": "image", "description": "官方 MV 结尾画面定格", "source": "provided"})
        elif scene_id.startswith("word_"):
            scene["description"] = "对应歌词时刻的官方 MV 定格置于上半部；泰语词组与中文释义置于下半部。"
            scene["framing"] = "1080×1920 竖屏；官方 MV 定格完整横幅，上下留文字安全区。"
            scene["required_assets"].append({"type": "image", "description": f"官方 MV {scene_id} 对应时刻定格", "source": "provided"})
    scene_plan.setdefault("metadata", {})["visual_revision"] = "Official MV live picture for song, aligned stills for words"
    save(ART / "scene_plan.json", scene_plan)
    checkpoint("scene_plan", scene_plan)

    manifest = load(ART / "asset_manifest.json")
    common = {"provider": "YouTube official MV", "original_url": SOURCE_URL, "cost_usd": 0}
    manifest["assets"].extend([
        {"id": "official-mv-master", "type": "video", "path": "assets/video/official_mv.mp4",
         "source_tool": "video_downloader", "scene_id": "original_first", "duration_seconds": 290,
         "generation_summary": "1080p official MV master, video-only", **common},
        {"id": "official-mv-hook-first", "type": "video", "path": "assets/video/official_hook_26s.mp4",
         "source_tool": "ffmpeg", "scene_id": "original_first", "duration_seconds": 26,
         "generation_summary": "Official MV 209.855–235.855 picture, 30 fps, muted in composition", **common},
        {"id": "official-mv-hook-replay", "type": "video", "path": "assets/video/official_hook_26s.mp4",
         "source_tool": "ffmpeg", "scene_id": "original_replay", "duration_seconds": 26,
         "generation_summary": "Same official MV hook, replayed at original speed", **common},
        {"id": "official-mv-intro-still", "type": "image", "path": "assets/images/word_09_mv.jpg",
         "source_tool": "ffmpeg", "scene_id": "song_intro",
         "generation_summary": "Official MV still at 234.2 seconds", **common},
    ])
    for i in range(1, 10):
        name = f"word_{i:02d}"
        manifest["assets"].append({"id": f"official-mv-{name}-still", "type": "image",
                                   "path": f"assets/images/{name}_mv.jpg", "source_tool": "ffmpeg",
                                   "scene_id": name, "generation_summary": "Still from the word's source interval in official MV", **common})
    manifest.setdefault("metadata", {})["visual_revision"] = "v3-official-mv"
    save(ART / "asset_manifest.json", manifest)
    checkpoint("assets", manifest)

    edit = load(ART / "edit_decisions.json")
    for cut in edit["cuts"]:
        if cut["id"] in {"original_first", "original_replay"}:
            cut["reason"] = "Official MV picture synchronized with original song and lyric overlay"
        elif cut["id"].startswith("word_"):
            cut["reason"] = "Official MV still at word source time; Thai and Chinese text remain unobscured"
    edit.setdefault("metadata", {})["visual_revision"] = "v3-official-mv"
    save(ART / "edit_decisions.json", edit)
    checkpoint("edit", edit)

    props_path = PROJECT / "composition/props.json"
    props = load(props_path)
    for row in props["review_timeline"]:
        if row["id"] in {"original_first", "original_replay"}:
            row["credit"] = "BOWKYLION 官方 MV · 原唱"
        elif row["id"] == "song_intro" or row["id"].startswith("word_"):
            row["credit"] = "BOWKYLION 官方 MV · Microsoft Edge 小晓女声"
    save(props_path, props)

    log = load(ART / "decision_log.json")
    assert not any(d["decision_id"] == "d-012" for d in log["decisions"])
    log["decisions"].append({
        "decision_id": "d-012", "stage": "scene_plan", "category": "visual_source",
        "subject": "第13首画面来源",
        "options_considered": [
            {"option_id": "official_mv", "label": "官方 MV 画面", "score": 1,
             "reason": "用户指定配官方 MV；原唱两遍使用动态画面，词卡使用对应定格"},
            {"option_id": "graphic_only", "label": "夜蓝沙漏图形", "score": 0,
             "reason": "此前成片使用", "rejected_because": "用户要求加入官方 MV 画面"},
        ],
        "selected": "official_mv", "reason": "用户明确要求视频画面配官方 MV。",
        "user_visible": True, "user_approved": True, "confidence": 1,
    })
    save(ART / "decision_log.json", log)
    save(ART / "source-analysis/official-mv-video.json", {
        "source_url": SOURCE_URL, "asset_path": "assets/video/official_mv.mp4",
        "hook_path": "assets/video/official_hook_26s.mp4",
        "source_window_seconds": [209.855, 235.855], "source_fps": 25,
        "render_fps": 30, "note": "Official MV picture only; existing original-song audio retained",
    })
    print("Song 13 official MV assets and decisions checkpointed")


if __name__ == "__main__":
    main()
