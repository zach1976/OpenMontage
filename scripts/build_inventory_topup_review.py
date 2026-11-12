#!/usr/bin/env python3
"""Build a Chrome review page for the September Thai/Vietnamese queue top-up."""
from __future__ import annotations

import html
import sys
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"
TAG = sys.argv[1] if len(sys.argv) > 1 else "202609"  # 批次：202609 / 202611 …
BUNDLE = PROJECTS / f"inventory-topup-{TAG}-review"
SERIES = [
    (f"thai-inventory-topup-{TAG}", "泰语待发布补齐", "#18A0AE", "泰语"),
    (f"viet-inventory-topup-{TAG}", "越南语待发布补齐", "#D65E45", "越南语"),
]


def e(value: object) -> str:
    return html.escape(str(value))


def main() -> None:
    BUNDLE.mkdir(parents=True, exist_ok=True)
    sections = []
    sections_n = []
    for project_id, label, color, language in SERIES:
        project = PROJECTS / project_id
        script = json.loads((project / "artifacts" / "script.json").read_text())
        cards = []
        for episode in script["metadata"]["episodes"]:
            eid = episode["id"]
            cfg = episode["render_config"]
            rows = "".join(
                f'<tr><td class="target">{e(x["thai"])}</td><td>{e(x["homophone"])}</td><td>{e(x["chinese"])}</td></tr>'
                for x in episode["items"]
            )
            base = f"../{project_id}/renders/{eid}"
            cards.append(f'''<article class="episode" style="--accent:{color}">
              <div class="media"><video controls preload="metadata" poster="{base}_cover.jpg" src="{base}.mp4"></video>
                <div class="badge">封面已绑定，入库后可直接使用</div>
                <p>横屏中央裁切预览</p><img src="{base}_cover_landscape.jpg" alt="横屏封面"></div>
              <div><div class="head"><div><span>{e(cfg['series_name'])} · {e(cfg['episode'])}</span><h3>{e(cfg['topic'])}</h3></div>
                <label><input type="checkbox" data-key="{project_id}-{eid}"> 已审核</label></div>
                <div class="hook"><b>开场旁白：</b>{e(cfg['hook'])}</div>
                <table><thead><tr><th>{language}</th><th>谐音</th><th>中文</th></tr></thead><tbody>{rows}</tbody></table>
                <p class="rule">播放顺序：{language}先念 → 中文紧接；含背景音乐；结尾含 App icon、slogan 与中文旁白。</p>
              </div></article>''')
        sections_n.append(len(cards))
        sections.append(f'<section><h2 style="--accent:{color}">{label}<small>{len(cards)} 条</small></h2>{"".join(cards)}</section>')
    # 同批次另走专用 builder 的片子（如教材带货），在 artifacts/publish.json 里有元数据
    extra = sorted(PROJECTS.glob("viet-book-coso-1[1-5]-*")) if TAG == "202611" else []
    if extra:
        cards = []
        for proj in extra:
            pub = json.loads((proj / "artifacts" / "publish.json").read_text())
            sc = json.loads((proj / "artifacts" / "script.json").read_text())
            lines = "".join(f'<tr><td>{e(x["label"])}</td><td colspan="2">{e(x["text"])}</td></tr>' for x in sc["sections"])
            base = f"../{proj.name}/renders/v1"
            cards.append(f'''<article class="episode" style="--accent:#C9473B">
              <div class="media"><video controls preload="metadata" poster="{base}_cover.jpg" src="{base}.mp4"></video>
                <p>横屏中央裁切预览</p><img src="{base}_cover_landscape.jpg" alt="横屏封面"></div>
              <div><div class="head"><div><span>越南语千词 · 教材带货</span><h3>{e(pub['title'])}</h3></div>
                <label><input type="checkbox" data-key="{proj.name}"> 已审核</label></div>
                <table><thead><tr><th>段落</th><th colspan="2">旁白</th></tr></thead><tbody>{lines}</tbody></table>
                <p class="rule">发布文案：{e(pub['publish_copy'])}</p></div></article>''')
        sections_n.append(len(cards))
        sections.append(f'<section><h2 style="--accent:#C9473B">越南语教材带货<small>{len(cards)} 条</small></h2>{"".join(cards)}</section>')
    total = sum(sections_n)
    labels = [l for _, l, _, _ in SERIES] + (["越南语教材带货"] if len(sections_n) > len(SERIES) else [])
    counts = ' · '.join(f'{l} {n} 条' for l, n in zip(labels, sections_n))
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>泰语/越南语待发布库存补齐审核</title>
<style>:root{{--bg:#081521;--panel:#10243a;--line:#29445f;--ink:#f5f2e8;--muted:#9cb0c4}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}}header{{position:sticky;top:0;z-index:3;background:rgba(8,21,33,.94);backdrop-filter:blur(12px);border-bottom:1px solid var(--line);padding:18px 28px}}h1{{margin:0;font-size:25px}}header p{{margin:5px 0 0;color:var(--muted)}}main{{max-width:1500px;margin:auto;padding:24px}}h2{{border-left:6px solid var(--accent);padding-left:12px}}h2 small{{font-size:14px;color:var(--muted);margin-left:10px}}.episode{{display:grid;grid-template-columns:310px 1fr;gap:22px;padding:18px;margin:0 0 22px;background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent);border-radius:18px}}video{{width:100%;aspect-ratio:9/16;background:#000;border-radius:12px}}.badge{{margin-top:9px;padding:9px 10px;background:#123a30;color:#86e3c0;border:1px solid #2c725e;border-radius:9px;font-size:12px}}.media p,.rule{{color:var(--muted);font-size:12px}}.media img{{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:9px;border:1px solid var(--line)}}.head{{display:flex;justify-content:space-between;align-items:flex-start;gap:18px}}.head span{{color:var(--accent);font-weight:750}}h3{{font-size:25px;margin:2px 0 10px}}label{{white-space:nowrap;color:var(--muted)}}.hook{{padding:11px 13px;border-left:3px solid var(--accent);background:#0b1c2d;margin-bottom:13px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px 9px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}}th{{font-size:12px;color:var(--muted)}}.target{{font-size:18px;font-weight:750}}@media(max-width:800px){{main{{padding:12px}}.episode{{grid-template-columns:1fr}}.media{{max-width:340px;margin:auto}}table{{font-size:12px}}}}</style></head>
<body><header><h1>泰语 / 越南语待发布库存补齐 · {TAG} · {total} 条</h1><p>{counts}｜具体文案、竖屏封面、横屏中央裁切封面与成片统一审核</p></header><main>{''.join(sections)}</main>
<script>document.querySelectorAll('[data-key]').forEach(x=>{{x.checked=localStorage.getItem('inventory-topup-{TAG}-'+x.dataset.key)==='1';x.onchange=()=>localStorage.setItem('inventory-topup-{TAG}-'+x.dataset.key,x.checked?'1':'0')}})</script></body></html>'''
    (BUNDLE / "review.html").write_text(page)
    (BUNDLE / "project.json").write_text(json.dumps({"version":"1.0","project_id":BUNDLE.name,"title":"泰语/越南语待发布库存补齐审核","pipeline_type":"animated-explainer"}, ensure_ascii=False, indent=2)+"\n")
    print(BUNDLE / "review.html")


if __name__ == "__main__":
    main()
