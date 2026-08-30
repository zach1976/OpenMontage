#!/usr/bin/env python3
"""越南语千词 · 禅意一句：五集立项脚手架（对标泰语那一支）。

与泰语支的区别只在语言层：目标语 `vi`、字体 Be Vietnam Pro、女声 HoaiMy。
排时间轴、切底片、封面接图全部复用 `zen_build.py` / `import_cover_src.py`。

**选句纪律**：句子是新写的（泰语那支是从老片逐字抄回的，这支没有老片），
所以卡上教的**实词一律取 app 词条**，`--check` 会逐个核：
    python3 scripts/scaffold_zen_viet.py --check
虚词（không / có / gì / là / phải）这套词库里本来就不收（它是短语型词表），不强求。

    python3 scripts/scaffold_zen_viet.py            # 全部
    python3 scripts/scaffold_zen_viet.py viet-zen-02
"""
import glob, json, re, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = REPO / "projects" / "thai-zen-01-impermanence-v2"      # 借字体/app icon/垫乐
VIET = REPO / "projects" / "viet-1000-name-01-nguyen"         # 借越南语字体
BGM_TARGET_DB = -13.8

EPISODES = [
    dict(no=1, pid="viet-zen-01-mainmai", comp="MaiMai", slug="viet_zen_01_mainmai",
         title="越南语千词 · 禅意 01 无常",
         hook="有什么，\n是永远不变的？", hook_tts="有什么，是永远不变的？",
         vi="Không có gì là mãi mãi.",
         vi_lines=["Không có gì", "là mãi mãi."],
         zh="没有什么，是永远的",
         words=[("Không", "不 · 没有"), ("Có", "有"), ("Gì", "什么"), ("Mãi mãi", "永远")],
         head=["Mãi mãi"], bgm="m_bowl.mp3",
         bg=[("coverr-walking-to-the-mountain-top-8360.mp4", 0.42),
             ("coverr-sunset-in-indonesia-3381.mp4", 0.50),
             ("coverr-road-in-the-mountains-7132.mp4", 0.38)],
         grade="saturation=0.60:brightness=0.030:contrast=1.20",
         art="炭青 + 灰白。装置是「同一个位置反复被顶掉」：所有词都出现在画面正中同一个方框里，"
             "下一个进来就把上一个推走 —— 位置永远在，内容永远换。"),
    dict(no=2, pid="viet-zen-02-buongbo", comp="BuongBo", slug="viet_zen_02_buongbo",
         title="越南语千词 · 禅意 02 放下",
         hook="放下，\n就一定要忘记吗？", hook_tts="放下，就一定要忘记吗？",
         vi="Buông bỏ không phải là quên hết.",
         vi_lines=["Buông bỏ không phải", "là quên hết."],
         zh="放下，并不是忘记一切",
         words=[("Buông bỏ", "放下"), ("Không phải", "不是"), ("Quên", "忘记"), ("Hết", "全部 · 完")],
         head=["Quên"], bgm="warm_gtr.mp3",
         bg=[("coverr-sunset-in-indonesia-3381.mp4", 0.34),
             ("coverr-desert-island-7521.mp4", 0.58),
             ("coverr-walking-to-the-mountain-top-8360.mp4", 0.54)],
         grade="saturation=0.64:brightness=0.035:contrast=1.20",
         art="暖褐 + 陶红。装置是「张开的手」：一对括号钳住词，念到第二遍时向两侧张开把词放出去。"),
    dict(no=3, pid="viet-zen-03-binhtinh", comp="BinhTinh", slug="viet_zen_03_binhtinh",
         title="越南语千词 · 禅意 03 平静",
         hook="平静，\n是不再担心了吗？", hook_tts="平静，是不再担心了吗？",
         vi="Bình tĩnh không phải là không lo lắng.",
         vi_lines=["Bình tĩnh không phải", "là không lo lắng."],
         zh="平静，不是不再担心",
         words=[("Bình tĩnh", "平静"), ("Không phải", "不是"), ("Là", "是"), ("Lo lắng", "担心")],
         head=["Bình tĩnh", "Lo lắng"], bgm="m_ambient.mp3",
         bg=[("coverr-sunrise-in-costa-rica-1299.mp4", 0.46),
             ("coverr-road-in-the-mountains-7132.mp4", 0.56),
             ("coverr-desert-island-7521.mp4", 0.40)],
         grade="saturation=0.52:brightness=0.040:contrast=1.22",
         art="青灰 + 湖蓝。装置是「一条起伏的线」：讲 Lo lắng 时波幅拉到最大，"
             "讲 Bình tĩnh 时收成一条直线 —— 平静不是没有波，是波的幅度小下来。"),
    dict(no=4, pid="viet-zen-04-hanhphuc", comp="HanhPhuc", slug="viet_zen_04_hanhphuc",
         title="越南语千词 · 禅意 04 知足",
         hook="要拥有多少，\n才算幸福？", hook_tts="要拥有多少，才算幸福？",
         vi="Hạnh phúc không phải là có nhiều.",
         vi_lines=["Hạnh phúc không phải", "là có nhiều."],
         zh="幸福，不是拥有得多",
         words=[("Hạnh phúc", "幸福"), ("Không phải", "不是"), ("Có", "拥有 · 有"), ("Nhiều", "多")],
         head=["Hạnh phúc", "Nhiều"], bgm="alt2_zen.mp3",
         bg=[("coverr-desert-island-7521.mp4", 0.24),
             ("coverr-sunrise-in-costa-rica-1299.mp4", 0.62),
             ("coverr-sunset-in-indonesia-3381.mp4", 0.44)],
         grade="saturation=0.58:brightness=0.030:contrast=1.20",
         art="靛蓝 + 米金。装置是「天平」：一根横梁，左盘装「多」右盘装「够」，"
             "每讲一个词横梁摆一次，最后停平 —— 停平的那一刻才是幸福。"),
    dict(no=5, pid="viet-zen-05-batdaulai", comp="BatDauLai", slug="viet_zen_05_batdaulai",
         title="越南语千词 · 禅意 05 重新开始",
         hook="今天撑不住，\n明天呢？", hook_tts="今天撑不住，明天呢？",
         vi="Hôm nay khó, ngày mai bắt đầu lại được.",
         vi_lines=["Hôm nay khó,", "ngày mai bắt đầu lại được."],
         zh="今天难，明天还能重新开始",
         words=[("Hôm nay", "今天"), ("Khó", "难"), ("Ngày mai", "明天"), ("Bắt đầu", "开始")],
         head=["Hôm nay", "Khó", "Ngày mai", "Bắt đầu"], bgm="zen_bed.mp3",
         bg=[("coverr-road-in-the-mountains-7132.mp4", 0.30),
             ("coverr-walking-to-the-mountain-top-8360.mp4", 0.60),
             ("coverr-sunrise-in-costa-rica-1299.mp4", 0.52)],
         grade="saturation=0.62:brightness=0.050:contrast=1.20",
         art="墨蓝 → 晨金。装置是「地平线上的光」：一条地平线，每讲一个词线上的光带升高一档，"
             "到最后整条线亮起来 —— 天亮不是一下子的事。"),
]


