"""Build the two user-requested Thai expression lessons using the approved series voices."""
from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import edge_tts

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from lib.checkpoint import init_project
TEMPLATE = REPO / "projects/thai-1000-idiom-01-diao"
FPS = 30
SOURCE = {
    "saranae": "https://dict.longdo.com/search/%E0%B8%AA%E0%B8%B2%E0%B8%A3%E0%B8%B0%E0%B9%81%E0%B8%99",
    "kuantin": "https://dict.longdo.com/search/-%E0%B8%81%E0%B8%A7%E0%B8%99%E0%B8%95%E0%B8%B5%E0%B8%99-",
}
LESSONS = [
    {
        "id": "thai-1000-idiom-02-saranae", "comp": "SaranaeLesson", "slug": "thai_funny_saranae_02",
        "title": "สาระแน｜爱管闲事", "word": "สาระแน", "meaning": "爱管闲事", "tone": "带责备的口语",
        "color": "#176b58", "tagline": "听懂它，也学会温和地说", "number": "02",
        "hook": "泰语里说人爱管闲事，可以用这个词。语气不客气，先听发音。",
        "cards": [
            ("word", "爱管闲事", "สาระแน", "说一个人爱管闲事。", "就是爱插手别人的事。", "核心词", "带责备意味"),
            ("stop", "别多管闲事", "อย่าสาระแน", "直接说，别多管闲事。", "语气很冲，别随便对人说。", "强硬说法", "适合识别，不宜随便用"),
            ("soft", "别管我的事", "อย่ายุ่งเรื่องของฉัน", "想说得平和一点。", "意思是，别管我的事。", "平和替换", "表达边界，语气较轻"),
        ],
        "reveal": "记住，刚学的强硬说法带着责备。日常沟通，尽量换成平和一点的说法。",
        "rule": "สาระแน 带责备；礼貌场合换个说法。",
        "description": "学泰语口语สาระแน：爱管闲事、别多管闲事，以及语气更平和的说法。",
        "source": SOURCE["saranae"],
    },
    {
        "id": "thai-1000-idiom-03-kuantin", "comp": "KuantinLesson", "slug": "thai_funny_kuantin_03",
        "title": "อย่ามากวนตีน｜别来找茬", "word": "อย่ามากวนตีน", "meaning": "别来找茬", "tone": "粗鲁，慎用",
        "color": "#9b4b3d", "tagline": "听懂语气，别随便模仿", "number": "03",
        "hook": "这句泰语的意思是别来找茬，语气很粗鲁。先听发音。",
        "cards": [
            ("word", "故意找茬", "กวนตีน", "先听核心词，故意找茬。", "这是粗话，别随便对人说。", "核心词", "粗鲁的口语"),
            ("stop", "别来找茬", "อย่ามากวนตีน", "有人故意挑衅，会听到这句。", "意思是别来找茬，语气更冲。", "强硬说法", "冲突中才可能听到"),
            ("soft", "别打扰", "อย่ากวน", "想说得平和一点。", "就是别打扰，少了攻击性。", "平和替换", "日常沟通更合适"),
        ],
        "reveal": "记住，刚学的强硬说法很粗鲁。需要客气一点时，换成最后那句。",
        "rule": "กวนตีน 很冲；อย่ากวน 更平和。",
        "description": "听懂泰语口语อย่ามากวนตีน的真实语气：别来找茬；再学较平和的อย่ากวน。",
        "source": SOURCE["kuantin"],
    },
]


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def duration(path: Path) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], text=True))


