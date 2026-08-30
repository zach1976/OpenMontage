#!/usr/bin/env python3
"""把成片登记到 videopublisher（通用版）。

为什么不再一集一个脚本：早先每集一个 push_to_videopublisher.py，
里面把 mp4 版本号写死（`nickname_ep02_v1.mp4`）。封面改了七版之后，
那些脚本指向的还是第一版 —— 再跑一次就把旧片推上去了。
这里**永远取 renders/ 里最新的那个 mp4**，封面**现抽第 0 帧**
（平台就是拿第 0 帧当封面的，静态 cover.jpg 会跟成片漂开）。

每集的元数据放在 artifacts/publish.json：
    {"series_id":1, "sub_series":"泰国小名", "slug":"thai_nickname_01_pig",
     "title":"...", "publish_copy":"...", "wechat_copy":"...", "credits":"..."}

file_path 必须落在 local_opener 的 ROOTS 白名单里（lang1000 / learn_thai），
否则后台点「打开」报 outside_project_root，所以成片先拷进 lang1000 的对应目录。

    python3 scripts/push_to_videopublisher.py --dry-run           # 全部，只打印
    python3 scripts/push_to_videopublisher.py <id> [<id> ...]     # 指定几集
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "projects"
LANG1000 = Path.home() / "projects" / "lang1000"
ENV = LANG1000 / ".env"

# series_id → (白名单根目录, 账号名)
SERIES = {1: (LANG1000 / "marketing" / "video", "泰语千词"),
          2: (LANG1000 / "marketing" / "video" / "vietnamese", "越南语千词")}
# sub_series → 落哪个子目录
SUBDIR = {"泰国小名": "series_nickname", "泰国人的英文名": "series_nickname",
          "怎么称呼": "series_nickname", "高频词": "series_high_freq_word",
          "禅意一句": "series_zen", "泰语谚语": "series_zen",
          "越南名字": "series_viet_name", "越南称呼": "series_viet_name",
          "越南美食": "series_food", "神曲跟唱": "series_song"}
# 少数子系列在两个号下的目录名不一样 —— 越南语那边高频词的老目录叫 series_high_freq
# （没有 _word 后缀），跟着老目录走，别新开一个平行目录。
SUBDIR_BY_SERIES = {(2, "高频词"): "series_high_freq"}


def load_env() -> dict:
    env = {}
    for line in ENV.read_text().splitlines():
        m = re.match(r"^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$", line)
        if m:
            env[m.group(1)] = m.group(2).strip().strip('"')
    return env


def latest_mp4(proj: Path) -> Path | None:
    mp4s = sorted(proj.glob("renders/*.mp4"), key=lambda p: p.stat().st_mtime)
    return mp4s[-1] if mp4s else None


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv[1:]

    metas = []
    for d in sorted(PROJECTS.iterdir()):
        if not d.is_dir() or (args and d.name not in args):
            continue
        pj = d / "artifacts" / "publish.json"
        if pj.exists():
            metas.append((d, json.loads(pj.read_text())))
    if not metas:
        print("没有带 artifacts/publish.json 的项目", file=sys.stderr)
        return 1

    env = load_env()
    base, token = env.get("VIDEOPUBLISHER_URL"), env.get("VIDEOPUBLISHER_TOKEN")
    if not (base and token):
        print("缺 VIDEOPUBLISHER_URL / VIDEOPUBLISHER_TOKEN", file=sys.stderr)
        return 1

    ok = fail = 0
    for proj, m in metas:
        mp4 = latest_mp4(proj)
        if mp4 is None:
            print(f"  ✗ {proj.name}  没有成片"); fail += 1; continue
        root, account = SERIES[m["series_id"]]
        dest = root / SUBDIR_BY_SERIES.get(
            (int(m["series_id"]), m["sub_series"]),
            SUBDIR.get(m["sub_series"], "series_misc"))
        out_mp4, out_cover = dest / f'{m["slug"]}.mp4', dest / f'{m["slug"]}_cover.jpg'
        size_mb = mp4.stat().st_size / 1e6
        print(f"  → {m['slug']:30} {account} · {m['sub_series']}  {mp4.name}  {size_mb:.1f}MB")
        if dry:
            continue

        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(mp4, out_mp4)
        # 封面现抽第 0 帧：平台拿的就是这一帧，静态 cover.jpg 会跟成片漂开
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4),
                        "-vf", "select=eq(n\\,0)", "-frames:v", "1", "-q:v", "2",
                        str(out_cover)], check=True)

        data = {"series_id": str(m["series_id"]), "normalized_title": m["slug"],
                "title": m["title"], "sub_series": m["sub_series"],
                "publish_copy": m.get("publish_copy", ""),
                "wechat_copy": m.get("wechat_copy", ""),
                "file_path": str(out_mp4.resolve()), "stage": "ready"}
        with open(out_cover, "rb") as fh:
            r = requests.post(f"{base}/api/videos/upsert", data=data,
                              files={"cover": (out_cover.name, fh, "image/jpeg")},
                              headers={"Authorization": f"Bearer {token}",
                                       "Accept": "application/json"}, timeout=180)
        if r.ok and r.json().get("ok"):
            j = r.json()
            print(f"     ✓ video_id={j['video_id']} stage={j['stage']} "
                  f"cover={'yes' if j.get('cover_url') else 'no'}")
            log = proj / "artifacts" / "publish_log.json"
            entries = (json.loads(log.read_text()).get("entries") if log.exists() else []) or []
            entries.insert(0, {"platform": "videopublisher", "status": "pending_review",
                               "video_id": j["video_id"], "slug": m["slug"],
                               "source_mp4": mp4.name,
                               "timestamp": datetime.now(timezone.utc).isoformat()})
            log.write_text(json.dumps({"version": "1.0", "entries": entries},
                                      ensure_ascii=False, indent=2), encoding="utf-8")
            ok += 1
        else:
            print(f"     ✗ HTTP {r.status_code} {r.text[:200]}", file=sys.stderr); fail += 1

    print(f"\n成功 {ok} · 失败 {fail}" + ("（dry-run，未上传）" if dry else ""))
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
