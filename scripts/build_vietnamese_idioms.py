"""Produce two Vietnamese counterparts to approved Thai idiom lessons."""
from __future__ import annotations

import asyncio, json, shutil, subprocess, sys
from datetime import date
from pathlib import Path
import edge_tts

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from lib.checkpoint import init_project
FPS=30
THAI=ROOT/'projects/thai-1000-idiom-02-saranae'
VIET=ROOT/'projects/vietnamese-couple-02-disagreement'
IMAGES=[Path('/Users/zhenyusong/.codex/generated_images/01a10c9a-da8d-78f1-b665-d37503ab8b03/exec-1a17168f-891a-478d-8bcf-f1d0b3e108c3.png'),Path('/Users/zhenyusong/.codex/generated_images/01a10c9a-da8d-78f1-b665-d37503ab8b03/exec-fb8555da-8bb5-4d32-8840-916f7f8b43c6.png')]
LESSONS=[
 dict(id='viet-1000-idiom-01-nhieu-chuyen',comp='NhieuChuyenLesson',number='01',slug='viet_funny_nhieu_chuyen_01',title='nhiều chuyện｜爱管闲事',word='nhiều chuyện',meaning='爱管闲事',tone='带责备的口语',color='#ae5340',photo='hanoi-cafe.png',tagline='也可能指爱说闲话，听语境',hook='说人爱管闲事，越南语可以这样说。先听发音。',cards=[('word','爱管闲事','nhiều chuyện','先听核心词，爱管闲事。','也能说人爱说闲话。','核心词','带责备，也指爱说闲话'),('stop','别多管闲事','Đừng có nhiều chuyện','直接说，别多管闲事。','这句带责备，熟人之间也要留意语气。','直接说法','语气较冲'),('soft','这是我的私事','Đây là chuyện riêng của tôi','想说得平和一点。','就是这是我的私事。','平和表达','表达边界更稳妥')],reveal='前一句带责备。需要表达边界，就说这是我的私事。',rule='责备别人，还是说明边界？换句话，语气就变了。',source='https://vdict.com/nhi%E1%BB%81u%20chuy%E1%BB%87n%2C3%2C0%2C0.html',description='学越南语口语 nhiều chuyện：爱管闲事、别多管闲事，以及更平和的表达边界方式。'),
 dict(id='viet-1000-idiom-02-kiem-chuyen',comp='KiemChuyenLesson',number='02',slug='viet_funny_kiem_chuyen_02',title='kiếm chuyện｜找茬',word='kiếm chuyện',meaning='找茬',tone='冲突语境，慎用',color='#c47b42',photo='saigon-cafe.png',tagline='听懂冲突，也会平和回应',hook='有人故意找茬，越南语里会用这个词。先听发音。',cards=[('word','找茬','kiếm chuyện','先听核心词，找茬。','就是故意制造麻烦。','核心词','发生冲突时常听到'),('stop','别找茬','Đừng kiếm chuyện','有人故意挑衅，会听到这句。','意思是别找茬，语气很直接。','直接说法','语气较冲'),('soft','别打扰我','Đừng làm phiền tôi','不想起冲突，就说。','意思是别打扰我，语气更平和。','平和表达','日常沟通更稳妥')],reveal='前一句是别找茬。只想让对方停下，可以说别打扰我。',rule='遇到挑衅，先分清“找茬”和“打扰”。',source='https://vi.wiktionary.org/wiki/ki%E1%BA%BFm_chuy%E1%BB%87n',description='学越南语口语 kiếm chuyện：找茬、别找茬，以及更平和的“别打扰我”。')]

def save(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def dur(path): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(path)],text=True))
def setup(c,i):
 p=ROOT/'projects'/c['id']
 if not p.exists():init_project(c['id'],title=c['title'],pipeline_type='animated-explainer')
 for sub in ['assets/audio','assets/images','assets/music','composition/public/audio','composition/public/images','composition/public/app']: (p/sub).mkdir(parents=True,exist_ok=True)
 shutil.copy2(IMAGES[i],p/'assets/images'/c['photo']);shutil.copy2(IMAGES[i],p/'composition/public/images'/c['photo'])
 shutil.copy2(VIET/'assets/images/app_icon.png',p/'composition/public/app/app_icon.png')
 shutil.copy2(THAI/'assets/music/background.mp3',p/'assets/music/background.mp3');shutil.copy2(THAI/'assets/music/background.mp3',p/'composition/public/audio/background.mp3')
 for name in ['Composition.tsx','index.tsx']: shutil.copy2(ROOT/'scripts/vietnamese_idiom_series'/name,p/'composition'/name)
 (p/'composition/Root.tsx').write_text(f'import React from "react";\nimport {{Composition}} from "remotion";\nimport {{Scene,calculateMetadata,SceneProps}} from "./Composition";\nexport const Root:React.FC=()=><Composition id="{c["comp"]}" component={{Scene}} durationInFrames={{1500}} fps={{30}} width={{1080}} height={{1920}} defaultProps={{{{}} as SceneProps}} calculateMetadata={{calculateMetadata}}/>;\n')
 (p/'art-direction.md').write_text('# Vietnamese street editorial\n\nFull-bleed Hanoi/Saigon coffee street photography, deep petrol lower panels, terracotta accents, gold type. The first frame is a cover. Distinct from the Thai notebook layout.\n')
 return p
