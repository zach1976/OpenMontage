#!/usr/bin/env python3
"""已发布条目「改三成重发」（2026-11-10 用户指令）：新标题 + 新钩子句 + 改写收尾，slug 加 _r2 作为新视频。

事实、词表、例句一个不动；只换说法。输出 artifacts 外的一份 variants JSON，交给
    python3 scripts/push_to_videopublisher.py <pids...> --variants=<json>
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1])          # published49.json（key/slug/title/copy）
OUT = Path(sys.argv[2])
TITLES_TSV = Path(sys.argv[3])   # 全库标题（查撞名）

# key → (新标题, 新钩子句)
NEW = {
    "thai-1000-hfx-02-chai": ("泰语里的是和对都靠它", "是、对、没错，泰国人一个 ใช่（谐音「猜」）全搞定。"),
    "thai-1000-hfx-11-mii": ("泰语有没有就看这个字", "有没有、有什么，泰国人都用 มี（谐音「米」）。"),
    "viet-1000-hfx-02-co": ("越南人问有没有就一句", "有没有、有了没，越南人全用 Có（谐音「够」）。"),
    "viet-1000-hfx-04-la": ("越南语我是从这里开始", "我是、是谁、是什么，开口先学 Là（谐音「堆」）。"),
    "viet-1000-hfx-05-muon": ("越南语想吃想去一字搞定", "想吃想喝想出门，越南语都是 Muốn（谐音「蒙」）。"),
    "viet-1000-hfx-06-cho": ("越南语给这个字用处多", "给我、给你、请给，越南语一个 Cho（谐音「桌」）全包。"),
    "viet-1000-hfx-10-den": ("越南语到和来是同一个字", "到这里、到点了、来了，越南语都说 Đến（谐音「登」）。"),
    "viet-1000-hfx-11-biet": ("越南语知道和会一字两用", "知道、会做，越南人都说 Biết（谐音「堆」）。"),
    "viet-1000-hfx-12-lay": ("越南语拿字还能这样用", "拿东西、取钱取票，越南语都是 Lấy（谐音「莱」）。"),
    "viet-1000-hfx-14-xem": ("越南语看字的12种用法", "看电影、看时间、给我看，越南语一个 Xem（谐音「现」）。"),
    "viet-1000-hfx-15-tot": ("越南语夸人就用这个字", "很好、太好了、好人，越南人夸人都用 Tốt（谐音「热」）。"),
    "thai-book-jichu-01-consonants": ("泰语入门先认这9个辅音", "泰文 44 个辅音别一口气背，先认 9 个中辅音。"),
    "thai-book-jichu-02-tones": ("泰语五个声调一次听懂", "同一个音换个声调，意思就全变了。"),
    "thai-book-jichu-03-day-one": ("刚到泰国先学这5句", "落地泰国第一天，这 5 句天天用得上。"),
    "thai-book-jichu-04-roadmap": ("泰语从零到读课文四本书", "零基础学泰语，四本书走完一条完整的路。"),
    "thai-book-jichu-05-three-steps": ("泰语教材音频三步用法", "教材配的音频，按这三步用效果最好。"),
    "thai-book-jichu-06-numbers": ("泰语从一数到十", "一到十先数熟，买东西问价都靠它。"),
    "thai-book-jichu-07-taxi": ("在泰国问路4句就够", "在泰国迷路不慌，问路就这 4 句。"),
    "thai-book-jichu-08-particles": ("泰语句尾小尾巴怎么加", "泰国人说话礼不礼貌，就看句尾这个小尾巴。"),
    "thai-book-jichu-14-family": ("泰语兄弟姐妹怎么叫", "哥哥姐姐弟弟妹妹，泰语只要拼两个词。"),
    "thai-book-jichu-15-weekday": ("泰语问今天星期几", "今天星期几、哪天上课，泰语这样问。"),
    "thai-book-jichu-18-phone": ("用泰语打电话4句话", "接打电话不卡壳，记住这 4 句。"),
    "thai-book-jichu-19-sick": ("泰国看病常用5句", "在泰国身体不舒服，先会说这几句。"),
    "thai-book-jichu-20-seasons": ("泰国只有热季雨季凉季", "泰国没有四季，一年只分三季。"),
    "viet-book-coso-01-tones": ("越南语声调一共有六个", "同一个 ma，换个声调就是六个意思。"),
    "viet-book-coso-02-hanviet": ("这些越南语听着像中文", "越南语里藏着很多中文词，一听就懂。"),
    "viet-book-coso-03-day-one": ("刚到越南先学这5句", "落地越南第一天，这 5 句最常用。"),
    "viet-book-coso-04-handbook": ("越南语单词按场景记", "单词别死记，按场景背更容易用出来。"),
    "viet-book-coso-05-numbers": ("越南语从一数到十", "一到十先数熟，问价付钱都用得上。"),
    "viet-book-coso-06-taxi": ("越南打车跟司机说这5个词", "在越南打车，跟司机说这 5 个词就够。"),
    "viet-book-coso-07-weekdays": ("越南人的星期一是第二", "越南语的星期很特别，星期一叫「第二」。"),
    "viet-book-coso-08-sick": ("越南看病常用5句", "在越南身体不舒服，先会说这 5 句。"),
    "viet-book-coso-09-fruits": ("越南水果用越南语怎么说", "去越南吃水果，名字先学会。"),
    "viet-book-coso-10-hotel": ("越南酒店前台5个词", "住酒店办入住退房，前台常用这 5 个词。"),
    "viet-book-coso-11-colors": ("越南语说颜色先加一个字", "越南语的颜色，前面都要先加一个 màu。"),
    "viet-book-coso-12-family": ("越南语一家人怎么称呼", "爸爸妈妈爷爷奶奶，越南语这样叫。"),
    "viet-inventory-topup-202611/ep01": ("越南语职业5词听力测验", "老师医生警察怎么说？听越南语猜职业。"),
    "viet-inventory-topup-202611/ep06": ("越南语一点点有五种说法", "要一点、少一点、再多一点，越南语说法不一样。"),
    "viet-inventory-topup-202609/ep01": ("听越南语猜美食5个词", "听越南语，猜猜是哪道越南美食。"),
    "viet-inventory-topup-202609/ep02": ("听越南语猜交通5个词", "听越南语，猜猜是哪种交通工具。"),
    "viet-inventory-topup-202609/ep03": ("听越南语猜酒店5个词", "听越南语，猜猜酒店里的这些词。"),
    "viet-inventory-topup-202609/ep05": ("越南咖啡店少糖打包这样说", "在越南点咖啡，要少糖还要打包，这样说。"),
    "viet-inventory-topup-202609/ep07": ("越南语说日期时间5句", "几号、几点、星期几，越南语这 5 句最常用。"),
    "viet-inventory-topup-202609/ep08": ("累了就歇越南语这样说", "累了就歇一歇，但别放弃。"),
    "viet-inventory-topup-202609/ep09": ("不必快只要不停", "走得慢没关系，不停下来就是在前进。"),
    "viet-inventory-topup-202609/ep11": ("越南电梯被困救急8句", "在越南被困电梯别慌，这 8 句能救急。"),
    "viet-inventory-topup-202609/ep13": ("越南语委婉说不的8句", "不想直接拒绝？越南人常这样委婉地说不。"),
    "viet-inventory-topup-202609/ep14": ("越南名字安的几种意思", "越南名字 Anh，可不止一种意思。"),
    "viet-inventory-topup-202609/ep16": ("越南甜汤这8个词先收藏", "去越南吃甜汤，这 8 个词先记下来。"),
}
TITLE_RE = re.compile(r"^[一-鿿0-9]{6,16}$")


def rewrite(key: str, old_copy: str, title: str, hook: str) -> str:
    lines = old_copy.split("\n")
    body = lines[1:]
    if body:
        if "book" in key:        # 教材：第二行是知识点，钩子插在它前面，知识点不动
            body.insert(0, hook)
        elif "topup" in key:     # 补片：原钩子 + 套话整行换掉
            body[0] = hook + "听一遍越南语，对一下中文和谐音，跟着念出来。"
        else:                    # 高频词：原钩子行换成新钩子（新钩子里带着这个词和谐音）
            body[0] = hook
    out = []
    for ln in body:
        ln = ln.replace("先听越南语，再看中文和谐音，收藏起来慢慢练。", "听一遍越南语，对一下中文和谐音，跟着念出来。")
        ln = ln.replace("背单词用「泰语千词」，练字母用「学泰文字母」。", "背单词可以用「泰语千词」，练字母可以用「学泰文字母」。")
        ln = ln.replace("背单词用「越南语千词」，练字母用「学越南语字母」。", "背单词可以用「越南语千词」，练字母可以用「学越南语字母」。")
        out.append(ln)
    if "hfx" in key:  # 三组用法倒序排（每组＝【标题】+ 一行词组），分隔符换掉；去掉原收尾句
        heads = [i for i, ln in enumerate(out) if ln.startswith("【")]
        if len(heads) >= 2:
            groups = [out[h:h + 2] for h in heads]
            rest_after = out[heads[-1] + 2:]
            out = out[:heads[0]] + [ln for g in reversed(groups) for ln in g] + rest_after
        out = [ln.replace(" · ", " ／ ") for ln in out if "跟着念一遍就记住了" not in ln and "跟着读一遍就记住" not in ln]
    if "book" in key:
        out = [re.sub(r"内容与原声取自(《[^》]+》第 \d+ 册第 \d+ 课)，1–4 册附音频。", r"这一课的原句和原声出自\1，整套 1–4 册都配音频。", ln) for ln in out]
        out = [ln.replace("原句与原声取自", "原句和原声都出自").replace("读音与例句取自", "读音和例句都出自")
                 .replace("规则与男女原声取自", "规则和男女原声都出自").replace(" / ", "、") for ln in out]
        out = [("配套教材：" + ln) if ln.startswith("《") else ln for ln in out]
        # 知识点行开头那段与标题重复的引子（「在越南打车跟司机说 5 个词：」）去掉，钩子句已经说过
        out = [re.sub(r"^[^：:]{4,22}[：:]", "", ln, count=1) if i == 1 else ln for i, ln in enumerate(out)]
        out = [ln.replace("背单词可以用「泰语千词」，练字母可以用「学泰文字母」。", "想背单词，用「泰语千词」；想练字母，用「学泰文字母」。")
                 .replace("背单词可以用「越南语千词」，练字母可以用「学越南语字母」。", "想背单词，用「越南语千词」；想练字母，用「学越南语字母」。")
                 .replace(" #带货", " #跟着教材学 #带货") for ln in out]
    # 高频词在标签行前补一句收尾
    if "hfx" in key:
        tag_i = next((i for i, ln in enumerate(out) if ln.startswith("#")), len(out))
        out.insert(tag_i, "跟着念一遍，下次直接开口。")
    return "\n".join([title] + out)


def main() -> int:
    items = json.loads(SRC.read_text())
    taken = {ln.split("\t")[1] for ln in TITLES_TSV.read_text().splitlines() if ln.count("\t") >= 2}
    seen, variants = set(), {}
    for it in items:
        title, hook = NEW[it["key"]]
        assert TITLE_RE.match(title), title
        assert title not in taken and title not in seen and title != it["title"], f"撞名：{title}"
        seen.add(title)
        variants[it["key"]] = {"slug": it["slug"] + "_r2", "title": title,
                               "publish_copy": rewrite(it["key"], it["copy"], title, hook),
                               "idea_notes": "【重发新版】美化重渲后改写标题文案作为新视频；原条目 " + it["slug"]}
    assert len(variants) == len(items) == len(NEW)
    OUT.write_text(json.dumps(variants, ensure_ascii=False, indent=1))
    print(f"{len(variants)} 条改写完成 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
