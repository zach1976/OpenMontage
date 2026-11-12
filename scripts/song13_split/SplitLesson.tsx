import React from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

type Lyric = {at:number; th:string; zh:string; chunks:{at:number;text:string}[]};
type Block = {id:string; label:string; kind:'song'|'intro'|'word'|'bridge'|'outro'; startFrame:number; frames:number; th?:string; zh?:string; detail?:string[]; source?:[number,number]; thaiAt?:number; zhAt?:number; audioId?:string; still?:string; ordinal?:number; replay?:boolean};
export type LessonProps = {fps:number; totalFrames:number; title:string; part:number; songStart:number; songFrames:number; blocks:Block[]; lines:Lyric[]; review_timeline:unknown[]};
const INK='#0D1D2D', MID='#172D40', PAPER='#F3F1E9', GOLD='#C9AC7A', MUTED='#AAB8BF';
const ZH='PingFang SC, Noto Sans CJK SC, sans-serif';
const TH='Sarabun, Thonburi, sans-serif';
const clamp=(v:number)=>Math.max(0,Math.min(1,v));

const Canvas:React.FC<{children:React.ReactNode;eyebrow:string;frame:number;part:number}>=({children,eyebrow,frame,part})=><AbsoluteFill style={{background:`radial-gradient(circle at ${part===1?'25% 22%':'73% 28%'}, ${MID} 0%, ${INK} 65%)`,color:PAPER,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,opacity:.13,backgroundImage:'radial-gradient(circle, #D9C6A0 1px, transparent 1px)',backgroundSize:'40px 40px',transform:`translateY(${Math.sin(frame/58)*12}px)`}}/>
  <div style={{position:'absolute',left:64,top:58,right:64,height:2,background:GOLD,opacity:.75}}/>
  <div style={{position:'absolute',left:64,top:82,fontFamily:ZH,fontSize:30,fontWeight:700,letterSpacing:3,color:GOLD}}>泰语千词 · SONG 13 · {part===1?'上篇':'下篇'}</div>
  <div style={{position:'absolute',right:64,top:140,fontFamily:ZH,fontSize:26,color:MUTED}}>{eyebrow}</div>
  <div style={{position:'absolute',left:64,bottom:70,right:64,height:1,background:GOLD,opacity:.45}}/>
  <div style={{position:'absolute',left:64,bottom:29,fontFamily:ZH,fontSize:20,letterSpacing:2,color:MUTED}}>BOWKYLION  /  นาฬิกาทราย (sign)</div>{children}
</AbsoluteFill>;
const MV:React.FC<{still?:string}>=({still})=><div style={{position:'absolute',left:0,right:0,top:245,height:608,overflow:'hidden',background:'#15222C',borderTop:`2px solid ${GOLD}`,borderBottom:`2px solid ${GOLD}`}}>
  {still?<Img src={staticFile(`images/${still}`)} style={{width:'100%',height:'100%',objectFit:'cover'}}/>:<OffthreadVideo src={staticFile('video/pair.mp4')} muted style={{width:'100%',height:'100%',objectFit:'cover'}}/>}
  <div style={{position:'absolute',right:24,bottom:18,padding:'8px 15px',background:'rgba(8,20,28,.7)',fontFamily:ZH,fontSize:22,color:PAPER}}>BOWKYLION · 官方 MV</div>
</div>;