async def synth(path,words,lang):
 if path.exists() and path.stat().st_size>500:return
 voice,rate=('zh-CN-XiaoxiaoNeural','+15%') if lang=='zh' else ('vi-VN-HoaiMyNeural','+8%')
 raw=path.with_name(path.stem+'_raw.mp3')
 for attempt in range(12):
  try:await edge_tts.Communicate(words,voice=voice,rate=rate).save(str(raw));break
  except Exception:
   if attempt==11:raise
   await asyncio.sleep(4*(attempt+1))
 subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(raw),'-af','silenceremove=start_periods=1:start_silence=0.02:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_silence=0.08:start_threshold=-45dB,areverse','-c:a','libmp3lame','-b:a','192k',str(path)],check=True)
 raw.unlink();print('audio',path.parent.parent.parent.name,path.name,flush=True)
def reads(c):
 r=[('hook_zh_x',c['hook'],'zh'),('hook_vi_x',c['word'],'vi')]
 for cid,zh,vi,intro,explain,*_ in c['cards']:r += [(f'{cid}_intro_zh_x',intro,'zh'),(f'{cid}_vi_x',vi,'vi'),(f'{cid}_explain_zh_x',explain,'zh')]
 return r+[('reveal_zh_x',c['reveal'],'zh'),('outro_zh_x','越南语千词，在越南生活，够用了。','zh')]
