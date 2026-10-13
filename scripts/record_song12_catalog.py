"""Verify and checkpoint the user-approved Song 12 Video Publisher ingest."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import write_checkpoint

ITEMS = (
    ("thai-1000-song-12-sai-naen-hua-jai", "v5", "843"),
    ("thai-1000-song-12-first-three-lines", "v2", "845"),
    ("thai-1000-song-12-last-three-lines", "v2", "846"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


for project_id, revision, expected_id in ITEMS:
    project = ROOT / "projects" / project_id
    art = project / "artifacts"
    manifest_path = art / "publish.json"
    manifest = json.loads(manifest_path.read_text())
    log = json.loads((art / "publish_log.json").read_text())
    latest = log["entries"][0]
    assert latest["video_id"] == expected_id
    assert log["metadata"]["source_mp4"] == f"final-{revision}.mp4"
    assert latest["status"] == "pending_review"
    source_video = project / manifest["video_path"]
    catalog_video = Path(latest["export_path"])
    source_cover = project / manifest["cover_path"]
    catalog_cover = catalog_video.with_name(catalog_video.stem + "_cover.jpg")
    assert sha256(source_video) == sha256(catalog_video)
    assert sha256(source_cover) == sha256(catalog_cover)
    manifest["note"] = f"已入库 Video Publisher（video_id={expected_id}，stage=ready），尚未公开发布。"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    write_checkpoint(
        ROOT / "projects", project_id, "publish", "in_progress", {},
        pipeline_type="animated-explainer",
        metadata={"video_id": expected_id, "source_mp4": source_video.name},
    )
    write_checkpoint(
        ROOT / "projects", project_id, "publish", "completed", {"publish_log": log},
        pipeline_type="animated-explainer", human_approved=True,
        review={"decision": "pass", "critical": 0, "suggestions": 0,
                "checks": ["User approved all three videos for ingest",
                           "Video Publisher returned stage=ready and cover=yes",
                           "Video and cover SHA-256 match library copies"]},
        cost_snapshot={"spent_usd": 0, "estimated_remaining_usd": 0},
        metadata={"approval_source": "用户明确说三个都可以入库了",
                  "video_id": expected_id, "source_mp4": source_video.name},
    )
    print(project_id, expected_id, source_video.name, "verified")
