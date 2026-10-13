"""Build a Thai 1000 lesson for เกี่ยวอะไรกับเธอ."""
from __future__ import annotations

import asyncio
from pathlib import Path

from build_remaining_thai_idioms import create_workspace, synth, reads, build_artifacts

CFG = {
    "id": "thai-1000-idiom-04-kiao-arai-kap-thoe",
    "comp": "KiaoAraiKapThoeLesson",
    "slug": "thai_funny_kiao_arai_kap_thoe_04",
    "title": "เกี่ยวอะไรกับเธอ｜关你什么事",
    "word": "เกี่ยวอะไรกับเธอ",
    "meaning": "关你什么事",
    "tone": "带反问，不客气",
    "color": "#956344",
    "tagline": "听懂反问，也学会平和拒答",
    "number": "04",
    "hook": "泰语里说关你什么事，可以用这句。先听发音。",
    "cards": [
        ("word", "有关", "เกี่ยว", "先听关键字，有关。", "就是和某件事有关系。", "关键字", "说两件事有没有关系"),
        ("stop", "关你什么事", "เกี่ยวอะไรกับเธอ", "合起来问，关你什么事。", "这是反问，语气不客气。", "直接说法", "带反问，容易顶撞人"),
        ("soft", "这事先不说了", "ขอไม่พูดเรื่องนี้นะ", "不想回答，可以说得委婉点。", "意思是，这件事我先不说了。", "平和替换", "婉拒回答，更适合日常"),
    ],
    "reveal": "这句反问容易顶撞人。不想聊自己的事，换成最后那句更合适。",
    "rule": "反问有火气；拒答可以说得柔和些。",
    "description": "学泰语口语เกี่ยวอะไรกับเธอ：关你什么事，并分清反问语气与平和拒答的说法。",
    "source": "https://dict.longdo.com/search/%E0%B9%80%E0%B8%81%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%A7",
}


async def main() -> None:
    project = create_workspace(CFG)
    # The shared source has a fade-in title. Make the actual first video frame
    # cover-ready, as required by the series.
    comp = project / "composition/Composition.tsx"
    source = comp.read_text()
    old = 'fontWeight:900,lineHeight:1.2,opacity:fade(f)'
    assert old in source
    comp.write_text(source.replace(old, 'fontWeight:900,lineHeight:1.2'))
    for name, words, lang in reads(CFG):
        await synth(project / "assets/audio" / f"{name}.mp3", words, lang)
    build_artifacts(project, CFG)


if __name__ == "__main__":
    asyncio.run(main())
