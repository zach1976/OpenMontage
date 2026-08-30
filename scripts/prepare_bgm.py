#!/usr/bin/env python3
"""把一首垫乐裁到片长、尾部淡出，并把响度对齐到系列基准。

各集选不同的曲子，源响度差好几 dB；不对齐的话 props 里的 volume 就不可比，
上一集踩过：warm_gtr 比基准轻 5.6dB，垫乐在成片里几乎听不见。

    python3 scripts/prepare_bgm.py <project_id> <track_name>
"""
import json, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MUSIC = REPO/'projects/thai-1000-zen-01-impermanence/assets/music'
BASELINE = 'fresh_folk'      # ep01 用的那首，作为系列基准

def duration(p):
    out = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                          '-of','csv=p=0',str(p)], capture_output=True, text=True)
    return float(out.stdout.strip())


def mean_db(p):
    out = subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(p),
                          '-af','volumedetect','-f','null','-'],
                         capture_output=True, text=True).stderr
    return float(re.search(r'mean_volume:\s*(-?[\d.]+) dB', out).group(1))

def main():
    if len(sys.argv) < 3:
        print(__doc__); return 1
    pid, track = sys.argv[1], sys.argv[2]
    proj = REPO/'projects'/pid
    total = json.load(open(proj/'composition/props.json'))['totalSeconds']
    src = MUSIC/f'{track}.mp3'
    base_db, src_db = mean_db(MUSIC/f'{BASELINE}.mp3'), mean_db(src)
    gain = round(base_db - src_db, 1)
    dst = proj/'composition/public/music/bgm.mp3'
    dst.parent.mkdir(parents=True, exist_ok=True)
    af = f'volume={gain}dB,afade=t=out:st={round(total-2.5,3)}:d=2.5' if abs(gain) > 0.2 \
         else f'afade=t=out:st={round(total-2.5,3)}:d=2.5'
    # 源比片长短就自动循环补齐，别让垫乐中途断掉（踩过：fresh_uku 只有 54s，片长 85s）
    src_len = duration(src)
    cmd = ['ffmpeg','-y','-loglevel','error']
    if src_len < total:
        cmd += ['-stream_loop', str(int(total // src_len) + 1)]
    cmd += ['-i',str(src),'-t',str(total),'-af',af,'-ar','44100','-b:a','192k',str(dst)]
    subprocess.run(cmd, check=True)

    got = duration(dst)
    print(f'{track}: {src_db:+.1f}dB  基准 {BASELINE}: {base_db:+.1f}dB  → 补 {gain:+.1f}dB')
    if src_len < total:
        print(f'  源只有 {src_len:.1f}s < 片长 {total}s，已循环补齐')
    print(f'  {dst}  实际 {got:.1f}s（需要 {total}s）  校准后 {mean_db(dst):+.1f}dB')
    if abs(got - total) > 0.5:
        print(f'  ⚠️  时长对不上，检查源文件', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
