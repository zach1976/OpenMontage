#!/usr/bin/env python3
"""Render the September top-up quizzes with the original quiz frameworks."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LANG1000 = Path.home() / "projects" / "lang1000" / "marketing" / "video"
TH_DIR = LANG1000 / "series_listening_quiz"
VI_DIR = LANG1000 / "vietnamese"

sys.path.insert(0, str(TH_DIR))
import quiz_framework as tqf  # noqa: E402

sys.path.insert(0, str(VI_DIR))
import viet_quiz_framework as vqf  # noqa: E402

CAPS_TH = ["看泰文，记意思", "答完马上知道对错", "听发音，选意思", "零基础也能开始", "每天五题就够"]
CAPS_VI = ["看越南文，记意思", "答完马上知道对错", "听发音，选意思", "零基础也能开始", "每天五题就够"]


def thq(text: str, rom: str, opts: list[str], ans: int, i: int) -> dict:
    return {"thai": text, "rom": rom, "opts": opts, "ans": ans, "pick": ans, "cap": CAPS_TH[i]}


def viq(text: str, xie: str, opts: list[str], ans: int, i: int) -> dict:
    return {"viet": text, "xie": xie, "opts": opts, "ans": ans, "pick": ans, "cap": CAPS_VI[i]}


THAI = {
    "theme": {"PRIMARY": (34, 92, 128), "ACCENT": (210, 101, 62), "SOFT": (177, 211, 226), "BGTOP": (230, 243, 248)},
    "questions": [
        thq("เมนู", "谐音 梅努", ["菜单", "账单"], 0, 0),
        thq("ช้อน", "谐音 乔恩", ["勺子", "筷子"], 0, 1),
        thq("ส้อม", "谐音 所姆", ["叉子", "盘子"], 0, 2),
        thq("จาน", "谐音 占", ["碗", "盘子"], 1, 3),
        thq("เช็กบิล", "谐音 切克宾", ["结账", "点菜"], 0, 4),
    ],
}

VIET = [
    ({"PRIMARY": (38, 95, 142), "ACCENT": (211, 92, 60), "SOFT": (178, 211, 232), "BGTOP": (231, 242, 250), "BGBOT": (214, 230, 244)}, [
        viq("cơm", "谐音 哥姆", ["米饭", "面包"], 0, 0), viq("phở", "谐音 佛", ["米饭", "河粉"], 1, 1),
        viq("bánh mì", "谐音 班米", ["越式法包", "春卷"], 0, 2), viq("cà phê", "谐音 嘎啡", ["茶", "咖啡"], 1, 3),
        viq("nước", "谐音 诺克", ["水", "牛奶"], 0, 4)]),
    ({"PRIMARY": (21, 116, 105), "ACCENT": (211, 145, 45), "SOFT": (166, 219, 210), "BGTOP": (229, 246, 241), "BGBOT": (207, 232, 226)}, [
        viq("xe máy", "谐音 塞麦", ["摩托车", "汽车"], 0, 0), viq("ô tô", "谐音 欧多", ["公交车", "汽车"], 1, 1),
        viq("xe buýt", "谐音 塞比特", ["公交车", "火车"], 0, 2), viq("tàu hỏa", "谐音 道火", ["飞机", "火车"], 1, 3),
        viq("máy bay", "谐音 麦拜", ["飞机", "摩托车"], 0, 4)]),
    ({"PRIMARY": (110, 70, 143), "ACCENT": (34, 137, 125), "SOFT": (205, 185, 224), "BGTOP": (243, 235, 249), "BGBOT": (226, 215, 239)}, [
        viq("phòng", "谐音 房", ["房间", "前台"], 0, 0), viq("chìa khóa", "谐音 匙呀跨", ["房卡", "钥匙"], 1, 1),
        viq("lễ tân", "谐音 礼新", ["前台", "电梯"], 0, 2), viq("thang máy", "谐音 汤麦", ["楼梯", "电梯"], 1, 3),
        viq("hành lý", "谐音 行李", ["行李", "护照"], 0, 4)]),
]


def main() -> None:
    thai_only = "--thai-only" in sys.argv
    viet_only = "--viet-only" in sys.argv
    if not viet_only:
        # 原框架的 rom 行默认用拉丁字体；本系列要求显示中文谐音，因此换成同模板中文字体。
        tqf.FL = tqf.FZ
        th_project = REPO / "projects" / "thai-inventory-topup-202609"
        tqf.build(THAI["theme"], THAI["questions"], str(th_project / "composition" / "quiz_ep14_original_template"), str(th_project / "renders" / "ep01.mp4"))
    if not thai_only:
        vi_project = REPO / "projects" / "viet-inventory-topup-202609"
        for offset, (theme, questions) in enumerate(VIET, start=1):
            ep = 16 + offset
            vqf.build(theme, questions, str(vi_project / "composition" / f"quiz_ep{ep:02d}_original_template"), str(vi_project / "renders" / f"ep{offset:02d}.mp4"), episode_key=f"viet_quiz_ep{ep:02d}")


if __name__ == "__main__":
    main()
