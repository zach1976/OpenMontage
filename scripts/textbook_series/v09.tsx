// 越 09 水果：一个水果摊。顶上一条遮阳棚，下面一根绳上挂五张手写价签，
// 念到哪个水果，那张价签就晃着翻过来、露出越南名字，摊上那颗水果滚到正中。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, Books, End, ZH, VI, VI_SERIES, SeriesCtx, ease, sceneOf, calcMeta} from "./Common";

type It={vi:string;zh:string;c:string;c2:string};
export type SceneProps=BaseProps&{data:{items:It[]}};
const LEAF="#1f6f3f",AW1="#ff7b00",AW2="#fff4e0",KRAFT="#e9c891",INK="#2a1c0f",WOOD="#8a5a2b";

const Awning:React.FC=()=><div style={{position:"absolute",top:330,left:0,right:0,height:110,background:`repeating-linear-gradient(90deg, ${AW1} 0 90px, ${AW2} 90px 180px)`,clipPath:"polygon(0 0,100% 0,100% 70%,97.5% 100%,95% 70%,92.5% 100%,90% 70%,87.5% 100%,85% 70%,82.5% 100%,80% 70%,77.5% 100%,75% 70%,72.5% 100%,70% 70%,67.5% 100%,65% 70%,62.5% 100%,60% 70%,57.5% 100%,55% 70%,52.5% 100%,50% 70%,47.5% 100%,45% 70%,42.5% 100%,40% 70%,37.5% 100%,35% 70%,32.5% 100%,30% 70%,27.5% 100%,25% 70%,22.5% 100%,20% 70%,17.5% 100%,15% 70%,12.5% 100%,10% 70%,7.5% 100%,5% 70%,2.5% 100%,0 70%)"}}/>;

const Fruit:React.FC<{c:string;c2:string;size:number}>=({c,c2,size})=><div style={{width:size,height:size,borderRadius:"50%",background:`radial-gradient(circle at 35% 30%, ${c} 0%, ${c} 45%, ${c2} 100%)`,boxShadow:"0 14px 30px rgba(0,0,0,.3)",position:"relative"}}>
  <div style={{position:"absolute",left:size*.44,top:-size*.12,width:size*.12,height:size*.22,borderRadius:6,background:"#3d5a1e"}}/>
  <div style={{position:"absolute",left:size*.5,top:-size*.08,width:size*.3,height:size*.14,borderRadius:"0 100% 0 100%",background:"#4caf50"}}/></div>;

const Cover:React.FC<{p:SceneProps}>=({p})=><AbsoluteFill style={{background:LEAF}}>
  <Awning/>
  <Brand color="#fff" top={268}/>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:"#fff",letterSpacing:6}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:168,color:"#ffd166",letterSpacing:6}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1330,left:0,right:0,display:"flex",justifyContent:"center",gap:26}}>{p.data.items.map((x,k)=><Fruit key={k} c={x.c} c2={x.c2} size={120}/>)}</div>
</AbsoluteFill>;

const Stall:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`f${k}`]);const x=i!==undefined?p.data.items[i]:undefined;
  return <AbsoluteFill style={{background:LEAF}}>
  <Awning/>
  <Brand color="#fff" top={268}/>
  <div style={{position:"absolute",top:500,left:40,right:40,height:4,background:"#d9c39a"}}/>
  {p.data.items.map((q,k)=>{const flip=i!==undefined&&k<=i?ease(t,m[`f${k}`],m[`f${k}`]+0.5):0;const sw=i===k?Math.sin((t-m[`f${k}`])*5)*Math.exp(-(t-m[`f${k}`])*1.2)*14:0;
    return <div key={k} style={{position:"absolute",top:500,left:70+k*190,width:170,transformOrigin:"50% 0",transform:`rotate(${sw}deg)`}}>
      <div style={{margin:"0 auto",width:2,height:30,background:"#d9c39a"}}/>
      <div style={{height:120,borderRadius:10,background:i===k?"#fff":KRAFT,display:"flex",alignItems:"center",justifyContent:"center",fontFamily:flip>0.5?VI:ZH,fontWeight:900,fontSize:flip>0.5?(q.vi.length>8?28:34):40,color:INK,transform:`rotateY(${flip<0.5?flip*180:(1-flip)*180}deg)`}}>{flip>0.5?q.vi:q.zh}</div></div>;})}
  {x&&(()=>{const r=ease(t,m[`f${i!}`],m[`f${i!}`]+0.5);return <>
    <div style={{position:"absolute",top:740,left:0,right:0,display:"flex",justifyContent:"center",transform:`translateX(${(1-r)*-500}px) rotate(${(1-r)*-200}deg)`}}><Fruit c={x.c} c2={x.c2} size={220}/></div>
    <div style={{position:"absolute",top:1000,left:60,right:60,textAlign:"center",opacity:r}}>
      <div style={{fontFamily:VI,fontSize:120,lineHeight:1.3,color:"#fff"}}>{x.vi}</div>
      <div style={{fontFamily:ZH,fontWeight:900,fontSize:60,color:"#ffd166"}}>{x.zh}</div></div></>;})()}
  <div style={{position:"absolute",top:1290,left:0,right:0,height:24,background:WOOD}}/>
  {i!==undefined&&<div style={{position:"absolute",top:1340,left:190,width:700}}><FollowBar t={t} m={m} k={`f${i}`} fg="#ffd166" track="rgba(255,255,255,.16)" muted="rgba(255,255,255,.65)" label={`${i+1} / 5`}/></div>}
</AbsoluteFill>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);const parts=["主课文","生词","会话","语法","练习","拓展阅读"];return <AbsoluteFill style={{background:AW2}}>
  <Brand color={LEAF}/>
  <div style={{position:"absolute",top:350,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:88,color:LEAF}}>每一课都有</div>
  <div style={{position:"absolute",top:480,left:90,right:90,display:"flex",flexWrap:"wrap",justifyContent:"center",gap:14}}>{parts.map((x,k)=><div key={x} style={{fontFamily:ZH,fontWeight:900,fontSize:40,color:"#fff",background:k%2?AW1:LEAF,borderRadius:16,padding:"8px 22px",opacity:ease(t,s.start+0.3+k*0.25,s.start+0.6+k*0.25)}}>{x}</div>)}</div>
  <div style={{position:"absolute",top:690+(1-up)*60,left:160,opacity:up,transform:"rotate(1.5deg)"}}><Books w={760} radius={14}/></div>
</AbsoluteFill>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <SeriesCtx.Provider value={VI_SERIES}><AbsoluteFill style={{background:LEAF}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("stall")} t={t}><Stall p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #2e8b57 0%, ${LEAF} 75%)`} accent="#ffd166"/></Layer>
  </AbsoluteFill></SeriesCtx.Provider>;};
export const calculateMetadata=calcMeta as any;
