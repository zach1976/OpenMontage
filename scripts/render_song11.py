"""Render the song 11 atelier composition through VideoCompose."""
from __future__ import annotations

import json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from tools.video.video_compose import VideoCompose

P=ROOT/'projects/thai-1000-song-11-mai-mi-khrai-ru-tua-rao'
props=json.loads((P/'composition/props.json').read_text())
cuts=[]
for b in props['blocks']:
    cuts.append({'id':b['id'],'source':'composition:MaiMiKhraiRuTuaRao#'+b['id'],'in_seconds':round(b['startFrame']/30,3),'out_seconds':round((b['startFrame']+b['frames'])/30,3),'transition_out':'fade','transition_duration':.2,'reason':'先原唱、再词组、最后回听' if b['kind'].startswith('song') else '原唱片段→泰语跟读→中文解释' if b['kind']=='word' else b['kind']})
edit={'version':'1.0','renderer_family':'explainer-teacher','render_runtime':'remotion','composition_mode':'atelier','cuts':cuts,'music':{'volume':1,'ducking':False},'subtitles':{'enabled':False},'bespoke':{'entry':str((P/'composition/index.tsx').resolve()),'composition_id':'MaiMiKhraiRuTuaRao','props_path':str((P/'composition/props.json').resolve()),'public_dir':str((P/'composition/public').resolve()),'crf':18,'timeout_ms':180000,'concurrency':2,'art_direction':'Night to dawn: paired Thai-Chinese lyric highlights, original singing before every word'},'metadata':{'fps':30,'resolution':'1080x1920','total_seconds':props['totalSeconds'],'proposal_render_runtime':'remotion','subtitles_reason':'歌词和逐词卡面已内嵌双语文字'}}
(P/'artifacts/edit_decisions.json').write_text(json.dumps(edit,ensure_ascii=False,indent=2)+'\n')
out=P/'renders/final-v4.mp4';proposal=json.loads((P/'artifacts/proposal_packet.json').read_text())
r=VideoCompose().execute({'operation':'render','edit_decisions':edit,'proposal_packet':proposal,'output_path':str(out)})
if not r.success:print('render failed',r.error,file=sys.stderr);raise SystemExit(2)
print(out,out.stat().st_size)
