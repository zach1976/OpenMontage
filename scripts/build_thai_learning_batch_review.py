#!/usr/bin/env python3
"""Build one Chrome-friendly review page for the three Thai learning batches."""

from __future__ import annotations

import html
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"
BUNDLE = PROJECTS / "thai-1000-missing-series-batch-review"
SERIES = [
    ("thai-1000-catchphrase-series-01-11", "经典口头禅", "#18A0AE"),
    ("thai-1000-emergency-series-01-13", "紧急应急", "#D35B4E"),
    ("thai-1000-food-series-01-09", "泰国美食", "#D7773A"),
]


def e(value: object) -> str:
    return html.escape(str(value))


def main() -> None:
    BUNDLE.mkdir(parents=True, exist_ok=True)
    sections = []
    review_summary = {"version": "1.0", "episode_count": 0, "series": []}
    for project_id, label, color in SERIES:
        project = PROJECTS / project_id
        script = json.loads((project / "artifacts" / "script.json").read_text())
        episode_cards = []
        copy_episodes = []
        for episode in script["metadata"]["episodes"]:
            eid = episode["id"]
            cfg = episode["render_config"]
            items = episode["items"]
            rows = "".join(
                f'<tr><td class="thai">{e(x["thai"])}</td><td>{e(x["homophone"])}</td><td>{e(x["chinese"])}</td><td>{e(x.get("note", ""))}</td></tr>'
                for x in items
            )
            video = f"../{project_id}/renders/{eid}.mp4"
            cover = f"../{project_id}/renders/covers/{eid}-cover.jpg"
            landscape_cover = f"../{project_id}/renders/covers/{eid}-cover-16x9.jpg"
            episode_cards.append(f'''<article class="episode" id="{project_id}-{eid}" style="--accent:{color}">
              <div class="video"><video controls preload="metadata" poster="{cover}" src="{video}"></video><div class="cover-ready"><strong>封面已绑定</strong><span>入库时自动上传首帧封面，无需下载</span></div><div class="crop-label">中央裁切后的横屏效果</div><img class="landscape-cover" src="{landscape_cover}" alt="{e(cfg['topic'])} 横屏封面预览"></div>
              <div class="copy"><div class="ephead"><div><span>{e(cfg["episode"])}</span><h3>{e(cfg["topic"])}</h3></div><label><input type="checkbox" data-key="{project_id}-{eid}"> 已审核</label></div>
              <p class="hook">开场：{e(cfg["hook"])}</p>
              <table><thead><tr><th>泰语</th><th>谐音</th><th>中文</th><th>提示</th></tr></thead><tbody>{rows}</tbody></table></div>
            </article>''')
            copy_episodes.append({
                "episode": cfg["episode"], "title": cfg["topic"], "hook": cfg["hook"],
                "dialogue": [{"role": f"词句 {i:02d}", "th": x["thai"], "rom": x["homophone"], "zh": x["chinese"]} for i, x in enumerate(items, 1)],
                "analysis": [], "replay": "每条均按泰语先念、中文紧接的顺序播放。",
            })
        (project / "artifacts" / "review_copy.json").write_text(json.dumps({"version": "1.0", "episodes": copy_episodes}, ensure_ascii=False, indent=2) + "\n")
        review_summary["episode_count"] += len(episode_cards)
        review_summary["series"].append({"project_id": project_id, "label": label, "episodes": len(episode_cards)})
        sections.append(f'<section><h2 style="--accent:{color}">{e(label)} <small>{len(episode_cards)} 集</small></h2>{"".join(episode_cards)}</section>')

    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>泰语补充系列 · 33集审核</title>
<style>
:root{{--bg:#09131f;--panel:#122238;--line:#28405e;--ink:#f3efe5;--muted:#9cacbf}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}}header{{position:sticky;top:0;z-index:4;padding:18px 28px;background:rgba(9,19,31,.94);border-bottom:1px solid var(--line);backdrop-filter:blur(12px)}}h1{{margin:0;font-size:24px}}header p{{margin:5px 0 0;color:var(--muted)}}main{{max-width:1500px;margin:auto;padding:26px}}h2{{border-left:6px solid var(--accent);padding-left:13px;margin:28px 0 16px}}h2 small{{font-size:14px;color:var(--muted);font-weight:500}}.episode{{display:grid;grid-template-columns:300px 1fr;gap:22px;background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent);border-radius:18px;padding:18px;margin-bottom:22px}}video{{width:100%;aspect-ratio:9/16;background:#000;border-radius:12px}}.cover-ready{{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:10px;padding:9px 11px;border:1px solid #2e725f;border-radius:10px;background:#12382f;color:#dff9ee;font-size:12px}}.cover-ready strong{{color:#70e0bb;white-space:nowrap}}.crop-label{{margin-top:13px;color:var(--muted);font-size:12px}}.landscape-cover{{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;margin-top:6px;border:1px solid var(--line);border-radius:10px;background:#000}}.ephead{{display:flex;justify-content:space-between;align-items:center}}.ephead span{{color:var(--accent);font-weight:800}}h3{{font-size:25px;margin:2px 0}}label{{color:var(--muted)}}.hook{{font-size:17px;margin:8px 0 14px}}table{{width:100%;border-collapse:collapse}}th,td{{border-bottom:1px solid var(--line);padding:8px 9px;text-align:left;vertical-align:top}}th{{color:var(--muted);font-size:12px}}.thai{{font-family:Sarabun,"Noto Sans Thai",sans-serif;font-size:18px;font-weight:700}}@media(max-width:800px){{main{{padding:12px}}.episode{{grid-template-columns:1fr}}.video{{max-width:330px;margin:auto}}table{{font-size:12px}}}}
</style></head><body><header><h1>泰语补充系列 · 33 集统一审核</h1><p>经典口头禅 11 集 · 紧急应急 13 集 · 泰国美食 9 集｜已入库 Video Publisher｜33 条封面均已自动绑定</p></header><main>{''.join(sections)}</main>
<script>document.querySelectorAll('[data-key]').forEach(x=>{{x.checked=localStorage.getItem('thai-review-'+x.dataset.key)==='1';x.onchange=()=>localStorage.setItem('thai-review-'+x.dataset.key,x.checked?'1':'0')}})</script></body></html>'''
    (BUNDLE / "review.html").write_text(page)
    (BUNDLE / "review_summary.json").write_text(json.dumps(review_summary, ensure_ascii=False, indent=2) + "\n")
    print(BUNDLE / "review.html")


if __name__ == "__main__":
    main()
