"""Build the approved official-chorus revision of song 12."""
from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from build_song12 import synth, duration

PID = 'thai-1000-song-12-sai-naen-hua-jai'
P = ROOT / 'projects' / PID
SRC = P / 'assets/audio/official-mv-candidate.webm'
FPS = 30
URL = 'https://www.youtube.com/watch?v=NSm8ZXEuhL0'
LINES = [
    {'th': 'ต่อจากนี้ สิคอยดูแล เจ้าให้ดีๆ', 'zh': '从今以后，我会好好照顾你', 'at': 0},
    {'th': 'บ่ให้ผู้ใด๋เข้ามากล้ำกลาย ในชีวิตเจ้า', 'zh': '不让任何人打扰你的生活', 'at': 3.5},
    {'th': 'ทั้งที่ใจบ่เชื่อว่าความฮักนั้นมีจริงอยู่บ่', 'zh': '我本来不相信爱情真的存在', 'at': 9.1},
    {'th': 'แต่ก็งง ชีวิตเจ้าของ เป็นหยังต้องมาดูแล', 'zh': '却不懂自己为何想照顾你', 'at': 14.1},
    {'th': 'คนๆ หนึ่งที่เฮาบ่เคยฮู้จักแต่ฮักไปเบิดทั้งใจ', 'zh': '从未认识的人，我却已倾心爱上', 'at': 19.0},
    {'th': 'หรือย้อนว่าเวรว่ากรรมอันใด เฮ็ดให้เฮาพ้อกัน', 'zh': '究竟是什么因缘，让我们相遇', 'at': 22.8},
]
WORDS = [
    ('ดูแล', '照顾', 'ดูแล，就是照顾。', 68.4, 71.3),
    ('ความฮัก', '爱情', 'ความฮัก，在伊森语里是爱情。', 76.9, 81.9),
    ('ฮู้จัก', '认识', 'ฮู้จัก，在伊森语里是认识。', 86.8, 90.6),
    ('พ้อกัน', '相遇', 'พ้อกัน，就是相遇。', 92.0, 97.0),
]