const Song:React.FC<{block:Block; props:LessonProps}>=({block,props})=>{
  const f=useCurrentFrame(),t=f/props.fps;
  const i=Math.max(0,props.lines.reduce((a,l,k)=>t>=l.at?k:a,0));
  const line=props.lines[i], active=Math.max(0,line.chunks.reduce((a,c,k)=>t>=c.at?k:a,0));
  return <Canvas eyebrow={block.replay?'第二遍 · 听懂了吗':'第一遍 · 先听原唱'} frame={f} part={props.part}>
    <MV/>
    <div style={{position:'absolute',left:64,top:905,fontFamily:ZH,fontSize:30,color:GOLD}}>{block.replay?'带着词义回听':'原唱两句'} · {String(i+1).padStart(2,'0')} / 02</div>
    <div style={{position:'absolute',left:64,right:64,top:1025,minHeight:325,display:'flex',flexDirection:'column',justifyContent:'center'}}>
      <div style={{fontFamily:TH,fontWeight:700,fontSize:line.th.length>24?65:76,lineHeight:1.42,textShadow:'0 9px 32px rgba(0,0,0,.28)',overflowWrap:'anywhere'}}>{line.chunks.map((c,k)=><span key={k} style={{color:k===active?GOLD:PAPER}}>{c.text}</span>)}</div>
      {block.replay?<div style={{fontFamily:ZH,fontWeight:700,fontSize:52,lineHeight:1.45,color:GOLD,marginTop:36}}>{line.zh}</div>:<div style={{fontFamily:ZH,fontSize:31,color:MUTED,marginTop:42}}>先听声音，稍后逐词拆解</div>}
    </div>
    <div style={{position:'absolute',left:64,right:64,bottom:224,height:3,background:'#42515D'}}><div style={{width:`${clamp(f/block.frames)*100}%`,height:'100%',background:GOLD}}/></div>
    <Audio src={staticFile('audio/original.mp3')} trimBefore={Math.round(props.songStart*props.fps)} trimAfter={Math.round(props.songStart*props.fps)+props.songFrames} volume={.92}/>
  </Canvas>;
};
const Intro:React.FC<{part:number}>=({part})=>{const f=useCurrentFrame();return <Canvas eyebrow="歌曲小介绍" frame={f} part={part}>
  <MV still={part===1?'word_06_mv.jpg':'word_09_mv.jpg'}/>
  <div style={{position:'absolute',left:64,top:920,fontFamily:ZH,fontSize:32,color:GOLD,letterSpacing:3}}>BOWKYLION · 《沙漏》</div>
  <div style={{position:'absolute',left:64,right:70,top:1055,fontFamily:ZH,fontSize:65,fontWeight:800,lineHeight:1.55}}>沙漏里的沙慢慢落下，<br/>像一段<span style={{color:GOLD}}>走向结束的感情</span>。</div>
  <div style={{position:'absolute',left:64,right:64,top:1430,fontFamily:TH,fontSize:42,color:MUTED}}>นาฬิกาทราย · 时间在流逝</div>
  <div style={{position:'absolute',left:64,right:64,top:1550,fontFamily:ZH,fontSize:31,color:GOLD}}>接着，拆开听。</div>
  <Audio src={staticFile('audio/song_intro_zh_v2.mp3')}/>
  </Canvas>};
