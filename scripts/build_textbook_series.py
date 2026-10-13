"""《新编基础泰语》带货系列 02–05。01 见 build_textbook_demo.py（已入库 video_id=844）。

每集的创意组件各写一份（scripts/textbook_series/epNN.tsx），共用的只有引擎与系列身份
（Common.tsx：品牌行 / 场景淡入淡出 / 音轨 / 片尾小黄车 + 学泰文字母）。
时间轴一律全片绝对秒；泰语例句全部取自 thai1000 词库（例句真子串或词条本身）。

    python3 scripts/build_textbook_series.py 02 03     # 合成配音 + props
    python3 scripts/build_textbook_series.py all --render
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

TEMPLATE = REPO / "projects/thai-1000-idiom-01-diao"
SERIES_SRC = REPO / "scripts/textbook_series"
BOOKS_PNG = REPO / "projects/thai-book-jichu-01-consonants/composition/public/img/books.png"
ALPHA_ICON = Path("/Users/zhenyusong/projects/AlphabetLearningFramework/apps/thai/ios/Runner/"
                  "Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png")
FPS = 30
ZH = ("zh-CN-XiaoxiaoNeural", "+8%")
TH_F = ("th-TH-PremwadeeNeural", "-8%")
TH_M = ("th-TH-NiwatNeural", "-8%")  # 句末带 ครับ 的用男声
CTA = "想系统学泰语，点左下角小黄车。"
OUTRO = "跟着书练字母，就用学泰文字母。"
TAGS = "#泰语 #泰语学习 #泰语入门 #泰语教材"


class TL:
    def __init__(self, d: dict[str, float]):
        self.d, self.t = d, 0.0
        self.audio, self.scenes, self.marks = [], [], {}
        self._open: tuple[str, float, str, str] | None = None

    def say(self, key: str, pre: float = 0.0, post: float = 0.0, mark: str | None = None) -> float:
        self.t += pre
        at = round(self.t, 3)
        self.audio.append({"file": f"{key}.mp3", "at": at})
        if mark:
            self.marks[mark] = at
        self.t = at + self.d[key] + post
        return at

    def drill(self, key: str, mark: str) -> None:
        """读两遍 + 跟读空档（≈ 词长 + 0.55）。"""
        self.say(key, pre=0.3, mark=f"{mark}_a")
        self.say(key, pre=0.35, mark=f"{mark}_b")
        self.marks[f"{mark}_f"] = round(self.t, 3)
        self.t += self.d[key] + 0.55
        self.marks[f"{mark}_e"] = round(self.t, 3)

    def gap(self, s: float) -> None:
        self.t += s

    def begin(self, sid: str, label: str, text: str) -> None:
        if self._open:
            self.end()
        self._open = (sid, self.t, label, text)

    def end(self) -> None:
        sid, s, label, text = self._open
        self.scenes.append({"id": sid, "start": round(s, 3), "end": round(self.t, 3), "label": label, "text": text})
        self._open = None


# ---------------------------------------------------------------- 02 声调
def plan02(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 一个音三个意思", L["hook"])
    tl.say("hook", post=0.45)
    tl.begin("tones", "五个声调，先听三个", L["tones"])
    tl.say("tones", pre=0.15, post=0.3)
    tl.begin("trio", "มา / ม้า / หมา", L["w0"] + L["w1"] + L["w2"])
    for i in range(3):
        tl.say(f"w{i}", pre=0.25, mark=f"w{i}")
        tl.drill(f"th_w{i}", f"w{i}")
    tl.begin("pair", "ใกล้ / ไกล：近与远", L["pair"])
    tl.say("pair", pre=0.2, post=0.1)
    tl.drill("th_p0", "p0")
    tl.drill("th_p1", "p1")
    tl.begin("quiz", "听音选词", L["quiz"] + L["answer"])
    tl.say("quiz", pre=0.2, post=0.25)
    tl.say("th_w2", mark="q")
    tl.gap(1.3)
    tl.say("answer", mark="ans", post=0.4)


# ---------------------------------------------------------------- 03 会话
def plan03(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 到泰国第一天", L["hook"])
    tl.say("hook", post=0.45)
    tl.begin("chat", "五句会话", "".join(L[f"s{i}"] for i in range(5)))
    for i in range(5):
        tl.say(f"s{i}", pre=0.25, mark=f"s{i}")
        tl.drill(f"th_s{i}", f"s{i}")


# ---------------------------------------------------------------- 04 路线图
def plan04(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 零基础到读课文", L["hook"])
    tl.say("hook", post=0.4)
    tl.begin("stairs", "1→4 册路线", "".join(L[f"k{i}"] for i in range(4)))
    for i in range(4):
        tl.say(f"k{i}", pre=0.25, mark=f"k{i}")
        tl.drill(f"th_k{i}", f"k{i}")


# ---------------------------------------------------------------- 05 三步
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
    tl.begin("check", "对：对照文字", L["st2"])
    tl.say("st2", pre=0.15, post=0.2, mark="st2")
    tl.say("th_x", pre=0.2, mark="c1", post=0.3)
    tl.say("sum", pre=0.2, mark="sum", post=0.3)


# ---------------------------------------------------------------- 06–10 共用：一句中文引子 + 读两遍跟读
def plan_list(tl: TL, L: dict, sid: str, label: str, prefix: str, n: int) -> None:
    tl.begin(sid, label, "".join(L[f"{prefix}{i}"] for i in range(n)))
    for i in range(n):
        tl.say(f"{prefix}{i}", pre=0.25, mark=f"{prefix}{i}")
        tl.drill(f"th_{prefix}{i}", f"{prefix}{i}")


def plan06(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 数字 1 到 10", L["hook"])
    tl.say("hook", post=0.4)
    tl.begin("count", "1–10 先听一遍，再跟读", L["n_intro"] + L["n_again"])
    tl.say("n_intro", pre=0.15, post=0.25)
    for i in range(10):
        tl.say(f"th_n{i}", mark=f"p{i}", post=0.22)
    tl.say("n_again", pre=0.3, post=0.25, mark="again")
    for i in range(10):
        tl.say(f"th_n{i}", mark=f"n{i}_a")
        tl.marks[f"n{i}_f"] = round(tl.t, 3)
        tl.gap(tl.d[f"th_n{i}"] + 0.4)
        tl.marks[f"n{i}_e"] = round(tl.t, 3)
    tl.begin("use", "用起来：价格十泰铢", L["use"])
    tl.say("use", pre=0.2, mark="use")
    tl.drill("th_use", "u")


def plan07(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 泰国打车", L["hook"])
    tl.say("hook", post=0.4)
    plan_list(tl, L, "route", "叫车 → 指路 → 停车", "t", 5)


def plan08(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 句尾的小尾巴", L["hook"])
    tl.say("hook", post=0.4)
    plan_list(tl, L, "mirror", "男生 / 女生 · 谢谢与问价", "g", 4)


def plan09(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 泰语语序", L["hook"])
    tl.say("hook", post=0.4)
    plan_list(tl, L, "tiles", "四组语序对照", "o", 4)
    tl.begin("rule", "记法", L["rule"])
    tl.say("rule", pre=0.2, post=0.4, mark="rule")


def plan10(tl: TL, L: dict) -> None:
    tl.begin("cover", "封面 · 泰国吃饭", L["hook"])
    tl.say("hook", post=0.4)
    plan_list(tl, L, "receipt", "菜单 → 买单", "d", 5)


def tail(tl: TL, L: dict) -> None:
    tl.begin("book", "教材：新编基础泰语 1–4 册", L["book"])
    tl.say("book", pre=0.15, post=0.5)
    tl.begin("end", "小黄车 + 学泰文字母 App", CTA + OUTRO)
    tl.say("cta", pre=0.1, post=0.25)
    tl.say("outro", mark="outro", post=1.2)
    tl.end()


EPISODES = {
    "02": dict(
        pid="thai-book-jichu-02-tones", comp="TextbookTones", plan=plan02,
        title="泰语一个音，三个意思", cover=("泰语一个音", "三个意思"),
        lines={
            "hook": "泰语里，同一个音，换个声调，意思就全变了。",
            "tones": "泰语有五个声调。今天先听三个：来、马、狗。",
            "w0": "平平地读，是来。",
            "w1": "往高处走，是马。",
            "w2": "先压低再扬起来，是狗。",
            "pair": "再看一对，近和远，只差一个声调。",
            "quiz": "考考你，这是哪一个？",
            "answer": "是狗。",
            "book": "声调规则，在新编基础泰语第一册的发音部分。大学泰语专业的教材，一到四册，附音频。",
        },
        thai={"th_w0": ("มา", TH_F), "th_w1": ("ม้า", TH_F), "th_w2": ("หมา", TH_F),
              "th_p0": ("ใกล้", TH_F), "th_p1": ("ไกล", TH_F)},
        data={"trio": [{"th": "มา", "zh": "来", "tone": "中平调", "rom": "maa", "curve": "flat"},
                       {"th": "ม้า", "zh": "马", "tone": "高调", "rom": "máa", "curve": "high"},
                       {"th": "หมา", "zh": "狗", "tone": "升调", "rom": "mǎa", "curve": "rise"}],
              "pair": [{"th": "ใกล้", "zh": "近", "tone": "降调", "rom": "glâi", "curve": "fall"},
                       {"th": "ไกล", "zh": "远", "tone": "中平调", "rom": "glai", "curve": "flat"}]},
        copy="泰语有五个声调：มา 来、ม้า 马、หมา 狗，同一个音意思全变。\n"
             "声调规则在《新编基础泰语》第一册发音部分，1–4 册附音频。",
    ),
    "03": dict(
        pid="thai-book-jichu-03-day-one", comp="TextbookDayOne", plan=plan03,
        title="到泰国第一天，这5句够用", cover=("到泰国第一天", "这5句够用"),
        lines={
            "hook": "到泰国第一天，这五句话一定用得上。",
            "s0": "见面打招呼。",
            "s1": "买东西问价钱。",
            "s2": "找厕所。",
            "s3": "点菜不要辣。",
            "s4": "别人跟你道歉，回一句没关系。",
            "book": "这样的日常会话，新编基础泰语第二册是中泰对照着练的。很多泰语培训班用的也是这套，一到四册，附音频。",
        },
        thai={"th_s0": ("สวัสดีครับ", TH_M), "th_s1": ("อันนี้เท่าไหร่ครับ", TH_M),
              "th_s2": ("ห้องน้ำอยู่ทางไหนครับ", TH_M), "th_s3": ("ขอไม่เผ็ดได้ไหม", TH_M),
              "th_s4": ("ไม่เป็นไรครับ", TH_M)},
        data={"lines": [{"th": "สวัสดีครับ", "zh": "你好", "tag": "打招呼"},
                        {"th": "อันนี้เท่าไหร่ครับ", "zh": "这个多少钱？", "tag": "问价"},
                        {"th": "ห้องน้ำอยู่ทางไหนครับ", "zh": "厕所在哪里？", "tag": "找厕所"},
                        {"th": "ขอไม่เผ็ดได้ไหม", "zh": "可以不要辣吗？", "tag": "点菜"},
                        {"th": "ไม่เป็นไรครับ", "zh": "没关系", "tag": "回应"}]},
        copy="到泰国第一天用得上的 5 句：你好 / 多少钱 / 厕所在哪 / 不要辣 / 没关系。\n"
             "女生把 ครับ 换成 ค่ะ。日常会话在《新编基础泰语》第二册，中泰对照，附音频。",
    ),
    "04": dict(
        pid="thai-book-jichu-04-roadmap", comp="TextbookRoadmap", plan=plan04,
        title="泰语零基础，一路读到课文", cover=("泰语零基础", "一路读到课文"),
        lines={
            "hook": "零基础学泰语，一路学到能读课文，这套书分四册。",
            "k0": "第一册，发音，字母和声调。比如，鸡。",
            "k1": "第二册，会话，开始学语法。比如，我懂了。",
            "k2": "第三册，课文变长，中文注释变少。比如，我正在学泰语。",
            "k3": "第四册，翻译和写作。比如，请在这里写名字。",
            "book": "这就是新编基础泰语一到四册，大学泰语专业的教材，很多培训班也用它，全套附音频。",
        },
        thai={"th_k0": ("ไก่", TH_M), "th_k1": ("ผมเข้าใจแล้วครับ", TH_M),
              "th_k2": ("ฉันกำลังเรียนภาษาไทย", TH_M), "th_k3": ("เขียนชื่อตรงนี้ครับ", TH_M)},
        data={"steps": [{"book": 1, "skill": "发音", "note": "字母 · 声调", "th": "ไก่", "zh": "鸡"},
                        {"book": 2, "skill": "会话", "note": "语法起步", "th": "ผมเข้าใจแล้วครับ", "zh": "我懂了"},
                        {"book": 3, "skill": "课文", "note": "更长 · 少注释", "th": "ฉันกำลังเรียนภาษาไทย", "zh": "我正在学泰语"},
                        {"book": 4, "skill": "写作", "note": "翻译 · 写作", "th": "เขียนชื่อตรงนี้ครับ", "zh": "请在这里写名字"}]},
        copy="《新编基础泰语》1–4 册怎么学：发音 → 会话 → 课文 → 翻译写作。\n大学泰语专业教材，全套附音频。",
    ),
    "05": dict(
        pid="thai-book-jichu-05-three-steps", comp="TextbookThreeSteps", plan=plan05,
        title="自学泰语，音频这样用", cover=("自学泰语", "音频这样用"),
        lines={
            "hook": "自学泰语，书配的音频怎么用？这样用。",
            "st0": "只听，不看字，听两遍。",
            "st1": "跟着读，一句跟两次。",
            "st2": "对照文字，哪个词没听出来，就标出来。",
            "sum": "听、跟、对，一课一课往下走。",
            "book": "新编基础泰语一到四册，每册都附音频。大学泰语专业的教材，很多培训班也用它。",
        },
        thai={"th_x": ("ฟังเพลงไทยบ่อยไหม", TH_F)},
        data={"sentence": {"th": "ฟังเพลงไทยบ่อยไหม", "zh": "你经常听泰语歌吗？",
                           "parts": [["ฟัง", "听"], ["เพลง", "歌"], ["ไทย", "泰国"], ["บ่อย", "经常"], ["ไหม", "吗"]]}},
        copy="自学泰语，教材音频这样用：只听不看、跟读两次、对照文字。\n《新编基础泰语》1–4 册每册附音频。",
    ),
    "06": dict(
        pid="thai-book-jichu-06-numbers", comp="TextbookNumbers", plan=plan06,
        title="泰语数字1到10", cover=("泰语数字", "1到10"),
        lines={
            "hook": "泰语数字一到十，买东西、问价钱都用得上。",
            "n_intro": "一到十，先听一遍。",
            "n_again": "跟我读。",
            "use": "比如，价格十泰铢。",
            "book": "发音和日常会话，是新编基础泰语前两册的内容。大学泰语专业的教材，一到四册，附音频。",
        },
        thai=dict({f"th_n{i}": (w, TH_F) for i, w in enumerate(
            ["หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า", "สิบ"])},
            th_use=("ราคาสิบบาท", TH_F)),
        data={"nums": [{"n": i + 1, "thd": d, "th": w} for i, (d, w) in enumerate(zip(
                  ["๑", "๒", "๓", "๔", "๕", "๖", "๗", "๘", "๙", "๑๐"],
                  ["หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า", "สิบ"]))],
              "use": {"th": "ราคาสิบบาท", "zh": "价格十泰铢", "parts": [["ราคา", "价格"], ["สิบ", "十"], ["บาท", "泰铢"]]}},
        copy="泰语数字 1–10：หนึ่ง สอง สาม สี่ ห้า หก เจ็ด แปด เก้า สิบ，泰文数字写作 ๑–๑๐。\n"
             "《新编基础泰语》1–4 册，附音频。",
    ),
    "07": dict(
        pid="thai-book-jichu-07-taxi", comp="TextbookTaxi", plan=plan07,
        title="泰国打车，这样说", cover=("泰国打车", "这样说"),
        lines={
            "hook": "在泰国打车，这几句一说，司机就懂。",
            "t0": "请人帮你叫车。",
            "t1": "一直往前开。",
            "t2": "左转。",
            "t3": "右转。",
            "t4": "停在酒店前面。",
            "book": "日常会话是新编基础泰语前两册的重点，例句中泰对照。很多泰语培训班用的也是这套，附音频。",
        },
        thai={"th_t0": ("เรียกแท็กซี่ให้หน่อยครับ", TH_M), "th_t1": ("ตรงไป", TH_M),
              "th_t2": ("เลี้ยวซ้าย", TH_M), "th_t3": ("เลี้ยวขวา", TH_M),
              "th_t4": ("จอดตรงหน้าโรงแรมครับ", TH_M)},
        data={"steps": [{"th": "เรียกแท็กซี่ให้หน่อยครับ", "zh": "帮我叫辆车", "kind": "taxi"},
                        {"th": "ตรงไป", "zh": "直走", "kind": "up"},
                        {"th": "เลี้ยวซ้าย", "zh": "左转", "kind": "left"},
                        {"th": "เลี้ยวขวา", "zh": "右转", "kind": "right"},
                        {"th": "จอดตรงหน้าโรงแรมครับ", "zh": "停酒店前面", "kind": "stop"}]},
        copy="泰国打车 5 句：帮我叫车 / 直走 ตรงไป / 左转 เลี้ยวซ้าย / 右转 เลี้ยวขวา / 停酒店前面。\n"
             "女生把 ครับ 换成 ค่ะ。《新编基础泰语》1–4 册，附音频。",
    ),
    "08": dict(
        pid="thai-book-jichu-08-particles", comp="TextbookParticles", plan=plan08,
        title="泰语说话要加尾巴", cover=("泰语说话", "要加尾巴"),
        lines={
            "hook": "泰语说话，句尾要加一个小尾巴，男生女生还不一样。",
            "g0": "男生说谢谢。",
            "g1": "女生说谢谢。",
            "g2": "男生问多少钱。",
            "g3": "女生问多少钱，尾巴的声调变了。",
            "book": "语法从新编基础泰语第二册开始学，例句中泰对照。大学泰语专业的教材，一到四册，附音频。",
        },
        thai={"th_g0": ("ขอบคุณครับ", TH_M), "th_g1": ("ขอบคุณค่ะ", TH_F),
              "th_g2": ("อันนี้เท่าไหร่ครับ", TH_M), "th_g3": ("ราคาเท่าไหร่คะ", TH_F)},
        data={"pairs": [{"who": "男", "base": "ขอบคุณ", "tail": "ครับ", "zh": "谢谢"},
                        {"who": "女", "base": "ขอบคุณ", "tail": "ค่ะ", "zh": "谢谢"},
                        {"who": "男", "base": "อันนี้เท่าไหร่", "tail": "ครับ", "zh": "这个多少钱？"},
                        {"who": "女", "base": "ราคาเท่าไหร่", "tail": "คะ", "zh": "多少钱？"}]},
        copy="泰语句尾的礼貌小尾巴：男生 ครับ，女生 ค่ะ，女生提问用 คะ。\n"
             "《新编基础泰语》1–4 册，附音频。",
    ),
    "09": dict(
        pid="thai-book-jichu-09-word-order", comp="TextbookWordOrder", plan=plan09,
        title="泰语语序，是反着的", cover=("泰语语序", "是反着的"),
        lines={
            "hook": "泰语的语序，很多地方跟中文是反着的。",
            "o0": "我的家，泰语说成，家的我。",
            "o1": "这家餐厅，说成，餐厅这。",
            "o2": "两只猫，说成，猫两只。",
            "o3": "这只狗，说成，狗只这。",
            "rule": "记住，先说东西，再说修饰它的词。",
            "book": "泰语的语法，新编基础泰语从第二册开始学。大学泰语专业的教材，一到四册，附音频。",
        },
        thai={"th_o0": ("บ้านของฉัน", TH_F), "th_o1": ("ร้านอาหารนี้", TH_F),
              "th_o2": ("แมวสองตัว", TH_F), "th_o3": ("หมาตัวนี้", TH_F)},
        data={"items": [{"label": "我的家", "zh": ["我", "的", "家"], "th": [["บ้าน", "家"], ["ของ", "的"], ["ฉัน", "我"]]},
                        {"label": "这家餐厅", "zh": ["这", "餐厅"], "th": [["ร้านอาหาร", "餐厅"], ["นี้", "这"]]},
                        {"label": "两只猫", "zh": ["两", "只", "猫"], "th": [["แมว", "猫"], ["สอง", "两"], ["ตัว", "只"]]},
                        {"label": "这只狗", "zh": ["这", "只", "狗"], "th": [["หมา", "狗"], ["ตัว", "只"], ["นี้", "这"]]}]},
        copy="泰语语序常跟中文反着：我的家 → บ้านของฉัน（家的我），两只猫 → แมวสองตัว（猫两只）。\n"
             "先说东西，再说修饰。《新编基础泰语》1–4 册，附音频。",
    ),
    "10": dict(
        pid="thai-book-jichu-10-dining", comp="TextbookDining", plan=plan10,
        title="泰国吃饭，点菜到买单", cover=("泰国吃饭", "点菜到买单"),
        lines={
            "hook": "在泰国餐厅，从点菜到买单，这五句全用得上。",
            "d0": "要菜单。",
            "d1": "要一杯白开水。",
            "d2": "夸一句，很好吃。",
            "d3": "吃饱了。",
            "d4": "买单。",
            "book": "日常会话是新编基础泰语前两册的重点。很多泰语培训班用的也是这套，一到四册，附音频。",
        },
        thai={"th_d0": ("ขอดูเมนูหน่อยครับ", TH_M), "th_d1": ("ขอน้ำเปล่าหนึ่งแก้ว", TH_M),
              "th_d2": ("อร่อยมาก", TH_M), "th_d3": ("ผมอิ่มแล้วครับ", TH_M),
              "th_d4": ("เช็คบิลด้วยครับ", TH_M)},
        data={"lines": [{"th": "ขอดูเมนูหน่อยครับ", "zh": "看下菜单"},
                        {"th": "ขอน้ำเปล่าหนึ่งแก้ว", "zh": "一杯白开水"},
                        {"th": "อร่อยมาก", "zh": "很好吃"},
                        {"th": "ผมอิ่มแล้วครับ", "zh": "我吃饱了"},
                        {"th": "เช็คบิลด้วยครับ", "zh": "买单"}]},
        copy="泰国餐厅 5 句：看菜单 / 一杯白开水 / 很好吃 อร่อยมาก / 吃饱了 / 买单 เช็คบิล。\n"
             "女生把 ครับ 换成 ค่ะ、ผม 换成 ฉัน。《新编基础泰语》1–4 册，附音频。",
    ),
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
    print("  audio", path.name, flush=True)
    await asyncio.sleep(0.6)  # 串行 + 间隔，防 edge-tts 限流


def save(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


async def build(num: str, render: bool) -> None:
    ep = EPISODES[num]
    proj = REPO / "projects" / ep["pid"]
    if not proj.exists():
        init_project(ep["pid"], title=f'{ep["title"]}（基础泰语带货 {num}）', pipeline_type="animated-explainer")
    pub = proj / "composition/public"
    for d in ("audio", "fonts", "app", "img"):
        (pub / d).mkdir(parents=True, exist_ok=True)
    A = proj / "assets/audio"
    A.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE / "composition/public/fonts/Sarabun-Bold.ttf", pub / "fonts/Sarabun-Bold.ttf")
    shutil.copy2(TEMPLATE / "assets/music/background.mp3", pub / "audio/background.mp3")
    shutil.copy2(ALPHA_ICON, pub / "app/alpha_icon.png")
    shutil.copy2(BOOKS_PNG, pub / "img/books.png")
    shutil.copy2(SERIES_SRC / "index.tsx", proj / "composition/index.tsx")
    shutil.copy2(SERIES_SRC / "Common.tsx", proj / "composition/Common.tsx")
    shutil.copy2(SERIES_SRC / f"ep{num}.tsx", proj / "composition/Composition.tsx")
    (proj / "composition/Root.tsx").write_text(
        'import {Composition} from "remotion";\nimport {Scene,calculateMetadata,SceneProps} from "./Composition";\n'
        f'export const Root:React.FC=()=><Composition id="{ep["comp"]}" component={{Scene}} durationInFrames={{1800}} '
        'fps={30} width={1080} height={1920} defaultProps={{} as SceneProps} calculateMetadata={calculateMetadata}/>;\n')

    L = dict(ep["lines"], cta=CTA, outro=OUTRO)
    for key, text in L.items():
        await synth(A / f"{key}.mp3", text, ZH)
    for key, (text, voice) in ep["thai"].items():
        await synth(A / f"{key}.mp3", text, voice)
    for f in A.glob("*.mp3"):
        shutil.copy2(f, pub / "audio" / f.name)
    d = {f.stem: dur(f) for f in A.glob("*.mp3")}

    tl = TL(d)
    ep["plan"](tl, L)
    tail(tl, L)
    total = round(tl.t * FPS)
    props = {
        "fps": FPS, "totalFrames": total, "totalSeconds": total / FPS, "num": num,
        "cover": list(ep["cover"]), "data": ep["data"], "marks": tl.marks,
        "scenes": tl.scenes, "audio": tl.audio,
        "speak": [[a["at"], round(a["at"] + d[a["file"][:-4]], 3)] for a in tl.audio],
        "bgm": {"file": "background.mp3", "volume": 0.05},
        "review_timeline": [{"id": x["id"], "label": x["label"], "start": x["start"], "end": x["end"],
                             "title": x["label"], "text": x["text"], "credit": "商品主图：出版社直营店"} for x in tl.scenes],
    }
    save(proj / "composition/props.json", props)
    save(proj / "artifacts/props.json", props)
    save(proj / "artifacts/script.json", {
        "version": "1.0", "title": ep["title"], "total_duration_seconds": props["totalSeconds"],
        "sections": [{"id": x["id"], "label": x["label"], "text": x["text"], "start_seconds": x["start"],
                      "end_seconds": x["end"], "speaker_directions": "中文女声讲解；泰语读两遍 + 跟读空档。"}
                     for x in tl.scenes],
        "metadata": {"language": "zh+th", "kind": "带货·图书",
                     "product": "新编基础泰语1-2 + 基础泰语3-4（世界图书出版广东公司）",
                     "thai_source": "lang1000 thai1000_20260716_131042_all.json（词条或例句子串）",
                     "tts": {"engine": "edge", "zh": ZH, "thai": {k: v[1][0] for k, v in ep["thai"].items()}},
                     "claims_policy": "画面只用可核实说法：大学泰语专业教材 / 1–4 册 / 附音频；旁白可说'很多培训班也用'；不说'都用''最权威'。"},
    })
    save(proj / "artifacts/publish.json", {
        "series_id": 1, "sub_series": "教材带货", "slug": f"thai_book_jichu_{num}",
        "title": ep["title"], "wechat_copy": ep["title"],
        "publish_copy": ep["copy"] + "\n\n" + TAGS,
        "credits": "教材图片：出版社直营店商品主图；配音与剪辑：泰语千词。",
    })
    print(ep["pid"], f'{props["totalSeconds"]:.1f}s', flush=True)

    if render:
        renders = proj / "renders"
        renders.mkdir(exist_ok=True)
        n = len(list(renders.glob("v*.mp4"))) + 1
        out = renders / f"v{n}.mp4"
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
