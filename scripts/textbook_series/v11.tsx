// 越 11 颜色：一叠油漆色卡。念到哪个颜色，那张色卡从扇面里抽出来、放大铺满上半幅，
// 底下的扇面留着已经讲过的几张 —— 像在五金店挑漆，挑一张少一张。
import React from "react";
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta} from "./Common";

type It={vi:string;zh:string;c:string;ink:string};
export type SceneProps=BaseProps&{data:{items:It[]}};
const PAPER="#f4f1ea",INK="#1d1d1f",MUTE="rgba(29,29,31,.45)";

const Fan:React.FC<{items:It[];cur:number;y:number}>=({items,cur,y})=><div style={{position:"absolute",top:y,left:0,right:0,height:420}}>
  {items.map((x,k)=>{const rot=(k-2)*11;const out=k===cur;return <div key={k} style={{position:"absolute",left:440,top:out?-40:0,width:200,height:400,borderRadius:18,background:x.c,transformOrigin:"50% 120%",transform:`rotate(${rot}deg)`,boxShadow:"0 14px 30px rgba(0,0,0,.18)",border:"6px solid #fff",opacity:cur>=0&&k>cur?.35:1}}>
    <div style={{position:"absolute",bottom:0,left:0,right:0,height:90,background:"#fff",fontFamily:ZH,fontWeight:800,fontSize:30,color:INK,display:"flex",alignItems:"center",justifyContent:"center"}}>{x.zh}</div></div>;})}
</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:PAPER}}>
  <Brand color={INK}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${INK}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 颜色</div></div>
  <div style={{position:"absolute",top:680,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:INK}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:880,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:p.data.items[0].c}}>{p.cover[1]}</div>
  <Fan items={p.data.items} cur={-1} y={1160}/>
</AbsoluteFill>;

const Chips:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`c${k}`]);const x=i!==undefined?p.data.items[i]:p.data.items[0];const a=i!==undefined?ease(t,m[`c${i}`],m[`c${i}`]+0.4):0;
  return <AbsoluteFill style={{background:PAPER}}>
  <Brand color={INK}/>
  <div style={{position:"absolute",top:340,left:90,right:90,height:560,borderRadius:28,background:x.c,transform:`scale(${.9+.1*a})`,opacity:a,boxShadow:"0 30px 70px rgba(0,0,0,.22)",border:"10px solid #fff"}}>
    <div style={{position:"absolute",left:50,top:60,fontFamily:VI,fontSize:x.vi.length>10?92:116,color:x.ink,lineHeight:1.2}}>{x.vi}</div>
    <div style={{position:"absolute",left:50,bottom:50,fontFamily:ZH,fontWeight:900,fontSize:84,color:x.ink}}>{x.zh}</div>
  </div>
  {i!==undefined&&<div style={{position:"absolute",top:950,left:150,width:780}}><FollowBar t={t} m={m} k={`c${i}`} fg={INK} track="rgba(0,0,0,.08)" muted={MUTE} label={`${i+1} / 5`}/></div>}
  <Fan items={p.data.items} cur={i??-1} y={1160}/>
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:PAPER}}>
  <Brand color={INK}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:INK}}>基础越南语 <span style={{color:p.data.items[0].c}}>1–4</span> 册</div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}>
    <div style={{width:720,height:653,borderRadius:16,overflow:"hidden",border:"10px solid #fff",boxShadow:"0 24px 60px rgba(0,0,0,.25)"}}><Img src={staticFile("img/books.png")} style={{width:"100%",height:"100%",objectFit:"cover"}}/></div></div>
  <div style={{position:"absolute",top:1260,left:0,right:0,display:"flex",justifyContent:"center",gap:18,opacity:ease(t,s.start+0.8,s.start+1.2)}}>{p.data.items.map((x,k)=><div key={k} style={{width:110,height:60,borderRadius:10,background:x.c,border:"4px solid #fff"}}/>)}</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:PAPER}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("chips")} t={t}><Chips p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg="radial-gradient(ellipse at 50% 40%, #3a3a3e 0%, #1d1d1f 75%)" accent="#e63946"/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
