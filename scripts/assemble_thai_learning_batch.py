#!/usr/bin/env python3
"""Assemble narration and Remotion props for every episode in a Thai batch."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REMOTION_PUBLIC = REPO / "remotion-composer" / "public"


def run(*args: str) -> None:
    subprocess.run(list(args), check=True)


def duration(path: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def silence(path: Path, seconds: float) -> None:
    run("ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{seconds:.3f}", "-c:a", "pcm_s16le", str(path))


def wav(source: Path, target: Path) -> None:
    run("ffmpeg", "-y", "-loglevel", "error", "-i", str(source), "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(target))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_id")
    parser.add_argument("--episode")
    args = parser.parse_args()
    project = REPO / "projects" / args.project_id
    script = json.loads((project / "artifacts" / "script.json").read_text())
    target_lang = script.get("metadata", {}).get("target_lang", "th")
    units = {u["id"]: u for u in script["metadata"]["tts_units"]}
    episodes = script["metadata"]["episodes"]
    if args.episode:
        episodes = [ep for ep in episodes if ep["id"] == args.episode]
        if not episodes:
            raise ValueError(f"Unknown episode: {args.episode}")

    audio_dir = project / "assets" / "audio"
    outro_audio = audio_dir / "series_outro_zh_x.mp3"
    if not outro_audio.exists():
        raise FileNotFoundError(f"Missing shared outro slogan audio: {outro_audio}")
    outro_speech_seconds = duration(outro_audio)
    music_source = REPO / episodes[0]["render_config"]["music_source"]
    music_target = project / "assets" / "music" / "background.mp3"
    music_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(music_source, music_target)
    results = []

    for episode in episodes:
        eid = episode["id"]
        render = episode["render_config"]
        comp_dir = project / "composition" / eid
        work = comp_dir / "audio_work"
        work.mkdir(parents=True, exist_ok=True)
        hook_id = f"{eid}_hook_zh"
        if hook_id not in units:
            raise ValueError(f"Missing opening hook unit for {eid}")
        hook_audio = audio_dir / f"{hook_id}_x.mp3"
        if not hook_audio.exists():
            raise FileNotFoundError(f"Missing synthesized opening hook for {eid}")
        hook_seconds = duration(hook_audio)
        lead_seconds = 0.16
        tail_seconds = 0.26
        cover_end = max(float(render.get("cover_end", 2.4)), lead_seconds + hook_seconds + tail_seconds)
        lead = work / "intro_lead.wav"
        hook_wav = work / "intro_hook.wav"
        hook_tail = work / "intro_tail.wav"
        silence(lead, lead_seconds)
        wav(hook_audio, hook_wav)
        silence(hook_tail, max(0.12, cover_end - lead_seconds - hook_seconds))
        parts = [lead, hook_wav, hook_tail]
        cursor = cover_end
        timings = []
        for index, item in enumerate(episode["items"], start=1):
            th_id = f"{eid}_{index:02d}_th"
            zh_id = f"{eid}_{index:02d}_zh"
            if th_id not in units or zh_id not in units:
                raise ValueError(f"Missing units for {eid} item {index}")
            thai = audio_dir / f"{th_id}_x.mp3"
            chinese = audio_dir / f"{zh_id}_x.mp3"
            if not thai.exists() or not chinese.exists():
                raise FileNotFoundError(f"Missing synthesized audio for {eid} item {index}")
            gap_seconds = float(render.get("language_gap", 0.16))
            gap = work / f"gap_{index:02d}.wav"
            silence(gap, gap_seconds)
            spoken = duration(thai) + gap_seconds + duration(chinese)
            word_parts = []
            word_timings = []
            for word_index, _word in enumerate(item.get("breakdown", []), start=1):
                word_prefix = f"{eid}_{index:02d}_word{word_index:02d}"
                word_thai = audio_dir / f"{word_prefix}_th_x.mp3"
                word_chinese = audio_dir / f"{word_prefix}_zh_x.mp3"
                if not word_thai.exists() or not word_chinese.exists():
                    raise FileNotFoundError(f"Missing word audio for {word_prefix}")
                word_lead = work / f"word_lead_{index:02d}_{word_index:02d}.wav"
                word_gap = work / f"word_gap_{index:02d}_{word_index:02d}.wav"
                word_th_wav = work / f"word_th_{index:02d}_{word_index:02d}.wav"
                word_zh_wav = work / f"word_zh_{index:02d}_{word_index:02d}.wav"
                silence(word_lead, 0.12)
                silence(word_gap, 0.08)
                wav(word_thai, word_th_wav)
                wav(word_chinese, word_zh_wav)
                word_start = cursor + spoken + 0.12
                word_end = word_start + duration(word_thai) + 0.08 + duration(word_chinese)
                word_timings.append({"start": round(word_start, 3), "end": round(word_end, 3)})
                word_parts.extend([word_lead, word_th_wav, word_gap, word_zh_wav])
                spoken += 0.12 + duration(word_thai) + 0.08 + duration(word_chinese)
            block = max(float(render.get("minimum_card_seconds", 3.5)), spoken + float(render.get("tail_gap", 0.32)))
            tail = work / f"tail_{index:02d}.wav"
            silence(tail, max(0.12, block - spoken))
            th_wav, zh_wav = work / f"thai_{index:02d}.wav", work / f"chinese_{index:02d}.wav"
            wav(thai, th_wav)
            wav(chinese, zh_wav)
            parts.extend([th_wav, gap, zh_wav, *word_parts, tail])
            timings.append({**item, "start": round(cursor, 3), "end": round(cursor + block, 3), "wordTimings": word_timings})
            cursor += block
        recap = None
        recap_speech_end = None
        recap_words = episode.get("recap_words", [])
        if recap_words:
            recap_start = cursor
            intro = audio_dir / f"{eid}_recap_intro_zh_x.mp3"
            if not intro.exists():
                raise FileNotFoundError(f"Missing recap intro audio: {intro}")
            intro_wav = work / "recap_intro.wav"
            wav(intro, intro_wav)
            parts.append(intro_wav)
            spoken = duration(intro)
            timed_words = []
            for word_index, word in enumerate(recap_words, start=1):
                prefix = f"{eid}_recap_word{word_index:02d}"
                thai = audio_dir / f"{prefix}_th_x.mp3"
                chinese = audio_dir / f"{prefix}_zh_x.mp3"
                if not thai.exists() or not chinese.exists():
                    raise FileNotFoundError(f"Missing recap word audio for {prefix}")
                lead = work / f"recap_lead_{word_index:02d}.wav"
                gap = work / f"recap_gap_{word_index:02d}.wav"
                thai_wav = work / f"recap_th_{word_index:02d}.wav"
                chinese_wav = work / f"recap_zh_{word_index:02d}.wav"
                silence(lead, 0.16)
                silence(gap, 0.08)
                wav(thai, thai_wav)
                wav(chinese, chinese_wav)
                word_start = recap_start + spoken + 0.16
                word_end = word_start + duration(thai) + 0.08 + duration(chinese)
                timed_words.append({**word, "start": round(word_start, 3), "end": round(word_end, 3)})
                parts.extend([lead, thai_wav, gap, chinese_wav])
                spoken += 0.16 + duration(thai) + 0.08 + duration(chinese)
            recap_speech_end = recap_start + spoken
            recap_duration = max(float(render.get("recap_seconds", 10.0)), spoken + 0.36)
            recap_tail = work / "recap_tail.wav"
            silence(recap_tail, max(0.12, recap_duration - spoken))
            parts.append(recap_tail)
            cursor += recap_duration
            recap = {"start": round(recap_start, 3), "end": round(cursor, 3), "words": timed_words}
        outro_start = cursor
        outro_lead_seconds = 0.18
        outro_tail_seconds = 0.36
        outro_seconds = max(float(render.get("outro_seconds", 3.5)), outro_lead_seconds + outro_speech_seconds + outro_tail_seconds)
        outro_lead = work / "outro_lead.wav"
        outro_wav = work / "outro_slogan.wav"
        outro_tail = work / "outro_tail.wav"
        silence(outro_lead, outro_lead_seconds)
        wav(outro_audio, outro_wav)
        silence(outro_tail, max(0.12, outro_seconds - outro_lead_seconds - outro_speech_seconds))
        parts.extend([outro_lead, outro_wav, outro_tail])
        concat = work / "concat.txt"
        concat.write_text("\n".join(f"file '{p.resolve()}'" for p in parts) + "\n")
        narration = audio_dir / f"{eid}_narration.wav"
        run("ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(narration))

        public_rel = Path("series") / args.project_id / eid
        public_dir = REMOTION_PUBLIC / public_rel
        public_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(narration, public_dir / "narration.wav")
        shutil.copy2(music_target, public_dir / "background.mp3")
        props = {
            "seriesName": render["series_name"], "episode": render["episode"], "topic": render["topic"], "hook": render["hook"],
            "accent": render["accent"], "accent2": render.get("accent2", "#F5C45A"), "durationSeconds": round(cursor + outro_seconds, 3),
            "coverEnd": round(cover_end, 3), "outroStart": round(outro_start, 3), "narrationSrc": str(public_rel / "narration.wav"),
            "musicSrc": str(public_rel / "background.mp3"), "backgroundSrc": render.get("background_src"), "mode": render.get("mode", "cards"),
            "coverTitle": render.get("cover_title"),
            "appIconSrc": "app/viet_app_icon.png" if target_lang == "vi" else "app/app_icon.png",
            "items": timings, "recap": recap,
            "speechRanges": [{"start": lead_seconds, "end": round(lead_seconds + hook_seconds, 3)}] + [{"start": i["start"], "end": i["end"] - float(render.get("tail_gap", 0.32))} for i in timings] + ([{"start": recap["start"], "end": round(recap_speech_end, 3)}] if recap else []) + [{"start": round(outro_start + outro_lead_seconds, 3), "end": round(outro_start + outro_lead_seconds + outro_speech_seconds, 3)}],
        }
        props_path = comp_dir / "props.json"
        props_path.write_text(json.dumps(props, ensure_ascii=False, indent=2) + "\n")
        results.append({"episode": eid, "props": str(props_path), "duration": props["durationSeconds"]})
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
