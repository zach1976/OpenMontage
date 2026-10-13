"""Build a four-line teaching cut of UNHEARD MUSIC's ไม่มีใครรู้ตัวเรา."""
from __future__ import annotations

import asyncio, json, shutil, subprocess, sys
from datetime import date
from pathlib import Path
import edge_tts

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from lib.checkpoint import init_project
PID='thai-1000-song-11-mai-mi-khrai-ru-tua-rao'
P=ROOT/'projects'/PID
SRC=P/'assets/audio/unheard_source.mp3'
FPS=30
NIGHT=Path('/Users/zhenyusong/.codex/generated_images/01a10c9a-da8d-78f1-b665-d37503ab8b03/exec-ffefebb8-6865-4250-80a3-328f40e35282.png')
DAWN=Path('/Users/zhenyusong/.codex/generated_images/01a10c9a-da8d-78f1-b665-d37503ab8b03/exec-3c8df45f-2638-43db-8ee1-b123740cd047.png')
LINES=[
 {'th':'ไม่มีใครรู้ตัวเราผ่านอะไรมา','zh':'没人知道我经历了什么','at':.6,'pairs':[('ไม่มีใคร','没有人',0),('รู้','知道',1.35),('ตัวเรา','我自己',2.2),('ผ่านอะไรมา','经历了什么',3.25)]},
 {'th':'รอยยิ้มที่เห็นมันแค่หน้ากากธรรมดา','zh':'你看到的笑容，不过是一张面具','at':7.7,'pairs':[('รอยยิ้ม','笑容',0),('ที่เห็น','你看到的',1.25),('มันแค่','不过是',2.25),('หน้ากาก','面具',3.15),('ธรรมดา','普通的',4.7)]},
 {'th':'กลางคืนที่อ้างว้าง มันดังเกินคำพูดจา','zh':'孤独的夜，心里的声音难以言说','at':14.7,'pairs':[('กลางคืน','夜晚',0),('อ้างว้าง','孤独',1.65),('ดังเกิน','响过',3.6),('คำพูดจา','言语',5.35)]},
 {'th':'มีแค่เงาของเราที่ยังยืนอยู่ข้างใน','zh':'只有自己的影子，还站在心里','at':21.55,'pairs':[('มีแค่','只有',0),('เงาของเรา','自己的影子',1.1),('ยังยืนอยู่','仍站着',2.75),('ข้างใน','心里',4.35)]},
]
WORDS=[
 ('ไม่มีใคร','没有人','就是没有人。',32.45,34.55),
 ('ผ่านอะไรมา','经历了什么','就是经历了什么。',34.55,37.65),
 ('รอยยิ้ม','笑容','是笑容。',39.52,41.55),
 ('หน้ากาก','面具','是面具。',42.05,44.65),
 ('อ้างว้าง','孤独','是孤独、空落落。',47.0,49.25),
 ('คำพูดจา','言语','就是说出来的话。',50.35,53.5),
 ('เงาของเรา','自己的影子','是自己的影子。',53.42,55.62),
 ('ข้างใน','心里','这里指心里。',56.0,59.35),
]

def save(path,obj):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def duration(path):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(path)],text=True))
def cut(start,end,path):
 if path.exists() and path.stat().st_size>1000:return
 subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(start),'-to',str(end),'-i',str(SRC),'-vn','-c:a','libmp3lame','-b:a','192k',str(path)],check=True)
