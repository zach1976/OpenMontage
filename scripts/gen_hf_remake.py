#!/usr/bin/env python3
"""泰语高频词：把最早发布的 16 个词按「老版式变体」重做一遍。

来源与依据
----------
最早那一代是 2026-05-12 的 `lang1000/.../make_thai_*_video.py`（一词一脚本，已发 20 支）。
它成在四件事：**一条 12 个真用法 / 表格静音可扫读 / 逐行推进 / 汉字 icon 锚点**。
这一批把这四条原样保留，内容（12 条 + 谐音）也逐条沿用老脚本，**一个字不重编**。

相对老版改掉的：
  · 罗马音 → 中文谐音（用户 2026-08-30：「最后一列需要加中文谐音，不要之前的音标」）
  · 泰语按词分开显示（用户同日：「泰语的部分需要把词分开」），只分显示，配音仍连写
  · 12 条按语义分三组，每组末尾连读一遍 + 跟读空档（把系列的跟读纪律接回来）
  · 去掉烧屏 hashtag
  · **每集换底色 + 一张实拍配图**（用户 2026-08-30 指令）

注意：本系列**刻意不换版式**。CLAUDE.md 那条「每集必须换视觉语言」针对的是禅意那种
一集一个概念的系列；高频词是**格式化系列**，老版 20 支同一张脸正是它成功的原因之一
（观众一眼认出是这个栏目）。这里的变化项是**配色与配图**，由用户明确指定。

    python3 scripts/gen_hf_remake.py            # 全部 16 个
    python3 scripts/gen_hf_remake.py ao chai    # 只做某几个
"""
import ast, glob, json, os, re, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD = Path.home() / "projects/lang1000/marketing/video/series_high_freq_word"
TEMPLATE = REPO / "projects" / "thai-1000-hf-04-laew"      # 版式模板（แล้ว 那一集）
BGM_TARGET_DB = -13.8

