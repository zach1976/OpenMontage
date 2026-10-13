#!/usr/bin/env python3
"""Materialize the approved Vietnamese couple plan as animation pipeline projects."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(REPO))
from lib.checkpoint import init_project,write_checkpoint

SHARED=REPO/'projects/_shared/couple-series'
PLAN=json.loads((SHARED/'vietnamese_plan.json').read_text())
ICON=REPO/'projects/vietnamese-family-kinship-vocabulary/assets/images/app_icon.png'
INTRO,CARD,OUTRO=3.5,4.4,4.5
SOURCES=[
    ('MSU Basic Vietnamese culture notes','https://openbooks.lib.msu.edu/vietnamese/chapter/u6-culture-notes/'),
    ('VietnameseLessons anh/em guide','https://vietnameselessons.com/guides/i-love-you-in-vietnamese'),
    ('VietnameseLessons xin lỗi guide','https://vietnameselessons.com/guides/sorry-in-vietnamese'),
    ('SVFF Vietnamese pronouns','https://svff.online/blog/how-to-say-you-and-i-southern-vietnamese'),
    ('VietLingo pronouns','https://vietlingo.com/blog/vietnamese-pronouns-complete-guide')]

def write(path:Path,value:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

for ep in PLAN['episodes']:
    pid=ep['project_id']
    p=init_project(pid,title=f"情侣越南语 {ep['number']:02d}｜{ep['title']}",pipeline_type='animation')
    for rel in ('assets/images','public/images','public/app','composition/public/images','composition/public/app'):
        (p/rel).mkdir(parents=True,exist_ok=True)
    for rel in ('assets/images','public/images','composition/public/images'):
        shutil.copy2(SHARED/'assets'/ep['sheet'],p/rel/ep['sheet'])
    for rel in ('assets/images/app_icon.png','public/app/app_icon.png','composition/public/app/app_icon.png'):
        shutil.copy2(ICON,p/rel)
    shutil.copy2(SHARED/'VietnameseSeriesComposition.tsx',p/'Composition.tsx')
    (p/'index.tsx').write_text("import {registerRoot} from 'remotion';\nimport {Root} from './Root';\nregisterRoot(Root);\n")
    duration=round(INTRO+len(ep['cards'])*CARD+OUTRO,1)
    frames=round(duration*30)
    (p/'Root.tsx').write_text("import React from 'react';\nimport {Composition} from 'remotion';\nimport {Scene,calculateMetadata,SceneProps} from './Composition';\n"+
        f"export const Root:React.FC=()=> <Composition id=\"VietnameseCoupleEpisode\" component={{Scene}} durationInFrames={{{frames}}} fps={{30}} width={{1080}} height={{1920}} defaultProps={{{{}} as SceneProps}} calculateMetadata={{calculateMetadata}}/>;\n")
    cards=[dict(id=f's{i:02d}',vi=vi,zh=zh,tag=tag,pic=pic) for i,(vi,zh,tag,pic) in enumerate(ep['cards'],1)]
    props=dict(title=ep['title'],subtitle=ep['subtitle'],episode=ep['number'],cards=cards,
               sheet=ep['sheet'],coverPic=ep.get('cover_pic',0),fps=30,totalSeconds=duration,review_timeline=[])
    sections=[];units=[];scenes=[];cuts=[]
    def scene(sid:str,start:float,end:float,label:str,text:str,native:str='',sub:str=''):
        sections.append(dict(id=sid,text=text,start_seconds=start,end_seconds=end))
        scenes.append(dict(id=sid,type='animation',description=label,start_seconds=start,end_seconds=end,
                           script_section_id=sid,framing='Vietnamese editorial vertical card',movement='short photographic reveal'))
        cuts.append(dict(id=sid,source=f'composition:VietnameseCoupleEpisode#{sid}',in_seconds=start,
                         out_seconds=end,transition_in='cut',transition_out='cut',reason=label))
        props['review_timeline'].append(dict(id=sid,label=label,title=native or label,thai=native,start=start,
                                             end=end,sub=sub,text=text,credit=''))
    scene('sc00',0,INTRO,'封面 · 第一帧',ep['intro'])
    units.append(dict(id='intro_zh',section='sc00',lang='zh',text=ep['intro']))
    for i,c in enumerate(cards):
        start=round(INTRO+i*CARD,1);end=round(start+CARD,1)
        scene(c['id'],start,end,f"{i+1:02d} · {c['zh']}",f"{c['zh']}。 → {c['vi']}",c['vi'],'先听中文，再跟越南语读')
        units.extend([dict(id=f"{c['id']}_zh",section=c['id'],lang='zh',text=f"{c['zh']}。"),
                      dict(id=f"{c['id']}_vi",section=c['id'],lang='vi',text=c['vi'])])
    outro_start=round(INTRO+len(cards)*CARD,1)
    outro='想继续学实用越南语，就来越南语千词，每天学一点。'
    scene('outro',outro_start,duration,'片尾 · App 推广',outro)
    units.append(dict(id='outro_zh',section='outro',lang='zh',text=outro))
    write(p/'artifacts/props.json',props);write(p/'composition/props.json',props)
    script=dict(version='1.0',title=ep['title'],total_duration_seconds=duration,sections=sections,
                metadata=dict(tts=dict(engine='edge',voices=dict(zh='zh-CN-XiaoxiaoNeural',vi='vi-VN-HoaiMyNeural'),
                                       rates=dict(zh='+12%',vi='+8%')),tts_units=units,
                              linguistic_context=PLAN['context']))
    scene_plan=dict(version='1.0',scenes=scenes,metadata=dict(series='情侣越南语',episode=ep['number']))
    edit=dict(version='1.0',renderer_family='animation-first',render_runtime='remotion',composition_mode='atelier',
              cuts=cuts,music=dict(volume=0),subtitles=dict(enabled=False),
              bespoke=dict(entry=str((p/'index.tsx').resolve()),composition_id='VietnameseCoupleEpisode',
                           props_path=str((p/'artifacts/props.json').resolve()),
                           public_dir=str((p/'composition/public').resolve()),
                           art_direction=str((p/'art-direction.md').resolve()),crf=18,concurrency=4),
              metadata=dict(fps=30,resolution='1080x1920',total_seconds=duration,
                            audio_architecture='Chinese before Vietnamese in every card; no music',cover_source_frame=0))
    write(p/'artifacts/script.json',script);write(p/'artifacts/scene_plan.json',scene_plan)
    write(p/'artifacts/edit_decisions.json',edit)
    (p/'art-direction.md').write_text(f"# 情侣越南语 {ep['number']:02d}｜{ep['title']}\n\n"
      "越南城市生活摄影，jade green／砖红／赭黄的编辑式版面，借鉴越南旧街区瓷砖和旅行画册的材质。"
      "封面采用单幅越南生活照片全宽主视觉，标题放在下方深绿文字区，首帧即可用作封面。"
      "与泰语版的奶油白、玫红卡片布局明显不同。每张词卡先听中文、再听越南语。"
      "例句用情侣之间的 anh/em 称呼，关系不同时称呼随之调整。片尾用越南语千词图标。\n")
    assets=dict(version='1.0',assets=[
        dict(id='vietnam_photo_sheet',type='image',path=f"assets/images/{ep['sheet']}",source_tool='image_gen',
             scene_id='all',provider='OpenAI imagegen',generation_summary='Original contemporary Vietnamese couple photography contact sheet'),
        dict(id='app_icon',type='image',path='assets/images/app_icon.png',source_tool='approved_series_asset',scene_id='outro')],
        total_cost_usd=0,metadata=dict(layer3_skills_read=['imagegen','remotion-best-practices']))
    write(p/'artifacts/asset_manifest.json',assets)
    proposal=dict(version='1.0',concept_options=[
        dict(id='c1',title=ep['title'],hook=ep['intro'],narrative_structure='tutorial',
             visual_approach='Vietnamese lifestyle editorial photographs and bilingual word cards',
             target_duration_seconds=duration,why_this_works='Vietnamese phrases and settings are authored independently from Thai series.'),
        dict(id='c2',title='一段越南语对话',hook='听情侣怎么说',narrative_structure='story',
             visual_approach='Continuous scene',target_duration_seconds=duration,why_this_works='A dialogue teaches context.'),
        dict(id='c3',title='越南语跟读小测',hook='你会怎么说？',narrative_structure='tutorial',
             visual_approach='Quiz cards',target_duration_seconds=duration,why_this_works='A quiz supports recall.')],
        selected_concept=dict(concept_id='c1',rationale='User approved a six-part learning series with independent Vietnamese visuals and usage.'),
        production_plan=dict(pipeline='animation',render_runtime='remotion',renderer_family='animation-first',
             composition_mode='atelier',art_direction=str((p/'art-direction.md').resolve()),
             stages=[dict(stage=x,tools=[],approach='Produce and review Vietnamese bilingual episode') for x in
                     ('research','proposal','script','scene_plan','assets','edit','compose','publish')],
             delivery_promise=dict(promise_type='teacher_explainer',motion_required=False,tone_mode='warm educational',
                                   quality_floor='presentable')),
        cost_estimate=dict(total_estimated_usd=0,line_items=[],budget_verdict='no_budget_set'),
        approval=dict(status='approved',user_notes='User requested six Vietnamese episodes after all Thai episodes, with distinct Vietnamese wording and visuals.'))
    write(p/'artifacts/proposal_packet.json',proposal)
    research=dict(version='1.0',topic=ep['title'],research_date='2026-10-08',
        landscape=dict(existing_content=[dict(title=t,source=u,angle='Vietnamese relationship language',
             what_it_covers='Vietnamese pronouns and everyday expressions',url=u) for t,u in SOURCES[:3]],
             saturated_angles=['Literal translations of generic romance phrases'],
             underserved_gaps=['Short Chinese-to-Vietnamese cues situated in contemporary Vietnamese life']),
        data_points=[dict(claim=x,source_url=u,credibility='secondary_source') for x,u in [
            ('Vietnamese personal address reflects relationship and context',SOURCES[0][1]),
            ('Romantic anh/em pronouns depend on the speaker-listener pairing',SOURCES[1][1]),
            ('Personal apology naturally uses relationship terms',SOURCES[2][1])]],
        audience_insights=dict(common_questions=['How should I address my partner?','What is a natural phrase in this situation?',
                                                 'How do I pronounce this with natural Vietnamese rhythm?'],
                               misconceptions=[dict(myth='Anh/em is a fixed universal I/you pair',
                                   reality='Vietnamese address depends on the speaker-listener relationship and context',
                                   source=SOURCES[0][1])],knowledge_level='beginner'),
        angles_discovered=[dict(name=x,hook=ep['intro'],type='evergreen',why_now='Part of the approved series') for x in
                           ('Relationship pronouns','Daily Vietnamese settings','Chinese-first speaking practice')],
        sources=[dict(url=u,title=t,used_for='Vietnamese address and relationship language background') for t,u in SOURCES],
        research_summary='Use anh/em in an explicit relationship context, and pair short Vietnamese utterances with locally grounded scenes.')
    write(p/'artifacts/research_brief.json',research)
    write(p/'artifacts/publish.json',dict(series_id=2,sub_series='情侣越南语',slug=ep['slug'],
        title=f"越南语千词 · 情侣越南语 {ep['number']:02d}｜{ep['title']}，8句一起跟读",
        publish_copy=f"情侣越南语第{ep['number']}期：{ep['title']}。\n\n"+
          '\n'.join(f"{c['vi']} · {c['zh']}" for c in cards)+
          '\n\n例句采用情侣间常见的 anh/em 称呼；实际使用时请按彼此的称呼习惯调整。每句先听中文，再跟读越南语。到「越南语千词」继续学。\n\n#越南语 #情侣越南语 #越南语学习 #越南语口语 #越南语千词',
        wechat_copy=f"情侣越南语 {ep['number']:02d}｜{ep['title']}，8句跟读",
        credits='画面：原创越南情侣生活摄影；中文配音：Edge 晓晓；越南语配音：Edge HoaiMy；App 图标：越南语千词。',
        video_path='renders/final-v1.mp4'))
    for stage,key in [('research','research_brief'),('proposal','proposal_packet'),('script','script'),
                      ('scene_plan','scene_plan'),('assets','asset_manifest'),('edit','edit_decisions')]:
        value=json.loads((p/'artifacts'/f'{key}.json').read_text())
        write_checkpoint(REPO/'projects',pid,stage,'completed',{key:value},human_approved=True)
    print(pid,duration,'seconds')
