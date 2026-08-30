#!/usr/bin/env python3
"""扫 composition/props.json 里的画面文字，报出比旁白还啰嗦的地方。

画面是标题、旁白才是内容。观众没时间一边听一边读同样的话。
上限见 CLAUDE.md「画面文字不是旁白字幕」。

    python3 scripts/check_screen_text.py <project_id> [more...]
"""
import json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# lead = 封面那一句点题。封面只有一句话的位置，超过 10 字就不是「一眼看明白」了。
LIMITS = {"note": (12, 2), "beat": (12, 2), "sub": (14, 2), "line1": (10, 1), "line2": (10, 1),
          "lead": (10, 1),
          # 海报版式：t1 铺垫行、t2 点题行（最大）、plaque 描金匾、foot 带外脚注
          "t1": (8, 1), "t2": (6, 1), "plaque": (12, 1), "foot": (20, 1)}
FILLER = ["因为", "所以", "而且", "不管", "很多时候", "有意思的是", "也就是说", "其实就是", "这样一来"]

def vlen(t: str) -> float:
    """按视觉宽度算，不是按字符数：汉字算 1，拉丁字母/数字/空格算 0.5。
    否则「英文的 s / th / st / l」会被误判成 19 字，其实看着很短。"""
    w = 0.0
    for ch in t:
        w += 0.5 if (ch.isascii() and (ch.isalnum() or ch in " /·-")) else 1.0
    return w


def check(kind, text, where, bad):
    if not text:
        return
    maxc, maxl = LIMITS[kind]
    lines = str(text).split("\n")
    if len(lines) > maxl:
        bad.append((where, f"{len(lines)} 行 > {maxl} 行", text))
    for ln in lines:
        w = vlen(ln)
        if w > maxc:
            bad.append((where, f"{w:.0f} 字宽 > {maxc}", ln))
    for f in FILLER:
        if f in str(text):
            bad.append((where, f"含连接词「{f}」", text))

def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    rc = 0
    for pid in sys.argv[1:]:
        p = REPO / "projects" / pid / "composition" / "props.json"
        if not p.exists():
            print(f"{pid}: 没有 props.json"); continue
        d = json.loads(p.read_text())
        bad = []
        h = d.get("hook") or {}
        cov = h.get("cover") or h
        check("line1", cov.get("line1"), "封面 line1", bad)
        check("line2", cov.get("line2"), "封面 line2", bad)
        check("sub", cov.get("sub"), "封面 sub", bad)
        # 海报版式的封面文案。早先只加了 LIMITS 却没接上扫描，
        # 结果「全部通过」对封面文案是空话 —— 点题行超宽一直没被拦下来。
        # 封面文案总量不超过 12 字（2026-08-28 用户指令「封面过于复杂了」）。
        # t1/t2 现在是同一句话的上下两行，所以卡的是**两行合计**，不是各自。
        po = h.get("poster") or {}
        t1, t2 = str(po.get("t1") or ""), str(po.get("t2") or "")
        if t1 or t2:
            tot = vlen(t1) + vlen(t2)
            if tot > 12:
                bad.append(("封面 标题合计", f"{tot:g} 字宽 > 12", f"{t1} / {t2}"))
            for k, lab in (("t1", "封面 第一行"), ("t2", "封面 第二行")):
                for f in FILLER:
                    if f in str(po.get(k) or ""):
                        bad.append((lab, f"含连接词「{f}」", po.get(k)))
        # 匾/词表/脚注不该再出现在封面上
        for k, lab in (("plaque", "匾内副标题"), ("row", "词表"), ("foot", "脚注")):
            if po.get(k):
                bad.append(("封面 多余字段", f"{lab}不该上封面", str(po.get(k))[:24]))
        for c in d.get("cards", []):
            check("note", c.get("note"), f"卡 {c.get('id')} note", bad)
        r = d.get("reveal") or {}
        for i, b in enumerate(r.get("beats") or [], 1):
            check("beat", b, f"反转 beat{i}", bad)
        for k in ("rule", "saying"):
            if r.get(k):
                check("sub", r[k], f"反转 {k}", bad)
        if bad:
            rc = 1
            print(f"\n{pid}  ⚠️ {len(bad)} 处")
            for where, why, txt in bad:
                print(f"   {where:18} {why:16} {str(txt)[:38].replace(chr(10),' / ')}")
        else:
            print(f"{pid}  画面文字自查通过 ✅")
    return rc

if __name__ == "__main__":
    raise SystemExit(main())
