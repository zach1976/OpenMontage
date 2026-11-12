"""Render one Song 13 two-line derivative through OpenMontage VideoCompose."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import write_checkpoint
from tools.video.video_compose import VideoCompose

IDS = {"first": "thai-1000-song-13-first-two-lines", "last": "thai-1000-song-13-last-two-lines"}
if len(sys.argv) != 2 or sys.argv[1] not in IDS:
    raise SystemExit("Usage: render_song13_split.py first|last")
project = ROOT / "projects" / IDS[sys.argv[1]]
art = project / "artifacts"
edit = json.loads((art / "edit_decisions.json").read_text())
proposal = json.loads((art / "proposal_packet.json").read_text())
assets = json.loads((art / "asset_manifest.json").read_text())
out = project / "renders/final-v1.mp4"
write_checkpoint(ROOT / "projects", project.name, "compose", "in_progress", {},
                 pipeline_type="animated-explainer", metadata={"partial_progress": {"rendering": out.name}})
result = VideoCompose().execute({"operation": "render", "edit_decisions": edit,
                                "proposal_packet": proposal, "asset_manifest": assets,
                                "output_path": str(out)})
if not result.success:
    print(f"render failed: {result.error}", file=sys.stderr)
    raise SystemExit(2)
print(out, out.stat().st_size)
