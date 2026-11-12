// 越 13 天气：一块电视天气预报板。左边是今天这一格的大图标（程序画的太阳/雪花/雨/云/风），
// 右边一列五天预报，念到哪个词，预报板就翻到那一天。
import React from "react";
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta} from "./Common";

type It={vi:string;zh:string;icon:"hot"|"cold"|"rain"|"sun"|"wind";day:string};
export type SceneProps=BaseProps&{data:{items:It[]}};
const SKY="#0f4c81",SKY2="#1b6fb3",SUN="#ffc93c",WHITE="#f6fbff",DIM="rgba(246,251,255,.45)";

const Icon:React.FC<{k:It["icon"];s:number;t:number}>=({k,s,t})=>{const spin=t*40;const box={position:"relative" as const,width:s,height:s};
  if(k==="hot"||k==="sun")return <div style={box}><div style={{position:"absolute",inset:s*.25,borderRadius:"50%",background:k==="hot"?"#ff7b39":SUN,boxShadow:`0 0 ${s*.25}px ${k==="hot"?"#ff7b39":SUN}`}}/>
    {Array.from({length:8}).map((_,j)=><div key={j} style={{position:"absolute",left:s/2-6,top:s*.02,width:12,height:s*.16,borderRadius:6,background:k==="hot"?"#ff7b39":SUN,transformOrigin:`6px ${s*.48}px`,transform:`rotate(${j*45+spin}deg)`}}/>)}</div>;
  if(k==="cold")return <div style={box}>{[0,60,120].map(r=><div key={r} style={{position:"absolute",left:s/2-7,top:s*.08,width:14,height:s*.84,borderRadius:7,background:"#bfe6ff",transform:`rotate(${r}deg)`}}/>)}</div>;
  const cloud=<div style={{position:"absolute",left:s*.12,top:s*.22,width:s*.76,height:s*.36,borderRadius:s*.2,background:WHITE}}><div style={{position:"absolute",left:s*.14,top:-s*.16,width:s*.36,height:s*.36,borderRadius:"50%",background:WHITE}}/></div>;
  if(k==="rain")return <div style={box}>{cloud}{[0,1,2,3].map(j=><div key={j} style={{position:"absolute",left:s*(.22+j*.16),top:s*.64+((t*300+j*40)%(s*.25)),width:8,height:s*.12,borderRadius:4,background:"#7cc4ff",transform:"rotate(15deg)"}}/>)}</div>;
  return <div style={box}>{[0,1,2].map(j=><div key={j} style={{position:"absolute",left:s*.1+((t*120+j*50)%(s*.2)),top:s*(.3+j*.18),width:s*(.7-j*.12),height:10,borderRadius:5,background:WHITE}}/>)}</div>;
};

const Cover:React.FC<{p:SceneProps}>=({p})=>{const f=useCurrentFrame();return <AbsoluteFill style={{background:`linear-gradient(180deg, ${SKY2}, ${SKY})`}}>
  <Brand color={WHITE}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:WHITE,border:`2px solid ${SUN}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 天气</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:WHITE}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:900,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:SUN}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1210,left:0,right:0,display:"flex",justifyContent:"center",gap:20}}>{p.data.items.map((x,k)=><Icon key={k} k={x.icon} s={150} t={f/30}/>)}</div>
</AbsoluteFill>;};

const Forecast:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`wx${k}`]);const x=i!==undefined?p.data.items[i]:undefined;const a=i!==undefined?ease(t,m[`wx${i}`],m[`wx${i}`]+0.35):0;
  return <AbsoluteFill style={{background:`linear-gradient(180deg, ${SKY2}, ${SKY})`}}>
  <Brand color={WHITE}/>
  <div style={{position:"absolute",top:340,left:60,width:600,height:640,borderRadius:30,background:"rgba(255,255,255,.1)",border:"3px solid rgba(255,255,255,.25)"}}>
    {x&&<div style={{opacity:a}}>
      <div style={{position:"absolute",top:30,left:40,fontFamily:ZH,fontSize:34,color:DIM}}>{x.day}</div>
      <div style={{position:"absolute",top:90,left:150}}><Icon k={x.icon} s={300} t={t}/></div>
      <div style={{position:"absolute",top:420,left:40,right:40,fontFamily:VI,fontSize:110,color:WHITE}}>{x.vi}</div>
      <div style={{position:"absolute",top:550,left:40,fontFamily:ZH,fontWeight:900,fontSize:56,color:SUN}}>{x.zh}</div></div>}
  </div>
  <div style={{position:"absolute",top:340,left:700,right:60,display:"flex",flexDirection:"column",gap:12}}>{p.data.items.map((q,k)=><div key={k} style={{height:118,borderRadius:20,background:k===i?SUN:"rgba(255,255,255,.08)",display:"flex",alignItems:"center",justifyContent:"space-between",padding:"0 22px"}}>
    <span style={{fontFamily:ZH,fontWeight:800,fontSize:30,color:k===i?SKY:DIM}}>{q.day}</span><Icon k={q.icon} s={80} t={t}/></div>)}</div>
  {i!==undefined&&<div style={{position:"absolute",top:1080,left:150,width:780}}><FollowBar t={t} m={m} k={`wx${i}`} fg={SUN} track="rgba(255,255,255,.15)" muted={DIM} label={`${i+1} / 5`}/></div>}
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:WHITE}}>
  <Brand color={SKY}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:SKY}}>四册 <span style={{color:"#ff7b39"}}>+</span> 词汇手册</div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",gap:40,opacity:up}}>
    <div style={{width:420,height:381,borderRadius:12,overflow:"hidden",boxShadow:"0 24px 60px rgba(0,0,0,.3)"}}><Img src={staticFile("img/books.png")} style={{width:"100%",height:"100%",objectFit:"cover"}}/></div>
    <div style={{width:334,height:381,borderRadius:12,overflow:"hidden",boxShadow:"0 24px 60px rgba(0,0,0,.3)"}}><Img src={staticFile("img/handbook.png")} style={{width:"100%",height:"100%",objectFit:"cover"}}/></div>
  </div>
  <div style={{position:"absolute",top:1020,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:48,color:SKY,opacity:ease(t,s.start+0.9,s.start+1.3)}}>8 大主题 · 32 个情景</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:SKY}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("forecast")} t={t}><Forecast p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, ${SKY2} 0%, ${SKY} 75%)`} accent={SUN}/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
