"""Prepare the Kong live teaching cut for the animated-explainer pipeline."""
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
from lib.checkpoint import init_project

PID = 'thai-1000-song-12-sai-naen-hua-jai'
P = ROOT / 'projects' / PID
SRC = P / 'assets/audio/kong_live.mp3'
FPS = 30
SOURCE_URL = 'https://www.youtube.com/watch?v=dRzFzflCQqs'
LINES = [
    {'th': 'ให้ใจคิดถึง ไม่เคยเป็นมาก่อน', 'zh': '心里想念一个人，过去从没有过', 'at': 0.0},
    {'th': 'ไม่ได้อ้อนวอน เรียกร้องขอจากใคร', 'zh': '没有向谁祈求，也没有强求', 'at': 3.6},
    {'th': 'สิ่งที่แนมบ่เห็น เคยปิดใจบ่ยอมรับมัน', 'zh': '看不见的牵绊，我曾关上心不肯相信', 'at': 7.2},
    {'th': 'แต่ตอนนี้ ทุกอย่างกลับแปรผัน', 'zh': '可现在，一切都变了', 'at': 14.7},
]
WORDS = [
    ('คิดถึง', '想念', 'คิดถึง，就是想念。', 50.9, 54.5),
    ('อ้อนวอน', '恳求', 'อ้อนวอน，是恳求。', 54.5, 58.1),
    ('แนม', '看', 'แนม，在伊森语里是看。', 58.1, 62.0),
    ('บ่', '不', 'บ่，在伊森语里是不。', 58.1, 62.0),
    ('ปิดใจ', '关上心', 'ปิดใจ，就是把心关起来。', 62.0, 65.6),
    ('แปรผัน', '改变', 'แปรผัน，是发生改变。', 65.6, 69.4),
]

def save(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def duration(path: Path) -> float:
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)], text=True))

def cut(start: float, end: float, out: Path) -> None:
    if out.exists() and out.stat().st_size > 1000:
        return
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(start), '-to', str(end), '-i', str(SRC), '-vn', '-c:a', 'libmp3lame', '-b:a', '192k', str(out)], check=True)

def setup() -> None:
    init_project(PID, title='สายแนนหัวใจ｜Kong 现场版泰语歌曲教学', pipeline_type='animated-explainer')
    for sub in ['assets/images', 'assets/audio', 'composition/public/images', 'composition/public/audio', 'composition/public/fonts']:
        (P / sub).mkdir(parents=True, exist_ok=True)
    prior = ROOT / 'projects/thai-1000-song-11-mai-mi-khrai-ru-tua-rao/composition/public'
    for name in ['isan-fields.png', 'isan-thread.png']:
        shutil.copy2(P / 'assets/images' / name, P / 'composition/public/images' / name)
    shutil.copy2(prior / 'images/promo-card-v4.png', P / 'composition/public/images/promo-card-v4.png')
    shutil.copy2(prior / 'fonts/Sarabun-Bold.ttf', P / 'composition/public/fonts/Sarabun-Bold.ttf')
    for name in ['Composition.tsx', 'Root.tsx', 'index.tsx']:
        shutil.copy2(ROOT / 'scripts/song12' / name, P / 'composition' / name)
    (P / 'art-direction.md').write_text('# Isan thread at golden hour\n\nDocumentary rural Isan photographs: rice field dusk and indigo handwoven cotton with a pale binding thread. Thai and Chinese remain crisp in a dark ink panel. The first frame is a usable cover. The live song starts immediately; short teaching cards follow; no unrelated lecture. Warm gold marks the fate motif.\n')
    assert SRC.exists(), SRC
    cut(50.9, 69.4, P / 'assets/audio/song_open.mp3')
    for i, (*_, start, end) in enumerate(WORDS, 1):
        cut(start, end, P / 'assets/audio' / f'w{i}_source.mp3')

async def synth(path: Path, line: str, language: str) -> None:
    if path.exists() and path.stat().st_size > 500:
        return
    voice, rate = ('zh-CN-XiaoxiaoNeural', '+12%') if language == 'zh' else ('th-TH-PremwadeeNeural', '+6%')
    raw = path.with_name(path.stem + '_raw.mp3')
    for attempt in range(8):
        try:
            await edge_tts.Communicate(line, voice=voice, rate=rate).save(str(raw))
            if raw.stat().st_size < 1000:
                raise RuntimeError('empty TTS')
            break
        except Exception:
            if attempt == 7:
                raise
            await asyncio.sleep(min(3 * (attempt + 1), 12))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(raw), '-af', 'silenceremove=start_periods=1:start_silence=0.02:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_silence=0.08:start_threshold=-45dB,areverse', '-c:a', 'libmp3lame', '-b:a', '192k', str(path)], check=True)
    raw.unlink()
    print('tts', path.name, flush=True)