def setup():
 init_project(PID,title='ไม่มีใครรู้ตัวเรา｜泰语歌曲逐词教学',pipeline_type='animated-explainer')
 for sub in ['assets/images','assets/audio','composition','composition/public/images','composition/public/audio','composition/public/fonts','composition/public/app']:(P/sub).mkdir(parents=True,exist_ok=True)
 for src,name in [(NIGHT,'night.png'),(DAWN,'dawn.png')]:shutil.copy2(src,P/'assets/images'/name);shutil.copy2(src,P/'composition/public/images'/name)
 shutil.copy2(ROOT/'projects/thai-1000-idiom-02-saranae/composition/public/fonts/Sarabun-Bold.ttf',P/'composition/public/fonts/Sarabun-Bold.ttf')
 shutil.copy2(ROOT/'projects/thai-1000-idiom-02-saranae/composition/public/app/app_icon.png',P/'composition/public/app/app_icon.png')
 for name in ['Composition.tsx','Root.tsx','index.tsx']:shutil.copy2(ROOT/'scripts/song11'/name,P/'composition'/name)
 (P/'art-direction.md').write_text('# Night to dawn\n\nThis song is about hidden struggle and persistence. Start in a rainy Bangkok night, move toward a warm dawn. Full-bleed documentary photographs, dark navy field, amber highlighted Thai-Chinese pairs. Signature device: paired Thai-Chinese lyric chips pulse at the sung phrase. No desert/couple visual treatment from prior songs.\n\nTaste: design_read=quiet resilience; visual_variance=5; motion_intensity=3; information_density=5.\n')
 assert SRC.exists(),SRC
 cut(31.9,59.45,P/'assets/audio/song_open.mp3')
 for i,(_,_,_,start,end) in enumerate(WORDS,1):cut(start,end,P/'assets/audio'/f'w{i}_source.mp3')

async def synth(path,text,lang):
 if path.exists() and path.stat().st_size>500:return
 voice,rate=('zh-CN-XiaoxiaoNeural','+12%') if lang=='zh' else ('th-TH-PremwadeeNeural','+6%')
 raw=path.with_name(path.stem+'_raw.mp3')
 for attempt in range(8):
  try:
   await edge_tts.Communicate(text,voice=voice,rate=rate).save(str(raw))
   if raw.stat().st_size<1000:raise RuntimeError('empty audio')
   break
  except Exception as e:
   if attempt==7:raise RuntimeError(f'TTS failed: {path.name}: {e}')
   await asyncio.sleep(min(3*(attempt+1),12))
 subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(raw),'-af','silenceremove=start_periods=1:start_silence=0.02:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_silence=0.08:start_threshold=-45dB,areverse','-c:a','libmp3lame','-b:a','192k',str(path)],check=True)
 raw.unlink();print('tts',path.name,flush=True)

async def audio():
 queue=[(P/'assets/audio/bridge_zh_x.mp3','这首歌唱的是：别人看不见你的难处，你还是努力往前走。','zh'),(P/'assets/audio/outro_zh_x.mp3','泰语千词，在泰国生活，够用了。','zh')]
 for i,(th,zh,explain,*_) in enumerate(WORDS,1):queue.extend([(P/'assets/audio'/f'w{i}_th_x.mp3',th+'。','th'),(P/'assets/audio'/f'w{i}_zh_x.mp3',explain,'zh')])
 sem=asyncio.Semaphore(2)
 async def one(row):
  async with sem:await synth(*row)
 await asyncio.gather(*(one(x) for x in queue))
 for f in (P/'assets/audio').glob('*.mp3'):shutil.copy2(f,P/'composition/public/audio'/f.name)