# ── 16 个词：配色 / 配图检索词 / 三组标题 / 封面文案 ──────────────────────────
# 配色每集不同（用户指令）。ink 是底，ink2 是中心渐变，accent 是全片唯一强色。
WORDS = {
 "ao":   dict(th="เอา", xie="凹", zh="要 · 拿", ink="#1A0E0C", ink2="#2E1712", accent="#F0A868",
              photo="Thai street food stall vendor", groups=["点单：直接说要","要吃要喝","拿来拿去"],
              t1="在泰国点单", t2="一个字就够了"),
 "chai": dict(th="ใช่", xie="猜", zh="是 · 对", ink="#0A1618", ink2="#122A2C", accent="#E8DE72",
              photo="Thailand market conversation people", groups=["是 · 不是 · 对吗","不太确定的时候","确认与反问"],
              t1="泰国人一天", t2="要说几十次的字"),
 "dai":  dict(th="ได้", xie="呆", zh="能 · 可以", ink="#0C1024", ink2="#182142", accent="#F09A5B",
              photo="Bangkok skyline sunset", groups=["能不能 · 行不行","做得到 · 拿得到","口语里的万能收尾"],
              t1="泰语里最好用", t2="的一个字"),
 "dii":  dict(th="ดี", xie="底", zh="好", ink="#0E1A10", ink2="#1B301E", accent="#F2C46A",
              photo="Thai woman smiling wai greeting", groups=["夸人夸事","好不好 · 也好","好在哪里"],
              t1="泰国人夸人", t2="离不开这个字"),
 "duu":  dict(th="ดู", xie="嘟", zh="看", ink="#140C1E", ink2="#241536", accent="#8FD0E8",
              photo="Bangkok cinema night street", groups=["看什么","怎么看","看起来 · 照顾"],
              t1="一个看字", t2="泰国人用出十二种"),
 "hai":  dict(th="ให้", xie="嗨", zh="给", ink="#1A0A10", ink2="#301420", accent="#F2B0B0",
              photo="Thai monks alms giving morning", groups=["给东西给人","替我做 · 帮我做","让 · 叫 · 使"],
              t1="泰语的给", t2="比中文管得宽"),
 "khaw": dict(th="ขอ", xie="考", zh="要 · 请求", ink="#0A1226", ink2="#132244", accent="#F08A6A",
              photo="Thai restaurant table menu", groups=["点单要东西","客气话","请求与借过"],
              t1="在泰国开口", t2="先学这个字"),
 "khong":dict(th="ของ", xie="抗", zh="的 · 东西", ink="#141416", ink2="#242428", accent="#C8E06A",
              photo="Thailand souvenir market stall", groups=["谁的","什么东西","真假与买卖"],
              t1="泰语说谁的", t2="就靠这个字"),
 "kin":  dict(th="กิน", xie="京", zh="吃", ink="#101A0C", ink2="#1E3016", accent="#F0783C",
              photo="Pad Thai Thai food", groups=["吃什么","怎么吃","吃完了没"],
              t1="泰国人问候", t2="从吃饭开始"),
 "maa":  dict(th="มา", xie="妈", zh="来", ink="#0A1020", ink2="#14213C", accent="#F0C878",
              photo="Bangkok train station platform", groups=["来 · 过来","从哪来 · 来做什么","来了没 · 一直"],
              t1="泰语的来", t2="不只是来"),
 "mii":  dict(th="มี", xie="米", zh="有", ink="#1A1008", ink2="#2E1E12", accent="#7FD0B0",
              photo="Thai fruit market stall", groups=["有没有","有什么","有人 · 有事"],
              t1="问有没有", t2="泰国人只用一个字"),
 "pai":  dict(th="ไป", xie="拜", zh="去", ink="#08161E", ink2="#0F2A38", accent="#F09040",
              photo="Tuk tuk Bangkok street", groups=["去哪儿","走 · 出发","去做什么"],
              t1="在泰国打车", t2="先会这个字"),
 "ruu":  dict(th="รู้", xie="鲁", zh="知道", ink="#0E1218", ink2="#1A222E", accent="#6FC0F0",
              photo="Thai school students classroom", groups=["知不知道","懂 · 认识","知道了 · 才知道"],
              t1="泰语说知道", t2="有三种说法"),
 "tham": dict(th="ทำ", xie="探", zh="做", ink="#16140A", ink2="#282412", accent="#E0C040",
              photo="Thai cooking street kitchen", groups=["做什么","做事 · 做饭","做好了 · 做不了"],
              t1="一个做字", t2="干什么都能说"),
 "yaak": dict(th="อยาก", xie="亚", zh="想 · 要", ink="#160C1A", ink2="#281630", accent="#F0A0C8",
              photo="Mango sticky rice Thai dessert", groups=["想吃想喝","想去想做","不想 · 很想"],
              t1="泰语说我想", t2="就这一个字"),
 "yuu":  dict(th="อยู่", xie="优", zh="在", ink="#0A140E", ink2="#12261A", accent="#D8D078",
              photo="Thai village house rural", groups=["在哪里","在家 · 在忙","还在 · 住在"],
              t1="问在哪儿", t2="泰国人这么说"),
}

# 机械切分会劈坏的复合词（`ดูแล` 是「照顾」，不是 ดู+แล）
SPLIT_OVERRIDE = {
    "ดูแลตัว": ["ดูแล", "ตัว"],
    "ขอโทษ":   ["ขอโทษ"],      # 固定说法「对不起」，拆开反而误导
    "ของขวัญ": ["ของขวัญ"],    # 礼物；ขวัญ 单用现代已不通
    "ของฝาก":  ["ของฝาก"],     # 土特产，同上
}
XIE_FIX = {"考威拉挪": "考威挪", "米阿来邦": "米来邦"}   # 谐音一律 ≤3 字


def old_rows(slug: str) -> list:
    s = (OLD / f"make_thai_{slug}_video.py").read_text(encoding="utf-8")
    m = re.search(r"PAGES[^=]*=\s*\[(.*?)\n\]\n", s, re.S)
    pages = ast.literal_eval("[" + m.group(1) + "]")
    return [r for pg in pages for r in pg]


