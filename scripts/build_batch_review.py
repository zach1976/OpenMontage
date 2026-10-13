#!/usr/bin/env python3
"""一批片子的合并审片页：所有视频放在同一个页面里（用户 2026-10-12：不要每个视频开一个页面）。

    python3 scripts/build_batch_review.py <名字> <project_id 前缀或 id>... [--open]
    python3 scripts/build_batch_review.py textbook thai-book-jichu- viet-book-coso- --open

产物：projects/_review/<名字>.html（纯本地，视频用相对路径引用各项目 renders/ 下最新一版）。
页面读 composition/props.json（场景时间轴）与 artifacts/publish.json（入库文案）；
每条可标 通过/打回 + 备注（存浏览器本地），「复制审核结论」一次打包全部。
"""
from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"
OUT_DIR = PROJECTS / "_review"


def e(v: object) -> str:
    return html.escape(str(v))


def latest_mp4(p: Path) -> Path | None:
    mp4s = sorted(p.glob("renders/*.mp4"), key=lambda f: f.stat().st_mtime)
    return mp4s[-1] if mp4s else None


def card(p: Path) -> str:
    props = json.loads((p / "composition/props.json").read_text())
    pub = json.loads((p / "artifacts/publish.json").read_text()) if (p / "artifacts/publish.json").exists() else {}
    mp4 = latest_mp4(p)
    if not mp4:
        return ""
    rel = f"../{p.name}/renders/{mp4.name}"
    scenes = "".join(
        f'<li><button data-t="{s["start"]}">{s["start"]:.1f}s</button> {e(s["label"])}</li>' for s in props.get("scenes", []))
    tags = " ".join(f'<span class="tag{" hot" if t == "#带货" else ""}">{e(t)}</span>'
                    for t in pub.get("publish_copy", "").split() if t.startswith("#"))
    copy = e(pub.get("publish_copy", "").split("\n\n#")[0]).replace("\n", "<br>")
    acct = {1: "泰语千词", 2: "越南语千词"}.get(pub.get("series_id"), "")
    return f'''<article class="ep" data-id="{e(p.name)}">
  <video controls preload="metadata" src="{e(rel)}"></video>
  <div class="info">
    <div class="top"><b>{e(pub.get("title", p.name))}</b><span class="dur">{props["totalSeconds"]:.1f}s</span></div>
    <div class="meta">{e(acct)} · {e(pub.get("sub_series", ""))} · <code>{e(pub.get("slug", ""))}</code> · {e(mp4.name)}</div>
    <div class="tags">{tags}</div>
    <details><summary>入库文案 / 场景</summary><p class="copy">{copy}</p><ol class="scenes">{scenes}</ol></details>
    <div class="verdict"><label><input type="radio" name="v-{e(p.name)}" value="通过">通过</label>
      <label><input type="radio" name="v-{e(p.name)}" value="打回">打回</label>
      <textarea placeholder="备注（可空）"></textarea></div>
  </div>
</article>'''


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print(__doc__)
        return 1
    name, keys = args[0], args[1:]
    projs = sorted({d for d in PROJECTS.iterdir() if d.is_dir() and any(d.name.startswith(k) for k in keys)
                    and (d / "composition/props.json").exists()}, key=lambda d: d.name)
    cards = "\n".join(c for c in (card(p) for p in projs) if c)
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"{name}.html"
    out.write_text(f'''<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>合并审片 · {e(name)}</title><style>
:root{{--bg:#f4f2ee;--card:#fff;--ink:#1d1d1f;--mute:#777;--acc:#c3202f}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151515;--card:#222;--ink:#eee;--mute:#999}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,PingFang SC,sans-serif}}
header{{position:sticky;top:0;z-index:2;background:var(--bg);padding:14px 20px;border-bottom:1px solid #8883;display:flex;gap:16px;align-items:center;flex-wrap:wrap}}
header h1{{font-size:18px;margin:0}} header .stat{{color:var(--mute)}} header button{{padding:8px 14px;border-radius:8px;border:0;background:var(--acc);color:#fff;font-weight:700;cursor:pointer}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;padding:18px 20px}}
.ep{{background:var(--card);border-radius:14px;overflow:hidden;box-shadow:0 2px 10px #0001;display:flex;flex-direction:column}}
.ep video{{width:100%;aspect-ratio:9/16;background:#000;display:block}}
.info{{padding:10px 12px;display:flex;flex-direction:column;gap:6px}} .top{{display:flex;justify-content:space-between;gap:8px}}
.dur,.meta{{color:var(--mute);font-size:12px}} code{{font-size:11px}}
.tag{{display:inline-block;font-size:11px;padding:1px 6px;border-radius:6px;background:#8882;margin:0 3px 3px 0}} .tag.hot{{background:var(--acc);color:#fff}}
details{{font-size:13px}} .copy{{margin:6px 0}} .scenes{{padding-left:18px;margin:4px 0}} .scenes button{{font-size:11px;border:0;border-radius:4px;padding:0 5px;cursor:pointer}}
.verdict{{display:flex;flex-wrap:wrap;gap:8px;align-items:center}} .verdict textarea{{width:100%;min-height:34px;border-radius:6px;border:1px solid #8885;background:transparent;color:inherit}}
.ep.pass{{outline:3px solid #2e9d5b}} .ep.fail{{outline:3px solid #d33}}
</style></head><body>
<header><h1>合并审片 · {e(name)}（{len(projs)} 条）</h1><span class="stat" id="stat"></span>
<button id="allpass">全部标通过</button><button id="copy">复制审核结论</button></header>
<main>{cards}</main>
<script>
const KEY="batch-review-{e(name)}";let st={{}};try{{st=JSON.parse(localStorage.getItem(KEY)||"{{}}")}}catch(_){{}}
const save=()=>{{try{{localStorage.setItem(KEY,JSON.stringify(st))}}catch(_){{}};paint()}};
function paint(){{let p=0,f=0;document.querySelectorAll(".ep").forEach(el=>{{const s=st[el.dataset.id]||{{}};el.classList.toggle("pass",s.v==="通过");el.classList.toggle("fail",s.v==="打回");
  el.querySelectorAll("input").forEach(i=>i.checked=i.value===s.v);const ta=el.querySelector("textarea");if(document.activeElement!==ta)ta.value=s.n||"";if(s.v==="通过")p++;if(s.v==="打回")f++;}});
  document.getElementById("stat").textContent=`通过 ${{p}} · 打回 ${{f}} · 未审 ${{document.querySelectorAll(".ep").length-p-f}}`}}
document.querySelectorAll(".ep").forEach(el=>{{const id=el.dataset.id;st[id]=st[id]||{{}};
  el.querySelectorAll("input").forEach(i=>i.onchange=()=>{{st[id].v=i.value;save()}});
  el.querySelector("textarea").oninput=ev=>{{st[id].n=ev.target.value;save()}};
  const v=el.querySelector("video");el.querySelectorAll(".scenes button").forEach(b=>b.onclick=()=>{{v.currentTime=+b.dataset.t;v.play()}});
  v.onplay=()=>document.querySelectorAll("video").forEach(o=>{{if(o!==v)o.pause()}});}});
document.getElementById("allpass").onclick=()=>{{document.querySelectorAll(".ep").forEach(el=>{{if(!st[el.dataset.id].v)st[el.dataset.id].v="通过"}});save()}};
document.getElementById("copy").onclick=()=>{{const lines=[...document.querySelectorAll(".ep")].map(el=>{{const s=st[el.dataset.id]||{{}};return `${{el.dataset.id}}\\t${{s.v||"未审"}}${{s.n?"\\t"+s.n:""}}`}});
  navigator.clipboard.writeText(`合并审片 {e(name)}\\n`+lines.join("\\n")).then(()=>alert("已复制"))}};
paint();
</script></body></html>''', encoding="utf-8")
    print(out, len(projs), "条")
    if "--open" in sys.argv:
        subprocess.run(["open", "-a", "Google Chrome", str(out)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
