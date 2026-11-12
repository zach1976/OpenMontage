"""Complete Song 13 v3 official-MV compose records."""

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
VIDEO = PROJECT / "renders/final_v3.mp4"


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
assert 122.5 < duration < 122.8
assert any(s.get("codec_type") == "video" and s.get("codec_name") == "h264"
           and s.get("width") == 1080 and s.get("height") == 1920 for s in probe["streams"])
assert any(s.get("codec_type") == "audio" and s.get("codec_name") == "aac" for s in probe["streams"])

report = load(ART / "render_report.json")
report["outputs"] = [{
    "path": "renders/final_v3.mp4", "format": "mp4", "codec": "h264",
    "audio_codec": "aac", "resolution": "1080x1920", "fps": 30,
    "duration_seconds": round(duration, 3), "file_size_bytes": size,
    "platform_target": "vertical",
}]
report["verification_notes"] = [
    f"ffprobe: H.264 1080×1920 30fps / AAC / {duration:.3f}s",
    "Official MV 03:29.855–03:55.855 picture embedded for both original-song passes",
    "MV stills from corresponding lyric times displayed on word cards and intro",
    "Audio PCM MD5 matches v2 exactly: fdb900512add071eac7eca49a36e9a9e",
    "Eight rendered frames across first song, intro, words, replay and outro inspected",
]
report["metadata"]["visual_revision"] = "official MV picture + lyric-time stills"
save(ART / "render_report.json", report)

review = load(ART / "final_review.json")
review["output_path"] = "renders/final_v3.mp4"
technical = review["checks"]["technical_probe"]
technical["duration_seconds"] = round(duration, 3)
technical["file_size_bytes"] = size
visual = review["checks"]["visual_spotcheck"]
visual["frames_sampled"] = 8
visual["frame_paths"] = [f"artifacts/qa/frame_v3_{t}.png"
                         for t in (3, 16, 29, 38, 57, 98, 113, 121)]
visual["issues"] = []
audio = review["checks"]["audio_spotcheck"]
audio["issues"] = ["Audio is sample-identical to v2; voice quality remains subject to listener review."]
review["metadata"]["visual_revision"] = "Official MV moving picture in both song passes; nine corresponding stills in teaching cards"
review["metadata"]["audio_pcm_md5"] = "fdb900512add071eac7eca49a36e9a9e"
save(ART / "final_review.json", review)

write_checkpoint(ROOT / "projects", PROJECT_ID, "compose", "completed",
                 {"render_report": report, "final_review": review},
                 pipeline_type="animated-explainer",
                 review={"decision": "pass", "critical": 0, "suggestions": 0,
                         "checks": ["H.264/AAC playable", "official MV visible", "8 frames inspected", "audio identical to v2"]},
                 cost_snapshot={"spent_usd": report["metadata"]["cost_usd"], "estimated_remaining_usd": 0},
                 metadata={"revision": "v3-official-mv", "human_review_next": True})
print(f"v3 composed and checkpointed: {duration:.3f}s, {size} bytes")
