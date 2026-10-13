"""Record review and checkpoints for song 12's standalone V4 narration."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import write_checkpoint

P = ROOT / "projects/thai-1000-song-12-sai-naen-hua-jai"
A = P / "artifacts"


def read(name: str) -> dict:
    return json.loads((A / name).read_text())


def save(name: str, value: dict) -> None:
    (A / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


assert (P / "renders/final-v4.mp4").is_file()
assert (P / "renders/cover-v4.jpg").is_file()
assert (P / "renders/qa-sheet-v4.jpg").is_file()

report = copy.deepcopy(read("render_report_v3.json"))
report["outputs"][0]["path"] = "renders/final-v4.mp4"
report["outputs"][0]["file_size_bytes"] = (P / "renders/final-v4.mp4").stat().st_size
report["metadata"]["cover_path"] = "renders/cover-v4.jpg"
report["verification_notes"] = [
    "V4 removes the cross-episode reference from the bridge narration.",
    "The rendered bridge was transcribed: 接下来，我们把这段副歌一句一句地拆开，逐词听懂每一句 (one low-confidence ASR word).",
    "Six chorus lines and 32 phrase cards remain; all 101 audio references resolve.",
    "H.264 1080x1920 at 30 fps, 48 kHz AAC, and 160.81 seconds verified by ffprobe.",
    "Nine timeline samples inspected; no silence longer than 0.8 seconds at -40 dBFS; audio peak -5.3 dBFS.",
]
save("render_report.json", report)
save("render_report_v4.json", report)

review = copy.deepcopy(read("final_review_v3.json"))
review["output_path"] = "renders/final-v4.mp4"
review["checks"]["visual_spotcheck"]["frames_sampled"] = 9
review["checks"]["visual_spotcheck"]["frame_paths"] = ["renders/qa-sheet-v4.jpg"]
review["metadata"]["revision"] = "v4-self-contained"
review["metadata"]["bridge_transcript_checked"] = True
save("final_review.json", review)
save("final_review_v4.json", review)

save("edit_decisions_v4.json", read("edit_decisions.json"))

for stage, artifact in (
    ("script", "script"),
    ("assets", "asset_manifest"),
    ("compose", "render_report"),
):
    artifacts = {artifact: read(f"{artifact}.json")}
    if stage == "compose":
        artifacts["final_review"] = review
    write_checkpoint(
        ROOT / "projects", P.name, stage, "completed", artifacts,
        pipeline_type="animated-explainer",
        human_approved=stage in {"script", "assets"},
        review={"decision": "pass", "critical": 0, "suggestions": 0},
        metadata={"revision": "v4-self-contained", "approval_source": "Recorded V4 full-run authorization in decision_log"},
    )

print(P / "renders/final-v4.mp4")
