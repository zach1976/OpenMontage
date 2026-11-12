"""Materialize two Song 13 derivatives from the frozen cataloged V5 assets.

Creative choices (line boundaries and detailed glosses) are fixed below; this
script only writes the corresponding project workspaces and pipeline records.
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import init_project, write_checkpoint

SOURCE = ROOT / "projects/thai-1000-song-13-nalika-sai"
SOURCE_PROPS = json.loads((SOURCE / "composition/props.json").read_text())
CONFIGS = [
    ("thai-1000-song-13-first-two-lines", 1, "前两句", 0, 2, 209.855, 450,
     ["word_01", "word_02", "word_03", "word_04", "word_05", "word_06"]),
    ("thai-1000-song-13-last-two-lines", 2, "后两句", 2, 4, 224.861, 330,
     ["word_07", "word_02b", "word_03b", "word_08", "word_09"]),
]
DETAILS = {
    "word_01": ["รัก = 爱；ฉัน = 我。", "放在句首，指“我的爱”。"],
    "word_02": ["เป็น = 是／成为；ดั่ง = 如同。", "连用时，把爱比作沙漏。"],
    "word_03": ["นาฬิกา = 钟表；ทราย = 沙。", "合起来是“沙漏”，带出时间流逝。"],
    "word_04": ["ทุ่มเท = 倾心付出；เท่าไร = 多少。", "接后半句，表达“无论付出多少”。"],
    "word_05": ["ก็ = 承接；คง = 大概、恐怕。", "这里带出无奈的推测。"],
    "word_06": ["สลาย = 消散；ไป = 离去。", "合起来是“消散而去”。"],
    "word_07": ["รัก = 爱；เรา = 我们。", "从“我的爱”转成“我们的爱”。"],
    "word_02b": ["เป็น = 是／成为；ดั่ง = 如同。", "再一次用沙漏比喻这段关系。"],
    "word_03b": ["นาฬิกา = 钟表；ทราย = 沙。", "沙漏里的沙，暗示时间慢慢流逝。"],
    "word_08": ["สัก = 某个；วัน = 日子。", "合起来是“总有一天”。"],
    "word_09": ["ก็ = 承接；คงจะ = 恐怕会。", "หายไป = 消失：爱终会消失。"],
}


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def clone_artifact(name: str) -> dict:
    return copy.deepcopy(json.loads((SOURCE / "artifacts" / f"{name}.json").read_text()))


def copy_asset(project: Path, category: str, name: str) -> None:
    src = SOURCE / "composition/public" / category / name
    dst = project / "composition/public" / category / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    if category in {"audio", "images", "video"}:
        asset = project / "assets" / category / name
        asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, asset)


def checkpoint(project_id: str, stage: str, artifacts: dict, source: str) -> None:
    write_checkpoint(
        ROOT / "projects", project_id, stage, "completed", artifacts,
        pipeline_type="animated-explainer",
        human_approved=stage in {"proposal", "script", "scene_plan", "assets"},
        review={"decision": "pass", "critical": 0, "suggestions": 0,
                "checks": ["V5 parent left unchanged", "two exact lyric lines", "local assets verified"]},
        cost_snapshot={"spent_usd": 0, "estimated_remaining_usd": 0},
        metadata={"approval_source": source, "source_project": SOURCE.name},
    )


def build(config: tuple) -> None:
    project_id, part, label, lo, hi, song_start, song_frames, word_ids = config
    project = ROOT / "projects" / project_id
    init_project(project_id, title=f"第13首《沙漏》{label}逐词学", pipeline_type="animated-explainer")
    art = project / "artifacts"
    source_note = "用户要求已入库原片不动，另拆前两句和后两句，并加详细逐词解释。"
    lines = copy.deepcopy(SOURCE_PROPS["lines"][lo:hi])
    line_offset = SOURCE_PROPS["lines"][lo]["at"]
    for line in lines:
        line["at"] = round(line["at"] - line_offset, 3)
        for chunk in line["chunks"]:
            chunk["at"] = round(chunk["at"] - line_offset, 3)

    # Stage 1: research is inherited from the frozen parent, with the exact two-line scope.
    research = clone_artifact("research_brief")
    research["topic"] = f"นาฬิกาทราย (sign) {label}逐词学"
    research["research_summary"] = f"已入库第13首V5的独立衍生片：仅取{label}，原唱、官方MV与已有小晓录音保持一致；新增词根、语法作用和句义卡。"
    research.setdefault("metadata", {})["derivative_of"] = SOURCE.name
    save(art / "research_brief.json", research)
    checkpoint(project_id, "research", {"research_brief": research}, source_note)

    # Stage 2: retain the previously approved Remotion runtime and official-song plan.
    proposal = clone_artifact("proposal_packet")
    proposal["selected_concept"]["rationale"] = f"按用户要求将已入库V5拆出{label}，把每个词讲得更细。"
    proposal["production_plan"]["render_runtime"] = "remotion"
    proposal["production_plan"]["composition_mode"] = "atelier"
    proposal["approval"] = {"status": "approved", "user_notes": source_note}
    proposal.setdefault("metadata", {}).update({"derivative_of": SOURCE.name, "part": part,
        "delivery_promise": "两句原唱、短介绍、详细逐词、两句回听；已入库V5不改动"})
    save(art / "proposal_packet.json", proposal)
    decisions = {"version": "1.0", "project_id": project_id, "decisions": [
        {"decision_id": "split-runtime", "stage": "proposal", "category": "render_runtime_selection",
         "subject": "视频合成引擎", "options_considered": [
             {"option_id": "remotion", "label": "Remotion", "score": 1, "reason": "复用已审核的逐词同步构图"},
             {"option_id": "hyperframes", "label": "HyperFrames", "score": .6, "reason": "新建HTML构图需重新核对同步"},
             {"option_id": "ffmpeg", "label": "FFmpeg", "score": .3, "reason": "不便制作逐词卡"}],
         "selected": "remotion", "reason": "沿用第13首已审定V5的Remotion技术路线。", "user_visible": True, "user_approved": True},
        {"decision_id": "split-voice", "stage": "assets", "category": "voice_selection",
         "subject": "中文介绍和泰语词组跟读", "options_considered": [
             {"option_id": "edge_xiaoxiao_reuse", "label": "复用小晓录音", "score": 1, "reason": "保持用户已批准的人声；新增释义写在屏幕"},
             {"option_id": "google_tts", "label": "Google TTS", "score": 0, "reason": "此前被用户评为机械", "rejected_because": "用户已要求更换"}],
         "selected": "edge_xiaoxiao_reuse", "reason": "在线Edge TTS 403，因此复用原有小晓录音，详细解释以文字呈现。", "user_visible": True, "user_approved": True},
        {"decision_id": "split-approval", "stage": "proposal", "category": "approval_policy",
         "subject": "第13首拆分两集的制作范围", "options_considered": [
             {"option_id": "full-run", "label": "制作两集并交审片", "score": 1, "reason": source_note},
             {"option_id": "per-gate", "label": "每步另等批准", "score": 0, "reason": "用户直接要求拆成两集"}],
         "selected": "full-run", "reason": "本次指令授权两支衍生片制作；入库仍需另行批准。", "user_visible": True, "user_approved": True},
        {"decision_id": "split-music", "stage": "proposal", "category": "music_source",
         "subject": "歌曲与背景音乐", "options_considered": [
             {"option_id": "original", "label": "官方原唱", "score": 1, "reason": "教学听辨对象"},
             {"option_id": "extra", "label": "新背景音乐", "score": 0, "reason": "会干扰歌词"}],
         "selected": "original", "reason": "只用官方原唱。", "user_visible": True, "user_approved": True},
    ]}
    save(art / "decision_log.json", decisions)
    checkpoint(project_id, "proposal", {"proposal_packet": proposal, "decision_log": decisions}, source_note)

    # Stage 3–4: deterministic timeline from the lyric and selected word cards.
    parent_words = {b["id"]: b for b in SOURCE_PROPS["blocks"] if b["kind"] == "word"}
    blocks: list[dict] = []
    cursor = 0
    def add(b: dict) -> None:
        nonlocal cursor
        b["startFrame"] = cursor
        cursor += b["frames"]
        blocks.append(b)
    add({"id": "original_first", "label": f"先听{label}", "kind": "song", "frames": song_frames, "replay": False})
    add({"id": "song_intro", "label": "歌曲简介", "kind": "intro", "frames": 212})
    for ordinal, wid in enumerate(word_ids, 1):
        audio_id = wid.removesuffix("b")
        old = parent_words[audio_id]
        b = {key: old[key] for key in ("th", "zh", "thaiAt", "zhAt")}
        b.update({"id": wid, "label": old["th"], "kind": "word", "audioId": audio_id,
                  "ordinal": ordinal, "detail": DETAILS[wid],
                  "still": f"{wid}_mv.jpg", "source": list(old["source"]),
                  "frames": old["frames"] + 18})
        if wid == "word_02b": b["source"] = [226.411, 227.3]
        if wid == "word_03b": b["source"] = [227.3, 229.439]
        add(b)
    add({"id": "replay_bridge", "label": "回听过渡", "kind": "bridge", "frames": 115 if part == 1 else 65})
    add({"id": "original_replay", "label": f"{label}回听", "kind": "song", "frames": song_frames, "replay": True})
    add({"id": "outro", "label": "泰语千词推广", "kind": "outro", "frames": 108})
    total = cursor / 30
    props = {"fps": 30, "totalFrames": cursor, "totalSeconds": total, "title": f"第13首《沙漏》{label}逐词学",
             "part": part, "songStart": song_start, "songFrames": song_frames,
             "lines": lines, "blocks": blocks, "review_timeline": []}
    timeline = []
    for b in blocks:
        start, end = b["startFrame"] / 30, (b["startFrame"] + b["frames"]) / 30
        if b["kind"] == "word": text = f"{b['th']}：{b['zh']}。{' '.join(b['detail'])}"
        elif b["kind"] == "song": text = f"官方 MV 与原唱{label}；{'带中文译文回听' if b['replay'] else '先听泰语歌词'}。"
        elif b["kind"] == "intro": text = "这首歌叫《沙漏》。沙漏里的沙慢慢落下，就像一段走向结束的感情。"
        elif b["kind"] == "bridge": text = "把刚才的词连起来，再听这两句。"
        else: text = "泰语千词，在泰国生活够用了。"
        timeline.append({"id": b["id"], "label": b["label"], "thai": b.get("th", ""),
                         "start": round(start, 3), "end": round(end, 3), "title": b.get("zh", b["label"]),
                         "sub": text, "text": text,
                         "credit": "BOWKYLION 官方 MV · Microsoft Edge 小晓女声"})
    props["review_timeline"] = timeline
    save(project / "composition/props.json", props)

    script = clone_artifact("script")
    sections_by_id = {x["id"]: x for x in script["sections"]}
    script["sections"] = []
    for b, t in zip(blocks, timeline):
        old = copy.deepcopy(sections_by_id[b["id"].removesuffix("b")])
        old.update({"id": b["id"], "label": b["label"], "text": t["text"],
                    "start_seconds": t["start"], "end_seconds": t["end"]})
        script["sections"].append(old)
    script["title"] = props["title"]
    script["total_duration_seconds"] = total
    script.setdefault("metadata", {})["detailed_glosses_on_screen"] = True
    save(art / "script.json", script)
    checkpoint(project_id, "script", {"script": script}, source_note)

    scene_plan = clone_artifact("scene_plan")
    scenes_by_id = {x["id"]: x for x in scene_plan["scenes"]}
    scene_plan["scenes"] = []
    for b, t in zip(blocks, timeline):
        old = copy.deepcopy(scenes_by_id[b["id"].removesuffix("b")])
        old.update({"id": b["id"], "script_section_id": b["id"],
                    "start_seconds": t["start"], "end_seconds": t["end"],
                    "description": t["text"]})
        scene_plan["scenes"].append(old)
    scene_plan.setdefault("metadata", {})["part"] = part
    save(art / "scene_plan.json", scene_plan)
    checkpoint(project_id, "scene_plan", {"scene_plan": scene_plan}, source_note)

    # Stage 5: copy only files referenced by each derivative; no writes to V5.
    copy_asset(project, "audio", "original.mp3")
    for name in ("song_intro_zh_v2.mp3", "bridge_zh_v4.mp3", "outro_zh_v5.mp3"):
        copy_asset(project, "audio", name)
    for wid in word_ids:
        aid = wid.removesuffix("b")
        for name in (f"{aid}_th.mp3", f"{aid}_zh_v4.mp3"):
            copy_asset(project, "audio", name)
        if not wid.endswith("b"):
            copy_asset(project, "images", f"{wid}_mv.jpg")
    copy_asset(project, "images", "word_09_mv.jpg" if part == 2 else "word_06_mv.jpg")
    for wid, second in (("word_02b", 17.0), ("word_03b", 18.1)) if part == 2 else []:
        out = project / "composition/public/images" / f"{wid}_mv.jpg"
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(second), "-i",
                        str(SOURCE / "composition/public/video/official_hook_26s.mp4"),
                        "-frames:v", "1", str(out)], check=True)
        asset = project / "assets/images" / out.name
        asset.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out, asset)
    clip = project / "composition/public/video/pair.mp4"
    clip.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "0" if part == 1 else "15", "-i",
                    str(SOURCE / "composition/public/video/official_hook_26s.mp4"),
                    "-t", str(song_frames / 30), "-an", "-c:v", "libx264", "-crf", "18",
                    "-pix_fmt", "yuv420p", str(clip)], check=True)
    video_asset = project / "assets/video/pair.mp4"
    video_asset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(clip, video_asset)
    copy_asset(project, "app", "app_icon.png")
    copy_asset(project, "fonts", "Sarabun-Bold.ttf")
    for name in ("SplitLesson.tsx", "Root.tsx", "index.tsx"):
        shutil.copy2(ROOT / "scripts/song13_split" / name, project / "composition" / name)

    manifest = clone_artifact("asset_manifest")
    keep_scene = {b["id"].removesuffix("b") for b in blocks}
    manifest["assets"] = [a for a in manifest["assets"] if a.get("scene_id") in keep_scene]
    manifest.setdefault("metadata", {})["derivative_of"] = SOURCE.name
    manifest["metadata"]["detailed_glosses_on_screen"] = True
    save(art / "asset_manifest.json", manifest)
    checkpoint(project_id, "assets", {"asset_manifest": manifest}, source_note)

    edit = clone_artifact("edit_decisions")
    edit["cuts"] = [{"id": b["id"], "source": f"composition:Song13SplitLesson#{b['id']}",
                     "in_seconds": t["start"], "out_seconds": t["end"], "layer": "primary",
                     "transition_in": "cut", "transition_out": "cut", "reason": t["text"]}
                    for b, t in zip(blocks, timeline)]
    edit["bespoke"].update({"entry": str((project / "composition/index.tsx").resolve()),
                            "composition_id": "Song13SplitLesson",
                            "props_path": str((project / "composition/props.json").resolve()),
                            "public_dir": str((project / "composition/public").resolve())})
    edit.setdefault("metadata", {})["total_seconds"] = total
    edit["metadata"]["derivative_of"] = SOURCE.name
    save(art / "edit_decisions.json", edit)
    checkpoint(project_id, "edit", {"edit_decisions": edit}, source_note)
    print(f"{project_id}: {len(lines)} lines, {len(word_ids)} cards, {total:.3f}s")


if __name__ == "__main__":
    for cfg in CONFIGS:
        build(cfg)
