#!/usr/bin/env python3
"""Materialize reviewed Thai series episode sources from the existing Thai lexicon.

The episode plan is intentionally explicit here; this command is only used to
freeze those selections as project artifacts before synthesis and rendering.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEX = Path("/Users/zhenyusong/projects/lang1000/apps/lang1000_all/assets/data/th")


def words(name: str) -> list[dict]:
    return json.loads((LEX / f"words_{name}.json").read_text())["words"]


def clean_roman(text: str) -> list[str]:
    text = "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))
    text = text.replace("...", " ").replace("/", " ")
    text = re.sub(r"[^a-zɔʉəɯ]+", " ", text)
    return [x for x in text.split() if x]


def sound(token: str) -> str:
    plain = "".join(c for c in unicodedata.normalize("NFKD", token) if not unicodedata.combining(c))
    exact = {
        "mai":"麦", "chai":"猜", "khrap":"卡普", "kha":"卡", "khun":"昆", "chan":"产", "phom":"碰", "arai":"阿莱", "rai":"莱",
        "dai":"代", "pai":"拜", "maa":"吗", "mii":"米", "nii":"尼", "nan":"南", "na":"纳", "noi":"诺伊", "duai":"对",
        "chuai":"吹", "thao":"套", "yang":"央", "ngai":"奈", "thii":"替", "nai":"乃", "yu":"优", "yuu":"优", "laew":"莱奥",
        "jer":"遮", "gan":"甘", "kho":"口", "thot":"托", "sawat":"萨瓦", "dii":"滴", "jing":"晶", "roo":"若", "pen":"奔",
        "sabai":"萨拜", "mak":"马", "maak":"马", "ao":"奥", "kin":"根", "khao":"靠", "naam":"南", "ahan":"阿含", "aroi":"阿洛伊",
        "phet":"佩", "waan":"万", "kem":"肯", "priao":"布里奥", "ron":"隆", "yen":"烟", "ya":"雅", "moh":"摸", "maw":"摸",
        "rot":"洛", "tamruat":"丹洛", "riak":"里亚", "fai":"怀", "hai":"海", "jep":"杰", "hua":"华", "thong":"通",
        "puat":"布阿", "khai":"开", "phae":"配", "ai":"爱", "lom":"隆", "fon":"丰", "daet":"代", "thalee":"塔雷",
        "suk":"素", "sao":"扫", "groot":"格洛", "glua":"格鲁阿", "tok":"多", "jai":"摘", "nueai":"女艾", "buea":"布厄",
        "som":"宋", "tam":"丹", "tom":"冬", "yam":"央", "kung":"贡", "phat":"帕", "thai":"泰", "mamuang":"马芒",
        "kluai":"古艾", "thurian":"突里安", "mangkhut":"曼库", "maphrao":"马炮", "malakaw":"马拉高", "sapparot":"萨巴洛",
        "kaeo":"给奥", "khaw":"靠", "niao":"尼奥", "mu":"木", "kai":"盖", "pla":"巴拉", "phak":"帕", "phrik":"普力",
    }
    if plain in exact:
        return exact[plain]
    replacements = [("kh","科"),("ph","坡"),("th","塔"),("ch","查"),("ng","恩"),("kr","格拉"),("pr","布拉"),("tr","达拉"),("r","乐"),("l","拉"),("m","马"),("n","那"),("p","巴"),("b","波"),("t","达"),("d","德"),("k","嘎"),("g","格"),("f","法"),("s","萨"),("h","哈"),("w","哇"),("y","雅"),("j","摘")]
    for prefix, zh in replacements:
        if plain.startswith(prefix):
            return zh + ("伊" if "i" in plain else "奥" if "o" in plain or "ɔ" in plain else "阿")
    return "阿"


def homophone(roman: str) -> str:
    return " ".join(sound(x) for x in clean_roman(roman))


def pick(specs: list[tuple[str, int, int]]) -> list[dict]:
    result = []
    for category, start, count in specs:
        result.extend(words(category)[start:start + count])
    return result


def item(row: dict) -> dict:
    chinese = row["chineseTranslation"].replace("/", "、")
    return {"thai": row["targetText"], "homophone": homophone(row["targetRomanization"]), "chinese": chinese, "spoken_chinese": chinese.replace("（", "，").replace("）", ""), "note": "旅行和日常交流中的高频说法。"}


def existing_items(project: Path) -> list[dict]:
    episode = project / "artifacts" / "episodes" / "ep01.json"
    if episode.exists():
        return json.loads(episode.read_text())["items"]
    return json.loads((project / "artifacts" / "script.json").read_text())["metadata"]["items"]


def write_series(project_id: str, series_title: str, series_name: str, accent: str, accent2: str, mode: str, plans: list[dict]) -> None:
    project = REPO / "projects" / project_id
    out = project / "artifacts" / "episodes"
    out.mkdir(parents=True, exist_ok=True)
    first = existing_items(project)
    for number, plan in enumerate(plans, start=1):
        rows = first if number == 1 else [item(x) for x in pick(plan["sources"])][:plan["count"]]
        source = {
            "id": f"ep{number:02d}", "series_title": series_title, "title": f"{series_title} {number:02d}：{plan['topic']}",
            "voice_energy": "medium-high", "items": rows,
            "render_config": {
                "series_name": series_name, "episode": f"NO.{number:02d}", "topic": plan["topic"], "hook": plan["hook"],
                "accent": accent, "accent2": accent2, "mode": mode, "cover_end": 2.4, "language_gap": 0.16,
                "minimum_card_seconds": 3.5 if mode != "cards" else 3.6, "tail_gap": 0.32, "outro_seconds": 3.5,
                "music_source": "projects/thai-1000-dialogue-01-ao/assets/music/bgm.mp3"
            }
        }
        (out / f"ep{number:02d}.json").write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    catch = [
        ("经典高频", "泰国人天天挂嘴边的12句话", []),
        ("情绪反应", "开心、生气、害怕都能马上说", [("emotions",0,12)]),
        ("聊天回应", "聊天不冷场的12个高频回应", [("daily_conversation",4,8),("common_phrases",4,4)]),
        ("催促指令", "让对方马上听懂你的意思", [("verbs",0,12)]),
        ("夸奖吐槽", "夸人和吐槽，泰语这样说", [("adjectives",0,12)]),
        ("礼貌寒暄", "见面、道谢、告别一次学会", [("daily_conversation",0,12)]),
        ("网络口头禅", "刷手机最常见的12个说法", [("social_internet",8,12)]),
        ("同意拒绝", "答应还是拒绝，说得自然一点", [("daily_conversation",4,12)]),
        ("道歉感谢", "把谢谢和对不起说到位", [("common_phrases",4,8),("daily_conversation",0,4)]),
        ("砍价购物", "逛夜市砍价就靠这12句", [("shopping",0,12)]),
        ("惊讶感叹", "遇到意外时的泰式反应", [("emotions",2,12)]),
    ]
    emergency = [
        ("呼救报警", "真遇到事，先把这10句说出来", []),
        ("诊所看病", "到诊所先会说这10个词", [("medical",0,10)]),
        ("描述症状", "哪里不舒服，直接这样说", [("medical",2,10)]),
        ("受伤处理", "受伤时把情况说明白", [("emergency",4,4),("medical",18,6)]),
        ("迷路寻人", "迷路或走散，马上求助", [("emergency",8,5),("directions_places",0,5)]),
        ("盗窃求助", "东西被偷，报警要会说", [("emergency",1,9),("common_phrases",8,1)]),
        ("交通事故", "路上出事故先说清这10个词", [("transportation",0,10)]),
        ("恶劣天气", "暴雨高温来时先保安全", [("weather",0,10)]),
        ("药店买药", "到药店说明需求不慌张", [("medical",5,10)]),
        ("证件遗失", "护照钱包丢失这样求助", [("emergency",8,5),("banking",0,5)]),
        ("食物中毒", "吃坏肚子，症状这样说", [("medical",18,10)]),
        ("中暑脱水", "太热不舒服，及时求助", [("weather",0,5),("medical",1,5)]),
        ("过敏虫咬", "过敏或被虫咬，别说不清", [("medical",8,8),("animals",0,2)]),
    ]
    food = [
        ("招牌名菜", "到泰国，这10道菜要会念", []),
        ("街头小吃", "逛夜市看到这些就会点", [("dining",20,10)]),
        ("泰式饮品", "咖啡奶茶果汁一次会点", [("dining",13,2),("bar_nightlife",0,8)]),
        ("食材味道", "酸甜辣咸，口味说明白", [("dining",4,8),("vegetables",0,2)]),
        ("餐厅必备", "入座点餐结账全都用得上", [("dining",0,10)]),
        ("忌口素食", "不吃什么，提前说清楚", [("vegetables",0,6),("dining",4,4)]),
        ("粉面加料", "点粉点面，配料自己选", [("dining",8,10)]),
        ("热带水果", "水果摊最常见的10种水果", [("fruits",1,10)]),
        ("青木瓜沙拉", "辣度、甜度、配料这样选", [("thai_culture",8,4),("vegetables",1,6)]),
    ]
    conv = lambda rows, count: [{"topic": a, "hook": b, "sources": c, "count": count} for a,b,c in rows]
    write_series("thai-1000-catchphrase-series-01-11", "泰语千词·经典口头禅", "泰语千词 · 经典口头禅", "#168493", "#F5C45A", "grid", conv(catch, 12))
    write_series("thai-1000-emergency-series-01-13", "泰语千词·紧急应急", "泰语千词 · 紧急应急", "#C9473B", "#F4C95D", "cards", conv(emergency, 10))
    write_series("thai-1000-food-series-01-09", "泰语千词·泰国美食", "泰语千词 · 泰国美食", "#C95F2E", "#F1C453", "food", conv(food, 10))


if __name__ == "__main__":
    main()
