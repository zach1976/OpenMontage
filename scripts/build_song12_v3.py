"""Song 12 V3: explain every phrase in the approved official chorus."""
from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from build_song12 import synth, duration

P = ROOT / 'projects/thai-1000-song-12-sai-naen-hua-jai'
SRC = P / 'assets/audio/official-mv-candidate.webm'
FPS = 30
URL = 'https://www.youtube.com/watch?v=NSm8ZXEuhL0'
LINE_DATA = [
    ('ต่อจากนี้ สิคอยดูแล เจ้าให้ดีๆ', '从今以后，我会好好照顾你', 0.0,
     [('ต่อจากนี้','从今以后',0.0),('สิคอย','会一直',1.92),('ดูแล','照顾',2.44),('เจ้า','你',2.839),('ให้ดีๆ','好好地',3.08)]),
    ('บ่ให้ผู้ใด๋เข้ามากล้ำกลาย ในชีวิตเจ้า', '不让任何人打扰你的生活', 3.72,
     [('บ่ให้','不让',3.72),('ผู้ใด๋','任何人',4.159),('เข้ามา','进来',4.60),('กล้ำกลาย','打扰',5.04),('ในชีวิตเจ้า','在你的生活中',5.72)]),
    ('ทั้งที่ใจบ่เชื่อว่าความฮักนั้นมีจริงอยู่บ่', '我本来不相信爱情真的存在', 8.04,
     [('ทั้งที่ใจ','虽然心里',8.04),('บ่เชื่อว่า','不相信',8.64),('ความฮัก','爱情',9.56),('นั้นมีจริง','真的存在',10.72),('อยู่บ่','是否存在',11.96)]),
    ('แต่ก็งง ชีวิตเจ้าของ เป็นหยังต้องมาดูแล', '却不懂自己为何想照顾你', 14.28,
     [('แต่ก็งง','却仍疑惑',14.28),('ชีวิตเจ้าของ','自己的人生',16.32),('เป็นหยัง','为什么',17.20),('ต้องมา','偏要来',17.839),('ดูแล','照顾',18.32)]),
    ('คนๆ หนึ่งที่เฮาบ่เคยฮู้จักแต่ฮักไปเบิดทั้งใจ', '从未认识的人，我却已倾心爱上', 19.159,
     [('คนๆ หนึ่ง','某个人',19.159),('ที่เฮา','我们所',19.879),('บ่เคย','从未',20.28),('ฮู้จัก','认识',20.80),('แต่ฮัก','却爱上',21.199),('ไปเบิดทั้งใจ','倾尽真心',21.64)]),
    ('หรือย้อนว่าเวรว่ากรรมอันใด เฮ็ดให้เฮาพ้อกัน', '究竟是什么因缘，让我们相遇', 23.0,
     [('หรือย้อนว่า','或许因为',23.0),('เวรว่ากรรม','因缘',23.60),('อันใด','什么',24.559),('เฮ็ดให้','使得',25.479),('เฮา','我们',26.279),('พ้อกัน','相遇',26.559)]),
]

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')

def clip_audio(start, end, out):
    if out.exists() and out.stat().st_size > 1000: return
    length = end - start
    fade = min(.08, length/8)
    af = f'afade=t=in:st=0:d={fade},afade=t=out:st={max(0,length-fade)}:d={fade},loudnorm=I=-16:TP=-1.5:LRA=11'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(67.6+start),'-t',str(length),'-i',str(SRC),'-vn','-af',af,'-ar','48000','-c:a','pcm_s16le',str(out)],check=True)