async def audio() -> None:
    queue = [
        (P / 'assets/audio/bridge_zh.mp3', '这首歌里，สายแนน就像一根线，把两个人的命运牵在一起。', 'zh'),
        (P / 'assets/audio/replay_bridge_zh.mp3', '这几个词听懂了，再听一遍现场。', 'zh'),
        (P / 'assets/audio/outro_zh.mp3', '想听懂更多泰语歌？跟着泰语千词继续学。在泰国生活，够用了。', 'zh'),
    ]
    for i, (th, _, explanation, *_) in enumerate(WORDS, 1):
        queue.extend([(P / 'assets/audio' / f'w{i}_th.mp3', th + '。', 'th'), (P / 'assets/audio' / f'w{i}_zh.mp3', explanation, 'zh')])
    sem = asyncio.Semaphore(2)
    async def one(row):
        async with sem:
            await synth(*row)
    await asyncio.gather(*(one(x) for x in queue))
    for f in (P / 'assets/audio').glob('*.mp3'):
        shutil.copy2(f, P / 'composition/public/audio' / f.name)

def build() -> None:
    cursor = 0
    blocks = []
    def clip(name: str):
        return {'file': name, 'dur': duration(P / 'assets/audio' / name)}
    def add(b: dict):
        nonlocal cursor
        b['startFrame'] = cursor
        b['frames'] = max(1, round(b['dur'] * FPS))
        cursor += b['frames']
        blocks.append(b)
    song = clip('song_open.mp3')
    add({'id': 'song_open', 'kind': 'song_open', 'audio': song, 'dur': song['dur']})
    intro = clip('bridge_zh.mp3')
    add({'id': 'bridge', 'kind': 'bridge', 'nar': intro, 'dur': intro['dur'] + .2})
    for i, (th, zh, *_rest) in enumerate(WORDS, 1):
        src, thai, chinese = clip(f'w{i}_source.mp3'), clip(f'w{i}_th.mp3'), clip(f'w{i}_zh.mp3')
        thai_at = src['dur'] + .12
        zh_at = thai_at + thai['dur'] + .12
        add({'id': f'w{i}', 'kind': 'word', 'index': i - 1, 'th': th, 'zh': zh, 'source': src, 'thaiAudio': thai, 'zhAudio': chinese, 'thaiAt': thai_at, 'zhAt': zh_at, 'dur': zh_at + chinese['dur'] + .13})
    replay_bridge = clip('replay_bridge_zh.mp3')
    add({'id': 'replay_bridge', 'kind': 'replay_bridge', 'nar': replay_bridge, 'dur': replay_bridge['dur'] + .1})
    add({'id': 'song_replay', 'kind': 'song_replay', 'audio': song, 'dur': song['dur']})
    outro = clip('outro_zh.mp3')
    add({'id': 'outro', 'kind': 'outro', 'nar': outro, 'dur': outro['dur'] + .3})
    review = []
    for b in blocks:
        label = b.get('th', {'song_open':'先听现场','bridge':'歌曲介绍','replay_bridge':'回听过渡','song_replay':'再听现场','outro':'泰语千词推广'}.get(b['kind'],''))
        review.append({'id':b['id'],'label':label,'start':b['startFrame']/FPS,'end':(b['startFrame']+b['frames'])/FPS,'title':b['id'],'text':label,'credit':SOURCE_URL})
    props = {'fps':FPS,'totalFrames':cursor,'totalSeconds':cursor/FPS,'title':'สายแนนหัวใจ','artist':'ก้อง ห้วยไร่','lines':LINES,'blocks':blocks,'review_timeline':review}
    save(P / 'composition/props.json', props)
    save(P / 'artifacts/props.json', props)
    save(P / 'artifacts/research_brief.json', {'version':'1.0','topic':'สายแนนหัวใจ｜Kong live','research_date':str(date.today()),'research_summary':'核对 SOUND ME HANG 官方现场视频，选 50.9–69.4 秒人声清楚段；歌词与伊森语词义核对。','sources':[{'url':SOURCE_URL,'title':'SOUND ME HANG Official live','used_for':'现场原唱音频','reliability':'primary'},{'url':'https://musicstation.kapook.com/สายแนนหัวใจ.html','title':'Kapook lyrics','used_for':'歌词核对','reliability':'secondary'},{'url':'https://esan108.com/dict/view/สายแนน','title':'อีสานร้อยแปด','used_for':'สายแนน 伊森语释义','reliability':'dictionary'}]})
    save(P / 'artifacts/proposal_packet.json', {'version':'1.0','title':'สายแนนหัวใจ｜Kong 现场版泰语歌曲教学','selected_concept':{'concept_id':'live-lesson','rationale':'延续系列已审核的现场原唱→逐词→回听结构。'},'production_plan':{'pipeline':'animated-explainer','render_runtime':'remotion','composition_mode':'atelier','target_duration_seconds':round(cursor/FPS),'visual_approach':'伊森乡间黄昏与靛蓝织物','audio_source':SOURCE_URL},'approval':{'status':'approved','user_notes':'用户明确要求开始制作该首歌并沿用此前歌曲教学方式。'}})
    save(P / 'artifacts/script.json', {'version':'1.0','title':'สายแนนหัวใจ｜现场版逐词学','sections':[{'id':b['id'],'label':r['label'],'text':r['text'],'start_seconds':r['start'],'end_seconds':r['end'],'speaker_directions':'原唱→泰语女声→中文解释。'} for b,r in zip(blocks,review)],'total_duration_seconds':cursor/FPS,'metadata':{'source_url':SOURCE_URL,'language':'th+zh','tts':{'zh':'zh-CN-XiaoxiaoNeural','th':'th-TH-PremwadeeNeural'}}})
    save(P / 'artifacts/scene_plan.json', {'version':'1.0','style_playbook':'isan-thread-at-golden-hour','scenes':[{'id':b['id'],'type':'animation','description':r['label'],'start_seconds':r['start'],'end_seconds':r['end'],'script_section_id':b['id'],'required_assets':[{'type':'audio','description':'现场原唱或配音','source':'local'},{'type':'image','description':'伊森田野与织物','source':'generated'}]} for b,r in zip(blocks,review)]})
    assets = [{'id':f.stem,'type':'audio','path':str(f.relative_to(P)),'source_tool':'edge-tts' if f.stem.endswith(('_th','_zh')) else 'ffmpeg/source-youtube','scene_id':'all','cost_usd':0,'format':'mp3'} for f in sorted((P/'assets/audio').glob('*.mp3'))]
    assets += [{'id':f.stem,'type':'image','path':str(f.relative_to(P)),'source_tool':'image_gen','scene_id':'all','cost_usd':0,'format':'png'} for f in (P/'assets/images').glob('*.png')]
    save(P / 'artifacts/asset_manifest.json', {'version':'1.0','assets':assets,'total_cost_usd':0,'metadata':{'source_url':SOURCE_URL}})
    save(P / 'artifacts/decision_log.json', {'version':'1.0','project_id':PID,'decisions':[{'decision_id':'s12-runtime','stage':'proposal','category':'render_runtime_selection','subject':'Video composition runtime','options_considered':[{'option_id':'remotion','label':'Remotion','score':1,'reason':'已审核系列的逐帧歌词同步与音轨时间线'},{'option_id':'hyperframes','label':'HyperFrames','score':.7,'reason':'动效灵活，歌曲音频逐词同步需要重建'},{'option_id':'ffmpeg','label':'FFmpeg','score':.3,'reason':'逐词高亮和卡面布局受限'}],'selected':'remotion','reason':'沿用前作用户批准的系列制作方式。','user_visible':True,'user_approved':True},{'decision_id':'s12-mode','stage':'proposal','category':'composition_mode','subject':'Composition authoring mode','options_considered':[{'option_id':'atelier','label':'Atelier','score':1,'reason':'伊森织物和乡间视觉专门设计'},{'option_id':'templated','label':'Templated','score':.4,'reason':'易与其他歌曲外观重复'}],'selected':'atelier','reason':'歌词文化背景需要独立视觉。','user_visible':True,'user_approved':True}]})
    save(P / 'artifacts/publish.json', {'series_id':1,'sub_series':'泰语神曲','slug':'thai_song_12_sai_naen_hua_jai','title':'泰语千词｜สายแนนหัวใจ Kong 现场版逐词学','video_path':'renders/final-v1.mp4','cover_path':'renders/cover-v1.jpg','publish_copy':'先听 Kong 现场版《สายแนนหัวใจ》，再学伊森语与泰语关键词，最后回听。\n\n#泰语 #泰语学习 #泰语千词 #泰语歌曲','credits':f'歌曲现场演唱：ก้อง ห้วยไร่；音源：{SOURCE_URL}；中文教学与剪辑：泰语千词。','note':'待审片；未入库。'})
    print(PID, round(cursor/FPS, 2), 'seconds', flush=True)

async def main():
    setup()
    await audio()
    build()

if __name__ == '__main__':
    asyncio.run(main())
