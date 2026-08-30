#!/usr/bin/env python3
"""把审片页导出的封面文案写回项目，并重建 props。

链路：审片页「封面文案」输入框 → 复制封面文案（JSON）→ 贴给我 →
      这个脚本写成 <project>/artifacts/cover_text.json → build_props 读它覆盖默认值。

这样调封面文案**不用动代码**，也不会被下次重跑 build_props 冲掉。

    python3 scripts/apply_cover_text.py <粘贴的 json 文件>
    pbpaste | python3 scripts/apply_cover_text.py -          # 直接读剪贴板
    python3 scripts/apply_cover_text.py - <<'EOF'
    {"project_id": "...", "t1": "...", ...}
    EOF

支持一次贴多条（JSON 数组）。写完会跑一遍字宽校验，超限当场报出来 ——
超限不拦，只是告诉你哪条超了，因为有时确实要压着上限走。
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"

# 与 scripts/check_screen_text.py 一致：全角 1，半角 0.5
# 封面只放一句话：两行合计 ≤12 字（2026-08-28 用户指令）
LIMITS = {"badge": 16, "t1": 9, "t2": 9}
HEAD_MAX = 12
FIELDS = ("badge", "t1", "t2")


def vlen(t: str) -> float:
    return sum(1.0 if (ord(c) > 0x2E80 or c == "·") else 0.5 for c in t)


def apply_one(o: dict) -> bool:
    pid = o.get("project_id")
    proj = PROJECTS / (pid or "")
    if not pid or not proj.is_dir():
        print(f"  ✗ project_id 不对：{pid!r}", file=sys.stderr)
        return False

    out = {k: o[k] for k in FIELDS if k in o}
    if not out:
        print(f"  ✗ {pid} 没有可写的字段", file=sys.stderr)
        return False

    over = [(k, vlen(v), LIMITS[k]) for k, v in out.items()
            if k in LIMITS and isinstance(v, str) and vlen(v) > LIMITS[k]]
    head = vlen(str(out.get("t1", ""))) + vlen(str(out.get("t2", "")))
    if "t1" in out or "t2" in out:
        if head > HEAD_MAX:
            over.append(("标题两行合计", head, HEAD_MAX))

    ct = proj / "artifacts" / "cover_text.json"
    ct.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    bp = proj / "build_props.py"
    r = subprocess.run(["python3", str(bp)], capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        print(f"  ✗ {pid} build_props 失败：{(r.stderr or '')[-200:]}", file=sys.stderr)
        return False

    print(f"  ✓ {pid}")
    for k in FIELDS:
        if k in out:
            v = out[k]
            print(f"      {k:7} {v if not isinstance(v, list) else ' · '.join(v)}")
    for k, w, lim in over:
        print(f"      ⚠ {k} 字宽 {w} > 上限 {lim}（没拦，但渲出来可能会挤）")
    return True


def main() -> int:
    args = [a for a in sys.argv[1:]]
    if not args:
        print(__doc__, file=sys.stderr)
        return 1
    raw = sys.stdin.read() if args[0] == "-" else Path(args[0]).read_text()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"贴进来的不是合法 JSON：{e}", file=sys.stderr)
        return 1

    items = data if isinstance(data, list) else [data]
    ok = sum(apply_one(o) for o in items)
    print(f"\n写回 {ok}/{len(items)} 个。改完记得重渲：")
    for o in items:
        if o.get("project_id"):
            print(f"  python3 <rerender> {o['project_id']}")
    return 0 if ok == len(items) else 1


if __name__ == "__main__":
    raise SystemExit(main())
