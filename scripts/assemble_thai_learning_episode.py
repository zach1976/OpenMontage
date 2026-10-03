#!/usr/bin/env python3
"""Mechanically assemble one ThaiLearningCards episode from script metadata.

Creative choices live in artifacts/script.json. This helper only concatenates the
already-approved TTS units, derives card timings, and writes Remotion props.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"
REMOTION_PUBLIC = REPO / "remotion-composer" / "public"


def duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def make_silence(path: Path, seconds: float) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{seconds:.3f}", "-c:a", "pcm_s16le", str(path)],
        check=True,
    )


def to_wav(source: Path, target: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(source), "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(target)],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_id")
    args = parser.parse_args()

    project = PROJECTS / args.project_id
    script_path = project / "artifacts" / "script.json"
    script = json.loads(script_path.read_text())
    meta = script["metadata"]
    items = meta["items"]
    units = meta["tts_units"]
    render = meta["render_config"]
    audio_dir = project / "assets" / "audio"
    composition_dir = project / "composition"
    composition_dir.mkdir(parents=True, exist_ok=True)
    work_dir = composition_dir / "audio_work"
    work_dir.mkdir(parents=True, exist_ok=True)

    by_section: dict[str, list[dict]] = {}
    for unit in units:
        by_section.setdefault(unit["section"], []).append(unit)

    parts: list[Path] = []
    timings: list[dict] = []
    cursor = float(render.get("cover_end", 2.4))
    intro = work_dir / "silence_intro.wav"
    make_silence(intro, cursor)
    parts.append(intro)

    for index, (section, item) in enumerate(zip(script["sections"], items, strict=True), start=1):
        section_units = by_section[section["id"]]
        if len(section_units) != 2 or [u["lang"] for u in section_units] != ["th", "zh"]:
            raise ValueError(f"{section['id']} must contain exactly Thai then Chinese TTS units")
        thai = audio_dir / f"{section_units[0]['id']}_x.mp3"
        chinese = audio_dir / f"{section_units[1]['id']}_x.mp3"
        if not thai.exists() or not chinese.exists():
            raise FileNotFoundError(f"Missing synthesized audio for {section['id']}")
        gap = work_dir / f"gap_{index:02d}.wav"
        make_silence(gap, float(render.get("language_gap", 0.16)))
        spoken = duration(thai) + duration(chinese) + float(render.get("language_gap", 0.16))
        block = max(float(render.get("minimum_card_seconds", 3.4)), spoken + float(render.get("tail_gap", 0.34)))
        tail = work_dir / f"tail_{index:02d}.wav"
        make_silence(tail, max(0.12, block - spoken))
        thai_wav = work_dir / f"thai_{index:02d}.wav"
        chinese_wav = work_dir / f"chinese_{index:02d}.wav"
        to_wav(thai, thai_wav)
        to_wav(chinese, chinese_wav)
        parts.extend([thai_wav, gap, chinese_wav, tail])
        timings.append({**item, "start": round(cursor, 3), "end": round(cursor + block, 3)})
        cursor += block

    outro_seconds = float(render.get("outro_seconds", 3.5))
    outro = work_dir / "silence_outro.wav"
    make_silence(outro, outro_seconds)
    parts.append(outro)

    concat_list = work_dir / "concat.txt"
    concat_list.write_text("\n".join(f"file '{p.resolve()}'" for p in parts) + "\n")
    narration = project / "assets" / "audio" / "episode_narration.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(narration)],
        check=True,
    )

    public_rel = Path("series") / args.project_id
    public_dir = REMOTION_PUBLIC / public_rel
    public_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(narration, public_dir / "narration.wav")
    music_source = REPO / render["music_source"]
    music_target = project / "assets" / "music" / "background.mp3"
    music_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(music_source, music_target)
    shutil.copy2(music_target, public_dir / "background.mp3")

    props = {
        "seriesName": render["series_name"],
        "episode": render["episode"],
        "topic": render["topic"],
        "hook": render["hook"],
        "accent": render["accent"],
        "accent2": render.get("accent2", "#F5C45A"),
        "durationSeconds": round(cursor + outro_seconds, 3),
        "coverEnd": float(render.get("cover_end", 2.4)),
        "outroStart": round(cursor, 3),
        "narrationSrc": str(public_rel / "narration.wav"),
        "musicSrc": str(public_rel / "background.mp3"),
        "backgroundSrc": render.get("background_src"),
        "mode": render.get("mode", "cards"),
        "items": timings,
        "speechRanges": [{"start": i["start"], "end": i["end"] - float(render.get("tail_gap", 0.34))} for i in timings],
    }
    props_path = composition_dir / "props.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False, indent=2))
    print(json.dumps({"props": str(props_path), "narration": str(narration), "duration_seconds": props["durationSeconds"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