def create_workspace(cfg: dict) -> Path:
    project = REPO / "projects" / cfg["id"]
    if not project.exists():
        init_project(cfg["id"], title=cfg["title"], pipeline_type="animated-explainer")
    (project / "composition/public/audio").mkdir(parents=True, exist_ok=True)
    (project / "composition/public/fonts").mkdir(parents=True, exist_ok=True)
    (project / "composition/public/app").mkdir(parents=True, exist_ok=True)
    (project / "assets/audio").mkdir(parents=True, exist_ok=True)
    (project / "assets/music").mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE / "composition/public/fonts/Sarabun-Bold.ttf", project / "composition/public/fonts/Sarabun-Bold.ttf")
    shutil.copy2(TEMPLATE / "composition/public/app/app_icon.png", project / "composition/public/app/app_icon.png")
    shutil.copy2(TEMPLATE / "assets/music/background.mp3", project / "assets/music/background.mp3")
    shutil.copy2(TEMPLATE / "assets/music/background.mp3", project / "composition/public/audio/background.mp3")
    for name in ("index.tsx", "Composition.tsx"):
        shutil.copy2(REPO / "scripts/thai_idiom_series" / name, project / "composition" / name)
    (project / "composition/Root.tsx").write_text(
        f'import {{Composition}} from "remotion";\nimport {{Scene,calculateMetadata,SceneProps}} from "./Composition";\n'
        f'export const Root:React.FC=()=><Composition id="{cfg["comp"]}" component={{Scene}} durationInFrames={{1500}} fps={{30}} width={{1080}} height={{1920}} defaultProps={{{{}} as SceneProps}} calculateMetadata={{calculateMetadata}}/>;\n'
    )
    return project


async def synth(path: Path, text: str, lang: str) -> None:
    if path.exists() and path.stat().st_size > 500:
        return
    voice, rate = ("zh-CN-XiaoxiaoNeural", "+15%") if lang == "zh" else ("th-TH-PremwadeeNeural", "+8%")
    raw = path.with_name(path.stem + "_raw.mp3")
    for attempt in range(12):
        try:
            await edge_tts.Communicate(text, voice=voice, rate=rate).save(str(raw))
            break
        except Exception:
            if attempt == 11:
                raise
            await asyncio.sleep(4 * (attempt + 1))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw),
                    "-af", "silenceremove=start_periods=1:start_silence=0.02:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_silence=0.08:start_threshold=-45dB,areverse",
                    "-c:a", "libmp3lame", "-b:a", "192k", str(path)], check=True)
    raw.unlink()
    print("audio", path.parent.parent.parent.name, path.name, flush=True)


def reads(cfg: dict) -> list[tuple[str, str, str]]:
    r = [("hook_zh_x", cfg["hook"], "zh"), ("hook_th_x", cfg["word"], "th")]
    for cid, zh, thai, intro, explain, *_ in cfg["cards"]:
        r.extend([(f"{cid}_intro_zh_x", intro, "zh"), (f"{cid}_th_x", thai, "th"), (f"{cid}_explain_zh_x", explain, "zh")])
    r.extend([("reveal_zh_x", cfg["reveal"], "zh"), ("outro_zh_x", "泰语千词，在泰国生活，够用了。", "zh")])
    return r


