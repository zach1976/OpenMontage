#!/usr/bin/env python3
"""高频词表格版通用排时间轴（แล้ว 那一集定的节奏，16 支重做批共用）。

    python3 scripts/hf_build.py projects/<pid>

原文档：—— 从 2026-05-12 的老版式做的变体，由实测音频时长排时间轴。

老版式（`lang1000/.../make_thai_*_video.py`）成在四件事，这一版全部保留：
  1. 一条给 **12 个真用法**（信息密度 = 观众觉得赚到）
  2. 表格式版面，**静音也能扫读**
  3. **逐行推进**，跟得住
  4. **汉字 icon 当锚点**，一眼定位这一行讲什么

去掉老版三个毛病：谐音（读不出也不可靠）、烧屏 hashtag、12 条平铺流水账。
12 条按 แล้ว 的三种用法**分成三页**，每页收尾四条连读一遍并留跟读空档 ——
这样既保住密度，又把系列的「读两遍 + 跟读」纪律接了回来。

片长上限 60 秒，所以这里每处停顿都短：讲过的行不再重复，靠"打勾变暗"留在画面上。
"""
import json, sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
S = json.load(open(ROOT / "artifacts/script.json"))
D = json.load(open(ROOT / "artifacts/_audio_durations.json"))
M = S["metadata"]
ROWS = {r["id"]: r for r in M["rows"]}
# 目标语言后缀（th / vi）从 tts_units 自己读，别写死 —— 这套排法两个号共用
LG = next(u["lang"] for u in M["tts_units"] if u["lang"] != "zh")

speak, t = [], 0.0

# 钩子：中文品牌 → 泰语词 → 中文释义（老版就是这三段，节奏很好用）
h_a, h_b, h_c = 0.25, 0.0, 0.0
h_b = h_a + D["s00_hook_a"] + 0.24
h_c = h_b + D["s00_hook_b"] + 0.24
hook_dur = h_c + D["s00_hook_c"] + 0.60
hook = dict(start=0.0, dur=round(hook_dur, 3),
            audio=[dict(src="audio/s00_hook_a_x.mp3", at=round(h_a, 3)),
                   dict(src="audio/s00_hook_b_x.mp3", at=round(h_b, 3)),
                   dict(src="audio/s00_hook_c_x.mp3", at=round(h_c, 3))])
for k, at in (("s00_hook_a", h_a), ("s00_hook_b", h_b), ("s00_hook_c", h_c)):
    speak.append([round(at, 3), round(at + D[k], 3)])
t += hook_dur

pages = []
for pi, pg in enumerate(M["pages"], 1):
    p_start = t
    tid = f"p{pi}_title_zh"
    title_at = t + 0.25
    t = title_at + D[tid] + 0.32
    speak.append([round(title_at, 3), round(title_at + D[tid], 3)])

    rows = []
    for rid in pg["rows"]:
        zh_at = t + 0.12
        th_at = zh_at + D[f"{rid}_zh"] + 0.16
        end = th_at + D[f"{rid}_{LG}"] + 0.24
        speak += [[round(zh_at, 3), round(zh_at + D[f'{rid}_zh'], 3)],
                  [round(th_at, 3), round(th_at + D[f'{rid}_{LG}'], 3)]]
        rows.append(dict(**ROWS[rid], start=round(t, 3), dur=round(end - t, 3),
                         zhAudio=f"audio/{rid}_zh_x.mp3", thAudio=f"audio/{rid}_{LG}_x.mp3",
                         zhAt=round(zh_at, 3), thAt=round(th_at, 3)))
        t = end

    # 页尾：四条连读一遍 + 跟读空档（空档按连读长度给，短组不空转）
    eid = f"p{pi}_echo_{LG}"
    echo_at = t + 0.35
    # 跟读空档按连读长度给，下限 1.0s —— 收的是死时间，不是跟读时间
    gap = max(1.0, D[eid] * 0.42)
    echo_end = echo_at + D[eid] + gap
    speak.append([round(echo_at, 3), round(echo_at + D[eid], 3)])
    pages.append(dict(index=pi, title=pg["title"], start=round(p_start, 3),
                      dur=round(echo_end - p_start, 3), rows=rows,
                      titleAudio=f"audio/{tid}_x.mp3", titleAt=round(title_at, 3),
                      echoAudio=f"audio/{eid}_x.mp3", echoAt=round(echo_at, 3),
                      echoDur=round(D[eid], 3)))
    t = echo_end

out_at = t + 0.4
out_dur = (out_at + D["s10_outro_zh"] + 1.0) - t
outro = dict(start=round(t, 3), dur=round(out_dur, 3),
             audio="audio/s10_outro_zh_x.mp3", audioAt=round(out_at, 3))
speak.append([round(out_at, 3), round(out_at + D["s10_outro_zh"], 3)])
t += out_dur

photo = "img/photo.jpg" if (ROOT / "composition/public/img/photo.jpg").exists() else None

props = dict(width=1080, height=1920, totalSeconds=round(t, 3), totalFrames=int(round(t * 30)),
             word=M["word"], badge=M["badge"], poster=M["poster"],
             palette=M.get("palette"), photo=photo,
             hook=hook, pages=pages, outro=outro,
             bgm=dict(src="music/bgm.mp3", gain=0.075), speak=speak, fps=30)
(ROOT / "composition/props.json").write_text(
    json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")
print(f'{ROOT/"composition/props.json"}  ·  {props["totalSeconds"]}s / {props["totalFrames"]} 帧')
print(f'  钩子   0.00 → {hook["dur"]:6.2f}')
for p in pages:
    print(f'  第{p["index"]}组 {p["start"]:6.2f} → {p["start"]+p["dur"]:6.2f}  {p["title"]}')
    for r in p["rows"]:
        print(f'      {r["icon"]} {r["zh"]:8} {r["th"]:14} {r["start"]:6.2f} → {r["start"]+r["dur"]:6.2f}')
print(f'  片尾   {outro["start"]:6.2f} → {outro["start"]+outro["dur"]:6.2f}')
if props["totalSeconds"] > 60:
    print(f'\n⚠ 超 60 秒上限 {props["totalSeconds"]-60:.1f}s')
