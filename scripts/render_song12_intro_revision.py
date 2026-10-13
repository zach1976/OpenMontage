"""Render one of the three Song 12 song-introduction revisions."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import write_checkpoint
from tools.video.video_compose import VideoCompose

PROJECTS = {
    "full": ("thai-1000-song-12-sai-naen-hua-jai", "v5"),
    "first": ("thai-1000-song-12-first-three-lines", "v2"),
    "last": ("thai-1000-song-12-last-three-lines", "v2"),
}

if len(sys.argv) != 2 or sys.argv[1] not in PROJECTS:
    raise SystemExit("Usage: render_song12_intro_revision.py full|first|last")

project_id, revision = PROJECTS[sys.argv[1]]
project = ROOT / "projects" / project_id
art = project / "artifacts"
edit = json.loads((art / "edit_decisions.json").read_text())
proposal = json.loads((art / "proposal_packet.json").read_text())
manifest = json.loads((art / "asset_manifest.json").read_text())
out = project / f"renders/final-{revision}.mp4"

write_checkpoint(ROOT / "projects", project_id, "compose", "in_progress", {},
                 pipeline_type="animated-explainer",
                 metadata={"partial_progress": {"rendering": out.name}})
result = VideoCompose().execute({
    "operation": "render", "edit_decisions": edit,
    "proposal_packet": proposal, "asset_manifest": manifest,
    "output_path": str(out),
})
if not result.success:
    print(f"render failed: {result.error}", file=sys.stderr)
    raise SystemExit(2)
print(out, out.stat().st_size)
