#!/usr/bin/env python3
"""Collect technical measurements and visual contact sheets for rendered lessons."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"


def command(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(list(map(str, args)), capture_output=True, text=True, check=True)


def one(project: Path, video_name: str = "final.mp4") -> tuple[dict, list[Path]]:
    video = project / "renders" / video_name
    suffix = "_v2" if Path(video_name).stem == "final_v2" else ""
    props = json.loads((project / "artifacts/props.json").read_text())
    probe = json.loads(command("ffprobe", "-v", "error", "-show_entries",
                               "format=duration,size:stream=codec_name,width,height,r_frame_rate",
                               "-of", "json", video).stdout)
    duration = float(probe["format"]["duration"])
    streams = probe["streams"]
    visual = next(s for s in streams if s["codec_name"] == "h264")
    has_audio = any(s["codec_name"] == "aac" for s in streams)
    intro_end = props["introFrames"] / 30
    song_end = intro_end + props["songFrames"] / 30
    bridge_end = song_end + props["bridgeFrames"] / 30
    lesson_times = [bridge_end + (x["start"] + x["frames"] / 2) / 30 for x in props["lessons"]]
    song_times = [intro_end + (x["songStartFrame"] + x["songEndFrame"]) / 60 for x in props["lessons"]]
    samples = [("cover", 0.1)] + [(f"song_{i+1}", t) for i, t in enumerate(song_times)] + [
        (f"lesson_{i+1}", t) for i, t in enumerate(lesson_times)] + [("outro", duration - props["outroFrames"] / 60)]
    snapshots = project / "snapshots"
    snapshots.mkdir(exist_ok=True)
    frames = []
    for name, second in samples:
        frame = snapshots / f"qa{suffix}_{name}.jpg"
        command("ffmpeg", "-y", "-loglevel", "error", "-ss", f"{second:.3f}", "-i", video,
                "-frames:v", "1", "-q:v", "2", frame)
        frames.append(frame)
    volume = command("ffmpeg", "-hide_banner", "-nostats", "-i", video,
                     "-vn", "-af", "volumedetect", "-f", "null", "-")
    peak_match = re.search(r"max_volume:\s*([\-\d.]+) dB", volume.stderr)
    peak = float(peak_match.group(1)) if peak_match else None
    metrics = {"duration_seconds": round(duration, 3), "resolution": f"{visual['width']}x{visual['height']}",
               "fps": visual["r_frame_rate"], "has_audio": has_audio, "audio_peak_dbfs": peak,
               "size_bytes": int(probe["format"]["size"]),
               "sample_frames": [str(f.relative_to(project)) for f in frames]}
    (project / f"artifacts/qa_metrics{suffix}.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
    return metrics, frames


def contact_sheet(files: list[tuple[str, list[Path]]], output: Path) -> None:
    cell_w, cell_h, label_h = 150, 267, 30
    cols = max(len(paths) for _, paths in files)
    sheet = Image.new("RGB", (cols * cell_w, len(files) * (cell_h + label_h)), "#0B1526")
    draw = ImageDraw.Draw(sheet)
    for row, (name, frames) in enumerate(files):
        y = row * (cell_h + label_h)
        draw.text((8, y + 5), name, fill="white")
        for col, frame in enumerate(frames):
            image = Image.open(frame).convert("RGB").resize((cell_w, cell_h))
            sheet.paste(image, (col * cell_w, y + label_h))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=88)


def main() -> None:
    series = PROJECTS / "thai-alphabet-pinkfong-lesson-batch"
    video_name = sys.argv[1] if len(sys.argv) > 1 else "final.mp4"
    suffix = "_v2" if Path(video_name).stem == "final_v2" else ""
    sheets: list[tuple[str, list[Path]]] = []
    for episode in range(2, 16):
        project = PROJECTS / f"thai-alphabet-pinkfong-{episode:02d}-lesson"
        metrics, frames = one(project, video_name)
        sheets.append((f"第 {episode:02d} 集  {metrics['duration_seconds']:.1f}s", frames))
        print(f"{project.name}: {metrics['duration_seconds']:.1f}s, peak {metrics['audio_peak_dbfs']} dBFS")
    contact_sheet(sheets[:7], series / f"artifacts/qa_contact_02_08{suffix}.jpg")
    contact_sheet(sheets[7:], series / f"artifacts/qa_contact_09_15{suffix}.jpg")


if __name__ == "__main__":
    main()
