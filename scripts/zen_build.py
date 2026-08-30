#!/usr/bin/env python3
"""禅意重做版通用的排时间轴 + 切底片。各集共用（这是引擎知识，不是创意）。

    python3 scripts/zen_build.py <project_id> [--bg]   # --bg 才重切底片（慢）

排法与 01 完全一致，两条来自 01 的纪律：
  · 收的是**死时间**不是留白；跟读空档按词长走 `max(0.95, td+0.35)`。
  · `Sequence from` 是**相对本场景**的，所以 props 里给的绝对秒，组件里必须减 `start`。
"""
import json, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BG_SRC = Path.home() / "projects/lang1000/marketing/video/series_zen/assets/bg"
XF = 1.0


def timeline(proj: Path) -> dict:
    S = json.loads((proj / "artifacts/script.json").read_text())
    D = json.loads((proj / "artifacts/_audio_durations.json").read_text())
    M = S["metadata"]
    SENT, WORDS = M["sentence"], M["cards"]
    # 目标语言后缀（th / vi）从 tts_units 自己读，别写死 —— 这套排法两个号共用
    LG = next(u["lang"] for u in M["tts_units"] if u["lang"] != "zh")
    disp = {k: v for k, v in SENT.items() if k not in ("thaiDisplay", "thaiLines")}
    disp["lines"] = SENT["thaiLines"]

    speak, t = [], 0.0
    hook_dur = 0.6 + D["s00_hook_zh"] + 1.1
    hook = dict(start=0.0, dur=round(hook_dur, 3), text=M["hook"],
                thaiLine=" ".join(SENT["thaiLines"]),
                audio="audio/s00_hook_zh_x.mp3", audioAt=0.6)
    speak.append([0.6, round(0.6 + D["s00_hook_zh"], 3)])
    t += hook_dur

    th_at = t + 0.55
    zh_at = th_at + D[f"s01_sent_{LG}"] + 0.45
    sent_dur = (zh_at + D["s01_sent_zh"] + 1.0) - t
    sentence = dict(start=round(t, 3), dur=round(sent_dur, 3), **disp,
                    thAudio=f"audio/s01_sent_{LG}_x.mp3", thAt=round(th_at, 3),
                    audio="audio/s01_sent_zh_x.mp3", audioAt=round(zh_at, 3))
    speak += [[round(th_at, 3), round(th_at + D[f"s01_sent_{LG}"], 3)],
              [round(zh_at, 3), round(zh_at + D["s01_sent_zh"], 3)]]
    t += sent_dur

    words = []
    for c in WORDS:
        zd, td = D[f'{c["id"]}_zh'], D[f'{c["id"]}_{LG}']
        zh_at = t + 0.32
        th_at = zh_at + zd + 0.25
        th_at2 = th_at + td + 0.55
        dur = (th_at2 + td + max(0.95, td + 0.35)) - t
        speak += [[round(zh_at, 3), round(zh_at + zd, 3)],
                  [round(th_at, 3), round(th_at + td, 3)],
                  [round(th_at2, 3), round(th_at2 + td, 3)]]
        words.append(dict(id=c["id"], thai=c["thai"], roman=c["roman"], zh=c["zh"],
                          start=round(t, 3), dur=round(dur, 3),
                          zhAudio=f'audio/{c["id"]}_zh_x.mp3', thAudio=f'audio/{c["id"]}_{LG}_x.mp3',
                          zhAt=round(zh_at, 3), thAt=round(th_at, 3), thAt2=round(th_at2, 3)))
        t += dur

    ag_at = t + 0.65
    again_dur = (ag_at + D[f"s09_again_{LG}"] + 1.5) - t
    again = dict(start=round(t, 3), dur=round(again_dur, 3), **disp,
                 thAudio=f"audio/s09_again_{LG}_x.mp3", thAt=round(ag_at, 3))
    speak.append([round(ag_at, 3), round(ag_at + D[f"s09_again_{LG}"], 3)])
    t += again_dur

    out_at = t + 0.45
    out_dur = (out_at + D["s10_outro_zh"] + 1.4) - t
    outro = dict(start=round(t, 3), dur=round(out_dur, 3),
                 audio="audio/s10_outro_zh_x.mp3", audioAt=round(out_at, 3))
    speak.append([round(out_at, 3), round(out_at + D["s10_outro_zh"], 3)])
    t += out_dur

    bgp = proj / "artifacts/bg_plan.json"
    # 封面底图由 import_cover_src.py 接进来；重排时间轴不能把它冲掉
    cover = "img/cover.png" if (proj / "composition/public/img/cover.png").exists() else None
    return dict(width=1080, height=1920, totalSeconds=round(t, 3), totalFrames=int(round(t * 30)),
                hook=hook, sentence=sentence, words=words, again=again, outro=outro, cover=cover,
                bg=json.loads(bgp.read_text()) if bgp.exists() else [],
                bgm=dict(src="music/bgm.mp3", gain=0.085), speak=speak, fps=30)


