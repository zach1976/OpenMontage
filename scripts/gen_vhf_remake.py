#!/usr/bin/env python3
"""越南语高频词：把已发布的 15 个词按「老版式变体」重做一遍。

与泰语那批（`gen_hf_remake.py`）是同一套做法，只换语言层：
内容逐条沿用 `lang1000/.../vietnamese/viet_highfreq.py`（12 条 + 谐音，已发布过），
**一个字不重编**；改的是罗马音→谐音（越南语老版本来就是谐音）、按词分开显示、
12 条分三组每组连读跟读、换底色、加 Wikimedia 实拍配图。

两处和泰语不同：
  · **越南语本来就用空格分词**，所以显示分词是天然安全的，不需要覆盖表。
  · 老脚本**没有汉字 icon**（泰语那批有）。这里从中文释义里推：
    去掉目标词的意思，取第一个还没被本集占用的字 —— 同一集 12 个 icon 不重复才有锚点作用。

    python3 scripts/gen_vhf_remake.py          # 全部 15 个
    python3 scripts/gen_vhf_remake.py o co     # 只做某几个
"""
import ast, json, os, re, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLDV = Path.home() / "projects/lang1000/marketing/video/vietnamese"
TEMPLATE = REPO / "projects" / "thai-1000-hf-04-laew"
VIETFONT = REPO / "projects" / "viet-1000-name-01-nguyen" / "composition/public/fonts"
BGM_TARGET_DB = -13.8

# 配色每集不同，且与泰语那 16 支全部错开
WORDS = {
 "o":    dict(ink="#0B1512", ink2="#152621", accent="#7ED8C0", photo="Hanoi old quarter street",
              groups=["在哪里","在什么地方","住 · 留下"], t1="越南语说在", t2="一个字全包"),
 "co":   dict(ink="#1C1208", ink2="#301F10", accent="#F5C542", photo="Vietnam market fruit stall",
              groups=["有什么","有没有 · 有了","可以 · 也许"], t1="问有没有", t2="越南人只用一个字"),
 "di":   dict(ink="#0A1220", ink2="#14213A", accent="#FF8C5A", photo="Vietnam motorbike traffic Saigon",
              groups=["去哪儿","怎么走","回去 · 去做什么"], t1="在越南出行", t2="先会这个字"),
 "la":   dict(ink="#180A18", ink2="#2C142C", accent="#E8A0E0", photo="Vietnamese people ao dai",
              groups=["我是 · 是谁","是什么身份","正是 · 不是"], t1="自我介绍", t2="从这个字开始"),
 "muon": dict(ink="#1A1006", ink2="#2E1D0E", accent="#FFB06A", photo="Vietnamese coffee cafe",
              groups=["想吃想喝","想做什么","不想 · 很想"], t1="越南语说我想", t2="就这一个字"),
 "cho":  dict(ink="#0E1A18", ink2="#1A302C", accent="#8FE0D0", photo="Vietnam street vendor giving",
              groups=["给谁","给我什么","让 · 允许"], t1="越南语的给", t2="管得比中文宽"),
 "duoc": dict(ink="#0A1428", ink2="#132444", accent="#6FB8FF", photo="Ha Long Bay Vietnam",
              groups=["行不行","能不能做","做得到 · 没问题"], t1="越南语说可以", t2="十二种说法"),
 "lam":  dict(ink="#1A1608", ink2="#2C2712", accent="#DCC84A", photo="Vietnamese cooking kitchen",
              groups=["做什么","正在做 · 做完","客套与本事"], t1="一个做字", t2="干什么都能说"),
 "an":   dict(ink="#140C08", ink2="#261610", accent="#FF7A45", photo="Pho Vietnamese noodle soup",
              groups=["吃什么","吃到什么程度","去哪吃"], t1="越南人打招呼", t2="先问吃了没"),
 "den":  dict(ink="#0C1018", ink2="#161E2C", accent="#9FD0F0", photo="Vietnam train station Hanoi",
              groups=["到哪里","到点了没","刚到 · 来接"], t1="越南语说到", t2="也说来"),
 "biet": dict(ink="#101418", ink2="#1C242C", accent="#7ADCF0", photo="Vietnamese school classroom",
              groups=["知不知道","会不会","告知 · 才知道"], t1="越南语说知道", t2="也说会"),
 "lay":  dict(ink="#161010", ink2="#281C1C", accent="#F09090", photo="Vietnam market shopping bag",
              groups=["拿什么","取钱取票","嫁娶 · 取回"], t1="越南语的拿", t2="还能说嫁娶"),
 "xin":  dict(ink="#0E1410", ink2="#1A281E", accent="#B8E060", photo="Vietnamese people greeting",
              groups=["最常用的客气话","请求帮忙","请假 · 求职"], t1="在越南开口", t2="先学这个字"),
 "xem":  dict(ink="#12081A", ink2="#22102E", accent="#C08CFF", photo="Vietnam cinema street night",
              groups=["看什么","怎么看","看病 · 再看"], t1="一个看字", t2="越南人用出十二种"),
 "tot":  dict(ink="#0A1608", ink2="#142812", accent="#B8E870", photo="Vietnamese woman smiling",
              groups=["夸人夸事","好在哪里","做得好 · 睡得好"], t1="越南人夸人", t2="离不开这个字"),
}
SLUG2EP = {"o":"ep01_o","co":"ep02_co","di":"ep03_di","la":"ep04_la","muon":"ep05_muon",
           "cho":"ep06_cho","duoc":"ep07_duoc","lam":"ep08_lam","an":"ep09_an","den":"ep10_den",
           "biet":"ep11_biet","lay":"ep12_lay","xin":"ep13_xin","xem":"ep14_xem","tot":"ep15_tot"}
