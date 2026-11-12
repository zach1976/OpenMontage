"""第 14 首：Billkin《กีดกัน (Skyline)》副歌逐词学（2026-11-11 用户指令：截图找歌、开做教学视频）。

结构沿用歌曲课：先听官方 MV 副歌原唱 → 一句歌曲介绍 → 10 张词卡（原唱片段 → 泰语跟读 → 中文意思）
→ 回听过渡 → 回听首句与末句 → 片尾。

    python3 scripts/build_song14.py            # 准备素材 + 配音 + props
    python3 scripts/build_song14.py --render   # 再渲染一版到 renders/final_vN.mp4

时间戳来源：官方 MV 自带泰文字幕（行级）+ Demucs 分离人声后 faster-whisper small 的字符级时间（词级）。
whisper 的文字不可信，只取时间；歌词文本一律以官方字幕为准。
"""
from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.checkpoint import init_project  # noqa: E402

PID = 'thai-1000-song-14-kheedkan'
P = ROOT / 'projects' / PID
MV = P / 'assets/video/official_mv.mp4'
SRC = P / 'assets/audio/original.mp3'
PUB = P / 'composition/public'
FPS = 30
SOURCE_URL = 'https://www.youtube.com/watch?v=hJeEOzEZstU'
HOOK = (65.4, 87.3)                       # 副歌第一遍 + 「ใช่ไหม..」
REPLAY = [(65.9, 70.35), (77.6, 87.3)]    # 回听：第一句（愿意闯过去）+ 第四句（命运面前认输）

# 官方字幕原文；第三句字幕写「กีดกัน」，其余三句「กีดกั้น」—— 展示统一成「กีดกั้น」（决策日志 s14-spelling）
LINES = [
    {'at': 66.0, 'group': 0, 'th': 'กีดกั้นด้วยแผ่นฟ้า แม้ไกลฉันยินดีจะฝ่าไป', 'zh': '被天空阻隔，再远我也愿意闯过去',
     'chunks': [(66.2, 'กีดกั้นด้วย'), (67.1, 'แผ่นฟ้า '), (67.84, 'แม้ไกล'), (68.14, 'ฉันยินดีจะฝ่าไป')]},
    {'at': 70.26, 'group': 1, 'th': 'กีดกั้นด้วยภูผาสูงชันลับตา ฉันไม่หวั่นไหว', 'zh': '被高山挡住，高到看不见，我也不动摇',
     'chunks': [(70.26, 'กีดกั้นด้วย'), (71.52, 'ภูผา'), (72.1, 'สูงชันลับตา '), (73.2, 'ฉันไม่หวั่นไหว')]},
    {'at': 75.1, 'group': 2, 'th': 'กีดกั้นด้วยเวลา ฉันยินดีรอ', 'zh': '被时间阻隔，我愿意等',
     'chunks': [(75.1, 'กีดกั้นด้วย'), (76.0, 'เวลา '), (76.54, 'ฉันยินดีรอ')]},
    {'at': 77.76, 'group': 3, 'th': 'แต่กีดกั้นด้วยชะตา ฉันคงต้องยอมพ่ายแพ้ใช่ไหม', 'zh': '可被命运阻隔，我只能认输了，是吗',
     'chunks': [(77.76, 'แต่กีดกั้นด้วย'), (78.78, 'ชะตา '), (79.32, 'ฉันคงต้อง'), (80.2, 'ยอมพ่ายแพ้'), (81.9, 'ใช่ไหม')]},
    {'at': 84.3, 'group': 3, 'th': 'ใช่ไหม..', 'zh': '是吗……', 'chunks': [(84.3, 'ใช่ไหม..')]},
]
# (泰语, 中文, 中文配音, 阻隔组, 原唱起, 原唱止)
WORDS = [
    ('กีดกั้นด้วย', '被……挡住', '被……挡住。', 0, 66.12, 67.16),
    ('แผ่นฟ้า', '天空', '天空。', 0, 67.08, 67.86),
    ('แม้ไกล', '就算很远', '就算很远。', 0, 67.78, 68.30),
    ('ยินดีจะฝ่าไป', '愿意闯过去', '我愿意闯过去。', 0, 68.48, 70.40),
    ('ภูผา', '高山', '高山。', 1, 71.46, 72.16),
    ('ไม่หวั่นไหว', '不动摇', '不动摇。', 1, 73.46, 75.20),
    ('เวลา', '时间', '时间。', 2, 75.96, 76.62),
    ('ยินดีรอ', '愿意等', '愿意等。', 2, 76.76, 77.76),
    ('ชะตา', '命运', '命运。', 3, 78.72, 79.40),
    ('ยอมพ่ายแพ้', '认输', '只能认输。', 3, 80.10, 81.62),
]
# 中文谐音（2026-11-11 用户：唱歌的每个单词下面加中文谐音）——一个泰语音节对一个汉字（CLAUDE.md 高频词谐音规矩）
XIE = {
    'กีดกั้นด้วย': '吉刚堆', 'แต่กีดกั้นด้วย': '呆吉刚堆', 'แผ่นฟ้า': '潘发', 'แม้ไกล': '咩盖',
    'ฉันยินดีจะฝ่าไป': '产音迪甲发拜', 'ยินดีจะฝ่าไป': '音迪甲发拜', 'ภูผา': '普帕', 'สูงชันลับตา': '松禅腊达',
    'ฉันไม่หวั่นไหว': '产麦弯外', 'ไม่หวั่นไหว': '麦弯外', 'เวลา': '威拉', 'ฉันยินดีรอ': '产音迪罗', 'ยินดีรอ': '音迪罗',
    'ชะตา': '恰达', 'ฉันคงต้อง': '产空洞', 'ยอมพ่ายแพ้': '用派拍', 'ใช่ไหม': '猜麦', 'ใช่ไหม..': '猜麦',
}


