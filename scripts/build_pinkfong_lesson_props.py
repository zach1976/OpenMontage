#!/usr/bin/env python3
"""Build exact Remotion timing from the finished Thai and Mandarin speech clips."""

from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"
FPS = 30


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build(project: Path) -> float:
    art = project / "artifacts"
    script = json.loads((art / "script.json").read_text())
    scene_plan = json.loads((art / "scene_plan.json").read_text())
    durations = json.loads((art / "_audio_durations.json").read_text())
    units = script["metadata"]["tts_units"]
    letters = script["metadata"]["letters"]
    missing = [u["id"] for u in units if u["id"] not in durations]
    if missing:
        raise RuntimeError(f"{project.name} missing speech audio: {missing}")

    public_audio = project / "public/narration"
    public_audio.mkdir(parents=True, exist_ok=True)
    for unit in units:
        filename = unit["id"] + "_x.mp3"
        shutil.copy2(project / "assets/audio" / filename, public_audio / filename)

    cursor = 0
    lessons = []
    song_cursor = 0
    song_length = json.loads((art / "asset_manifest.json").read_text())["assets"][0]["duration_seconds"]
    song_frames = math.ceil(song_length * FPS)
    for letter in letters:
        lesson_id = "lesson_" + letter["id"]
        local = 6
        lesson_units = []
        records = [u for u in units if u["section"] == lesson_id]
        word_map = {x["id"]: x for x in letter["words_detailed"]}
        for unit in records:
            if unit["id"].endswith("_th") and "_w" in unit["id"]:
                word_id = unit["id"][:-3]
                song_id = word_id + "_song"
                sung_seconds = word_map[word_id]["song_duration_seconds"]
                frames = math.ceil(sung_seconds * FPS) + 2
                lesson_units.append({"id": song_id, "text": "歌里唱的", "lang": "song",
                                     "frames": frames, "start": local})
                local += frames + 3
            frames = math.ceil(durations[unit["id"]] * FPS) + 3
            lesson_units.append({"id": unit["id"], "text": unit["text"],
                                 "lang": unit["lang"], "frames": frames, "start": local})
            local += frames + 3
        source_seconds = letter["source_end_seconds"] - letter["source_start_seconds"]
        next_song_cursor = song_cursor + math.ceil(source_seconds * FPS)
        lessons.append({"id": letter["id"], "letter": letter["letter"], "name": letter["name"],
                        "phrase": letter["phrase"], "chinese": letter["chinese"], "image": letter["image"],
                        "words": [{"th": x["th"], "zh": x["zh"]} for x in letter["words_detailed"]],
                        "relation": letter["relation"], "units": lesson_units, "start": cursor,
                        "frames": local + 10, "songStartFrame": song_cursor,
                        "songEndFrame": min(song_frames, next_song_cursor)})
        cursor += local + 10
        song_cursor = next_song_cursor
    if lessons:
        lessons[-1]["songEndFrame"] = song_frames
    intro_frames = max(120, math.ceil(durations["intro"] * FPS) + 18)
    bridge_frames = max(70, math.ceil(durations["bridge"] * FPS) + 10)
    outro_frames = max(105, math.ceil(durations["outro"] * FPS) + 20)
    recap_voice_frames = math.ceil(durations["recap"] * FPS) if "recap" in durations else 0
    recap_frames = recap_voice_frames + 12 + 2 * song_frames if recap_voice_frames else 0
    total = intro_frames + song_frames + bridge_frames + cursor + recap_frames + outro_frames
    props = {"introFrames": intro_frames, "songFrames": song_frames,
             "bridgeFrames": bridge_frames, "outroFrames": outro_frames,
             "recapFrames": recap_frames, "recapVoiceFrames": recap_voice_frames,
             "totalFrames": total, "episode": script["metadata"]["episode"],
             "lettersLabel": " ".join(x["letter"] for x in letters),
             "introAudioFrames": math.ceil(durations["intro"] * FPS),
             "bridgeAudioFrames": math.ceil(durations["bridge"] * FPS),
             "outroAudioFrames": math.ceil(durations["outro"] * FPS),
             "lessons": lessons}
    boundaries = [0, intro_frames, intro_frames + song_frames,
                  intro_frames + song_frames + bridge_frames]
    lesson_start = boundaries[-1]
    boundaries.extend(lesson_start + sum(item["frames"] for item in lessons[:i+1])
                      for i in range(len(lessons)))
    if recap_frames:
        boundaries.append(boundaries[-1] + recap_frames)
    boundaries.append(total)
    for index, section in enumerate(script["sections"]):
        section["start_seconds"] = round(boundaries[index] / FPS, 3)
        section["end_seconds"] = round(boundaries[index+1] / FPS, 3)
        scene_plan["scenes"][index]["start_seconds"] = section["start_seconds"]
        scene_plan["scenes"][index]["end_seconds"] = section["end_seconds"]
    script["total_duration_seconds"] = round(total / FPS, 3)
    script_sections = {s["id"]: s for s in script["sections"]}
    props["review_timeline"] = [
        {"id": scene["id"], "label": scene["id"].replace("lesson_l", "逐词 · "),
         "thai": next((x["letter"] for x in lessons if scene["id"] == "lesson_" + x["id"]), ""),
         "start": scene["start_seconds"], "end": scene["end_seconds"],
         "title": scene["description"], "sub": "", "text": script_sections[scene["id"]]["text"], "credit": ""}
        for scene in scene_plan["scenes"]]
    save(art / "script.json", script)
    save(art / "scene_plan.json", scene_plan)
    save(art / "props.json", props)
    save(project / "composition/props.json", props)
    print(f"{project.name}: {len(lessons)} letters, {total/FPS:.1f}s")
    return total / FPS


def main() -> None:
    ids = sys.argv[1:] or [f"thai-alphabet-pinkfong-{i:02d}-lesson" for i in range(2, 16)]
    for project_id in ids:
        build(PROJECTS / project_id)


if __name__ == "__main__":
    main()
