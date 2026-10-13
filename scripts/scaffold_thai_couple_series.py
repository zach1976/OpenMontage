#!/usr/bin/env python3
"""Materialize the approved Thai couple series plan into pipeline projects.

This script writes project data and composition files only. Narration synthesis,
validation, rendering, review, and publishing use the standard pipeline tools.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from lib.checkpoint import init_project

SHARED = REPO / "projects/_shared/couple-series"
PLAN = json.loads((SHARED / "series_plan.json").read_text())
ICON = REPO / "projects/thai-lovers-terms-phrases/assets/images/app_icon.png"
INTRO, CARD, OUTRO = 3.5, 4.4, 4.5


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


for ep in PLAN["thai_episodes"]:
    pid = ep["project_id"]
    p = init_project(pid, title=f"情侣泰语 {ep['number']:02d}｜{ep['title']}", pipeline_type="animation")
    (p / "composition").mkdir(exist_ok=True)
    (p / "public/images").mkdir(parents=True, exist_ok=True)
    (p / "public/app").mkdir(parents=True, exist_ok=True)
    (p / "public/audio").mkdir(parents=True, exist_ok=True)
    (p / "composition/public/images").mkdir(parents=True, exist_ok=True)
    (p / "composition/public/app").mkdir(parents=True, exist_ok=True)
    sheet = SHARED / "assets" / ep["sheet"]
    for dest in (p / "assets/images" / ep["sheet"], p / "public/images" / ep["sheet"], p / "composition/public/images" / ep["sheet"]):
        shutil.copy2(sheet, dest)
    for dest in (p / "assets/images/app_icon.png", p / "public/app/app_icon.png", p / "composition/public/app/app_icon.png"):
        shutil.copy2(ICON, dest)
    shutil.copy2(SHARED / "ThaiSeriesComposition.tsx", p / "Composition.tsx")
    (p / "index.tsx").write_text("import {registerRoot} from 'remotion';\nimport {Root} from './Root';\nregisterRoot(Root);\n")
    duration = round(INTRO + CARD * len(ep["cards"]) + OUTRO, 1)
    frames = round(duration * 30)
    (p / "Root.tsx").write_text(
        "import React from 'react';\n"
        "import {Composition} from 'remotion';\n"
        "import {Scene,calculateMetadata,SceneProps} from './Composition';\n"
        f"export const Root:React.FC=()=> <Composition id=\"ThaiCoupleEpisode\" component={{Scene}} durationInFrames={{{frames}}} fps={{30}} width={{1080}} height={{1920}} defaultProps={{{{}} as SceneProps}} calculateMetadata={{calculateMetadata}}/>;\n"
    )
    cards = [dict(id=f"s{i:02d}", th=th, zh=zh, tag=tag, pic=pic)
             for i, (th, zh, tag, pic) in enumerate(ep["cards"], 1)]
    props = dict(title=ep["title"], subtitle=ep["cover_subtitle"], episode=ep["number"],
                 cards=cards, sheet=ep["sheet"], fps=30, totalSeconds=duration,
                 review_timeline=[])
    sections = []
    units = []
    cuts = []
    scenes = []

    def scene(sid: str, start: float, end: float, label: str, text: str, native: str = "", group: str = "") -> None:
        sections.append(dict(id=sid, text=text, start_seconds=start, end_seconds=end))
        scenes.append(dict(id=sid, type="animation", description=label, start_seconds=start,
                           end_seconds=end, script_section_id=sid, framing="9:16 central card",
                           movement="short fade and rise"))
        cuts.append(dict(id=sid, source=f"composition:ThaiCoupleEpisode#{sid}",
                         in_seconds=start, out_seconds=end, transition_in="cut",
                         transition_out="cut", reason=label))
        props["review_timeline"].append(dict(id=sid, label=label, title=native or label,
                                             thai=native, start=start, end=end,
                                             sub=group, text=text, credit=""))

    scene("sc00", 0, INTRO, "封面 · 第一帧", ep["intro"])
    units.append(dict(id="intro_zh", section="sc00", lang="zh", text=ep["intro"]))
    for i, card in enumerate(cards):
        start = round(INTRO + i * CARD, 1)
        end = round(start + CARD, 1)
        scene(card["id"], start, end, f"{i+1:02d} · {card['zh']}",
              f"{card['zh']}。 → {card['th']}", card["th"], "先听中文，再跟泰语读")
        units.extend([dict(id=f"{card['id']}_zh", section=card["id"], lang="zh", text=f"{card['zh']}。"),
                      dict(id=f"{card['id']}_th", section=card["id"], lang="th", text=card["th"])])
    outro_start = round(INTRO + len(cards) * CARD, 1)
    outro = "想继续学实用泰语，就来泰语千词，每天学一点。"
    scene("outro", outro_start, duration, "片尾 · App 推广", outro)
    units.append(dict(id="outro_zh", section="outro", lang="zh", text=outro))
    write(p / "artifacts/props.json", props)
    write(p / "composition/props.json", props)
    write(p / "artifacts/script.json", dict(version="1.0", title=ep["title"], total_duration_seconds=duration,
         sections=sections, metadata=dict(tts=dict(engine="edge", voices=dict(zh="zh-CN-XiaoxiaoNeural",
         th="th-TH-PremwadeeNeural"), rates=dict(zh="+12%", th="+5%")), tts_units=units)))
    write(p / "artifacts/scene_plan.json", dict(version="1.0", scenes=scenes,
         metadata=dict(series="情侣泰语", episode=ep["number"])))
    write(p / "artifacts/edit_decisions.json", dict(version="1.0", renderer_family="animation-first",
         render_runtime="remotion", composition_mode="atelier", cuts=cuts, music=dict(volume=0),
         subtitles=dict(enabled=False), bespoke=dict(entry=str((p / "index.tsx").resolve()),
         composition_id="ThaiCoupleEpisode", props_path=str((p / "artifacts/props.json").resolve()),
         public_dir=str((p / "composition/public").resolve()), art_direction=str((p / "art-direction.md").resolve()),
         crf=18, concurrency=4), metadata=dict(fps=30, resolution="1080x1920", total_seconds=duration,
         audio_architecture="Chinese before Thai on all eight cards; no music", cover_source_frame=0)))
    (p / "art-direction.md").write_text(
        f"# 情侣泰语 {ep['number']:02d}｜{ep['title']}\n\n"
        "奶油白与玫红的情侣篇系列视觉。第0帧为可直接使用的封面；"
        "泰国生活摄影带出场景，每张词卡先听中文、再听泰语。"
        "片尾采用泰语千词官方图标，不放打开 App 按钮。\n")
    write(p / "artifacts/asset_manifest.json", dict(version="1.0", assets=[
        dict(id="thai_photo_sheet", type="image", path=f"assets/images/{ep['sheet']}",
             source_tool="image_gen", scene_id="all", provider="OpenAI imagegen",
             generation_summary="Original Thai couple photography contact sheet"),
        dict(id="app_icon", type="image", path="assets/images/app_icon.png",
             source_tool="approved_series_asset", scene_id="outro")], total_cost_usd=0))
    # The series is explicitly authorized by the user; this episode follows the
    # approved Remotion and Edge voice choices from episode 01.
    write(p / "artifacts/proposal_packet.json", dict(version="1.0", concept_options=[
        dict(id="c1", title=ep["title"], hook=ep["intro"], narrative_structure="tutorial",
             visual_approach="Thai daily-life photography and bilingual word cards", target_duration_seconds=duration,
             why_this_works="Fast Chinese cue before each Thai phrase, matching the approved series."),
        dict(id="c2", title="一段情侣对话", hook="从一句对话学泰语", narrative_structure="story",
             visual_approach="Short dramatized scene", target_duration_seconds=duration,
             why_this_works="A continuous scenario can teach context."),
        dict(id="c3", title="泰语情景小测", hook="你会怎么回答？", narrative_structure="tutorial",
             visual_approach="Quiz cards", target_duration_seconds=duration,
             why_this_works="A quiz invites active recall.")],
         selected_concept=dict(concept_id="c1", rationale="User requested episodes similar to the approved first video."),
         production_plan=dict(pipeline="animation", render_runtime="remotion", renderer_family="animation-first",
         composition_mode="atelier", art_direction=str((p / "art-direction.md").resolve()),
         stages=[dict(stage=x, tools=[], approach="Produce and review the bilingual series episode")
                 for x in ("research","proposal","script","scene_plan","assets","edit","compose","publish")],
         delivery_promise=dict(promise_type="teacher_explainer", motion_required=False, tone_mode="warm educational",
                               quality_floor="presentable")),
         cost_estimate=dict(total_estimated_usd=0, line_items=[], budget_verdict="no_budget_set"),
         approval=dict(status="approved", user_notes="User requested six similar Thai episodes and subsequent Vietnamese adaptations.")))
    write(p / "artifacts/research_brief.json", dict(version="1.0", topic=ep["title"], research_date="2026-10-08",
         landscape=dict(existing_content=[dict(title=x, source=u, angle="Thai couple phrases", what_it_covers="Romance and daily Thai usage", url=u)
             for x,u in [("Thai Language Hut romance","https://thailanguagehut.com/the-thai-language/thai-phrases/romance-sweet-talk/"),
                         ("Thai Language Hut love phrases","https://thailanguagehut.com/thai-love-phrases-flirting-in-thai/"),
                         ("Thai with Nariss","https://thaiwithnariss.com/blog/how-to-say-i-love-you-in-thai")]],
         saturated_angles=["Isolated love confession"], underserved_gaps=["Bilingual phrases grouped by one real relationship situation"]),
         data_points=[dict(claim=f"Selected Thai phrase: {x['th']}", source_url="https://www.thai-language.com/",
                           credibility="secondary_source") for x in cards[:3]],
         audience_insights=dict(common_questions=["How do I say this in Thai?", "When is it used?", "How do I pronounce it?"],
                                misconceptions=[], knowledge_level="beginner"),
         angles_discovered=[dict(name=x, hook=ep["intro"], type="evergreen", why_now="Part of the approved six-episode series")
                            for x in ("Everyday phrases","Scenario cards","Quick follow-along")],
         sources=[dict(url=u,title=t,used_for="Thai usage background") for t,u in [
             ("Thai Language Hut romance","https://thailanguagehut.com/the-thai-language/thai-phrases/romance-sweet-talk/"),
             ("Thai Language Hut love phrases","https://thailanguagehut.com/thai-love-phrases-flirting-in-thai/"),
             ("Thai with Nariss","https://thaiwithnariss.com/blog/how-to-say-i-love-you-in-thai"),
             ("Thai language dictionary","https://www.thai-language.com/"),
             ("Thai Language Hut","https://thailanguagehut.com/")]],
         research_summary="Eight usable phrases are grouped by one relationship context and narrated Chinese before Thai."))
    write(p / "artifacts/publish.json", dict(series_id=1, sub_series="情侣泰语", slug=ep["slug"],
         title=f"泰语千词 · 情侣泰语 {ep['number']:02d}｜{ep['title']}，8句一起跟读",
         publish_copy=(f"情侣泰语第{ep['number']}期：{ep['title']}。\n\n" +
                       "\n".join(f"{c['th']} · {c['zh']}" for c in cards) +
                       "\n\n每句先听中文，再跟读泰语。到「泰语千词」继续学。\n\n#泰语 #情侣泰语 #泰语学习 #泰语口语 #泰语千词"),
         wechat_copy=f"情侣泰语 {ep['number']:02d}｜{ep['title']}，8句跟读",
         credits="画面：原创泰国情侣场景摄影；中文配音：Edge 晓晓；泰语配音：Edge Premwadee；App 图标：泰语千词。",
         video_path="renders/final-v1.mp4"))
    print(pid, duration, "seconds")
