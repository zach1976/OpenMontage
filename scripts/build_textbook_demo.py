"""《新编基础泰语》带货系列 · 01 demo：泰语第一课先背 9 个中辅音。

配音 edge-tts（零费用）；时间轴全部用全片绝对秒，音频在合成顶层挂，
避免 Sequence 相对时间漏减 start 的老坑。

    python3 scripts/build_textbook_demo.py           # 合成配音 + 写 props/artifacts
    python3 scripts/build_textbook_demo.py --render  # 再渲染 renders/demo-v1.mp4
"""
from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path

import edge_tts

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from lib.checkpoint import init_project

PID = "thai-book-jichu-01-consonants"
COMP = "TextbookConsonants"
PROJ = REPO / "projects" / PID
TEMPLATE = REPO / "projects/thai-1000-idiom-01-diao"
SRC_SHOT = Path("/Users/zhenyusong/.terminalAssist/grabs/2026-10-11_16-00-31.png")
FPS = 30
ALPHA_ICON = Path("/Users/zhenyusong/projects/AlphabetLearningFramework/apps/thai/ios/Runner/Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png")

ZH = ("zh-CN-XiaoxiaoNeural", "+8%")
TH = ("th-TH-PremwadeeNeural", "-8%")

# 9 个中辅音（传统字母序）；ฎ ฏ 少用，只上屏不念
MID = [
    ("ก", "กอ ไก่", "鸡", True),
    ("จ", "จอ จาน", "盘", True),
    ("ฎ", "ฎอ ชฎา", "冠", False),
    ("ฏ", "ฏอ ปฏัก", "棒", False),
    ("ด", "ดอ เด็ก", "童", True),
    ("ต", "ตอ เต่า", "龟", True),
    ("บ", "บอ ใบไม้", "叶", True),
    ("ป", "ปอ ปลา", "鱼", True),
    ("อ", "ออ อ่าง", "盆", True),
]

LINES = {
    "hook": "大学泰语专业，第一节课学什么？不是你好，是辅音分组。",
    "groups": "泰语有四十四个辅音，分成中、高、低三组。分在哪一组，决定这个字的声调怎么读。",
    "mid": "先认中辅音，一共九个，常用的是这七个。",
    "again": "跟我再读一遍。",
    "book": "这些都在新编基础泰语第一册。大学泰语专业的教材，很多泰语培训班用的也是它。一到四册，还附音频。",
    "cta": "想系统学泰语，点左下角小黄车。",
    "outro": "跟着书练字母，就用学泰文字母。",
}


def dur(p: Path) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)], text=True))


async def synth(path: Path, text: str, voice: tuple[str, str]) -> None:
    if path.exists() and path.stat().st_size > 500:
        return
    raw = path.with_name(path.stem + "_raw.mp3")
    for attempt in range(6):
        try:
            await edge_tts.Communicate(text, voice=voice[0], rate=voice[1]).save(str(raw))
            break
        except Exception:
            if attempt == 5:
                raise
            await asyncio.sleep(5 * (attempt + 1))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
                    "silenceremove=start_periods=1:start_silence=0.02:start_threshold=-45dB,areverse,"
                    "silenceremove=start_periods=1:start_silence=0.08:start_threshold=-45dB,areverse",
                    "-c:a", "libmp3lame", "-b:a", "192k", str(path)], check=True)
    raw.unlink()
    print("audio", path.name, flush=True)


def workspace() -> None:
    if not PROJ.exists():
        init_project(PID, title="泰语第一课 · 9 个中辅音（基础泰语带货 01）", pipeline_type="animated-explainer")
    pub = PROJ / "composition/public"
    for d in ("audio", "fonts", "app", "img"):
        (pub / d).mkdir(parents=True, exist_ok=True)
    (PROJ / "assets/audio").mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE / "composition/public/fonts/Sarabun-Bold.ttf", pub / "fonts/Sarabun-Bold.ttf")
    shutil.copy2(ALPHA_ICON, pub / "app/alpha_icon.png")
    shutil.copy2(TEMPLATE / "assets/music/background.mp3", pub / "audio/background.mp3")
    # 商品主图里的四册合照（截图 822×716，书在 x195–625 / y160–550）
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(SRC_SHOT), "-vf",
                    "crop=430:390:195:160,scale=1290:-1:flags=lanczos", str(pub / "img/books.png")], check=True)
    src = REPO / "scripts/textbook_series"
    for name in ("index.tsx", "Composition.tsx"):
        shutil.copy2(src / name, PROJ / "composition" / name)
    (PROJ / "composition/Root.tsx").write_text(
        'import {Composition} from "remotion";\nimport {Scene,calculateMetadata,SceneProps} from "./Composition";\n'
        f'export const Root:React.FC=()=><Composition id="{COMP}" component={{Scene}} durationInFrames={{1800}} '
        'fps={30} width={1080} height={1920} defaultProps={{} as SceneProps} calculateMetadata={calculateMetadata}/>;\n')


def reads() -> list[tuple[str, str, tuple[str, str]]]:
    r = [(k, v, ZH) for k, v in LINES.items()]
    r += [(f"th_{i}", name, TH) for i, (_, name, _, live) in enumerate(MID) if live]
    return r


