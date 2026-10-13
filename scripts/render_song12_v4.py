"""Render the standalone-narration revision of song 12 via VideoCompose."""
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from lib.checkpoint import write_checkpoint
from tools.video.video_compose import VideoCompose
P=ROOT/'projects/thai-1000-song-12-sai-naen-hua-jai'
props=json.loads((P/'composition/props.json').read_text())
cuts=[{'id':b['id'],'source':'composition:SaiNaenHuaJai#'+b['id'],'in_seconds':round(b['startFrame']/30,3),'out_seconds':round((b['startFrame']+b['frames'])/30,3),'transition_out':'fade','transition_duration':.2,'reason':b['kind']} for b in props['blocks']]
edit={'version':'1.0','renderer_family':'explainer-teacher','render_runtime':'remotion','composition_mode':'atelier','cuts':cuts,'music':{'volume':1,'ducking':False},'subtitles':{'enabled':False},'bespoke':{'entry':str((P/'composition/index.tsx').resolve()),'composition_id':'SaiNaenHuaJai','props_path':str((P/'composition/props.json').resolve()),'public_dir':str((P/'composition/public').resolve()),'crf':18,'timeout_ms':180000,'concurrency':2,'art_direction':'Isan rice-field dusk, indigo weave and fate thread; official MV chorus with 32 phrase cards, Thai TTS and Chinese meanings'},'metadata':{'fps':30,'resolution':'1080x1920','total_seconds':props['totalSeconds'],'proposal_render_runtime':'remotion','subtitles_reason':'泰中歌词和逐词卡面已内嵌'}}
(P/'artifacts/edit_decisions.json').write_text(json.dumps(edit,ensure_ascii=False,indent=2)+'\n')
write_checkpoint(ROOT/'projects',P.name,'edit','completed',{'edit_decisions':edit},pipeline_type='animated-explainer',metadata={'revision':'v4-self-contained'})
write_checkpoint(ROOT/'projects',P.name,'compose','in_progress',{},pipeline_type='animated-explainer',metadata={'revision':'v4-self-contained'})
out=P/'renders/final-v4.mp4';proposal=json.loads((P/'artifacts/proposal_packet.json').read_text())
r=VideoCompose().execute({'operation':'render','edit_decisions':edit,'proposal_packet':proposal,'output_path':str(out)})
if not r.success:print('render failed',r.error,file=sys.stderr);raise SystemExit(2)
print(out,out.stat().st_size)