ICON_OVERRIDE = {"Có ai?": "谁", "Có rồi": "了"}    # 启发式撞车的两条，手工定


def load_old() -> dict:
    src = (OLDV / "viet_highfreq.py").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"EP\d+_\w+\s*=\s*HFEpisode\((.*?)\n\)\n", src, re.S):
        b = m.group(1)
        g = lambda k: (re.search(rf'{k}\s*=\s*"([^"]*)"', b) or [None, None])[1]
        pm = re.search(r"pages\s*=\s*(\[.*?\]),?\s*$", b, re.S)
        out[g("slug")] = dict(word=g("word"), zh=g("word_zh"),
                              pages=ast.literal_eval(pm.group(1)))
    return out


def make_icons(ep: dict) -> list[str]:
    """汉字 icon（老越南语脚本没有，这里从中文释义推）。
    同一集 12 个必须互不相同 —— 重复了就不是锚点了。"""
    used, out = set(), []
    for pg in ep["pages"]:
        for vi, _xie, zh in pg:
            if vi in ICON_OVERRIDE:
                out.append(ICON_OVERRIDE[vi]); used.add(ICON_OVERRIDE[vi]); continue
            strip = zh
            for c in ep["zh"]:
                strip = strip.replace(c, "", 1)
            for ch in list(strip.strip("的了着 ")) + list(zh):
                if ch.strip() and ch not in used:
                    used.add(ch); out.append(ch); break
            else:
                out.append(zh[0])
    assert len(set(out)) == 12, (ep["word"], out)
    return out


def split_viet(chunk: str, target: str) -> list[str]:
    """越南语本来就用空格分词，直接按空格切；目标词单独成段供高亮。"""
    parts = chunk.split()
    assert " ".join(parts) == chunk.strip(), (chunk, parts)
    return parts


def normalize_bgm(src: Path, dst: Path) -> None:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src),
                          "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    adj = BGM_TARGET_DB - float(re.search(r"mean_volume:\s*(-?[\d.]+)", out).group(1))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                    "-af", f"volume={adj:.2f}dB", "-b:a", "192k", str(dst)], check=True)


def fetch_photo(query: str, dst: Path) -> dict | None:
    sys.path.insert(0, str(REPO))
    from tools.video.stock_sources.wikimedia import WikimediaSource
    from tools.video.stock_sources.base import SearchFilters
    w = WikimediaSource()
    for c in w.search(query, SearchFilters(kind="image", per_page=6)):
        try:
            w.download(c, dst)
            if dst.exists() and dst.stat().st_size > 40000:
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(dst),
                                "-vf", "scale=1080:-2,eq=saturation=0.42:contrast=1.06,"
                                       "gblur=sigma=0.6", str(dst.with_suffix(".jpg"))], check=True)
                return dict(query=query, source_url=c.source_url)
        except Exception:
            continue
    return None


