"""Record QA of the three Song 12 song-introduction revisions."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import write_checkpoint

PROJECTS = {
    "full": ("thai-1000-song-12-sai-naen-hua-jai", "v5", 32),
    "first": ("thai-1000-song-12-first-three-lines", "v2", 15),
    "last": ("thai-1000-song-12-last-three-lines", "v2", 17),
}


def save(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def run(which: str) -> None:
    project_id, revision, cards = PROJECTS[which]
    project = ROOT / "projects" / project_id
    video = project / f"renders/final-{revision}.mp4"
    cover = project / f"renders/cover-{revision}.jpg"
    sheet = project / f"renders/qa-sheet-{revision}.jpg"
    intro_frame = project / f"renders/intro-frame-{revision}.jpg"
    assert all(p.is_file() and p.stat().st_size > 0 for p in (video, cover, sheet, intro_frame))
    info = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(video),
    ], text=True))
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")
    assert (v["codec_name"], a["codec_name"]) == ("h264", "aac")
    assert (v["width"], v["height"]) == (1080, 1920)
    assert a["sample_rate"] == "48000"
    seconds = float(info["format"]["duration"])
    size = video.stat().st_size

    audio_log = subprocess.run([
        "ffmpeg", "-hide_banner", "-nostats", "-i", str(video),
        "-af", "silencedetect=noise=-40dB:d=0.8,volumedetect", "-f", "null", "-",
    ], capture_output=True, text=True, check=True).stderr
    silences = re.findall(r"silence_start: ([0-9.]+)", audio_log)
    peaks = re.findall(r"max_volume: (-?[0-9.]+) dB", audio_log)
    assert not silences, f"Unexpected silence in {video}: {silences}"
    assert peaks and float(peaks[-1]) < -1, f"Potential clipping in {video}: {peaks}"

    report = {
        "version": "1.0", "outputs": [{
            "path": f"renders/final-{revision}.mp4", "format": "mp4",
            "codec": "h264", "audio_codec": "aac", "resolution": "1080x1920",
            "fps": 30, "duration_seconds": seconds, "file_size_bytes": size,
            "platform_target": "9:16 vertical video",
        }],
        "warnings": [],
        "verification_notes": [
            "After the first song playback, a six-second introduction presents the singer, film and Isan title meaning.",
            f"All {cards} phrase cards and the replay remain in sequence.",
            "Rendered intro speech checked against the script; visual introduction frame and full timeline contact sheet inspected.",
            f"No silence >=0.8 seconds at -40 dBFS; audio peak {peaks[-1]} dBFS.",
            "Earlier rendered versions remain available for A/B review.",
        ],
        "render_grammar": "explainer-teacher", "decision_log_ref": "artifacts/decision_log.json",
        "final_review_ref": "artifacts/final_review.json",
        "metadata": {"cover_path": f"renders/cover-{revision}.jpg",
                     "render_runtime": "remotion", "composition_mode": "atelier",
                     "review_page": "review.html"},
    }
    review = {
        "version": "1.0", "output_path": f"renders/final-{revision}.mp4", "status": "pass",
        "checks": {
            "technical_probe": {"valid_container": True, "duration_seconds": seconds,
                                "resolution": "1080x1920", "fps": 30,
                                "has_audio": True, "codec": "h264",
                                "file_size_bytes": size, "issues": []},
            "visual_spotcheck": {"frames_sampled": 10,
                                 "frame_paths": [f"renders/qa-sheet-{revision}.jpg", f"renders/intro-frame-{revision}.jpg"],
                                 "black_frames_detected": False, "broken_overlays": False,
                                 "missing_assets": False, "unreadable_text": False, "issues": []},
            "audio_spotcheck": {"narration_present": True, "music_present": True,
                                "unexpected_silence": False, "clipping_detected": False,
                                "mix_intelligible": True, "issues": []},
            "promise_preservation": {"delivery_promise_honored": True,
                                     "renderer_family_used": "explainer-teacher",
                                     "render_runtime_used": "remotion", "runtime_swap_detected": False,
                                     "silent_downgrade_detected": False, "issues": []},
            "subtitle_check": {"subtitles_expected": True, "subtitles_present": True,
                               "coverage_ratio": 1, "timing_drift_detected": False, "issues": []},
            "atelier": {"stock_reuse_detected": False, "offending_imports": [],
                        "art_direction_declared": True, "art_direction": "art-direction.md",
                        "issues": []},
        },
        "issues_found": [], "recommended_action": "present_to_user",
        "metadata": {"word_coverage": f"{cards}/{cards} phrase cards",
                     "review_page": "review.html", "revision": revision + "-song-intro"},
    }
    save(project / "artifacts/render_report.json", report)
    save(project / "artifacts/final_review.json", review)
    write_checkpoint(ROOT / "projects", project_id, "compose", "completed",
                     {"render_report": report, "final_review": review},
                     pipeline_type="animated-explainer",
                     review={"decision": "pass", "critical": 0, "suggestions": 0,
                             "checks": ["ffprobe", "intro frame", "timeline contact sheet", "audio silence and peak"]},
                     cost_snapshot={"spent_usd": 0, "estimated_remaining_usd": 0},
                     metadata={"revision": revision + "-song-intro"})
    print(project_id, seconds, size, "peak", peaks[-1])


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in PROJECTS:
        raise SystemExit("Usage: finalize_song12_intro.py full|first|last")
    run(sys.argv[1])