const Word:React.FC<{block:Block;part:number;wordCount:number}>=({block,part,wordCount})=>{
  const f=useCurrentFrame(),{fps}=useVideoConfig(); const phase=f/fps<(block.thaiAt||0)?0:f/fps<(block.zhAt||0)?1:2;
  const enter=interpolate(f,[0,16],[.88,1],{extrapolateRight:'clamp'});
  return <Canvas eyebrow={`逐词拆解 · ${String(block.ordinal).padStart(2,'0')} / ${String(wordCount).padStart(2,'0')}`} frame={f} part={part}>
    <MV still={block.still}/>
    <div style={{position:'absolute',left:64,top:895,fontFamily:ZH,fontSize:29,color:GOLD}}>原唱 · 跟读 · 用法</div>
    <div style={{position:'absolute',left:62,right:62,top:955,transform:`scale(${enter})`,transformOrigin:'left center',fontFamily:TH,fontSize:block.th!.length>11?68:86,fontWeight:700,lineHeight:1.35,wordBreak:'break-word'}}>{block.th}</div>
    <div style={{position:'absolute',left:64,right:64,top:1166,height:2,background:GOLD,opacity:.65}}/>
    <div style={{position:'absolute',left:64,right:64,top:1200,fontFamily:ZH,fontSize:59,fontWeight:800,lineHeight:1.3,color:phase===2?GOLD:PAPER}}>{block.zh}</div>
    <div style={{position:'absolute',left:64,right:64,top:1330,fontFamily:ZH,fontSize:34,lineHeight:1.5,color:PAPER}}>{block.detail?.map((s,i)=><div key={i}>{s}</div>)}</div>
    <div style={{position:'absolute',left:64,right:64,top:1604,display:'flex',gap:14}}>{['原唱','跟读','词义'].map((x,i)=><div key={x} style={{flex:1,border:`1px solid ${phase===i?GOLD:'#53616B'}`,background:phase===i?GOLD:'transparent',color:phase===i?INK:MUTED,textAlign:'center',padding:'13px 0',borderRadius:6,fontFamily:ZH,fontSize:27,fontWeight:700}}>{x}</div>)}</div>
    <Audio src={staticFile('audio/original.mp3')} trimBefore={Math.round(block.source![0]*fps)} trimAfter={Math.round(block.source![1]*fps)} volume={.9}/>
    <Sequence from={Math.round((block.thaiAt||0)*fps)}><Audio src={staticFile(`audio/${block.audioId}_th.mp3`)}/></Sequence>
    <Sequence from={Math.round((block.zhAt||0)*fps)}><Audio src={staticFile(`audio/${block.audioId}_zh_v4.mp3`)}/></Sequence>
  </Canvas>;
};
const Bridge:React.FC<{part:number}>=({part})=>{const f=useCurrentFrame();return <Canvas eyebrow="再听一遍" frame={f} part={part}>
  <div style={{position:'absolute',left:64,right:64,top:530,fontFamily:TH,fontSize:74,color:GOLD}}>นาฬิกาทราย</div>
  <div style={{position:'absolute',left:64,right:64,top:680,fontFamily:ZH,fontSize:51,fontWeight:700}}>刚才的词，连起来再听两句。</div>
  <div style={{position:'absolute',left:64,right:64,top:820,height:2,background:GOLD}}/>
  <div style={{position:'absolute',left:64,right:64,top:940,fontFamily:ZH,fontSize:46,lineHeight:1.6,color:MUTED}}>{part===1?'从“我的爱”到“终会消散”。':'从“我们的爱”到“终会消失”。'}</div>
  {part===1?<Audio src={staticFile('audio/bridge_zh_v4.mp3')}/>:null}
  </Canvas>};
const Outro:React.FC<{part:number}>=({part})=>{const f=useCurrentFrame();const v=interpolate(f,[0,12],[0,1],{extrapolateRight:'clamp'});return <Canvas eyebrow="学泰语 · 用泰语千词" frame={f} part={part}>
  <div style={{position:'absolute',left:350,top:415,width:380,height:380,borderRadius:82,overflow:'hidden',boxShadow:'0 28px 72px rgba(0,0,0,.36)',transform:`scale(${.9+.1*v})`,opacity:v}}><Img src={staticFile('app/app_icon.png')} style={{width:'100%',height:'100%'}}/></div>
  <div style={{position:'absolute',left:64,right:64,top:930,textAlign:'center',fontFamily:ZH,fontSize:96,fontWeight:850,opacity:v}}>泰语千词</div>
  <div style={{position:'absolute',left:64,right:64,top:1095,height:2,background:GOLD,opacity:.75}}/>
  <div style={{position:'absolute',left:64,right:64,top:1170,textAlign:'center',fontFamily:ZH,fontSize:60,fontWeight:800,lineHeight:1.4,color:GOLD,opacity:v}}>在泰国生活够用了</div>
  <Audio src={staticFile('audio/outro_zh_v5.mp3')}/>
  </Canvas>};
export const SplitLesson:React.FC<LessonProps>=(props)=><AbsoluteFill style={{background:INK}}>
  <style>{`@font-face{font-family:Sarabun;src:url("${staticFile('fonts/Sarabun-Bold.ttf')}");font-weight:700;}`}</style>
  {props.blocks.map(b=><Sequence key={b.id} from={b.startFrame} durationInFrames={b.frames}>
    {b.kind==='song'?<Song block={b} props={props}/>:b.kind==='intro'?<Intro part={props.part}/>:b.kind==='word'?<Word block={b} part={props.part} wordCount={props.blocks.filter(x=>x.kind==='word').length}/>:b.kind==='bridge'?<Bridge part={props.part}/>:<Outro part={props.part}/>}
  </Sequence>)}
</AbsoluteFill>;
