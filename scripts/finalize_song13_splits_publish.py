"""Record the user's catalog approval for the two Song 13 derivative episodes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import write_checkpoint

EXPECTED = {
    "thai-1000-song-13-first-two-lines": "877",
    "thai-1000-song-13-last-two-lines": "878",
}
for project_id, video_id in EXPECTED.items():
    project = ROOT / "projects" / project_id
    art = project / "artifacts"
    publish_log = json.loads((art / "publish_log.json").read_text())
    entry = publish_log["entries"][0]
    assert entry["video_id"] == video_id, (project_id, entry)
    assert Path(entry["export_path"]).exists(), entry["export_path"]
    decisions_path = art / "decision_log.json"
    decisions = json.loads(decisions_path.read_text())
    if not any(d.get("decision_id") == "catalog-approved" for d in decisions["decisions"]):
        decisions["decisions"].append({
            "decision_id": "catalog-approved", "stage": "publish",
            "category": "publish_approval", "subject": "第13首拆分集入库",
            "options_considered": [
                {"option_id": "catalog", "label": "入库", "score": 1,
                 "reason": "用户明确说新的两集也可以入库"},
                {"option_id": "hold", "label": "继续待审", "score": 0,
                 "reason": "用户已经完成审片并批准"}],
            "selected": "catalog", "reason": "用户本轮明确批准两集入库。",
            "user_visible": True, "user_approved": True,
        })
        decisions_path.write_text(json.dumps(decisions, ensure_ascii=False, indent=2) + "\n")
    write_checkpoint(ROOT / "projects", project_id, "publish", "completed",
                     {"publish_log": publish_log}, pipeline_type="animated-explainer",
                     human_approved=True,
                     review={"decision": "pass", "critical": 0, "suggestions": 0,
                             "checks": ["videopublisher returned stage=ready", "cover bound", "catalog video ID verified"]},
                     cost_snapshot={"spent_usd": 0, "estimated_remaining_usd": 0},
                     metadata={"user_approval": "新的两集也可以入库了", "video_id": video_id})
    print(project_id, video_id, "cataloged")
