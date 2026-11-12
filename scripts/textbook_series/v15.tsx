// 越 15 交通工具：一张地铁线路图。五个交通工具是五个站，一个小圆点沿线开过去，
// 到站就亮出这一站的词 —— 从摩托车一路换乘到轻轨。
import React from "react";
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta, cl} from "./Common";

type It={vi:string;zh:string;c:string};
export type SceneProps=BaseProps&{data:{items:It[]}};
const BG="#fbfaf6",INK="#202124",MUTE="rgba(32,33,36,.4)";
const STOPS=[[150,520],[400,520],[400,820],[680,820],[930,820]];

const Line:React.FC<{items:It[];cur:number;pos:number}>=({items,cur,pos})=>{
  const seg=(k:number)=>{const [a,b]=[STOPS[k],STOPS[k+1]];return <line key={k} x1={a[0]} y1={a[1]} x2={b[0]} y2={b[1]} stroke={items[k+1].c} strokeWidth={22} strokeLinecap="round" opacity={k<cur?1:.25}/>;};
  const k=Math.floor(pos),f=pos-k;const a=STOPS[Math.min(k,4)],b=STOPS[Math.min(k+1,4)];const dot=[a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f];
  return <svg width={1080} height={1100} style={{position:"absolute",top:0,left:0}}>
    {[0,1,2,3].map(seg)}
    {STOPS.map((s,j)=><circle key={j} cx={s[0]} cy={s[1]} r={j===cur?36:26} fill="#fff" stroke={items[j].c} strokeWidth={12}/>)}
    {cur>=0&&<circle cx={dot[0]} cy={dot[1]} r={16} fill={INK}/>}
  </svg>;};

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:BG}}>
  <Brand color={INK}/>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:INK,border:`2px solid ${p.data.items[1].c}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 交通</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:INK}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:900,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:150,color:p.data.items[1].c}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:830,left:0,right:0}}><Line items={p.data.items} cur={4} pos={4}/></div>
</AbsoluteFill>;

const Route:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`tr${k}`]);
  const pos=i===undefined?0:i===0?0:interpolate(t,[m[`tr${i}`]-0.6,m[`tr${i}`]],[i-1,i],cl);const x=i!==undefined?p.data.items[i]:undefined;
  return <AbsoluteFill style={{background:BG}}>
  <Brand color={INK}/>
  <Line items={p.data.items} cur={i??-1} pos={pos}/>
  {p.data.items.map((q,j)=><div key={j} style={{position:"absolute",left:STOPS[j][0]-90,top:STOPS[j][1]+(j<2?-120:52),width:180,textAlign:"center",fontFamily:ZH,fontWeight:800,fontSize:28,color:i!==undefined&&j<=i?INK:MUTE}}>{q.zh}</div>)}
  {x&&<div style={{position:"absolute",top:1020,left:90,right:90,padding:"36px 40px",borderRadius:26,background:"#fff",borderLeft:`16px solid ${x.c}`,boxShadow:"0 18px 40px rgba(0,0,0,.12)",opacity:ease(t,m[`tr${i}`],m[`tr${i}`]+0.3)}}>
    <div style={{fontFamily:VI,fontSize:x.vi.length>14?70:92,color:INK}}>{x.vi}</div>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:56,color:x.c,marginTop:8}}>{x.zh}</div></div>}
  {i!==undefined&&<div style={{position:"absolute",top:1370,left:150,width:780}}><FollowBar t={t} m={m} k={`tr${i}`} fg={INK} track="rgba(0,0,0,.08)" muted={MUTE} label={`${i+1} / 5`}/></div>}
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <AbsoluteFill style={{background:BG}}>
  <Brand color={INK}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:84,color:INK}}>出门在外 · <span style={{color:p.data.items[1].c}}>按情景查</span></div>
  <div style={{position:"absolute",top:520+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",gap:40,opacity:up}}>
    <div style={{width:420,height:381,borderRadius:12,overflow:"hidden",boxShadow:"0 24px 60px rgba(0,0,0,.2)"}}><Img src={staticFile("img/books.png")} style={{width:"100%",height:"100%",objectFit:"cover"}}/></div>
    <div style={{width:334,height:381,borderRadius:12,overflow:"hidden",boxShadow:"0 24px 60px rgba(0,0,0,.2)"}}><Img src={staticFile("img/handbook.png")} style={{width:"100%",height:"100%",objectFit:"cover"}}/></div>
  </div>
  <div style={{position:"absolute",top:1020,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:48,color:INK,opacity:ease(t,s.start+0.9,s.start+1.3)}}>8000+ 词 · 32 个情景</div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:BG}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("route")} t={t}><Route p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg="radial-gradient(ellipse at 50% 40%, #3b3f45 0%, #202124 75%)" accent="#f9a825"/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