def split_thai(chunk: str, target: str) -> list[str]:
    """显示用分词：只在目标词处切开，其余整块保留。
    **只影响画面** —— 配音仍用连写，泰语 TTS 遇空格会断读。"""
    if chunk in SPLIT_OVERRIDE:
        parts = SPLIT_OVERRIDE[chunk]
    else:
        i = chunk.index(target)
        parts = [p for p in (chunk[:i], target, chunk[i + len(target):]) if p]
    assert "".join(parts) == chunk, (chunk, parts)      # 分词必须还原成原词
    return parts


def normalize_bgm(src: Path, dst: Path) -> None:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src),
                          "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    adj = BGM_TARGET_DB - float(re.search(r"mean_volume:\s*(-?[\d.]+)", out).group(1))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                    "-af", f"volume={adj:.2f}dB", "-b:a", "192k", str(dst)], check=True)


def fetch_photo(query: str, dst: Path) -> dict | None:
    """配图走 Wikimedia（本机唯一能用的图源；其余 12 个工具全不通）。
    只取 CC 授权的实拍，署名写进 artifacts 备查。"""
    sys.path.insert(0, str(REPO))
    from tools.video.stock_sources.wikimedia import WikimediaSource
    from tools.video.stock_sources.base import SearchFilters
    w = WikimediaSource()
    for c in w.search(query, SearchFilters(kind="image", per_page=6)):
        try:
            w.download(c, dst)
            if dst.exists() and dst.stat().st_size > 40000:
                # 压到 1080 宽、去色降对比 —— 它是底纹不是主角
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(dst),
                                "-vf", "scale=1080:-2,eq=saturation=0.42:contrast=1.06,"
                                       "gblur=sigma=0.6", str(dst.with_suffix(".jpg"))], check=True)
                if dst.suffix != ".jpg":
                    dst.unlink(missing_ok=True)
                return dict(query=query, source_url=c.source_url, credit=c.source_url)
        except Exception:
            continue
    return None