def build() -> dict:
    A = PROJ / "assets/audio"
    pub = PROJ / "composition/public/audio"
    for f in A.glob("*.mp3"):
        shutil.copy2(f, pub / f.name)
    d = {f.stem: dur(f) for f in A.glob("*.mp3")}
    audio, scenes, t = [], [], 0.0

    def say(key: str, at: float) -> float:
        audio.append({"file": f"{key}.mp3", "at": round(at, 3)})
        return at + d[key]

    def scene(sid: str, start: float, end: float, label: str, text: str) -> None:
        scenes.append({"id": sid, "start": round(start, 3), "end": round(end, 3), "label": label, "text": text})

    # 封面：第 0 帧即成品
    s = t
    t = say("hook", t) + 0.45
    scene("cover", s, t, "封面 · 泰语第一课", LINES["hook"])
    s = t
    t = say("groups", t + 0.2) + 0.5
    scene("groups", s, t, "44 个辅音分三组", LINES["groups"])

    s = t
    t = say("mid", t + 0.2) + 0.35
    pass1, pass2 = [], []
    for i, (_, _, _, live) in enumerate(MID):
        if not live:
            continue
        pass1.append({"i": i, "at": round(t, 3)})
        t = say(f"th_{i}", t) + 0.32
    t = say("again", t + 0.25) + 0.3
    for i, (_, _, _, live) in enumerate(MID):
        if not live:
            continue
        pass2.append({"i": i, "at": round(t, 3), "gap": round(d[f"th_{i}"] + 0.55, 3)})
        t = say(f"th_{i}", t)
        t += d[f"th_{i}"] + 0.55  # 跟读空档 ≈ 词长 + 0.55
    scene("mid", s, t, "中辅音 · 读两遍 + 跟读", LINES["mid"] + LINES["again"])

    s = t
    t = say("book", t + 0.15) + 0.5
    scene("book", s, t, "教材：新编基础泰语 1–4 册", LINES["book"])
    s = t
    t = say("cta", t + 0.1) + 0.25
    t = say("outro", t) + 1.2
    scene("end", s, t, "小黄车 + 学泰文字母 App", LINES["cta"] + LINES["outro"])

    total = round(t * FPS)
    props = {
        "fps": FPS, "totalFrames": total, "totalSeconds": total / FPS,
        "mid": [{"ch": c, "name": n, "anchor": a, "live": live} for c, n, a, live in MID],
        "pass1": pass1, "pass2": pass2, "scenes": scenes, "audio": audio,
        "bgm": {"file": "background.mp3", "volume": 0.05},
        "speak": [[a["at"], round(a["at"] + d[a["file"][:-4]], 3)] for a in audio],
        "review_timeline": [{"id": x["id"], "label": x["label"], "start": x["start"], "end": x["end"],
                             "title": x["label"], "text": x["text"], "credit": "商品主图：出版社直营店"} for x in scenes],
    }
    return props


def save(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def artifacts(props: dict) -> None:
    A = PROJ / "artifacts"
    save(PROJ / "composition/props.json", props)
    save(A / "props.json", props)
    save(A / "script.json", {
        "version": "1.0", "title": "泰语第一课 · 先背这 9 个",
        "total_duration_seconds": props["totalSeconds"],
        "sections": [{"id": x["id"], "label": x["label"], "text": x["text"], "start_seconds": x["start"],
                      "end_seconds": x["end"], "speaker_directions": "中文女声讲解；泰语女声念辅音名，读两遍，第二遍留跟读空档。"}
                     for x in props["scenes"]],
        "metadata": {"language": "zh+th", "kind": "带货·图书", "product": "新编基础泰语1-2 + 基础泰语3-4（世界图书出版广东公司）",
                     "tts": {"engine": "edge", "voices": {"zh": ZH[0], "th": TH[0]}, "rates": {"zh": ZH[1], "th": TH[1]}},
                     "claims_policy": "只用封面可核实的说法：大学泰语专业教材 / 1–4 册 / 附音频；不用'都在用''最权威'。"},
    })
    save(A / "publish.json", {
        "series_id": 1, "sub_series": "教材带货", "slug": "thai_book_jichu_01",
        "title": "泰语第一课，先背这9个",
        "publish_copy": "大学泰语专业第一课：44 个辅音分中、高、低三组，先认 9 个中辅音。\n"
                        "教材：新编基础泰语 1–4 册，附音频；配套练字母用「学泰文字母」。\n\n#泰语 #泰语学习 #泰语入门 #泰语教材",
        "wechat_copy": "泰语第一课，先背这9个中辅音",
        "credits": "教材图片：出版社直营店商品主图；配音与剪辑：泰语千词。",
    })


async def main() -> None:
    workspace()
    for key, text, voice in reads():
        await synth(PROJ / "assets/audio" / f"{key}.mp3", text, voice)
        await asyncio.sleep(0.6)  # 串行 + 间隔，防 edge-tts 限流
    props = build()
    artifacts(props)
    print(PID, f"{props['totalSeconds']:.1f}s")
    if "--render" in sys.argv:
        out = PROJ / "renders/demo-v1.mp4"
        out.parent.mkdir(exist_ok=True)
        subprocess.run(["npx", "remotion", "render", str(PROJ / "composition/index.tsx"), COMP, str(out),
                        f"--props={PROJ / 'composition/props.json'}",
                        f"--public-dir={PROJ / 'composition/public'}"],
                       cwd=REPO / "remotion-composer", check=True)


if __name__ == "__main__":
    asyncio.run(main())
