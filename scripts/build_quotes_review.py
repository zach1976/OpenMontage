#!/usr/bin/env python3
"""泰国人生小语 5 集的合并审片页 → projects/thai-quotes-202611/review.html"""
import html, json
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
P = REPO / "projects" / "thai-quotes-202611"
script = json.loads((P / "artifacts/script.json").read_text())["episodes"]
cards = []
for ep in script:
    eid = ep["episode_id"]
    rows = "".join(f"<tr><td class=th>{html.escape(l['thai'])}</td><td>{html.escape(l['chinese'])}</td></tr>" for l in ep["lines"])
    cards.append(f"""<section><h2>{eid} · {html.escape(ep['title'])} <small>{ep['duration']}s</small></h2>
<div class=row><video controls preload=metadata src="renders/{eid}.mp4" poster="renders/{eid}_cover.jpg"></video>
<div><p>封面：<b>{html.escape(ep['cover'][0])} / {html.escape(ep['cover'][1])}</b></p><table>{rows}</table>
<p><label><input type=checkbox data-k="{eid}-ok"> 通过</label> <label><input type=checkbox data-k="{eid}-no"> 打回</label></p>
<textarea data-k="{eid}-note" placeholder="备注"></textarea></div></div></section>""")
page = f"""<!doctype html><meta charset=utf-8><title>泰国人生小语 审片</title><style>
body{{font-family:-apple-system,"PingFang SC";background:#111;color:#eee;max-width:1200px;margin:auto;padding:20px}}
section{{border-top:1px solid #333;padding:16px 0}}.row{{display:flex;gap:24px}}video{{width:320px;border-radius:12px}}
td{{padding:4px 12px;border-bottom:1px solid #2a2a2a}}.th{{font-size:20px}}textarea{{width:100%;height:60px;background:#222;color:#eee}}
small{{color:#888}}</style><h1>泰国人生小语 · 5 集（推广泰语千词）</h1>
<p>参照抖音「泰语人生语录」形式，文案自写。泰语女声 Premwadee，片尾中文旁白「泰语千词，在泰国生活够用了」。</p>
{''.join(cards)}<script>document.querySelectorAll('[data-k]').forEach(el=>{{const k='tq-'+el.dataset.k;
try{{const v=localStorage.getItem(k);if(v!==null){{if(el.type==='checkbox')el.checked=v==='1';else el.value=v}}}}catch(e){{}}
el.addEventListener('input',()=>{{try{{localStorage.setItem(k,el.type==='checkbox'?(el.checked?'1':'0'):el.value)}}catch(e){{}}}})}})</script>"""
(P / "review.html").write_text(page)
print(P / "review.html")