def build(slug: str, no: int) -> None:
    W = WORDS[slug]
    pid = f"thai-1000-hfx-{no:02d}-{slug}"
    proj = REPO / "projects" / pid
    (proj / "artifacts").mkdir(parents=True, exist_ok=True)
    (proj / "renders").mkdir(exist_ok=True)
    for sub in ("composition/public/fonts", "composition/public/app"):
        if not (proj / sub).exists():
            shutil.copytree(TEMPLATE / sub, proj / sub)
    (proj / "composition/public/music").mkdir(parents=True, exist_ok=True)
    normalize_bgm(TEMPLATE / "composition/public/music/bgm.mp3",
                  proj / "composition/public/music/bgm.mp3")

    photo = None
    pdst = proj / "composition/public/img/photo.jpg"
    pdst.parent.mkdir(parents=True, exist_ok=True)
    if not pdst.exists():
        photo = fetch_photo(W["photo"], pdst)
        if photo:
            (proj / "artifacts/photo_credit.json").write_text(
                json.dumps(photo, ensure_ascii=False, indent=2), encoding="utf-8")

    rows_src = old_rows(slug)
    sections, units, rows = [], [], []
    sections.append(dict(id="s00_hook", text=f'泰语高频词：{W["th"]}。一个词，十二种用法。'))
    units += [dict(id="s00_hook_a", section="s00_hook", lang="zh", text="泰语高频词"),
              dict(id="s00_hook_b", section="s00_hook", lang="th", text=W["th"]),
              dict(id="s00_hook_c", section="s00_hook", lang="zh", text="一个词，十二种用法。")]
    for pi in range(3):
        title = W["groups"][pi]
        sections.append(dict(id=f"p{pi+1}_title", text=title))
        units.append(dict(id=f"p{pi+1}_title_zh", section=f"p{pi+1}_title", lang="zh", text=title))
        grp = rows_src[pi * 4:(pi + 1) * 4]
        for ri, (icon, zh, th, _rom, xie) in enumerate(grp, 1):
            rid = f"p{pi+1}r{ri}"
            sections.append(dict(id=rid, text=f"{zh} → {th}"))
            units += [dict(id=f"{rid}_zh", section=rid, lang="zh", text=zh),
                      dict(id=f"{rid}_th", section=rid, lang="th", text=th)]
            rows.append(dict(id=rid, page=pi + 1, icon=icon, zh=zh, th=th,
                             thParts=split_thai(th, W["th"]),
                             rom=_rom, xie=XIE_FIX.get(xie, xie)))
        sections.append(dict(id=f"p{pi+1}_echo", text="（本组四条连读一遍，跟读）"))
        units.append(dict(id=f"p{pi+1}_echo_th", section=f"p{pi+1}_echo", lang="th",
                          text="　".join(r[2] for r in grp)))
    sections.append(dict(id="s10_outro", text="泰语千词，在泰国生活够用了。"))
    units.append(dict(id="s10_outro_zh", section="s10_outro", lang="zh",
                      text="泰语千词，在泰国生活够用了。"))

    (proj / "artifacts/script.json").write_text(json.dumps({
        "version": "1.0", "project_id": pid, "sections": sections,
        "metadata": {
            "word": {"th": W["th"], "rom": "", "zh": W["zh"], "xie": W["xie"]},
            "origin": f"重做自 lang1000/.../make_thai_{slug}_video.py（2026-05-12，已发布）。"
                      "12 条用法与谐音逐条沿用老脚本，一个字不重编；"
                      "改动：罗马音→中文谐音、泰语按词分开显示、12 条分三组每组末尾连读跟读、"
                      "去掉烧屏 hashtag、换底色并加一张 Wikimedia 实拍配图。",
            "tts": {"engine": "edge",
                    "voices": {"zh": "zh-CN-XiaoxiaoNeural", "th": "th-TH-PremwadeeNeural"},
                    "rates": {"th": "-28%"}},
            "tts_units": units,
            "pages": [{"title": W["groups"][i],
                       "rows": [r["id"] for r in rows if r["page"] == i + 1]} for i in range(3)],
            "rows": rows,
            "badge": f"泰语高频词 · No.{no:02d}",
            "poster": {"t1": W["t1"], "t2": W["t2"]},
            "palette": {"ink": W["ink"], "ink2": W["ink2"], "accent": W["accent"]},
            "photo": W["photo"],
        }}, ensure_ascii=False, indent=2), encoding="utf-8")
    (proj / "project.json").write_text(json.dumps({
        "version": "1.0", "project_id": pid,
        "title": f'泰语千词 · 高频词 {no:02d} {W["th"]}（老版式重做）',
        "pipeline_type": "animated-explainer"}, ensure_ascii=False, indent=2), encoding="utf-8")
    (proj / "artifacts/edit_decisions.json").write_text(json.dumps({
        "version": "1.0", "project_id": pid, "render_runtime": "remotion",
        "composition_mode": "atelier", "renderer_family": "bespoke",
        "bespoke": {"entry": str(proj / "composition/index.tsx"), "composition_id": "HF",
                    "props_path": str(proj / "composition/props.json"),
                    "public_dir": str(proj / "composition/public"), "crf": 18,
                    "art_direction": f'底 {W["ink"]} / 强色 {W["accent"]}；配图「{W["photo"]}」压在表格下方。'
                                     "版式沿用 2026-05-12 老版：一条 12 用、表格静音可扫读、逐行推进、"
                                     "汉字 icon 锚点；讲过的行打勾沉下去不还原。"}},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f'✓ {pid:28} {W["th"]:6} 配图 {"有" if pdst.exists() else "无"}  {W["ink"]} / {W["accent"]}')


def main() -> int:
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    for i, slug in enumerate(WORDS, 1):
        if only and slug not in only:
            continue
        build(slug, i)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
