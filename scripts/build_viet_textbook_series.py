"""《基础越南语》1–4 册 +《越英汉常用词汇分类手册》带货系列（越南语千词号，series_id=2）。

和泰语那条线共用引擎（build_textbook_series.TL / synth、textbook_series/Common.tsx），
账号身份（品牌行、片尾 app）走 Common.SeriesCtx 覆盖。每集的创意组件独立：textbook_series/vNN.tsx。

教材说法只用可核实的：封面（国家级教学成果二等奖系列教材 / 亚非语言文学国家级特色专业建设点系列教材；
手册 8000+ 词汇 · 8 大主题 · 32 个情景）与出版社 App 介绍（解放军外国语学院越南语专业编写，
共四册、每册 15–16 课，约 4000 词，每课有主课文 / 生词 / 会话 / 语法 / 练习 / 拓展阅读，另有语音部分）。
越南语一律取自 viet1000 词库（词条或例句子串）；唯一例外是 v01 的 ma 六声调示例，交片时单独标注。

    python3 scripts/build_viet_textbook_series.py all [--render]
"""
from __future__ import annotations

import asyncio
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_textbook_series import TL, synth, dur, save, REPO, TEMPLATE, SERIES_SRC, FPS, ZH  # noqa: E402
from lib.checkpoint import init_project  # noqa: E402

GRABS = Path("/Users/zhenyusong/.terminalAssist/grabs")
SET_SHOT, HANDBOOK_SHOT = GRABS / "2026-10-11_22-23-59.png", GRABS / "2026-10-11_22-23-35.png"
VI_FONT = REPO / "projects/viet-zen-01-mainmai/composition/public/fonts/BeVietnamPro-Bold.ttf"
VI_ICON = Path("/Users/zhenyusong/projects/AlphabetLearningFramework/apps/vietnamese/ios/Runner/"
               "Assets.xcassets/AppIcon.appiconset/Icon-App-1024x1024@1x.png")
VI_F = ("vi-VN-HoaiMyNeural", "-10%")
VI_M = ("vi-VN-NamMinhNeural", "-10%")
CTA = "想系统学越南语，点左下角小黄车。"
OUTRO = "背单词用越南语千词，练字母用学越南语字母。"
TAGS = "#越南语 #越南语学习 #越南语入门 #越南语教材 #带货"


def plan_list(tl: TL, L: dict, sid: str, label: str, prefix: str, n: int) -> None:
    tl.begin(sid, label, "".join(L[f"{prefix}{i}"] for i in range(n)))
    for i in range(n):
        tl.say(f"{prefix}{i}", pre=0.25, mark=f"{prefix}{i}")
        tl.drill(f"vi_{prefix}{i}", f"{prefix}{i}")


def opener(tl: TL, label: str) -> None:
    tl.begin("cover", label, "")
    tl.say("hook", post=0.4)


def plan01(tl, L):
    opener(tl, "封面 · 六个声调")
    plan_list(tl, L, "tones", "ma 的六个声调", "w", 6)


def plan02(tl, L):
    opener(tl, "封面 · 越南语里的中文")
    plan_list(tl, L, "seals", "汉越词四个", "h", 4)


def plan03(tl, L):
    opener(tl, "封面 · 到越南第一天")
    plan_list(tl, L, "street", "五句会话", "s", 5)


def plan04(tl, L):
    opener(tl, "封面 · 按情景背词")
    tl.begin("theme", "情景：餐厅", L["theme"])
    tl.say("theme", pre=0.15, post=0.2, mark="theme")
    plan_list(tl, L, "map", "餐厅情景五个词", "r", 5)


def plan05(tl, L):
    opener(tl, "封面 · 数字 1 到 10")
    tl.begin("count", "1–10 先听一遍，再跟读", L["n_intro"] + L["n_again"])
    tl.say("n_intro", pre=0.15, post=0.25)
    for i in range(10):
        tl.say(f"vi_n{i}", mark=f"p{i}", post=0.22)
    tl.say("n_again", pre=0.3, post=0.25, mark="again")
    for i in range(10):
        tl.say(f"vi_n{i}", mark=f"n{i}_a")
        tl.marks[f"n{i}_f"] = round(tl.t, 3)
        tl.gap(tl.d[f"vi_n{i}"] + 0.4)
        tl.marks[f"n{i}_e"] = round(tl.t, 3)
    tl.begin("use", "用起来：一万越南盾", L["use"])
    tl.say("use", pre=0.2, mark="use")
    tl.drill("vi_use", "u")


def plan06(tl, L):
    opener(tl, "封面 · 打车五个词")
    plan_list(tl, L, "route", "跟司机说的五个词", "d", 5)


def plan07(tl, L):
    opener(tl, "封面 · 星期一叫第二")
    plan_list(tl, L, "week", "星期一到星期天", "k", 7)


