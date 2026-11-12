#!/usr/bin/env python3
"""泰国蘸酱一集（2026-11-11 用户指令）：参考抖音「泰国人吃的酱比菜还多」（7679750465157082278），
那条只说「每道菜都有自己的酱」却没说是什么酱 —— 这一集把酱名、配什么菜、用什么做的讲清楚。

菜 → 酱的对应取那条视频里点到的：炸鸡、烤猪颈肉、海南鸡饭（白斩鸡）、烤虾、炸豆腐、肉丸、青芒果。
配料只写公认的主料，不写分量、不写「最正宗」之类无法核实的话。

走 ThaiLearningCards 卡片产线（与 202611 补片同一条链）：
    python3 scripts/seed_thai_sauce.py
    python3 scripts/build_thai_learning_batch.py thai-food-sauce-202611
    python3 scripts/synth_narration.py thai-food-sauce-202611
    python3 scripts/assemble_thai_learning_batch.py thai-food-sauce-202611
    python3 scripts/render_thai_learning_batch.py thai-food-sauce-202611
    python3 scripts/finalize_inventory_topup.py thai-food-sauce-202611
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import seed_inventory_topup_202611 as base  # noqa: E402

PID = "thai-food-sauce-202611"


def bd(*pairs):
    return [{"thai": t, "chinese": c, "spoken_chinese": c + "。"} for t, c in pairs]


SAUCES = [
    {"thai": "น้ำจิ้มไก่", "homophone": "南金 盖", "chinese": "甜辣鸡酱",
     "pair": {"dish": "炸鸡烤鸡", "icon": "🍗", "made": "辣椒加糖和醋熬成，甜辣"},
     "breakdown": bd(("น้ำจิ้ม", "蘸酱"), ("ไก่", "鸡"))},
    {"thai": "น้ำจิ้มแจ่ว", "homophone": "南金 交", "chinese": "伊森辣蘸酱",
     "pair": {"dish": "烤猪颈肉", "icon": "🥩", "made": "鱼露罗望子加炒米粉"},
     "breakdown": bd(("แจ่ว", "东北辣蘸酱"))},
    {"thai": "น้ำจิ้มเต้าเจี้ยว", "homophone": "南金 道接", "chinese": "豆酱蘸汁",
     "pair": {"dish": "海南鸡饭", "icon": "🍚", "made": "黄豆酱加姜蒜辣椒"},
     "breakdown": bd(("เต้าเจี้ยว", "黄豆酱"))},
    {"thai": "น้ำจิ้มซีฟู้ด", "homophone": "南金 西傅", "chinese": "海鲜蘸酱",
     "pair": {"dish": "烤虾海鲜", "icon": "🦐", "made": "青辣椒蒜头加青柠"},
     "breakdown": bd(("ซีฟู้ด", "海鲜"))},
    {"thai": "น้ำจิ้มเต้าหู้ทอด", "homophone": "南金 道虎 托", "chinese": "炸豆腐蘸酱",
     "pair": {"dish": "炸豆腐", "icon": "🥢", "made": "甜酸酱撒花生碎"},
     "breakdown": bd(("เต้าหู้", "豆腐"), ("ทอด", "炸"))},
    {"thai": "น้ำจิ้มลูกชิ้น", "homophone": "南金 路勤", "chinese": "肉丸蘸酱",
     "pair": {"dish": "烤肉丸", "icon": "🍢", "made": "酸甜带辣的红酱"},
     "breakdown": bd(("ลูกชิ้น", "肉丸"))},
    {"thai": "น้ำปลาหวาน", "homophone": "南巴 万", "chinese": "甜鱼露",
     "pair": {"dish": "青芒果", "icon": "🥭", "made": "鱼露熬糖加虾米辣椒"},
     "breakdown": bd(("น้ำปลา", "鱼露"), ("หวาน", "甜"))},
]
for _s in SAUCES:   # 旁白接着中文名把「配什么、什么做的」念出来 —— 这一集的重点就在这句
    _s["spoken_chinese"] = f"{_s['chinese']}。配{_s['pair']['dish']}，{_s['pair']['made']}。"
# 2026-11-11 用户：「蘸酱一定要有对应的图片」→ 每种酱一张 ChatGPT 生成的实物图（酱碗 + 配的菜），
# 放在卡片中间，替掉拆词格子（拆词那块地方给了图片）。图片由 scripts/import_sauce_photos.py 裁好放进 public。
for _i, _s in enumerate(SAUCES, 1):
    _s["photoSrc"] = f"series/{PID}/ep01/sauce_{_i:02d}.jpg"
    _s.pop("breakdown", None)
    _s["pair"].pop("icon", None)   # 有实物图了，面板里的 emoji 重复

ROW = ("泰国美食", "food_sauce", 1, "泰国7种蘸酱配什么菜", "泰国蘸酱", "泰国每道菜都有专配的酱，这7种先认识",
       "#B5432A", "#FFD36F", SAUCES)


def main() -> None:
    for s in SAUCES:
        assert len(s["pair"]["made"]) <= 14 and len(s["pair"]["dish"]) <= 6, s["pair"]
    base.seed(PID, "th", [ROW])
    # 开头口播（2026-11-11 用户：开始要说「泰国菜很神奇，各种菜都有不同的蘸酱」）+ 照片封面
    epf = REPO / "projects" / PID / "artifacts" / "episodes" / "ep01.json"
    ep1 = json.loads(epf.read_text())
    ep1["render_config"].update({
        "spoken_hook": "泰国菜很神奇，各种菜都有不同的蘸酱。最常见的七种，一起认识一下。",
        "cover_image_src": f"series/{PID}/ep01/cover_bowls.jpg",
        "cover_lines": ["泰国7种蘸酱", "配什么菜"],
        # 泰国味垫乐（2026-11-11 用户）：Pixabay「Bangkok Mirage」(u_98673jp944, 438526；用户在试听页四选一选的第 4 首)，免费商用、无需署名；
        # 已归一到 −14dB（与原通用垫乐同电平），倍率 2.5 让它在停顿处听得出来
        "music_source": f"projects/{PID}/assets/music/thai_bgm.mp3",
        "music_gain": 2.5,
    })
    epf.write_text(json.dumps(ep1, ensure_ascii=False, indent=2) + "\n")
    # seed() 的 slug 规则是 <prefix>_<safe>_ep<no>，这里改成有意义的；标题文案按这一集重写
    pb = REPO / "projects" / PID / "artifacts" / "publish_batch.json"
    data = json.loads(pb.read_text())
    ep = data["episodes"][0]
    ep["slug"] = "thai_food_sauce_7"
    listing = "\n".join(f"{s['thai']} {s['chinese']}｜配{s['pair']['dish']}：{s['pair']['made']}" for s in SAUCES)
    ep["publish_copy"] = (f"{ep['title']}\n泰国人吃的酱比菜还多，每道菜都有专配的酱。7 种最常见的蘸酱：叫什么、配什么菜、用什么做的。\n"
                          f"{listing}\n\n#泰语千词 #泰语 #泰国美食 #泰餐 #泰式蘸酱")
    ep["wechat_copy"] = f"{ep['title']} #泰语千词 #泰语 #泰国美食 #泰餐"
    pb.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    proj = json.loads((REPO / "projects" / PID / "project.json").read_text())
    proj["title"] = "泰国7种蘸酱配什么菜"
    (REPO / "projects" / PID / "project.json").write_text(json.dumps(proj, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
