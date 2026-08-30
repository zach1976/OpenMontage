#!/usr/bin/env python3
"""逐段核对成片里每个配音区间是否真的有声，并量出人声与垫乐的差距。

本地转写校验在这台机器上不可用（whisper 无缓存 + huggingface 不通），
用能量对齐替代：把 props.speak 的每个区间单独 volumedetect 一遍。

**判据必须相对垫乐，不能用固定阈值。**（2026-08-29 踩过）
禅意 01 有四段旁白因为 `Sequence from` 用了全片绝对秒（应该减去场景起点）
根本没播出来，但那几段仍有垫乐垫着、量到 −44.7dB —— 比固定阈值 −45dB 高，
于是"静默 0 段"，检查全过，最后是用户听出来片尾没说话。
现在拿每段和纯垫乐中位数比：**高不出 6dB 就判为「没响」**。

    python3 scripts/verify_audio_coverage.py <project_id> [mp4 文件名]
"""
import json, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def mean_db(mp4, start, dur):
    out = subprocess.run(['ffmpeg','-hide_banner','-nostats','-ss',str(start),'-t',str(dur),
        '-i',str(mp4),'-af','volumedetect','-f','null','-'], capture_output=True, text=True).stderr
    m = re.search(r'mean_volume:\s*(-?[\d.]+) dB', out)
    return float(m.group(1)) if m else None

def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    pid = sys.argv[1]
    proj = REPO/'projects'/pid
    props = json.load(open(proj/'composition/props.json'))
    if len(sys.argv) > 2:
        mp4 = proj/'renders'/sys.argv[2]
    else:
        mp4 = max((proj/'renders').glob('*.mp4'), key=lambda p: p.stat().st_mtime)
    print(f'片子：{mp4.name}')

    speak = props['speak']
    vals = [mean_db(mp4, a, max(0.25, b-a)) for a, b in speak]

    # 先量纯垫乐的底噪，判据全部相对它
    gaps, prev = [], 0.0
    for a, b in speak:
        if a - prev > 0.9: gaps.append((prev+0.15, a-0.15))
        prev = max(prev, b)
    gv = sorted(x for x in (mean_db(mp4, a, min(1.5, b-a)) for a, b in gaps[:12]) if x is not None)
    bed = gv[len(gv)//2] if gv else None

    MARGIN = 6.0
    dead = [(a, b, v) for (a, b), v in zip(speak, vals)
            if v is None or (bed is not None and v - bed < MARGIN) or v < -45]
    ok = sorted(v for v in vals if v is not None)
    print(f'配音区间 {len(speak)} 段，没响 {len(dead)} 段'
          + (f'（判据：比垫乐 {bed:.1f}dB 高不足 {MARGIN:.0f}dB）' if bed is not None else '（判据：<-45dB）'))
    if ok:
        print('  人声区间 mean_volume 中位数: %.1f dB (最低 %.1f / 最高 %.1f)' % (ok[len(ok)//2], ok[0], ok[-1]))
    if dead:
        print('  ✗ 没响的段：')
        for a, b, v in dead:
            print('     %6.2f → %6.2f  %s' % (a, b, ('%.1f dB' % v) if v is not None else 'n/a'))
    if bed is not None:
        print('  纯垫乐区间 mean_volume 中位数: %.1f dB' % bed)
        if ok: print('  人声高出垫乐 %.1f dB' % (ok[len(ok)//2] - bed))

    out = subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(mp4),
                          '-af','volumedetect','-f','null','-'], capture_output=True, text=True).stderr
    print('  整片:', re.search(r'mean_volume:.*', out).group(0), '/', re.search(r'max_volume:.*', out).group(0))
    return 2 if dead else 0

if __name__ == '__main__':
    raise SystemExit(main())
