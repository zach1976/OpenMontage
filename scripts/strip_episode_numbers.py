#!/usr/bin/env python3
"""把 ThaiLearningCards 各集 props 里的期号（"NO.xx"）换成栏目标签，走 standalone 封面。

规矩：画面不放期号（记忆 feedback-videos-standalone）。原来 episode="NO.17" 会印在封面、
期号胶囊和大号底纹数字上。改成 episode=<栏目名>、coverVariant=<原来按期号算出的版式>，
版式保持不变，只是不再出现数字。

    python3 scripts/strip_episode_numbers.py            # 列出并改写
    python3 scripts/strip_episode_numbers.py --check    # 只列出
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    check = "--check" in sys.argv
    hits = []
    for f in sorted((REPO / "projects").glob("*/composition/ep*/props.json")):
        d = json.loads(f.read_text())
        ep = d.get("episode")
        if not isinstance(ep, str) or not ep.startswith("NO.") or d.get("coverVariant") is not None:
            continue
        num = int("".join(c for c in ep if c.isdigit()) or 1)
        name = d["seriesName"]
        offset = 2 if "紧急应急" in name else 4 if "泰国美食" in name else 0
        hits.append(f)
        if not check:
            d["episode"] = name.split("·")[-1].strip()
            d["coverVariant"] = (num - 1 + offset) % 6
            d["episodeNumberRemoved"] = ep
            f.write_text(json.dumps(d, ensure_ascii=False, indent=2))
    for f in hits:
        print(f.relative_to(REPO / "projects"))
    print(f"{'待改' if check else '已改'} {len(hits)} 集")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
