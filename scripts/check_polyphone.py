#!/usr/bin/env python3
"""扫 script.json 的中文口播，找 TTS 真会读错的多音字。

只报**确认踩过的**模式，不做宽泛匹配——宽泛匹配会把「为什么」「因为」「听得见」
全报出来，噪声淹掉真问题，反而没人看。

已确认的坑：
  长  当「长度」讲时的单字用法 → edge-tts 读成 zhǎng。
      安全写法：塞进复合词（多长/长度/加长），或换说法。
      注意 年长/长辈/成长/长大 里的 zhǎng 是对的，不报。

以后再撞到新的，往 RULES 里加一条，别改成模糊匹配。

    python3 scripts/check_polyphone.py <project_id>
"""
import json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

RULES = [
    dict(char='长',
         ok_zhang=['年长', '长辈', '成长', '长大', '长子', '生长', '长相', '家长', '校长', '长老'],
         ok_chang=['多长', '长度', '加长', '长期', '长久', '很长', '太长', '长长'],
         hint='单字「长」当长度讲会被读成 zhǎng；改用 多长/长度/加长，或换说法'),
]

def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    p = REPO/'projects'/sys.argv[1]/'artifacts'/'script.json'
    units = (json.load(open(p)).get('metadata') or {}).get('tts_units') or []
    hits = []
    for u in units:
        if u['lang'] != 'zh':
            continue
        for rule in RULES:
            for m in re.finditer(rule['char'], u['text']):
                win = u['text'][max(0, m.start()-1):m.start()+2]
                if any(w in win for w in rule['ok_zhang'] + rule['ok_chang']):
                    continue
                hits.append((u['id'], win, rule['hint']))
    if hits:
        print(f'⚠️  {len(hits)} 处可能读错：')
        for uid, win, hint in hits:
            print(f'   {uid:16} …{win}…   {hint}')
        return 1
    print(f'口播多音字自查：{len([u for u in units if u["lang"]=="zh"])} 段中文，无风险 ✅')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