def build():
 A=P/'artifacts';cursor=0;blocks=[]
 def clip(name):return {'file':name,'dur':duration(P/'assets/audio'/name)}
 def add(b):
  nonlocal cursor
  b['startFrame']=cursor;b['frames']=max(1,round(b['dur']*FPS));cursor+=b['frames'];blocks.append(b)
 song=clip('song_open.mp3');add({'id':'song_open','kind':'song_open','audio':song,'dur':song['dur']})
 bridge=clip('bridge_zh_x.mp3');add({'id':'bridge','kind':'bridge','nar':bridge,'dur':bridge['dur']+.25})
 for i,(th,zh,*_) in enumerate(WORDS,1):
  src,thc,zhc=clip(f'w{i}_source.mp3'),clip(f'w{i}_th_x.mp3'),clip(f'w{i}_zh_x.mp3')
  thai_at=src['dur']+.12;zh_at=thai_at+thc['dur']+.13
  add({'id':f'w{i}','kind':'word','index':i-1,'th':th,'zh':zh,'source':src,'thaiAudio':thc,'zhAudio':zhc,'thaiAt':thai_at,'zhAt':zh_at,'dur':zh_at+zhc['dur']+.16})
 add({'id':'song_replay','kind':'song_replay','audio':song,'dur':song['dur']})
 outro=clip('outro_zh_x.mp3');add({'id':'outro','kind':'outro','nar':outro,'dur':outro['dur']+.45})
 lines=[{'th':l['th'],'zh':l['zh'],'at':l['at'],'pairs':[{'th':th,'zh':zh,'at':at} for th,zh,at in l['pairs']]} for l in LINES]
 review=[]
 for b in blocks:
  text=('先听原唱四句，泰中对应高亮。' if b['kind']=='song_open' else '再听一遍原唱。' if b['kind']=='song_replay' else '这首歌唱的是：别人看不见你的难处，你还是努力往前走。' if b['kind']=='bridge' else '泰语千词，在泰国生活，够用了。' if b['kind']=='outro' else f"原唱→泰语跟读→中文解释：{b['th']}，{b['zh']}。")
  review.append({'id':b['id'],'label':b.get('th','原唱四句' if b['kind']=='song_open' else '回听' if b['kind']=='song_replay' else '歌曲小介绍' if b['kind']=='bridge' else 'App 片尾'),'start':b['startFrame']/FPS,'end':(b['startFrame']+b['frames'])/FPS,'title':b['id'],'text':text,'credit':'https://www.youtube.com/watch?v=Bh0y2Y0LPMs'})
 props={'fps':FPS,'totalFrames':cursor,'totalSeconds':cursor/FPS,'title':'ไม่มีใครรู้ตัวเรา','artist':'UNHEARD MUSIC','lines':lines,'blocks':blocks,'review_timeline':review};save(P/'composition/props.json',props);save(A/'props.json',props)
 research=json.loads((ROOT/'projects/thai-1000-idiom-02-saranae/artifacts/research_brief.json').read_text());research.update(topic='ไม่มีใครรู้ตัวเรา｜UNHEARD MUSIC',research_date=str(date.today()),research_summary='核对 UNHEARD MUSIC 原版，选原唱前四句教学；音源开头有口播，演唱从约 32.5 秒开始。',sources=[{'url':'https://www.youtube.com/watch?v=Bh0y2Y0LPMs','title':'UNHEARD MUSIC official audio','used_for':'原唱音频与艺术家、时长','reliability':'primary'},{'url':'https://www.joox.com/mo/single/Od0uSb7q0jB%2B_TM7fj5A0Q%3D%3D','title':'JOOX lyrics','used_for':'前四句歌词核对','reliability':'licensed lyrics source'}]);save(A/'research_brief.json',research)
 proposal=json.loads((ROOT/'projects/thai-1000-idiom-02-saranae/artifacts/proposal_packet.json').read_text());proposal['concept_options'][0].update(title='ไม่มีใครรู้ตัวเรา｜泰语歌曲逐词学',hook='先听原唱，再拆前四句',visual_approach='曼谷雨夜走向清晨，泰中对照词组随原唱高亮。',target_duration_seconds=round(cursor/FPS),core_message='歌里听原声，词组学发音和意思。');proposal['selected_concept']={'concept_id':proposal['concept_options'][0]['id'],'rationale':'延续已审核歌曲课的原唱→简短介绍→逐词→回听结构。'};proposal['production_plan'].update(render_runtime='remotion',composition_mode='atelier',taste_profile={'design_read':'雨夜里独自坚持，最后天亮','visual_variance':5,'motion_intensity':3,'information_density':5,'palette_discipline':'深海蓝与暖金','reference_strategy':'夜景与清晨两张原创照片','anti_patterns':['沙丘与情侣画面重复']});proposal['approval']={'status':'approved','user_notes':'用户要求后续做这首歌的教学视频；沿用已审核歌曲教学结构。'};save(A/'proposal_packet.json',proposal)
 script=json.loads((ROOT/'projects/thai-1000-idiom-02-saranae/artifacts/script.json').read_text());script.update(title='ไม่มีใครรู้ตัวเรา｜前四句逐词学',sections=[{'id':b['id'],'label':r['label'],'text':r['text'],'start_seconds':b['startFrame']/FPS,'end_seconds':(b['startFrame']+b['frames'])/FPS,'speaker_directions':'原唱→泰语女声→中文解释；原唱与中文对应高亮。'} for b,r in zip(blocks,review)],total_duration_seconds=cursor/FPS);script['metadata']={'language':'zh+th','music_source':'UNHEARD MUSIC official YouTube audio','source_url':'https://www.youtube.com/watch?v=Bh0y2Y0LPMs','tts':{'engine':'edge','voices':{'zh':'zh-CN-XiaoxiaoNeural','th':'th-TH-PremwadeeNeural'}}};save(A/'script.json',script)
 save(A/'scene_plan.json',{'version':'1.0','style_playbook':'night-to-dawn-song','scenes':[{'id':b['id'],'type':'animation','description':r['text'],'start_seconds':b['startFrame']/FPS,'end_seconds':(b['startFrame']+b['frames'])/FPS,'script_section_id':b['id'],'required_assets':[{'type':'audio','description':'原唱／配音','source':'local'},{'type':'image','description':'曼谷夜与晨','source':'generated'}]} for b,r in zip(blocks,review)]})
 assets=[{'id':f.stem,'type':'audio','path':str(f.relative_to(P)),'source_tool':'edge-tts' if '_x' in f.stem else 'ffmpeg/source-youtube','scene_id':'all','cost_usd':0,'format':'mp3'} for f in sorted((P/'assets/audio').glob('*.mp3'))];assets += [{'id':n,'type':'image','path':'assets/images/'+n,'source_tool':'image_gen','scene_id':'all','cost_usd':0,'format':'png'} for n in ['night.png','dawn.png']];save(A/'asset_manifest.json',{'version':'1.0','assets':assets,'total_cost_usd':0,'metadata':{'source_url':'https://www.youtube.com/watch?v=Bh0y2Y0LPMs','intro_trim':'31.9–59.45 sec original singing','visuals':'night to dawn original imagegen'}})
 save(A/'decision_log.json',{'version':'1.0','project_id':PID,'decisions':[{'decision_id':'s11-runtime','stage':'proposal','category':'render_runtime_selection','subject':'Video composition runtime','options_considered':[{'option_id':'remotion','label':'Remotion','score':1,'reason':'原唱歌词与中文词组逐帧高亮'},{'option_id':'hyperframes','label':'HyperFrames','score':.7,'reason':'可做字形动效，但逐词音频同步需额外校对'},{'option_id':'ffmpeg','label':'FFmpeg','score':.3,'reason':'歌词对应高亮不足'}],'selected':'remotion','reason':'延续已审核歌曲课程路径。','user_visible':True,'user_approved':True},{'decision_id':'s11-mode','stage':'proposal','category':'composition_mode','subject':'Composition authoring mode','options_considered':[{'option_id':'atelier','label':'Atelier','score':1,'reason':'为歌曲制作雨夜到清晨的专属视觉'},{'option_id':'templated','label':'Templated','score':.4,'reason':'与其他歌曲画面重复'}],'selected':'atelier','reason':'歌曲意境适合独立画面。','user_visible':True,'user_approved':True},{'decision_id':'s11-source','stage':'assets','category':'music_source','subject':'Song source version','options_considered':[{'option_id':'unheard','label':'UNHEARD MUSIC original','score':1,'reason':'同名曲中最常见且官方音频可核对'},{'option_id':'first_party','label':'First Party Music version','score':.4,'reason':'同名但更少见'}],'selected':'unheard','reason':'用户未给链接，暂按主流官方版本制作；已向用户询问版本。','user_visible':True,'user_approved':False}]})
 save(A/'publish.json',{'series_id':1,'sub_series':'泰语神曲','slug':'thai_song_11_mai_mi_khrai_ru_tua_rao','title':'泰语千词｜ไม่มีใครรู้ตัวเรา 前四句逐词学','video_path':'renders/final-v1.mp4','cover_path':'renders/cover-v1.jpg','publish_copy':'先听《ไม่มีใครรู้ตัวเรา》原唱前四句，再逐词听原唱、泰语发音和中文解释，最后回听。\n\n#泰语 #泰语学习 #泰语千词 #泰语歌曲','wechat_copy':'《ไม่มีใครรู้ตัวเรา》前四句逐词学','credits':'歌曲原唱：UNHEARD MUSIC；音源：https://www.youtube.com/watch?v=Bh0y2Y0LPMs；歌词核对：JOOX；中文教学与剪辑：泰语千词。','note':'待审片；未入库。'})
 print(PID,round(cursor/FPS,2),'seconds',flush=True)

async def main():setup();await audio();build()
if __name__=='__main__':asyncio.run(main())
