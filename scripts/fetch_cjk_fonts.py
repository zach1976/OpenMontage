#!/usr/bin/env python3
"""按项目实际用到的汉字，从 Google Fonts 只下需要的分块，存到本地。

为什么不直接在渲染时联网加载：渲染就多一个网络依赖，断网或被墙就整批失败
（这仓库已经踩过 upload.wikimedia.org / huggingface.co 不通）。字体下一次存本地，
之后渲染完全离线。

Google 把 CJK 字体切成上百个 unicode 分块（按字频排的），
我们实际只用到其中十来块 —— 全下是几十 MB，按需下是几 MB。

用法：
    python3 scripts/fetch_cjk_fonts.py            # 下载 + 生成 loader
    python3 scripts/fetch_cjk_fonts.py --report   # 只报要下哪些块
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMPOSER = REPO / "remotion-composer"
OUT = REPO / "projects" / "_shared" / "fonts"

# (家族, 字重, 本地 family 名) —— 标题用重衬线，说明/品牌行用无衬线，两者角色分开
# 禅意系列另加一档 300 细衬线：900 的黑体衬线太"重"，压在实拍上像鸡汤海报；
# 禅意标题要的是细、疏、留白（2026-08-29 用户「封面还是不行，需要继续美化」）
WANT = [("NotoSerifSC", "900", "SerifSC900"),
        ("NotoSerifSC", "300", "SerifSC300"),
        ("NotoSansSC", "500", "SansSC500")]


def used_chars() -> set[str]:
    """扫所有项目的 props.json + 组件源码里的中文，得出真正用到的字。"""
    chars: set[str] = set()
    for f in list((REPO / "projects").glob("*/composition/props.json")) + \
             list((REPO / "projects").glob("*/composition/*.tsx")) + \
             list((REPO / "projects").glob("*/artifacts/script.json")):
        try:
            chars.update(ch for ch in f.read_text(encoding="utf-8")
                         if "　" <= ch <= "鿿" or "＀" <= ch <= "￯")
        except Exception:
            pass
    # 常用标点与数字也带上，免得掉字回落到系统字体
    chars.update("，。、；：？！「」『』（）—…·0123456789")
    return chars


def parse_ranges(spec: str) -> list[tuple[int, int]]:
    out = []
    for part in spec.split(","):
        part = part.strip().replace("U+", "").replace("u+", "")
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-")
            out.append((int(a, 16), int(b, 16)))
        else:
            out.append((int(part, 16), int(part, 16)))
    return out


def font_info(family: str) -> dict:
    js = f"const g=require('@remotion/google-fonts/{family}');console.log(JSON.stringify(g.getInfo()))"
    r = subprocess.run(["node", "-e", js], cwd=COMPOSER, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-300:])
    return json.loads(r.stdout)


def write_loader(faces: list[dict]) -> None:
    """把 FACES 表和 loadFonts 一起生成出来。

    **这一步以前是漏的** —— 脚本只写 `cjk_faces.json`，`CjkFonts.tsx` 是手工维护的。
    于是 2026-08-29 加了 300 字重、字块也下好了，组件却引不到，
    标题还是 900 的重衬线（用户：「封面还是不行」）。加一个字重必须连 loader 一起重生成。
    """
    rows = ",\n".join(
        '  { f: "%s", w: "%s", s: "%s", r: "%s" }' % (f["family"], f["weight"], f["file"], f["range"])
        for f in faces)
    fams = sorted({(f["family"], f["weight"]) for f in faces})
    doc = "\n".join(f"//   {a:<11} 字重 {b}" for a, b in fams)
    src = LOADER_TMPL.replace("__DOC__", doc).replace("__ROWS__", rows).replace("__N__", str(len(faces)))
    (REPO / "projects" / "_shared" / "CjkFonts.tsx").write_text(src, encoding="utf-8")


LOADER_TMPL = '''import { continueRender, delayRender, staticFile } from "remotion";

// ═══════════════════════════════════════════════════════════════════════════
// 中文字体加载器 —— 由 scripts/fetch_cjk_fonts.py 生成，勿手改。
//
// Google 把 CJK 字体按字频切成 101 个 unicode 块，这里只下项目真正用到的那些
// （脚本扫过所有 props/组件/script.json 统计），文件已落到本地 public/fonts/，
// **渲染完全不联网** —— 这仓库踩过 upload.wikimedia.org / huggingface.co 不通
// 导致整批失败，字体不能再挂一个网络依赖。共 __N__ 个分块：
__DOC__
//
// 排版分工（这是版面好不好看的关键，不是字号）：
//   SerifSC900  重衬线 —— 海报大标题。700 的正文宋体撑不住 190px 的金字。
//   SerifSC300  细衬线 —— 禅意封面标题。900 压在实拍上像鸡汤海报，禅意要细、疏。
//   SansSC500   无衬线 —— 品牌行、期号、说明行、脚注，安静退到后面，不跟标题抢。
// ═══════════════════════════════════════════════════════════════════════════

type Face = { f: string; w: string; s: string; r: string };

const FACES: Face[] = [
__ROWS__,
];

type ExtraFont = [family: string, file: string];

export function loadFonts(extra: ExtraFont[] = []) {
  const handle = delayRender("cjk-fonts", { timeoutInMilliseconds: 240000 });
  const cjk = FACES.map((x) =>
    new FontFace(x.f, `url(${staticFile("fonts/" + x.s)})`,
                 { weight: x.w, unicodeRange: x.r } as FontFaceDescriptors).load());
  const others = extra.map(([fam, file]) =>
    new FontFace(fam, `url(${staticFile("fonts/" + file)})`).load());
  // allSettled 而不是 all：`all` 一块加载失败就整批 reject，
  // 结果是**一个字体都没装上**（少一个分块 → 全片回落到系统字体）。逐个结算才对。
  Promise.allSettled([...cjk, ...others])
    .then((rs) => {
      rs.forEach((r) => { if (r.status === "fulfilled") (document.fonts as any).add(r.value); });
      continueRender(handle);
    })
    .catch(() => continueRender(handle));   // 掉字也要出片，别把渲染卡死
}

// 语义化的 font-family 串，组件里直接引这几个，别再各自写字符串
export const ZH_TITLE = \'"SerifSC900", "SerifSC", "ThaiBold", "VietBold", serif\';
export const ZH_UI = \'"SansSC500", "SerifSC", "ThaiReg", "VietSemi", sans-serif\';
export const ZH_ZEN = \'"SerifSC300", "SerifSC", "ThaiReg", "VietSemi", serif\';
'''


def main() -> int:
    report_only = "--report" in sys.argv[1:]
    chars = used_chars()
    cps = {ord(c) for c in chars}
    print(f"项目里实际用到 {len(chars)} 个中文字符/全角标点")

    OUT.mkdir(parents=True, exist_ok=True)
    faces = []
    for family, weight, local in WANT:
        info = font_info(family)
        ranges = info["unicodeRanges"]
        urls = info["fonts"]["normal"][weight]
        need = []
        for key, url in urls.items():
            spec = ranges.get(key)
            if not spec:
                continue
            rs = parse_ranges(spec)
            if any(any(a <= cp <= b for a, b in rs) for cp in cps):
                need.append((key, url, spec))
        print(f"  {family} {weight}: {len(urls)} 块中需要 {len(need)} 块")
        for key, url, spec in need:
            name = f"{local}_{re.sub(r'[^0-9]', '', key)}.woff2"
            dst = OUT / name
            if not report_only and not dst.exists():
                subprocess.run(["curl", "-sSL", "--max-time", "60", "-o", str(dst), url], check=True)
            faces.append(dict(family=local, weight=weight, file=name, range=spec))

    if report_only:
        return 0

    (OUT / "cjk_faces.json").write_text(json.dumps(faces, ensure_ascii=False, indent=2), encoding="utf-8")
    write_loader(faces)
    total = sum((OUT / f["file"]).stat().st_size for f in faces if (OUT / f["file"]).exists())
    print(f"\n共 {len(faces)} 个分块 / {total/1e6:.1f}MB → {OUT.relative_to(REPO)}")
    print(f"  loader → projects/_shared/CjkFonts.tsx（{len(faces)} 个 FontFace）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
