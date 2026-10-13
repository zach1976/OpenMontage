"""基础泰语带货系列 · 书本素材版（2026-10-11 用户指令：素材一律取自书的 PDF + MP3）。

和 build_textbook_series.py 的区别只在素材来源：
  - 泰语读音 = 书配套 MP3 里切出来的原声（不再用 edge-tts 泰语）
  - 画面 = 书页扫描件的裁图（2× 渲染、去掉反面透字和浅灰水印）
  - 教学内容 = 书里对应那一课的真实内容
中文讲解仍是 edge-tts。选题、版式与 01–10 原版一致（"原来的视频保留，只换素材"），
另加 11–20 跟着书的课程走。成片入库沿用原 slug，覆盖原来那条。

素材目录：~/Downloads/基础泰语PDF+mp3/基础泰语{1..4}  PDF MP3/
  第 1 册 PDF 页 = 书页 + 8；第 2 册 PDF 页 = 书页 + 1。MP3 按课编号。

    python3 scripts/build_thai_book_series.py 01 [--render]
"""
from __future__ import annotations

import asyncio
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_textbook_series import TL, synth, dur, save, REPO, TEMPLATE, SERIES_SRC, FPS, ZH, BOOKS_PNG, ALPHA_ICON  # noqa: E402
from lib.checkpoint import init_project  # noqa: E402

ROOT = Path.home() / "Downloads" / "基础泰语PDF+mp3"
BOOK = {1: ROOT / "基础泰语1  PDF MP3", 2: ROOT / "基础泰语2  PDF MP3",
        3: ROOT / "基础泰语3  PDF MP3", 4: ROOT / "基础泰语4  PDF MP3"}
PDF = {1: "基础泰语1.pdf", 2: "泰语基础二完整版.pdf", 3: "基础泰语3.pdf", 4: "基础泰语4.pdf"}
CTA = "想系统学泰语，点左下角小黄车。"
OUTRO = "背单词用泰语千词，练字母用学泰文字母。"
TAGS = "#泰语 #泰语学习 #泰语入门 #泰语教材 #带货"
GRID_W = 1000  # 裁切框按 1000 宽的页面量；实际 2× 渲染


def crop_page(book: int, page: int, box: tuple[int, int, int, int], out: Path, scale: int = 2) -> None:
    """书页裁图：2× 渲染 → 裁切 → 浅灰（反面透字、PDG 水印、扫描底色）推白，黑字保留。"""
    d = tempfile.mkdtemp()
    subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-scale-to-x", str(GRID_W * scale),
                    "-scale-to-y", "-1", "-png", str(BOOK[book] / PDF[book]), f"{d}/p"], check=True)
    im = Image.open(next(Path(d).glob("p*.png"))).convert("L")
    x0, y0, x1, y1 = (v * scale for v in box)
    im = im.crop((x0, y0, x1, y1)).point(lambda v: 255 if v > 168 else int(v * 255 / 168))
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)


def cut_clip(book: int, mp3: str, s: float, e: float, out: Path, pad: float = 0.08) -> None:
    """书配套录音切片：前后各留一点，响度拉到和中文讲解相近。"""
    if out.exists() and out.stat().st_size > 500:
        return
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(0, s - pad):.3f}", "-to", f"{e + pad:.3f}",
                    "-i", str(BOOK[book] / mp3), "-af", "loudnorm=I=-17:TP=-2:LRA=7,afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse",
                    "-ar", "24000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "160k", str(out)], check=True)
    print("  clip", out.name, f"{e - s:.2f}s", flush=True)


# ================================================================ 01 中辅音（第 1 册第 1 课）
MID9 = [("ก", "g"), ("จ", "z"), ("ฎ", "同 ด"), ("ฏ", "同 ต"), ("ด", "d"), ("ต", "d·不振动"), ("บ", "b"), ("ป", "b·不振动"), ("อ", "o")]
# U01-01.mp3 40–60s：九个中辅音各读一遍，顺序同书第 10 页
MID9_T = [(40.35, 40.91), (42.97, 43.61), (45.39, 46.10), (47.95, 48.56), (50.24, 50.95),
          (52.55, 53.19), (54.72, 55.37), (56.97, 57.58), (59.10, 59.65)]
# 第 10–11 页的发音方法卡（ฎ 用 ด 的卡、ฏ 用 ต 的卡：书上就是合在一张卡里的）
CARD = {"ก": (18, (80, 410, 930, 590)), "จ": (18, (80, 630, 930, 800)), "ด": (18, (80, 840, 930, 1015)),
        "ต": (18, (80, 1110, 930, 1285)), "บ": (19, (85, 75, 935, 245)), "ป": (19, (85, 285, 935, 445)),
        "อ": (19, (85, 490, 935, 655))}