def plan08(tl, L):
    opener(tl, "封面 · 生病五句")
    plan_list(tl, L, "pills", "看病五句", "m", 5)


def plan09(tl, L):
    opener(tl, "封面 · 越南水果")
    plan_list(tl, L, "stall", "五种水果", "f", 5)


def plan10(tl, L):
    opener(tl, "封面 · 住酒店")
    plan_list(tl, L, "lift", "前台五个词", "o", 5)


def plan11(tl, L):
    opener(tl, "封面 · 颜色")
    plan_list(tl, L, "chips", "五个颜色", "c", 5)


def plan12(tl, L):
    opener(tl, "封面 · 家人")
    plan_list(tl, L, "tree", "一家人怎么叫", "fa", 5)


def plan13(tl, L):
    opener(tl, "封面 · 天气")
    plan_list(tl, L, "forecast", "五个天气词", "wx", 5)


def plan14(tl, L):
    opener(tl, "封面 · 自我介绍")
    plan_list(tl, L, "chat", "初次见面五句", "me", 5)


def plan15(tl, L):
    opener(tl, "封面 · 交通工具")
    plan_list(tl, L, "route", "五种交通工具", "tr", 5)


def tail(tl, L):
    tl.begin("book", "教材：基础越南语 1–4 册", L["book"])
    tl.say("book", pre=0.15, post=0.5)
    tl.begin("end", "小黄车 + 越南语千词 + 学越南语字母", CTA + OUTRO)
    tl.say("cta", pre=0.1, post=0.25)
    tl.say("outro", mark="outro", post=1.2)
    tl.end()


NUMS = ["một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười"]