async def make_audio():
    aud=P/'assets/audio';pub=P/'composition/public/audio';pub.mkdir(parents=True,exist_ok=True)
    clip_audio(0,29.42,aud/'chorus_official_v3.wav')
    queue=[];names=['chorus_official_v3.wav','bridge_v3_zh.mp3','replay_bridge_v3_zh.mp3','outro_zh.mp3']
    queue.append((aud/'bridge_v3_zh.mp3','接下来，像前几首一样，把副歌一句一句拆开，逐词听懂。','zh'))
    queue.append((aud/'replay_bridge_v3_zh.mp3','六句副歌拆完了，再听一遍，看看能听懂多少。','zh'))
    for li,(_lyric,_meaning,at,pairs) in enumerate(LINE_DATA,1):
        line_end=LINE_DATA[li][2] if li<len(LINE_DATA) else 29.42
        for wi,(th,zh,word_at) in enumerate(pairs,1):
            nxt=pairs[wi][2] if wi<len(pairs) else line_end
            end=min(line_end,nxt+.12)
            start=max(at,word_at-.08)
            key=f'l{li}_w{wi}_v3'
            clip_audio(start,end,aud/f'{key}_source.wav')
            queue += [(aud/f'{key}_th.mp3',th+'。','th'),(aud/f'{key}_zh.mp3',f'{th}，{zh}。','zh')]
            names += [f'{key}_source.wav',f'{key}_th.mp3',f'{key}_zh.mp3']
    if os.environ.get("SONG12_V3_LANG"):
        queue=[row for row in queue if row[2]==os.environ["SONG12_V3_LANG"]]
    sem=asyncio.Semaphore(2)
    async def one(row):
        async with sem: await synth(*row)
    await asyncio.gather(*(one(row) for row in queue))
    if os.environ.get("SONG12_V3_LANG"):
        return
    for name in names: shutil.copy2(aud/name,pub/name)

