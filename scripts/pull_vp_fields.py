#!/usr/bin/env python3
"""推送前把 videopublisher 库里的 title / publish_copy / wechat_copy / idea_notes 拉回本地元数据。

upsert 是整条覆盖：本地 publish.json 若是旧版，直接推会把后台手改过的标题文案冲掉
（记忆 feedback-cta-compliance-redlines）。所以任何「重渲后再推」都先跑这个。

    python3 scripts/pull_vp_fields.py <project_id> [<project_id> ...]
只改库里已存在的条目；同时打印每条的 stage，供决定推不推（published 的不推）。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIELDS = ("title", "publish_copy", "wechat_copy", "idea_notes")


def env() -> dict:
    out = {}
    for line in (Path.home() / "projects/.env").read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def metas(pid: str):
    proj = REPO / "projects" / pid / "artifacts"
    if (proj / "publish_batch.json").exists():
        data = json.loads((proj / "publish_batch.json").read_text())
        return proj / "publish_batch.json", data, data["episodes"]
    data = json.loads((proj / "publish.json").read_text())
    return proj / "publish.json", data, [data]


def fetch(slugs: list[str]) -> dict:
    e = env()
    key, host = e["SSH_KEY_FILE"], f'{e["SSH_USER"]}@{e["SSH_HOST"]}'
    php = ("<?php\n$s=json_decode(file_get_contents('/tmp/vp_pull_in.json'),true);\n"
           "$r=\\DB::table('videos')->whereIn('normalized_title',$s)->get(['normalized_title','stage','title','publish_copy','wechat_copy','idea_notes']);\n"
           "file_put_contents('/tmp/vp_pull_out.json',json_encode($r,JSON_UNESCAPED_UNICODE));echo 'rows '.count($r).\"\\n\";\n")
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "x.php").write_text(php)
        (Path(td) / "in.json").write_text(json.dumps(slugs))
        subprocess.run(["scp", "-q", "-i", key, f"{td}/x.php", f"{host}:/tmp/vp_pull.php"], check=True)
        subprocess.run(["scp", "-q", "-i", key, f"{td}/in.json", f"{host}:/tmp/vp_pull_in.json"], check=True)
        subprocess.run(["timeout", "90", "ssh", "-i", key, host,
                        "cd /srv/httpd/htdocs/videopublisher && php artisan tinker /tmp/vp_pull.php < /dev/null"],
                       stdin=subprocess.DEVNULL, capture_output=True, text=True)  # tinker 不接 /dev/null 会等输入挂满 90s，输出已写文件，不看退出码
        subprocess.run(["scp", "-q", "-i", key, f"{host}:/tmp/vp_pull_out.json", f"{td}/out.json"], check=True)
        return {r["normalized_title"]: r for r in json.loads((Path(td) / "out.json").read_text())}


def main() -> int:
    pids = [a for a in sys.argv[1:] if not a.startswith("--")]
    loaded = {pid: metas(pid) for pid in pids}
    slugs = [m["slug"] for _, _, ms in loaded.values() for m in ms]
    db = fetch(slugs)
    changed = 0
    for pid, (path, data, ms) in loaded.items():
        dirty = False
        for m in ms:
            row = db.get(m["slug"])
            if not row:
                continue
            for f in FIELDS:
                if row.get(f) is not None and m.get(f) != row[f]:
                    m[f] = row[f]
                    dirty = True
                    changed += 1
            m["_db_stage"] = row["stage"]
        if dirty or any("_db_stage" in m for m in ms):
            path.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    stages = {}
    for _, _, ms in loaded.values():
        for m in ms:
            stages[m.get("_db_stage", "不在库")] = stages.get(m.get("_db_stage", "不在库"), 0) + 1
    print(f"{len(slugs)} 条，库里命中 {len(db)}；拉回字段 {changed} 处；stage 分布 {stages}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