def save(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def cut(start: float, end: float, out: Path) -> None:
    if out.exists() and out.stat().st_size > 1000:
        return
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(start), '-to', str(end), '-i', str(SRC), '-vn', '-af', 'afade=t=in:st=0:d=0.08,afade=t=out:st='+str(end-start-.12)+':d=0.12,loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'pcm_s16le', str(out)], check=True)

async def make_audio() -> None:
    assert SRC.exists(), SRC
    aud = P / 'assets/audio'
    pub = P / 'composition/public/audio'
    pub.mkdir(parents=True, exist_ok=True)
    cut(67.8, 97.0, aud / 'chorus_official_v2.wav')
    for i, (_, _, _, a, b) in enumerate(WORDS, 1):
        cut(a, b, aud / f'w{i}_source_v2.wav')
    queue = [
        (aud / 'bridge_v2_zh.mp3', '这一段最抓耳：想好好照顾你，也想知道，是什么让我们相遇。', 'zh'),
        (aud / 'replay_bridge_v2_zh.mp3', '四个词听懂了，再听一遍副歌。', 'zh'),
    ]
    for i, (th, _, explanation, *_range) in enumerate(WORDS, 1):
        queue += [(aud / f'w{i}_v2_th.mp3', th + '。', 'th'), (aud / f'w{i}_v2_zh.mp3', explanation, 'zh')]
    sem = asyncio.Semaphore(2)
    async def one(row):
        async with sem:
            await synth(*row)
    await asyncio.gather(*(one(row) for row in queue))
    names = ['chorus_official_v2.wav', 'bridge_v2_zh.mp3', 'replay_bridge_v2_zh.mp3', 'outro_zh.mp3']
    for i in range(1, 5):
        names += [f'w{i}_source_v2.wav', f'w{i}_v2_th.mp3', f'w{i}_v2_zh.mp3']
    for name in names:
        shutil.copy2(aud / name, pub / name)

def build() -> None:
    blocks = []
    cursor = 0
    def clip(name): return {'file': name, 'dur': duration(P / 'assets/audio' / name)}
    def add(block):
        nonlocal cursor
        block['startFrame'] = cursor
        block['frames'] = round(block['dur'] * FPS)
        cursor += block['frames']
        blocks.append(block)
    song = clip('chorus_official_v2.wav')
    add({'id':'song_open','kind':'song_open','audio':song,'dur':song['dur']})
    bridge = clip('bridge_v2_zh.mp3')
    add({'id':'bridge','kind':'bridge','nar':bridge,'dur':bridge['dur']+.2})
    for i, (th, zh, *_rest) in enumerate(WORDS, 1):
        src, thai, chinese = clip(f'w{i}_source_v2.wav'), clip(f'w{i}_v2_th.mp3'), clip(f'w{i}_v2_zh.mp3')
        thai_at = src['dur'] + .12
        zh_at = thai_at + thai['dur'] + .12
        add({'id':f'w{i}','kind':'word','index':i-1,'th':th,'zh':zh,'source':src,'thaiAudio':thai,'zhAudio':chinese,'thaiAt':thai_at,'zhAt':zh_at,'dur':zh_at+chinese['dur']+.13})
    replay = clip('replay_bridge_v2_zh.mp3')
    add({'id':'replay_bridge','kind':'replay_bridge','nar':replay,'dur':replay['dur']+.1})
    add({'id':'song_replay','kind':'song_replay','audio':song,'dur':song['dur']})
    outro = clip('outro_zh.mp3')
    add({'id':'outro','kind':'outro','nar':outro,'dur':outro['dur']+.3})
    labels = {'song_open':'先听官方原唱副歌','bridge':'歌曲介绍','replay_bridge':'回听过渡','song_replay':'再听官方原唱副歌','outro':'泰语千词推广'}
    review = [{'id':b['id'],'label':b.get('th',labels.get(b['id'],'')),'start':b['startFrame']/FPS,'end':(b['startFrame']+b['frames'])/FPS,'title':b['id'],'text':b.get('th',labels.get(b['id'],'')),'credit':URL} for b in blocks]
    props = {'fps':FPS,'totalFrames':cursor,'totalSeconds':cursor/FPS,'title':'สายแนนหัวใจ','artist':'ก้อง ห้วยไร่','lines':LINES,'blocks':blocks,'review_timeline':review}
    save(P / 'composition/props.json', props)
    save(P / 'artifacts/props_v2.json', props)
    script = json.loads((P / 'artifacts/script.json').read_text())
    for section, row in zip(script['sections'], review):
        section['start_seconds'], section['end_seconds'] = row['start'], row['end']
    script['total_duration_seconds'] = cursor/FPS
    save(P / 'artifacts/script.json', script)
    scene = {'version':'1.0','style_playbook':'isan-thread-at-golden-hour','scenes':[{'id':b['id'],'type':'animation','description':r['label'],'start_seconds':r['start'],'end_seconds':r['end'],'script_section_id':b['id'],'required_assets':[{'type':'audio','description':'官方原唱副歌或配音','source':'local'},{'type':'image','description':'伊森田野与织物','source':'local'}]} for b,r in zip(blocks,review)]}
    save(P / 'artifacts/scene_plan.json', scene)
    names = set(['chorus_official_v2.wav','bridge_v2_zh.mp3','replay_bridge_v2_zh.mp3','outro_zh.mp3'])
    for i in range(1,5): names.update([f'w{i}_source_v2.wav', f'w{i}_v2_th.mp3', f'w{i}_v2_zh.mp3'])
    assets = [{'id':Path(name).stem,'type':'audio','path':'assets/audio/'+name,'source_tool':'edge-tts' if name.endswith(('_th.mp3','_zh.mp3')) else 'ffmpeg/source-youtube','scene_id':'all','cost_usd':0,'format':Path(name).suffix[1:]} for name in sorted(names)]
    assets += [{'id':f.stem,'type':'image','path':str(f.relative_to(P)),'source_tool':'existing-approved-asset','scene_id':'all','cost_usd':0,'format':'png'} for f in sorted((P/'assets/images').glob('*.png'))]
    save(P / 'artifacts/asset_manifest.json', {'version':'1.0','assets':assets,'total_cost_usd':0,'metadata':{'source_url':URL,'revision':'v2-chorus'}})
    pub = json.loads((P/'artifacts/publish.json').read_text())
    pub.update({'title':'泰语千词｜สายแนนหัวใจ 官方原唱副歌逐词学','video_path':'renders/final-v2.mp4','cover_path':'renders/cover-v2.jpg','publish_copy':'先听《สายแนนหัวใจ》官方原唱副歌，再学四个关键词，最后回听。\n\n#泰语 #泰语学习 #泰语千词 #泰语歌曲','credits':f'歌曲原唱：ก้อง ห้วยไร่；音源：{URL}；中文教学与剪辑：泰语千词。'})
    save(P/'artifacts/publish.json',pub)
    print('V2 duration',round(cursor/FPS,2),'seconds',flush=True)

async def main():
    await make_audio()
    build()

if __name__=='__main__': asyncio.run(main())
