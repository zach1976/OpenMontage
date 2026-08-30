#!/usr/bin/env python3
"""按 artifacts/script.json 合成全部旁白 —— 文案的唯一事实来源就是那个文件。

背景：早先文案存在两个地方（script.json 与各自的生成脚本），改了一处忘了另一处，
审片页显示的旁白落后了三个版本。现在合成只认 script.json，且合成后会把
每个 section 的 text 按其 tts_units 重新拼一遍，让"显示的"与"念出来的"不可能漂。

script.json 里需要的两块（都放在 metadata 下，schema 允许自由字段）：

    "metadata": {
      "tts": {
        "engine": "edge",                      # 目前只实现 edge-tts（免费、无 key）
        "voices": {"zh": "zh-CN-XiaoxiaoNeural", "th": "th-TH-PremwadeeNeural"},
        "rates":  {"th": "-30%"},              # 不写就是常速
        "pitches": {"zh": "-12Hz"}             # 不写就是原调；压低 = 更沉
      },
      "tts_units": [
        {"id": "s00_hook_zh", "section": "s00_hook", "lang": "zh", "text": "..."},
        {"id": "s01_mu_th",   "section": "s01_mu",   "lang": "th", "text": "หมู",
         "display": "{text}（读两遍）"},        # 可选：拼回 section.text 时怎么写
        ...
      ]
    }

用法：
    python3 scripts/synth_narration.py <project_id>
    python3 scripts/synth_narration.py <project_id> --dry-run   # 只报字数，不合成
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"

# edge-tts 之外的引擎都要花钱，这里不给默认路径——要用得显式改配置并走费用确认流程。
FREE_ENGINES = {"edge"}

TRIM_AND_NORM = (
    "silenceremove=start_periods=1:start_silence=0.05:start_threshold=-50dB:detection=peak,"
    "areverse,"
    "silenceremove=start_periods=1:start_silence=0.10:start_threshold=-50dB:detection=peak,"
    "areverse,"
    "loudnorm=I=-16:TP=-1.5:LRA=11"
)


def probe(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return round(float(out.stdout.strip()), 3)


def edge_say(text: str, voice: str, rate: str | None, raw: Path,
             pitch: str | None = None) -> None:
    """edge-tts 偶发 NoAudioReceived（微软端点抽风），重试三次。

    rate / pitch 都用 `--rate=<v>` 这种等号写法——分开传过一次没拿到音频。
    pitch 是 Hz 偏移（"-12Hz"）：edge-tts 的中文男声只有四个，
    真正"沉稳"那一档要靠 Yunjian + 压调 + 降速 配出来，光换音色不够。
    """
    cmd = ["edge-tts", "--voice", voice, "--text", text, "--write-media", str(raw)]
    if rate and rate not in ("+0%", "0%"):
        cmd.insert(3, f"--rate={rate}")
    if pitch and pitch not in ("+0Hz", "0Hz"):
        cmd.insert(3, f"--pitch={pitch}")
    last = ""
    for attempt in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and raw.exists() and raw.stat().st_size > 1000:
            return
        last = (r.stderr or "")[-200:]
        time.sleep(1.5)
    raise RuntimeError(f"edge-tts 三次都失败：{last}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_id")
    ap.add_argument("--dry-run", action="store_true", help="只报字数与预计费用，不合成")
    args = ap.parse_args()

    proj = PROJECTS / args.project_id
    script_path = proj / "artifacts" / "script.json"
    if not script_path.exists():
        print(f"找不到 {script_path}", file=sys.stderr)
        return 1

    script = json.loads(script_path.read_text())
    meta = script.get("metadata") or {}
    cfg = meta.get("tts") or {}
    units = meta.get("tts_units") or []
    if not units:
        print("script.json 的 metadata.tts_units 是空的——没有可合成的内容。", file=sys.stderr)
        print("文案现在必须写在 script.json 里，生成脚本不再硬编码文本。", file=sys.stderr)
        return 1

    engine = cfg.get("engine", "edge")
    voices = cfg.get("voices") or {}
    rates = cfg.get("rates") or {}
    pitches = cfg.get("pitches") or {}

    total_chars = sum(len(u["text"]) for u in units)
    print(f"{len(units)} 段 / {total_chars} 字符 / 引擎 {engine}")
    if engine not in FREE_ENGINES:
        print(f"\n⚠️  {engine} 不是免费引擎，本脚本不执行付费合成。", file=sys.stderr)
        print("   走费用确认流程、拿到明确许可后再单独处理。", file=sys.stderr)
        return 2
    if args.dry_run:
        for u in units:
            print(f"  {u['id']:16} {u['lang']}  {len(u['text']):3} 字符  {u['text'][:30]}")
        print("\n(dry-run，未合成；edge-tts 零成本)")
        return 0

    audio = proj / "assets" / "audio"
    audio.mkdir(parents=True, exist_ok=True)
    durations: dict[str, float] = {}

    for u in units:
        lang = u["lang"]
        voice = voices.get(lang)
        if not voice:
            print(f"metadata.tts.voices 里没有 {lang} 的音色", file=sys.stderr)
            return 1
        raw = audio / f"{u['id']}_raw.mp3"
        final = audio / f"{u['id']}_x.mp3"
        edge_say(u["text"], voice, rates.get(lang), raw, pitches.get(lang))
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw),
             "-af", TRIM_AND_NORM, "-ar", "44100", "-b:a", "192k", str(final)],
            check=True,
        )
        durations[u["id"]] = probe(final)
        print(f"  {u['id']:16} {durations[u['id']]:6.2f}s  {voice.split('-')[-1]:20} {u['text'][:26]}")

    (proj / "artifacts" / "_audio_durations.json").write_text(
        json.dumps(durations, indent=2), encoding="utf-8"
    )

    # 合成产物落在 assets/audio/，但 Remotion 合成读的是 composition/public/audio/。
    # 早先靠手动 cp 同步，改完文案忘了拷 —— 渲出来的片子旁白还是旧的，肉眼完全看不出。
    # 现在合成完就自动同步，这一步不再可能漏。
    public_audio = proj / "composition" / "public" / "audio"
    if (proj / "composition").is_dir():
        public_audio.mkdir(parents=True, exist_ok=True)
        n = 0
        for uid in durations:
            src = audio / f"{uid}_x.mp3"
            if src.exists():
                shutil.copy2(src, public_audio / src.name)
                n += 1
        print(f"已同步 {n} 段到 {public_audio.relative_to(REPO)}")

    # 把 section.text 按 units 重拼一遍——显示用的文本从此不可能与念出来的漂开。
    by_section: dict[str, list[dict]] = {}
    for u in units:
        by_section.setdefault(u.get("section", u["id"]), []).append(u)
    touched = 0
    for sec in script.get("sections", []):
        us = by_section.get(sec["id"])
        if not us:
            continue
        parts = [u.get("display", "{text}").format(text=u["text"]) for u in us]
        joined = " → ".join(parts)
        if sec.get("text") != joined:
            sec["text"] = joined
            touched += 1
    if touched:
        script_path.write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nscript.json：{touched} 个 section 的 text 已按 tts_units 重拼")

    print(f"\n合成完毕：{len(units)} 段，旁白总时长 {sum(durations.values()):.1f}s，费用 $0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