def artifacts(p,c):
 A=p/'artifacts';cursor=0
 def clip(n):return {'file':n+'.mp3','dur':dur(p/'assets/audio'/(n+'.mp3'))}
 def place(x):
  nonlocal cursor
  x['startFrame']=cursor;x['frames']=round(x['dur']*FPS);cursor+=x['frames'];return x
 hook={'nar':clip('hook_zh_x'),'viet':clip('hook_vi_x')};hook['vietAt']=hook['nar']['dur']+.12;hook['dur']=hook['vietAt']+hook['viet']['dur']+.3;place(hook)
 cards=[]
 for cid,zh,vi,intro,explain,tag,hint in c['cards']:
  a,b,e=clip(cid+'_intro_zh_x'),clip(cid+'_vi_x'),clip(cid+'_explain_zh_x');v=a['dur']+.13;r=v+b['dur']+.10;x=r+b['dur']+.14
  cards.append(place(dict(id=cid,zh=zh,viet=vi,tag=tag,hint=hint,intro=a,pronounce=b,explain=e,vietAt=v,repeatAt=r,explainAt=x,dur=x+e['dur']+.2)))
 reveal=place({'nar':clip('reveal_zh_x'),'rule':c['rule'],'dur':dur(p/'assets/audio/reveal_zh_x.mp3')+.35})
 outro=place({'nar':clip('outro_zh_x'),'dur':dur(p/'assets/audio/outro_zh_x.mp3')+.35})
 timeline=[('hook',c['title'],hook)]+[(x['id'],x['zh']+' · '+x['viet'],x) for x in cards]+[('reveal','语气小结',reveal),('outro','越南语千词 App',outro)]
 texts={'hook':c['hook'],'reveal':c['reveal'],'outro':'越南语千词，在越南生活，够用了。'}
 for cid,zh,vi,intro,explain,*_ in c['cards']:texts[cid]=intro+' 越南语读两遍。'+explain
 props={'fps':FPS,'totalFrames':cursor,'totalSeconds':cursor/FPS,'lesson':{k:c[k] for k in ['title','word','meaning','tone','color','tagline','number','photo']},'hook':hook,'cards':cards,'reveal':reveal,'outro':outro,'bgm':{'file':'background.mp3','volume':.045},'review_timeline':[{'id':cid,'label':lab,'start':item['startFrame']/FPS,'end':(item['startFrame']+item['frames'])/FPS,'title':lab,'text':texts[cid],'credit':c['source']} for cid,lab,item in timeline]}
 save(A/'props.json',props);save(p/'composition/props.json',props)
 research=json.loads((THAI/'artifacts/research_brief.json').read_text());research.update(topic=c['title'],research_date=str(date.today()),research_summary=c['description'],sources=[{'url':c['source'],'title':'Vietnamese dictionary','used_for':'词义与语气','reliability':'dictionary'}]);research['data_points']=[{'claim':c['word']+' 的词义和语气','source_url':c['source'],'source_name':'Vietnamese dictionary','credibility':'dictionary','usable_as':'script_anchor'}];save(A/'research_brief.json',research)
 proposal=json.loads((THAI/'artifacts/proposal_packet.json').read_text());proposal['concept_options'][0].update(title=c['title'],hook=c['hook'],visual_approach='越南街边咖啡馆纪实照片与深青信息区',target_duration_seconds=round(cursor/FPS),core_message=c['description']);proposal['selected_concept']={'concept_id':proposal['concept_options'][0]['id'],'rationale':'越南语本地表达及独立视觉，沿用已审核的双语教学节奏。'};proposal['production_plan']['render_runtime']='remotion';proposal['production_plan']['composition_mode']='atelier';proposal['approval']={'status':'approved','user_notes':'用户明确要求直接制作越南语对应视频，并延续此前系列。'};save(A/'proposal_packet.json',proposal)
 script=json.loads((THAI/'artifacts/script.json').read_text());script.update(title=c['title'],sections=[{'id':cid,'label':lab,'text':texts[cid],'start_seconds':item['startFrame']/FPS,'end_seconds':(item['startFrame']+item['frames'])/FPS,'speaker_directions':'每句先中文提示、越南语女声读两遍，再中文解释。'} for cid,lab,item in timeline],total_duration_seconds=cursor/FPS);script['metadata']={'language':'zh+vi','tts':{'engine':'edge','voices':{'zh':'zh-CN-XiaoxiaoNeural','vi':'vi-VN-HoaiMyNeural'}},'sources':[c['source']]};save(A/'script.json',script)
 save(A/'scene_plan.json',{'version':'1.0','style_playbook':'custom-vietnamese-street-editorial','scenes':[{'id':cid,'type':'animation','description':lab,'start_seconds':item['startFrame']/FPS,'end_seconds':(item['startFrame']+item['frames'])/FPS,'script_section_id':cid,'required_assets':[{'type':'audio','description':'中越双语配音','source':'generate'},{'type':'image','description':'越南街边咖啡情境图','source':'generated'}]} for cid,lab,item in timeline]})
 assets=[{'id':f.stem,'type':'narration','path':str(f.relative_to(p)),'source_tool':'edge-tts','scene_id':f.stem.split('_')[0],'cost_usd':0,'format':'mp3'} for f in sorted((p/'assets/audio').glob('*_x.mp3'))];assets += [{'id':'photo','type':'image','path':'assets/images/'+c['photo'],'source_tool':'image_gen','scene_id':'all','cost_usd':0,'format':'png'},{'id':'background','type':'music','path':'assets/music/background.mp3','source_tool':'existing-local-series','scene_id':'all','cost_usd':0,'format':'mp3'},{'id':'app-icon','type':'image','path':'composition/public/app/app_icon.png','source_tool':'existing-brand-asset','scene_id':'outro','cost_usd':0,'format':'png'}];save(A/'asset_manifest.json',{'version':'1.0','assets':assets,'total_cost_usd':0,'metadata':{'visuals':'generated Vietnam-specific cafe photos','tts':'approved Chinese and Vietnamese voice family'}})
 save(A/'decision_log.json',{'version':'1.0','project_id':c['id'],'decisions':[{'decision_id':c['number']+'-runtime','stage':'proposal','category':'render_runtime_selection','subject':'Composition runtime','options_considered':[{'option_id':'remotion','label':'Remotion','score':1,'reason':'已审系列节奏及精确双语时序'},{'option_id':'hyperframes','label':'HyperFrames','score':.6,'reason':'适合网页动效，但需重搭音频时间轴'},{'option_id':'ffmpeg','label':'FFmpeg','score':.3,'reason':'逐词动态较弱'}],'selected':'remotion','reason':'沿用已批准的系列制作运行时，重做越南语视觉。','user_visible':True,'user_approved':True},{'decision_id':c['number']+'-voice','stage':'assets','category':'voice_selection','subject':'Chinese and Vietnamese lesson voices','options_considered':[{'option_id':'edge_existing','label':'Xiaoxiao 中文 + HoaiMy 越南语','score':1,'reason':'越南语系列既有音色'}],'selected':'edge_existing','reason':'沿用已审系列音色。','user_visible':True,'user_approved':True}]})
 save(A/'publish.json',{'series_id':2,'sub_series':'趣味越南语','slug':c['slug'],'title':'越南语千词｜'+c['title'],'video_path':'renders/final-v1.mp4','cover_path':'renders/cover-v1.jpg','publish_copy':c['description']+'\n\n#越南语 #越南语学习 #越南语千词 #实用越南语','wechat_copy':c['title'],'credits':'越南语释义参考在线越南语词典；中越配音与剪辑：越南语千词。','note':'待审片；未入库。'})
 print(c['id'],round(cursor/FPS,2),'seconds',flush=True)
async def main():
 pair=[(setup(c,i),c) for i,c in enumerate(LESSONS)]
 for p,c in pair:
  for n,words,lang in reads(c):await synth(p/'assets/audio'/(n+'.mp3'),words,lang)
  for f in (p/'assets/audio').glob('*_x.mp3'):shutil.copy2(f,p/'composition/public/audio'/f.name)
  artifacts(p,c)
if __name__=='__main__':asyncio.run(main())
