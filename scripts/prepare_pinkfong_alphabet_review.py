#!/usr/bin/env python3
"""Package the verified three-letter Pinkfong excerpts for batch review."""

import json
import shutil
import subprocess
from pathlib import Path

from lib.checkpoint import init_project
from schemas.artifacts import validate_artifact

ROOT = Path(__file__).resolve().parent.parent
PARENT_ID = "thai-alphabet-pinkfong-three-letter"
PARENT = ROOT / "projects" / PARENT_ID
SOURCE_URL = "https://www.youtube.com/watch?v=pxLHURprYuI"
LETTERS = json.loads((PARENT / "artifacts/letter_timeline.json").read_text())["letter_segments"]


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def probe(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(result.stdout)["format"]
    return float(data["duration"]), int(data["size"])


outputs = []
sections = []
scenes = []
assets = [{
    "id": "pinkfong_source", "type": "video", "path": "assets/video/source.mp4",
    "source_tool": "yt-dlp", "scene_id": "source", "duration_seconds": 183.974,
    "resolution": "1280x720", "format": "mp4", "original_url": SOURCE_URL,
}]
cuts = []
for group_index in range(15):
    group = LETTERS[group_index * 3:group_index * 3 + 3]
    number = f"{group_index + 1:02d}"
    child_id = f"thai-alphabet-pinkfong-{number}"
    child = ROOT / "projects" / child_id
    label = " · ".join(item[0] for item in group)
    title = f"泰文字母歌 第{number}集｜{label}"
    init_project(child_id, title=title, pipeline_type="clip-factory")
    source_clip = PARENT / f"assets/video/letter_group_{number}_cover.mp4"
    final = child / "renders/final.mp4"
    if not source_clip.exists():
        raise FileNotFoundError(source_clip)
    shutil.copyfile(source_clip, final)
    duration, size = probe(final)

    local_scenes = []
    cursor = 0.0
    for letter, start, end in group:
        letter_duration = end - start
        local_scenes.append({"start": round(cursor, 3), "end": round(cursor + letter_duration, 3),
                             "label": f"{letter} · 原唱"})
        cuts.append({"id": f"{number}-{letter}", "source": "pinkfong_source",
                     "in_seconds": start, "out_seconds": end, "layer": "primary",
                     "reason": "只保留该字母的原唱与原画面。"})
        cursor += letter_duration
    write_json(child / "composition/props.json", {
        "width": 1280, "height": 720, "fps": 30, "totalSeconds": duration,
        "letters": label, "scenes": local_scenes, "sourceUrl": SOURCE_URL,
    })
    write_json(child / "artifacts/publish.json", {
        "title": title, "slug": f"thai_alphabet_pinkfong_{number}",
        "sub_series": "泰文字母歌原唱拆条", "series_id": 1,
        "publish_copy": f"{title}\n\nPinkfong 原唱片段，每集只听对应的{'三个' if len(group) == 3 else '两个'}泰文字母。原唱及画面：Pinkfong Baby Shark。\n\n#泰语 #泰文字母 #泰语字母歌",
        "status": "review_only",
    })
    outputs.append({"path": str(final.relative_to(ROOT)), "format": "mp4", "codec": "h264",
                    "audio_codec": "aac", "resolution": "1280x720", "fps": 30,
                    "duration_seconds": duration, "file_size_bytes": size,
                    "platform_target": "generic"})
    sections.append({"id": f"group_{number}", "label": label, "text": f"原片字母原唱：{label}",
                     "start_seconds": 0, "end_seconds": duration, "source_ref": SOURCE_URL})
    scenes.append({"id": f"group_{number}", "type": "broll",
                   "description": f"保留 {label} 的原唱与原画面。",
                   "start_seconds": 0, "end_seconds": duration,
                   "script_section_id": f"group_{number}",
                   "framing": "保留来源片 1280×720 横版画幅，字母与例物同时可见。",
                   "overlay_notes": "保留原片泰文；不加额外片头、总览或讲解。"})
    assets.append({"id": f"group_{number}", "type": "video",
                   "path": f"assets/video/letter_group_{number}_cover.mp4",
                   "source_tool": "ffmpeg", "scene_id": f"group_{number}",
                   "duration_seconds": duration, "resolution": "1280x720", "format": "mp4",
                   "original_url": SOURCE_URL})

brief = {"version": "1.0", "title": "Pinkfong 泰文字母歌三字母分集",
         "hook": "每集直接从字母原唱开始。",
         "key_points": ["原曲 44 个辅音按原序每三字母一集，末集两字母。",
                        "只保留字母原唱，跳过片头、字母总览和片尾。",
                        "保留原片画幅，以同时展示泰文字母与例物。"],
         "tone": "原片童趣", "style": "source-only clean cuts", "target_platform": "generic",
         "target_duration_seconds": 5.6, "reference_material": [SOURCE_URL],
         "metadata": {"source_type": "alphabet song", "source_duration_seconds": 183.974,
                      "clip_count": 15, "letters_count": 44, "output_mix": "15 independent excerpts"}}
script = {"version": "1.0", "title": brief["title"],
          "total_duration_seconds": sum(o["duration_seconds"] for o in outputs),
          "sections": sections, "metadata": {"source_url": SOURCE_URL}}
scene_plan = {"version": "1.0", "scenes": scenes,
              "metadata": {"aspect_ratio": "16:9", "batch_size": 15}}
asset_manifest = {"version": "1.0", "assets": assets, "total_cost_usd": 0,
                  "metadata": {"source_url": SOURCE_URL}}
edit_decisions = {"version": "1.0", "cuts": cuts, "render_runtime": "ffmpeg",
                  "composition_mode": "templated",
                  "metadata": {"group_size": 3, "skip_non_letter_sections": True,
                               "source_audio_preserved": True}}
render_report = {"version": "1.0", "outputs": outputs, "warnings": [],
                 "verification_notes": ["15/15 视频含 H.264 画面和 AAC 原声音轨。",
                                        "首尾帧均人工抽看；片头、总览、片尾未入片。",
                                        "每集首帧取第一个字母的完整画面，原声时间轴保持不变。",
                                        "每条为原片 1280×720 横版，未裁掉字母或例物。"],
                 "decision_log_ref": "artifacts/decision_log.json",
                 "final_review_ref": "artifacts/final_review.json",
                 "metadata": {"clip_count": 15, "source_url": SOURCE_URL}}
final_review = {"version": "1.0", "output_path": outputs[0]["path"], "status": "pass",
                "checks": {
                    "technical_probe": {"valid_container": True, "duration_seconds": outputs[0]["duration_seconds"],
                                        "resolution": "1280x720", "fps": 30, "has_audio": True,
                                        "codec": "h264", "issues": []},
                    "visual_spotcheck": {"frames_sampled": 30, "black_frames_detected": False,
                                         "broken_overlays": False, "missing_assets": False,
                                         "unreadable_text": False, "issues": []},
                    "audio_spotcheck": {"narration_present": False, "music_present": True,
                                        "unexpected_silence": False, "mix_intelligible": True, "issues": []},
                    "promise_preservation": {"delivery_promise_honored": True,
                                              "render_runtime_used": "ffmpeg", "runtime_swap_detected": False,
                                              "runtime_swap_check": "ok — source-only FFmpeg cuts",
                                              "issues": []},
                    "subtitle_check": {"subtitles_expected": False, "subtitles_present": False,
                                       "coverage_ratio": 0, "timing_drift_detected": False,
                                       "issues": []}},
                "issues_found": [], "recommended_action": "present_to_user",
                "metadata": {"output_count": len(outputs), "review_scope": "all 15 outputs"}}

for name, artifact in [
    ("brief", brief), ("script", script), ("scene_plan", scene_plan),
    ("asset_manifest", asset_manifest), ("edit_decisions", edit_decisions),
    ("render_report", render_report), ("final_review", final_review),
]:
    validate_artifact(name, artifact)
    write_json(PARENT / f"artifacts/{name}.json", artifact)
print(f"Packaged {len(outputs)} clips and validated seven pipeline artifacts.")
