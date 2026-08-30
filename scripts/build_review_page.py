#!/usr/bin/env python3
"""从项目工作区生成一张本地审片页 projects/<project_id>/review.html。

页面本身不含任何硬编码内容——时间轴、旁白、配图署名、决策、校验结论全部读自
artifacts/ 与 composition/props.json。改完一版重跑一次即可，不用手改 HTML。

用法：
    python3 scripts/build_review_page.py <project_id>
    python3 scripts/build_review_page.py thai-1000-nickname-01 --open
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"


def load(path: Path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def probe(path: Path) -> dict:
    """拿视频的时长/分辨率/大小。ffprobe 不在就退回文件大小。"""
    info = {"size": path.stat().st_size if path.exists() else 0}
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration:stream=width,height", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=20,
        )
        d = json.loads(out.stdout)
        info["duration"] = float(d["format"]["duration"])
        for s in d.get("streams", []):
            if s.get("width"):
                info["w"], info["h"] = s["width"], s["height"]
                break
    except Exception:
        pass
    return info


def collect_versions(proj: Path) -> list[dict]:
    """renders/ 下所有 mp4，按修改时间倒序——最新的默认选中。"""
    mp4s = sorted((proj / "renders").glob("*.mp4"),
                  key=lambda p: p.stat().st_mtime, reverse=True)
    if not mp4s:
        return []

    # 按钮标签：把所有文件名的公共前缀剥掉，只留区分版本的那一小段。
    # （光切最后一个下划线会把 nickname_ep01 显示成 "ep01"，看着像期号不像版本。）
    stems = [p.stem for p in mp4s]
    prefix = ""
    if len(stems) > 1:
        for i, ch in enumerate(stems[0]):
            if all(len(s) > i and s[i] == ch for s in stems):
                prefix += ch
            else:
                break
    out = []
    for mp4 in mp4s:
        info = probe(mp4)
        label = mp4.stem[len(prefix):].lstrip("_-") or "初版"
        out.append({
            "file": f"renders/{mp4.name}",
            "name": mp4.stem,
            "label": label,
            "duration": info.get("duration"),
            "size_mb": round(info["size"] / 1e6, 1) if info.get("size") else None,
            "res": f"{info['w']}x{info['h']}" if info.get("w") else None,
            "mtime": mp4.stat().st_mtime,
        })
    return out


def collect_scenes(props: dict | None, script: dict | None) -> list[dict]:
    """时间轴 = 可点击跳转的场景条。旁白正文从 script.json 里按 section id 对上。"""
    if not props:
        return []
    narration = {}
    for sec in (script or {}).get("sections", []):
        narration[sec["id"]] = sec.get("text", "")

    scenes = []
    hook = props.get("hook")
    if hook:
        # 片头这一屏历经三种结构：四行递进 lines[] → 标题卡 line1/line2 →
        # 封面即第一帧（字段搬进 hook.cover）。三种都要认，否则时间轴第一条会是空的。
        cov = hook.get("cover") or {}
        src = cov or hook
        parts = [src.get("line1"), src.get("bigNum", "") + src.get("bigTail", ""),
                 src.get("line2"), (src.get("hook", "") + src.get("hookAccent", ""))]
        if not any(parts) and isinstance(hook.get("lines"), list):
            parts = [l.get("text") for l in hook["lines"] if isinstance(l, dict)]
        scenes.append({
            "id": "s00_hook",
            "label": "封面 · 第一帧" if cov else "片头",
            "thai": src.get("thaiRow", ""),
            "start": hook["start"], "end": round(hook["start"] + hook["dur"], 2),
            "title": " ".join(x for x in parts if x),
            "sub": src.get("badge", ""),
            "text": narration.get("s00_hook", ""),
            "credit": src.get("credit", ""),
        })
    # 各系列的 props 字段名不统一（泰语用 thai，越南语用 viet），按候选键取。
    def pick(d: dict, *keys, default=""):
        for k in keys:
            if d.get(k):
                return d[k]
        return default

    for i, c in enumerate(props.get("cards", []), 1):
        word = pick(c, "thai", "viet", "word", "native")
        roman = pick(c, "roman", "pinyin")
        xie = pick(c, "xie")
        title = " · ".join(x for x in [roman, f"谐音 {xie}" if xie else ""] if x)
        sub = " / ".join(x for x in [c.get("who1"), c.get("who2"), c.get("usage")] if x)
        # 词组优先：这一版的主角是能跟读的词组（chunk），整句只是出处小字。
        # 页面早先拿整句当标题，跟脚本对不上 —— 看着像"另一版片子"。
        chunk, chunk_zh = c.get("chunk"), c.get("chunkZh")
        if chunk:
            label = f"{i:02d} · {c.get('roleNote') or c.get('role') or ''} {chunk_zh or ''}".rstrip()
            sub = " / ".join(x for x in [f"{chunk}　{chunk_zh}" if chunk_zh else chunk,
                                         f"例：{c.get('zh','')}" if c.get("zh") else ""] if x)
        else:
            label = f"{c.get('order', i):02d} · {pick(c, 'zh', default='')}"
        scenes.append({
            "id": c.get("id", f"card{i}"),
            "label": label,
            "thai": word or (chunk or ""),
            "start": c["start"], "end": round(c["start"] + c["dur"], 2),
            "title": title, "sub": sub,
            "text": narration.get(c.get("id", ""), ""),
            "credit": c.get("credit", ""),
        })
    br = props.get("bridge")
    if br:
        scenes.append({
            "id": "s06_bridge", "label": "桥接", "thai": "",
            "start": br["start"], "end": round(br["start"] + br["dur"], 2),
            "title": br.get("line1", ""), "sub": br.get("line2", ""),
            "text": narration.get("s06_bridge", ""), "credit": "",
        })
    rv = props.get("reveal")
    if rv:
        beats = rv.get("beats") or []
        scenes.append({
            "id": "s06_reveal", "label": "收束", "thai": "",
            "start": rv["start"], "end": round(rv["start"] + rv["dur"], 2),
            "title": rv.get("line1", ""),
            "sub": " / ".join(x for x in [str(rv.get("line2", "")).replace("\n", " "),
                                          " · ".join(beats) if beats else ""] if x),
            "text": narration.get("s06_reveal", ""), "credit": "",
        })
    o = props.get("outro")
    if o:
        scenes.append({
            "id": "s07_outro", "label": "片尾", "thai": "",
            "start": o["start"], "end": round(o["start"] + o["dur"], 2),
            "title": o.get("line2", ""), "sub": o.get("cta", ""),
            "text": narration.get("s07_outro", ""), "credit": "",
        })
    return scenes


# 审核清单：前几条来自本产线反复踩过的坑，最后几条是每条片都要过的通用项。
CHECKS = [
    ("frame0", "第一帧可直接当封面", "平台抓第一帧做缩略图——第一帧必须是排好版的成品，不能是动画起始的空屏"),
    ("safe", "文字全在安全区", "顶部导航和底部评论条会盖住画面，字不能压到 y=240–1380 之外"),
    ("thai", "泰文加符完整", "Sarabun 行高不够时，上下加符会被切或压到下一行"),
    ("audio", "每段配音都出声", "分段音频错位时会出现哑段，画面照走但没人声"),
    ("sync", "声画对得上", "旁白讲的词和画面上的卡是同一个"),
    ("follow", "跟读空档够用", "泰语读两遍，中间的空档要能塞下自己跟一遍"),
    ("fact", "配图没有事实错误", "野猪不是家猪，云的倒影不是天空"),
    ("credit", "CC 署名在位", "BY / BY-SA 的图必须署名，公有领域也标一下"),
    ("icon", "片尾 app icon 出现", "观众照着图标去应用商店找"),
    ("nocomment", "没有提评论区", "硬要求"),
]


def build_html(ctx: dict) -> str:
    e = lambda s: html.escape(str(s if s is not None else ""))
    j = lambda o: json.dumps(o, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>审片 · {e(ctx['title'])}</title>
<style>
  /* 审片间：深底是为了让画面自己说话，不跟界面抢眼。单一深色主题是刻意的。 */
  :root {{
    --ground:   #0B1526;
    --panel:    #13233D;
    --panel-2:  #1A2E4D;
    --line:     #24395C;
    --ink:      #EDE5D4;
    --ink-soft: #93A3BC;
    --ink-dim:  #61738F;
    --gold:     #C9A24B;
    --gold-lift:#E5CFA0;
    --ok:       #5FB683;
    --bad:      #D9755B;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    background: var(--ground); color: var(--ink);
    font-family: "Noto Sans SC", "PingFang SC", system-ui, sans-serif;
    font-size: 15px; line-height: 1.6; -webkit-font-smoothing: antialiased;
  }}
  .thai {{ font-family: "Sarabun", "Noto Sans Thai", system-ui, sans-serif; }}
  .num  {{ font-variant-numeric: tabular-nums; }}

  header {{
    padding: 22px 28px 18px; border-bottom: 1px solid var(--line);
    display: flex; align-items: baseline; gap: 18px; flex-wrap: wrap;
  }}
  h1 {{ font-size: 21px; margin: 0; font-weight: 700; letter-spacing: .02em; }}
  .eyebrow {{
    font-size: 11px; letter-spacing: .2em; text-transform: uppercase;
    color: var(--gold); font-weight: 700;
  }}
  .hdr-meta {{ margin-left: auto; color: var(--ink-dim); font-size: 13px; }}

  .cols {{ display: grid; grid-template-columns: minmax(320px, 460px) 1fr; gap: 28px; padding: 24px 28px 60px; align-items: start; }}
  @media (max-width: 900px) {{ .cols {{ grid-template-columns: 1fr; }} }}

  .stage {{ position: sticky; top: 18px; }}
  video {{
    width: 100%; display: block; border-radius: 10px; background: #000;
    box-shadow: 0 18px 50px rgba(0,0,0,.55); border: 1px solid var(--line);
  }}

  .vers {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }}
  .vers button {{
    appearance: none; cursor: pointer; font: inherit; font-size: 13px;
    background: var(--panel); color: var(--ink-soft); border: 1px solid var(--line);
    border-radius: 7px; padding: 7px 13px;
  }}
  .vers button[aria-pressed="true"] {{ background: var(--gold); color: #16223A; border-color: var(--gold); font-weight: 600; }}
  .vers button:focus-visible {{ outline: 2px solid var(--gold-lift); outline-offset: 2px; }}
  .vers .vmeta {{ display: block; font-size: 11px; opacity: .75; margin-top: 1px; }}

  .now {{
    margin-top: 10px; padding: 10px 13px; background: var(--panel);
    border: 1px solid var(--line); border-radius: 8px; font-size: 13px;
    display: flex; gap: 12px; align-items: baseline;
  }}
  .now b {{ color: var(--gold-lift); font-weight: 600; }}
  .now .t {{ margin-left: auto; color: var(--ink-dim); }}

  section.block {{ margin-bottom: 30px; }}
  h2 {{
    font-size: 12px; letter-spacing: .18em; text-transform: uppercase;
    color: var(--ink-dim); margin: 0 0 12px; font-weight: 700;
    padding-bottom: 8px; border-bottom: 1px solid var(--line);
  }}

  /* 场景条 */
  .scene {{
    display: grid; grid-template-columns: 62px 1fr; gap: 14px;
    width: 100%; text-align: left; cursor: pointer;
    background: transparent; border: 0; border-bottom: 1px solid var(--line);
    padding: 13px 10px; color: inherit; font: inherit;
    border-radius: 6px;
  }}
  .scene:hover {{ background: var(--panel); }}
  .scene:focus-visible {{ outline: 2px solid var(--gold-lift); outline-offset: -2px; }}
  .scene.active {{ background: var(--panel-2); }}
  .scene .at {{ color: var(--gold); font-size: 12.5px; font-weight: 700; }}
  .scene .dur {{ color: var(--ink-dim); font-size: 11.5px; }}
  .scene .lab {{ font-weight: 600; font-size: 15px; }}
  .scene .th {{ font-size: 20px; color: var(--gold-lift); margin-left: 8px; }}
  .scene .sub {{ color: var(--ink-soft); font-size: 12.5px; }}
  .scene .nar {{ color: var(--ink-dim); font-size: 12.5px; margin-top: 4px; }}
  .scene .cr {{ color: var(--ink-dim); font-size: 11px; margin-top: 3px; opacity: .8; }}

  /* 清单 */
  .check {{ display: flex; gap: 11px; padding: 10px 8px; border-bottom: 1px solid var(--line); align-items: flex-start; }}
  .check input {{ margin-top: 4px; width: 17px; height: 17px; accent-color: var(--ok); flex: none; }}
  .check label {{ cursor: pointer; }}
  .check .t {{ font-weight: 500; }}
  .check .d {{ color: var(--ink-dim); font-size: 12.5px; }}
  .check.done .t {{ color: var(--ok); }}

  textarea {{
    width: 100%; min-height: 110px; resize: vertical;
    background: var(--panel); color: var(--ink); border: 1px solid var(--line);
    border-radius: 8px; padding: 11px 13px; font: inherit; line-height: 1.65;
  }}
  textarea:focus {{ outline: none; border-color: var(--gold); }}

  .btn {{
    appearance: none; cursor: pointer; font: inherit; font-size: 14px;
    padding: 9px 18px; border-radius: 8px; border: 1px solid var(--line);
    background: var(--panel); color: var(--ink);
  }}
  .cf {{ display:grid; grid-template-columns:96px 1fr 64px; gap:10px; align-items:center;
         margin-bottom:9px; }}
  .cf label {{ font-size:13px; color:var(--ink-dim); text-align:right; }}
  .cf input {{ width:100%; background:var(--panel-2); color:var(--ink); font:inherit; font-size:14px;
               border:1px solid var(--line); border-radius:7px; padding:7px 11px; }}
  .cf input:focus {{ outline:none; border-color:var(--gold); }}
  .cf .cnt {{ font-size:12px; color:var(--ink-dim); text-align:right; font-variant-numeric:tabular-nums; }}
  .cf.over input {{ border-color:var(--bad); }}
  .cf.over .cnt {{ color:var(--bad); font-weight:600; }}
  .alts {{ margin:12px 0 4px; }}
  .alts .lb {{ font-size:12px; letter-spacing:.12em; color:var(--ink-dim); margin-bottom:8px; }}
  .alts .chips {{ display:flex; flex-wrap:wrap; gap:8px; }}
  .chip {{ appearance:none; cursor:pointer; font:inherit; font-size:13px; text-align:left;
           background:var(--panel-2); color:var(--ink); border:1px solid var(--line);
           border-radius:9px; padding:8px 12px; line-height:1.45; }}
  .chip:hover {{ border-color:var(--gold); }}
  .chip:focus-visible {{ outline:2px solid var(--gold-lift); outline-offset:2px; }}
  .chip b {{ display:block; color:var(--gold-lift); font-weight:600; font-size:15px; }}
  .chip span {{ color:var(--ink-dim); }}
  .chip.on {{ border-color:var(--gold); background:rgba(201,162,75,.12); }}
  .hint {{ font-size:13px; color:var(--ink-dim); margin:0 0 12px; line-height:1.6; }}
  .hint code {{ color:var(--gold-lift); }}
  .btn.primary {{ background: var(--gold); color: #16223A; border-color: var(--gold); font-weight: 600; }}
  .btn:focus-visible {{ outline: 2px solid var(--gold-lift); outline-offset: 2px; }}
  .row {{ display: flex; gap: 10px; align-items: center; margin-top: 12px; flex-wrap: wrap; }}
  .row .st {{ color: var(--ink-dim); font-size: 13px; }}

  .facts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
  .fact {{ background: var(--panel); padding: 12px 14px; }}
  .fact dt {{ font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: var(--ink-dim); }}
  .fact dd {{ margin: 3px 0 0; font-size: 17px; font-weight: 600; }}
  .fact dd.free {{ color: var(--ok); }}

  .stale {{
    margin: 18px 28px 0; padding: 12px 16px; border-radius: 8px;
    background: rgba(217,117,91,.13); border: 1px solid var(--bad); color: var(--ink);
  }}
  .stale b {{ color: var(--bad); }}
  .stale ul {{ margin: 6px 0 0; padding-left: 20px; font-size: 13.5px; color: var(--ink-soft); }}
  ul.notes {{ margin: 0; padding-left: 20px; color: var(--ink-soft); font-size: 13.5px; }}
  ul.notes li {{ margin-bottom: 6px; }}
  ul.notes.warn li::marker {{ color: var(--bad); }}
  .dec {{ display: grid; grid-template-columns: 130px 1fr; gap: 12px; padding: 9px 0; border-bottom: 1px solid var(--line); font-size: 13.5px; }}
  .dec dt {{ color: var(--ink-dim); }}
  .dec dd {{ margin: 0; }}
  .dec dd b {{ color: var(--gold-lift); }}
</style>
</head>
<body>

<header>
  <div>
    <div class="eyebrow">审片台</div>
    <h1>{e(ctx['title'])}</h1>
  </div>
  <div class="hdr-meta">{e(ctx['project_id'])} · 生成于本机 · 数据读自 artifacts/</div>
</header>

{ctx['stale_html']}

<div class="cols">
  <div class="stage">
    <div class="vers" id="vers"></div>
    <video id="v" controls preload="metadata"{ctx['poster_attr']}></video>
    <div class="now">
      <b id="nowLabel">—</b>
      <span id="nowSub" class="sub"></span>
      <span class="t num" id="nowTime">0.0s</span>
    </div>
  </div>

  <div>
    <section class="block">
      <h2>封面文案 · 可直接改</h2>
      <p class="hint">封面只放一句话：第一行 + 第二行**合计不超过 12 字**（全角算 1，半角算 0.5），超了标红。
        改完点「复制封面文案」贴回对话，我用 <code>apply_cover_text.py</code> 写回去重渲。</p>
      <div id="coverFields"></div>
      <div class="cf"><label></label><div id="headTotal" class="cnt"></div><div></div></div>
      <div id="coverAlts"></div>
      <div class="row">
        <button class="btn primary" id="copyCoverBtn">复制封面文案</button>
        <button class="btn" id="resetCoverBtn">还原成当前成片的文案</button>
        <span class="st" id="coverStat"></span>
      </div>
    </section>

    <section class="block">
      <h2>时间轴 · 点击跳转</h2>
      <div id="scenes"></div>
    </section>

    <section class="block">
      <h2>审核清单</h2>
      <div id="checks"></div>
      <div class="row"><span class="st" id="checkStat"></span></div>
    </section>

    <section class="block">
      <h2>问题记录</h2>
      <textarea id="notes" placeholder="哪一秒、什么问题。写完点「复制审核意见」贴回对话。"></textarea>
      <div class="row">
        <button class="btn primary" id="copyBtn">复制审核意见</button>
        <button class="btn" id="clearBtn">清空</button>
        <span class="st" id="status"></span>
      </div>
    </section>

    <section class="block">
      <h2>这一版是什么</h2>
      <dl class="facts">{ctx['facts_html']}</dl>
    </section>

    {ctx['decisions_html']}
    {ctx['verify_html']}
    {ctx['warn_html']}
  </div>
</div>

<script>
(function () {{
  "use strict";
  var VERSIONS = {j(ctx['versions'])};
  var SCENES   = {j(ctx['scenes'])};
  var CHECKS   = {j(ctx['checks'])};
  var KEY      = "review:" + {j(ctx['project_id'])};
  var PROJECT_ID = {j(ctx['project_id'])};
  var COVER_SRC  = {j(ctx['cover_text'])};
  var COVER_ALTS = {j(ctx['cover_alts'])};

  var v = document.getElementById("v");
  var state = {{ version: VERSIONS.length ? VERSIONS[0].file : "", checks: {{}}, notes: "" }};
  try {{
    var s = JSON.parse(localStorage.getItem(KEY) || "null");
    if (s) {{
      // 版本**不从本地恢复**：它以前会把你钉在某一版上 —— 选过第 6 版之后，
      // 我又渲了 7、8、9、10，页面还是给你放第 6 版，看着就像"脚本没改"。
      // 审片默认永远看最新那版；版本按钮留着做同一次会话内的 A/B。
      // （s.version 读进来只为兼容旧存档，不再生效。）
      if (s.checks) state.checks = s.checks;
      if (typeof s.notes === "string") state.notes = s.notes;
    }}
  }} catch (e) {{}}
  function persist() {{ try {{ localStorage.setItem(KEY, JSON.stringify(state)); }} catch (e) {{}} }}

  function fmt(t) {{ return (Math.round(t * 10) / 10).toFixed(1) + "s"; }}

  // ---- 版本切换 ----
  var versBox = document.getElementById("vers");
  VERSIONS.forEach(function (ver) {{
    var b = document.createElement("button");
    b.type = "button";
    b.innerHTML = ver.label +
      '<span class="vmeta num">' + (ver.duration ? fmt(ver.duration) : "?") +
      (ver.size_mb ? " · " + ver.size_mb + "MB" : "") + "</span>";
    b.title = ver.file;
    b.addEventListener("click", function () {{ setVersion(ver.file); }});
    b.dataset.file = ver.file;
    versBox.appendChild(b);
  }});
  function setVersion(file) {{
    state.version = file;
    var t = v.currentTime;
    v.src = file;
    v.addEventListener("loadedmetadata", function once() {{
      v.removeEventListener("loadedmetadata", once);
      if (t && t < v.duration) v.currentTime = t;   // 换版本保持在同一时间点，方便 A/B
    }});
    Array.prototype.forEach.call(versBox.children, function (b) {{
      b.setAttribute("aria-pressed", String(b.dataset.file === file));
    }});
    persist();
  }}

  // ---- 场景条 ----
  var scenesBox = document.getElementById("scenes");
  SCENES.forEach(function (sc) {{
    var b = document.createElement("button");
    b.type = "button"; b.className = "scene"; b.dataset.id = sc.id;
    var left = '<div><div class="at num">' + fmt(sc.start) + '</div>' +
               '<div class="dur num">' + (sc.end - sc.start).toFixed(1) + 's</div></div>';
    var right = '<div><div class="lab">' + sc.label +
                (sc.thai ? '<span class="th thai">' + sc.thai + '</span>' : "") + '</div>' +
                (sc.title ? '<div class="sub">' + sc.title + '</div>' : "") +
                (sc.sub ? '<div class="sub">' + sc.sub + '</div>' : "") +
                (sc.text ? '<div class="nar">' + sc.text + '</div>' : "") +
                (sc.credit ? '<div class="cr">图：' + sc.credit + '</div>' : "") + '</div>';
    b.innerHTML = left + right;
    b.addEventListener("click", function () {{ v.currentTime = sc.start + 0.05; v.play(); }});
    scenesBox.appendChild(b);
  }});

  var nowLabel = document.getElementById("nowLabel");
  var nowSub   = document.getElementById("nowSub");
  var nowTime  = document.getElementById("nowTime");
  v.addEventListener("timeupdate", function () {{
    var t = v.currentTime, cur = null;
    for (var i = 0; i < SCENES.length; i++) if (t >= SCENES[i].start && t < SCENES[i].end) cur = SCENES[i];
    nowTime.textContent = fmt(t);
    nowLabel.textContent = cur ? cur.label : "—";
    nowSub.textContent = cur && cur.thai ? cur.thai : "";
    Array.prototype.forEach.call(scenesBox.children, function (b) {{
      b.classList.toggle("active", !!cur && b.dataset.id === cur.id);
    }});
  }});

  // ---- 清单 ----
  var checksBox = document.getElementById("checks");
  var checkStat = document.getElementById("checkStat");
  CHECKS.forEach(function (c) {{
    var wrap = document.createElement("div");
    wrap.className = "check";
    var box = document.createElement("input");
    box.type = "checkbox"; box.id = "ck-" + c[0];
    box.checked = !!state.checks[c[0]];
    var lab = document.createElement("label");
    lab.htmlFor = box.id;
    lab.innerHTML = '<div class="t">' + c[1] + '</div><div class="d">' + c[2] + '</div>';
    wrap.appendChild(box); wrap.appendChild(lab);
    checksBox.appendChild(wrap);
    function sync() {{ wrap.classList.toggle("done", box.checked); }}
    box.addEventListener("change", function () {{
      state.checks[c[0]] = box.checked; sync(); tally(); persist();
    }});
    sync();
  }});
  function tally() {{
    var n = CHECKS.filter(function (c) {{ return state.checks[c[0]]; }}).length;
    checkStat.textContent = n + " / " + CHECKS.length + (n === CHECKS.length ? " —— 全过了" : " 项已确认");
    checkStat.style.color = n === CHECKS.length ? "var(--ok)" : "";
  }}

  // ---- 记录 ----
  var notes = document.getElementById("notes");
  notes.value = state.notes;
  notes.addEventListener("input", function () {{ state.notes = notes.value; persist(); }});

  var statusEl = document.getElementById("status");
  var timer = null;
  function flash(m) {{
    statusEl.textContent = m;
    if (timer) clearTimeout(timer);
    timer = setTimeout(function () {{ statusEl.textContent = ""; }}, 2200);
  }}

  // ── 封面文案编辑 ───────────────────────────────────────────────────
  // 上限跟 scripts/check_screen_text.py 保持一致：全角算 1，半角算 0.5。
  // 这里当场校验，省得改完渲完才发现超宽。
  var COVER = COVER_SRC;
  // 2026-08-28 起封面只有「期号 + 一句话」：t1/t2 是同一句拆成的上下两行，
  // 两行合计不超过 12 字。匾/词表/脚注不再上封面，字段也就一并撤了。
  var CFIELDS = [["badge", "期号", 16], ["t1", "第一行", 9], ["t2", "第二行", 9]];
  var HEAD_MAX = 12;
  function vlen(t) {{
    var w = 0;
    for (var i = 0; i < t.length; i++) {{
      var c = t.charCodeAt(i);
      w += (c > 0x2e80 || c === 0x00b7) ? 1 : 0.5;
    }}
    return Math.round(w * 10) / 10;
  }}
  var coverState = {{}};
  CFIELDS.forEach(function (f) {{ coverState[f[0]] = COVER[f[0]] != null ? COVER[f[0]] : ""; }});
  try {{
    var cs = JSON.parse(localStorage.getItem(KEY + ":cover") || "null");
    if (cs) CFIELDS.forEach(function (f) {{ if (cs[f[0]] != null) coverState[f[0]] = cs[f[0]]; }});
  }} catch (e) {{}}

  var cfWrap = document.getElementById("coverFields");
  function paintCover() {{
    cfWrap.innerHTML = "";
    CFIELDS.forEach(function (f) {{
      var key = f[0], label = f[1], max = f[2];
      var row = document.createElement("div"); row.className = "cf";
      var lb = document.createElement("label"); lb.textContent = label;
      lb.setAttribute("for", "cf_" + key);
      var inp = document.createElement("input");
      inp.type = "text"; inp.id = "cf_" + key; inp.value = coverState[key];
      var cnt = document.createElement("div"); cnt.className = "cnt";
      function upd() {{
        var w = vlen(inp.value);
        cnt.textContent = w + "/" + max;
        row.classList.toggle("over", w > max);
        var tot = vlen(coverState.t1 || "") + vlen(coverState.t2 || "");
        var te = document.getElementById("headTotal");
        if (te) {{
          te.textContent = "两行合计 " + tot + " / " + HEAD_MAX + " 字";
          te.className = tot > HEAD_MAX ? "cnt over" : "cnt";
        }}
      }}
      inp.addEventListener("input", function () {{
        coverState[key] = inp.value; upd();
        try {{ localStorage.setItem(KEY + ":cover", JSON.stringify(coverState)); }} catch (e) {{}}
        flashCover("已存本机"); paintAlts();
      }});
      upd();
      row.appendChild(lb); row.appendChild(inp); row.appendChild(cnt);
      cfWrap.appendChild(row);
    }});
  }}
  // 备选核心词：点一下把「铺垫行 + 点题行」一起填进去。
  // 数据在 <project>/artifacts/cover_alts.json，改那份文件就能换备选。
  var ALTS = COVER_ALTS;
  function paintAlts() {{
    var box = document.getElementById("coverAlts");
    box.innerHTML = "";
    if (!ALTS || !ALTS.length) return;
    var w = document.createElement("div"); w.className = "alts";
    var lb = document.createElement("div"); lb.className = "lb";
    lb.textContent = "备选核心词 · 点一下换上去";
    var chips = document.createElement("div"); chips.className = "chips";
    ALTS.forEach(function (a) {{
      var b = document.createElement("button");
      b.type = "button"; b.className = "chip";
      var big = document.createElement("b"); big.textContent = a.t2;
      var sm = document.createElement("span"); sm.textContent = a.t1;
      b.appendChild(sm); b.appendChild(big);
      if (coverState.t1 === a.t1 && coverState.t2 === a.t2) b.classList.add("on");
      b.addEventListener("click", function () {{
        coverState.t1 = a.t1; coverState.t2 = a.t2;
        try {{ localStorage.setItem(KEY + ":cover", JSON.stringify(coverState)); }} catch (e) {{}}
        paintCover(); paintAlts(); flashCover("已换成：" + a.t1 + " / " + a.t2);
      }});
      chips.appendChild(b);
    }});
    w.appendChild(lb); w.appendChild(chips); box.appendChild(w);
  }}

  var coverStatEl = document.getElementById("coverStat"), coverTimer = null;
  function flashCover(m) {{
    coverStatEl.textContent = m;
    if (coverTimer) clearTimeout(coverTimer);
    coverTimer = setTimeout(function () {{ coverStatEl.textContent = ""; }}, 1600);
  }}
  paintCover();
  paintAlts();

  document.getElementById("copyCoverBtn").addEventListener("click", function () {{
    var out = {{ project_id: PROJECT_ID }};
    CFIELDS.forEach(function (f) {{
      var v = coverState[f[0]];
      out[f[0]] = f[0] === "row"
        ? v.split("·").map(function (x) {{ return x.trim(); }}).filter(function (x) {{ return x !== ""; }})
        : v;
    }});
    var text = JSON.stringify(out, null, 2);
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(text).then(
        function () {{ flashCover("已复制，贴回对话"); }},
        function () {{ flashCover("复制失败，手动选中复制"); }});
    }} else {{ flashCover("此浏览器不支持自动复制"); }}
  }});

  document.getElementById("resetCoverBtn").addEventListener("click", function () {{
    CFIELDS.forEach(function (f) {{ coverState[f[0]] = COVER[f[0]] != null ? COVER[f[0]] : ""; }});
    try {{ localStorage.removeItem(KEY + ":cover"); }} catch (e) {{}}
    paintCover(); paintAlts(); flashCover("已还原成当前成片的文案");
  }});

  document.getElementById("copyBtn").addEventListener("click", function () {{
    var failed = CHECKS.filter(function (c) {{ return !state.checks[c[0]]; }});
    var lines = ["审片：" + state.version];
    lines.push("清单：" + (CHECKS.length - failed.length) + "/" + CHECKS.length + " 通过");
    if (failed.length) lines.push("未确认：" + failed.map(function (c) {{ return c[1]; }}).join("、"));
    if (state.notes.trim()) {{ lines.push(""); lines.push(state.notes.trim()); }}
    var text = lines.join("\\n");
    if (navigator.clipboard && navigator.clipboard.writeText) {{
      navigator.clipboard.writeText(text).then(
        function () {{ flash("已复制，贴回对话"); }},
        function () {{ flash("复制失败，手动选中复制"); }});
    }} else {{ flash("此浏览器不支持自动复制"); }}
  }});

  document.getElementById("clearBtn").addEventListener("click", function () {{
    notes.value = ""; state.notes = ""; persist(); flash("已清空");
  }});

  setVersion(state.version);
  tally();
}})();
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_id")
    ap.add_argument("--open", action="store_true", help="生成后用默认浏览器打开")
    args = ap.parse_args()

    proj = PROJECTS / args.project_id
    if not proj.is_dir():
        print(f"找不到项目：{proj}", file=sys.stderr)
        return 1

    marker = load(proj / "project.json") or {}
    report = load(proj / "artifacts" / "render_report.json") or {}
    props = load(proj / "composition" / "props.json")
    script = load(proj / "artifacts" / "script.json")
    decisions = load(proj / "artifacts" / "decision_log.json") or []

    versions = collect_versions(proj)
    if not versions:
        print(f"{args.project_id} 的 renders/ 下没有 mp4，没什么可审的", file=sys.stderr)
        return 1
    scenes = collect_scenes(props, script)

    e = lambda s: html.escape(str(s if s is not None else ""))

    # 事实面板
    out0 = (report.get("outputs") or [{}])[0]
    meta = report.get("metadata") or {}
    cost = meta.get("total_cost_usd")
    facts = [
        ("片长", f"{out0.get('duration_seconds', versions[0]['duration'] or 0):.1f}s", ""),
        ("分辨率", out0.get("resolution") or versions[0].get("res") or "—", ""),
        ("大小", f"{versions[0]['size_mb']}MB" if versions[0].get("size_mb") else "—", ""),
        ("成本", ("$0" if not cost else f"${cost}"), "free" if not cost else ""),
        ("运行时", meta.get("render_runtime", "—"), ""),
        ("合成方式", meta.get("composition_mode", "—"), ""),
    ]
    facts_html = "".join(
        f'<div class="fact"><dt>{e(k)}</dt><dd class="{cls}">{e(val)}</dd></div>'
        for k, val, cls in facts
    )

    # 决策：每个 (category, subject) 只显示最后一条（改期决策覆盖旧的）
    # decision_log 在不同项目里存过两种形态：条目数组，或 {"decisions": [...]}。
    if isinstance(decisions, dict):
        decisions = decisions.get("decisions") or decisions.get("entries") or []
    latest: dict[tuple, dict] = {}
    for d in decisions:
        if not isinstance(d, dict) or not d.get("user_visible"):
            continue
        latest[(d.get("category"), d.get("subject"))] = d
    dec_rows = "".join(
        f'<div class="dec"><dt>{e(d.get("subject"))}</dt>'
        f'<dd><b>{e(d.get("selected"))}</b><br>{e((d.get("reason") or "")[:180])}</dd></div>'
        for d in latest.values()
    )
    decisions_html = (
        f'<section class="block"><h2>当前生效的决策</h2>{dec_rows}</section>' if dec_rows else ""
    )

    def bullets(items, cls=""):
        return "".join(f"<li>{e(x)}</li>" for x in items)

    verify_html = ""
    if report.get("verification_notes"):
        verify_html = (f'<section class="block"><h2>已做过的校验</h2>'
                       f'<ul class="notes">{bullets(report["verification_notes"])}</ul></section>')
    warn_html = ""
    if report.get("warnings"):
        warn_html = (f'<section class="block"><h2>已知问题 / 未做的检查</h2>'
                     f'<ul class="notes warn">{bullets(report["warnings"])}</ul></section>')

    # poster：从**当前这一版**的第 0 帧现抽。
    #
    # 早先是拿 renders/*cover*.jpg 当 poster，有两个毛病：
    #   1. 那是很久以前导出的静态封面，封面改版后不跟着变；
    #   2. 高频词这类项目**根本没有 cover.jpg**，于是 <video> 没有 poster，
    #      未点播放前就是一个纯黑框 —— 看着像"没有视频"（用户就是这么反馈的）。
    # 第 0 帧才是平台真正拿去当封面的那一帧，也永远跟成片同步。
    mp4s = sorted((proj / "renders").glob("*.mp4"),
                  key=lambda x: x.stat().st_mtime, reverse=True)
    poster_attr = ""
    if mp4s:
        poster = proj / "artifacts" / "_poster.jpg"
        newest = mp4s[0]
        if (not poster.exists()) or poster.stat().st_mtime < newest.stat().st_mtime:
            try:
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(newest),
                                "-vf", "select=eq(n\\,0)", "-frames:v", "1", "-q:v", "3",
                                str(poster)], check=True, timeout=60)
            except Exception:
                pass
        if poster.exists():
            poster_attr = ' poster="artifacts/_poster.jpg"'

    # 陈旧告警：script.json 比 props.json 旧，说明改了文案没回写脚本artifact，
    # 页面上显示的旁白就会是几个版本之前的（这个坑真踩过）。
    stale = []
    props_p, script_p = proj / "composition" / "props.json", proj / "artifacts" / "script.json"
    # 早先这里比的是 script.json 与 props.json 的新旧，但**正常流程里 props 本来就该比
    # script 新**（改文案 → 合成 → build_props），只要重跑一次 build_props 就误报。
    # 真正要防的是「改了文案却没重新合成配音」—— 那就得比 script 和音频时长表。
    dur_p = proj / "artifacts" / "_audio_durations.json"
    if script_p.exists() and dur_p.exists() and script_p.stat().st_mtime > dur_p.stat().st_mtime + 60:
        stale.append("script.json 比 _audio_durations.json 新——文案改过但没重新合成配音，"
                     "页面显示的旁白与实际念出来的可能不是一回事")
    newest_mp4 = max((p.stat().st_mtime for p in (proj / "renders").glob("*.mp4")), default=0)
    rep_p = proj / "artifacts" / "render_report.json"
    if rep_p.exists() and newest_mp4 and rep_p.stat().st_mtime < newest_mp4 - 60:
        stale.append("render_report.json 比最新的 mp4 旧——事实面板可能对不上当前版本")
    stale_html = ""
    if stale:
        stale_html = ('<div class="stale"><b>数据可能过期</b><ul>'
                      + "".join(f"<li>{e(x)}</li>" for x in stale) + "</ul></div>")

    page = build_html({
        "poster_attr": poster_attr,
        "stale_html": stale_html,
        "title": marker.get("title", args.project_id),
        "project_id": args.project_id,
        "versions": versions,
        "scenes": scenes,
        "checks": CHECKS,
        # 封面文案的当前值：props.json 里 hook 上真正在用的那份
        "cover_alts": (lambda f: json.loads(f.read_text()) if f.exists() else [])
                      (proj / "artifacts" / "cover_alts.json"),
        "cover_text": (lambda h: {
            "badge": h.get("badge") or (h.get("cover") or {}).get("badge") or "",
            **{k: ((" · ".join(v) if isinstance(v, list) else (v or ""))
                   if (v := (h.get("poster") or {}).get(k)) is not None else "")
               for k in ("t1", "t2", "plaque", "row", "foot")},
        })(props.get("hook") or {}),
        "facts_html": facts_html,
        "decisions_html": decisions_html,
        "verify_html": verify_html,
        "warn_html": warn_html,
    })

    out = proj / "review.html"
    out.write_text(page, encoding="utf-8")
    print(f"{out}  ·  {len(versions)} 个版本 / {len(scenes)} 个场景")
    if args.open:
        subprocess.run(["open", str(out)], check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