def lexicon() -> dict:
    """词表里有「Rất / Nhiều」这种一条收两个词的写法，按斜杠拆开都算词条 ——
    否则 Nhiều 会被误判成"不在词库"。"""
    f = sorted(glob.glob(str(Path.home() / "projects/lang1000/backups/sync_words/viet1000_*_all.json")))[-1]
    lex = {}
    for w in json.load(open(f)):
        t, zh = (w.get("target_text") or "").strip(), w.get("chinese_translation")
        if not t:
            continue
        lex.setdefault(t.lower(), zh)
        for part in t.split("/"):
            part = part.strip()
            if part:
                lex.setdefault(part.lower(), zh)
    return lex


def check() -> int:
    lex = lexicon()
    bad = 0
    print(f"词库 {len(lex)} 条\n")
    for ep in EPISODES:
        print(f'{ep["pid"]}  {ep["vi"]}')
        for w in ep["head"]:
            hit = lex.get(w.lower())
            print(f'   实词 {w:12} {"✓ app 词条：" + str(hit) if hit else "✗ 不在词库"}')
            if not hit:
                bad += 1
        print()
    print("虚词（không/có/gì/là/phải/hết）这套词表本来就不收，不计入。")
    return 1 if bad else 0


def normalize_bgm(src: Path, dst: Path) -> float:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src),
                          "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    mean = float(re.search(r"mean_volume:\s*(-?[\d.]+)", out).group(1))
    adj = BGM_TARGET_DB - mean
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                    "-af", f"volume={adj:.2f}dB", "-b:a", "192k", str(dst)], check=True)
    return adj


