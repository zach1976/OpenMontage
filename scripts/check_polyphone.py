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
    dict(char='句',
         ok_zhang=[],
         # 「数词 + 句」（第三句 / 六句都）是安全的 —— 2026-09-11 把 edge-tts 合出来的
         # 六段拿 faster-whisper 回读，第一到第六句全部读对。原先只白名单了「一句」，
         # 于是把「第二句」也拦了，那是误报：出问题的是**没有前字**的单字句（句尾）。
         ok_chang=['句子', '这句', '那句', '整句', '几句', '句号',
                   *[f'{n}句' for n in '一二三四五六七八九十两半上下每'],
                   *[f'{n}句' for n in '0123456789']],
         hint='「句尾」里的单字「句」会被读错（2026-09-10 用户听出来）；'
              '改用「句子最后」「最后那个字」，或塞进 句子/一句/这句 这类复合词'),
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