def plan01(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 泰语第一课", L["hook"])
    tl.say("hook", post=0.45)
    tl.begin("groups", "44 个辅音分三组", L["groups"])
    tl.say("groups", pre=0.2, post=0.5)
    tl.begin("mid", "第 1 课 · 九个中辅音（书的原声）", L["mid"] + L["again"])
    tl.say("mid", pre=0.2, post=0.35)
    for i in range(9):
        tl.say(f"th_m{i}", mark=f"p{i}", post=0.24)
    tl.say("again", pre=0.25, post=0.3, mark="again")
    for i in range(9):
        tl.say(f"th_m{i}", mark=f"m{i}_a")
        tl.marks[f"m{i}_f"] = round(tl.t, 3)
        tl.gap(tl.d[f"th_m{i}"] + 0.42)
        tl.marks[f"m{i}_e"] = round(tl.t, 3)


# ================================================================ 02 声调（第 1 册第 3 课）
# U01-03.mp3：12–20s 是"以 ก 为例"的五个声调（音高曲线已核：平/低/降/高/升）；
# 137–178s 是第 30 页词汇表，按书上顺序逐词读（ป้า / เก้า / เก่า / ป่า 的音高也核过）。
FIVE_T = [(12.06, 12.76), (13.89, 14.54), (15.75, 16.36), (17.45, 18.04), (19.06, 19.63)]


def plan02(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 一个音五个声调", L["hook"])
    tl.say("hook", post=0.45)
    tl.begin("tones", "书上的五声调表", L["tones"])
    tl.say("tones", pre=0.15, post=0.3)
    tl.begin("five", "以 ก 为例：กา ก่า ก้า ก๊า ก๋า（书的原声）", "".join(L[f"t{i}"] for i in range(5)))
    for i in range(5):
        tl.say(f"t{i}", pre=0.2, mark=f"t{i}")
        tl.drill(f"th_t{i}", f"t{i}")
    tl.begin("pair", "เก่า 旧 / เก้า 九", L["pair"])
    tl.say("pair", pre=0.2, post=0.1)
    tl.drill("th_p0", "p0")
    tl.drill("th_p1", "p1")
    tl.begin("quiz", "听音选词：ป่า / ป้า", L["quiz"] + L["answer"])
    tl.say("quiz", pre=0.2, post=0.25)
    tl.say("th_q", mark="q")
    tl.gap(1.3)
    tl.say("answer", mark="ans", post=0.4)


# ================================================================ 03 第一天五句（第 1 册第 15 课 日常用语 + 课堂用语）
# U01-15.mp3：同一位女声，每句先读 ครับ 版再读 ค่ะ 版；取 ค่ะ 版。逐段 small 模型识别核过。
def plan03(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 到泰国第一天", L["hook"])
    tl.say("hook", post=0.45)
    tl.begin("chat", "五句（第 15 课原句 + 原声）", "".join(L[f"s{i}"] for i in range(5)))
    for i in range(5):
        tl.say(f"s{i}", pre=0.25, mark=f"s{i}")
        tl.drill(f"th_s{i}", f"s{i}")


# ================================================================ 04 四册路线（各册原声 + 目录 / 课页）
def plan04(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 零基础到读课文", L["hook"])
    tl.say("hook", post=0.4)
    tl.begin("stairs", "1→4 册（各册原声）", "".join(L[f"k{i}"] for i in range(4)))
    for i in range(4):
        tl.say(f"k{i}", pre=0.25, mark=f"k{i}")
        tl.drill(f"th_k{i}", f"k{i}")


# ================================================================ 05 / 08 / 09（第 2 册第 1 课 打招呼：对话 + 生词朗读）
B2L1 = "01.mp3"


def plan05(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 音频这样用", L["hook"])
    tl.say("hook", post=0.4)
    tl.begin("listen", "听：只听不看", L["st0"])
    tl.say("st0", pre=0.15, post=0.2, mark="st0")
    tl.say("th_x", pre=0.2, mark="l1")
    tl.say("th_x", pre=0.45, mark="l2", post=0.4)
    tl.begin("shadow", "跟：跟着读", L["st1"])
    tl.say("st1", pre=0.15, mark="st1")
    for k in ("r1", "r2"):
        tl.say("th_x", pre=0.3, mark=f"{k}_a")
        tl.marks[f"{k}_f"] = round(tl.t, 3)
        tl.gap(tl.d["th_x"] + 0.6)
    tl.begin("check", "对：对照课本", L["st2"])
    tl.say("st2", pre=0.15, post=0.2, mark="st2")
    tl.say("th_x", pre=0.2, mark="c1", post=0.3)
    tl.say("sum", pre=0.2, mark="sum", post=0.3)


def plan_n(sid: str, label: str, prefix: str, n: int, tail_rule: bool = False):
    def plan(tl: TL, L: dict) -> None:
        tl.begin("cover", "封面", L["hook"])
        tl.say("hook", post=0.4)
        tl.begin(sid, label, "".join(L[f"{prefix}{i}"] for i in range(n)))
        for i in range(n):
            tl.say(f"{prefix}{i}", pre=0.25, mark=f"{prefix}{i}")
            tl.drill(f"th_{prefix}{i}", f"{prefix}{i}")
        if tail_rule:
            tl.begin("rule", "记法", L["rule"])
            tl.say("rule", pre=0.2, post=0.4, mark="rule")
    return plan


# ================================================================ 06 数字（第 2 册第 2 课 泰语数字的写法与读法(1)）
NUM_T = [(218.13, 218.78), (220.36, 221.09), (222.56, 223.33), (224.74, 225.44), (226.94, 227.65),
         (229.10, 229.62), (231.20, 231.72), (233.48, 234.01), (235.68, 236.41), (240.95, 241.48)]


def plan06(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 数字 1 到 10", L["hook"])
    tl.say("hook", post=0.4)
    tl.begin("count", "1–10 先听一遍，再跟读（书的原声）", L["n_intro"] + L["n_again"])
    tl.say("n_intro", pre=0.15, post=0.25)
    for i in range(10):
        tl.say(f"th_n{i}", mark=f"p{i}", post=0.26)
    tl.say("n_again", pre=0.3, post=0.25, mark="again")
    for i in range(10):
        tl.say(f"th_n{i}", mark=f"n{i}_a")
        tl.marks[f"n{i}_f"] = round(tl.t, 3)
        tl.gap(tl.d[f"th_n{i}"] + 0.42)
        tl.marks[f"n{i}_e"] = round(tl.t, 3)
    tl.begin("use", "用起来：一共四口人", L["use"])
    tl.say("use", pre=0.2, mark="use")
    tl.drill("th_use", "u")


# ================================================================ 11 高辅音（第 1 册第 4 课）
HIGH10 = ["ข", "ฉ", "ถ", "ฐ", "ผ", "ฝ", "ศ", "ษ", "ส", "ห"]
HIGH_T = [(11.93, 12.71), (14.02, 14.79), (16.22, 16.93), (18.37, 19.06), (20.70, 21.39),
          (22.87, 23.50), (24.88, 25.53), (26.81, 27.45), (28.78, 29.50), (30.70, 31.28)]


def plan11(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 高辅音", L["hook"])
    tl.say("hook", post=0.4)
    tl.begin("rise", "十个高辅音（书的原声）", L["intro"] + L["again"])
    tl.say("intro", pre=0.15, post=0.3)
    for i in range(10):
        tl.say(f"th_h{i}", mark=f"p{i}", post=0.26)
    tl.say("again", pre=0.3, post=0.25, mark="again")
    for i in range(10):
        tl.say(f"th_h{i}", mark=f"h{i}_a")
        tl.marks[f"h{i}_f"] = round(tl.t, 3)
        tl.gap(tl.d[f"th_h{i}"] + 0.42)
        tl.marks[f"h{i}_e"] = round(tl.t, 3)
    tl.begin("rule", "书上的规则", L["rule"])
    tl.say("rule", pre=0.2, post=0.4, mark="rule")


# ================================================================ 12 高低辅音配对（第 1 册第 4、5 课） / 13 尾辅音（第 1 册第 9 课）
PAIRS = [("ข", "ค", (11.93, 12.71), (12.68, 13.38), "k"), ("ฉ", "ช", (14.02, 14.79), (16.18, 16.96), "ch"),
         ("ส", "ซ", (28.78, 29.50), (17.98, 18.69), "s"), ("ผ", "พ", (20.70, 21.39), (27.82, 28.47), "p"),
         ("ฝ", "ฟ", (22.87, 23.50), (29.50, 30.09), "f")]


def plan12(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 高低辅音", L["hook"])
    tl.say("hook", post=0.4)
    tl.begin("pairs", "五对高低辅音（书的原声）", L["intro"])
    tl.say("intro", pre=0.15, post=0.3)
    for i in range(5):
        tl.say(f"th_hi{i}", pre=0.3, mark=f"hi{i}", post=0.35)
        tl.drill(f"th_lo{i}", f"lo{i}")
    tl.begin("rule", "书上的规则", L["rule"])
    tl.say("rule", pre=0.2, post=0.4, mark="rule")


def plan13(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 尾辅音", L["hook"])
    tl.say("hook", post=0.4)
    tl.begin("tails", "กา 加五种尾巴（书的原声）", L["base"] + "".join(L[f"e{i}"] for i in range(5)))
    tl.say("base", pre=0.15, post=0.25, mark="base")
    tl.say("th_base", post=0.5, mark="b0")
    for i in range(5):
        tl.say(f"e{i}", pre=0.2, mark=f"e{i}")
        tl.drill(f"th_e{i}", f"e{i}")


def tail(tl: TL, L: dict) -> None:
    tl.begin("book", "教材：基础泰语第 1 册第 1 课", L["book"])
    tl.say("book", pre=0.15, post=0.5)
    tl.begin("end", "小黄车 + 泰语千词 + 学泰文字母", CTA + OUTRO)
    tl.say("cta", pre=0.1, post=0.25)
    tl.say("outro", mark="outro", post=1.2)
    tl.end()


EPISODES = {
    "01": dict(
        pid="thai-book-jichu-01-consonants", pub_title="泰语第一课先背这9个", comp="TextbookConsonants", src="b01.tsx", plan=plan01,
        title="泰语第一课，先背这9个", cover=("泰语第一课", "先背这9个"), slug="thai_book_jichu_01",
        lines={
            "hook": "大学泰语专业，第一节课学什么？不是你好，是辅音分组。",
            "groups": "泰语有四十四个辅音，分中、高、低三组，分组决定声调。",
            "mid": "书上第一课，九个中辅音，听原声。",
            "again": "跟原声再读一遍。",
            "book": "这是基础泰语第一册第一课，适用于培训班学员，附音频。",
        },
        clips={f"th_m{i}": (1, "U01-01.mp3", s, e) for i, (s, e) in enumerate(MID9_T)},
        crops=dict({f"card_{k}": (1, p, b) for k, (p, b) in CARD.items()},
                   row9=(1, 18, (125, 85, 885, 165)), same=(1, 18, (80, 200, 930, 275)),
                   lesson=(1, 16, (0, 0, 1000, 1000))),
        data={"mid": [{"ch": c, "hint": h, "card": f"card_{'ด' if c == 'ฎ' else 'ต' if c == 'ฏ' else c}"} for c, h in MID9]},
        copy="泰语第一课：44 个辅音分中、高、低三组，先认 9 个中辅音（ฎ 同 ด、ฏ 同 ต）。\n"
             "内容与原声取自《基础泰语》第 1 册第 1 课，1–4 册附音频。",
    ),
    "02": dict(
        pid="thai-book-jichu-02-tones", pub_title="泰语一个音五个声调", comp="TextbookTones", src="b02.tsx", plan=plan02,
        title="泰语一个音，五个声调", cover=("泰语一个音", "五个声调"), slug="thai_book_jichu_02",
        book_label="第 1 册 · 第 3 课",
        lines={
            "hook": "泰语五个声调，换个声调，就是另一个字。",
            "tones": "书上用一个音，演示五个声调。",
            "t0": "第一声。",
            "t1": "第二声，像上声。",
            "t2": "第三声，像去声。",
            "t3": "第四声。",
            "t4": "第五声，像阳平。",
            "pair": "旧和九，只差一个声调。",
            "quiz": "考考你，这是哪一个？",
            "answer": "是伯母。",
            "book": "声调在基础泰语第一册第三课，一到四册，附原声音频。",
        },
        clips=dict({f"th_t{i}": (1, "U01-03.mp3", s, e) for i, (s, e) in enumerate(FIVE_T)},
                   th_p0=(1, "U01-03.mp3", 170.72, 171.33), th_p1=(1, "U01-03.mp3", 165.67, 166.33),
                   th_q=(1, "U01-03.mp3", 144.62, 145.21)),
        crops={"table": (1, 36, (85, 765, 935, 1300)), "ka": (1, 37, (140, 760, 880, 975)),
               "vocab": (1, 38, (70, 850, 900, 1250)), "lesson": (1, 36, (0, 0, 1000, 1000))},
        data={"five": [{"th": "กา", "tone": "第一声", "desc": "中平", "curve": "flat"},
                       {"th": "ก่า", "tone": "第二声", "desc": "像上声", "curve": "low"},
                       {"th": "ก้า", "tone": "第三声", "desc": "降调", "curve": "fall"},
                       {"th": "ก๊า", "tone": "第四声", "desc": "往上挑", "curve": "high"},
                       {"th": "ก๋า", "tone": "第五声", "desc": "像阳平", "curve": "rise"}],
              "pair": [{"th": "เก่า", "zh": "旧", "tone": "第二声", "curve": "low"},
                       {"th": "เก้า", "zh": "九", "tone": "第三声", "curve": "fall"}],
              "quiz": [{"th": "ป่า", "zh": "树林"}, {"th": "ป้า", "zh": "伯母"}], "answer": 1},
        copy="泰语五个声调：กา ก่า ก้า ก๊า ก๋า；一个声调之差：เก่า 旧 / เก้า 九，ป่า 树林 / ป้า 伯母。\n"
             "内容与原声取自《基础泰语》第 1 册第 3 课，1–4 册附音频。",
    ),
    "03": dict(
        pid="thai-book-jichu-03-day-one", pub_title="到泰国第一天这5句够用", comp="TextbookDayOne", src="b03.tsx", plan=plan03,
        title="到泰国第一天，这5句够用", cover=("到泰国第一天", "这5句够用"), slug="thai_book_jichu_03",
        book_label="第 1 册 · 第 15 课",
        lines={
            "hook": "到泰国第一天，这五句话一定用得上。",
            "s0": "见面打招呼。",
            "s1": "别人帮了你。",
            "s2": "不小心碰到人。",
            "s3": "对方说太快。",
            "s4": "没听懂。",
            "book": "这五句都在基础泰语第一册第十五课，日常用语和课堂用语。一到四册，附原声音频。",
        },
        clips={"th_s0": (1, "U01-15.mp3", 16.47, 17.38), "th_s1": (1, "U01-15.mp3", 23.71, 24.63),
               "th_s2": (1, "U01-15.mp3", 20.06, 20.90), "th_s3": (1, "U01-15.mp3", 144.65, 145.93),
               "th_s4": (1, "U01-15.mp3", 167.42, 168.36)},
        crops={"l0": (1, 185, (120, 376, 440, 424)), "l1": (1, 185, (120, 468, 440, 516)),
               "l2": (1, 185, (120, 422, 440, 470)), "l3": (1, 186, (120, 856, 600, 906)),
               "l4": (1, 186, (120, 1084, 600, 1132)), "lesson": (1, 185, (0, 0, 1000, 1060))},
        data={"lines": [{"th": "สวัสดีค่ะ", "zh": "你好", "tag": "打招呼", "crop": "l0"},
                        {"th": "ขอบคุณค่ะ", "zh": "谢谢", "tag": "道谢", "crop": "l1"},
                        {"th": "ขอโทษค่ะ", "zh": "对不起", "tag": "道歉", "crop": "l2"},
                        {"th": "พูดช้าๆ หน่อยค่ะ", "zh": "说慢点", "tag": "太快", "crop": "l3"},
                        {"th": "ไม่เข้าใจค่ะ", "zh": "不明白", "tag": "没懂", "crop": "l4"}]},
        copy="到泰国第一天的 5 句：สวัสดี 你好 / ขอบคุณ 谢谢 / ขอโทษ 对不起 / พูดช้าๆ หน่อย 说慢点 / ไม่เข้าใจ 不明白。\n"
             "男生句尾说 ครับ，女生说 ค่ะ。原句与原声取自《基础泰语》第 1 册第 15 课。",
    ),
    "04": dict(
        pid="thai-book-jichu-04-roadmap", pub_title="泰语零基础一路读到课文", comp="TextbookRoadmap", src="b04.tsx", plan=plan04,
        title="泰语零基础，一路读到课文", cover=("泰语零基础", "一路读到课文"), slug="thai_book_jichu_04",
        book_label="1–4 册",
        lines={
            "hook": "零基础学泰语，一路学到能读课文，这套书分四册。",
            "k0": "第一册，发音。比如这个辅音。",
            "k1": "第二册，会话，开始学语法。",
            "k2": "第三册，课文。老师，我迟到了。",
            "k3": "第四册，名篇课文，连鲁迅都有。",
            "book": "基础泰语一到四册，适用于培训班学员，附音频。",
        },
        clips={"th_k0": (1, "U01-01.mp3", 40.35, 40.91), "th_k1": (2, "01.mp3", 38.88, 39.85),
               "th_k2": (3, "02.mp3", 3.17, 5.76), "th_k3": (4, "01.mp3", 1.57, 4.57)},
        crops={"s1": (1, 18, (125, 85, 885, 165)), "s2": (2, 2, (52, 330, 780, 705)),
               "s3": (3, 6, (100, 300, 950, 520)), "s4": (4, 1, (90, 290, 950, 560)),
               "lesson": (1, 16, (0, 0, 1000, 1000))},
        data={"steps": [{"book": 1, "skill": "发音", "th": "ก", "zh": "第 1 课 · 中辅音", "crop": "s1"},
                        {"book": 2, "skill": "会话", "th": "สวัสดีครับ", "zh": "你好", "crop": "s2"},
                        {"book": 3, "skill": "课文", "th": "ครูครับ ผมมาสาย", "zh": "老师，我迟到了", "crop": "s3"},
                        {"book": 4, "skill": "名篇", "th": "ภาษาไทยพื้นฐาน เล่มที่ ๔ บทที่ ๑", "zh": "基础泰语 第4册 第1课", "crop": "s4"}]},
        copy="《基础泰语》1–4 册：发音 → 会话 → 课文 → 名篇（第 4 册有鲁迅）。\n"
             "示例原声取自各册配套 MP3，书上写明适用于泰语学习者、培训班学员及二外学生。",
    ),
    "05": dict(
        pid="thai-book-jichu-05-three-steps", pub_title="自学泰语音频这样用", comp="TextbookThreeSteps", src="b05.tsx", plan=plan05,
        title="自学泰语，音频这样用", cover=("自学泰语", "音频这样用"), slug="thai_book_jichu_05",
        book_label="第 2 册 · 第 1 课",
        lines={
            "hook": "自学泰语，书配的音频怎么用？这样用。",
            "st0": "只听，不看字，听两遍。",
            "st1": "跟着读，一句跟两次。",
            "st2": "再对照课本，哪个词没听出来，就标出来。",
            "sum": "听、跟、对，一课一课往下走。",
            "book": "这句出自基础泰语第二册第一课。一到四册，每册都附音频。",
        },
        clips={"th_x": (2, B2L1, 43.06, 44.25)},
        crops={"dlg": (2, 2, (40, 215, 800, 470)), "lesson": (2, 2, (0, 0, 1000, 1000))},
        data={"sentence": {"th": "คุณชื่ออะไรครับ", "zh": "你叫什么名字？",
                           "parts": [["คุณ", "你"], ["ชื่อ", "名字"], ["อะไร", "什么"], ["ครับ", "礼貌"]]}},
        copy="自学泰语，教材音频这样用：只听不看、跟读两次、对照课本。\n"
             "例句 คุณชื่ออะไรครับ 你叫什么名字，原句与原声取自《基础泰语》第 2 册第 1 课。",
    ),
    "08": dict(
        pid="thai-book-jichu-08-particles", pub_title="泰语说话要加尾巴", comp="TextbookParticles", src="b08.tsx", plan=plan_n("mirror", "男 ครับ / 女 ค่ะ คะ（书的原声）", "g", 4),
        title="泰语说话要加尾巴", cover=("泰语说话", "要加尾巴"), slug="thai_book_jichu_08",
        book_label="第 2 册 · 第 1 课",
        lines={
            "hook": "泰语说话，句尾要加一个小尾巴，男生女生还不一样。",
            "g0": "男生打招呼。",
            "g1": "女生打招呼。",
            "g2": "男生提问。",
            "g3": "女生提问，尾巴变了声调。",
            "book": "书上第二册第一课专门讲这三个词，例句和录音都是男女对读。",
        },
        clips={"th_g0": (2, B2L1, 38.88, 39.71), "th_g1": (2, B2L1, 40.42, 41.33),
               "th_g2": (2, B2L1, 43.06, 44.25), "th_g3": (2, B2L1, 47.64, 48.34)},
        crops={"note": (2, 5, (60, 1010, 960, 1355)), "lesson": (2, 2, (0, 0, 1000, 1000))},
        data={"pairs": [{"who": "男", "base": "สวัสดี", "tail": "ครับ", "zh": "你好"},
                        {"who": "女", "base": "สวัสดี", "tail": "ค่ะ", "zh": "你好"},
                        {"who": "男", "base": "คุณชื่ออะไร", "tail": "ครับ", "zh": "你叫什么名字？"},
                        {"who": "女", "base": "คุณล่ะ", "tail": "คะ", "zh": "你呢？"}]},
        copy="泰语句尾的礼貌小尾巴：男生 ครับ，女生 ค่ะ，女生提问用 คะ。\n"
             "规则与男女原声取自《基础泰语》第 2 册第 1 课。",
    ),
    "09": dict(
        pid="thai-book-jichu-09-word-order", pub_title="泰语语序是反着的", comp="TextbookWordOrder", src="b09.tsx", plan=plan_n("tiles", "三组语序对照（书的原声）", "o", 3, True),
        title="泰语语序，是反着的", cover=("泰语语序", "是反着的"), slug="thai_book_jichu_09",
        book_label="第 2 册 · 第 1 课",
        lines={
            "hook": "泰语的语序，很多地方跟中文是反着的。",
            "o0": "新生，泰语说成，学生新。",
            "o1": "外语，说成，语言外国。",
            "o2": "外贸，说成，贸易外国。",
            "rule": "书上原话：修饰词放在被修饰词之后，正好和中文相反。",
            "book": "这条规则在基础泰语第二册第一课的注释里。一到四册，附音频。",
        },
        clips={"th_o0": (2, B2L1, 64.03, 66.00), "th_o1": (2, B2L1, 106.85, 108.49),
               "th_o2": (2, B2L1, 110.10, 111.87)},
        crops={"note": (2, 6, (40, 775, 920, 965)), "lesson": (2, 2, (0, 0, 1000, 1000))},
        data={"items": [{"label": "新生", "zh": ["新", "生"], "th": [["นักศึกษา", "生"], ["ใหม่", "新"]], "say": "ดิฉันเป็นนักศึกษาใหม่ค่ะ"},
                        {"label": "外语", "zh": ["外", "语"], "th": [["ภาษา", "语"], ["ต่างประเทศ", "外"]]},
                        {"label": "外贸", "zh": ["外", "贸"], "th": [["การค้า", "贸"], ["ต่างประเทศ", "外"]]}]},
        copy="泰语语序常跟中文反着：新生 นักศึกษาใหม่（学生+新），外语 ภาษาต่างประเทศ（语言+外国）。\n"
             "书上原话：修饰词放在被修饰词之后。出自《基础泰语》第 2 册第 1 课。",
    ),
    "07": dict(
        pid="thai-book-jichu-07-taxi", pub_title="泰国问路这样说", comp="TextbookTaxi", src="b07.tsx", plan=plan_n("route", "问路四句（第 2 册第 7 课原声）", "t", 4),
        title="泰国问路，这样说", cover=("泰国问路", "这样说"), slug="thai_book_jichu_07",
        book_label="第 2 册 · 第 7 课",
        lines={
            "hook": "在泰国问路，这四句就够了。",
            "t0": "先问，银行在哪儿。",
            "t1": "沿着这条路直走。",
            "t2": "看到红绿灯就左转。",
            "t3": "到三岔路口右转。",
            "book": "问路在基础泰语第二册第七课，附原声。",
        },
        clips={"th_t0": (2, "07.mp3", 14.13, 16.16), "th_t1": (2, "07.mp3", 42.92, 45.02),
               "th_t2": (2, "07.mp3", 53.26, 55.74), "th_t3": (2, "07.mp3", 100.49, 102.71)},
        crops={"c0": (2, 63, (40, 395, 960, 440)), "c1": (2, 63, (40, 750, 995, 795)),
               "c2": (2, 63, (40, 800, 995, 845)), "c3": (2, 64, (40, 30, 960, 85)), "lesson": (2, 63, (0, 0, 1000, 1000))},
        data={"steps": [{"th": "ธนาคารกรุงเทพอยู่ที่ไหนคะ", "zh": "盘谷银行在哪儿？", "kind": "ask", "crop": "c0"},
                        {"th": "คุณเดินตรงไปตามถนนนี้", "zh": "沿这条路直走", "kind": "up", "crop": "c1"},
                        {"th": "พอคุณเห็นไฟจราจรก็เลี้ยวซ้าย", "zh": "见红绿灯左转", "kind": "left", "crop": "c2"},
                        {"th": "พอถึงสามแยกก็เลี้ยวขวา", "zh": "到三岔路口右转", "kind": "right", "crop": "c3"}]},
        copy="泰国问路 4 句：อยู่ที่ไหน 在哪儿 / เดินตรงไป 直走 / เลี้ยวซ้าย 左转 / เลี้ยวขวา 右转。\n"
             "原句与原声取自《基础泰语》第 2 册第 7 课。",
    ),
    "10": dict(
        pid="thai-book-jichu-10-dining", pub_title="泰国吃饭这5句够用", comp="TextbookDining", src="b10.tsx", plan=plan_n("receipt", "一顿饭五句（第 2 册第 5 课原声）", "d", 5),
        title="泰国吃饭，这5句够用", cover=("泰国吃饭", "这5句够用"), slug="thai_book_jichu_10",
        book_label="第 2 册 · 第 5 课",
        lines={
            "hook": "在泰国吃饭，从点菜到吃饱，这五句全用得上。",
            "d0": "问有什么吃的。",
            "d1": "请人尝一尝。",
            "d2": "夸一句，真好吃。",
            "d3": "问人吃饱了吗。",
            "d4": "吃饱了。",
            "book": "饮食是基础泰语第二册第五课，书上还有一整页菜名分类词汇，附原声音频。",
        },
        clips={"th_d0": (2, "05.mp3", 32.49, 33.89), "th_d1": (2, "05.mp3", 82.98, 84.27),
               "th_d2": (2, "05.mp3", 80.83, 82.55), "th_d3": (2, "05.mp3", 121.90, 123.08),
               "th_d4": (2, "05.mp3", 123.79, 124.78)},
        crops={"c0": (2, 42, (40, 532, 960, 582)), "c1": (2, 42, (40, 905, 960, 955)),
               "c3": (2, 43, (40, 114, 960, 164)), "c4": (2, 43, (40, 168, 960, 216)),
               "lesson": (2, 44, (0, 0, 1000, 1000))},
        data={"lines": [{"th": "มีอะไรทานบ้างคะ", "zh": "有什么吃的？", "crop": "c0"},
                        {"th": "คุณลองชิมดูสิครับ", "zh": "你尝尝", "crop": "c1"},
                        {"th": "หมูพะโล้นี่อร่อยจริงๆ", "zh": "这卤肉真好吃", "crop": "c1"},
                        {"th": "คุณอิ่มหรือเปล่าครับ", "zh": "你吃饱了吗？", "crop": "c3"},
                        {"th": "อิ่มแล้วค่ะ", "zh": "吃饱了", "crop": "c4"}]},
        copy="泰国吃饭 5 句：มีอะไรทานบ้าง 有什么吃的 / ลองชิมดู 尝尝 / อร่อยจริงๆ 真好吃 / อิ่มหรือเปล่า 饱了吗 / อิ่มแล้ว 吃饱了。\n"
             "原句与原声取自《基础泰语》第 2 册第 5 课。",
    ),
    "06": dict(
        pid="thai-book-jichu-06-numbers", pub_title="泰语数字1到10", comp="TextbookNumbers", src="b06.tsx", plan=plan06,
        title="泰语数字1到10", cover=("泰语数字", "1到10"), slug="thai_book_jichu_06",
        book_label="第 2 册 · 第 2 课",
        lines={
            "hook": "泰语数字一到十，还有泰文写法。",
            "n_intro": "一到十，先听原声。",
            "n_again": "跟着读。",
            "use": "课文里：一共四口人。",
            "book": "数字在基础泰语第二册第二课，附原声。",
        },
        clips=dict({f"th_n{i}": (2, "02.mp3", s, e) for i, (s, e) in enumerate(NUM_T)},
                   th_use=(2, "02.mp3", 29.06, 30.75)),
        crops={"table": (2, 11, (110, 1050, 885, 1380)), "table10": (2, 12, (135, 40, 860, 375)),
               "use": (2, 10, (40, 372, 960, 415)), "lesson": (2, 10, (0, 0, 1000, 1000))},
        data={"nums": [{"n": i + 1, "thd": dd, "th": w} for i, (dd, w) in enumerate(zip(
                  ["๑", "๒", "๓", "๔", "๕", "๖", "๗", "๘", "๙", "๑๐"],
                  ["หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า", "สิบ"]))],
              "use": {"th": "มีทั้งหมด ๔ คนครับ", "zh": "一共有四口人",
                      "parts": [["มี", "有"], ["ทั้งหมด", "一共"], ["๔", "四"], ["คน", "人"], ["ครับ", "礼貌"]]}},
        copy="泰语数字 1–10：หนึ่ง สอง สาม สี่ ห้า หก เจ็ด แปด เก้า สิบ，泰文数字写作 ๑–๑๐。\n"
             "课文例句 มีทั้งหมด ๔ คน 一共四口人。读音与例句取自《基础泰语》第 2 册第 2 课。",
    ),
    "14": dict(
        pid="thai-book-jichu-14-family", pub_title="泰语哥哥姐姐两个词搞定", comp="TextbookFamily", src="b14.tsx", plan=plan_n("tree", "家庭称呼六个（第 2 册第 2 课原声）", "f", 6),
        title="泰语哥哥姐姐，两个词搞定", cover=("哥哥姐姐", "两个词搞定"), slug="thai_book_jichu_14", series_new=True,
        book_label="第 2 册 · 第 2 课",
        lines={
            "hook": "泰语的哥哥姐姐弟弟妹妹，只要记两个词。",
            "f0": "爸爸。", "f1": "妈妈。",
            "f2": "哥哥，年长加男。", "f3": "姐姐，年长加女。",
            "f4": "弟弟，年幼加男。", "f5": "妹妹，年幼加女。",
            "book": "家庭称呼在基础泰语第二册第二课，分类词汇整整一页，附原声。",
        },
        clips={"th_f0": (2, "02.mp3", 176.93, 177.52), "th_f1": (2, "02.mp3", 179.19, 179.86),
               "th_f2": (2, "02.mp3", 183.77, 184.87), "th_f3": (2, "02.mp3", 181.24, 182.33),
               "th_f4": (2, "02.mp3", 188.71, 189.86), "th_f5": (2, "02.mp3", 186.10, 187.27)},
        crops={"vocab": (2, 11, (60, 585, 920, 965)), "lesson": (2, 10, (0, 0, 1000, 1000))},
        data={"members": [{"th": "พ่อ", "zh": "爸爸", "a": "", "b": ""}, {"th": "แม่", "zh": "妈妈", "a": "", "b": ""},
                          {"th": "พี่ชาย", "zh": "哥哥", "a": "พี่", "b": "ชาย"}, {"th": "พี่สาว", "zh": "姐姐", "a": "พี่", "b": "สาว"},
                          {"th": "น้องชาย", "zh": "弟弟", "a": "น้อง", "b": "ชาย"}, {"th": "น้องสาว", "zh": "妹妹", "a": "น้อง", "b": "สาว"}]},
        copy="泰语兄弟姐妹两个词就够：พี่ 年长 / น้อง 年幼 + ชาย 男 / สาว 女。\n"
             "พี่ชาย 哥哥 / พี่สาว 姐姐 / น้องชาย 弟弟 / น้องสาว 妹妹。原声取自《基础泰语》第 2 册第 2 课。",
    ),
    "15": dict(
        pid="thai-book-jichu-15-weekday", pub_title="泰语星期几这样问", comp="TextbookWeekday", src="b15.tsx", plan=plan_n("cal", "星期几四句（第 2 册第 3 课原声）", "w", 4),
        title="泰语星期几，这样问", cover=("泰语星期几", "这样问"), slug="thai_book_jichu_15", series_new=True,
        book_label="第 2 册 · 第 3 课",
        lines={
            "hook": "泰语问今天星期几，这四句就够了。",
            "w0": "今天星期几？", "w1": "今天星期四。",
            "w2": "星期一到星期五上课。", "w3": "星期六、星期天休息。",
            "book": "年月日在基础泰语第二册第三课，书上有星期和月份的整张表，附原声。",
        },
        clips={"th_w0": (2, "03.mp3", 34.91, 36.59), "th_w1": (2, "03.mp3", 39.12, 41.15),
               "th_w2": (2, "03.mp3", 87.33, 89.35), "th_w3": (2, "03.mp3", 89.91, 92.18)},
        crops={"dlg": (2, 20, (30, 270, 960, 1060)), "lesson": (2, 20, (0, 0, 1000, 1000))},
        data={"lines": [{"th": "วันนี้วันอะไรคะ", "zh": "今天星期几？", "days": []},
                        {"th": "วันนี้วันพฤหัสครับ", "zh": "今天星期四", "days": [3]},
                        {"th": "เรียนวันจันทร์ถึงวันศุกร์ครับ", "zh": "周一到周五上课", "days": [0, 1, 2, 3, 4]},
                        {"th": "วันเสาร์และวันอาทิตย์หยุดครับ", "zh": "周六周日休息", "days": [5, 6]}],
              "week": [["จันทร์", "一"], ["อังคาร", "二"], ["พุธ", "三"], ["พฤหัส", "四"], ["ศุกร์", "五"], ["เสาร์", "六"], ["อาทิตย์", "日"]]},
        copy="泰语问星期几：วันนี้วันอะไร？今天星期四 วันนี้วันพฤหัส。\n"
             "周一到周五上课 เรียนวันจันทร์ถึงวันศุกร์。原句与原声取自《基础泰语》第 2 册第 3 课。",
    ),
    "16": dict(
        pid="thai-book-jichu-16-time", pub_title="泰语报时晚上另有叫法", comp="TextbookTime", src="b16.tsx", plan=plan_n("clock", "几点了四句（第 2 册第 4 课原声）", "c", 4),
        title="泰语报时，晚上另有叫法", cover=("泰语报时", "晚上另有叫法"), slug="thai_book_jichu_16", series_new=True,
        book_label="第 2 册 · 第 4 课",
        lines={
            "hook": "泰语报时，白天和晚上的钟点，叫法不一样。",
            "c0": "现在几点了？", "c1": "再过十分钟八点。",
            "c2": "大约晚上十点，晚上的钟点另有叫法。", "c3": "要半夜十二点才睡。",
            "book": "泰语报时在基础泰语第二册第四课，课文是一整张作息时间表，附原声。",
        },
        clips={"th_c0": (2, "04.mp3", 19.09, 20.73), "th_c1": (2, "04.mp3", 22.26, 24.05),
               "th_c2": (2, "04.mp3", 71.92, 73.30), "th_c3": (2, "04.mp3", 92.24, 93.57)},
        crops={"dlg": (2, 30, (30, 270, 960, 960)), "lesson": (2, 30, (0, 0, 1000, 1000))},
        data={"lines": [{"th": "ตอนนี้กี่โมงแล้วคะ", "zh": "现在几点了？", "h": 7, "m": 50},
                        {"th": "อีก ๑๐ นาที ๘ โมง", "zh": "再过10分钟8点", "h": 8, "m": 0},
                        {"th": "ประมาณ ๔ ทุ่มค่ะ", "zh": "大约晚上10点", "h": 22, "m": 0},
                        {"th": "ต้องนอนเที่ยงคืนค่ะ", "zh": "半夜12点才睡", "h": 24, "m": 0}]},
        copy="泰语报时：ตอนนี้กี่โมงแล้ว 现在几点了；白天用 โมง，晚上用 ทุ่ม，晚上十点是 สี่ทุ่ม，半夜十二点 เที่ยงคืน。\n"
             "原句与原声取自《基础泰语》第 2 册第 4 课。",
    ),
    "17": dict(
        pid="thai-book-jichu-17-bargain", pub_title="泰国买水果这样讲价", comp="TextbookBargain", src="b17.tsx", plan=plan_n("stall", "买榴莲讲价五句（第 2 册第 6 课原声）", "b", 5),
        title="泰国买水果，这样讲价", cover=("泰国买水果", "这样讲价"), slug="thai_book_jichu_17", series_new=True,
        book_label="第 2 册 · 第 6 课",
        lines={
            "hook": "在泰国买水果，从问价到讲价，五句话。",
            "b0": "榴莲怎么卖？", "b1": "一公斤四十七铢。",
            "b2": "一共多少钱？", "b3": "便宜点行吗？", "b4": "那就二百四吧。",
            "book": "购物在基础泰语第二册第六课，买水果、买衣服两段对话，附原声。",
        },
        clips={"th_b0": (2, "06.mp3", 15.50, 17.31), "th_b1": (2, "06.mp3", 20.82, 22.78),
               "th_b2": (2, "06.mp3", 43.50, 44.69), "th_b3": (2, "06.mp3", 48.75, 50.09),
               "th_b4": (2, "06.mp3", 51.18, 53.05)},
        crops={"dlg": (2, 53, (30, 300, 980, 770)), "lesson": (2, 53, (0, 0, 1000, 1000))},
        data={"lines": [{"th": "ทุเรียนนี้ขายอย่างไรคะ", "zh": "榴莲怎么卖？", "price": ""},
                        {"th": "กิโลละ ๔๗ บาทค่ะ", "zh": "一公斤47铢", "price": "47/kg"},
                        {"th": "ทั้งหมดเท่าไรคะ", "zh": "一共多少？", "price": "248"},
                        {"th": "ลดหน่อยได้ไหมคะ", "zh": "便宜点行吗？", "price": "248"},
                        {"th": "๒๔๐ ก็แล้วกัน", "zh": "那就240吧", "price": "240"}]},
        copy="泰国买水果讲价 5 句：ขายอย่างไร 怎么卖 / กิโลละ…บาท 一公斤…铢 / ทั้งหมดเท่าไร 一共多少 / ลดหน่อยได้ไหม 便宜点 / …ก็แล้วกัน 那就…吧。\n"
             "原句与原声取自《基础泰语》第 2 册第 6 课。",
    ),
    "18": dict(
        pid="thai-book-jichu-18-phone", pub_title="泰语打电话这4句", comp="TextbookPhone", src="b18.tsx", plan=plan_n("call", "打电话四句（第 2 册第 9 课原声）", "p", 4),
        title="泰语打电话，这4句", cover=("泰语打电话", "这4句"), slug="thai_book_jichu_18", series_new=True,
        book_label="第 2 册 · 第 9 课",
        lines={
            "hook": "用泰语打电话，转分机、找人，这四句。",
            "p0": "请转分机。", "p1": "请稍等。",
            "p2": "我想找某某。", "p3": "我就是。",
            "book": "打电话在基础泰语第二册第九课，两段电话对话，附原声。",
        },
        clips={"th_p0": (2, "09.mp3", 21.04, 23.68), "th_p1": (2, "09.mp3", 41.71, 43.37),
               "th_p2": (2, "09.mp3", 94.92, 97.22), "th_p3": (2, "09.mp3", 98.11, 100.27)},
        crops={"dlg": (2, 87, (30, 380, 980, 1120)), "lesson": (2, 87, (0, 0, 1000, 1000))},
        data={"lines": [{"th": "กรุณาต่อ ๖๒๖๙ ค่ะ", "zh": "请转6269", "who": "me"},
                        {"th": "กรุณารอสักครู่นะคะ", "zh": "请稍等", "who": "op"},
                        {"th": "ผมขอพูดกับคุณสุภาพรครับ", "zh": "我找苏帕蓬", "who": "me"},
                        {"th": "ดิฉันสุภาพรกำลังพูดค่ะ", "zh": "我就是苏帕蓬", "who": "op"}]},
        copy="泰语打电话 4 句：กรุณาต่อ 请转 / กรุณารอสักครู่ 请稍等 / ขอพูดกับ… 我找… / …กำลังพูด 我就是。\n"
             "原句与原声取自《基础泰语》第 2 册第 9 课。",
    ),
    "19": dict(
        pid="thai-book-jichu-19-sick", pub_title="在泰国生病这5句", comp="TextbookSick", src="b19.tsx", plan=plan_n("chart", "生病五句（第 2 册第 10 课原声）", "s", 5),
        title="在泰国生病，这5句", cover=("在泰国生病", "这5句"), slug="thai_book_jichu_19", series_new=True,
        book_label="第 2 册 · 第 10 课",
        lines={
            "hook": "在泰国生病了，这五句话一定要会。",
            "s0": "你怎么了？", "s1": "我不太舒服，感冒了。", "s2": "得赶紧去看医生。",
            "s3": "发烧吗？", "s4": "头很疼吗？",
            "book": "疾病在基础泰语第二册第十课，两段对话，附原声。",
        },
        clips={"th_s0": (2, "10.mp3", 15.73, 17.01), "th_s1": (2, "10.mp3", 22.81, 25.06),
               "th_s2": (2, "10.mp3", 27.23, 28.74), "th_s3": (2, "10.mp3", 39.48, 40.54),
               "th_s4": (2, "10.mp3", 85.48, 86.67)},
        crops={"dlg": (2, 100, (30, 330, 980, 745)), "lesson": (2, 100, (0, 0, 1000, 1000))},
        data={"lines": [{"th": "คุณเป็นอะไรไป", "zh": "你怎么了？", "tag": "问"},
                        {"th": "ดิฉันไม่ค่อยสบาย เป็นหวัดค่ะ", "zh": "不太舒服，感冒了", "tag": "感冒"},
                        {"th": "ต้องรีบไปหาหมอสิคะ", "zh": "得赶紧看医生", "tag": "就医"},
                        {"th": "มีไข้ไหมคะ", "zh": "发烧吗？", "tag": "发烧"},
                        {"th": "ปวดหัวมากไหม", "zh": "头很疼吗？", "tag": "头疼"}]},
        copy="在泰国生病 5 句：เป็นอะไรไป 怎么了 / ไม่ค่อยสบาย 不太舒服 / เป็นหวัด 感冒 / หาหมอ 看医生 / มีไข้ 发烧 / ปวดหัว 头疼。\n"
             "原句与原声取自《基础泰语》第 2 册第 10 课。",
    ),
    "11": dict(
        pid="thai-book-jichu-11-high", pub_title="泰语高辅音一共10个", comp="TextbookHigh", src="b11.tsx", plan=plan11,
        title="泰语高辅音，一共10个", cover=("泰语高辅音", "一共10个"), slug="thai_book_jichu_11", series_new=True,
        book_label="第 1 册 · 第 4 课",
        lines={
            "hook": "泰语的高辅音，一共十个，单念都往上扬。",
            "intro": "先听书里的原声。",
            "again": "跟着读。",
            "rule": "书上说：中辅音单念发第一声，高辅音单念发第五声。",
            "book": "高辅音在基础泰语第一册第四课，一到四册，附原声。",
        },
        clips={f"th_h{i}": (1, "U01-04.mp3", s, e) for i, (s, e) in enumerate(HIGH_T)},
        crops={"row": (1, 43, (135, 800, 890, 905)), "rule": (1, 43, (60, 900, 960, 1000)),
               "lesson": (1, 43, (0, 0, 1000, 1000))},
        data={"letters": HIGH10},
        copy="泰语 10 个高辅音：ข ฉ ถ ฐ ผ ฝ ศ ษ ส ห。书上规则：中辅音单念发第一声，高辅音发第五声。\n"
             "原声取自《基础泰语》第 1 册第 4 课。",
    ),
    "20": dict(
        pid="thai-book-jichu-20-seasons", pub_title="泰国一年只有三个季节", comp="TextbookSeasons", src="b20.tsx", plan=plan_n("wheel", "季节四句（第 2 册第 12 课原声）", "q", 4),
        title="泰国一年只有三个季节", cover=("泰国一年", "只有三个季节"), slug="thai_book_jichu_20", series_new=True,
        book_label="第 2 册 · 第 12 课",
        lines={
            "hook": "泰国一年只有三个季节，是哪三个？",
            "q0": "泰国一年有几个季节？", "q1": "有三个。",
            "q2": "热季、雨季和凉季。", "q3": "中国呢？四个。",
            "book": "季节在基础泰语第二册第十二课，附原声。",
        },
        clips={"th_q0": (2, "12.mp3", 35.01, 37.62), "th_q1": (2, "12.mp3", 38.88, 40.20),
               "th_q2": (2, "12.mp3", 41.69, 45.60), "th_q3": (2, "12.mp3", 95.04, 96.02)},
        crops={"dlg": (2, 124, (30, 350, 980, 740)), "lesson": (2, 124, (0, 0, 1000, 1000))},
        data={"lines": [{"th": "เมืองไทยปีหนึ่งมีกี่ฤดูคะ", "zh": "泰国一年几个季节？", "lit": []},
                        {"th": "มีสามฤดูค่ะ", "zh": "有三个", "lit": [0, 1, 2]},
                        {"th": "ฤดูร้อน ฤดูฝน และฤดูหนาว", "zh": "热季、雨季和凉季", "lit": [0, 1, 2]},
                        {"th": "สี่ฤดูค่ะ", "zh": "中国：四个", "lit": []}],
              "thai": [["ฤดูร้อน", "热季", "#ff7b2e"], ["ฤดูฝน", "雨季", "#2f7dd1"], ["ฤดูหนาว", "凉季", "#7fb7a4"]],
              "china": [["ฤดูใบไม้ผลิ", "春", "#e88bb4"], ["ฤดูร้อน", "夏", "#ff7b2e"], ["ฤดูใบไม้ร่วง", "秋", "#d99a3c"], ["ฤดูหนาว", "冬", "#7fa7c9"]]},
        copy="泰国一年三季：ฤดูร้อน 热季 / ฤดูฝน 雨季 / ฤดูหนาว 凉季；中国是 สี่ฤดู 四季。\n"
             "原句与原声取自《基础泰语》第 2 册第 12 课。",
    ),
    "12": dict(
        pid="thai-book-jichu-12-low", pub_title="泰语辅音高低成对", comp="TextbookLow", src="b12.tsx", plan=plan12,
        title="泰语辅音，高低成对", cover=("泰语辅音", "高低成对"), slug="thai_book_jichu_12", series_new=True,
        book_label="第 1 册 · 第 5 课",
        lines={
            "hook": "泰语里很多辅音成对，读音一样，声调不同。",
            "intro": "上面是高辅音，下面是低辅音，听书里的原声。",
            "rule": "书上说：低辅音单念，声调和中辅音一样，高辅音单念发第五声。",
            "book": "低辅音在基础泰语第一册第五课，一到四册，附原声。",
        },
        clips=dict({f"th_hi{i}": (1, "U01-04.mp3", h[0], h[1]) for i, (_, _, h, _, _) in enumerate(PAIRS)},
                   **{f"th_lo{i}": (1, "U01-05.mp3", l[0], l[1]) for i, (_, _, _, l, _) in enumerate(PAIRS)}),
        crops={"row": (1, 52, (140, 890, 885, 970)), "pairs": (1, 52, (60, 990, 960, 1310)),
               "lesson": (1, 52, (0, 0, 1000, 1000))},
        data={"pairs": [{"hi": h, "lo": l, "snd": snd} for h, l, _, _, snd in PAIRS]},
        copy="泰语高低辅音成对：ข/ค、ฉ/ช、ส/ซ、ผ/พ、ฝ/ฟ —— 读音相同，单念时高辅音发第五声，低辅音和中辅音一样。\n"
             "原声取自《基础泰语》第 1 册第 4、5 课。",
    ),
    "13": dict(
        pid="thai-book-jichu-13-finals", pub_title="泰语尾辅音五种收尾", comp="TextbookFinals", src="b13.tsx", plan=plan13,
        title="泰语尾音，一个กา五种收尾", cover=("泰语尾辅音", "五种收尾"), slug="thai_book_jichu_13", series_new=True,
        book_label="第 1 册 · 第 9 课",
        lines={
            "hook": "泰语的尾辅音，同一个音，换个收尾就是另一个字。",
            "base": "先记住这个音。",
            "e0": "收在昂。", "e1": "收在安。", "e2": "收在闭嘴。", "e3": "收在衣。", "e4": "收在乌。",
            "book": "尾辅音在基础泰语第一册第九课，书上有一整张拼读表，附原声。",
        },
        clips={"th_base": (1, "U01-03.mp3", 12.06, 12.76), "th_e0": (1, "U01-09.mp3", 19.69, 20.40), "th_e1": (1, "U01-09.mp3", 42.20, 42.98),
               "th_e2": (1, "U01-09.mp3", 60.45, 61.29), "th_e3": (1, "U01-09.mp3", 71.19, 71.75),
               "th_e4": (1, "U01-09.mp3", 87.89, 88.41)},
        crops={"table": (1, 97, (150, 960, 890, 1310)), "head": (1, 97, (60, 290, 960, 480)),
               "lesson": (1, 97, (0, 0, 1000, 1000))},
        data={"finals": [{"f": "ง", "w": "กาง", "mae": "แม่กง", "snd": "-ng"}, {"f": "น", "w": "กาน", "mae": "แม่กน", "snd": "-n"},
                         {"f": "ม", "w": "กาม", "mae": "แม่กม", "snd": "-m"}, {"f": "ย", "w": "กาย", "mae": "แม่เกย", "snd": "-i"},
                         {"f": "ว", "w": "กาว", "mae": "แม่เกอว", "snd": "-o"}]},
        copy="泰语尾辅音：กา + ง/น/ม/ย/ว = กาง กาน กาม กาย กาว（แม่กง แม่กน แม่กม แม่เกย แม่เกอว）。\n"
             "拼读与原声取自《基础泰语》第 1 册第 9 课。",
    ),
}


async def build(num: str, render: bool) -> None:
    ep = EPISODES[num]
    proj = REPO / "projects" / ep["pid"]
    if not proj.exists():
        init_project(ep["pid"], title=f'{ep["title"]}（基础泰语带货 {num}）', pipeline_type="animated-explainer")
    pub = proj / "composition/public"
    for d in ("audio", "fonts", "app", "img", "book"):
        (pub / d).mkdir(parents=True, exist_ok=True)
    A = proj / "assets/audio"
    A.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE / "composition/public/fonts/Sarabun-Bold.ttf", pub / "fonts/Sarabun-Bold.ttf")
    shutil.copy2(TEMPLATE / "assets/music/background.mp3", pub / "audio/background.mp3")
    shutil.copy2(ALPHA_ICON, pub / "app/alpha_icon.png")
    shutil.copy2(Path("/Users/zhenyusong/projects/lang1000/apps/thai1000/playstore/icon-512.png"), pub / "app/qianci_icon.png")
    # 书影一律用《基础泰语》PDF 封面拼的图 —— 商品主图是《新编基础泰语》，不能出现（2026-10-12 用户指令）
    shutil.copy2(REPO / "projects/_shared/textbook/jichu_books.png", pub / "img/books.png")
    for name, (book, page, box) in ep["crops"].items():
        crop_page(book, page, box, pub / "book" / f"{name}.png")
    shutil.copy2(SERIES_SRC / "index.tsx", proj / "composition/index.tsx")
    shutil.copy2(SERIES_SRC / "Common.tsx", proj / "composition/Common.tsx")
    shutil.copy2(SERIES_SRC / ep["src"], proj / "composition/Composition.tsx")
    (proj / "composition/Root.tsx").write_text(
        'import {Composition} from "remotion";\nimport {Scene,calculateMetadata,SceneProps} from "./Composition";\n'
        f'export const Root:React.FC=()=><Composition id="{ep["comp"]}" component={{Scene}} durationInFrames={{1800}} '
        'fps={30} width={1080} height={1920} defaultProps={{} as SceneProps} calculateMetadata={calculateMetadata}/>;\n')

    L = dict(ep["lines"], cta=CTA, outro=OUTRO)
    BA = proj / "assets/book_audio"
    BA.mkdir(parents=True, exist_ok=True)
    for old in BA.glob("*.mp3") if BA.exists() else []:
        if old.stem not in ep["clips"]:
            old.unlink()
    # 配音按文件名缓存；文案改了必须重合成，否则会悄悄沿用旧文案的音频
    import json
    manifest = A / ".texts.json"
    old_texts = json.loads(manifest.read_text()) if manifest.exists() else {}
    for key, text in L.items():
        if old_texts.get(key) != text and (A / f"{key}.mp3").exists():  # 没记录过也算变了
            (A / f"{key}.mp3").unlink()
        await synth(A / f"{key}.mp3", text, ZH)
    manifest.write_text(json.dumps(L, ensure_ascii=False, indent=1))
    for key, (book, mp3, s, e) in ep["clips"].items():
        cut_clip(book, mp3, s, e, BA / f"{key}.mp3")
    for f in list(A.glob("*.mp3")) + list(BA.glob("*.mp3")):
        shutil.copy2(f, pub / "audio" / f.name)
    d = {f.stem: dur(f) for f in list(A.glob("*.mp3")) + list(BA.glob("*.mp3"))}

    tl = TL(d)
    ep["plan"](tl, L)
    tail(tl, L)
    for sc in tl.scenes:
        if sc["id"] == "book":
            sc["label"] = f'教材：基础泰语 {ep.get("book_label", "第 1 册 · 第 1 课")}'
    total = round(tl.t * FPS)
    props = {
        "fps": FPS, "totalFrames": total, "totalSeconds": total / FPS, "num": num,
        "cover": list(ep["cover"]), "data": ep["data"], "marks": tl.marks,
        "scenes": tl.scenes, "audio": tl.audio,
        "speak": [[a["at"], round(a["at"] + d[a["file"][:-4]], 3)] for a in tl.audio],
        "bgm": {"file": "background.mp3", "volume": 0.05},
        "review_timeline": [{"id": x["id"], "label": x["label"], "start": x["start"], "end": x["end"],
                             "title": x["label"], "text": x["text"], "credit": "书页与原声：《基础泰语》PDF + MP3"} for x in tl.scenes],
    }
    save(proj / "composition/props.json", props)
    save(proj / "artifacts/props.json", props)
    save(proj / "artifacts/script.json", {
        "version": "1.0", "title": ep["title"], "total_duration_seconds": props["totalSeconds"],
        "sections": [{"id": x["id"], "label": x["label"], "text": x["text"], "start_seconds": x["start"],
                      "end_seconds": x["end"], "speaker_directions": "中文女声讲解；泰语用书配套 MP3 原声，读两遍 + 跟读空档。"}
                     for x in tl.scenes],
        "metadata": {"language": "zh+th", "kind": "带货·图书", "source": "书本素材版",
                     "book_clips": {k: {"book": b, "file": f, "start": s, "end": e} for k, (b, f, s, e) in ep["clips"].items()},
                     "book_pages": {k: {"book": b, "pdf_page": p, "box_at_1000w": list(x)} for k, (b, p, x) in ep["crops"].items()},
                     "tts": {"engine": "edge", "zh": ZH}},
    })
    save(proj / "artifacts/publish.json", {
        "series_id": 1, "sub_series": "教材带货", "slug": ep["slug"],
        "title": ep.get("pub_title", ep["title"]), "wechat_copy": ep.get("pub_title", ep["title"]),
        "idea_notes": "【带货】商品：《基础泰语》1–4 册（出版社直营店）；发布时挂小黄车。",
        "publish_copy": ep["copy"] + "\n背单词用「泰语千词」，练字母用「学泰文字母」。\n\n" + TAGS,
        "credits": "书页与原声：《基础泰语》；配音与剪辑：泰语千词。",
    })
    print(ep["pid"], f'{props["totalSeconds"]:.1f}s', flush=True)

    if render:
        renders = proj / "renders"
        renders.mkdir(exist_ok=True)
        out = renders / f"book-v{len(list(renders.glob('book-v*.mp4'))) + 1}.mp4"
        subprocess.run(["npx", "remotion", "render", str(proj / "composition/index.tsx"), ep["comp"], str(out),
                        f"--props={proj / 'composition/props.json'}", f"--public-dir={pub}", "--log=error"],
                       cwd=REPO / "remotion-composer", check=True)
        print("  rendered", out.relative_to(REPO), flush=True)


async def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    nums = list(EPISODES) if (not args or args == ["all"]) else args
    for n in nums:
        await build(n, "--render" in sys.argv)


if __name__ == "__main__":
    asyncio.run(main())
