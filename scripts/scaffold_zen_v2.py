#!/usr/bin/env python3
"""禅意系列重做版的立项脚手架：从 01 的项目结构生成 02–05。

**文案逐字保留**（钩子、整句、逐字拆解、片尾都从老片里逐字抄回，不改一个字），
重做的只有画面、配乐和分辨率。老片 02–05 的生成脚本已经不存在了，
文案是从 `lang1000/marketing/video/series_zen/thai_zen_0N_*.mp4` 的画面逐帧读回来的。

各集共用的只有"引擎知识"：字体、app icon、TTS 配置、时间轴排法、底片处理。
**装置（那个 `*.tsx`）每集单独写**，不共用 —— 见 CLAUDE.md「同一系列每集必须换视觉语言」。

    python3 scripts/scaffold_zen_v2.py            # 全部
    python3 scripts/scaffold_zen_v2.py zen-02     # 只做某一集
"""
import json, shutil, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = REPO / "projects" / "thai-zen-01-impermanence-v2"

EPISODES = [
    dict(
        no=2, pid="thai-zen-02-letgo-v2", comp="LetGo", slug="thai_zen_02_letgo",
        title="泰语千词 · 禅意 02 放下（重做版）",
        hook="放下，\n就一定要忘记吗？", hook_tts="放下，就一定要忘记吗？",
        thai="การปล่อยวางไม่ใช่การลืมทุกอย่าง",
        thai_lines=["การ ปล่อยวาง ไม่ใช่", "การ ลืม ทุกอย่าง"],
        roman="gaan plòi-waang mâi-châi — gaan lʉʉm túk-yàang",
        zh="放下，并不是忘记一切",
        words=[("ปล่อยวาง", "plòi-waang", "放下"), ("ไม่ใช่", "mâi-châi", "不是"),
               ("ลืม", "lʉʉm", "忘记"), ("ทุกอย่าง", "túk-yàang", "一切 · 每件事")],
        bgm="m_bowl.mp3", bgm_gain=0.085,
        # 底片：暖夜。放下不是清空，所以选有"留下来的东西"的画面
        bg=[("coverr-sunset-in-indonesia-3381.mp4", 0.30),
            ("coverr-desert-island-7521.mp4", 0.55),
            ("coverr-walking-to-the-mountain-top-8360.mp4", 0.50)],
        grade="saturation=0.62:brightness=0.00:contrast=1.06",
        art="暖夜 + 琥珀。装置是「落下不消失」：讲过的词沉到画面下端排成一列留痕 —— "
            "和 01「讲完就退掉不再回来」正好相反，因为这一集说的就是放下≠忘记。",
    ),
    dict(
        no=3, pid="thai-zen-03-calm-v2", comp="Calm", slug="thai_zen_03_calm",
        title="泰语千词 · 禅意 03 平静（重做版）",
        hook="是不是没有烦恼，\n才叫平静？", hook_tts="是不是没有烦恼，才叫平静？",
        thai="ใจสงบไม่ใช่ไม่มีปัญหา",
        thai_lines=["ใจ สงบ ไม่ใช่", "ไม่มี ปัญหา"],
        roman="jai sà-ngòp mâi-châi — mâi-mii pan-hǎa",
        zh="心的平静，不是没有问题",
        words=[("ใจ", "jai", "心"), ("สงบ", "sà-ngòp", "平静"),
               ("ไม่มี", "mâi-mii", "没有"), ("ปัญหา", "pan-hǎa", "问题")],
        bgm="m_ambient.mp3", bgm_gain=0.08,
        bg=[("coverr-sunrise-in-costa-rica-1299.mp4", 0.50),
            ("coverr-desert-island-7521.mp4", 0.32),
            ("coverr-road-in-the-mountains-7132.mp4", 0.45)],
        grade="saturation=0.50:brightness=-0.01:contrast=1.04",
        art="青蓝 + 月白。装置是「水面倒影」：词立在水线上，倒影在水线下轻轻晃；"
            "讲到「问题」时倒影起一次涟漪又归于平 —— 水面不是没有波，是波过之后还照得出人。",
    ),
    dict(
        no=4, pid="thai-zen-04-enough-v2", comp="Enough", slug="thai_zen_04_enough",
        title="泰语千词 · 禅意 04 知足（重做版）",
        hook="要拥有多少，\n才算幸福？", hook_tts="要拥有多少，才算幸福？",
        thai="ความสุขไม่ใช่การมีมาก",
        thai_lines=["ความสุข ไม่ใช่", "การ มี มาก"],
        roman="khwaam-sùk mâi-châi — gaan mii mâak",
        zh="幸福，不是拥有得多",
        words=[("ความสุข", "khwaam-sùk", "幸福"), ("ไม่ใช่", "mâi-châi", "不是"),
               ("มี", "mii", "拥有 · 有"), ("มาก", "mâak", "多")],
        bgm="alt1_piano.mp3", bgm_gain=0.085,
        bg=[("coverr-desert-island-7521.mp4", 0.70),
            ("coverr-sunset-in-indonesia-3381.mp4", 0.55),
            ("coverr-sunrise-in-costa-rica-1299.mp4", 0.35)],
        grade="saturation=0.55:brightness=-0.01:contrast=1.05",
        art="暗紫 + 蜜色。装置是「越数越少」：开场满屏细点代表「拥有得多」，"
            "每讲一个词就熄掉一片，最后只剩正中一点还亮着 —— 幸福是剩下的那一个，不是攒下的那一堆。",
    ),
    dict(
        no=5, pid="thai-zen-05-beginagain-v2", comp="BeginAgain", slug="thai_zen_05_beginagain",
        title="泰语千词 · 禅意 05 重新开始（重做版）",
        hook="今天，\n撑不下去了吗？", hook_tts="今天，撑不下去了吗？",
        thai="ยังหายใจอยู่ก็เริ่มใหม่ได้",
        thai_lines=["ยัง หายใจ อยู่", "ก็ เริ่มใหม่ ได้"],
        roman="yang hǎai-jai yùu — gɔ̂ɔ rə̂əm-mài dâai",
        zh="只要还在呼吸，就能重新开始",
        words=[("หายใจ", "hǎai-jai", "呼吸"), ("เริ่มใหม่", "rə̂əm-mài", "重新开始"),
               ("ได้", "dâai", "能够"), ("ยัง", "yang", "还 · 仍")],
        bgm="zen_bed.mp3", bgm_gain=0.09,
        bg=[("coverr-walking-to-the-mountain-top-8360.mp4", 0.38),
            ("coverr-road-in-the-mountains-7132.mp4", 0.62),
            ("coverr-sunrise-in-costa-rica-1299.mp4", 0.50)],
        grade="saturation=0.56:brightness=0.00:contrast=1.05",
        art="墨绿 + 晨光金。装置是「呼吸」：整幅画面以 4 秒一次的节律极缓地明暗与缩放，"
            "词在吸气那一档亮起 —— 这一集的主语就是呼吸，画面自己得在呼吸。",
    ),
]

