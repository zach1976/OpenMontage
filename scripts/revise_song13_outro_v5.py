"""Persist the requested Song 13 logo and slogan outro revision."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import write_checkpoint

PROJECT_ID = "thai-1000-song-13-nalika-sai"
PROJECT = ROOT / "projects" / PROJECT_ID
ART = PROJECT / "artifacts"
REVISION = "v5-logo-slogan"
SLOGAN = "泰语千词，在泰国生活够用了。"


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def checkpoint(stage: str, artifact: dict) -> None:
    key = {"script": "script", "scene_plan": "scene_plan", "assets": "asset_manifest",
           "edit": "edit_decisions"}[stage]
    write_checkpoint(ROOT / "projects", PROJECT_ID, stage, "in_progress", {},
                     pipeline_type="animated-explainer", metadata={"revision": REVISION})
    write_checkpoint(
        ROOT / "projects", PROJECT_ID, stage, "completed", {key: artifact},
        pipeline_type="animated-explainer", human_approved=stage in {"script", "scene_plan", "assets"},
        review={"decision": "pass", "critical": 0, "suggestions": 0,
                "checks": ["Official Thai 1000 app icon used", "Exact brand slogan on screen",
                           "Existing Xiaoxiao recording of slogan fits outro"]},
        cost_snapshot={"spent_usd": 0, "estimated_remaining_usd": 0},
        metadata={"revision": REVISION, "approval_source": "User required logo and Thai 1000 slogan in outro"},
    )


def main() -> None:
    props_path = PROJECT / "composition/props.json"
    props = read(props_path)
    assert props["totalFrames"] == 2747
    outro = next(b for b in props["blocks"] if b["id"] == "outro")
    assert outro["frames"] == 108
    row = next(x for x in props["review_timeline"] if x["id"] == "outro")
    row["text"] = row["sub"] = SLOGAN
    row["credit"] = "泰语千词官方 App 图标 · Microsoft Edge 小晓女声"
    save(props_path, props)

    script = read(ART / "script.json")
    section = next(x for x in script["sections"] if x["id"] == "outro")
    section["text"] = SLOGAN
    section["speaker_directions"] = "沿用已认可的小晓女声品牌口播；清楚收在‘够用了’。"
    section["delivery_cues"]["provider_text"] = SLOGAN
    section["enhancement_cues"] = [{"type": "overlay",
                                     "description": "泰语千词官方 App 图标、品牌名和‘在泰国生活够用了’完整呈现。",
                                     "timestamp_seconds": section["start_seconds"]}]
    script.setdefault("metadata", {})["outro_revision"] = REVISION
    save(ART / "script.json", script)
    checkpoint("script", script)

    scene_plan = read(ART / "scene_plan.json")
    scene = next(x for x in scene_plan["scenes"] if x["id"] == "outro")
    scene["description"] = "泰语千词官方 App 图标居中，品牌名与‘在泰国生活够用了’清楚呈现。"
    scene["framing"] = "1080×1920 竖屏；图标置于画面中上方，品牌名和 slogan 居中排列。"
    scene["movement"] = "图标与品牌字在前 0.4 秒轻微显现，之后稳定供阅读。"
    scene["overlay_notes"] = "Logo 使用原始 App 图标，不改图形与颜色；标语使用可编辑文字。"
    scene["narrative_role"] = "call_to_action"
    scene["required_assets"] = [
        {"type": "image", "description": "泰语千词官方 App 图标", "source": "provided"},
        {"type": "narration", "description": "小晓女声品牌口播：泰语千词，在泰国生活，够用了。", "source": "provided"},
    ]
    scene_plan.setdefault("metadata", {})["outro_revision"] = REVISION
    save(ART / "scene_plan.json", scene_plan)
    checkpoint("scene_plan", scene_plan)

    manifest = read(ART / "asset_manifest.json")
    voice = next(x for x in manifest["assets"] if x["id"] == "outro-zh")
    voice["path"] = "assets/audio/outro_zh_v5.mp3"
    voice["duration_seconds"] = 2.783583
    voice["voice_performance"]["provider_text_used"] = True
    voice["voice_performance"]["review_notes"] = "Same Xiaoxiao voice and exact brand line reused from approved Song 11 recording after Edge returned 403."
    voice.pop("reused_from_project", None)
    manifest["assets"] = [x for x in manifest["assets"] if x["id"] != "thai-1000-app-icon-outro"]
    manifest["assets"].append({
        "id": "thai-1000-app-icon-outro", "type": "image",
        "path": "assets/images/app/app_icon.png", "source_tool": "local_asset_copy",
        "scene_id": "outro", "cost_usd": 0,
        "generation_summary": "Official Thai 1000 app icon reused from project thai-1000-song-11-mai-mi-khrai-ru-tua-rao",
    })
    manifest.setdefault("metadata", {})["outro_revision"] = REVISION
    save(ART / "asset_manifest.json", manifest)
    checkpoint("assets", manifest)

    edit = read(ART / "edit_decisions.json")
    cut = next(x for x in edit["cuts"] if x["id"] == "outro")
    cut["reason"] = "Logo, brand name and exact slogan finish the lesson in one clear card."
    edit.setdefault("metadata", {})["outro_revision"] = REVISION
    save(ART / "edit_decisions.json", edit)
    checkpoint("edit", edit)

    log = read(ART / "decision_log.json")
    assert not any(d["decision_id"] == "d-014" for d in log["decisions"])
    log["decisions"].append({
        "decision_id": "d-014", "stage": "edit", "category": "brand_outro",
        "subject": "第13首片尾品牌呈现",
        "options_considered": [
            {"option_id": "logo_slogan", "label": "官方图标与完整标语", "score": 1,
             "reason": "用户明确要求 Logo 与‘在泰国生活够用了’"},
            {"option_id": "text_only", "label": "文字推广", "score": 0,
             "reason": "V4 做法", "rejected_because": "缺少用户要求的 Logo 和品牌标语"},
        ],
        "selected": "logo_slogan", "reason": "用户要求片尾同时显示 Logo、品牌名和完整标语。",
        "user_visible": True, "user_approved": True, "confidence": 1,
    })
    save(ART / "decision_log.json", log)
    print("V5 outro artifacts and checkpoints updated")


if __name__ == "__main__":
    main()
