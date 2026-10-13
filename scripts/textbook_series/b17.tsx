// 17 讲价：水果摊的小黑板。价格用粉笔写在板上，跟着对话变 —— 47/公斤 → 一共 248 →
// "便宜点" 时 248 被一笔划掉 → 改写成 240。讲价这件事就发生在黑板上。
import React from "react";
import {AbsoluteFill, useCurrentFrame, useVideoConfig} from "remotion";
import {BaseProps, Brand, Layer, Track, FollowBar, BookPeek, End, ZH, TH, ease, sceneOf, calcMeta} from "./Common";

type Line={th:string;zh:string;price:string};
export type SceneProps=BaseProps&{data:{lines:Line[]}};
const BOARD="#26402f",WOOD="#8a5a2b",CHALK="#f4f1e8",PINK="#ff8fab",YEL="#ffe066",DIM="rgba(244,241,232,.5)";
const CHALKF="Chalkboard SE, Marker Felt, PingFang SC, sans-serif";
const thSize=(s:string)=>s.length>18?66:s.length>12?78:92;

const Board:React.FC<{children:React.ReactNode}>=({children})=><AbsoluteFill style={{background:"#3b2a1a"}}>
  <div style={{position:"absolute",inset:24,border:`22px solid ${WOOD}`,borderRadius:20,background:`radial-gradient(ellipse at 50% 40%, #2f5039 0%, ${BOARD} 75%)`}}/>
  <Brand color={YEL}/>{children}</AbsoluteFill>;

const Cover:React.FC<{p:SceneProps}>=({p})=><Board>
  <div style={{position:"absolute",top:338,left:0,right:0,display:"flex",justifyContent:"center"}}><div style={{fontFamily:ZH,fontSize:28,color:CHALK,border:`2px dashed ${CHALK}`,borderRadius:40,padding:"6px 26px",letterSpacing:3}}>教材精读 · 购物</div></div>
  <div style={{position:"absolute",top:690,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:CHALK,letterSpacing:4}}>{p.cover[0]}</div>
  <div style={{position:"absolute",top:1010,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:160,color:PINK,letterSpacing:4}}>{p.cover[1]}</div>
  <div style={{position:"absolute",top:1320,left:0,right:0,textAlign:"center",fontFamily:CHALKF,fontSize:90,color:YEL}}><span style={{textDecoration:"line-through",color:DIM}}>248</span>　→　240 ฿</div>
</Board>;

const Stall:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const m=p.marks;const i=[4,3,2,1,0].find(k=>t>=m[`b${k}`])??0;const l=p.data.lines[i];
  const a=ease(t,m[`b${i}`],m[`b${i}`]+0.35);const cut=i>=3?ease(t,m.b3_a,m.b3_a+0.5):0;const fresh=i===4?ease(t,m.b4_a,m.b4_a+0.4):0;
  return <Board>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:CHALKF,fontSize:60,color:YEL}}>ทุเรียน · 榴莲</div>
  <div style={{position:"absolute",top:450,left:0,right:0,height:300,display:"flex",alignItems:"center",justifyContent:"center",gap:40}}>
    {l.price===""&&<div style={{fontFamily:CHALKF,fontSize:200,color:CHALK}}>?</div>}
    {l.price==="47/kg"&&<div style={{fontFamily:CHALKF,fontSize:150,color:CHALK}}>47 <span style={{fontSize:70}}>฿ / kg</span></div>}
    {i>=2&&<div style={{position:"relative",fontFamily:CHALKF,fontSize:180,color:i>=3?DIM:CHALK}}>248
      <div style={{position:"absolute",left:-10,top:"52%",height:12,width:`${cut*110}%`,background:PINK,borderRadius:8,transform:"rotate(-8deg)"}}/></div>}
    {i===4&&<div style={{fontFamily:CHALKF,fontSize:180,color:PINK,opacity:fresh,transform:`scale(${0.8+0.2*fresh})`}}>240</div>}
  </div>
  <div style={{position:"absolute",top:820,left:70,right:70,textAlign:"center",opacity:a}}>
    <div style={{fontFamily:ZH,fontWeight:900,fontSize:76,color:CHALK}}>{l.zh}</div>
    <div style={{fontFamily:TH,fontSize:thSize(l.th),lineHeight:1.5,color:YEL}}>{l.th}</div>
  </div>
  <div style={{position:"absolute",top:1130,left:0,right:0,display:"flex",justifyContent:"center",gap:14}}>{p.data.lines.map((_,k)=><div key={k} style={{width:60,height:12,borderRadius:6,background:k<=i?PINK:"rgba(244,241,232,.2)"}}/>)}</div>
  <div style={{position:"absolute",top:1220,left:190,width:700}}><FollowBar t={t} m={m} k={`b${i}`} fg={PINK} track="rgba(244,241,232,.15)" muted={DIM} label={`${i+1} / 5`}/></div>
</Board>;};

const Book:React.FC<{p:SceneProps;t:number}>=({p,t})=>{const s=sceneOf(p,"book");const up=ease(t,s.start,s.start+0.6);return <Board>
  <div style={{position:"absolute",top:340,left:0,right:0,textAlign:"center",fontFamily:ZH,fontWeight:900,fontSize:92,color:CHALK}}>第 <span style={{color:PINK}}>2</span> 册 · 第 <span style={{color:PINK}}>6</span> 课</div>
  <div style={{position:"absolute",top:500+(1-up)*60,left:0,right:0,display:"flex",justifyContent:"center",opacity:up}}><BookPeek name="dlg" w={860} rot={-1.5} shadow="0 30px 70px rgba(0,0,0,.5)"/></div>
</Board>;};

export const Scene:React.FC<SceneProps>=(p)=>{const f=useCurrentFrame(),{fps}=useVideoConfig(),t=f/fps;const S=(id:string)=>sceneOf(p,id);
  return <AbsoluteFill style={{background:BOARD}}>
    <Track p={p}/>
    <Layer s={S("cover")} t={t} first><Cover p={p}/></Layer>
    <Layer s={S("stall")} t={t}><Stall p={p} t={t}/></Layer>
    <Layer s={S("book")} t={t}><Book p={p} t={t}/></Layer>
    <Layer s={S("end")} t={t}><End p={p} t={t} bg={`radial-gradient(ellipse at 50% 40%, #2f5039 0%, ${BOARD} 75%)`} accent={YEL}/></Layer>
  </AbsoluteFill>;};
export const calculateMetadata=calcMeta as any;