def build_script_json(ep: dict) -> dict:
    sections = [dict(id="s00_hook", text=ep["hook_tts"]),
                dict(id="s01_sent", text=f'{ep["zh"]}。 → {ep["vi"]}')]
    units = [dict(id="s00_hook_zh", section="s00_hook", lang="zh", text=ep["hook_tts"]),
             dict(id="s01_sent_zh", section="s01_sent", lang="zh", text=ep["zh"] + "。"),
             dict(id="s01_sent_vi", section="s01_sent", lang="vi", text=ep["vi"], display="{text}")]
    cards = []
    for i, (vi, zh) in enumerate(ep["words"], 1):
        sections.append(dict(id=f"w{i}", text=f"{zh} → {vi}（读两遍）"))
        units += [dict(id=f"w{i}_zh", section=f"w{i}", lang="zh", text=zh.replace(" · ", "、")),
                  dict(id=f"w{i}_vi", section=f"w{i}", lang="vi", text=vi)]
        cards.append(dict(id=f"w{i}", thai=vi, roman="", zh=zh))   # thai/roman 是排版键名，沿用
    sections += [dict(id="s09_again", text=f'{ep["vi"]}（整句再读一次）'),
                 dict(id="s10_outro", text="越南语千词，在越南生活够用了。")]
    units += [dict(id="s09_again_vi", section="s09_again", lang="vi", text=ep["vi"]),
              dict(id="s10_outro_zh", section="s10_outro", lang="zh",
                   text="越南语千词，在越南生活够用了。")]
    return {"version": "1.0", "project_id": ep["pid"], "sections": sections,
            "metadata": {
                "origin": "新立项；句子为新写，卡上教的实词一律取自 viet1000 词库（见 --check）",
                "sentence": dict(thai=ep["vi"], roman="", zh=ep["zh"],
                                 thaiDisplay=" ".join(ep["vi_lines"]), thaiLines=ep["vi_lines"]),
                "hook": ep["hook"],
                "tts": {"engine": "edge",
                        "voices": {"zh": "zh-CN-YunjianNeural", "vi": "vi-VN-HoaiMyNeural"},
                        "rates": {"vi": "-22%", "zh": "-15%"}, "pitches": {"zh": "-4Hz"}},
                "tts_units": units, "cards": cards}}


def main() -> int:
    if "--check" in sys.argv:
        return check()
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    for ep in EPISODES:
        if only and not any(a in ep["pid"] for a in only):
            continue
        proj = REPO / "projects" / ep["pid"]
        (proj / "artifacts").mkdir(parents=True, exist_ok=True)
        (proj / "renders").mkdir(exist_ok=True)
        for sub in ("composition/public/fonts", "composition/public/app"):
            if not (proj / sub).exists():
                shutil.copytree(BASE / sub, proj / sub)
        for f in ("BeVietnamPro-Bold.ttf", "BeVietnamPro-SemiBold.ttf"):
            shutil.copy2(VIET / "composition/public/fonts" / f, proj / "composition/public/fonts" / f)
        shutil.copy2(BASE / "composition/CjkFonts.tsx", proj / "composition/CjkFonts.tsx")
        idx = (BASE / "composition/index.tsx").read_text().replace("Impermanence", ep["comp"])
        (proj / "composition/index.tsx").write_text(idx, encoding="utf-8")

        (proj / "assets/music").mkdir(parents=True, exist_ok=True)
        shutil.copy2(BASE / "assets/music" / ep["bgm"], proj / "assets/music" / ep["bgm"])
        (proj / "composition/public/music").mkdir(parents=True, exist_ok=True)
        normalize_bgm(BASE / "assets/music" / ep["bgm"], proj / "composition/public/music/bgm.mp3")

        (proj / "artifacts/script.json").write_text(
            json.dumps(build_script_json(ep), ensure_ascii=False, indent=2), encoding="utf-8")
        (proj / "project.json").write_text(json.dumps({
            "version": "1.0", "project_id": ep["pid"], "title": ep["title"],
            "pipeline_type": "animated-explainer"}, ensure_ascii=False, indent=2), encoding="utf-8")
        (proj / "artifacts/edit_decisions.json").write_text(json.dumps({
            "version": "1.0", "project_id": ep["pid"], "render_runtime": "remotion",
            "composition_mode": "atelier", "renderer_family": "bespoke",
            "bespoke": {"entry": str(proj / "composition/index.tsx"), "composition_id": ep["comp"],
                        "props_path": str(proj / "composition/props.json"),
                        "public_dir": str(proj / "composition/public"), "crf": 18,
                        "art_direction": ep["art"]}}, ensure_ascii=False, indent=2), encoding="utf-8")
        (proj / "artifacts/bg_spec.json").write_text(json.dumps(
            {"clips": [{"file": f, "x": x} for f, x in ep["bg"]], "grade": ep["grade"]},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print(f'✓ {ep["pid"]:24} {len(ep["words"])} 词 · 垫乐 {ep["bgm"]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
