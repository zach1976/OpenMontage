#!/usr/bin/env python3
"""扫描 projects/ 生成一张总览列表页 review_index.html —— 每条片子审到哪一步，一眼看完。

状态分两层：

  **磁盘推出来的**（自动，不可改）：渲了几版、当前版本片长/大小、成本、
  是否已登记到 videopublisher、流水线走到哪个 stage。

  **人工判定的**（在页面上点，存本页 localStorage）：待审 / 通过 / 打回。
  各项目的 review.html 有自己的勾选清单，但 file:// 下不同目录的存储不互通，
  所以那份细清单读不到——本页只管"这条片子我审完了没、结论是什么"。

用法：
    python3 scripts/build_review_index.py
    python3 scripts/build_review_index.py --open
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"

STAGES = ["research", "proposal", "script", "scene_plan", "assets", "edit", "compose", "publish"]


def load(path: Path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def probe_duration(path: Path) -> float | None:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=20,
        )
        return round(float(out.stdout.strip()), 1)
    except Exception:
        return None


def thumbs(proj: Path, latest: Path | None) -> tuple[str | None, str | None]:
    """返回 (竖屏封面, 16:9 裁切) 两张缩略图的相对路径。

    **一律从最新成片的第 0 帧抽**。早先会优先用 renders/*cover*.jpg，
    但那是很久以前导出的静态封面文件，封面改版之后它不会跟着变 ——
    总览页于是长期显示上一版设计，而磁盘上的片子早就换了。
    第 0 帧就是平台拿去当封面的那一帧，也只有它不会漂。

    16:9 那张按封面规矩裁（y 656–1264），让人在总览页就能看出横屏版位下还剩什么。
    """
    if latest is None:
        return None, None
    cache = proj / "artifacts"
    cache.mkdir(parents=True, exist_ok=True)
    portrait = cache / "_idx_portrait.jpg"
    land = cache / "_idx_16x9.jpg"
    mt = latest.stat().st_mtime
    for out, vf in ((portrait, "select=eq(n\\,0),scale=420:-1"),
                    (land, "select=eq(n\\,0),crop=iw:min(ih\\,iw*9/16):0:(ih-min(ih\\,iw*9/16))/2,scale=420:-1")):
        if out.exists() and out.stat().st_mtime >= mt:
            continue          # 每张各自判新旧，不然改了一张另一张会留着旧的
        try:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(latest),
                            "-vf", vf, "-frames:v", "1", str(out)], check=True, timeout=60)
        except Exception:
            pass
    rel = lambda f: f"projects/{proj.name}/artifacts/{f.name}" if f.exists() else None
    return rel(portrait), rel(land)


def scan(proj: Path) -> dict | None:
    marker = load(proj / "project.json")
    if marker is None:
        return None  # 不是一个 OpenMontage 项目工作区

    renders = sorted((proj / "renders").glob("*.mp4"),
                     key=lambda p: p.stat().st_mtime, reverse=True)
    latest = renders[0] if renders else None

    report = load(proj / "artifacts" / "render_report.json") or {}
    publog = load(proj / "artifacts" / "publish_log.json") or {}

    # 流水线走到哪：按 manifest 顺序找最后一个 completed 的 stage
    done = []
    for st in STAGES:
        ck = load(proj / f"checkpoint_{st}.json")
        if ck and ck.get("status") == "completed":
            done.append(st)

    pub = None
    for e in (publog.get("entries") or []):
        pub = dict(platform=e.get("platform"), status=e.get("status"),
                   video_id=e.get("video_id"), url=e.get("url"))
        break

    meta = report.get("metadata") or {}
    cost = meta.get("total_cost_usd")
    t_portrait, t_land = thumbs(proj, latest)

    return {
        "id": proj.name,
        "title": marker.get("title", proj.name),
        "pipeline": marker.get("pipeline_type", ""),
        "versions": len(renders),
        "latest": f"renders/{latest.name}" if latest else None,
        "latest_name": latest.stem if latest else None,
        "duration": probe_duration(latest) if latest else None,
        "size_mb": round(latest.stat().st_size / 1e6, 1) if latest else None,
        "mtime": datetime.fromtimestamp(latest.stat().st_mtime).strftime("%m-%d %H:%M") if latest else "",
        "mtime_raw": latest.stat().st_mtime if latest else 0,
        "cost": cost,
        "warnings": len(report.get("warnings") or []),
        "stages_done": done,
        "publish": pub,
        "review_page": "review.html" if (proj / "review.html").exists() else None,
        "thumb": t_portrait,
        "thumb16": t_land,
    }


def build(rows: list[dict]) -> str:
    e = lambda s: html.escape(str(s if s is not None else ""))
    j = lambda o: json.dumps(o, ensure_ascii=False)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>审片总览 · OpenMontage</title>
<style>
  :root {{
    --ground:#0B1526; --panel:#13233D; --panel-2:#1A2E4D; --line:#24395C;
    --ink:#EDE5D4; --ink-soft:#93A3BC; --ink-dim:#61738F;
    --gold:#C9A24B; --gold-lift:#E5CFA0;
    --ok:#5FB683; --warn:#D9A85B; --bad:#D9755B; --pend:#6E7F9A;
  }}
  * {{ box-sizing:border-box; }}
  html,body {{ margin:0; padding:0; }}
  body {{
    background:var(--ground); color:var(--ink);
    font-family:"Noto Sans SC","PingFang SC",system-ui,sans-serif;
    font-size:15px; line-height:1.6; -webkit-font-smoothing:antialiased;
  }}
  .num {{ font-variant-numeric:tabular-nums; }}

  /* 全站限宽。早先没限宽，宽屏下一行拉到两千多像素：标题在最左、审核按钮甩到最右，
     看完标题得把眼睛横扫过去才够得着按钮。限宽 + 操作紧跟标题才是人的读法。 */
  .page {{ max-width:1000px; margin:0 auto; padding:0 24px; }}

  header {{ border-bottom:1px solid var(--line); }}
  header .page {{ padding-top:26px; padding-bottom:18px; display:flex; align-items:baseline; gap:16px; flex-wrap:wrap; }}
  .eyebrow {{ font-size:11px; letter-spacing:.2em; text-transform:uppercase; color:var(--gold); font-weight:700; }}
  h1 {{ font-size:22px; margin:0; font-weight:700; }}
  .hdr-meta {{ margin-left:auto; color:var(--ink-dim); font-size:13px; }}

  .tally {{ border-bottom:1px solid var(--line); }}
  .tally .page {{ display:flex; gap:26px; padding-top:15px; padding-bottom:15px; flex-wrap:wrap; }}
  .tally div {{ display:flex; align-items:baseline; gap:7px; }}
  .tally b {{ font-size:24px; line-height:1; }}
  .tally span {{ font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--ink-dim); }}

  .wrap {{ padding-top:22px; padding-bottom:84px; }}
  .card {{
    display:grid; grid-template-columns:296px 1fr; gap:24px;
    background:var(--panel); border:1px solid var(--line); border-radius:12px;
    padding:16px; margin-bottom:14px; align-items:start;
  }}
  @media (max-width:760px) {{ .card {{ grid-template-columns:1fr; }} }}

  /* 预览：竖屏封面 + 16:9 裁切并排。横屏那张是审「封面是否两屏通吃」用的 */
  .thumbs {{ display:flex; gap:8px; align-items:flex-start; }}
  .thumb {{ position:relative; border:1px solid var(--line); border-radius:8px; overflow:hidden;
            background:#000; flex:none; display:block; }}
  .thumb img {{ display:block; }}
  .thumb.p img {{ width:132px; height:235px; object-fit:cover; }}
  .thumb.l img {{ width:148px; height:83px; object-fit:cover; }}
  /* 说明放图外面。压在图上时：贴底挡匾、贴顶挡标题 —— 挡的都是要审的东西 */
  .shot {{ display:flex; flex-direction:column; gap:5px; flex:none; }}
  .shot .cap {{ color:var(--ink-dim); font-size:10.5px; letter-spacing:.1em; text-align:center; }}
  .thumb.miss {{ width:132px; height:235px; display:flex; align-items:center;
                 justify-content:center; color:var(--ink-dim); font-size:11px; }}
  a.thumb:hover {{ border-color:var(--gold); }}
  a.thumb:focus-visible {{ outline:2px solid var(--gold-lift); outline-offset:2px; }}
  .card.done {{ border-color:rgba(95,182,131,.5); }}
  .card.rejected {{ border-color:rgba(217,117,91,.55); }}

  .t {{ font-size:17px; font-weight:600; margin-bottom:5px; line-height:1.35; }}
  .sub {{ color:var(--ink-dim); font-size:12.5px; display:flex; gap:14px; flex-wrap:wrap; }}
  .sub b {{ color:var(--ink-soft); font-weight:500; }}

  .pills {{ display:flex; gap:6px; flex-wrap:wrap; margin-top:9px; }}
  .pill {{ font-size:11.5px; padding:3px 10px; border-radius:999px; border:1px solid var(--line); color:var(--ink-soft); }}
  .pill.ok {{ color:var(--ok); border-color:rgba(95,182,131,.45); }}
  .pill.warn {{ color:var(--warn); border-color:rgba(217,168,91,.45); }}
  .pill.free {{ color:var(--ok); border-color:rgba(95,182,131,.45); }}
  .pill.cost {{ color:var(--gold); border-color:rgba(201,162,75,.45); }}

  /* 操作跟标题同一列、紧挨着，不再是甩到行尾的第三栏 */
  .acts {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-top:13px; }}
  .states {{ display:flex; gap:0; border:1px solid var(--line); border-radius:8px; overflow:hidden; }}
  .states button {{
    appearance:none; border:0; cursor:pointer; font:inherit; font-size:12.5px;
    background:transparent; color:var(--ink-dim); padding:7px 15px;
  }}
  .states button + button {{ border-left:1px solid var(--line); }}
  .states button:focus-visible {{ outline:2px solid var(--gold-lift); outline-offset:-2px; }}
  .states button[aria-pressed="true"][data-s="pending"] {{ background:var(--pend); color:#0B1526; font-weight:600; }}
  .states button[aria-pressed="true"][data-s="passed"]  {{ background:var(--ok);   color:#0B1526; font-weight:600; }}
  .states button[aria-pressed="true"][data-s="rejected"]{{ background:var(--bad);  color:#0B1526; font-weight:600; }}

  a.open {{
    font-size:13px; color:var(--gold-lift); text-decoration:none;
    border:1px solid var(--line); border-radius:8px; padding:7px 14px; white-space:nowrap;
  }}
  a.open:hover {{ border-color:var(--gold); }}
  a.open:focus-visible {{ outline:2px solid var(--gold-lift); outline-offset:2px; }}
  a.open.dim {{ color:var(--ink-dim); pointer-events:none; opacity:.5; }}

  .note {{ margin-top:11px; }}
  .note input {{
    width:100%; background:var(--panel-2); color:var(--ink);
    border:1px solid var(--line); border-radius:7px; padding:7px 11px; font:inherit; font-size:13px;
  }}
  .note input:focus {{ outline:none; border-color:var(--gold); }}

  .bar {{
    position:fixed; left:0; right:0; bottom:0; background:color-mix(in srgb,var(--ground) 94%,transparent);
    backdrop-filter:blur(12px); border-top:1px solid var(--line); padding:0;
  }}
  .btn {{
    appearance:none; cursor:pointer; font:inherit; font-size:14px; padding:9px 18px;
    border-radius:8px; border:1px solid var(--line); background:var(--panel); color:var(--ink);
  }}
  .btn.primary {{ background:var(--gold); color:#16223A; border-color:var(--gold); font-weight:600; }}
  .btn:focus-visible {{ outline:2px solid var(--gold-lift); outline-offset:2px; }}
  .bar .page {{ display:flex; gap:10px; align-items:center; padding-top:12px; padding-bottom:12px; }}
  .st {{ margin-left:auto; color:var(--ink-dim); font-size:13px; }}
  @media (prefers-reduced-motion: reduce) {{ * {{ transition:none !important; }} }}
</style>
</head>
<body>

<header>
  <div class="page">
    <div>
      <div class="eyebrow">审片总览</div>
      <h1>OpenMontage · 所有片子</h1>
    </div>
    <div class="hdr-meta">生成于 {e(generated)} · 磁盘状态自动读取，审核结论存本机浏览器</div>
  </div>
</header>

<div class="tally"><div class="page">
  <div><b id="tTotal">0</b><span>条片子</span></div>
  <div><b id="tPending" style="color:var(--pend)">0</b><span>待审</span></div>
  <div><b id="tPassed" style="color:var(--ok)">0</b><span>通过</span></div>
  <div><b id="tRejected" style="color:var(--bad)">0</b><span>打回</span></div>
  <div><b id="tPub" style="color:var(--gold)">0</b><span>已登记发布</span></div>
</div></div>

<div class="wrap page" id="list"></div>

<div class="bar"><div class="page">
  <button class="btn primary" id="copyBtn">复制审核结论</button>
  <button class="btn" id="resetBtn">全部重置为待审</button>
  <span class="st" id="status"></span>
</div></div>

<script>
(function () {{
  "use strict";
  var ROWS = {j(rows)};
  var KEY = "openmontage:review-index";

  var state = {{}};
  try {{ state = JSON.parse(localStorage.getItem(KEY) || "{{}}"); }} catch (e) {{}}
  function persist() {{ try {{ localStorage.setItem(KEY, JSON.stringify(state)); }} catch (e) {{}} }}
  function get(id) {{ return state[id] || {{ s: "pending", note: "" }}; }}

  var STATES = [["pending","待审"],["passed","通过"],["rejected","打回"]];
  var list = document.getElementById("list");

  function el(t, c, x) {{ var n = document.createElement(t); if (c) n.className = c; if (x != null) n.textContent = x; return n; }}

  ROWS.forEach(function (r) {{
    var card = el("div", "card");

    var thumbs = el("div", "thumbs");
    // 缩略图本身可点 —— 点击目标比一个小链接大得多，看到问题顺手就点进去了
    function shot(src, cls, cap, alt) {{
      var wrap = el("div", "shot");
      var box;
      if (r.review_page) {{
        box = document.createElement("a");
        box.href = "projects/" + r.id + "/" + r.review_page;
        box.setAttribute("aria-label", alt);
      }} else {{ box = document.createElement("div"); }}
      box.className = "thumb " + cls;
      var im = document.createElement("img"); im.src = src; im.alt = alt; im.loading = "lazy";
      box.appendChild(im);
      wrap.appendChild(box); wrap.appendChild(el("div", "cap", cap));
      return wrap;
    }}
    if (r.thumb) thumbs.appendChild(shot(r.thumb, "p", "9:16", r.title + " 竖屏封面"));
    else thumbs.appendChild(el("div", "thumb miss", "无预览"));
    if (r.thumb16) thumbs.appendChild(shot(r.thumb16, "l", "16:9 裁切", r.title + " 横屏裁切"));

    var left = el("div");
    left.appendChild(el("div", "t", r.title));

    var sub = el("div", "sub");
    function bit(label, val) {{
      if (val === null || val === undefined || val === "") return;
      var d = el("div");
      d.innerHTML = label + " <b>" + val + "</b>";
      sub.appendChild(d);
    }}
    bit("ID", r.id);
    bit("版本", r.versions);
    if (r.duration) bit("当前", r.duration + "s");
    if (r.size_mb) bit("", r.size_mb + "MB");
    if (r.mtime) bit("更新", r.mtime);
    left.appendChild(sub);

    var pills = el("div", "pills");
    function pill(text, cls) {{ pills.appendChild(el("span", "pill " + (cls || ""), text)); }}
    if (!r.versions) pill("还没渲染", "warn");
    // 只有明确记了 0 才敢说零成本；没记录就是"不知道"，不能替它宣称
    if (r.cost === 0) pill("零成本", "free");
    else if (typeof r.cost === "number") pill("$" + r.cost, "cost");
    else if (r.versions) pill("成本未记录");
    if (r.publish) {{
      var lab = {{published:"已发布", pending_review:"已登记", exported:"已导出",
                  draft:"草稿", failed:"发布失败"}}[r.publish.status] || r.publish.status;
      pill(lab + " · " + r.publish.platform + (r.publish.video_id ? " #" + r.publish.video_id : ""),
           r.publish.status === "failed" ? "warn" : "ok");
    }} else if (r.versions) {{
      pill("未发布");
    }}
    if (r.warnings) pill(r.warnings + " 条已知问题", "warn");
    if (r.stages_done && r.stages_done.length) pill("流水线 " + r.stages_done.length + "/8");
    left.appendChild(pills);

    var acts = el("div", "acts");
    var states = el("div", "states");
    STATES.forEach(function (pair) {{
      var b = document.createElement("button");
      b.type = "button"; b.dataset.s = pair[0]; b.textContent = pair[1];
      b.addEventListener("click", function () {{
        var s = get(r.id); s.s = pair[0]; state[r.id] = s; persist(); paint(); tally(); flash("已标记：" + pair[1]);
      }});
      states.appendChild(b);
    }});
    acts.appendChild(states);

    var a = document.createElement("a");
    a.className = "open" + (r.review_page ? "" : " dim");
    a.textContent = r.review_page ? "打开审片页 →" : "无审片页";
    if (r.review_page) a.href = "projects/" + r.id + "/" + r.review_page;
    acts.appendChild(a);
    left.appendChild(acts);

    var note = el("div", "note");
    var inp = document.createElement("input");
    inp.type = "text"; inp.placeholder = "审核备注（存本机）";
    inp.value = get(r.id).note;
    inp.setAttribute("aria-label", r.title + " 审核备注");
    inp.addEventListener("input", function () {{
      var s = get(r.id); s.note = inp.value; state[r.id] = s; persist(); flash("已存");
    }});
    note.appendChild(inp);
    left.appendChild(note);

    card.appendChild(thumbs); card.appendChild(left);
    list.appendChild(card);

    card._paint = function () {{
      var s = get(r.id).s;
      Array.prototype.forEach.call(states.children, function (b) {{
        b.setAttribute("aria-pressed", String(b.dataset.s === s));
      }});
      card.classList.toggle("done", s === "passed");
      card.classList.toggle("rejected", s === "rejected");
    }};
  }});

  function paint() {{ Array.prototype.forEach.call(list.children, function (c) {{ c._paint(); }}); }}
  function tally() {{
    var n = {{ pending: 0, passed: 0, rejected: 0 }}, pub = 0;
    ROWS.forEach(function (r) {{ n[get(r.id).s]++; if (r.publish) pub++; }});
    document.getElementById("tTotal").textContent = ROWS.length;
    document.getElementById("tPending").textContent = n.pending;
    document.getElementById("tPassed").textContent = n.passed;
    document.getElementById("tRejected").textContent = n.rejected;
    document.getElementById("tPub").textContent = pub;
  }}

  var statusEl = document.getElementById("status"), timer = null;
  function flash(m) {{
    statusEl.textContent = m;
    if (timer) clearTimeout(timer);
    timer = setTimeout(function () {{ statusEl.textContent = ""; }}, 1800);
  }}

  document.getElementById("copyBtn").addEventListener("click", function () {{
    var lines = ["审核结论（" + new Date().toLocaleString("zh-CN") + "）"];
    var LABEL = {{ pending: "待审", passed: "通过", rejected: "打回" }};
    ROWS.forEach(function (r) {{
      var s = get(r.id);
      lines.push("- [" + LABEL[s.s] + "] " + r.title + (s.note ? " —— " + s.note : ""));
    }});
    var text = lines.join("\\n");
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(text).then(
        function () {{ flash("已复制，贴回对话"); }},
        function () {{ flash("复制失败，手动选中复制"); }});
    }} else {{ flash("此浏览器不支持自动复制"); }}
  }});

  document.getElementById("resetBtn").addEventListener("click", function () {{
    ROWS.forEach(function (r) {{ state[r.id] = {{ s: "pending", note: get(r.id).note }}; }});
    persist(); paint(); tally(); flash("全部重置为待审");
  }});

  paint(); tally();
}})();
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    if not PROJECTS.is_dir():
        print("没有 projects/ 目录", file=sys.stderr)
        return 1

    rows = [r for r in (scan(p) for p in sorted(PROJECTS.iterdir()) if p.is_dir()) if r]
    rows.sort(key=lambda r: r["mtime_raw"], reverse=True)   # 最近动过的排前面

    out = REPO / "review_index.html"
    out.write_text(build(rows), encoding="utf-8")
    print(f"{out}  ·  {len(rows)} 个项目")
    for r in rows:
        pub = f"已登记#{r['publish']['video_id']}" if r["publish"] else "未发布"
        print(f"  {r['id']:34} {r['versions']:>2} 版  {str(r['duration'] or '—'):>6}s  {pub}")
    if args.open:
        subprocess.run(["open", str(out)], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
