// 越 08 看病：一板药。五粒药各封在一个泡罩里，念到哪一句，那一粒就从铝箔里顶出来；
// 念完五句，药板空了 —— 话说清楚了，药也拿到了。
import React from "react";
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta} from "./Common";

type It={vi:string;zh:string};
export type SceneProps=BaseProps&{data:{items:It[]}};
const MINT="#e8f6f3",TEAL="#127a73",RED="#e63946",INK="#16302d",FOIL="#cfd8dc",GRAY="#7c9490";
const PILL=["#ff8fa3","#ffd166","#80ed99","#a0c4ff","#f4a261"];
const viSize=(s:string)=>s.length>12?92:s.length>6?112:140;

const Blister:React.FC<{t:number;m:Record<string,number>;i:number|undefined}>=({t,m,i})=><div style={{width:900,height:300,borderRadius:30,background:`linear-gradient(135deg, #eef2f3, ${FOIL})`,boxShadow:"0 20px 50px rgba(18,122,115,.18)",display:"flex",alignItems:"center",justifyContent:"space-around",padding:"0 20px"}}>
  {PILL.map((c,k)=>{const out=i!==undefined&&k<=i;const pop=i===k?ease(t,m[`m${k}`],m[`m${k}`]+0.4):out?1:0;return <div key={k} style={{width:140,height:200,borderRadius:70,background:out?"rgba(0,0,0,.06)":"rgba(255,255,255,.7)",border:"3px solid rgba(255,255,255,.9)",display:"flex",alignItems:"center",justifyContent:"center",position:"relative"}}>
    <div style={{width:84,height:150,borderRadius:42,background:`linear-gradient(180deg, ${c} 50%, #fff 50%)`,boxShadow:"0 6px 14px rgba(0,0,0,.15)",transform:`translateY(${-pop*150}px) rotate(${pop*(k%2?20:-20)}deg)`,opacity:i!==undefined&&k<i?0:1}}/>
  </div>;})}
</div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:MINT}}>
  <Brand color={TEAL}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${RED}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 看病</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:INK,letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:RED,letterSpacing:4}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1310,left:0,right:0,display:"flex",justifyContent:"center",transform:"scale(.6)"}}><Blister t={0} m={p.marks} i={undefined}/></div>
</AbsoluteFill>;

const Pills:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`m${k}`]);const x=i!==undefined?p.data.items[i]:undefined;const a=i!==undefined?ease(t,m[`m${i}`]+0.15,m[`m${i}`]+0.5):0;
  return <AbsoluteFill style={{background:MINT}}>
  <Brand color={TEAL}/>
  <div style={{position:"absolute",top:340,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{width:90,height:90,position:"relative"}}><div style={{position:"absolute",left:30,top:0,width:30,height:90,background:RED,borderRadius:6}}/><div style={{position:"absolute",left:0,top:30,width:90,height:30,background:RED,borderRadius:6}}/></div></div>
  <div style={{position:"absolute",top:580,left:90}}><Blister t={t} m={m} i={i}/></div>
  {x&&<div style={{position:"absolute",top:930,left:60,right:60,textAlign:"center",opacity:a}}>
    <div style={{fontFamily:VI,fontSize:viSize(x.vi),lineHeight:1.3,color:TEAL}}>{x.vi}</div>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:64,color:INK,marginTop:6}}>{x.zh}</div></div>}
  {i!==undefined&&<div style={{position:"absolute",top:1250,left:190,width:700}}><FollowBar t={t} m={m} k={`m${i}`} fg={TEAL} track="rgba(18,122,115,.14)" muted={GRAY} label={`${i+1} / 5`}/></div>}
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:TEAL}}>
  <Brand color={MINT}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:88,color:"#fff"}}>按情景查词</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:300,opacity:up,width:480,height:548,borderRadius:12,overflow:"hidden",boxShadow:"0 30px 70px rgba(0,0,0,.4)",transform:"rotate(-2deg)"}}><Img src={staticFile("img/handbook.png")} style={{width:"100%",height:"100%",objectFit:"cover"}}/></div>
  <div style={{position:"absolute",top:1140,left:0,right:0,display:"flex",justifyContent:"center",gap:18,opacity:ease(t,s.start+0.9,s.start+1.3)}}>{["8000+ 词","8 大主题","32 个情景"].map(x=><div key={x} style={{fontFamily:ZH,fontWeight:900,fontSize:42,color:TEAL,background:MINT,borderRadius:18,padding:"10px 24px"}}>{x}</div>)}</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:MINT}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("pills")} t={t}><Pills p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #1a9a90 0%, ${TEAL} 75%)`} accent="#fff"/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
