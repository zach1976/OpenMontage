// 越 01 六个声调：一排六个琴键 —— 同一个 ma，按下哪个键就是哪个声调。
// 中间放大当前这个词，声调名和意思跟着换；键盘本身就是"一个音六种按法"。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta} from "./Common";

type Tone={vi:string;mark:string;name:string;zh:string;tone:string};
export type SceneProps=BaseProps&{data:{tones:Tone[]}};

const JADE="#0f3b36",JADE2="#175249",LOTUS="#f07aa0",CREAM="#fbf3e6",DIM="rgba(251,243,230,.45)";
const BG=`radial-gradient(ellipse at 50% 42%, ${JADE2} 0%, ${JADE} 72%)`;

const Keys:React.FC<{tones:Tone[];cur:number;top:number;h:number;showZh?:boolean}>=({tones,cur,top,h,showZh})=><div style={{position:"absolute",top,left:60,right:60,height:h,display:"flex",gap:12}}>
  {tones.map((x,i)=>{const on=i===cur;return <div key={i} style={{flex:1,borderRadius:"0 0 22px 22px",background:on?LOTUS:CREAM,boxShadow:on?`0 0 40px ${LOTUS}`:"inset 0 -10px 0 rgba(15,59,54,.12)",transform:`translateY(${on?14:0}px)`,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"flex-end",paddingBottom:22}}>
    <div style={{fontFamily:VI,fontSize:h>300?62:46,color:on?"#fff":JADE}}>{x.vi}</div>
    {showZh&&<div style={{fontFamily:ZH,fontWeight:800,fontSize:30,color:on?"#fff":"#6f8c86"}}>{x.zh}</div>}
  </div>;})}
</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:BG}}>
  <Brand color={LOTUS}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:CREAM,border:`2px solid ${LOTUS}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 声调</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:CREAM,letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:CREAM,letterSpacing:6}}><span style={{color:LOTUS}}>六个</span>声调</div>
  <Keys tones={p.data.tones} cur={1} top={1300} h={180}/>
</AbsoluteFill>;

const Tones:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[5,4,3,2,1,0].find(k=>t>=m[`w${k}`])??0;const x=p.data.tones[i];const pop=ease(t,m[`w${i}_a`]-0.05,m[`w${i}_a`]+0.25);
  return <AbsoluteFill style={{background:BG}}>
  <Brand color={LOTUS}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:64,color:LOTUS}}>{x.tone}<span style={{fontFamily:VI,fontSize:50,color:DIM}}>　{x.name}</span></div>
  <div style={{position:"absolute",top:450,left:0,right:0,textAlign:"center",fontFamily:VI,fontSize:330,lineHeight:1.3,color:CREAM,transform:`scale(${0.92+0.08*pop})`}}>{x.vi}</div>
  <div style={{position:"absolute",top:930,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:96,color:LOTUS}}>{x.zh}</div>
  <div style={{position:"absolute",top:1080,left:190,width:700}}><FollowBar t={t} m={m} k={`w${i}`} fg={LOTUS} track="rgba(251,243,230,.14)" muted={DIM} label={`${i+1} / 6`}/></div>
  <Keys tones={p.data.tones} cur={i} top={1210} h={300} showZh/>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:BG}}>
  <Brand color={LOTUS}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:CREAM}}>声调在语音部分</div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:110,opacity:up}}><Books w={860} shadow="0 30px 80px rgba(0,0,0,.5)"/></div>
  <div style={{position:"absolute",top:1340,left:0,right:0,display:"flex",justifyContent:"center",gap:20,opacity:ease(t,s.start+0.9,s.start+1.3)}}>{["国家级教学成果二等奖","共 4 册"].map(x=><div key={x} style={{fontFamily:ZH,fontWeight:900,fontSize:42,color:JADE,background:LOTUS,borderRadius:18,padding:"10px 26px"}}>{x}</div>)}</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:JADE}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("tones")} t={t}><Tones p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={BG} accent={LOTUS}/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
