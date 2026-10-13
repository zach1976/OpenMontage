#!/usr/bin/env python3
"""Build one local review hub for the completed Thai and Vietnamese couple series."""
from __future__ import annotations

import html
import json
from pathlib import Path

REPO=Path(__file__).resolve().parent.parent
SHARED=REPO/'projects/_shared/couple-series'
thai=json.loads((SHARED/'series_plan.json').read_text())['thai_episodes']
viet=json.loads((SHARED/'vietnamese_plan.json').read_text())['episodes']
episodes=[('泰语',1,'thai-lovers-terms-phrases','泰语情侣称呼与常用语')]
episodes += [('泰语',e['number'],e['project_id'],e['title']) for e in thai]
episodes += [('越南语',e['number'],e['project_id'],e['title']) for e in viet]
cards=[]
for lang,num,pid,title in episodes:
    root=REPO/'projects'/pid
    pub=root/'artifacts/publish_log.json'
    log=json.loads(pub.read_text()) if pub.exists() else {}
    video_id=(log.get('entries') or [{}])[0].get('video_id','')
    video=sorted((root/'renders').glob('*.mp4'),key=lambda p:p.stat().st_mtime)[-1]
    metadata=root/'artifacts/publish.json'
    publish=json.loads(metadata.read_text()) if metadata.exists() else {}
    cover=root/publish.get('cover_path','renders/cover-v1.jpg')
    if not cover.exists():
        cover=root/'renders/cover-v3.png'
    rel='../../'+pid+'/'
    cards.append(f'<article><a class="cover" href="{rel}review.html"><img src="{rel}'+
      html.escape(str(cover.relative_to(root)))+f'" alt="第{num}期封面"></a><div class="body">'+
      f'<span class="tag">{lang} · {num:02d}</span><h2>{html.escape(title)}</h2>'+ 
      f'<p>43–57 秒 · 入库编号 {video_id}</p><div class="links"><a href="{rel}review.html">打开审片页</a>'+ 
      f'<a href="{rel}{video.relative_to(root)}">播放成片</a></div></div></article>')
css='''body{margin:0;background:#0c1e24;color:#f7efdc;font-family:"PingFang SC",sans-serif}main{max-width:1100px;margin:auto;padding:48px 24px 80px}h1{font-size:38px;margin:0 0 10px}header p{color:#c9b98e;font-size:17px;margin:0 0 38px}section h2{font-size:27px;margin:45px 0 20px;color:#e8bb78}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:22px}article{background:#17323a;border:1px solid #416263;border-radius:16px;overflow:hidden}article .cover{display:block;height:420px;overflow:hidden;background:#102f31}article img{width:100%;height:100%;object-fit:contain}article .body{padding:18px 20px 23px}article h2{font-size:21px;margin:8px 0;color:#fff8e9}article p{font-size:14px;color:#b8c9c2}.tag{font-size:13px;color:#e7bd83;letter-spacing:2px}.links{display:flex;gap:16px;margin-top:18px}.links a{color:#f0cf91;text-decoration:none;font-weight:700}.links a:hover{text-decoration:underline}'''
page=f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>情侣称呼与常用语 · 系列审片</title><style>{css}</style><main><header><h1>情侣称呼与常用语</h1><p>泰语 6 期 · 越南语 6 期｜已导出并登记到待发布库</p></header><section><h2>泰语系列</h2><div class="grid">{"".join(cards[:6])}</div></section><section><h2>越南语系列</h2><div class="grid">{"".join(cards[6:])}</div></section></main></html>'
out=SHARED/'review.html'
out.write_text(page)
print(out)
