"""Complete Song 13 V4 compose records after render and QA."""

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
VIDEO = PROJECT / "renders/final_v4.mp4"


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
    "path": "renders/final_v4.mp4", "format": "mp4", "codec": "h264",
    "audio_codec": "aac", "resolution": "1080x1920", "fps": 30,
    "duration_seconds": round(duration, 3), "file_size_bytes": size,
    "platform_target": "vertical",
}]
report["verification_notes"] = [
    f"ffprobe: H.264 1080×1920 30fps / AAC / {duration:.3f}s",
    "Opening official MV and song preserved in full; recap is two synchronized lyric lines, 11.07s",
    "Xiaoxiao Chinese transitions added after first play and before recap",
    "Word gloss tails trimmed; silence scan finds no >0.6s pauses in teaching cards",
    "Whisper checked the two new spoken transitions against script",
    "Nine final-render frames inspected across intro, cards, bridge, replay and outro",
]
report.setdefault("metadata", {})["pacing_revision"] = "v4-faster-transitions"
save(ART / "render_report.json", report)

review = load(ART / "final_review.json")
review["output_path"] = "renders/final_v4.mp4"
technical = review["checks"]["technical_probe"]
technical["duration_seconds"] = round(duration, 3)
technical["file_size_bytes"] = size
visual = review["checks"]["visual_spotcheck"]
visual["frames_sampled"] = 9
visual["frame_paths"] = [f"artifacts/qa/frame_v4_final_{str(t).replace('.', '_')}.png"
                         for t in (27, 32.6, 36, 44, 68, 74, 77.5, 82, 88.3)]
visual["issues"] = []
audio = review["checks"]["audio_spotcheck"]
audio["unexpected_silence"] = False
audio["issues"] = []
review["checks"]["transcript_comparison"]["issues"] = [
    "Whisper confirms both new Chinese transitions; Thai source and retained Chinese glosses were not retranscribed."
]
review["metadata"]["expected_learning_pauses"] = False
review["metadata"]["pacing_revision"] = "91.57s timeline; short card gaps; two-line recap"
review["metadata"]["visual_revision"] = "Official MV in full opening and two-line recap; nine matching teaching stills"
review["metadata"].pop("audio_pcm_md5", None)
save(ART / "final_review.json", review)

write_checkpoint(ROOT / "projects", PROJECT_ID, "compose", "completed",
                 {"render_report": report, "final_review": review},
                 pipeline_type="animated-explainer",
                 review={"decision": "pass", "critical": 0, "suggestions": 0,
                         "checks": ["H.264/AAC playable", "official MV synchronized",
                                    "9 frames inspected", "new Chinese transitions transcribed",
                                    "no long teaching-card silence"]},
                 cost_snapshot={"spent_usd": report["metadata"]["cost_usd"], "estimated_remaining_usd": 0},
                 metadata={"revision": "v4-faster-transitions", "human_review_next": True})
print(f"v4 composed and checkpointed: {duration:.3f}s, {size} bytes")