def xie(text: str) -> str:
    return XIE[text.strip()]


NARR = {
    'intro_zh': '这是 Billkin 的《阻挡》，泰剧《以你的心诠释我的爱》的插曲。四句副歌，每一句都在说：被什么挡住了。',
    'bridge_zh': '天空、高山、时间都挡不住他，只有命运，让他问一句：是吗？再听一遍。',
    'outro_zh': '想听懂更多泰语歌，跟着泰语千词学。在泰国生活，够用了。',
}


def save(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def dur(path: Path) -> float:
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)], text=True))


def ff(*args: str) -> None:
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *args], check=True)


def setup() -> None:
    if not (P / 'project.json').exists():
        init_project(PID, title='กีดกัน (Skyline)｜Billkin 副歌逐词学', pipeline_type='animated-explainer')
    for sub in ['video', 'images', 'audio', 'fonts', 'app']:
        (PUB / sub).mkdir(parents=True, exist_ok=True)
    song13 = ROOT / 'projects/thai-1000-song-13-nalika-sai/composition/public'
    shutil.copy2(song13 / 'fonts/Sarabun-Bold.ttf', PUB / 'fonts/Sarabun-Bold.ttf')
    shutil.copy2(ROOT / 'remotion-composer/public/app/app_icon.png', PUB / 'app/app_icon.png')
    for name in ['Composition.tsx', 'Root.tsx', 'index.tsx']:
        shutil.copy2(ROOT / 'scripts/song14' / name, P / 'composition' / name)
    shutil.copy2(SRC, PUB / 'audio/original.mp3')
    vf = 'scale=1080:608:force_original_aspect_ratio=increase,crop=1080:608,fps=30'
    hook = PUB / 'video/mv_hook.mp4'
    if not hook.exists():
        ff('-ss', str(HOOK[0]), '-to', str(HOOK[1]), '-i', str(MV), '-an', '-vf', vf, '-c:v', 'libx264', '-crf', '18', str(hook))
    rep = PUB / 'video/mv_replay.mp4'
    if not rep.exists():
        parts = []
        for k, (a, b) in enumerate(REPLAY):
            part = P / f'assets/video/replay_{k}.mp4'
            ff('-ss', str(a), '-to', str(b), '-i', str(MV), '-an', '-vf', vf, '-c:v', 'libx264', '-crf', '18', str(part))
            parts.append(part)
        lst = P / 'assets/video/replay_list.txt'
        lst.write_text(''.join(f"file '{p}'\n" for p in parts))
        ff('-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy', str(rep))
    for i, (*_, a, b) in enumerate(WORDS, 1):
        still = PUB / f'images/w{i:02d}_mv.jpg'
        if not still.exists():
            ff('-ss', f'{(a + b) / 2:.2f}', '-i', str(MV), '-frames:v', '1', '-vf', 'scale=1080:608:force_original_aspect_ratio=increase,crop=1080:608', '-q:v', '2', str(still))
        src = P / f'assets/audio/w{i:02d}_source.mp3'
        if not src.exists():
            ff('-ss', str(a), '-to', str(b), '-i', str(SRC), '-af', 'afade=t=in:d=0.04,areverse,afade=t=in:d=0.08,areverse', '-c:a', 'libmp3lame', '-b:a', '192k', str(src))
    intro_still = PUB / 'images/intro_mv.jpg'
    if not intro_still.exists():
        ff('-ss', '100', '-i', str(MV), '-frames:v', '1', '-vf', 'scale=1080:608:force_original_aspect_ratio=increase,crop=1080:608', '-q:v', '2', str(intro_still))


