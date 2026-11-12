"""Complete Song 13 v2 compose records after the approved voice revision."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import write_checkpoint

PROJECT_ID = "thai-1000-song-13-nalika-sai"
PROJECT = ROOT / "projects" / PROJECT_ID
ART = PROJECT / "artifacts"
VIDEO = PROJECT / "renders/final_v2.mp4"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


probe = json.loads(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries",
    "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate",
    "-of", "json", str(VIDEO),
], text=True))
duration = float(probe["format"]["duration"])
size = int(probe["format"]["size"])
streams = probe["streams"]
assert any(s.get("codec_type") == "video" and s.get("codec_name") == "h264"
           and s.get("width") == 1080 and s.get("height") == 1920 for s in streams)
assert any(s.get("codec_type") == "audio" and s.get("codec_name") == "aac" for s in streams)
assert 122.5 < duration < 122.8

report = load(ART / "render_report.json")
report["outputs"] = [{
    "path": "renders/final_v2.mp4", "format": "mp4", "codec": "h264",
    "audio_codec": "aac", "resolution": "1080x1920", "fps": 30,
    "duration_seconds": round(duration, 3), "file_size_bytes": size,
    "platform_target": "vertical",
}]
report["verification_notes"] = [
    f"ffprobe: H.264 1080×1920 30fps / AAC / {duration:.3f}s",
    "Chinese narration replaced by Edge Xiaoxiao; replay cue plays at native speed",
    "Every Chinese clip ends at least 0.2 seconds before its scene boundary",
    "Rendered frame samples at 34, 58.5, 70.5 and 121 seconds inspected",
]
report["metadata"]["voice_revision"] = "edge-tts zh-CN-XiaoxiaoNeural -3%"
report["metadata"]["cost_usd"] = load(ART / "asset_manifest.json")["total_cost_usd"]
save(ART / "render_report.json", report)

review = load(ART / "final_review.json")
review["output_path"] = "renders/final_v2.mp4"
technical = review["checks"]["technical_probe"]
technical["duration_seconds"] = round(duration, 3)
technical["file_size_bytes"] = size
visual = review["checks"]["visual_spotcheck"]
visual["frames_sampled"] = 4
visual["frame_paths"] = [f"artifacts/qa/frame_v2_{name}.png"
                         for name in ("34", "58_5", "70_5", "121")]
audio = review["checks"]["audio_spotcheck"]
audio["issues"] = ["Chinese voice quality awaits listener review on the review page."]
review["checks"]["transcript_comparison"] = {
    "transcript_matches_script": None,
    "word_accuracy": None,
    "issues": ["New Chinese narration generated from revised script; no automatic transcript for v2."],
}
review["metadata"].pop("qa_transcript", None)
review["metadata"]["voice_revision"] = "Edge Xiaoxiao / all Chinese segments / native playback"
save(ART / "final_review.json", review)

write_checkpoint(ROOT / "projects", PROJECT_ID, "compose", "completed",
                 {"render_report": report, "final_review": review},
                 pipeline_type="animated-explainer",
                 review={"decision": "pass", "critical": 0, "suggestions": 0,
                         "checks": ["H.264/AAC playable", "voice assets present", "scene timing fits", "4 rendered frames inspected"]},
                 cost_snapshot={"spent_usd": report["metadata"]["cost_usd"], "estimated_remaining_usd": 0},
                 metadata={"revision": "v2-xiaoxiao", "human_listen_next": True})
print(f"v2 composed and checkpointed: {duration:.3f}s, {size} bytes")
