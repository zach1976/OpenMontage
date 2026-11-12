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
          "情景对话": "series_dialogue",
          "情侣泰语": "series_couple",
          "情侣越南语": "series_couple",
          "经典口头禅": "series_catchphrase", "紧急应急": "series_emergency",
          "泰国美食": "series_food",
          "趣味泰语": "series_funny", "趣味越南语": "series_funny",
          "听力测验": "series_listening_quiz", "场景短句": "series_scene_phrase",
          "招牌识字": "series_signboard", "数数": "series_numbers",
          "怎么称呼": "series_nickname", "泰国人的英文名": "series_nickname",
          "禅意一句": "series_zen", "泰语谚语": "series_zen",
          "越南名字": "series_viet_name", "越南称呼": "series_viet_name",
          "越南美食": "series_food", "越南语神曲": "series_song",
           "泰语神曲": "series_song", "神曲跟唱": "series_song",
           "泰文字母歌逐词教学": "series_song",
          "教材带货": "series_textbook",
          "泰国人生小语": "series_quotes", "越南人生小语": "series_quotes"}
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
    only_episode = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--only-episode=")), "")
    only_episodes = {x.strip() for x in only_episode.split(",") if x.strip()}
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv[1:]

    metas = []
    for d in sorted(PROJECTS.iterdir()):
        if not d.is_dir() or (args and d.name not in args):
            continue
        pj = d / "artifacts" / "publish.json"
        batch = d / "artifacts" / "publish_batch.json"
        if batch.exists():
            payload = json.loads(batch.read_text())
            metas.extend((d, item) for item in payload.get("episodes", [])
                         if not only_episodes or item.get("episode_id") in only_episodes)
        elif pj.exists():
            metas.append((d, json.loads(pj.read_text())))
    # --variants=<json>：已发布条目「改三成重发」—— 按 key（pid 或 pid/episode_id）覆盖 slug/title/publish_copy/idea_notes，
    # 只推 variants 里列出的条目；slug 换新 → 作为新视频入库，旧条目（已发布）不动。
    vfile = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--variants=")), "")
    if vfile:
        variants = json.loads(Path(vfile).read_text())
        picked = []
        for proj, m in metas:
            key = proj.name + (f"/{m['episode_id']}" if m.get("episode_id") else "")
            if key in variants:
                m = {**m, **variants[key]}
                if m.get("video_path") is None and "video_path" in variants[key]:
                    m.pop("video_path")
                picked.append((proj, m))
        metas = picked
    if not metas:
        print("没有带 artifacts/publish.json 的项目", file=sys.stderr)
        return 1

    env = load_env()
    base, token = env.get("VIDEOPUBLISHER_URL"), env.get("VIDEOPUBLISHER_TOKEN")
    if not (base and token):
        print("缺 VIDEOPUBLISHER_URL / VIDEOPUBLISHER_TOKEN", file=sys.stderr)
        return 1

    # 推送前查库（2026-11-11 加，起因：上一轮漏查 stage）——upsert 固定写 stage=ready、整条覆盖文案：
    #   · 库里已 published 的条目：拒推（会被改回待发、可能重复发布）。要重发新版就走 --variants 换 slug。
    #   · 库里待发、但本地标题/文案跟库里不一致：拒推（会冲掉后台手改），先跑 pull_vp_fields.py。
    # 查不了库（ssh 不通）就整批不推；确实要跳过用 --skip-stage-check。
    if "--skip-stage-check" not in sys.argv[1:]:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from pull_vp_fields import fetch
        try:
            db = fetch([m["slug"] for _, m in metas])
        except Exception as e:  # noqa: BLE001
            print(f"查库失败（{e.__class__.__name__}），整批不推；确认库里状态后可加 --skip-stage-check", file=sys.stderr)
            return 1
        allow_pub = "--allow-published" in sys.argv[1:]
        kept = []
        for proj, m in metas:
            row = db.get(m["slug"])
            if row and row["stage"] != "ready" and not allow_pub:
                print(f"  ✗ {m['slug']}  库里 stage={row['stage']}，不覆盖（要重发新版请用 --variants 换 slug）", file=sys.stderr)
                continue
            stale = [f for f in ("title", "publish_copy") if row and row.get(f) and (m.get(f) or "").strip() != row[f].strip()]
            if stale and "--overwrite-fields" not in sys.argv[1:]:
                print(f"  ✗ {m['slug']}  本地 {'/'.join(stale)} 跟库里不一致，先跑 pull_vp_fields.py {proj.name}"
                      "（确定要用本地版覆盖加 --overwrite-fields）", file=sys.stderr)
                continue
            kept.append((proj, m))
        print(f"查库：{len(metas)} 条，命中 {len(db)}，可推 {len(kept)}")
        metas = kept

    ok = fail = 0
    for proj, m in metas:
        configured_video = m.get("video_path")
        mp4 = (proj / configured_video).resolve() if configured_video else latest_mp4(proj)
        if mp4 is None:
            print(f"  ✗ {proj.name}  没有成片"); fail += 1; continue
        if not mp4.exists():
            print(f"  ✗ {proj.name}  成片不存在: {mp4}"); fail += 1; continue
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
        # 批量项目可传入已审核的首帧封面；普通项目仍从最终成片现抽第 0 帧。
        configured_cover = m.get("cover_path")
        cover_source = (proj / configured_cover).resolve() if configured_cover else None
        if cover_source and cover_source.exists():
            shutil.copy2(cover_source, out_cover)
        else:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4),
                            "-vf", "select=eq(n\\,0)", "-frames:v", "1", "-q:v", "2",
                            str(out_cover)], check=True)

        # 标题规则（2026-10-12 用户指令，对齐视频号短标题）：只许中文+数字，无符号/emoji/泰文/越南文，6–16 字。
        # dashboard 拿 publish_copy 第一行当视频号/小红书标题，所以 title 字段和文案首行都要合规；
        # wechat_copy（视频号一行式）= 标题 + 非泰文的 #标签。不合规又洗不干净的，直接拒绝入库。
        def _clean(t: str) -> str:
            t = re.sub(r"[\u0E00-\u0E7F]+|[A-Za-zÀ-ỹ]+", "", t or "")
            return re.sub(r"[^\u4e00-\u9fff0-9]", "", t)
        _ok = lambda t: bool(re.fullmatch(r"[\u4e00-\u9fff0-9]{6,16}", t or ""))
        _title = m["title"] if _ok(m["title"]) else _clean(m["title"])
        if not _ok(_title):
            print(f"  ✗ {m['slug']}  标题不合规（只许中文数字 6–16 字）：{m['title']!r}", file=sys.stderr)
            fail += 1
            continue
        m["title"] = _title
        _copy = (m.get("publish_copy") or "").strip()
        if _copy.split("\n")[0].strip() != _title:
            m["publish_copy"] = _title + "\n" + _copy
        _tags = " ".join(t for t in re.findall(r"#[^\s#]+", m["publish_copy"]) if not re.search(r"[\u0E00-\u0E7F]", t))
        m["wechat_copy"] = (_title + " " + _tags).strip()
        # 导流合规（lang1000 2026-05-23 / 08-24 两平台实锤判罚）：文案不许引导站外下载、不许福利措辞、
        # 不许评论区引导；app 发音是 AI 合成，不许写真人/原生发音（2026-10-20 用户纠正）。
        # 只拦引导句式，不拦单字 —— 「刷手机」那集把「下载」「App」当词来教，是正常内容。
        _BANNED = r"主页搜|全部免费|App ?Store|应用商店|下载(泰语|越南语)千词|千词 ?[Aa][Pp][Pp]|评论区|真人发音|原生发音|原声发音"
        _hit = re.search(_BANNED, " ".join(str(m.get(k) or "") for k in ("title", "publish_copy", "wechat_copy")))
        if _hit:
            print(f"  ✗ {m['slug']}  文案含导流/虚假表述「{_hit.group(0)}」，拒绝入库", file=sys.stderr)
            fail += 1
            continue
        # 带货片入库必须带「带货」标签（2026-10-12 用户指令）：文案里补 #带货，idea_notes 以【带货】开头
        if "带货" in m.get("sub_series", ""):
            if "#带货" not in m.get("publish_copy", ""):
                m["publish_copy"] = m.get("publish_copy", "").rstrip() + " #带货"
            if not m.get("idea_notes", "").startswith("【带货】"):
                m["idea_notes"] = "【带货】" + m.get("idea_notes", "")
        data = {"series_id": str(m["series_id"]), "normalized_title": m["slug"],
                "title": m["title"], "sub_series": m["sub_series"],
                "publish_copy": m.get("publish_copy", ""),
                "wechat_copy": m.get("wechat_copy", ""),
                "idea_notes": m.get("idea_notes", ""),
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
            hashtags = re.findall(r"#[^\s#]+", m.get("publish_copy", ""))
            entries.insert(0, {
                "platform": "videopublisher", "status": "pending_review",
                "video_id": str(j["video_id"]), "export_path": str(out_mp4.resolve()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata_used": {
                    "title": m["title"],
                    "description": m.get("publish_copy", ""),
                    "hashtags": hashtags,
                },
            })
            log.write_text(json.dumps({"version": "1.0", "entries": entries,
                                       "metadata": {"slug": m["slug"],
                                                    "source_mp4": mp4.name,
                                                    "cover_mode": "uploaded_and_bound"}},
                                      ensure_ascii=False, indent=2), encoding="utf-8")
            ok += 1
        else:
            print(f"     ✗ HTTP {r.status_code} {r.text[:200]}", file=sys.stderr); fail += 1

    print(f"\n成功 {ok} · 失败 {fail}" + ("（dry-run，未上传）" if dry else ""))
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
