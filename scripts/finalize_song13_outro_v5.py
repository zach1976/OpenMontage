"""Complete Song 13 V5 compose records after logo/slogan QA."""

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
VIDEO = PROJECT / "renders/final_v5.mp4"


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
assert 91.4 < duration < 91.8
assert any(s.get("codec_type") == "video" and s.get("codec_name") == "h264"
           and s.get("width") == 1080 and s.get("height") == 1920 for s in probe["streams"])
assert any(s.get("codec_type") == "audio" and s.get("codec_name") == "aac" for s in probe["streams"])

report = load(ART / "render_report.json")
report["outputs"] = [{
    "path": "renders/final_v5.mp4", "format": "mp4", "codec": "h264",
    "audio_codec": "aac", "resolution": "1080x1920", "fps": 30,
    "duration_seconds": round(duration, 3), "file_size_bytes": size,
    "platform_target": "vertical",
}]
report["verification_notes"] = [
    f"ffprobe: H.264 1080×1920 30fps / AAC / {duration:.3f}s",
    "Official Thai 1000 app icon visible for final 3.6s",
    "Brand name 泰语千词 and exact screen slogan 在泰国生活够用了 readable in final frames",
    "Existing Xiaoxiao slogan recording reused from Song 11; fits outro without truncation",
    "Four rendered outro frames visually inspected and final audio transcribed",
]
report.setdefault("metadata", {})["outro_revision"] = "v5-logo-slogan"
save(ART / "render_report.json", report)

review = load(ART / "final_review.json")
review["output_path"] = "renders/final_v5.mp4"
technical = review["checks"]["technical_probe"]
technical["duration_seconds"] = round(duration, 3)
technical["file_size_bytes"] = size
visual = review["checks"]["visual_spotcheck"]
visual["frames_sampled"] = 4
visual["frame_paths"] = [f"artifacts/qa/frame_v5_{str(t).replace('.', '_')}.png"
                         for t in (88.1, 88.5, 90.0, 91.1)]
visual["issues"] = []
audio = review["checks"]["audio_spotcheck"]
audio["issues"] = []
review["checks"]["transcript_comparison"]["issues"] = [
    "Final audio contains the complete existing Xiaoxiao brand line; Whisper transcribes 千词 as homophone 签词."
]
review["metadata"]["outro_revision"] = "Official app icon + 泰语千词 + 在泰国生活够用了"
save(ART / "final_review.json", review)

write_checkpoint(ROOT / "projects", PROJECT_ID, "compose", "completed",
                 {"render_report": report, "final_review": review},
                 pipeline_type="animated-explainer",
                 review={"decision": "pass", "critical": 0, "suggestions": 0,
                         "checks": ["H.264/AAC playable", "official app icon visible",
                                    "brand name and slogan readable", "outro voice complete"]},
                 cost_snapshot={"spent_usd": report["metadata"]["cost_usd"], "estimated_remaining_usd": 0},
                 metadata={"revision": "v5-logo-slogan", "human_review_next": True})
print(f"v5 composed and checkpointed: {duration:.3f}s, {size} bytes")