EPISODES = {
    "01": dict(
        pid="viet-book-coso-01-tones", pub_title="越南语六个声调", comp="VietBookTones", plan=plan01,
        title="越南语，六个声调", cover=("越南语", "六个声调"), topic="声调",
        lines={
            "hook": "越南语有六个声调。同一个音，换个声调，意思全变了。",
            "w0": "平平地读，是鬼。",
            "w1": "往上扬，是脸颊。",
            "w2": "往下沉，是但是。",
            "w3": "先降再升，是坟墓。",
            "w4": "中间一折再扬起，是马。",
            "w5": "又低又短，是秧苗。",
            "book": "声调和发音，是基础越南语的语音部分。国家级教学成果二等奖系列教材，一共四册。",
        },
        viet={f"vi_w{i}": (w, VI_F) for i, w in enumerate(["ma", "má", "mà", "mả", "mã", "mạ"])},
        data={"tones": [{"vi": "ma", "mark": "", "name": "ngang", "zh": "鬼", "tone": "平声"},
                        {"vi": "má", "mark": "´", "name": "sắc", "zh": "脸颊", "tone": "锐声"},
                        {"vi": "mà", "mark": "`", "name": "huyền", "zh": "但是", "tone": "玄声"},
                        {"vi": "mả", "mark": "̉", "name": "hỏi", "zh": "坟墓", "tone": "问声"},
                        {"vi": "mã", "mark": "~", "name": "ngã", "zh": "马", "tone": "跌声"},
                        {"vi": "mạ", "mark": ".", "name": "nặng", "zh": "秧苗", "tone": "重声"}]},
        copy="越南语六个声调：ma 鬼 / má 脸颊 / mà 但是 / mả 坟墓 / mã 马 / mạ 秧苗。\n"
             "《基础越南语》1–4 册，国家级教学成果二等奖系列教材。",
    ),
    "02": dict(
        pid="viet-book-coso-02-hanviet", pub_title="越南语里藏着中文", comp="VietBookHanViet", plan=plan02,
        title="越南语里，藏着中文", cover=("越南语里", "藏着中文"), topic="汉越词",
        lines={
            "hook": "越南语里藏着很多中文，听一遍你就能猜出来。",
            "h0": "电话。",
            "h1": "时间。",
            "h2": "病院，就是医院。",
            "h3": "感恩，就是谢谢。",
            "book": "基础越南语，解放军外国语学院越南语专业编写。一共四册，按教材设计，学完能掌握四千个左右的单词。",
        },
        viet={"vi_h0": ("điện thoại", VI_F), "vi_h1": ("thời gian", VI_F),
              "vi_h2": ("bệnh viện", VI_F), "vi_h3": ("cảm ơn", VI_F)},
        data={"words": [{"vi": "điện thoại", "han": ["電", "話"], "syl": ["điện", "thoại"], "zh": "电话"},
                        {"vi": "thời gian", "han": ["時", "間"], "syl": ["thời", "gian"], "zh": "时间"},
                        {"vi": "bệnh viện", "han": ["病", "院"], "syl": ["bệnh", "viện"], "zh": "医院"},
                        {"vi": "cảm ơn", "han": ["感", "恩"], "syl": ["cảm", "ơn"], "zh": "谢谢"}]},
        copy="越南语里的中文：điện thoại 电话、thời gian 时间、bệnh viện 病院（医院）、cảm ơn 感恩（谢谢）。\n"
             "《基础越南语》1–4 册，按教材设计约 4000 词。",
    ),
    "03": dict(
        pid="viet-book-coso-03-day-one", pub_title="到越南第一天先学这5句", comp="VietBookDayOne", plan=plan03,
        title="到越南第一天，先学这5句", cover=("到越南第一天", "先学这5句"), topic="会话",
        lines={
            "hook": "到越南第一天，先学这五句。",
            "s0": "见面打招呼。",
            "s1": "不小心碰到人。",
            "s2": "买东西问价钱。",
            "s3": "别人道歉，你说没关系。",
            "s4": "走的时候说再见。",
            "book": "基础越南语每一课都有会话和生词。国家级教学成果二等奖系列教材，一共四册。",
        },
        viet={"vi_s0": ("Xin chào", VI_F), "vi_s1": ("Xin lỗi", VI_F),
              "vi_s2": ("Cái này bao nhiêu tiền?", VI_F), "vi_s3": ("Không sao", VI_F),
              "vi_s4": ("Tạm biệt", VI_F)},
        data={"lines": [{"vi": "Xin chào", "zh": "你好", "tag": "打招呼"},
                        {"vi": "Xin lỗi", "zh": "对不起", "tag": "道歉"},
                        {"vi": "Cái này bao nhiêu tiền?", "zh": "这个多少钱？", "tag": "问价"},
                        {"vi": "Không sao", "zh": "没关系", "tag": "回应"},
                        {"vi": "Tạm biệt", "zh": "再见", "tag": "告别"}]},
        copy="到越南第一天先学 5 句：Xin chào 你好 / Xin lỗi 对不起 / Cái này bao nhiêu tiền? 多少钱 / "
             "Không sao 没关系 / Tạm biệt 再见。\n《基础越南语》1–4 册，每课都有会话和生词。",
    ),
    "04": dict(
        pid="viet-book-coso-04-handbook", pub_title="越南语单词按情景背", comp="VietBookHandbook", plan=plan04,
        title="越南语单词，按情景背", cover=("越南语单词", "按情景背"), topic="词汇",
        lines={
            "hook": "背越南语单词，别一个个硬背，按情景背。",
            "theme": "比如在餐厅，这几个词一起记。",
            "r0": "菜单。",
            "r1": "河粉。",
            "r2": "咖啡。",
            "r3": "好吃。",
            "r4": "买单。",
            "book": "这本越英汉常用词汇分类手册，八千多个词，分八大主题、三十二个情景。配上基础越南语四册一起学。",
        },
        viet={"vi_r0": ("thực đơn", VI_F), "vi_r1": ("phở", VI_F), "vi_r2": ("cà phê", VI_F),
              "vi_r3": ("ngon", VI_F), "vi_r4": ("tính tiền", VI_F)},
        data={"theme": "餐厅", "words": [{"vi": "thực đơn", "zh": "菜单"}, {"vi": "phở", "zh": "河粉"},
                                          {"vi": "cà phê", "zh": "咖啡"}, {"vi": "ngon", "zh": "好吃"},
                                          {"vi": "tính tiền", "zh": "买单"}]},
        copy="越南语单词按情景背：餐厅里 thực đơn 菜单 / phở 河粉 / cà phê 咖啡 / ngon 好吃 / tính tiền 买单。\n"
             "《越英汉常用词汇分类手册》8000+ 词汇 · 8 大主题 · 32 个情景，配《基础越南语》1–4 册。",
    ),
    "05": dict(
        pid="viet-book-coso-05-numbers", pub_title="越南语数字1到10", comp="VietBookNumbers", plan=plan05,
        title="越南语数字1到10", cover=("越南语数字", "1到10"), topic="数字",
        lines={
            "hook": "越南语数字一到十，买东西、讲价钱都用得上。",
            "n_intro": "一到十，先听一遍。",
            "n_again": "跟我读。",
            "use": "比如，价格一万越南盾。",
            "book": "基础越南语一共四册，每册十五到十六课。配上越英汉常用词汇分类手册，按情景查词。",
        },
        viet=dict({f"vi_n{i}": (w, VI_F) for i, w in enumerate(NUMS)}, vi_use=("Giá mười nghìn đồng", VI_F)),
        data={"nums": [{"n": i + 1, "vi": w} for i, w in enumerate(NUMS)],
              "use": {"vi": "Giá mười nghìn đồng", "zh": "价格一万越南盾",
                      "parts": [["Giá", "价格"], ["mười", "十"], ["nghìn", "千"], ["đồng", "越南盾"]]}},
        copy="越南语数字 1–10：một hai ba bốn năm sáu bảy tám chín mười。\n"
             "价格一万越南盾：Giá mười nghìn đồng（十个千）。《基础越南语》1–4 册，每册 15–16 课。",
    ),
    "06": {'pid': 'viet-book-coso-06-taxi', 'pub_title': '在越南打车这5个词', 'comp': 'VietBookTaxi', 'plan': plan06, 'title': '在越南打车这5个词', 'cover': ('在越南打车', '说这5个词'), 'topic': '交通', 'lines': {'hook': '在越南打车、坐摩的，跟司机说这五个词就够了。', 'book': '基础越南语一共四册，每课都有会话、生词、语法和练习。', 'd0': '直走。', 'd1': '左转。', 'd2': '右转。', 'd3': '十字路口。', 'd4': '到了，停。'}, 'viet': {'vi_d0': ('Đi thẳng', VI_F), 'vi_d1': ('Rẽ trái', VI_F), 'vi_d2': ('Rẽ phải', VI_F), 'vi_d3': ('Ngã tư', VI_F), 'vi_d4': ('Dừng lại', VI_F)}, 'data': {'items': [{'vi': 'Đi thẳng', 'zh': '直走', 'sign': 'up'}, {'vi': 'Rẽ trái', 'zh': '左转', 'sign': 'left'}, {'vi': 'Rẽ phải', 'zh': '右转', 'sign': 'right'}, {'vi': 'Ngã tư', 'zh': '十字路口', 'sign': 'cross'}, {'vi': 'Dừng lại', 'zh': '停', 'sign': 'stop'}]}, 'copy': '在越南打车跟司机说 5 个词：Đi thẳng 直走 / Rẽ trái 左转 / Rẽ phải 右转 / Ngã tư 十字路口 / Dừng lại 停。\n《基础越南语》1–4 册，每课都有会话、生词、语法和练习。'},
    "07": {'pid': 'viet-book-coso-07-weekdays', 'pub_title': '越南语星期一叫第二', 'comp': 'VietBookWeek', 'plan': plan07, 'title': '越南语星期一叫第二', 'cover': ('越南语星期一', '叫第二'), 'topic': '星期', 'lines': {'hook': '越南语的星期一，叫第二。从星期一开始，一路往后数，星期天单独叫主日。', 'book': '基础越南语，解放军外国语学院越南语专业编写。国家级教学成果二等奖系列教材，一共四册。', 'k0': '星期一。', 'k1': '星期二。', 'k2': '星期三。', 'k3': '星期四。', 'k4': '星期五。', 'k5': '星期六。', 'k6': '星期天。'}, 'viet': {'vi_k0': ('Thứ Hai', VI_F), 'vi_k1': ('Thứ Ba', VI_F), 'vi_k2': ('Thứ Tư', VI_F), 'vi_k3': ('Thứ Năm', VI_F), 'vi_k4': ('Thứ Sáu', VI_F), 'vi_k5': ('Thứ Bảy', VI_F), 'vi_k6': ('Chủ Nhật', VI_F)}, 'data': {'items': [{'vi': 'Thứ Hai', 'zh': '星期一', 'n': '2'}, {'vi': 'Thứ Ba', 'zh': '星期二', 'n': '3'}, {'vi': 'Thứ Tư', 'zh': '星期三', 'n': '4'}, {'vi': 'Thứ Năm', 'zh': '星期四', 'n': '5'}, {'vi': 'Thứ Sáu', 'zh': '星期五', 'n': '6'}, {'vi': 'Thứ Bảy', 'zh': '星期六', 'n': '7'}, {'vi': 'Chủ Nhật', 'zh': '星期天', 'n': '主'}]}, 'copy': '越南语星期一叫「第二」：Thứ Hai 星期一 / Thứ Ba 星期二 / Thứ Tư 星期三 / Thứ Năm 星期四 / Thứ Sáu 星期五 / Thứ Bảy 星期六 / Chủ Nhật 星期天（主日）。\n《基础越南语》1–4 册，国家级教学成果二等奖系列教材。'},
    "08": {'pid': 'viet-book-coso-08-sick', 'pub_title': '在越南生病这5句', 'comp': 'VietBookSick', 'plan': plan08, 'title': '在越南生病这5句', 'cover': ('在越南生病', '说这5句'), 'topic': '看病', 'lines': {'hook': '在越南生病了，先学这五句。', 'book': '出门在外的常用词，可以查越英汉常用词汇分类手册。八千多个词，八大主题、三十二个情景。', 'm0': '我生病了。', 'm1': '头痛。', 'm2': '发烧。', 'm3': '咳嗽。', 'm4': '我需要看医生。'}, 'viet': {'vi_m0': ('Tôi bị ốm', VI_F), 'vi_m1': ('Đau đầu', VI_F), 'vi_m2': ('Sốt', VI_F), 'vi_m3': ('Ho', VI_F), 'vi_m4': ('Tôi cần bác sĩ', VI_F)}, 'data': {'items': [{'vi': 'Tôi bị ốm', 'zh': '我生病了'}, {'vi': 'Đau đầu', 'zh': '头痛'}, {'vi': 'Sốt', 'zh': '发烧'}, {'vi': 'Ho', 'zh': '咳嗽'}, {'vi': 'Tôi cần bác sĩ', 'zh': '我需要看医生'}]}, 'copy': '在越南生病先学 5 句：Tôi bị ốm 我生病了 / Đau đầu 头痛 / Sốt 发烧 / Ho 咳嗽 / Tôi cần bác sĩ 我需要看医生。\n《越英汉常用词汇分类手册》8000+ 词汇 · 8 大主题 · 32 个情景，配《基础越南语》1–4 册。'},
    "09": {'pid': 'viet-book-coso-09-fruits', 'pub_title': '越南水果名这样说', 'comp': 'VietBookFruits', 'plan': plan09, 'title': '越南水果名这样说', 'cover': ('越南水果', '这样叫'), 'topic': '水果', 'lines': {'hook': '越南的水果，名字这样叫。', 'book': '基础越南语一共四册，每课有主课文、生词、会话、语法、练习和拓展阅读。', 'f0': '芒果。', 'f1': '榴莲，越南人叫它水果之王。', 'f2': '山竹，水果皇后。', 'f3': '火龙果。', 'f4': '红毛丹，外面一层红毛。'}, 'viet': {'vi_f0': ('xoài', VI_F), 'vi_f1': ('sầu riêng', VI_F), 'vi_f2': ('măng cụt', VI_F), 'vi_f3': ('thanh long', VI_F), 'vi_f4': ('chôm chôm', VI_F)}, 'data': {'items': [{'vi': 'xoài', 'zh': '芒果', 'c': '#ffb703', 'c2': '#fb8500'}, {'vi': 'sầu riêng', 'zh': '榴莲', 'c': '#c5d86d', 'c2': '#7a8b2c'}, {'vi': 'măng cụt', 'zh': '山竹', 'c': '#6a2c70', 'c2': '#3e1641'}, {'vi': 'thanh long', 'zh': '火龙果', 'c': '#ff4f8b', 'c2': '#c2185b'}, {'vi': 'chôm chôm', 'zh': '红毛丹', 'c': '#e63946', 'c2': '#9d0208'}]}, 'copy': '越南水果这样叫：xoài 芒果 / sầu riêng 榴莲（水果之王）/ măng cụt 山竹（水果皇后）/ thanh long 火龙果 / chôm chôm 红毛丹。\n《基础越南语》1–4 册，每课有主课文、生词、会话、语法、练习和拓展阅读。'},
    "10": {'pid': 'viet-book-coso-10-hotel', 'pub_title': '越南住酒店这5个词', 'comp': 'VietBookHotel', 'plan': plan10, 'title': '越南住酒店这5个词', 'cover': ('越南住酒店', '这5个词'), 'topic': '酒店', 'lines': {'hook': '在越南住酒店，前台这五个词用得上。', 'book': '基础越南语四册打底，配上越英汉常用词汇分类手册，八千多个词，按情景查。', 'o0': '入住。', 'o1': '退房。', 'o2': '无线网密码。', 'o3': '热水。', 'o4': '含早餐。'}, 'viet': {'vi_o0': ('Nhận phòng', VI_F), 'vi_o1': ('Trả phòng', VI_F), 'vi_o2': ('Mật khẩu Wi-Fi', VI_F), 'vi_o3': ('Nước nóng', VI_F), 'vi_o4': ('Bao gồm bữa sáng', VI_F)}, 'data': {'items': [{'vi': 'Nhận phòng', 'zh': '入住', 'n': '1'}, {'vi': 'Trả phòng', 'zh': '退房', 'n': '2'}, {'vi': 'Mật khẩu Wi-Fi', 'zh': '无线网密码', 'n': '3'}, {'vi': 'Nước nóng', 'zh': '热水', 'n': '4'}, {'vi': 'Bao gồm bữa sáng', 'zh': '含早餐', 'n': '5'}]}, 'copy': '越南住酒店前台 5 个词：Nhận phòng 入住 / Trả phòng 退房 / Mật khẩu Wi-Fi 无线网密码 / Nước nóng 热水 / Bao gồm bữa sáng 含早餐。\n《基础越南语》1–4 册 +《越英汉常用词汇分类手册》8000+ 词汇，按情景查。'},
    # ── 2026-11 库存补齐：11–15。越南语全部取自 viet1000（词条或已校对例句的子串），逐个核过。
    "11": dict(pid="viet-book-coso-11-colors", pub_title="越南语颜色这样说", comp="VietBookColors", plan=plan11,
        title="越南语颜色这样说", cover=("越南语", "颜色这样说"), topic="颜色",
        lines={"hook": "越南语的颜色，前面都加一个词，màu，就是颜色。", "c0": "红色。", "c1": "黄色。", "c2": "白色。", "c3": "黑色。", "c4": "绿色。",
               "book": "基础越南语一共四册，每课都有会话、生词、语法和练习。"},
        viet={"vi_c0": ("màu đỏ", VI_F), "vi_c1": ("màu vàng", VI_F), "vi_c2": ("màu trắng", VI_F), "vi_c3": ("màu đen", VI_F), "vi_c4": ("màu xanh lá", VI_F)},
        data={"items": [{"vi": "màu đỏ", "zh": "红色", "c": "#d62828", "ink": "#ffffff"}, {"vi": "màu vàng", "zh": "黄色", "c": "#ffcc00", "ink": "#1d1d1f"},
                        {"vi": "màu trắng", "zh": "白色", "c": "#fafafa", "ink": "#1d1d1f"}, {"vi": "màu đen", "zh": "黑色", "c": "#1d1d1f", "ink": "#ffffff"},
                        {"vi": "màu xanh lá", "zh": "绿色", "c": "#2a9d4b", "ink": "#ffffff"}]},
        copy="越南语颜色前面都加 màu：màu đỏ 红色 / màu vàng 黄色 / màu trắng 白色 / màu đen 黑色 / màu xanh lá 绿色。\n"
             "《基础越南语》1–4 册，每课都有会话、生词、语法和练习。"),
    "12": dict(pid="viet-book-coso-12-family", pub_title="越南语家人怎么叫", comp="VietBookFamily", plan=plan12,
        title="越南语家人怎么叫", cover=("越南语", "家人怎么叫"), topic="家人",
        lines={"hook": "越南语里，一家人怎么叫？", "fa0": "爷爷奶奶。", "fa1": "爸爸。", "fa2": "妈妈。", "fa3": "弟弟。", "fa4": "妹妹。",
               "book": "基础越南语，解放军外国语学院越南语专业编写，一共四册。"},
        viet={"vi_fa0": ("ông bà", VI_F), "vi_fa1": ("bố", VI_F), "vi_fa2": ("mẹ", VI_F), "vi_fa3": ("em trai", VI_F), "vi_fa4": ("em gái", VI_F)},
        data={"me": {"x": 540, "y": 880}, "items": [{"vi": "ông bà", "zh": "爷爷奶奶", "x": 540, "y": 430}, {"vi": "bố", "zh": "爸爸", "x": 290, "y": 660},
                        {"vi": "mẹ", "zh": "妈妈", "x": 790, "y": 660}, {"vi": "em trai", "zh": "弟弟", "x": 290, "y": 1100},
                        {"vi": "em gái", "zh": "妹妹", "x": 790, "y": 1100}]},
        copy="越南语一家人：ông bà 爷爷奶奶 / bố 爸爸 / mẹ 妈妈 / em trai 弟弟 / em gái 妹妹。\n"
             "《基础越南语》1–4 册，解放军外国语学院越南语专业编写。"),
    "13": dict(pid="viet-book-coso-13-weather", pub_title="越南天气这5个词", comp="VietBookWeather", plan=plan13,
        title="越南天气这5个词", cover=("越南天气", "这5个词"), topic="天气",
        lines={"hook": "去越南前看天气，这五个词先学会。", "wx0": "热。", "wx1": "冷。", "wx2": "下雨。", "wx3": "晴天，太阳很大。", "wx4": "刮风。",
               "book": "常用词可以查越英汉常用词汇分类手册，八千多个词，八大主题、三十二个情景。"},
        viet={"vi_wx0": ("nóng", VI_F), "vi_wx1": ("lạnh", VI_F), "vi_wx2": ("mưa", VI_F), "vi_wx3": ("nắng", VI_F), "vi_wx4": ("gió", VI_F)},
        data={"items": [{"vi": "nóng", "zh": "热", "icon": "hot", "day": "周一"}, {"vi": "lạnh", "zh": "冷", "icon": "cold", "day": "周二"},
                        {"vi": "mưa", "zh": "下雨", "icon": "rain", "day": "周三"}, {"vi": "nắng", "zh": "晴、阳光", "icon": "sun", "day": "周四"},
                        {"vi": "gió", "zh": "风", "icon": "wind", "day": "周五"}]},
        copy="越南天气 5 个词：nóng 热 / lạnh 冷 / mưa 下雨 / nắng 晴、阳光 / gió 风。\n"
             "《越英汉常用词汇分类手册》8000+ 词汇 · 8 大主题 · 32 个情景，配《基础越南语》1–4 册。"),
    "14": dict(pid="viet-book-coso-14-intro", pub_title="越南语自我介绍5句", comp="VietBookIntro", plan=plan14,
        title="越南语自我介绍5句", cover=("越南语", "自我介绍"), topic="会话",
        lines={"hook": "第一次见越南朋友，自我介绍就这五句。", "me0": "你好。", "me1": "你好吗？", "me2": "我叫……", "me3": "很高兴认识你。", "me4": "我是中国人。",
               "book": "基础越南语每一课都有会话和生词，一共四册，每册十五到十六课。"},
        viet={"vi_me0": ("Xin chào", VI_F), "vi_me1": ("Bạn khỏe không?", VI_F), "vi_me2": ("Tôi tên là", VI_F),
              "vi_me3": ("Rất vui được gặp bạn", VI_F), "vi_me4": ("Tôi là người Trung Quốc", VI_F)},
        data={"items": [{"vi": "Xin chào", "zh": "你好", "side": "l"}, {"vi": "Bạn khỏe không?", "zh": "你好吗？", "side": "l"},
                        {"vi": "Tôi tên là…", "zh": "我叫……", "side": "r"}, {"vi": "Rất vui được gặp bạn", "zh": "很高兴认识你", "side": "r"},
                        {"vi": "Tôi là người Trung Quốc", "zh": "我是中国人", "side": "r"}]},
        copy="越南语自我介绍 5 句：Xin chào 你好 / Bạn khỏe không? 你好吗 / Tôi tên là… 我叫… / Rất vui được gặp bạn 很高兴认识你 / "
             "Tôi là người Trung Quốc 我是中国人。\n《基础越南语》1–4 册，每课都有会话和生词。"),
    "15": dict(pid="viet-book-coso-15-transport", pub_title="越南交通工具5个词", comp="VietBookTransport", plan=plan15,
        title="越南交通工具5个词", cover=("越南出行", "坐什么车"), topic="交通",
        lines={"hook": "在越南出门，坐什么车？这五个词先学会。", "tr0": "摩托车。", "tr1": "公交车。", "tr2": "火车。", "tr3": "船。", "tr4": "轻轨。",
               "book": "基础越南语四册打底，配上越英汉常用词汇分类手册，八千多个词，按情景查。"},
        viet={"vi_tr0": ("xe máy", VI_F), "vi_tr1": ("xe buýt", VI_F), "vi_tr2": ("tàu hỏa", VI_F), "vi_tr3": ("thuyền", VI_F), "vi_tr4": ("tàu điện trên cao", VI_F)},
        data={"items": [{"vi": "xe máy", "zh": "摩托车", "c": "#e53935"}, {"vi": "xe buýt", "zh": "公交车", "c": "#1e88e5"},
                        {"vi": "tàu hỏa", "zh": "火车", "c": "#43a047"}, {"vi": "thuyền", "zh": "船", "c": "#00897b"},
                        {"vi": "tàu điện trên cao", "zh": "轻轨", "c": "#8e24aa"}]},
        copy="越南出行 5 个词：xe máy 摩托车 / xe buýt 公交车 / tàu hỏa 火车 / thuyền 船 / tàu điện trên cao 轻轨。\n"
             "《基础越南语》1–4 册 +《越英汉常用词汇分类手册》8000+ 词汇，按情景查。"),
}


