#!/usr/bin/env python3
"""Write approved Remotion edit decisions after narration timing is locked."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"
ENTRY = ROOT / "projects/thai-alphabet-pinkfong-lesson-batch/index.tsx"


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def one(project: Path) -> None:
    art = project / "artifacts"
    props = json.loads((art / "props.json").read_text())
    script = json.loads((art / "script.json").read_text())
    manifest = json.loads((art / "asset_manifest.json").read_text())
    if not any(item["id"] == "narration" for item in manifest["assets"]):
        manifest["assets"].append({
            "id": "narration", "type": "narration", "path": "public/narration",
            "source_tool": "azure_tts", "scene_id": "all",
            "model": "Azure Speech F0 XiaoxiaoNeural chat-casual / PremwadeeNeural standard",
            "cost_usd": 0,
            "generation_summary": "Mandarin explanation and standard Thai reading; each word follows a sung source excerpt."})
    manifest["metadata"]["narration_pending"] = False
    manifest["metadata"]["source_vs_generated_map"] = "Pinkfong source footage, stills and sung word excerpts; Azure F0 standard narration; approved app visuals"
    save(art / "asset_manifest.json", manifest)

    cuts = []
    for section in script["sections"]:
        section_id = section["id"]
        if section_id in {"song", "recap"}:
            source = "source_song"
        elif section_id.startswith("lesson_l"):
            source = "still_" + section_id.removeprefix("lesson_")
        elif section_id == "outro":
            source = "app_home"
        else:
            source = "still_" + props["lessons"][0]["id"]
        cuts.append({"id": section_id, "source": source, "in_seconds": section["start_seconds"],
                     "out_seconds": section["end_seconds"], "layer": "primary",
                     "reason": "Approved source-led teaching order: song, sung word, Thai reading, Mandarin meaning."})
    edit = {"version": "1.0", "renderer_family": "explainer-teacher", "render_runtime": "remotion",
            "composition_mode": "atelier", "cuts": cuts,
            "bespoke": {"entry": str(ENTRY), "composition_id": "PinkfongAlphabetLesson",
                        "props_path": str((art / "props.json").resolve()),
                        "public_dir": str((project / "public").resolve()),
                        "crf": 18, "timeout_ms": 180000, "concurrency": 2,
                        "art_direction": "Approved Pinkfong letter visuals and bilingual word-card teaching treatment"},
            "metadata": {"proposal_render_runtime": "remotion", "sample_reference": "thai-alphabet-pinkfong-01-lesson/renders/final_azure.mp4",
                         "source_url": script["metadata"]["source_url"],
                         "source_windows_seconds": script["metadata"]["source_windows_seconds"],
                         "subtitles": "Thai source lyric above its Chinese meaning",
                         "word_card_order": "source sung excerpt, standard Thai reading, Mandarin meaning",
                         "duration_seconds": props["totalFrames"] / 30,
                         "approval_policy": "final videos only"}}
    save(art / "edit_decisions.json", edit)
    print(f"{project.name}: edit ready, {props['totalFrames']/30:.1f}s")


def main() -> None:
    ids = sys.argv[1:] or [f"thai-alphabet-pinkfong-{i:02d}-lesson" for i in range(2, 16)]
    for project_id in ids:
        one(PROJECTS / project_id)


if __name__ == "__main__":
    main()