def build(slug: str, no: int, old: dict) -> None:
    W, ep = WORDS[slug], old[SLUG2EP[slug]]
    pid = f"viet-1000-hfx-{no:02d}-{slug}"
    proj = REPO / "projects" / pid
    (proj / "artifacts").mkdir(parents=True, exist_ok=True)
    (proj / "renders").mkdir(exist_ok=True)
    for sub in ("composition/public/fonts", "composition/public/app"):
        if not (proj / sub).exists():
            shutil.copytree(TEMPLATE / sub, proj / sub)
    for f in ("BeVietnamPro-Bold.ttf", "BeVietnamPro-SemiBold.ttf"):
        shutil.copy2(VIETFONT / f, proj / "composition/public/fonts" / f)
    (proj / "composition/public/music").mkdir(parents=True, exist_ok=True)
    normalize_bgm(TEMPLATE / "composition/public/music/bgm.mp3",
                  proj / "composition/public/music/bgm.mp3")

    pdst = proj / "composition/public/img/photo.jpg"
    pdst.parent.mkdir(parents=True, exist_ok=True)
    if not pdst.exists():
        cr = fetch_photo(W["photo"], pdst)
        if cr:
            (proj / "artifacts/photo_credit.json").write_text(
                json.dumps(cr, ensure_ascii=False, indent=2), encoding="utf-8")

    icons = make_icons(ep)
    flat = [r for pg in ep["pages"] for r in pg]
    sections, units, rows = [], [], []
    sections.append(dict(id="s00_hook", text=f'越南语高频词：{ep["word"]}。一个词，十二种用法。'))
    units += [dict(id="s00_hook_a", section="s00_hook", lang="zh", text="越南语高频词"),
              dict(id="s00_hook_b", section="s00_hook", lang="vi", text=ep["word"]),
              dict(id="s00_hook_c", section="s00_hook", lang="zh", text="一个词，十二种用法。")]
    for pi in range(3):
        title = W["groups"][pi]
        sections.append(dict(id=f"p{pi+1}_title", text=title))
        units.append(dict(id=f"p{pi+1}_title_zh", section=f"p{pi+1}_title", lang="zh", text=title))
        grp = flat[pi * 4:(pi + 1) * 4]
        for ri, (vi, xie, zh) in enumerate(grp, 1):
            rid = f"p{pi+1}r{ri}"
            sections.append(dict(id=rid, text=f"{zh} → {vi}"))
            units += [dict(id=f"{rid}_zh", section=rid, lang="zh", text=zh),
                      dict(id=f"{rid}_vi", section=rid, lang="vi", text=vi)]
            rows.append(dict(id=rid, page=pi + 1, icon=icons[pi * 4 + ri - 1], zh=zh, th=vi,
                             thParts=split_viet(vi, ep["word"]), rom="", xie=xie))
        sections.append(dict(id=f"p{pi+1}_echo", text="（本组四条连读一遍，跟读）"))
        units.append(dict(id=f"p{pi+1}_echo_vi", section=f"p{pi+1}_echo", lang="vi",
                          text="，".join(r[0] for r in grp)))
    sections.append(dict(id="s10_outro", text="越南语千词，在越南生活够用了。"))
    units.append(dict(id="s10_outro_zh", section="s10_outro", lang="zh",
                      text="越南语千词，在越南生活够用了。"))

    (proj / "artifacts/script.json").write_text(json.dumps({
        "version": "1.0", "project_id": pid, "sections": sections,
        "metadata": {
            "word": {"th": ep["word"], "rom": "", "zh": ep["zh"], "xie": flat[0][1].split()[0]},
            "origin": f'重做自 lang1000/.../vietnamese/viet_highfreq.py 的 {SLUG2EP[slug]}（已发布）。'
                      "12 条用法与谐音逐条沿用，一个字不重编；汉字 icon 由中文释义推出（老脚本没有）。",
            "tts": {"engine": "edge",
                    "voices": {"zh": "zh-CN-XiaoxiaoNeural", "vi": "vi-VN-HoaiMyNeural"},
                    "rates": {"vi": "-22%"}},
            "tts_units": units,
            "pages": [{"title": W["groups"][i],
                       "rows": [r["id"] for r in rows if r["page"] == i + 1]} for i in range(3)],
            "rows": rows,
            "badge": f"越南语高频词 · No.{no:02d}",
            "poster": {"t1": W["t1"], "t2": W["t2"]},
            "palette": {"ink": W["ink"], "ink2": W["ink2"], "accent": W["accent"]},
            "photo": W["photo"],
        }}, ensure_ascii=False, indent=2), encoding="utf-8")
    (proj / "project.json").write_text(json.dumps({
        "version": "1.0", "project_id": pid,
        "title": f'越南语千词 · 高频词 {no:02d} {ep["word"]}（老版式重做）',
        "pipeline_type": "animated-explainer"}, ensure_ascii=False, indent=2), encoding="utf-8")
    (proj / "artifacts/edit_decisions.json").write_text(json.dumps({
        "version": "1.0", "project_id": pid, "render_runtime": "remotion",
        "composition_mode": "atelier", "renderer_family": "bespoke",
        "bespoke": {"entry": str(proj / "composition/index.tsx"), "composition_id": "HF",
                    "props_path": str(proj / "composition/props.json"),
                    "public_dir": str(proj / "composition/public"), "crf": 18,
                    "art_direction": f'底 {W["ink"]} / 强色 {W["accent"]}；配图「{W["photo"]}」压在表格下方。'
                                     "版式与泰语高频词重做批一致（格式化栏目，刻意不换版式）。"}},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f'✓ {pid:28} {ep["word"]:8} 配图 {"有" if pdst.exists() else "无"}  {W["ink"]} / {W["accent"]}')


def main() -> int:
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    old = load_old()
    for i, slug in enumerate(WORDS, 1):
        if only and slug not in only:
            continue
        build(slug, i, old)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
