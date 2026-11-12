#!/usr/bin/env python3
"""把 projects/_shared/HF.tsx 同步到 31 个高频词项目（泰语 16 + 越南语 15）。

各集 composition/HF.tsx 是独立拷贝 —— 只改共享版不同步，渲出来还是旧代码
（CLAUDE.md 记过的坑）。越南语版做固定替换：字体、品牌字样、泰文字号换成越南文字号。

    python3 scripts/sync_hf_template.py          # 同步
    python3 scripts/sync_hf_template.py --check  # 只报告哪些拷贝与共享版不一致
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHARED = REPO / "projects" / "_shared" / "HF.tsx"

VI_REPLACE = [
    ('loadFonts([["ThaiBold", "Sarabun-Bold.ttf"], ["ThaiReg", "Sarabun-Regular.ttf"],',
     'loadFonts([["VietBold", "BeVietnamPro-Bold.ttf"], ["VietSemi", "BeVietnamPro-SemiBold.ttf"],'),
    ('const TH = "ThaiBold, sans-serif", TH_R = "ThaiReg, sans-serif";',
     'const TH = "VietBold, sans-serif", TH_R = "VietSemi, sans-serif";'),
    ("泰语千词 · 高频词（老版式重做批）", "越南语千词 · 高频词（老版式重做批）"),
    ('const BRAND_LINE = "泰语千词 · 每天一个高频词";', 'const BRAND_LINE = "越南语千词 · 每天一个高频词";'),
    (">泰语千词</div>", ">越南语千词</div>"),
    ("在泰国生活，够用了", "在越南生活，够用了"),
    ("fontSize: on ? 64 : 58, lineHeight: 1.5", "fontSize: on ? 50 : 45, lineHeight: 1.45"),
    ("fontFamily: TH, fontSize: 200, lineHeight: 1.34", "fontFamily: TH, fontSize: 168, lineHeight: 1.34"),
]


def variant(src: str, lang: str) -> str:
    if lang == "th":
        return src
    for a, b in VI_REPLACE:
        assert a in src, f"越南语替换锚点不见了：{a[:50]}"
        src = src.replace(a, b)
    return src


def main() -> int:
    src = SHARED.read_text()
    check = "--check" in sys.argv
    n = bad = 0
    for proj in sorted((REPO / "projects").glob("*-1000-hfx-*")):
        dst = proj / "composition" / "HF.tsx"
        if not dst.exists():
            continue
        want = variant(src, "vi" if proj.name.startswith("viet") else "th")
        if dst.read_text() != want:
            bad += 1
            if not check:
                dst.write_text(want)
        n += 1
    print(f"{n} 个项目，{'不一致' if check else '已更新'} {bad} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
