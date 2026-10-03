#!/usr/bin/env python3
"""Build per-episode Video Publisher manifests for the three Thai learning batches."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"
SERIES = [
    ("thai-1000-catchphrase-series-01-11", "经典口头禅", "thai_catchphrase"),
    ("thai-1000-emergency-series-01-13", "紧急应急", "thai_emergency"),
    ("thai-1000-food-series-01-09", "泰国美食", "thai_food"),
]


def main() -> None:
    total = 0
    for project_id, sub_series, slug_prefix in SERIES:
        project = PROJECTS / project_id
        episode_dir = project / "artifacts" / "episodes"
        episodes = []
        for source in sorted(episode_dir.glob("ep??.json")):
            data = json.loads(source.read_text())
            eid = data["id"]
            number = int(eid[2:])
            cfg = data["render_config"]
            learned = " · ".join(item["chinese"] for item in data["items"])
            title = f"泰语千词 · {sub_series} {number:02d}｜{cfg['hook']}"
            description = (
                f"{cfg['hook']}\n\n"
                f"本集会学：{learned}\n\n"
                "每条都先念泰语，再讲中文意思和中文谐音。收藏这一集，"
                "在泰国遇到对应场景就能直接开口。\n\n"
                "#泰语 #泰语学习 #泰语千词 #泰语入门 #泰国生活 #在泰华人"
            )
            episodes.append({
                "episode_id": eid,
                "series_id": 1,
                "sub_series": sub_series,
                "slug": f"{slug_prefix}_{number:02d}",
                "title": title,
                "publish_copy": description,
                "wechat_copy": f"泰语千词 · {sub_series} {number:02d}｜{cfg['hook']}",
                "video_path": f"renders/{eid}.mp4",
                "cover_path": f"renders/covers/{eid}-cover.jpg",
                "cover_landscape_path": f"renders/covers/{eid}-cover-16x9.jpg",
            })
        payload = {
            "version": "1.0",
            "series_id": 1,
            "sub_series": sub_series,
            "cover_policy": "upload_first_frame_and_bind",
            "episodes": episodes,
        }
        output = project / "artifacts" / "publish_batch.json"
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        print(project_id, len(episodes), output)
        total += len(episodes)
    print("total", total)


if __name__ == "__main__":
    main()