async def synth(path: Path, text: str, lang: str) -> None:
    if path.exists() and path.stat().st_size > 500:
        return
    voice, rates = (('zh-CN-XiaoxiaoNeural', ['-3%', '+0%']) if lang == 'zh' else ('th-TH-PremwadeeNeural', ['-8%', '+0%']))
    raw = path.with_name(path.stem + '_raw.mp3')
    last = None
    for attempt in range(8):      # Premwadee 某些「文本+语速」组合稳定失败 → 换语速重试（lessons-learned）
        try:
            await edge_tts.Communicate(text, voice=voice, rate=rates[attempt % 2]).save(str(raw))
            if raw.stat().st_size < 1000:
                raise RuntimeError('empty TTS')
            break
        except Exception as e:  # noqa: BLE001
            last = e
            await asyncio.sleep(min(3 * (attempt + 1), 12))
    else:
        raise RuntimeError(f'TTS 失败：{text}（{last}）')
    ff('-i', str(raw), '-af', 'silenceremove=start_periods=1:start_silence=0.02:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_silence=0.08:start_threshold=-45dB,areverse', '-c:a', 'libmp3lame', '-b:a', '192k', str(path))
    raw.unlink()
    print('tts', path.name, flush=True)


async def audio() -> None:
    queue = [(P / f'assets/audio/{k}.mp3', v, 'zh') for k, v in NARR.items()]
    # Premwadee 对「แม้ไกล」任何语速都 NoAudioReceived，中间加空格就能出（只改配音文本，画面照旧连写）
    th_say = {'แม้ไกล': 'แม้ ไกล', 'ยินดีจะฝ่าไป': 'ยินดี จะฝ่าไป', 'ยอมพ่ายแพ้': 'ยอม พ่ายแพ้'}
    for i, (th, _zh, zh_say, *_r) in enumerate(WORDS, 1):
        queue += [(P / f'assets/audio/w{i:02d}_th.mp3', th_say.get(th, th), 'th'), (P / f'assets/audio/w{i:02d}_zh.mp3', zh_say, 'zh')]
    for row in queue:              # 串行：edge-tts 批量会限流（CLAUDE.md）
        await synth(*row)
    for f in (P / 'assets/audio').glob('*.mp3'):
        shutil.copy2(f, PUB / 'audio' / f.name)