def cut_bg(proj: Path, props: dict) -> list:
    """按分段把横屏空镜切成竖屏底片。分段边界从内容来：
    钩子+整句一条、词卡对半分两条 —— 换了就不回来。"""
    spec = json.loads((proj / "artifacts/bg_spec.json").read_text())
    out = proj / "composition/public/video"
    out.mkdir(parents=True, exist_ok=True)
    W = [w["start"] for w in props["words"]]
    mid = W[len(W) // 2]
    bounds = [(0.0, W[0]), (W[0], mid), (mid, props["totalSeconds"])]
    plan = []
    for i, ((a, b), c) in enumerate(zip(bounds, spec["clips"]), 1):
        src = BG_SRC / c["file"]
        need = round(b - a + XF, 3)
        have = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                     "-of", "csv=p=0", str(src)],
                                    capture_output=True, text=True, check=True).stdout.strip())
        speed = max(1.0, need / have)
        x = c["x"]
        vf = (f"crop=trunc(ih*9/16/2)*2:ih:(iw-trunc(ih*9/16/2)*2)*{x}:0,scale=1080:1920,"
              f"setpts={speed:.4f}*PTS,fps=30,eq={spec['grade']},gblur=sigma=1.2")
        dst = out / f"bg{i}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", vf,
                        "-an", "-t", f"{need}", "-c:v", "libx264", "-crf", "22",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dst)], check=True)
        plan.append(dict(src=f"video/bg{i}.mp4", start=round(a, 3), dur=round(b - a, 3), xf=XF,
                         origin=c["file"], x=x, slow=round(speed, 3)))
        print(f"  bg{i}  {a:6.2f} → {b:6.2f}  ({need:5.2f}s / 素材 {have:5.2f}s"
              f"{'，放慢 ×%.2f' % speed if speed > 1.01 else '，原速'})  {c['file']}")
    (proj / "artifacts/bg_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return plan


def main() -> int:
    pid = sys.argv[1]
    proj = REPO / "projects" / pid
    props = timeline(proj)
    if "--bg" in sys.argv:
        props["bg"] = cut_bg(proj, props)
    ed = json.loads((proj / "artifacts/edit_decisions.json").read_text())
    gain = {"thai-zen-02-letgo-v2": 0.085, "thai-zen-03-calm-v2": 0.08,
            "thai-zen-04-enough-v2": 0.085, "thai-zen-05-beginagain-v2": 0.09}.get(pid, 0.085)
    props["bgm"]["gain"] = gain
    (proj / "composition/props.json").write_text(
        json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f'{proj / "composition/props.json"}  ·  {props["totalSeconds"]}s / {props["totalFrames"]} 帧')
    print(f'  钩子   {0:6.2f} → {props["hook"]["dur"]:6.2f}')
    s = props["sentence"]; print(f'  整句   {s["start"]:6.2f} → {s["start"]+s["dur"]:6.2f}')
    for w in props["words"]:
        print(f'  {w["thai"]:12} {w["start"]:6.2f} → {w["start"]+w["dur"]:6.2f}   {w["zh"]}')
    a, o = props["again"], props["outro"]
    print(f'  再读   {a["start"]:6.2f} → {a["start"]+a["dur"]:6.2f}')
    print(f'  片尾   {o["start"]:6.2f} → {o["start"]+o["dur"]:6.2f}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
