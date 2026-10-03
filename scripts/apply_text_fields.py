#!/usr/bin/env python3
"""把审片页上改过的文案写回项目，供 build_props.py 覆盖内置文案。

审片页的「全片文案 · 可直接改」面板复制出来的是
    {"project": "<id>", "fields": {"<key>": "<新文案>", ...}}
只含**改动过**的字段。这里合并进 artifacts/text_overrides.json（不覆盖没提到的键），
然后重跑 build_props.py 即可生效 —— 改文案不用动脚本。

    pbpaste | python3 scripts/apply_text_fields.py -
    python3 scripts/apply_text_fields.py <文件路径>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__); return 1
    raw = sys.stdin.read() if sys.argv[1] == "-" else Path(sys.argv[1]).read_text()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"贴进来的不是合法 JSON：{e}", file=sys.stderr); return 1

    pid = payload.get("project")
    fields = payload.get("fields") or {}
    if not pid:
        print("缺 project 字段", file=sys.stderr); return 1
    if not fields:
        print("没有改动，什么都不用做"); return 0

    art = REPO / "projects" / pid / "artifacts"
    if not art.is_dir():
        print(f"找不到项目 {pid}", file=sys.stderr); return 1

    # 校验键名：只接受 text_fields.json 里真实存在的键，
    # 免得贴错项目或手改 JSON 时塞进一个永远不会生效的键，还以为改了。
    tf = art / "text_fields.json"
    if tf.exists():
        known = {f["key"] for f in json.loads(tf.read_text())}
        unknown = [k for k in fields if k not in known]
        if unknown:
            print(f"这些键在 {pid} 里不存在：{unknown}", file=sys.stderr); return 1

    dst = art / "text_overrides.json"
    cur = json.loads(dst.read_text()) if dst.exists() else {}
    cur.update(fields)
    dst.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"✓ {dst.relative_to(REPO)}  本次 {len(fields)} 条，累计 {len(cur)} 条")
    for k, v in fields.items():
        print(f"    {k:22} → {v}")
    print(f"\n接着跑：python3 projects/{pid}/build_props.py   然后重渲")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
