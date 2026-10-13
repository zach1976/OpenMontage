// 16 报时：一只表盘。每句话把指针拨到它说的那个钟点，背景随白天/夜里变亮变暗 ——
// "晚上另有叫法"不用讲，看天色就明白。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, BookPeek, End, ZH, TH, cl, ease, sceneOf, calcMeta} from "./Common";

type Line={th:string;zh:string;h:number;m:number};
export type SceneProps=BaseProps&{data:{lines:Line[]}};
const AMBER="#ffb703",SKYD="#a9d6f5",NIGHT="#14213d",INK="#0b132b",CREAM="#fdf6e3";
const thSize=(s:string)=>s.length>18?70:86;

const Clock:React.FC<{h:number;m:number;size:number;dark:boolean}>=({h,m,size,dark})=>{const r=size/2;const ha=((h%12)+m/60)*30,ma=m*6;const fg=dark?CREAM:INK;
  return <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
    <circle cx={r} cy={r} r={r-8} fill={dark?"#1f2c4f":"#fff"} stroke={AMBER} strokeWidth={10}/>
    {Array.from({length:12}).map((_,k)=>{const a=k*30*Math.PI/180;return <line key={k} x1={r+Math.sin(a)*(r-30)} y1={r-Math.cos(a)*(r-30)} x2={r+Math.sin(a)*(r-55)} y2={r-Math.cos(a)*(r-55)} stroke={fg} strokeWidth={k%3?4:9} strokeLinecap="round"/>;})}
    <line x1={r} y1={r} x2={r+Math.sin(ha*Math.PI/180)*r*0.5} y2={r-Math.cos(ha*Math.PI/180)*r*0.5} stroke={fg} strokeWidth={16} strokeLinecap="round"/>
    <line x1={r} y1={r} x2={r+Math.sin(ma*Math.PI/180)*r*0.75} y2={r-Math.cos(ma*Math.PI/180)*r*0.75} stroke={AMBER} strokeWidth={9} strokeLinecap="round"/>
    <circle cx={r} cy={r} r={14} fill={AMBER}/>
  </svg>;};

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:`linear-gradient(180deg, ${SKYD} 0%, #5b7db1 50%, ${NIGHT} 100%)`}}>
  <Brand color={INK}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${INK}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 时间</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:"#fff",letterSpacing:6,textShadow:"0 6px 24px rgba(0,0,0,.3)"}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:140,color:AMBER,letterSpacing:4,textShadow:"0 6px 24px rgba(0,0,0,.4)"}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1290,left:0,right:0,display:"flex",justifyContent:"center",gap:60,fontFamily:TH,fontSize:76,lineHeight:1.4}}><span style={{color:INK}}>☀ โมง</span><span style={{color:AMBER}}>☾ ทุ่ม</span></div>
</AbsoluteFill>;

const ClockScene:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const mk=p.marks;const i=[3,2,1,0].find(k=>t>=mk[`c${k}`])??0;const L=p.data.lines;const l=L[i];const prev=L[Math.max(0,i-1)];
  const k=ease(t,mk[`c${i}`],mk[`c${i}`]+0.8);const cur=(prev.h*60+prev.m)+((l.h*60+l.m)-(prev.h*60+prev.m))*k;const tot=Math.floor(cur+1e-6);const hh=Math.floor(tot/60),mm=tot%60;
  const night=hh>=19||hh<6;const nk=interpolate(cur,[17*60,20*60],[0,1],cl);
  const bg=`linear-gradient(180deg, ${night?NIGHT:SKYD} 0%, ${night?"#22335e":"#e8f4fd"} 100%)`;const fg=nk>0.5?CREAM:INK;
  return <AbsoluteFill style={{background:bg}}>
  <Brand color={nk>0.5?AMBER:INK}/>
  <div style={{position:"absolute",top:330,left:0,right:0,display:"flex",justifyContent:"center"}}><Clock h={hh} m={mm} size={520} dark={nk>0.5}/></div>
  <div style={{position:"absolute",top:880,left:0,right:0,textAlign:"center",fontFamily:"SF Pro Display, Helvetica, sans-serif",fontWeight:800,fontSize:90,color:AMBER}}>{String(hh%24).padStart(2,"0")}:{String(mm).padStart(2,"0")}</div>
  <div style={{position:"absolute",top:1010,left:60,right:60,textAlign:"center",opacity:ease(t,mk[`c${i}`],mk[`c${i}`]+0.3)}}>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:70,color:fg}}>{l.zh}</div>
    <div style={{fontFamily:TH,fontSize:thSize(l.th),lineHeight:1.5,color:fg}}>{l.th}</div>
  </div>
  <div style={{position:"absolute",top:1290,left:190,width:700}}><FollowBar t={t} m={mk} k={`c${i}`} fg={AMBER} track={nk>0.5?"rgba(253,246,227,.15)":"rgba(11,19,43,.12)"} muted={nk>0.5?"rgba(253,246,227,.6)":"#5b6b80"} label={`${i+1} / 4`}/></div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:NIGHT}}>
  <Brand color={AMBER}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:CREAM}}>第 <span style={{color:AMBER}}>2</span> 册 · 第 <span style={{color:AMBER}}>4</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="dlg" w={860} rot={1.5} shadow="0 30px 80px rgba(0,0,0,.6)"/></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:NIGHT}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("clock")} t={t}><ClockScene p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #2b3d6b 0%, ${NIGHT} 75%)`} accent={AMBER}/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