def build() -> dict:
    cursor, blocks = 0, []

    def clip(name: str) -> dict:
        return {'file': name, 'dur': dur(PUB / 'audio' / name)}

    def add(b: dict, seconds: float) -> None:
        nonlocal cursor
        b['startFrame'], b['frames'] = cursor, max(1, round(seconds * FPS))
        cursor += b['frames']
        blocks.append(b)

    add({'id': 'song_open', 'kind': 'song_open', 'segments': [{'start': HOOK[0], 'end': HOOK[1], 'offset': 0}]}, HOOK[1] - HOOK[0])
    n = clip('intro_zh.mp3')
    add({'id': 'intro', 'kind': 'intro', 'nar': n, 'still': 'intro_mv.jpg'}, n['dur'] + .35)
    for i, (th, zh, _say, g, *_r) in enumerate(WORDS, 1):
        src, thai, chi = clip(f'w{i:02d}_source.mp3'), clip(f'w{i:02d}_th.mp3'), clip(f'w{i:02d}_zh.mp3')
        thai_at = src['dur'] + .18
        zh_at = thai_at + thai['dur'] + .15
        add({'id': f'w{i:02d}', 'kind': 'word', 'index': i - 1, 'group': g, 'th': th, 'zh': zh, 'xie': xie(th), 'source': src, 'still': f'w{i:02d}_mv.jpg',
             'thaiAt': round(thai_at, 3), 'zhAt': round(zh_at, 3)}, zh_at + chi['dur'] + .3)
    n = clip('bridge_zh.mp3')
    add({'id': 'replay_bridge', 'kind': 'replay_bridge', 'nar': n}, n['dur'] + .3)
    segs, off = [], 0.0
    for a, b in REPLAY:
        segs.append({'start': a, 'end': b, 'offset': round(off, 3)})
        off += b - a
    add({'id': 'song_replay', 'kind': 'song_replay', 'segments': segs}, off)
    n = clip('outro_zh.mp3')
    add({'id': 'outro', 'kind': 'outro', 'nar': n}, n['dur'] + .5)

    labels = {'song_open': '先听原唱副歌', 'intro': '歌曲介绍', 'replay_bridge': '回听过渡', 'song_replay': '回听首句与末句', 'outro': '泰语千词片尾'}
    review = [{'id': b['id'], 'label': b.get('th') or labels[b['kind']], 'start': b['startFrame'] / FPS, 'end': (b['startFrame'] + b['frames']) / FPS,
               'title': b.get('zh') or labels[b['kind']], 'text': b.get('zh') or (NARR.get(b.get('nar', {}).get('file', '')[:-4]) or labels[b['kind']]),
               'credit': 'Billkin 官方 MV（Nadao Music）' if b['kind'] in ('song_open', 'song_replay', 'word') else 'Microsoft Edge 小晓 / Premwadee'} for b in blocks]
    lines = [{**l, 'chunks': [{'at': a, 'text': t, 'xie': xie(t)} for a, t in l['chunks']]} for l in LINES]
    props = {'fps': FPS, 'totalFrames': cursor, 'totalSeconds': cursor / FPS, 'title': 'กีดกัน (Skyline)', 'hookStart': HOOK[0],
             'lines': lines, 'blocks': blocks, 'review_timeline': review}
    save(P / 'composition/props.json', props)
    save(P / 'artifacts/props.json', props)
    write_artifacts(props, review)
    print(PID, round(cursor / FPS, 2), 's', flush=True)
    return props