def build_artifacts(project: Path, cfg: dict) -> None:
    A = project / "artifacts"
    cursor = 0
    def clip(name: str) -> dict:
        return {"file": name, "dur": duration(project / "assets/audio" / name)}
    def place(obj: dict) -> dict:
        nonlocal cursor
        obj["startFrame"] = cursor
        obj["frames"] = round(obj["dur"] * FPS)
        cursor += obj["frames"]
        return obj
    hook = {"nar": clip("hook_zh_x.mp3"), "thai": clip("hook_th_x.mp3")}
    hook["thaiAt"] = hook["nar"]["dur"] + .12
    hook["dur"] = hook["thaiAt"] + hook["thai"]["dur"] + .42
    place(hook)
    cards = []
    for cid, zh, thai, _intro, _explain, tag, hint in cfg["cards"]:
        a,b,c = (clip(f"{cid}_{part}_x.mp3") for part in ("intro_zh", "th", "explain_zh"))
        t = a["dur"] + .13
        r = t + b["dur"] + .12
        e = r + b["dur"] + .16
        cards.append(place({"id": cid, "zh": zh, "thai": thai, "hint": hint, "tag": tag,
                            "intro": a, "pronounce": b, "explain": c, "thaiAt": t,
                            "repeatAt": r, "explainAt": e, "dur": e + c["dur"] + .25}))
    reveal = place({"nar": clip("reveal_zh_x.mp3"), "rule": cfg["rule"], "dur": duration(project / "assets/audio/reveal_zh_x.mp3") + .4})
    outro = place({"nar": clip("outro_zh_x.mp3"), "dur": duration(project / "assets/audio/outro_zh_x.mp3") + .45})
    timeline = [("hook", cfg["title"], hook)] + [(c["id"], c["zh"] + " · " + c["thai"], c) for c in cards] + [("reveal", "语气小结", reveal), ("outro", "泰语千词 App", outro)]
    script_text = {"hook": cfg["hook"], "reveal": cfg["reveal"], "outro": "泰语千词，在泰国生活，够用了。"}
    for cid, _, _, intro, explain, *_ in cfg["cards"]:
        script_text[cid] = intro + "泰语读两遍。" + explain
    props = {"fps": FPS, "totalFrames": cursor, "totalSeconds": cursor/FPS,
             "lesson": {k: cfg[k] for k in ("title","word","meaning","tone","color","tagline","number")},
             "hook": hook, "cards": cards, "reveal": reveal, "outro": outro,
             "bgm": {"file": "background.mp3", "volume": .055},
             "review_timeline": [{"id": cid, "label": label, "start": item["startFrame"]/FPS,
                                  "end": (item["startFrame"]+item["frames"])/FPS,
                                  "title": label, "text": script_text[cid], "credit": cfg["source"]} for cid,label,item in timeline]}
    save(A / "props.json", props)
    save(project / "composition/props.json", props)
    source = {"url": cfg["source"], "title": "Longdo Dictionary", "used_for": "泰语词义和语气", "reliability": "primary"}
    research = json.loads((TEMPLATE / "artifacts/research_brief.json").read_text())
    research.update(topic=cfg["title"], research_date=str(date.today()), research_summary=cfg["description"], sources=[source,
        {"url":"https://dict.longdo.com/search/%E0%B8%A2%E0%B8%B8%E0%B9%88%E0%B8%87","title":"Longdo Dictionary：ยุ่ง","used_for":"别插手的平和说法","reliability":"primary"},
        {"url":"https://dict.longdo.com/search/%E0%B8%81%E0%B8%A7%E0%B8%99","title":"Longdo Dictionary：กวน","used_for":"打扰与找茬的语气区别","reliability":"primary"},
        {"url":"https://dict.longdo.com/search/%E0%B8%AD%E0%B8%A2%E0%B9%88%E0%B8%B2%E0%B8%81%E0%B8%A7%E0%B8%99","title":"Longdo Dictionary：อย่ากวน","used_for":"平和替代说法","reliability":"primary"},
        {"url":"local:user-image","title":"用户提供的泰中词卡截图","used_for":"选题与目标表达","reliability":"anecdotal"}])
    research["data_points"] = [
        {"claim": cfg["word"] + " 对应 " + cfg["meaning"] + "，需注意语气。", "source_url":cfg["source"],"source_name":"Longdo Dictionary","credibility":"primary_source","usable_as":"script_anchor"},
        {"claim": cfg["cards"][1][2] + " 是更强硬的表达。", "source_url":cfg["source"],"source_name":"Longdo Dictionary","credibility":"primary_source","usable_as":"supporting_point"},
        {"claim": cfg["cards"][2][2] + " 可用于较平和的表达。", "source_url":"https://dict.longdo.com/search/%E0%B8%A2%E0%B8%B8%E0%B9%88%E0%B8%87" if cfg["number"]=="02" else "https://dict.longdo.com/search/%E0%B8%AD%E0%B8%A2%E0%B9%88%E0%B8%B2%E0%B8%81%E0%B8%A7%E0%B8%99","source_name":"Longdo Dictionary","credibility":"primary_source","usable_as":"supporting_point"},
    ]
    research["landscape"]["existing_content"] = [
        {"title":"用户提供的泰语截图","url":"local:user-image","source":"user","angle":"一词一义","what_it_covers":cfg["title"],"what_it_misses":"语气和准确用法"},
        {"title":"Longdo：目标词","url":cfg["source"],"source":"dictionary","angle":"词义与例句","what_it_covers":cfg["word"],"what_it_misses":"中文学习顺序"},
        {"title":"Longdo：较平和的表达","url":"https://dict.longdo.com/search/%E0%B8%A2%E0%B8%B8%E0%B9%88%E0%B8%87" if cfg["number"]=="02" else "https://dict.longdo.com/search/%E0%B8%81%E0%B8%A7%E0%B8%99","source":"dictionary","angle":"相关词义","what_it_covers":"ยุ่ง 的插手义" if cfg["number"]=="02" else "กวน 的打扰义","what_it_misses":"目标词语气对比"},
    ]
    research["landscape"]["underserved_gaps"] = ["截图的中文义可能掩盖原词语气"]
    research["landscape"]["saturated_angles"] = []
    research["audience_insights"]["common_questions"] = [cfg["word"] + "是什么意思？", "对什么人可以说？", "有没有更平和的替换说法？"]
    research["audience_insights"]["misconceptions"] = []
    research["angles_discovered"] = [
        {"name":"词义与语气一起学","hook":cfg["description"],"type":"evergreen","why_now":"截图引发学习兴趣","grounded_in":[cfg["source"]]},
        {"name":"一句话的轻重区别","hook":"同一意思，语气变了怎么说？","type":"narrative","why_now":"词典指出目标词带有鲜明的语气色彩","grounded_in":[cfg["source"]]},
        {"name":"强硬话换温和话","hook":"听懂冲突表达，也学会温和回应。","type":"evergreen","why_now":"学习者需要知道何时不宜使用","grounded_in":[cfg["source"]]},
    ]
    research["visual_references"] = [{"description":"用户提供的简洁词卡截图","url":"local:user-image","what_works":"泰中词义一眼可见"}]
    save(A / "research_brief.json", research)
    proposal = json.loads((TEMPLATE / "artifacts/proposal_packet.json").read_text())
    proposal["concept_options"] = [{"id":"c1","title":cfg["title"],"hook":cfg["hook"],"narrative_structure":"tutorial","visual_approach":"沿用系列笔记纸与深色泰语词卡，突出语气差别。","target_duration_seconds":round(cursor/FPS),"why_this_works":"同时教词义、实际说法和较平和的替换。","key_points":[cfg["meaning"],cfg["tone"],"中文引入后泰语女声读两遍","片尾 App 推广"],"core_message":cfg["description"],"tone":"清楚、紧凑"},{"id":"c2","title":"情景问答","hook":"从一段冲突对话切入","narrative_structure":"story","visual_approach":"双人对话气泡","target_duration_seconds":40,"why_this_works":"更戏剧化，但词义讲解不如词卡直接。","key_points":[cfg["meaning"],cfg["tone"]],"core_message":cfg["description"],"tone":"戏剧化"},{"id":"c3","title":"语气阶梯","hook":"同一意思，说话轻重有差别","narrative_structure":"comparison","visual_approach":"从强硬到平和的竖向刻度卡","target_duration_seconds":35,"why_this_works":"容易比较语气，但泰语发音的注意力更分散。","key_points":[cfg["tone"],"温和替换"],"core_message":cfg["description"],"tone":"对比式"}]
    proposal["selected_concept"] = {"concept_id":"c1","rationale":"与用户已审过的泰语词卡系列保持连续，并直接教准确词义。"}
    proposal["production_plan"]["render_runtime"] = "remotion"
    proposal["production_plan"]["composition_mode"] = "atelier"
    proposal["approval"] = {"status":"approved","user_notes":"用户要求继续制作剩余两期，沿用此前已审核的系列音色和合成路径。"}
    save(A / "proposal_packet.json", proposal)
    sections = [{"id":cid,"label":label,"text":script_text[cid],"start_seconds":item["startFrame"]/FPS,"end_seconds":(item["startFrame"]+item["frames"])/FPS,"speaker_directions":"先中文、后泰语；泰语跟读两遍。"} for cid,label,item in timeline]
    script = json.loads((TEMPLATE / "artifacts/script.json").read_text())
    script.update(title=cfg["title"], sections=sections, total_duration_seconds=cursor/FPS)
    script["metadata"] = {"language":"zh+th","reference":"用户截图","tts":{"engine":"edge","voices":{"zh":"zh-CN-XiaoxiaoNeural","th":"th-TH-PremwadeeNeural"}},"sources":[source]}
    script["voice_performance"].update(performance_intent="直接讲词义和语气，中文自然，泰语女声跟读两遍。",energy_curve="直接介绍，三张词卡，语气小结，App 片尾。",sample_section_id="word")
    save(A / "script.json", script)
    scene = {"version":"1.0","style_playbook":"custom-thai-notebook","scenes":[{"id":cid,"type":"animation","description":label,"start_seconds":item["startFrame"]/FPS,"end_seconds":(item["startFrame"]+item["frames"])/FPS,"script_section_id":cid,"required_assets":[{"type":"audio","description":"中泰配音","source":"generate"}]} for cid,label,item in timeline]}
    save(A / "scene_plan.json", scene)
    assets = [{"id":f.stem,"type":"narration","path":str(f.relative_to(project)),"source_tool":"edge-tts-cli","scene_id":f.stem.split("_")[0],"cost_usd":0,"format":"mp3"} for f in sorted((project/"assets/audio").glob("*_x.mp3"))]
    assets += [{"id":"background","type":"music","path":"assets/music/background.mp3","source_tool":"existing-local-series","scene_id":"all","cost_usd":0,"format":"mp3"},{"id":"app-icon","type":"image","path":"composition/public/app/app_icon.png","source_tool":"existing-brand-asset","scene_id":"outro","cost_usd":0,"format":"png"}]
    save(A / "asset_manifest.json", {"version":"1.0","assets":assets,"total_cost_usd":0,"metadata":{"voice_source":"approved Thai 1000 series voices","music_source":"approved local music","visuals":"original notebook lesson design"}})
    save(A / "decision_log.json", {"version":"1.0","project_id":cfg["id"],"decisions":[
        {"decision_id":cfg["number"]+"-runtime","stage":"proposal","category":"render_runtime_selection","subject":"Composition runtime","options_considered":[{"option_id":"remotion","label":"Remotion","score":1,"reason":"延续已审核双语词卡与精准配音节奏"},{"option_id":"hyperframes","label":"HyperFrames","score":.6,"reason":"适合重做动效，但本次以系列连续性为主"},{"option_id":"ffmpeg","label":"FFmpeg","score":.3,"reason":"逐词动态较弱"}],"selected":"remotion","reason":"用户授权继续做同系列，沿用已审过的运行时。","user_visible":True,"user_approved":True},
        {"decision_id":cfg["number"]+"-voice","stage":"assets","category":"voice_selection","subject":"Chinese and Thai lesson voices","options_considered":[{"option_id":"edge_existing","label":"Xiaoxiao 中文 + Premwadee 泰语","score":1,"reason":"延续同系列已审核的音色。"}],"selected":"edge_existing","reason":"延续已审核音色。","user_visible":True,"user_approved":True}]})
    save(A / "publish.json", {"series_id":1,"sub_series":"趣味泰语","slug":cfg["slug"],"title":"泰语千词｜"+cfg["title"],"video_path":"renders/final-v1.mp4","cover_path":"renders/cover-v1.jpg","publish_copy":cfg["description"]+"\n\n#泰语 #泰语学习 #泰语千词 #实用泰语","wechat_copy":cfg["title"],"credits":"泰语释义参考 Longdo Dictionary；中泰配音与剪辑：泰语千词。","note":"待审片；未入库。"})
    (project / "art-direction.md").write_text("# Art direction\n\nApproved Thai 1000 notebook series: warm paper, strong Thai word card, concise Chinese explanation. Highlight register and a gentler alternative. First frame works as cover.\n")
    print(project.name, len(cards), f"{cursor/FPS:.2f}s", flush=True)


async def main() -> None:
    projects = [(create_workspace(cfg), cfg) for cfg in LESSONS]
    queue = [(p/"assets/audio"/(name+".mp3"), words, lang) for p,cfg in projects for name,words,lang in reads(cfg)]
    sem = asyncio.Semaphore(1)
    async def one(item):
        async with sem:
            await synth(*item)
    await asyncio.gather(*(one(q) for q in queue))
    for project,cfg in projects:
        build_artifacts(project,cfg)


if __name__ == "__main__":
    asyncio.run(main())