def build():
    aud=P/'assets/audio'
    lines=[]
    for lyric,meaning,at,pairs in LINE_DATA:
        lines.append({'th':lyric,'zh':meaning,'at':at,'pairs':[{'th':th,'zh':zh,'at':round(t-at,3)} for th,zh,t in pairs]})
    blocks=[];cursor=0
    def clip(name):return {'file':name,'dur':duration(aud/name)}
    def add(b):
        nonlocal cursor
        b['startFrame']=cursor;b['frames']=max(1,round(b['dur']*FPS));cursor+=b['frames'];blocks.append(b)
    song=clip('chorus_official_v3.wav')
    add({'id':'song_open','kind':'song_open','audio':song,'dur':song['dur']})
    bridge=clip('bridge_v3_zh.mp3');add({'id':'bridge','kind':'bridge','nar':bridge,'dur':bridge['dur']+.16})
    idx=0
    for li,(lyric,meaning,_at,pairs) in enumerate(LINE_DATA,1):
        for wi,(th,zh,_start) in enumerate(pairs,1):
            idx+=1;key=f'l{li}_w{wi}_v3'
            src,thai,chinese=clip(f'{key}_source.wav'),clip(f'{key}_th.mp3'),clip(f'{key}_zh.mp3')
            thai_at=src['dur']+.08;zh_at=thai_at+thai['dur']+.08
            add({'id':f'l{li}_w{wi}','kind':'word','index':idx-1,'line':li,'word':wi,'lineWordTotal':len(pairs),'th':th,'zh':zh,'lyric':lyric,'lineMeaning':meaning,'source':src,'thaiAudio':thai,'zhAudio':chinese,'thaiAt':thai_at,'zhAt':zh_at,'dur':zh_at+chinese['dur']+.10})
    replay=clip('replay_bridge_v3_zh.mp3');add({'id':'replay_bridge','kind':'replay_bridge','nar':replay,'dur':replay['dur']+.12})
    add({'id':'song_replay','kind':'song_replay','audio':song,'dur':song['dur']})
    outro=clip('outro_zh.mp3');add({'id':'outro','kind':'outro','nar':outro,'dur':outro['dur']+.3})
    labels={'song_open':'先听官方副歌','bridge':'逐词拆解','replay_bridge':'回听过渡','song_replay':'再听官方副歌','outro':'泰语千词推广'}
    review=[{'id':b['id'],'label':b.get('th',labels.get(b['id'],'')),'start':b['startFrame']/FPS,'end':(b['startFrame']+b['frames'])/FPS,'title':b['id'],'text':b.get('th',labels.get(b['id'],'')),'credit':URL} for b in blocks]
    props={'fps':FPS,'totalFrames':cursor,'totalSeconds':cursor/FPS,'title':'สายแนนหัวใจ','artist':'ก้อง ห้วยไร่','lines':lines,'blocks':blocks,'review_timeline':review}
    save(P/'composition/props.json',props);save(P/'artifacts/props_v3.json',props)
    sections=[]
    for b,r in zip(blocks,review):
        sections.append({'id':b['id'],'label':r['label'],'text':b.get('th',r['label'])+('，'+b['zh'] if b['kind']=='word' else ''),'start_seconds':r['start'],'end_seconds':r['end'],'speaker_directions':'原唱片段、泰语跟读、中文词义依次出现。' if b['kind']=='word' else '按画面时间线播放原唱或中文过渡。','enhancement_cues':[{'type':'overlay','description':r['label'],'timestamp_seconds':r['start']}]})
    script={'version':'1.0','title':'สายแนนหัวใจ｜官方副歌六句逐词学','total_duration_seconds':cursor/FPS,'sections':sections,'voice_performance':{'performance_intent':'原唱片段、泰语跟读、中文词义三步清楚交替。','pacing_profile':'custom','energy_curve':'原唱开场，逐词拆解，回听收束。','pause_policy':'三步之间留约0.08秒。','sample_section_id':'l1_w1','provider_notes':{'edge-tts':'沿用已批准的泰语和中文女声。'}},'metadata':{'revision':'v3-word-by-word','source_url':URL,'phrase_count':idx}}
    save(P/'artifacts/script.json',script)
    scene={'version':'1.0','style_playbook':'isan-thread-at-golden-hour','scenes':[{'id':b['id'],'type':'animation','description':r['label'],'start_seconds':r['start'],'end_seconds':r['end'],'script_section_id':b['id'],'required_assets':[{'type':'audio','description':'官方原唱片段或配音','source':'source'},{'type':'image','description':'伊森田野或织物','source':'provided'}]} for b,r in zip(blocks,review)]}
    save(P/'artifacts/scene_plan.json',scene)
    assets=[]
    for b in blocks:
        for k in ('audio','nar','source','thaiAudio','zhAudio'):
            if k in b:
                f=aud/b[k]['file']
                if not any(a['id']==f.stem for a in assets):assets.append({'id':f.stem,'type':'audio','path':str(f.relative_to(P)),'source_tool':'edge-tts' if f.suffix=='.mp3' and f.name!='outro_zh.mp3' else 'ffmpeg/source-youtube','scene_id':'all','cost_usd':0,'format':f.suffix[1:]})
    assets += [{'id':f.stem,'type':'image','path':str(f.relative_to(P)),'source_tool':'existing-approved-asset','scene_id':'all','cost_usd':0,'format':'png'} for f in sorted((P/'assets/images').glob('*.png'))]
    save(P/'artifacts/asset_manifest.json',{'version':'1.0','assets':assets,'total_cost_usd':0,'metadata':{'revision':'v3-word-by-word','source_url':URL}})
    proposal=json.loads((P/'artifacts/proposal_packet.json').read_text())
    for option in proposal.get('concept_options',[]):
        if option.get('id')==proposal['selected_concept']['concept_id']:option['target_duration_seconds']=round(cursor/FPS)
    proposal['selected_concept']['modifications']=['保留官方副歌','六句全部逐词拆解','原唱时逐词高亮']
    proposal['production_plan']['stages'][0]['approach']='把六句副歌拆成32个短语词卡。'
    proposal['production_plan']['stages'][-1]['approach']='输出 V3，检查逐词卡、跟唱高亮和音轨。'
    proposal['metadata']['revision']='v3-word-by-word'
    proposal['approval']={'status':'approved','user_notes':'用户指出 V2 应逐词解释，并要求参照前几首视频；此前已授权直接出视频。'}
    save(P/'artifacts/proposal_packet.json',proposal)
    publish=json.loads((P/'artifacts/publish.json').read_text())
    publish.update({'title':'泰语千词｜สายแนนหัวใจ 官方副歌六句逐词学','video_path':'renders/final-v3.mp4','cover_path':'renders/cover-v3.jpg','publish_copy':'先听《สายแนนหัวใจ》官方原唱副歌，再把六句歌词逐词听懂，最后完整回听。\n\n#泰语 #泰语学习 #泰语千词 #泰语歌曲'})
    save(P/'artifacts/publish.json',publish)
    print('V3',idx,'phrase cards',round(cursor/FPS,2),'seconds',flush=True)

async def main():
    await make_audio();build()

if __name__=='__main__':asyncio.run(main())