def write_artifacts(props: dict, review: list) -> None:
    save(P / 'artifacts/art_direction.json', {'palette': 'sunset plum + coral + apricot', 'motif': '四重阻隔：天空/高山/时间/命运；词卡横墙在中文意思出现时裂开'})
    (P / 'art-direction.md').write_text(
        '# 第 14 首：《กีดกัน (Skyline)》副歌\n\n'
        '- 副歌是四重阻隔的排比（天空、高山、时间、命运），整集的视觉从这里长出来。\n'
        '- 画面中段一条「阻隔栏」：唱到哪一重亮哪一重；词卡里已讲过的几重划掉。\n'
        '- 词卡下方一道横墙，中文意思出现时从中间裂开（ฝ่าไป 闯过去）。\n'
        '- 回听前把天空、高山、时间划掉，只剩命运亮着，引出末句「ใช่ไหม 是吗」。\n'
        '- 配色：落日梅紫 + 珊瑚红 + 杏色（取自原剧 I Told Sunset About You 的落日），与第 13 首夜蓝灰金、第 12 首伊森金岔开。\n'
        '- 底部远山剪影 = Skyline。封面即第一帧：核心带 640–1280 一块标题牌「泰国神曲《阻挡》」，1.2 秒后淡出交回 MV。\n')
    save(P / 'artifacts/research_brief.json', {'version': '1.0', 'topic': 'Billkin《กีดกัน (Skyline)》副歌逐词学', 'research_date': str(date.today()),
        'research_summary': '用户截图是 Billkin 现场演唱，字幕「กีดกั้นด้วยแผ่นฟ้าแม้ไกลฉันยินดีจะฝ่าไป / 即使天违人愿 相隔万里 我也愿前行」。检索确认为《กีดกัน (Skyline)》，泰剧《แปลรักฉันด้วยใจเธอ》(I Told Sunset About You) OST。按系列规矩用官方 MV（Nadao Music）而非现场转载。',
        'sources': [{'url': SOURCE_URL, 'title': 'Billkin - กีดกัน (Skyline) OST.แปลรักฉันด้วยใจเธอ [Official MV]', 'used_for': '原唱音频、画面、官方泰文字幕', 'reliability': 'primary'},
                    {'url': 'https://lyric.in.th/lyric.php?n=44247', 'title': 'lyric.in.th 歌词页', 'used_for': '歌词核对', 'reliability': 'secondary'},
                    {'url': 'https://www.dochord.com/358915/', 'title': 'dochord 和弦页', 'used_for': '歌名与歌手核对', 'reliability': 'secondary'}]})
    save(P / 'artifacts/script.json', {'version': '1.0', 'title': 'กีดกัน (Skyline)｜副歌逐词学', 'total_duration_seconds': props['totalSeconds'],
        'sections': [{'id': r['id'], 'label': r['label'], 'text': r['text'], 'start_seconds': r['start'], 'end_seconds': r['end'], 'speaker_directions': '原唱→泰语女声跟读→中文意思（小晓）'} for r in review],
        'metadata': {'source_url': SOURCE_URL, 'language': 'th+zh', 'tts': {'zh': 'zh-CN-XiaoxiaoNeural -3%', 'th': 'th-TH-PremwadeeNeural -8%'}}})
    save(P / 'artifacts/decision_log.json', {'version': '1.0', 'project_id': PID, 'decisions': [
        {'decision_id': 's14-source', 'stage': 'research', 'category': 'source_selection', 'subject': '原唱版本',
         'options_considered': [{'option_id': 'official-mv', 'label': '官方 MV（Nadao Music）', 'score': 1, 'reason': '系列规矩：歌曲片用官方 MV 做背景'},
                                {'option_id': 'live', 'label': '截图里的现场版', 'score': .3, 'reason': '转载来源不明、现场混响重'}],
         'selected': 'official-mv', 'reason': '官方版权方上传、音质清楚、自带泰文字幕', 'user_visible': True},
        {'decision_id': 's14-spelling', 'stage': 'script', 'category': 'text', 'subject': 'กีดกัน / กีดกั้น 拼写',
         'options_considered': [{'option_id': 'as-subtitle', 'label': '照字幕逐句', 'score': .4, 'reason': '官方字幕第三句写 กีดกัน，其余写 กีดกั้น，同一首歌里两种拼法会让初学者以为是两个词'},
                                {'option_id': 'unify', 'label': '统一成 กีดกั้น', 'score': 1, 'reason': '与用户截图、四句里的三句一致；歌名本身保留 กีดกัน'}],
         'selected': 'unify', 'reason': '教学一致性', 'user_visible': True},
        {'decision_id': 's14-runtime', 'stage': 'proposal', 'category': 'render_runtime_selection', 'subject': 'Video composition runtime',
         'options_considered': [{'option_id': 'remotion', 'label': 'Remotion', 'score': 1, 'reason': '沿用歌曲课逐帧歌词同步'}],
         'selected': 'remotion', 'reason': '与前 13 首同一套制作方式', 'user_visible': False}]})
    pj = P / 'artifacts/publish.json'
    meta = json.loads(pj.read_text()) if pj.exists() else {}
    meta.update({'series_id': 1, 'sub_series': '泰语神曲', 'slug': 'thai_song_14_kheedkan', 'title': '泰国神曲阻挡副歌逐词学',
                 'publish_copy': '泰国神曲阻挡副歌逐词学\n先听 Billkin《กีดกัน》（阻挡）副歌原唱，再拆十个重点词组：天空、高山、时间都挡不住，只有命运让他问一句「是吗」。最后回听首句和末句。\n\n#泰语 #泰语学习 #泰语千词 #泰语歌曲 #泰国神曲 #Billkin',
                 'credits': f'歌曲与画面：Billkin《กีดกัน (Skyline)》官方 MV（Nadao Music）{SOURCE_URL}；中文教学与剪辑：泰语千词。'})
    save(pj, meta)


def render() -> Path:
    out_dir = P / 'renders'
    out_dir.mkdir(exist_ok=True)
    n = len(list(out_dir.glob('final_v*.mp4'))) + 1
    out = out_dir / f'final_v{n}.mp4'
    subprocess.run(['npx', 'remotion', 'render', str(P / 'composition/index.tsx'), 'KheedkanLesson', str(out),
                    f'--props={P / "composition/props.json"}', f'--public-dir={PUB}', '--codec=h264', '--crf=20',
                    '--audio-codec=aac', '--concurrency=4', '--timeout=120000', '--log=error'], cwd=ROOT / 'remotion-composer', check=True)
    ff('-i', str(out), '-frames:v', '1', '-q:v', '2', str(out_dir / f'cover_v{n}.jpg'))
    meta = json.loads((P / 'artifacts/publish.json').read_text())
    meta['video_path'], meta['cover_path'] = f'renders/final_v{n}.mp4', f'renders/cover_v{n}.jpg'
    save(P / 'artifacts/publish.json', meta)
    print('rendered', out, round(dur(out), 2), flush=True)
    return out


async def main() -> None:
    setup()
    await audio()
    build()
    if '--render' in sys.argv:
        render()


if __name__ == '__main__':
    asyncio.run(main())
