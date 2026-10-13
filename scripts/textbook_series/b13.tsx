// 13 尾辅音：一节"กา"车头，后面挂车厢。每念一个，就挂上一节不同颜色的尾巴车厢（ง น ม ย ว），
// 车头不变、只换尾巴 —— 这就是"แม่"（尾辅音类）的意思。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, BookPeek, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

type F={f:string;w:string;mae:string;snd:string};
export type SceneProps=BaseProps&{data:{finals:F[]}};
const RUST="#b5482a",SAND="#f6e7d0",INK="#3b1f12",GRAY="#9b7b66";
const CAR=["#2a9d8f","#e9c46a","#f4a261","#264653","#8ab17d"];

const Car:React.FC<{ch:string;c:string;w:number;h:number}>=({ch,c,w,h})=><div style={{width:w,height:h,borderRadius:h*.16,background:c,display:"flex",alignItems:"center",justifyContent:"center",position:"relative",boxShadow:"0 10px 24px rgba(59,31,18,.2)"}}>
  <div style={{fontFamily:TH,fontSize:h*.62,lineHeight:1.25,color:"#fff"}}>{ch}</div>
  {[0.22,0.78].map(x=><div key={x} style={{position:"absolute",bottom:-h*.16,left:`${x*100}%`,marginLeft:-h*.13,width:h*.26,height:h*.26,borderRadius:"50%",background:INK}}/>)}
</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:SAND}}>
  <Brand color={RUST}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${RUST}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 尾辅音</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:INK,letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:RUST,letterSpacing:4}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1320,left:0,right:0,display:"flex",justifyContent:"center",gap:10}}><Car ch="กา" c={RUST} w={190} h={110}/>{p.data.finals.map((x,k)=><Car key={k} ch={x.f} c={CAR[k]} w={110} h={110}/>)}</div>
</AbsoluteFill>;

const Tails:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`e${k}`]);const x=i!==undefined?p.data.finals[i]:undefined;
  const hook=i!==undefined?ease(t,m[`e${i}`],m[`e${i}`]+0.45):0;
  return <AbsoluteFill style={{background:SAND}}>
  <Brand color={RUST}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:60,color:GRAY}}>{x?<>尾巴 <span style={{fontFamily:TH,color:CAR[i!]}}>{x.f}</span> · <span style={{fontFamily:TH}}>{x.mae}</span></>:"车头不变"}</div>
  <div style={{position:"absolute",top:470,left:0,right:0,display:"flex",justifyContent:"center",alignItems:"center",gap:14}}>
    <Car ch="กา" c={RUST} w={360} h={220}/>
    {x&&<div style={{transform:`translateX(${(1-hook)*300}px)`,opacity:hook}}><Car ch={x.f} c={CAR[i!]} w={220} h={220}/></div>}
  </div>
  <div style={{position:"absolute",top:540+220+40,left:60,right:60,height:10,borderRadius:5,background:"#c7ab8e"}}/>
  {x&&<div style={{position:"absolute",top:870,left:0,right:0,textAlign:"center",opacity:hook}}>
    <div style={{fontFamily:TH,fontSize:220,lineHeight:1.3,color:INK}}>{x.w}</div>
    <div style={{fontFamily:"Helvetica, sans-serif",fontWeight:800,fontSize:56,color:CAR[i!]}}>kaa{x.snd}</div>
  </div>}
  {i!==undefined&&<div style={{position:"absolute",top:1240,left:190,width:700}}><FollowBar t={t} m={m} k={`e${i}`} fg={RUST} track="rgba(181,72,42,.14)" muted={GRAY} label={`${i+1} / 5`}/></div>}
  <div style={{position:"absolute",top:1370,left:0,right:0,display:"flex",justifyContent:"center",gap:16}}>{p.data.finals.map((q,k)=><div key={k} style={{fontFamily:TH,fontSize:54,lineHeight:1.4,color:i!==undefined&&k<=i?CAR[k]:"rgba(59,31,18,.2)"}}>{q.w}</div>)}</div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:SAND}}>
  <Brand color={RUST}/>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:INK}}>第 <span style={{color:RUST}}>1</span> 册 · 第 <span style={{color:RUST}}>9</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="head" w={900}/></div>
  <div style={{position:"absolute",top:780,left:0,right:0,display:"flex",justifyContent:"center",opacity:ease(t,s.start+0.8,s.start+1.3)}}><BookPeek name="table" w={860} rot={-1}/></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:SAND}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("tails")} t={t}><Tails p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, ${RUST} 0%, #6e2814 75%)`} accent="#ffe0b8"/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