async def build(num: str, render: bool) -> None:
    ep = EPISODES[num]
    proj = REPO / "projects" / ep["pid"]
    if not proj.exists():
        init_project(ep["pid"], title=f'{ep["title"]}（基础越南语带货 {num}）', pipeline_type="animated-explainer")
    pub = proj / "composition/public"
    for d in ("audio", "fonts", "app", "img"):
        (pub / d).mkdir(parents=True, exist_ok=True)
    A = proj / "assets/audio"
    A.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE / "composition/public/fonts/Sarabun-Bold.ttf", pub / "fonts/Sarabun-Bold.ttf")
    shutil.copy2(VI_FONT, pub / "fonts/BeVietnamPro-Bold.ttf")
    shutil.copy2(TEMPLATE / "assets/music/background.mp3", pub / "audio/background.mp3")
    shutil.copy2(VI_ICON, pub / "app/viet_alpha_icon.png")
    shutil.copy2(Path("/Users/zhenyusong/projects/lang1000/apps/viet1000/playstore/icon-512.png"), pub / "app/viet_qianci_icon.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(SET_SHOT), "-vf",
                    "scale=900:-1:flags=lanczos,crop=900:816", str(pub / "img/books.png")], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(HANDBOOK_SHOT), "-vf",
                    "crop=560:800:90:60,scale=700:-1:flags=lanczos", str(pub / "img/handbook.png")], check=True)
    shutil.copy2(SERIES_SRC / "index.tsx", proj / "composition/index.tsx")
    shutil.copy2(SERIES_SRC / "Common.tsx", proj / "composition/Common.tsx")
    shutil.copy2(SERIES_SRC / f"v{num}.tsx", proj / "composition/Composition.tsx")
    (proj / "composition/Root.tsx").write_text(
        'import {Composition} from "remotion";\nimport {Scene,calculateMetadata,SceneProps} from "./Composition";\n'
        f'export const Root:React.FC=()=><Composition id="{ep["comp"]}" component={{Scene}} durationInFrames={{1800}} '
        'fps={30} width={1080} height={1920} defaultProps={{} as SceneProps} calculateMetadata={calculateMetadata}/>;\n')

    L = dict(ep["lines"], cta=CTA, outro=OUTRO)
    for key, text in L.items():
        await synth(A / f"{key}.mp3", text, ZH)
    for key, (text, voice) in ep["viet"].items():
        await synth(A / f"{key}.mp3", text, voice)
    for f in A.glob("*.mp3"):
        shutil.copy2(f, pub / "audio" / f.name)
    d = {f.stem: dur(f) for f in A.glob("*.mp3")}

    tl = TL(d)
    ep["plan"](tl, L)
    tail(tl, L)
    total = round(tl.t * FPS)
    tl.scenes[0]["text"] = L["hook"]
    props = {
        "fps": FPS, "totalFrames": total, "totalSeconds": total / FPS, "num": num, "topic": ep["topic"],
        "cover": list(ep["cover"]), "data": ep["data"], "marks": tl.marks,
        "scenes": tl.scenes, "audio": tl.audio,
        "speak": [[a["at"], round(a["at"] + d[a["file"][:-4]], 3)] for a in tl.audio],
        "bgm": {"file": "background.mp3", "volume": 0.05},
        "review_timeline": [{"id": x["id"], "label": x["label"], "start": x["start"], "end": x["end"],
                             "title": x["label"], "text": x["text"], "credit": "商品主图：出版方店铺"} for x in tl.scenes],
    }
    save(proj / "composition/props.json", props)
    save(proj / "artifacts/props.json", props)
    save(proj / "artifacts/script.json", {
        "version": "1.0", "title": ep["title"], "total_duration_seconds": props["totalSeconds"],
        "sections": [{"id": x["id"], "label": x["label"], "text": x["text"], "start_seconds": x["start"],
                      "end_seconds": x["end"], "speaker_directions": "中文女声讲解；越南语读两遍 + 跟读空档。"}
                     for x in tl.scenes],
        "metadata": {"language": "zh+vi", "kind": "带货·图书",
                     "product": "基础越南语1-4（谭志词 徐方宇 林丽 曾添翼）+ 越英汉常用词汇分类手册（梁炳猛）· 世界图书出版公司",
                     "vi_source": "lang1000 viet1000_20260711_002314_all.json（词条或例句子串）" +
                                  ("；ma 六声调示例不在词库，为标准声调教学例" if num == "01" else ""),
                     "tts": {"engine": "edge", "zh": ZH, "vi": {k: v[1][0] for k, v in ep["viet"].items()}},
                     "claims_policy": "只用封面与出版社 App 介绍可核实的说法。"},
    })
    save(proj / "artifacts/publish.json", {
        "series_id": 2, "sub_series": "教材带货", "slug": f"viet_book_coso_{num}",
        "title": ep.get("pub_title", ep["title"]), "wechat_copy": ep.get("pub_title", ep["title"]),
        "idea_notes": "【带货】商品：《基础越南语》1–4 册 +《越英汉常用词汇分类手册》；发布时挂小黄车。",
        "publish_copy": ep["copy"] + "\n背单词用「越南语千词」，练字母用「学越南语字母」。\n\n" + TAGS,
        "credits": "教材图片：出版方商品主图；配音与剪辑：越南语千词。",
    })
    print(ep["pid"], f'{props["totalSeconds"]:.1f}s', flush=True)

    if render:
        renders = proj / "renders"
        renders.mkdir(exist_ok=True)
        out = renders / f"v{len(list(renders.glob('v*.mp4'))) + 1}.mp4"
        subprocess.run(["npx", "remotion", "render", str(proj / "composition/index.tsx"), ep["comp"], str(out),
                        f"--props={proj / 'composition/props.json'}", f"--public-dir={pub}", "--log=error", "--timeout=120000"],
                       cwd=REPO / "remotion-composer", check=True)
        print("  rendered", out.relative_to(REPO), flush=True)


async def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    nums = list(EPISODES) if (not args or args == ["all"]) else args
    for n in nums:
        await build(n, "--render" in sys.argv)


if __name__ == "__main__":
    asyncio.run(main())