SHARED = ["composition/CjkFonts.tsx", "composition/index.tsx"]
BGM_TARGET_DB = -13.8       # 01 的 warm_piano 就是这个电平，全系列以它为准


def normalize_bgm(src: Path, dst: Path) -> float:
    import re, subprocess
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src),
                          "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    mean = float(re.search(r"mean_volume:\s*(-?[\d.]+)", out).group(1))
    adj = BGM_TARGET_DB - mean
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                    "-af", f"volume={adj:.2f}dB", "-b:a", "192k", str(dst)], check=True)
    return adj


def build_script_json(ep: dict) -> dict:
    words = ep["words"]
    sections = [dict(id="s00_hook", text=ep["hook_tts"]),
                dict(id="s01_sent", text=f'{ep["zh"]}。 → {ep["thai"]}')]
    units = [dict(id="s00_hook_zh", section="s00_hook", lang="zh", text=ep["hook_tts"]),
             dict(id="s01_sent_zh", section="s01_sent", lang="zh", text=ep["zh"] + "。"),
             dict(id="s01_sent_th", section="s01_sent", lang="th", text=ep["thai"], display="{text}")]
    cards = []
    for i, (th, rom, zh) in enumerate(words, 1):
        sections.append(dict(id=f"w{i}", text=f"{zh} → {th}（读两遍）"))
        units += [dict(id=f"w{i}_zh", section=f"w{i}", lang="zh", text=zh.replace(" · ", "、")),
                  dict(id=f"w{i}_th", section=f"w{i}", lang="th", text=th)]
        cards.append(dict(id=f"w{i}", thai=th, roman=rom, zh=zh))
    sections += [dict(id="s09_again", text=f'{ep["thai"]}（整句再读一次）'),
                 dict(id="s10_outro", text="泰语千词，在泰国生活够用了。")]
    units += [dict(id="s09_again_th", section="s09_again", lang="th", text=ep["thai"]),
              dict(id="s10_outro_zh", section="s10_outro", lang="zh", text="泰语千词，在泰国生活够用了。")]
    return {
        "version": "1.0", "project_id": ep["pid"], "sections": sections,
        "metadata": {
            "origin": f'lang1000/marketing/video/series_zen/{ep["slug"]}.mp4（540×960，moviepy 老产线）；'
                      "文案逐帧读回、逐字保留，画面与配乐重做，输出改为 1080×1920",
            "sentence": dict(thai=ep["thai"], roman=ep["roman"], zh=ep["zh"],
                             thaiDisplay=" ".join(ep["thai_lines"]), thaiLines=ep["thai_lines"]),
            "hook": ep["hook"],
            "tts": {"engine": "edge",
                    "voices": {"zh": "zh-CN-YunjianNeural", "th": "th-TH-PremwadeeNeural"},
                    "rates": {"th": "-30%", "zh": "-15%"}, "pitches": {"zh": "-4Hz"}},
            "tts_units": units, "cards": cards,
        },
    }


