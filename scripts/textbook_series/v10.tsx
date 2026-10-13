// 越 10 住酒店：一块电梯按钮面板。五个词就是五层楼，念到哪个词，那一层的按钮亮起、
// 楼层屏跳到那一层，屏上显示这层的词 —— 前台到房间，一层层往上。
import React from "react";
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta, cl} from "./Common";

type It={vi:string;zh:string;n:string};
export type SceneProps=BaseProps&{data:{items:It[]}};
const STEEL="#2b2f36",STEEL2="#3c424b",AMBER="#ffb627",LCD="#0b1d12",GLOW="#5dff8f",PALE="#e9ecef",DIM="rgba(233,236,239,.4)";
const viSize=(s:string)=>s.length>14?66:s.length>10?80:96;

const Btn:React.FC<{n:string;on:boolean;cur:boolean}>=({n,on,cur})=><div style={{width:130,height:130,borderRadius:"50%",background:`radial-gradient(circle at 40% 35%, #59616c, ${STEEL})`,border:`6px solid ${cur?AMBER:on?"rgba(255,182,39,.45)":"#555c66"}`,boxShadow:cur?`0 0 40px ${AMBER}`:"inset 0 4px 10px rgba(0,0,0,.4)",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:"Helvetica, sans-serif",fontWeight:800,fontSize:58,color:cur?AMBER:on?"rgba(255,182,39,.7)":PALE}}>{n}</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:`linear-gradient(90deg, ${STEEL}, ${STEEL2} 50%, ${STEEL})`}}>
  <Brand color={AMBER}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:PALE,border:`2px solid ${AMBER}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 酒店</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:PALE,letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:AMBER,letterSpacing:4}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1320,left:0,right:0,display:"flex",justifyContent:"center",gap:24,transform:"scale(.8)"}}>{p.data.items.map(x=><Btn key={x.n} n={x.n} on={false} cur={x.n==="5"}/>)}</div>
</AbsoluteFill>;

const Lift:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`o${k}`]);const x=i!==undefined?p.data.items[i]:undefined;const a=i!==undefined?ease(t,m[`o${i}`],m[`o${i}`]+0.35):0;
  const floor=i===undefined?"L":String(Math.round(interpolate(t,[m[`o${i}`],m[`o${i}`]+0.4],[i,i+1],cl)));
  return <AbsoluteFill style={{background:`linear-gradient(90deg, ${STEEL}, ${STEEL2} 50%, ${STEEL})`}}>
  <Brand color={AMBER}/>
  <div style={{position:"absolute",top:340,left:90,right:90,height:500,borderRadius:24,background:LCD,border:"8px solid #14171c",boxShadow:"inset 0 0 40px rgba(93,255,143,.12)"}}>
    <div style={{position:"absolute",top:24,left:36,fontFamily:"Courier New, monospace",fontWeight:900,fontSize:120,color:GLOW}}>{floor}<span style={{fontSize:60}}>{i!==undefined&&a<1?" ▲":""}</span></div>
    {x&&<div style={{position:"absolute",top:200,left:36,right:36,opacity:a}}>
      <div style={{fontFamily:VI,fontSize:viSize(x.vi),lineHeight:1.3,color:GLOW}}>{x.vi}</div>
      <div style={{fontFamily:ZH,fontWeight:900,fontSize:60,color:AMBER,marginTop:10}}>{x.zh}</div></div>}
  </div>
  <div style={{position:"absolute",top:900,left:0,right:0,display:"flex",justifyContent:"center",gap:24}}>{p.data.items.map((q,k)=><Btn key={k} n={q.n} on={i!==undefined&&k<i} cur={k===i}/>)}</div>
  {i!==undefined&&<div style={{position:"absolute",top:1110,left:190,width:700}}><FollowBar t={t} m={m} k={`o${i}`} fg={AMBER} track="rgba(255,255,255,.12)" muted={DIM} label={`${i+1} / 5`}/></div>}
  <div style={{position:"absolute",top:1250,left:90,right:90,display:"flex",flexDirection:"column",gap:6}}>{p.data.items.map((q,k)=><div key={k} style={{fontFamily:ZH,fontSize:30,color:i!==undefined&&k<=i?PALE:"rgba(233,236,239,.25)"}}>{q.n}F · {q.zh}</div>)}</div>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:PALE}}>
  <Brand color={STEEL}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:STEEL}}>四册 <span style={{color:AMBER}}>+</span> 词汇手册</div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",gap:40,opacity:up}}>
    <div style={{width:420,height:381,borderRadius:12,overflow:"hidden",boxShadow:"0 24px 60px rgba(0,0,0,.3)",transform:"rotate(-3deg)"}}><Img src={staticFile("img/books.png")} style={{width:"100%",height:"100%",objectFit:"cover"}}/></div>
    <div style={{width:334,height:381,borderRadius:12,overflow:"hidden",boxShadow:"0 24px 60px rgba(0,0,0,.3)",transform:"rotate(3deg)"}}><Img src={staticFile("img/handbook.png")} style={{width:"100%",height:"100%",objectFit:"cover"}}/></div>
  </div>
  <div style={{position:"absolute",top:1020,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:48,color:STEEL,opacity:ease(t,s.start+0.9,s.start+1.3)}}>8000+ 词 · 按情景查</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:STEEL}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("lift")} t={t}><Lift p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #4a515c 0%, ${STEEL} 75%)`} accent={AMBER}/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