def main() -> int:
    only = sys.argv[1:]
    for ep in EPISODES:
        if only and not any(a in ep["pid"] for a in only):
            continue
        proj = REPO / "projects" / ep["pid"]
        (proj / "artifacts").mkdir(parents=True, exist_ok=True)
        (proj / "renders").mkdir(exist_ok=True)
        (proj / "assets").mkdir(exist_ok=True)

        # 引擎知识：字体、app icon 直接拷；这些各集完全一样
        for sub in ("composition/public/fonts", "composition/public/app"):
            dst = proj / sub
            if not dst.exists():
                shutil.copytree(BASE / sub, dst)
        for f in SHARED:
            (proj / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(BASE / f, proj / f)
        # index.tsx 的 composition id 每集不同
        idx = proj / "composition/index.tsx"
        idx.write_text(idx.read_text().replace("Impermanence", ep["comp"]), encoding="utf-8")

        # 垫乐：每集换一条，从 01 已经下好的 13 条里挑（Pixabay 免费授权，本地已有）。
        # **必须先校准到 −13.8dB 再用** —— 这 13 条原始电平差了 17dB
        # （m_bowl −27.4 / zen_bed −10.1），不校准的话 props 里那个 gain
        # 在不同集里含义完全不同：02 的垫乐量到 −49.5dB，等于没放。
        (proj / "assets/music").mkdir(parents=True, exist_ok=True)
        shutil.copy2(BASE / "assets/music" / ep["bgm"], proj / "assets/music" / ep["bgm"])
        (proj / "composition/public/music").mkdir(parents=True, exist_ok=True)
        normalize_bgm(BASE / "assets/music" / ep["bgm"], proj / "composition/public/music/bgm.mp3")

        (proj / "artifacts/script.json").write_text(
            json.dumps(build_script_json(ep), ensure_ascii=False, indent=2), encoding="utf-8")
        (proj / "project.json").write_text(json.dumps({
            "version": "1.0", "project_id": ep["pid"], "title": ep["title"],
            "pipeline_type": "animated-explainer"}, ensure_ascii=False, indent=2), encoding="utf-8")
        (proj / "artifacts/edit_decisions.json").write_text(json.dumps({
            "version": "1.0", "project_id": ep["pid"], "render_runtime": "remotion",
            "composition_mode": "atelier", "renderer_family": "bespoke",
            "bespoke": {
                "entry": str(proj / "composition/index.tsx"), "composition_id": ep["comp"],
                "props_path": str(proj / "composition/props.json"),
                "public_dir": str(proj / "composition/public"), "crf": 18,
                "art_direction": ep["art"],
            }}, ensure_ascii=False, indent=2), encoding="utf-8")
        (proj / "artifacts/bg_spec.json").write_text(json.dumps(
            {"clips": [{"file": f, "x": x} for f, x in ep["bg"]], "grade": ep["grade"]},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print(f'✓ {ep["pid"]:28} {len(ep["words"])} 词 · 垫乐 {ep["bgm"]} · 底片 {len(ep["bg"])} 段')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
